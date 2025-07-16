""" Module to hold codeword block as a data class"""

class QRCodeCodewordBlock:
    """Class to model the last column of Table 9 from the ISO 18004.
    """
    def __init__(self, total_codewords: int, number_of_data_codewords: int, error_correction_capacity: int):
        self._codewords = total_codewords #[None for _ in range(total_codewords)]
        self._data_codewords = number_of_data_codewords #[None for _ in range(number_of_data_codewords)]
        self._error_correction_capacity = error_correction_capacity
        
    
    def data_codewords(self):
        """Getter method for the number of data codewords of a block"""
        return self._data_codewords

    def total_codewords(self):
        """Getter method for the total sum of codewords of a block"""
        return self._codewords
    
    def error_correction_capacity(self):
        """Getter method to get the error correction capactiy (for completeness)"""
        return self._error_correction_capacity