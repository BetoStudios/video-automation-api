from flask import Flask, request, jsonify
import requests
import tempfile
import os
import ffmpeg

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
            
            # Usar ffmpeg-python
            (
                ffmpeg
                .input(video_path)
                .input(image_path)
                .filter('overlay', '(W-w)/2:(H-h)/2')
                .output(output_path, acodec='copy')
                .overwrite_output()
                .run()
            )
            
            # Devolver éxito
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
