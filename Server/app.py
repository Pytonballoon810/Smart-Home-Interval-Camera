"""
app.py - Smart Camera Web Server

This module contains code for setting up a web server on an ESP32 device
to control a smart camera. It allows users to configure the camera settings,
view the last captured image, and upload new images to the server.

Author: [Your Name]
Date: [Date]
"""

import os
import subprocess
import zipfile
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = '/mounted_directory'

DEBUG_MSG = os.getenv("DEBUG_MSG", "False").lower() == "true"

def debug_print(message):
    """Prints the debug message if DEBUG_MSG is True.

    Args:
        message (str): The message to be printed.

    Returns:
        None
    """
    if DEBUG_MSG:
        print(f"\033[94m[DEBUG]\033[0m {message}")

@app.route('/upload', methods=['POST'])
def upload_image():
    """Uploads an image file to the server.

    Returns:
        A JSON response containing the status of the upload and the client ID.
    """
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
    """Render the index.html page.

    This function retrieves a list of folders in the UPLOAD_FOLDER directory and passes it to the index.html template for rendering.

    Returns:
        The rendered index.html page with the list of folders.
    """
    debug_print("Rendering index.html...")
    folders = [name for name in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, name))]
    return render_template('index.html', folders=folders)

@app.route('/view/<client_id>')
def view_images(client_id):
    """
    View images for a specific client.

    Args:
        client_id (str): The ID of the client.

    Returns:
        tuple: A tuple containing the rendered template and the list of images for the client.
    """
    debug_print(f"Viewing images for client: {client_id}")
    client_folder = os.path.join(UPLOAD_FOLDER, client_id)
    if not os.path.exists(client_folder):
        debug_print("Client folder not found")
        return jsonify({'error': 'Client folder not found'}), 404

    images = os.listdir(client_folder)
    return render_template('view.html', client_id=client_id, images=images)

@app.route('/create_video/<client_id>', methods=['POST'])
def create_video(client_id):
    """
    Create a video from a sequence of images for a specific client.

    Args:
        client_id (str): The ID of the client.

    Returns:
        dict: A dictionary containing the message and the path of the created video.
            - 'message' (str): A message indicating the status of the video creation process.
            - 'video_path' (str): The path of the created video file.

    Raises:
        FileNotFoundError: If the client folder is not found.
    """
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
    command = ['ffmpeg', '-framerate', '24', '-i',
               os.path.join(client_folder, '%*.jpg'),
               output_file]
    subprocess.run(command, check=False)

    return jsonify({'message': 'Video created successfully', 'video_path': output_file}), 200

@app.route('/download/<path:file_path>')
def download_file(file_path):
    """Download a file from the server.

    Args:
        file_path (str): The path of the file to be downloaded.

    Returns:
        Response: The file as a response object.

    """
    debug_print(f"Downloading file: {file_path}")
    return send_from_directory(UPLOAD_FOLDER, file_path, as_attachment=True)

@app.route('/create_videos', methods=['POST'])
def create_videos():
    """Create videos from selected folders.

    This function creates videos by calling the `create_video` function for each selected folder.
    The selected folders are obtained from the request form.

    Returns:
        A JSON response indicating the success of video creation.

    """
    debug_print("Creating videos...")
    folders = request.form.getlist('folders[]')
    for folder in folders:
        create_video(folder)
    return jsonify({'message': 'Videos created successfully'}), 200

@app.route('/download_files', methods=['POST'])
def download_files():
    """
    Downloads the selected files and creates a zip file containing them.

    Returns:
        Response: The response object containing the zip file as an attachment.
    """
    debug_print("Downloading files...")
    files = request.form.getlist('files[]')
    zip_file_path = os.path.join(UPLOAD_FOLDER, 'downloaded_files.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in files:
            zipf.write(os.path.join(UPLOAD_FOLDER, file), file)
    return send_from_directory(UPLOAD_FOLDER, 'downloaded_files.zip', as_attachment=True)

def main():
    """
    This function is the entry point of the application.
    
    It starts the application by running the Flask app on the specified host and port.
    """
    debug_print("Starting application...")
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    main()
