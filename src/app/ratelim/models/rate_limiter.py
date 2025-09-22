""" A model to denote the entries that are expected in the Rate Limiter """

import ipaddress
from pydantic import BaseModel, AfterValidator, Field
from typing_extensions import Annotated
from typing import Union


def validate_ipv4_request_address(value: str) -> str:
    """ Validation of whether the supplied IP is a valid IPv4
    Args:
        value (str): IPv4 from the server where the application is running
    """
    if value.lower() == 'localhost':
        return value
    try: 
        ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        raise ValueError(f'IP {value} is not a valid IPv4 value')
    return value

class RateLimiterModel(BaseModel):
    """ Class to model a valid entry in redis containing the required
        fields and functionalities to update the entry. Each row
        retrieved in Redis will be mapped to a valid instance of a RateLimiter
        class.

    Args:
        BaseModel (pydantic.BaseModel): Basic model component of Pydantic module, to be
                                        extended and used as required by client applications
    """
    ip: Annotated[str, AfterValidator(validate_ipv4_request_address)]
    requests_left: Annotated[int, Field(ge=0)]
    eviction_date: Annotated[Union[int | float], Field(type=int | float)]
