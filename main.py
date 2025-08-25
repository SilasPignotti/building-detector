#!/usr/bin/env python3
"""
Building Detector - Main Entry Point

This is the main entry point for the Building Detector application.
It starts the Flask web server and handles the web-based interface
for building detection from satellite imagery.

Usage:
    python main.py

The application will start on http://127.0.0.1:5000/
"""

from app.app import app
from app.utils.logger import logger

if __name__ == '__main__':
    logger.info('Starting Building Detector application from main.py')
    print("Starting Building Detector...")
    print("Application will be available at: http://127.0.0.1:5000/")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='127.0.0.1', port=5000, debug=False)