""" Module with the router for QR code related features"""

import uuid #for now, generates the temp file on disk with UUID.
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from src.app.models.qr_code_image import QRCodeImage
from src.app.services.qr_code_service import create_qr_code

router = APIRouter()

FILE_PATH = os.path.join(Path(__file__).parent.parent, "static")  #TODO: set this up in a config file...

@router.post("/qr")
async def generate_qr_code(payload: QRCodeImage):
    """ Generate a QR Code based on the request data

    Args:
        data (QRModel): a Pydantic representation of a QR code model,
                        based on the app model

    Returns:
        FileResponse: a binary descriptor of the QR code image generated
    """
    try:
        # adds a uuid to filename to reduce collision chance with tempfile naming algorithm
        filename = f'{uuid.uuid4()}'
        file_data = None
        with tempfile.NamedTemporaryFile(prefix=filename, suffix='.png', dir=FILE_PATH) as file_dir:
            create_qr_code(payload, None, None, file_dir)
            file_dir.seek(0) # this is required to set the offset to the beginning of the file
            file_data = file_dir.read() # this is a bytes file - readlines will not work here...
        return Response(file_data, media_type='image/png')
    except (OSError, RuntimeError) as exc:
        return JSONResponse({
            "message": f'An error has occurred while processing your request: {exc.strerror}'
        }, status_code=500)
