"""Module to create QR codes and its dependencies (like input analyzer, encoder et al.)
"""

from src.qr.QRCode import QRCode
from src.qr.QRCodeImage import QRCodeImage
from src.qr.QRCodeEncoder import QRCodeEncoder
from src.qr.QRCodeInputAnalyzer import QRCodeInputAnalyzer
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel
from src.qr.QRCodeFormatInfo import QRCodeFormatInfoEncoder

class QRCodeFactory:

    @staticmethod
    def create_qr_code_obj(version: int, error_correction_level: QRErrorCorrectionLevel, image_path: str) -> QRCode:
        """Factory method to create QR code objects and its dependencies.

        Args:
            image_path (str): path to where the image needs to be created

        Returns:
            QRCode: an instance of a QR Code object
        """
        qr_encoder = QRCodeEncoder(version, error_correction_level, QRCodeInputAnalyzer())
        qr_format_encoder = QRCodeFormatInfoEncoder(getattr(qr_encoder, 'error_correction_level'))
        qr_code_gen = QRCodeImage(version, qr_encoder, qr_format_encoder, 1)
        qr = QRCode(image_path, qr_code_gen)
        return qr
