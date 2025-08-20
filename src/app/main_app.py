""" Main entry point for the FastAPI RESTful API. """
import uvicorn
from fastapi import FastAPI
from src.app.routes.qr import router as qr_router

app = FastAPI()
app.include_router(qr_router)
if __name__ == '__main__':
    uvicorn.run(app)
