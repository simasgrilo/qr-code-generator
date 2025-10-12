from abc import ABC

class StorageStrategy(ABC):
    """Class to define an abstract storage strategy, rathen than the standard logging strategy."""
    
    
    def setup(self):
        """Setup the configuration
        """
        pass
    
    def save(self):
        """Save the information
        """
        pass