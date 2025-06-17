"""Unit test module for class QRCodeEncoder"""

import unittest
from src.qr.QRCodeEncoder import QRCodeEncoder
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel

class TestQRCodeEncoder(unittest.TestCase):
    """Unit test class for QRCodeEncoder methods.
       This class will test all the four implemented modalities to encode data for QR codes.
    """
    def setUp(self):
        self._encoder = QRCodeEncoder(QRErrorCorrectionLevel.L)
        
    def test_encode_numeric_is_not_none(self):
        """Test encoding numeric input."""
        result = self._encoder.encode_numeric("1234567890", QRCodeEncoder.get_char_count_indicator("NUMERIC"), QRCodeEncoder.get_mode_indicator("NUMERIC"))
        self.assertNotEqual(result, None) 
        
    def test_valid_encode_numeric(self):
        """Test encoding numeric input."""
        result = self._encoder.encode_numeric("01234567",QRCodeEncoder.get_char_count_indicator("NUMERIC"), QRCodeEncoder.get_mode_indicator("NUMERIC"))
        self.assertEqual(result, b'000100001000000000110001010110011000011')

    def test_encode_alphanumeric(self):
        """Test encoding alphanumeric input."""
        result = self._encoder.encode_alphanumeric("AC-42", QRCodeEncoder.get_char_count_indicator("ALPHANUMERIC"), QRCodeEncoder.get_mode_indicator("ALPHANUMERIC"))
        self.assertEqual(result, b'0011100111011100111001000010')