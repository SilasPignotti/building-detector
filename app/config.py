"""
Configuration settings for the Building Detector application.
"""
import os

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# External services - Load from environment variable or use default
COLAB_SERVER_URL = os.environ.get('COLAB_SERVER_URL', 'https://your-ngrok-url.ngrok-free.app') 