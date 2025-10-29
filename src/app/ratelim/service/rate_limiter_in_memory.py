"""Module to add a fallback to when Redis is down: the idea is to use a LRUCache that will be dropped once Redis is back"""

import time
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from src.app.ratelim.models.rate_limiter import RateLimiterModel
from src.app.ratelim.service.rate_limiter_intf import RateLimiterInterface
from src.app.ratelim.models.rate_limit_config import RateLimitConfig


class MemoryRateLimiter(RateLimiterInterface):
    """In memory rate limiter. a fallback for when the Redis service is down.

    Args:
        RateLimiterInterface (abc.ABC): Abstract base class that defines the storage service
    """
    
    def __init__(self, config: RateLimitConfig):
        self.max_size = config.max_size
        self.cooldown_time = config.cooldown_time
        self.num_requests = config.num_requests
        self.data_store = {}
        self.activity = config.activity
        self.num_keys = 0
        
    def get(self, key: str) -> RateLimiterModel | None:
        return self.get(key)

    def set(self, key: str, value: object):
        """Method compliant with the RateLimiterInterface
           which is basically a wrapper on the underlying data store
           retrieval method

        Args:
            key (str): Hashed key to identify the record of the current user
                       being evaluated to whether they will be throttled or not
            value (object): the record with data from the user
        """
        if self.num_keys == self.max_size: 
            raise HTTPException(HTTP_429_TOO_MANY_REQUESTS,f'No requests left. Try again in a couple of seconds')
        if key not in self.data_store:
            self.num_keys += 1
        self.data_store[key] = value
        
    def check_rate_limiting(self, request: Request) -> None:
        """Method to check whether the current request needs
        to be rate limited. If it cannot be served, raises a
        NoRequestsAvailableException which will be treated
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
        self.set(record_key, new_record.model_dump())
