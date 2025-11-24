""" Module to manage redis connectivity and operations"""

import os
# note: no redis.asyncio here. we need the
# rate limiter check sync with the app
import heapq
from redis import Redis
from redis.exceptions import ConnectionError
from src.app.ratelim.service.rate_limiter_intf import RateLimiterInterface
from src.app.exceptions.data_store_conn_error import DataStoreConnectionError

class RedisStore(RateLimiterInterface):
    """ Utility class to interface with Redis as the underlying data store
        required for decoupling and better testability of the Rate limiter
        service

    Args:
        RateLimiter (class): Super class 
        that describes a common interface for the rate limiter
    """

    def __init__(self, redis_host: str, redis_port: int, username: str, password: str):
        try:
            self.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis.ping()
        except ConnectionError as exc:
            raise DataStoreConnectionError from exc

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
            return RedisStore(redis_host, redis_port, username, password)
        except ConnectionError as exc:
            raise DataStoreConnectionError from exc

import json
class InMemoryStore(RateLimiterInterface):
    """Mock class to mimic a key value store but in memory
       this is only to be used within unit tests!!!

    Args:
        RateLimiterInterface (object): the interface to describe a rate limiting interface
                                       any class that functions like the rate limiting class
                                       needs to implement these methods.
    """
    def __init__(self, memory_cap: int):
        self.store = {}
        self.memory_cap = memory_cap
        self.num_keys = 0
        self.oldest_record = []

    def get(self, key):
        return self.store.get(key)

    def set(self, key: str, value: dict):
        """Method to set a value bounded to a key
           this implementation considers a LRU-like cache policy
           to avoid having memory overflow if the map gets too big.

        Args:
            key (str): key of the record being set
            value (dict): a hash table (dict) having the entries referring to the current user request.
        """
        if self.num_keys == self.memory_cap:
            # this doesn't look thread safe
            self._clear()
        # FIX: your current record structure does not work because you can have equal timestamp for two records. So if you use a tuple, the
        # default behavior of __lt__ of a tuple is to try to compare elements from the left to the right.
        # transform this to an object and redefine the __lt__ relation...
        elif key not in self.store:
            self.num_keys += 1
        heapq.heappush(self.oldest_record, (value["eviction_date"], key))
        self.store[key] = value
    
    def _clear(self):
        """Method to release the current oldest record based on the value of eviction date and the 
           current value of eviction date. This uses a "lazy deletion" strategy of the heap,
           in which we'll only consider valid the entry containing the same eviction date as the one
           referred to the key
        """
        while self.oldest_record:
            curr_eviction_date, curr_key = heapq.heappop(self.oldest_record)
            data_for_curr_key = self.get(curr_key)
            if data_for_curr_key and curr_eviction_date == data_for_curr_key['eviction_date']:
                del self.store[curr_key]
                self.num_keys -= 1
                break
