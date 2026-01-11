""" Module with the router for QR code related features"""

import uuid #for now, generates the temp file on disk with UUID.
import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE
from src.app.models.qr_code_image import QRCodeImage
from src.app.services.qr_code_service import create_qr_code
from src.app.ratelim.service.rate_limiter import RateLimiter
from src.app.ratelim.models.rate_limit_config import RateLimitConfig
from src.app.exceptions.data_store_conn_error import DataStoreConnectionError
from src.app.log.logger import Logger

# fix: adding a generic exception handler to deal with the case
# where a dependency raises an exception. This happens between the
# endpoint call and the FastAPI instantiation, and FastAPI only 
# allows custom exception handlers to be attached to the FastAPI instance
# see https://fastapi.tiangolo.com/tutorial/handling-errors/?h=hand#install-custom-exception-handlers 
# for more info

def qr_route_custom_exception_handler(app: FastAPI):
    """Route handler for the FastAPI object

    Args:
        app (FastAPI): Main API object, denoting our
    """
    @app.exception_handler(DataStoreConnectionError)
    async def datastore_connection_error_handler(request: Request, exception: DataStoreConnectionError):
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            content={
            "message": "An error has occurred! Please try again after a couple of seconds, and reach out the administrator if the problem persists"
        })


def  get_qr_router(rate_limiter_config : RateLimitConfig) -> APIRouter:
    logger = Logger.get_logger()
    router = APIRouter()
    #file_path = os.path.join(Path(__file__).parent.parent, "static")
    file_path = os.path.join(Path(__file__).parent.parent, "static")
    try:
        config_file_path = os.getenv("QR_FILE_PATH")
        if os.path.isdir(config_file_path):
            file_path = Path(config_file_path)
    except OSError:
        pass
    except TypeError:
        logger.info(f'Defaut QR code temp folder is ${file_path}')

    #rate limiting is set by route, but created elsewhere:
    rate_limiter = RateLimiter.get_instance(rate_limiter_config.data_store)
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
            with tempfile.NamedTemporaryFile(prefix=filename, 
                                             suffix='.png', 
                                             dir=file_path) as file_dir:
                create_qr_code(payload, None, None, file_dir)
                file_dir.seek(0) # this is required to set the offset to the beginning of the file
                file_data = file_dir.read() # this is a bytes file - readlines will not work here...
            return Response(file_data, media_type='image/png')
        except (OSError, RuntimeError) as exc:
            print(f'error: ${file_path}')
            logger.error(f'Error occurred: cannot access ${file_path}')
            return JSONResponse({
                "message": f'An error has occurred while processing your request: {exc.strerror}'
            }, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    return router
