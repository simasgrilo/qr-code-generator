""" Module to manage redis connectivity and operations"""

import os
# note: no redis.asyncio here. we need the
# rate limiter check sync with the app
from redis import Redis
from src.app.ratelim.service.rate_limiter_intf import RateLimiterInterface

class RedisManager(RateLimiterInterface):
    """ Utility class to interface with Redis as the underlying data store
        required for decoupling and better testability of the Rate limiter
        service

    Args:
        RateLimiter (class): Super class 
        that describes a common interface for the rate limiter
    """

    def __init__(self, redis_host: str, redis_port: int, username: str, password: str):
        self.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)

    def set(self, key: str, value: dict):
        """ Method to set the pair (key, value) in the Redis instance
        """
        self.redis.hset(key, mapping=value)

    def get(self, key: object):
        """Method to check whether the request will be rate limited,
           updating the record based on the requests left.

        Args:
            key (object): id of the object to be identified, usually an IP associated with 
                          the requester.
        """
        return self.redis.hgetall(key)

    @staticmethod
    def create():
        """Creates a standard instance of a Redis connection manager 
        with the preset config in .env file, loaded upon server start

        Returns:
            RedisManager: Abstraction to manage the Redis interface implementation
        """
        redis_host = os.getenv("REDIS_HOST")
        redis_port = os.getenv("REDIS_PORT")
        username = os.getenv("REDIS_USERNAME")
        password = os.getenv("REDIS_PASSWORD")
        return RedisManager(redis_host, redis_port, username, password)

class MockRedis(RateLimiterInterface):
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
