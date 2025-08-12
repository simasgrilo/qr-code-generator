"""Test class to provide basic unit tests for QR code creation
"""

import os
from unittest import TestCase
from PIL import Image, ImageChops
from src.qr.QRCode import QRCode
from src.qr.utils.QRCodeFactory import QRCodeFactory
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel

class TestQRCodeImageGenerator(TestCase):

    def setUp(self):
        self.known_good_image_path = "test\\qr\\qr_code_ok.png" #usar OS.path pra isso aqui
        self.created_img_path = "test\\qr\\test_qr_code.png"
        self.qr_code_gen = QRCodeFactory.create_qr_code_obj(4, QRErrorCorrectionLevel.L, self.created_img_path)
        
    def test_check_object_created(self):
        """Method to confirm that the QR code factory indeed return QR Code objects
           looks a bit overkill
        """
        self.assertIsInstance(self.qr_code_gen, QRCode)

    def test_qr_code_creation(self):
        """Method to compare the creation of a QR Code with alphanumeric
           encoded data. 
        """
        self.qr_code_gen.create_qr_code("qr code test")
        diff_img = None
        with Image.open(self.known_good_image_path) as img_expected, Image.open(self.created_img_path) as img_output:
            diff_img = ImageChops.difference(img_output, img_expected).getbbox()
        self.assertIsNone(diff_img, "Generated image does not match expected image")
        os.remove(self.created_img_path)

