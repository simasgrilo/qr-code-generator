""" Main entry point for the FastAPI RESTful API. """

import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.routes.qr import get_qr_router as qr_router, qr_route_custom_exception_handler
from src.app.ratelim.service.rate_limit_config_builder import get_rate_limiter_instance
from src.app.config import read_cors_config

def create_app(test_config: Dict[str,str] = None) -> FastAPI:
    """Factory function to allow injection of test dependencies
    Args:
        test_config (dict): A dictionary containing rate limiter config
                        and a mocked data_store for testing.
    """
    dotenv_path = os.path.join(Path(__file__).parent.parent.resolve(), '.env')
    load_dotenv(dotenv_path, override=True)   
    config = get_rate_limiter_instance(test_config)
    app = FastAPI()
    qr_route_custom_exception_handler(app)
    allowed_origins = read_cors_config()
    app.add_middleware(CORSMiddleware,
                       allow_origins=allowed_origins,
                       allow_credentials=True,
                       allow_methods=['*'],
                       allow_headers=['*'])
    app.include_router(qr_router(config))
    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run(app)

