"""Service class to provide the QR code injections"""


from fastapi import HTTPException
from src.app.models.qr_code_image import QRCodeImage
from src.qr.utils.QRCodeFactory import QRCodeFactory
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel


def create_qr_code(qr_code_model: QRCodeImage,
                   version: int | None,
                   ecl: str | None,
                   file_path: str) -> None:
    """ Service method to be called by FastAPI QR router. 
        This is the middleware between the FastAPI endpoints and
        the business model.

    Args:
        data (str): Data to be encoded in the QR code symbol
        version (int | None): QR Code version to be used in the encoding process
        ecl (str | None): Error correction level to be used in the encoding process

    Raises:
        OSError: If the generated file cannot be opened

    Returns:
        File: A File pointer to the QR code generated image
    """
    version = qr_code_model.version
    ecl = qr_code_model.error_correction_level
    data = qr_code_model.data
    calc_version, calc_error_correction_level = QRCodeFactory.determine_min_qr_code_size(data)
    # if provided an error correction level version, cast it:
    try:
        ecl = QRErrorCorrectionLevel(ecl) if ecl else calc_error_correction_level
        if not version:
            version = calc_version
        encoder = QRCodeFactory.create_qr_code_obj(version, ecl, file_path)
        encoder.create_qr_code(data)
    except OSError as exc:
        raise HTTPException(status_code=500,
                            detail=f'error in reading file at {file_path}.'
                                    'Please contact your admin') from exc
    except ValueError as exc:
        raise HTTPException(status_code=400,
                            detail=f'Bad request. Check your input. Message={str(exc)}') from exc
