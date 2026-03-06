#!/usr/bin/env python3
"""Run the Building Detector Flask application."""

from app.app import app
from app.utils.logger import logger

if __name__ == "__main__":
    logger.info("Starting Building Detector application from main.py")
    print("Starting Building Detector...")
    print("Application will be available at: http://127.0.0.1:5000/")
    print("Press Ctrl+C to stop the server")

    app.run(host="127.0.0.1", port=5000, debug=False)
