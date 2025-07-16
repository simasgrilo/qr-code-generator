"""Module to maintaint he QR Code data size based on the version 4 and the error correction level."""


import enum
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel

class QRCodeDataSize(enum.Enum):
    """
    Enum representing the QR Code data sizes based on version and error correction level.
    Args:
        enum (QRErrorCorrectionLevel): enum type that model differnt error correction levels for QR codes.
    """

    DATA_SIZE = {
        "L" : {
            "NUMERIC": 187,
            "ALPHANUMERIC": 114,
            "BYTE": 78,
            "KANJI": 48
        },
        "M" : {
            "NUMERIC": 149,
            "ALPHANUMERIC": 90,
            "BYTE": 62,
            "KANJI": 38
        },
        "Q" : {
            "NUMERIC": 111,
            "ALPHANUMERIC": 67,
            "BYTE": 46,
            "KANJI": 28
        },
        "H" : {
            "NUMERIC": 82,
            "ALPHANUMERIC": 59,
            "BYTE": 34,
            "KANJI": 21
        },
    }

    @staticmethod
    def get_data_size(error_correction_level: QRErrorCorrectionLevel, mode: str) -> int:
        """
        Get the data size for a specific error correction level and mode.
        Args:
            error_correction_level (QRErrorCorrectionLevel): The error correction level.
            mode (str): The mode of the QR code (e.g., "NUMERIC", "ALPHANUMERIC", "BYTE", "KANJI").
        """
        return QRCodeDataSize.DATA_SIZE[error_correction_level.name][mode.upper()]


