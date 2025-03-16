import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger():
    """
    Configure and set up the application logger to write to a file rather than stdout.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('osm_building_detector')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to prevent duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create rotating file handler
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Create formatters and add it to the handlers
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    
    # Prevent propagation to the root logger (which outputs to console)
    logger.propagate = False
    
    # Configure root logger to use our file handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers from root logger
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our file handler to the root logger
    root_logger.addHandler(file_handler)
    
    # Redirect Flask's logging to our file
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.propagate = False
    werkzeug_logger.addHandler(file_handler)
    
    # Redirect stdout and stderr to the log file (optional)
    # This is a more extreme solution to capture all output
    # sys.stdout = open(os.path.join(log_dir, 'stdout.log'), 'a')
    # sys.stderr = open(os.path.join(log_dir, 'stderr.log'), 'a')
    
    return logger

# Create and configure logger
logger = setup_logger() 