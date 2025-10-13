"""Module that holds test for logging features"""
import unittest
import os
from io import StringIO
from logging import StreamHandler
from unittest.mock import patch, MagicMock
from src.app.log.logger import Logger

class LoggingUnitTest(unittest.TestCase):
    """Class with unit test methods for the logging procedure defined.
       This class focuses on the structure of the class, setup, parameters, etc."""
    
    def test_singleton_instance(self):
        """Method to test the singleton instatiation
        """
        logger_1 = Logger.get_logger()
        logger_2 = Logger.get_logger()
        self.assertIs(logger_1, logger_2)
        
    @patch('os.getenv', side_effect=lambda param: None)
    @patch('logging.getLogger')
    @patch('logging.handlers.TimedRotatingFileHandler')
    def test_env_fallbacks_used(self, mock_handler, mock_get_logger, mock_getenv):
        """Tests whether when the correct values are not read in the .env file, the default fallback values are used.

        Args:
            mock_handler : Mocked parameter patched to denote logging.handler
            mock_get_logger (_type_): Mocked parameter patched to denote the singleton constructor
            mock_getenv (_type_): Mocked parameter to denote os.getenv method 
                                  behavior, where the mock will not find the corresponding entry.
        """
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        # below call is to trigger the constructor of the class defined in logger.py
        Logger()
        self.assertIn('missing .env var %s. Defaulting to log path logs/app.log', [call[0][0] for call in mock_logger.info.call_args_list])
        self.assertIn("missing .env var %s. Defaulting to log path logs/app.log", [call[0][0] for call in mock_logger.info.call_args_list])


class TestLoggerRealLoggingOutput(unittest.TestCase):
    """Class to unit test the logging output as a stream using StringIO, to avoid creating
       real files in the filesystem.

    """
    def setUp(self):
        Logger.instance = None  
        self.logger = Logger.get_instance()
        self.stream = StringIO()
        self.stream_handler = StreamHandler(self.stream)
        self.stream_handler.setFormatter(self.logger.formatter)
        self.logger = Logger.get_logger()
        self.logger.addHandler(self.stream_handler)

    def tearDown(self):
        self.logger.removeHandler(self.stream_handler)
        Logger.instance = None

    def test_logger_outputs_info_log(self):
        """Tests whether the logger outputs a information entry (i.e., the result logger.info call)
        """
        message = "This is a test log message"
        self.logger.info(message)

        self.stream_handler.flush()
        log_output = self.stream.getvalue()

        self.assertIn(message, log_output)
        self.assertIn("INFO", log_output)

    def test_logger_outputs_error_log(self):
        """Method to test output in error entries
        """
        message = "An error occurred"
        self.logger.error(message)

        self.stream_handler.flush()
        log_output = self.stream.getvalue()

        self.assertIn(message, log_output)
        self.assertIn("ERROR", log_output)