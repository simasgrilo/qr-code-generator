""" Module that holds custom exceptions in the backend application"""


class DataStoreConnectionError(ConnectionError):
    """ Exception to be raised whenever a connection to the data store fails
       it does not depend on the datastore, so the main application (logic layer)
       will catch this, instead of a data store specific exception
       (e.g., redis.exceptions.ConnectionError)
    """
    def __init__(self, message: str = "Failed to connect to the rate limiting data store"):
        self.message = message
        super().__init__(message)
