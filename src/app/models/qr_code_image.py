"""FastAPI compatible model using Pydantic"""
from typing import Union
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class QRCodeImage(BaseModel):
    """Pydantic model for QRCode image class
    to be used in FastAPI
    """
    model_config = ConfigDict(alias_generator=to_camel)
    data: str
    # version: Union[int, str] = None
    version: Union[int, None] = None
    error_correction_level: Union[str, None] = None
    module_size: Union[int, None] = None

    @field_validator('version', mode='before')
    @classmethod
    def validate_version(cls, version: int):
        """Validates the version to be a valid int between 1 and 40.

        Args:
            val (int): value provided as the QR Code version

        Returns:
            int | None: a valid integer if 1 <= val <= 40, and None if val == 'Auto'
        """
        if version == 'Auto':
            return None
        int_val = int(version)
        if 1 <= int_val <= 40:
            return int_val
        return None

    @field_validator('error_correction_level', mode='before')
    @classmethod
    def validate_ecl(cls, ecl: str) -> str | None:
        """validates ECL values, and allow the special case 'Auto' to be calculated by the system

        Args:
            val (str): QR Code error correction level

        Raises:
            ValueError: raised if the provided ECL is not one of the following: 'H', 'L', 'Q' or 'M'

        Returns:
            str | None: str if a valid ECL, None if it's the 'Auto' scenario
        """
        if ecl == 'Auto':
            return None
        if ecl not in ['L','H','Q','M']:
            raise ValueError(f'Invalid error correction value type {ecl}')
        return ecl
