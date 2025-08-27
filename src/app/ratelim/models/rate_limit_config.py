""" Utility class to manage parameters passed as the Rate limiter config"""

from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    """ Model class to model a Rate Limiter configuration object

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic on which the model is based
    """
    data_store: object #RateLimiterInterface
    cooldown_time: float
    num_requests: int
    activity: str
