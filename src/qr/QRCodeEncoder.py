""" module to determine the error correction level of a QR code """

from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel

class QRCodeEncoder:
    """
    QR Code encoder - implemetation of the algorithmic steps described in section 7.4.2 to 7.4.6 as per ISO 18004:2015 standard.
    """
    def __init__(self, level: QRErrorCorrectionLevel):
        """
        Initialize the QRErrorCorrection with a specific error correction level.
        
        Args:
            level (QRErrorCorrectionLevel): The error correction level to set.
        """
        self.error_correction_level = level
        
    @staticmethod
    def get_mode_indicator(mode: str) -> bin:
        """
        Get the mode indicator for a specific mode.
        
        Args:
            mode (str): The mode of the QR code (e.g., "NUMERIC", "ALPHANUMERIC", "BYTE", "KANJI").
        
        Returns:
            int: The mode indicator as an integer.
        """
        try:
            mode_indicators = {
                "NUMERIC": b'0001',
                "ALPHANUMERIC": b'0010',
                "BYTE": b'0100',
                "KANJI": b'1000'
            }
            return mode_indicators.get(mode.upper(), None)
        except KeyError as exc:
            raise KeyError(f"Invalid mode: {mode}. Supported modes are: 'NUMERIC', 'ALPHANUMERIC', 'BYTE', 'KANJI'.") from exc
    
    @staticmethod    
    def get_char_count_indicator(mode: str) -> int:
        """Get the character count indicator per mode. for QR codes of version 1 to 9 is as below as in page 23 of the ISO 18004:2015 standard.

        Args:
            mode (str): encoding mode of the QR code data

        Returns:
            int: number of bits that the encoded data needs to have.
        """
        bit_count = {
            "NUMERIC": 10,
            "ALPHANUMERIC": 9,
            "BYTE": 8,
            "KANJI": 8
        }
        return bit_count.get(mode.upper(), None)
    
    
    def encode_input(self, input: str) -> bytes:
        """
        Encode the input string following the procedure in ISO 18004:2015.
        
        Args: 
            input (str): data to be encoded
        
        Returs:
            bytes: result of the encoding process as bytes.
        """
        
    def encode_numeric(self, input_str: str, char_count_indicator: int, mode_indicator: bytes) -> bytes:
        """
        Encode numeric data. See section 7.4.3. of ISO for details
        
        Args:
            input (str): Numeric data to encode.
        
        Returns:
            bytes: Encoded numeric data as bytes.
        """
        if mode_indicator != self.get_mode_indicator("NUMERIC"):
            raise ValueError("Invalid mode indicator for numeric encoding.")
        if char_count_indicator != self.get_char_count_indicator("NUMERIC"):
            raise ValueError("Invalid character count indicator for numeric encoding.")
        bytes_array = []
        index = 0
        while index < len(input_str):
            curr_group = input_str[index: min(index + 3, len(input_str))]
            curr_digit_group = bin(int(curr_group))[2:]  # Remove '0b' prefix
            if len(curr_group) == 3:
                padding = '0' * max(0, (char_count_indicator - len(curr_digit_group)))
            # handle edges case where the last group has less than 3 digits
            elif len(curr_group) == 2:
                padding = '0' * max(0, (7 - len(curr_digit_group)))
            else:
                # handle edges case where the last group has less than 3 digits
                padding = '0' * max(0, (4 - len(curr_digit_group)))
            bytes_array.append(padding + curr_digit_group)
            index += 3
        print(bytes_array)
        bytes_array = bytes("".join(bytes_array), encoding='utf-8')
        binary_count = bin(len(input_str))
        padding = "0" * (char_count_indicator - len(binary_count))
        binary_count = bytes(padding + binary_count[2:], encoding='utf-8')  # Remove '0b' prefix
        return mode_indicator + binary_count + bytes_array

    @staticmethod
    def get_encode_decode_table_alphanumeric(character: str) -> dict:
        """
        Get the encoding and decoding table for alphanumeric mode.
        Raise:
            KeyError: if the character is out of the range of valid alphanumeric characters.
        Returns:
            dict: a dictionary mapping alphanumeric characters to their corresponding values.
        """
        try:
            char_map =  {
                '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19,
                'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29,
                'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35, ' ': 36, '$': 37, '%': 38, '*': 39,
                '+': 40, '-': 41, '.': 42, '/': 43, ':': 44
            }
            return char_map.get(character.upper(), None)
        except KeyError as exc:
            raise KeyError(f"Invalid character: {character}. Supported characters are alphanumeric characters and the symbols $, %, *, +, -, ., /,:, and space.") from exc   

    def encode_alphanumeric(self, input_str: str, char_count_indicator: int, mode_indicator: bytes) -> bytes:
        """
        Encode alphanumeric data. See section 7.4.4. of ISO for details.
        From the specs, if the length of the input string is odd, the last character value is encoded as a 6-bit binary number.
        Args:
            input_str (str): Alphanumeric data to encode
            char_count_indicator (int): Character count indicator for alphanumeric mode
            mode_indicator (bytes): mode indicator for alphanumeric mode

        Returns:
            bytes: a byte string with the encoded alphanumeric data.
        """
        encoded_data = []
        index = 0
        MULTIPLIER = 45  # The multiplier for alphanumeric encoding
        while index < len(input_str):
            group_data = input_str[index: min(index + 2, len(input_str))]
            # Get the value of the first and second characters in the group
            char_values = [-1,-1]
            char_values[0] = self.get_encode_decode_table_alphanumeric(group_data[0]) 
            if len(group_data) == 2:
                char_values[1] = self.get_encode_decode_table_alphanumeric(group_data[1]) if len(group_data) > 1 else 0
            if char_values[1] != -1:
                encoded_group = (char_values[0] * MULTIPLIER + char_values[1])
                encoded_data.append(bin(encoded_group)[2:].zfill(11))
            else:
                encoded_data.append(bin(char_values[0])[2:].zfill(6))
            index += 2
        return bytes("".join(encoded_data), encoding='utf-8')
