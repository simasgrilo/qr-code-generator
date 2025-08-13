"""Module to create QR codes and its dependencies (like input analyzer, encoder et al.)
"""

from src.qr.QRCode import QRCode
from src.qr.QRCodeImage import QRCodeImage
from src.qr.QRCodeEncoder import QRCodeEncoder
from src.qr.QRCodeInputAnalyzer import QRCodeInputAnalyzer
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel
from src.qr.QRCodeFormatInfo import QRCodeFormatInfoEncoder

class QRCodeFactory:
    """Factory class for QR Code objects
       this should be the main entry point for QR Code object creation

    Returns:
        QRCode: an object that has all the functionalities required to create a QR Code.
    """
    @staticmethod
    def create_qr_code_obj(version: int,
                           error_correction_level: QRErrorCorrectionLevel,
                           image_path: str) -> QRCode:
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

    @staticmethod
    def determine_min_qr_code_size(data: str):
        """Method to determine automatically the minimum QR code version and ECL
           that fits the inpput data, based on the number of data bits that the
           encoded input has, based on the values of Table 7 of the ISO.

        Args:
            data (str): raw data, before enccoding

        Returns:
            version, error_correction_code (Tuple[Int, QRErrorCorrectionLevel]): 
            A tuple containing the minimum version and error correction level that 
            the data being encoded fits.
        """
        # special dummy object to access encoding methods...
        phantom_encoder = QRCodeEncoder(None, None, QRCodeInputAnalyzer())
        encoded_data = phantom_encoder.encode_data_into_bit_stream(data)
        number_data_bits = len(encoded_data)
        error_correction_codes = [ qr_ecl for qr_ecl in QRErrorCorrectionLevel ]
        for version in range(1, 40):
            for error_corr_code in error_correction_codes:
                if number_data_bits <= error_corr_code.get_numbers_of_bits_per_codewords(version):
                    return (version, error_corr_code)
        return None
