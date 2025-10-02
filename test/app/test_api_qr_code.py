""" API integration tests """
import unittest
import os
from pathlib import Path
from io import BytesIO
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_429_TOO_MANY_REQUESTS, HTTP_422_UNPROCESSABLE_ENTITY
from PIL import Image, ImageChops
from src.app.main_app import create_app as app
from src.app.ratelim.service.redis_manager import MockRedis



class TestBasicAPIOperations(unittest.TestCase):
    """Class to test basic API operations - mainly retrieving a valid QR code image

    Args:
        unittest (unittest.TestCase): inherits from TestCase as the base test case in unittest
    """

    def setUp(self):
        self.known_good_image_path = os.path.join(Path(__file__).parent, 'static', 'good_qr_code.png')
        self.test_headers = {"X-Forwarded-For": "127.0.0.1"}
        test_config = {
            "data_store" : MockRedis(),
            "cooldown_time" : 60,
            "num_requests" : 20,
            "activity" : "qr_code_gen"
        }
        self.client = TestClient(app(test_config))

    def test_create_qr_code(self):
        """ Basic integration automated test to guarantee that the generated
            image matches the known good image
        """
        body = {
	        "data": "test code"
        }
        qr_response = self.client.post("/qr", json=body, headers=self.test_headers)
        self.assertEqual(qr_response.status_code, HTTP_200_OK)
        with Image.open(self.known_good_image_path) as img_expected, \
             Image.open(BytesIO(qr_response.content)) as response_image:
            img_expected = img_expected.convert('1')
            response_image = response_image.convert('1')
            diff_img = ImageChops.difference(response_image, img_expected).getbbox()
        self.assertIsNone(diff_img, "Generated image does not match expected image")

    def test_create_qr_code_invalid_payload(self):
        """ Test method to confirm that an invalid payload
            without data which is a mandatory field returns
            HTTP status code 422 - Unprocessable entity
        """
        body = {
	        "notvalidfield": "invalid value"
        }
        qr_response = self.client.post("/qr", json=body, headers=self.test_headers )
        self.assertEqual(qr_response.status_code, HTTP_422_UNPROCESSABLE_ENTITY)

    def test_api_call_with_auto_params(self):
        """Method to test functionality of processing "Auto" parameters
           which triggers the feature to calculate the minimum version and ECL that
           fits the QR code text.
        """
        super().setUp()
        body = {
	        "data": "test code",
            "version": "Auto",
            "errorCorrectionLevel": "Auto"
        }
        response = self.client.post('/qr', json=body, headers=self.test_headers)
        self.assertEqual(response.status_code, HTTP_200_OK)

class TestAPIRateLimiter(unittest.TestCase):
    """Class to test rate limiting functionalities

    Args:
        unittest (unittest.TestCase): inherits from TestCase as the base test case in unittest
    """
    def setUp(self):
        super().setUp()
        test_config = {
            "data_store" : MockRedis(),
            "cooldown_time" : 60,
            "num_requests" : 20,
            "activity" : "qr_code_gen"
        }
        self.client = TestClient(app(test_config))
        self.rate_limit = test_config.get("num_requests")
        self.body = {
	        "data": "test code"
        }
        self.test_headers = {"X-Forwarded-For": "127.0.0.1"}


    def test_rate_limit_calls_in_range(self):
        """ Method to test that the rate limiting allows requests 
            up to the last possible available token.
        """
        status = HTTP_200_OK
        for _ in range(self.rate_limit):
            response = self.client.post("/qr", json=self.body, headers=self.test_headers)
            status = response.status_code
        self.assertEqual(status, HTTP_200_OK)

    def test_rate_limit_exceed_calls(self):
        """ Methdo to test that once more requests are made 
            than what's available, the user will get throttled
        """
        status = HTTP_200_OK
        for _ in range(self.rate_limit + 2):
            response = self.client.post("/qr", json=self.body, headers=self.test_headers)
            status = response.status_code
        self.assertEqual(status, HTTP_429_TOO_MANY_REQUESTS)
