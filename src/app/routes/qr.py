""" Module with the router for QR code related features"""

import uuid #for now, generates the temp file on disk with UUID.
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from src.app.models.qr_code_image import QRCodeImage
from src.app.services.qr_code_service import create_qr_code
from src.app.ratelim.service.rate_limiter_service import RateLimiterService
from src.app.ratelim.models.rate_limit_config import RateLimitConfig


def get_qr_router(rate_limiter_config : RateLimitConfig) -> APIRouter:
    router = APIRouter()
    FILE_PATH = os.path.join(Path(__file__).parent.parent, "static")
    #rate limiting is set by route, but created elsewhere:
    rate_limiter = RateLimiterService.get_instance(rate_limiter_config.data_store)

    @router.post("/qr", dependencies=[Depends(rate_limiter.check_rate_limiting)])
    async def generate_qr_code(payload: QRCodeImage):
        """ Generate a QR Code based on the request data

        Args:
            data (QRModel): a Pydantic representation of a QR code model,
                            based on the app model

        Returns:
            FileResponse: a binary descriptor of the QR code image generated
        """
        try:
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
            }, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    return router
