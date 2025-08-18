""" Main entry point for the FastAPI RESTful API. """
import uvicorn
from fastapi import FastAPI
from src.app.routes.qr import router as qr_router

app = FastAPI()

# def generate_num():
#     for index in range(100):
#         yield 100 - index

# generator = generate_num()

# print(generate_num())

@app.get('/')
async def root():
    return {"message": "Alive and Kicking"}

app.include_router(qr_router)

if __name__ == '__main__':
    uvicorn.run(app)
