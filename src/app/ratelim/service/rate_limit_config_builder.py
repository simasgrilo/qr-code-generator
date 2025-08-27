""" Module to create the RateLimitConfig object for test and production app"""

import os
from typing import Optional, Dict, Any
import dotenv
from src.app.ratelim.models.rate_limit_config import RateLimitConfig
from src.app.ratelim.service.redis_manager import RedisManager, MockRedis

def build_rate_limit_config(test_config: Optional[Dict[str, Any]]):
    """ Factory function to create the initialization of dependencies of the app
       specified either in a .env file or for unit testing purposes

    Args:
        test_config (Optional[Dict[str, Any]]): test configuration dict
                                                which will be supplied by test methods

    Returns:
        rate_limit_config (RateLimitConfig): An object with all the rate liimting
                                             relevant configuration
    """
    if test_config:
        data_store = MockRedis()
        cooldown_time = int(test_config.get("cooldown_time", 30))
        num_requests = int(test_config.get("num_requests", 10))
        activity = test_config.get("activity", "qr_code_gen")
    else:
        dotenv.load_dotenv()
        data_store = RedisManager.create()
        cooldown_time = int(os.getenv("RATE_LIMITER_COOLDOWN"))
        num_requests = int(os.getenv("RATE_LIMITER_REQUESTS"))
        activity = os.getenv("RATE_LIMITER_QR_ACTIVITY")
    rate_limit_config = RateLimitConfig(data_store=data_store,
                    cooldown_time=cooldown_time,
                    num_requests=num_requests,
                    activity=activity)
    return rate_limit_config