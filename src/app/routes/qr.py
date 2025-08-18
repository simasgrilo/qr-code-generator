""" Module with the router for QR code related features"""

import uuid #for now, generates the temp file on disk with UUID.
import os
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from src.app.models.qr_code_image import QRCodeImage
from src.app.services.qr_code_service import create_qr_code

router = APIRouter()

FILE_PATH = "static" #TODO: set this up in a config file...

@router.post("/qr", response_model=QRCodeImage)
async def generate_qr_code(payload: QRCodeImage):
    """ Generate a QR Code based on the request data

    Args:
        data (QRModel): a Pydantic representation of a QR code model,
                        based on the app model

    Returns:
        FileResponse: a binary descriptor of the QR code image generated
    """
    try:
        filename = f'{uuid.uuid4()}.png'
        file_dir = os.path.join(Path(__file__).parent.parent, "static", filename)
        create_qr_code(payload, None, None, file_dir)
        return FileResponse(file_dir, media_type='image/png')
    except OSError:
        return JSONResponse({
            "message": "An error has occurred while processing your request"
        }, status_code=500)
