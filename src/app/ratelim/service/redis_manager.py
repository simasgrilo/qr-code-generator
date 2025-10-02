""" Module to manage redis connectivity and operations"""

import os
# note: no redis.asyncio here. we need the
# rate limiter check sync with the app
from redis import Redis
from redis.exceptions import ConnectionError
from src.app.ratelim.service.rate_limiter_intf import RateLimiterInterface
from src.app.exceptions.data_store_conn_error import DataStoreConnectionError

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
        try:
            self.redis.hset(key, mapping=value)
        except ConnectionError as exc:
            raise DataStoreConnectionError from exc

    def get(self, key: object):
        """Method to check whether the request will be rate limited,
           updating the record based on the requests left.

        Args:
            key (object): id of the object to be identified, usually an IP associated with 
                          the requester.
        """
        try:
            return self.redis.hgetall(key)
        except ConnectionError as exc:
            raise DataStoreConnectionError from exc

    @staticmethod
    def create():
        """Creates a standard instance of a Redis connection manager 
        with the preset config in .env file, loaded upon server start

        Returns:
            RedisManager: Abstraction to manage the Redis interface implementation
        """
        try:
            redis_host = os.getenv("REDIS_HOST")
            redis_port = os.getenv("REDIS_PORT")
            username = os.getenv("REDIS_USERNAME")
            password = os.getenv("REDIS_PASSWORD")
            return RedisManager(redis_host, redis_port, username, password)
        except ConnectionError as exc:
            raise DataStoreConnectionError from exc

class MockRedis(RateLimiterInterface):
    """Mock class to mimic a key value store but in memory
       this is only to be used within unit tests!!!

    Args:
        RateLimiterInterface (object): the interface to describe a rate limiting interface
                                       any class that functions like the rate limiting class
                                       needs to implement these methods.
    """
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value
