""" API integration tests """
import unittest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image, ImageChops
from src.app.main_app import app

client = TestClient(app)


class TestBasicAPIOperations(unittest.TestCase):
    """Class to test basic API operations - mainly retrieving a valid QR code image

    Args:
        unittest (_type_): _description_
    """

    def setUp(self):
        self.known_good_image_path = os.path.join(Path(__file__).parent, 'static', 'good_qr_code.png')

    def test_create_qr_code(self):
        """ Basic integration automated test to guarantee that the generated
            image matches the known good image
        """
        body = {
	        "data": "test code"
        }
        qr_response = client.post("/qr", json=body)
        self.assertAlmostEquals(qr_response.status_code, 200)
        with Image.open(self.known_good_image_path) as img_expected, \
             Image.open(BytesIO(qr_response.content)) as response_image:
            img_expected = img_expected.convert('1')
            response_image = response_image.convert('1')
            diff_img = ImageChops.difference(response_image, img_expected).getbbox()
        self.assertIsNone(diff_img, "Generated image does not match expected image")
        # os.remove(self.created_img_path)
        print(qr_response)
