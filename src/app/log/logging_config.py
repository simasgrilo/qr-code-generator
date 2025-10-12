"""Logger object that will record both QR requests failures at api level, as well as issues in the application layer"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger:
    """Logger class

    """
    instance = None
    
    def __new__(cls):
        return cls.get_logger()
    
    def __init__(self):
        self.logger = logging.getLogger("qr_code_logger")
        self.logger.setLevel(logging.INFO)
        log_directory = os.getenv("LOG_FILE")
        rotation = os.getenv("LOG_FILE_ROTATION")
        if not log_directory:
            self.logger.info("missing .env var LOG_FILE. Defaulting to log path logs/app.log")
            log_directory = 'logs/app.log'
        if not rotation:
            self.logger.info("missing .env var LOG_FILE. Defaulting to log path logs/app.log")
            rotation = 'midnight'
        handler = TimedRotatingFileHandler(
            filename=log_directory,
            when=rotation,
            backupCount=7
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname) - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    @classmethod
    def get_logger(cls):
        """Gets a logger instance of the logger Object
        """
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
    

