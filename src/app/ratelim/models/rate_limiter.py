""" A model to denote the entries that are expected in the Rate Limiter """

import re
from datetime import date
from pydantic import BaseModel, AfterValidator, Field
from typing_extensions import Annotated


def check_application_server_ip(value: str):
    """ Validation of whether the supplied IP is a valid IPv4
    Args:
        value (str): IPv4 from the server where the application is running
    """
    regex = re.compile(r"^([1-9][0-9])|([1-2][1-9][1-5])\.([1-9]{1,3}\.){2}\.[1-9]{3}")
    match_val = regex.match(value)
    if not match_val:
        raise ValueError(f'IP {value} is not a valid IP value')
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
    ip: Annotated[str, AfterValidator(check_application_server_ip)]
    requests_left: Annotated[int, Field(ge=0)]
    eviction_date: Annotated[float, Field(type=int | float)]
