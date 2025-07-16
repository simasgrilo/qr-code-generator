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
        
    def test_encode_data_length_equals_iso_spec(self):
        """ Test to confirm if the encoding with version 1, level M
            yields the same number of codewords as the spec in Table 9
        """
        qr = self._encoder
        result = qr.generate_blocks(1, QRErrorCorrectionLevel.M, qr.encode_input("HELLO WORLD"))
        self.assertEqual(len(result) // 8, 26)
        
    def test_encode_data_version_1_level_m_value(self):
        """ Test to check if the value of the encoding with version 1
            and level M matches the same data as in a bytestring.
        """
        qr = self._encoder
        result = qr.generate_blocks(1, QRErrorCorrectionLevel.M, qr.encode_input("HELLO WORLD"))
        self.assertEqual(result, bytes(("0110000101101111000110100010111001011011100010011010100001"
                                        "1010001110110000010001111011000001000111101100000100011110"
                                        "1100000100011100001011110011001011100100100001100100101101"
                                        "01101011111011001101111110110011000000000"), encoding='utf-8'))
        
    def test_encode_data_version_4_level_q(self):
        """ Test to check if the conversion and encoding process works for more than one block """
        qr = self._encoder
        result = qr.generate_blocks(4, QRErrorCorrectionLevel.Q, qr.encode_input("HELLO WORLD"))
        self.assertEqual(result, bytes(('011000011110110001101111000100010001101011101100001011'
                                        '1000010001010110111110110010001001000100011010100011101'
                                        '10001101000000100011110110011101100000100010001000111101'
                                        '1001110110000010001000100011110110011101100000100010001'
                                        '0001111011001110110000010001000100011110110011101100000'
                                        '1000100010001111011001110110000010001000100011110110011'
                                        '1011000001000100010001111011001110110000010001000100011'
                                        '0010011010111110111101001011101000010100001100000111111'
                                        '00101110010110011001011100111101100110101100110100100100'
                                        '01001110100100011100001100001011010001101100011100011010'
                                        '11111001010100111100010001000110101101001111111110101011'
                                        '00011100111001111110001010000001100101110000101010111111'
                                        '11100110010011001011101000101011001010000100010011000101'
                                        '11100001001000100001000110001000011111011110000110101110'
                                        '1011111010110000010010100000000'), encoding='utf-8'))