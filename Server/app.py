from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import uuid
import subprocess
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = '/mounted_directory'

DEBUG_MSG = os.getenv("DEBUG_MSG", "False").lower() == "true"

def debug_print(message):
    if DEBUG_MSG:
        print(f"\033[94m[DEBUG]\033[0m {message}")

@app.route('/upload', methods=['POST'])
def upload_image():
    debug_print("Starting upload_image function...")

    if 'image' not in request.files:
        debug_print("No file part")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        debug_print("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    # Create a subfolder for each unique client
    client_id = str(uuid.uuid4())
    client_folder = os.path.join(UPLOAD_FOLDER, client_id)
    os.makedirs(client_folder, exist_ok=True)

    # Save the image to the client's subfolder
    file.save(os.path.join(client_folder, file.filename))
    
    debug_print("File uploaded successfully")
    return jsonify({'message': 'File uploaded successfully', 'client_id': client_id}), 200

@app.route('/')
def index():
    debug_print("Rendering index.html...")
    folders = [name for name in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, name))]
    return render_template('index.html', folders=folders)

@app.route('/view/<client_id>')
def view_images(client_id):
    debug_print(f"Viewing images for client: {client_id}")
    client_folder = os.path.join(UPLOAD_FOLDER, client_id)
    if not os.path.exists(client_folder):
        debug_print("Client folder not found")
        return jsonify({'error': 'Client folder not found'}), 404

    images = os.listdir(client_folder)
    return render_template('view.html', client_id=client_id, images=images)

@app.route('/create_video/<client_id>', methods=['POST'])
def create_video(client_id):
    debug_print(f"Creating video for client: {client_id}")
    client_folder = os.path.join(UPLOAD_FOLDER, client_id)
    if not os.path.exists(client_folder):
        debug_print("Client folder not found")
        return jsonify({'error': 'Client folder not found'}), 404

    # Delete existing video, if any
    existing_video = os.path.join(client_folder, 'video.mp4')
    if os.path.exists(existing_video):
        os.remove(existing_video)

    images = os.listdir(client_folder)
    images_paths = [os.path.join(client_folder, image) for image in images]

    # Create a video from images
    output_file = os.path.join(client_folder, 'video.mp4')
    command = ['ffmpeg', '-framerate', '24', '-i', os.path.join(client_folder, '%*.jpg'), output_file]
    subprocess.run(command)

    return jsonify({'message': 'Video created successfully', 'video_path': output_file}), 200

@app.route('/download/<path:file_path>')
def download_file(file_path):
    debug_print(f"Downloading file: {file_path}")
    return send_from_directory(UPLOAD_FOLDER, file_path, as_attachment=True)

@app.route('/create_videos', methods=['POST'])
def create_videos():
    debug_print("Creating videos...")
    folders = request.form.getlist('folders[]')
    for folder in folders:
        create_video(folder)
    return jsonify({'message': 'Videos created successfully'}), 200

@app.route('/download_files', methods=['POST'])
def download_files():
    debug_print("Downloading files...")
    files = request.form.getlist('files[]')
    zip_file_path = os.path.join(UPLOAD_FOLDER, 'downloaded_files.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in files:
            zipf.write(os.path.join(UPLOAD_FOLDER, file), file)
    return send_from_directory(UPLOAD_FOLDER, 'downloaded_files.zip', as_attachment=True)

def main():
    debug_print("Starting application...")
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
