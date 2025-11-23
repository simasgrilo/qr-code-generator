"""Module to provide connection to Redis as the rate limiter"""

import os
import time
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from src.app.ratelim.models.rate_limiter import RateLimiterModel
from src.app.ratelim.models.rate_limit_config import RateLimitConfig
from src.app.ratelim.service.rate_limiter_intf import RateLimiterInterface


class RateLimiter:
    """Concrete class to provide rate limiting functionalities with Redis
       because our API is gonna be free, every user can create up to 20 QR codes per minute
       This can easily be a microsservice but due to team design, we'll stick with a modular
       monolith for now.
    """
    # required to differ other requests from the same
    # IP that can be captured by the same Redis
    # instance.

    _instance = None


    def __new__(cls, rate_limiter_config: RateLimitConfig):
        if cls._instance is None:
            cls._instance = super(RateLimiter, cls).__new__(cls)
        return cls._instance

    def __init__(self, rate_limiter_config: RateLimitConfig):
        self.data_store = rate_limiter_config.data_store
        self.cooldown_time = rate_limiter_config.cooldown_time
        self.num_requests = rate_limiter_config.num_requests
        self.activity = rate_limiter_config.activity
        self.max_size = rate_limiter_config.max_size

    @classmethod
    def get_instance(cls, data_store: RateLimiterInterface):
        """Factory method to return an instance of
           the redis instance

        Args:
            data_store (RedisManager): a data store reference to where the rate
                                       limiter instance is setups

        Returns:
            RedisManager: RedisManager instance
        """
        num_requests = int(os.getenv("RATE_LIMITER_REQUESTS"))
        cooldown_time = int(os.getenv("RATE_LIMITER_COOLDOWN"))
        activity = os.getenv("RATE_LIMITER_QR_ACTIVITY")
        rate_limiter_config = RateLimitConfig(data_store=data_store, num_requests=num_requests, cooldown_time=cooldown_time, activity=activity)
        return RateLimiter(rate_limiter_config)

    def get(self, key: str) -> RateLimiterModel | None:
        return self.data_store.get(key)

    def set(self, key: str, value: object):
        """Method compliant with the RateLimiterInterface
           which is basically a wrapper on the underlying data store
           retrieval method

        Args:
            key (str): Hashed key to identify the record of the current user
                       being evaluated to whether they will be throttled or not
            value (object): the record with data from the user
        """
        self.data_store.set(key, value)

    def check_rate_limiting(self, request: Request) -> None:
        """Method to check whether the current request needs
        to be rate limited. If it cannot be served, raises a
        NoRequestsAvailableException which will be treated6
        by the callee.

        Args:
            ip (str): ip of the server making the request

        Raises:
            NoRequestsAvailableException: Exception denoting that there is no requests left
        """
        ip = request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else request.headers['host'].split(":")[0]
        record_key = f'{self.activity} : {ip}'
        start_cooldown_time = time.time() + self.cooldown_time
        existing_record = self.get(record_key)
        if existing_record:
            # casts the resuting record from memory to a RateLimiterModel to have the
            # same data types as expected (e.g., converting string where it is
            # an integer )
            existing_record = RateLimiterModel(ip=existing_record['ip'],
                                               requests_left=existing_record['requests_left'],
                                               eviction_date=existing_record['eviction_date'])
            wait_time = time.time() - existing_record.eviction_date
            if not existing_record.requests_left and wait_time < 0:
                raise HTTPException(HTTP_429_TOO_MANY_REQUESTS,f'No requests left. Try after {int(wait_time) * -1} seconds')
            if wait_time >= 0:
                existing_record.eviction_date = start_cooldown_time
                existing_record.requests_left = self.num_requests
            existing_record.requests_left -= 1
            self.set(record_key, existing_record.model_dump())
            return
        new_record = RateLimiterModel(ip=ip,
                                      requests_left=self.num_requests, 
                                      eviction_date=start_cooldown_time)
        self.set(record_key, new_record.model_dump_json())
