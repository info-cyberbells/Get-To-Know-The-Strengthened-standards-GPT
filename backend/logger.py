import os
from logging.handlers import TimedRotatingFileHandler
import logging
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logger():
    # Generate log filename with current date
    date_string = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join('logs', f'assistant-chatbot-{date_string}.log')

    # Create and configure handler
    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=5,
        encoding='utf-8'
    )
    handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to prevent duplicate logging
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)
    
    # Add our configured handler
    logger.addHandler(handler)
    
    return logger

# Create logger instance
logger = setup_logger()