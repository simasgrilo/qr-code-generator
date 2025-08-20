"""FastAPI compatible model using Pydantic"""

from pydantic import BaseModel

class QRCodeImage(BaseModel):
    """Pydantic model for QRCode image class
       to be used in FastAPI
    """
    data: str
    version: int | None = None
    error_correction_level: str | None = None
    module_size: int | None = None
