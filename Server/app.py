"""
app.py - Smart Camera Web Server

This module contains code for setting up a web server on an ESP32 device
to control a smart camera. It allows users to configure the camera settings,
view the last captured image, and upload new images to the server.

Author: Philipp Hofmann
Date: 18/4/2014
"""

import os
import subprocess
import zipfile
import uuid
import shutil
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for

app = Flask(__name__, static_folder='static', static_url_path='')

UPLOAD_FOLDER = '/upload'

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

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return app.send_static_file('icons/favicon.ico')

@app.route('/api/get-clients', methods=['GET'])
def get_clients():
    """
    This function returns a list of all clients that uploaded images at some point.

    Returns:
        list: A list of all connected clients.
    """
    clients = []
    for client in os.listdir(UPLOAD_FOLDER):
        if os.path.isdir(os.path.join(UPLOAD_FOLDER, client)):
            clients.append(client)
    return jsonify(clients)

def main():
    """
    This function is the entry point of the application.
    
    It starts the application by running the Flask app on the specified host and port.
    """
    debug_print("Starting application...")
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    main()
