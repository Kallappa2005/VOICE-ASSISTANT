"""
Logger Configuration
Centralized logging for the application
"""

import logging
import os
from datetime import datetime

def setup_logger(name):
    """
    Setup logger with file and console handlers
    
    Args:
        name (str): Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger
    """
    # Create logs directory if not exists
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log filename with date
    log_file = os.path.join(log_dir, f'voice_assistant_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger