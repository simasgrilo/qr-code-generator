""" Utility class to manage parameters passed as the Rate limiter config"""

from pydantic import BaseModel, ConfigDict
from src.app.ratelim.service.rate_limiter_intf import RateLimiterInterface

class RateLimitConfig(BaseModel):
    """ Model class to model a Rate Limiter configuration object

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic on which the model is based
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data_store: RateLimiterInterface
    cooldown_time: float
    num_requests: int
    activity: str
