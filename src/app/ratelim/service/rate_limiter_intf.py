""" Generic Rate limiter interface """

from abc import ABC, abstractmethod


class RateLimiterInterface(ABC):
    """Abstract class to provide an interface for the actual rate limiting
       services. The structure is considered to be compatible to a 
       hash-map like structure, where we can assign a value to a key
       like in the pair (key, value).
       
       The main reason for this extra abstraction layer
       is to decouple the functionality from
       the underlying infrastructure, making changing providers and
       testing easier.

    Args:
        ABC (abc.ABC): Abstract base class module from Python to simulate
                       this as an interface.
    """

    @abstractmethod
    def set(self, key: object, value: object):
        """ Method to set the pair (key, value) in the dictionary structure
        """


    @abstractmethod
    def get(self, key: object):
        """Method to check whether the request will be rate limited,
           updating the record based on the requests left.

        Args:
            key (object): id of the object to be identified, usually an IP associated with 
                          the requester.
        """
