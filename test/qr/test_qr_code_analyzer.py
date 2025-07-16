"""Module for unit testing of QRCodeAnalyzer class."""

import unittest

from src.qr.QRCodeInputAnalyzer import QRCodeInputAnalyzer


class TestQRCodeInputAnalyzer(unittest.TestCase):
    """Test cases for QRCodeAnalyzer class."""

    def setUp(self):
        """Set up the QRCodeAnalyzer instance."""
        self.analyzer = QRCodeInputAnalyzer()

    def test_numeric(self):
        """Test numeric input."""
        self.assertEqual(self.analyzer.analyse("1234567890"), "Numeric")

    def test_alphanumeric(self):
        """Test alphanumeric input."""
        self.assertEqual(self.analyzer.analyse("HELLO123"), "Alphanumeric")

    def test_byte(self):
        """Test byte input."""
        self.assertEqual(self.analyzer.analyse("Hello, World!"), "Byte")

    def test_kanji(self):
        """Test kanji input."""
        self.assertEqual(self.analyzer.analyse("こんにちは"), "Kanji")