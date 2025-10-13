"""Service class to provide the QR code injections"""


from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR 
from src.app.models.qr_code_image import QRCodeImage
from src.qr.utils.QRCodeFactory import QRCodeFactory
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel
from src.app.log.logger import Logger



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
    logger = Logger.get_logger()
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
        logger.info("QR code generation successful")
    except OSError as exc:
        message = f'error in reading file at {file_path}. Please contact your admin'
        logger.exception("An error has occurred", message)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=message) from exc
    except ValueError as exc:
        message = f'Bad request. Check your input. Message={str(exc)}'
        logger.exception("An error has occurred", message)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail=message) from exc
