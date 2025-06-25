"""Unit test module for class QRCodeEncoder"""

import unittest
from src.qr.QRCodeEncoder import QRCodeEncoder
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel
from src.qr.QRCodeInputAnalyzer import QRCodeInputAnalyzer

class TestQRCodeEncoder(unittest.TestCase):
    """Unit test class for QRCodeEncoder methods.
       This class will test all the four implemented modalities to encode data for QR codes.
    """
    def setUp(self):
        self._encoder = QRCodeEncoder(4, QRErrorCorrectionLevel.L, QRCodeInputAnalyzer())
        
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
        
    def test_encode_byte(self):
        """Test encoding byte input."""
        result = self._encoder.encode_bytes("Hello, World!", QRCodeEncoder.get_char_count_indicator("BYTE"), QRCodeEncoder.get_mode_indicator("BYTE"))
        self.assertEqual(result, b'0100100001100101011011000110110001101111')
        
    def test_encode_kanji_single_char(self):
        """Test the encoding of a single kanji character input"""
        result = self._encoder.encode_kanji("点".encode("shift-jis"), QRCodeEncoder.get_char_count_indicator("KANJI"), QRCodeEncoder.get_mode_indicator("KANJI"))
        self.assertEqual(result, b'100010000110110011111')
        
    def test_encode_kanji_multiple_char(self):
        """Test the encoding of more than one Shift-JIS char"""
        result = self._encoder.encode_kanji("こんにちは".encode("shift-jis"), QRCodeEncoder.get_char_count_indicator("KANJI"), QRCodeEncoder.get_mode_indicator("KANJI"))
        self.assertEqual(result, b'1000100010001010000011010001000001100100000100110001010011111001000001101')
        
    def test_encode_decider(self):
        """ a Single test step to test the encoder itself for each of the modes:"""
        result = self._encoder.encode_data_into_bit_stream("AC-42")
        self.assertEqual(result, b'0011100111011100111001000010')
        result = self._encoder.encode_data_into_bit_stream("01234567")
        self.assertEqual(result, b'000100001000000000110001010110011000011')
        result = self._encoder.encode_data_into_bit_stream("点")
        self.assertEqual(result, b'100010000110110011111')
        
    def test_encode_string_per_iso_standards(self):
        """ Test the full encoding functionality for codewords instead of single bit streams as in sections 7.4.2 to 7.4.7, and the teriminator / pad codewords
            from Sections 7.4.9 and 7.4.10.
            Note that the version being 4 and the Error Correction Level is L, we have 80 codewords which results in the final encoded string having 640 bits.
        """
        result = self._encoder.encode_input("01234567")
        self.assertEqual(result, b'0001000010000000001100010101100110000110111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100000100011110110000010001111011000001000111101100')