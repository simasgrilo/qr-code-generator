"""Logger object that will record both QR requests failures at api level, as well as issues in the application layer"""
import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger:
    """Logger class

    """
    instance = None
    DEFAULT_LOG_PATH = 'logs\\app.log'
    LOG_FILE = 'LOG_FILE'
    LOG_FILE_ROTATION = 'LOG_FILE_ROTATION'
    LOG_FILE_BACKUP_COUNT = 'LOG_FILE_BACKUP_COUNT'

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance
        cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger("qr_code_logger")
        self.logger.setLevel(logging.INFO)
        log_directory = os.getenv(self.LOG_FILE)
        rotation = os.getenv(self.LOG_FILE_ROTATION)
        if not log_directory:
            self.logger.info("missing .env var %s. Defaulting to log path logs/app.log", self.LOG_FILE)
            log_directory = os.path.join(Path(__file__).parent, self.DEFAULT_LOG_PATH)
        if not rotation:
            self.logger.info("missing .env var %s. Defaulting to log path logs/app.log", self.LOG_FILE_ROTATION)
            rotation = 'midnight'
        try:
            backup_count = int(os.getenv(self.LOG_FILE_BACKUP_COUNT))
            if not backup_count:
                raise ValueError
        except (ValueError, KeyError, TypeError):
            self.logger.info('provided .env entry for %s is invalid. Defaulting to 7 days',self.LOG_FILE_BACKUP_COUNT)
            backup_count = 7
        handler = TimedRotatingFileHandler(
            filename=log_directory,
            when=rotation,
            backupCount=7
        )
        self.formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = Logger()
        return cls.instance

    @classmethod
    def get_logger(cls):
        """Gets a logger instance of the logger Object
        """
        if cls.instance is None:
            cls.instance = Logger()
        return cls.instance.logger
