""" Module to create the RateLimitConfig object for test and production app"""

import os
import dotenv
from typing import Optional, Dict, Any
from redis.exceptions import ConnectionError
from src.app.ratelim.models.rate_limit_config import RateLimitConfig
from src.app.ratelim.service.data_store_manager import RedisStore, InMemoryStore
from src.app.exceptions.data_store_conn_error import DataStoreConnectionError

def get_rate_limiter_instance(test_config: Optional[Dict[str, Any]]):
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
        in_memory_cap = int(test_config.get("in_memory_cap", 100))
        cooldown_time = int(test_config.get("cooldown_time", 30))
        num_requests = int(test_config.get("num_requests", 10))
        data_store = InMemoryStore(in_memory_cap)
        activity = test_config.get("activity", "qr_code_gen")
    else:
        dotenv.load_dotenv()
        cooldown_time = int(os.getenv("RATE_LIMITER_COOLDOWN"))
        num_requests = int(os.getenv("RATE_LIMITER_REQUESTS"))
        activity = os.getenv("RATE_LIMITER_QR_ACTIVITY")
        try:
            data_store = RedisStore.create()
        except DataStoreConnectionError:
            # an issue with redis upon getting the instance
            in_memory_cap = int(os.getenv("RATE_LIMITER_IN_MEMORY_CAP"))
            data_store = InMemoryStore(in_memory_cap)
            #data_store = MemoryRateLimiter(rate_limit_config)
    rate_limit_config = RateLimitConfig(
        data_store=data_store,
        cooldown_time=cooldown_time,
        num_requests=num_requests,
        activity=activity
    )
    return rate_limit_config