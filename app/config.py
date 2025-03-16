"""
Configuration settings for the Building Detector application.
"""
import os

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# External services
COLAB_SERVER_URL = 'https://5a71-34-139-152-103.ngrok-free.app'  # ngrok URL from Colab Server 