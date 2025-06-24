from flask import Flask, request, jsonify
import requests
import tempfile
import os
import ffmpeg
import traceback

app = Flask(__name__)

@app.route('/merge-video-image', methods=['POST'])
def merge_video_image():
    try:
        print("=== INICIO: Recibiendo petición ===")
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        video_url = data['video_url']
        image_url = data['image_url']
        print(f"Video URL: {video_url}")
        print(f"Image URL: {image_url}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Directorio temporal: {temp_dir}")
            
            # Descargar video
            print("=== Descargando video ===")
            video_path = f"{temp_dir}/input_video.mp4"
            response = requests.get(video_url)
            print(f"Response status video: {response.status_code}")
            
            if response.status_code != 200:
                return jsonify({'error': f'Error descargando video: {response.status_code}'}), 500
                
            with open(video_path, 'wb') as f:
                f.write(response.content)
            print(f"Video guardado: {os.path.exists(video_path)}")
            
            # Descargar imagen
            print("=== Descargando imagen ===")
            image_path = f"{temp_dir}/input_image.jpg"
            response = requests.get(image_url)
            print(f"Response status imagen: {response.status_code}")
            
            if response.status_code != 200:
                return jsonify({'error': f'Error descargando imagen: {response.status_code}'}), 500
                
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"Imagen guardada: {os.path.exists(image_path)}")
            
            # Procesar con FFmpeg
            print("=== Procesando con FFmpeg ===")
            output_path = f"{temp_dir}/output.mp4"
            
            (
                ffmpeg
                .input(video_path)
                .input(image_path)
                .filter('overlay', '(W-w)/2:(H-h)/2')
                .output(output_path, acodec='copy')
                .overwrite_output()
                .run()
            )
            
            print(f"Video procesado: {os.path.exists(output_path)}")
            print("=== ÉXITO ===")
            
            return jsonify({
                'success': True,
                'message': 'Video procesado correctamente'
            })
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"=== ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Traceback: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    app.run(debug=True)
