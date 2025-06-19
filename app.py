from flask import Flask, request, jsonify
import subprocess
import requests
import tempfile
import os

app = Flask(__name__)

@app.route('/merge-video-image', methods=['POST'])
def merge_video_image():
    try:
        data = request.get_json()
        video_url = data['video_url']
        image_url = data['image_url']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Descargar video
            video_path = f"{temp_dir}/input_video.mp4"
            response = requests.get(video_url)
            with open(video_path, 'wb') as f:
                f.write(response.content)
            
            # Descargar imagen
            image_path = f"{temp_dir}/input_image.jpg"
            response = requests.get(image_url)
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Procesar con FFmpeg
            output_path = f"{temp_dir}/output.mp4"
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', image_path,
                '-filter_complex', 
                '[1:v]scale=800:600[img];[0:v][img]overlay=(W-w)/2:(H-h)/2',
                '-c:a', 'copy',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return jsonify({'error': result.stderr}), 500
            
            # Por ahora, devolver éxito (luego añadiremos upload)
            return jsonify({
                'success': True,
                'message': 'Video procesado correctamente'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    app.run(debug=True)
