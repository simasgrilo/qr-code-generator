"""Module containing the class that define the encoding types of data that will be encoded in a QR code."""

class QRCodeAnalyzer:
    """Class to analyze QR code input according to the ISO/IEC 18004:2015 standard.
        This class determines the type of QR code that can be generated based on the input string, by heuristically checking the smallest possible encoding set
        that can be used to encode the input string.
        The supported types are:
        Numerical (Numeric) - from 0 to 9
        Alphanumeric - from 0 to 9, uppercase english letters, and the symbols $, %, *, +, -, ., /,:, and space 
        Byte - any character in the ISO-8859-1 character set (original ASCII set)
        Kanji - characters from the Shift JIS character set, which includes Japanese characters and some symbols.
        Note: current version does not support ECI.
    """

    def analyse(self, input_string: str) -> str:
        """Analyze the input string and return the type of QR code it can generate."""
        #TODO this can be better implemented without a set of ifs...
        if self.is_numeric(input_string):
            return "Numeric"
        if self.is_alphanumeric(input_string):
            return "Alphanumeric"
        if self.is_byte(input_string):
            return "Byte"
        if self.is_kanji(input_string):
            return "Kanji"
        return "Unknown"

    def is_numeric(self, input_string: str) -> bool:
        """Check whether the input string comprises only numeric characters."""
        return all(char.isdigit() for char in input_string)

    def is_alphanumeric(self, input_string: str) -> bool:
        """
        Check whether the input string comprises only alphanumeric characters.
        Args:
            input_string (str): _description_

        Returns:
            bool: _description_
        """
        input_string = input_string.upper() # to handle lowercase letters
        alphanumeric_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ#%*+-./;: "
        return all(char in alphanumeric_chars for char in input_string)

    def is_byte(self, input_string: str) -> bool:
        """
        Check whether the input string fits in the original byte set by converting the current char to its ordinal byte representation value
        Args:
            input_string (str): _description_

        Returns:
            bool: whether all elements in the input string are in the range of 0 to 127
        """
        return all(ord(char) in range(32, 127) for char in input_string) # ignore control characters and extended ASCII

    def is_kanji(self, input_string: str) -> bool:
        """ Check whether the input string comprises only Kanji (double-byte Shift JIS characters).
            this implementation follows the JIS X 0208:1997 byte map, where each character is represented by two bytes.
            Proceed by encoding it to shift JIS and checking if the bytes fall within the valid range for Kanji characters following the JIS x 0208 parity rule
        """
        hex_str = input_string.encode('shift-jis')
        first_byte_parity = -1
        for index in range(len(input_string)):
            if index % 2 == 0:
                # first byte
                first_byte_parity = (hex_str[index] & 1) == 0
                if not (0x81 <= hex_str[index] <= 0x9F) and not (0xE0 <= hex_str[index] <= 0xEF): # note that katakana characters cannot be used unanbiguously.
                    return False
            else:
                # first byte is odd and the second byte is out of th specified range
                if first_byte_parity and not (0x9F <= hex_str[index] <= 0xFC):
                    return False
                # first byte is even and the second byte is out of the specified range
                if not first_byte_parity and ( not (0x40 <= hex_str[index] <= 0x9E) or hex_str[index] == 0x7F):
                    return False
        return len(hex_str) % 2 == 0 # Kanji characters must be in pairs - decoded string will have an even length.
    