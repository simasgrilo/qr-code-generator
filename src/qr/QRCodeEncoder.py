""" module to implement the QR Code encoding process
    from input parser analysis and encoding to polynomial
    division, data and error codewords generation and encoding (up to section 7.6 of ISO 18004)
"""

from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel
from src.qr.QRCodeInputAnalyzer import QRCodeInputAnalyzer
from src.qr.error.utils.QRCodePolynomial import PolynomialOperations, IntPolynomial, Term

class QRCodeEncoder:
    """
    QR Code encoder - implemetation of the algorithmic steps described in section 7.4.2 to 7.4.6 as per ISO 18004:2015 standard.
    """
    def __init__(self, version: int, level: QRErrorCorrectionLevel, analyzer: QRCodeInputAnalyzer):
        """
        Initialize the QRErrorCorrection with a specific error correction level for a specific version
        
        Args:
            level (QRErrorCorrectionLevel): The error correction level to set.
        """
        self.version = version
        self.error_correction_level = level
        self.analyzer = analyzer

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

    def get_remainder_bits(self):
        """Method to return the remainder bits to be appended to every codeword message as per
           Table 1.
        """
        remainder_bits = {
            1: 0, 2: 7, 3: 7, 4: 7, 5: 7, 6: 7, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0,
            12: 0, 13: 0, 14: 3, 15: 3, 16: 3, 17: 3, 18: 3, 19: 3, 20: 3, 21: 4, 22: 4,
            23: 4, 24: 4, 25: 4, 26: 4, 27: 4, 28: 3, 29: 3, 30: 3, 31: 3, 32: 3, 33: 3,
            34: 3, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0
        }
        return remainder_bits[self.version]

    def encode_input(self, input_str: str) -> bytes:
        """
        Encode the input string following the procedure in ISO 18004:2015.
        
        Args: 
            input (str): data to be encoded
        
        Returs:
            bytes: result of the encoding process as bytes.
        """

        encoded_data = self.encode_data_into_bit_stream(input_str)
        final_encoded_data = self._add_terminator_and_padding(encoded_data)
        return final_encoded_data

    def encode_data_into_bit_stream(self, input_str: str) -> bytes:
        """Encodes only the bit stream part (sections 7.4.2 to 7.4.7) of the characters as in ISO 18004:2015
           This only support modes BYTE, NUMERIC, ALPHANUMERIC and KANJI.
        Args:
            input_str (str): the data itself to be encoded

        Raises:
            ValueError: if the data is not in a format currently supported by the implementation

        Returns:
            bytes: the bit stream encoded following the ISO rules.
        """
        encoding_mode = self.analyzer.analyse(input_str).upper()
        encoding_char_count_indicator = self.get_char_count_indicator(encoding_mode)
        mode_indicator = self.get_mode_indicator(encoding_mode)
        match encoding_mode:
            case 'NUMERIC':
                return self.encode_numeric(input_str, encoding_char_count_indicator, mode_indicator)
            case 'ALPHANUMERIC':
                return self.encode_alphanumeric(input_str, encoding_char_count_indicator, mode_indicator)
            case 'BYTE':
                return self.encode_bytes(input_str, encoding_char_count_indicator, mode_indicator)
            case 'KANJI':
                return self.encode_kanji(input_str.encode(encoding='shift-jis'), encoding_char_count_indicator, mode_indicator)
            case _:
                raise ValueError(f"Unknown format of string {input_str}. Please correct your input and try again")

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
    
    
    def encode_bytes(self, input_str: str, char_count_indicator: int, mode_indicator: bytes ) -> bytes:
        """
        Encode byte data. See section 7.4.5. of ISO for details.
        Note that this encoding follows hte same standard as in ISO/IEC 8859-1, which subsumes ascii encoding.
        We can use the currently encoding table to map the byte to the character.
        Each character is encoded as an 8-bit binary number.
        Args:
            input_str (str): Byte data to encode.
            char_count_indicator (int): Character count indicator for byte mode.
            mode_indicator (bytes): Mode indicator for byte mode.
        
        Returns:
            bytes: Encoded byte data as bytes.
        """
        if char_count_indicator != self.get_char_count_indicator("BYTE"):
            raise ValueError("Invalid character count indicator for byte encoding.")
        if mode_indicator != self.get_mode_indicator("BYTE"):
            raise ValueError("Invalid mode indicator for byte encoding.")
        encoded_data = []
        for char in input_str:
            encoded_data.append(bin(ord(char))[2:].zfill(8))
        input_length = bytes(bin(len(input_str))[2::], encoding='utf-8')
        bits_char_count_indicator = bytes(bin(char_count_indicator)[2::].zfill(char_count_indicator), encoding='utf-8')
        return mode_indicator + bits_char_count_indicator + input_length + bytes("".join(encoded_data), encoding='utf-8')


    def encode_kanji(self, input_str: str, char_count_indicator: int, mode_indicator: bytes):
        """
        Implementation of the algorithmic encoding of Shift-JIS characters as in Section 7.4.5 of ISO 18004/2015. We need to make a series of calculations depending of the
        character:
        1) For characters with Shift JIS values from 0x8140 to 0x9FFC:
            - Subtract 0x8140 from Shift JIS value
            - Multiply the MSB of the result by 0xC0
            - Add LSB of the result to the product above
            - convert the result to a 13-bit binary string
        2) For characters with Shift JIS values from 0xE040 to 0xEBBF:
            - Subtract 0xC140 from Shift JIS value
            - Multiply most significant byte of result by 0xCO
            - Add Least significant byte to product from the product above
            - convert the result to a 13-bit binary string
        after doing this to all the characters, prefix the string withthe character count indicator and mode indicator.
        Args:
            input_str (str): the input Kanji string
            char_count_indicator (int): The character count indicator for the corresponding mode (as per ISO)
            mode_indicator (bytes): The mode indicator for the corresponding encoding mode (as per ISO)

        Raises:
            ValueError: if the character is not in the correct Shift-JIS format or it cannot be decoded as a character within the Shift-JIS two-byte representation range

        Returns:
            the encoded string as in Section 7.4.6 of the ISO
        """
        LOWER_BOUND_BYTE_1 = 0x8140
        UPPER_BOUND_BYTE_1 = 0x9ffc
        LOWER_BOUND_BYTE_2 = 0xe040
        UPPER_BOUND_BYTE_2 = 0xebbf
        BASELINE_BOUND_2 = 0xc040
        MULTIPLIER = 0xc0
        encoded_data = []
        if len(input_str) % 2:
            raise ValueError("Invalid string format. Kanji encoding require two bytes per each character. Perhaps you forgot to encode as shift-jis?")
        for index in range(0, len(input_str), 2):
            hex_bytes = int(input_str[index:index + 2].hex(), 16)
            intermediate_sub = 0
            if not(hex_bytes >= LOWER_BOUND_BYTE_1 and hex_bytes <= UPPER_BOUND_BYTE_1) and not(hex_bytes >= LOWER_BOUND_BYTE_2 and hex_bytes <= UPPER_BOUND_BYTE_2):
                raise ValueError("Invalid string format")
            if LOWER_BOUND_BYTE_1 <= hex_bytes <= UPPER_BOUND_BYTE_1: 
                intermediate_sub = hex(hex_bytes - LOWER_BOUND_BYTE_1)[2:] # get rid of the 0x from the str representation
            elif LOWER_BOUND_BYTE_2 <= hex_bytes <= UPPER_BOUND_BYTE_2:
                intermediate_sub = hex(hex_bytes - BASELINE_BOUND_2)[2:]
            intermediate_sub_msb = hex(int(intermediate_sub[0:2], 16))
            intermediate_sub_lsb = hex(int(intermediate_sub[2:4], 16))
            most_sig_byte_mult = hex(int(intermediate_sub_msb, 16) * MULTIPLIER)
            add_lsb_to_mult = bin(int(most_sig_byte_mult, 16) + int(intermediate_sub_lsb, 16))[2:]
            converted_bin_represent = bytes(add_lsb_to_mult.zfill(13), encoding='utf-8')
            encoded_data.append(converted_bin_represent)
        bin_char_count_indicator = bytes(bin(char_count_indicator)[2:], encoding='utf-8')
        bin_encoded_data = bytes()
        for data_part in encoded_data:
            bin_encoded_data += data_part
        return bin_char_count_indicator + mode_indicator + bin_encoded_data
    
    def _add_terminator_and_padding(self, encoded_input: bytes) -> bytes:
        """
        Adds the specified terminator for the encoded data (See Table 2 of ISO). For modes different that any micro QR code (M1, M2, M3 and M4),
        the terminator is always 0000. This needs to fit 4 bytes if the data length is smaller than the size, or else truncated. For more information, check sections
        7.4.9 and 7.4.10 of ISO 18004.
        note: in the ISO, a codeword is a byte for versions 1 to 40 (see section 7.4.10)
        The algorithm is as follows:
        1) position the codeword 0000 to fit the last byte (it needs to have 8 characters)
        2) if even after adding up to 0000, add more 000 until it is a complete byte -> 4 bits + extra padding to totalize a byte after the least
           significant bit of the data stream
        3) if after adding the padding zeroes it still does not fit the number of codewords, add bytes 11101100 and 00010001 alternatively 

        Args:
            encoded_input (bytes): encoded input in bytes format produced based on the detected encoding format

        Returns:
            bytes: a stream of bytes with padding zeroes appended to the original encoded data.
        """
        codeword_per_version_and_ecl = self.error_correction_level.get_numbers_of_bits_per_codewords(self.version)
        remainder_of_zeroes = codeword_per_version_and_ecl - len(encoded_input)
        transformed_encoded_input = encoded_input
        terminator_zeroes = bytes()
        if 0 < remainder_of_zeroes <= 4:
            # 1) add the codeword zeroes, up to 0000
            terminator_zeroes = bytes("".join(["0" for _ in range(remainder_of_zeroes)]), encoding="utf-8")
        transformed_encoded_input += terminator_zeroes
        # 2) add the remainder of padding zeroes to fit a whole byte:
        remainder_for_whole_byte = 8 - (len(transformed_encoded_input) % 8)
        transformed_encoded_input += bytes("".join(["0" for _ in range(remainder_for_whole_byte)]), encoding="utf-8")
        # 3) add the pad codewords if required:
        PAD_CODEWORD_0 = bytes('11101100', encoding='utf-8')
        PAD_CODEWORD_1 = bytes('00010001', encoding='utf-8')
        counter = 0
        while len(transformed_encoded_input) < codeword_per_version_and_ecl:
            if counter % 2 == 0:
                transformed_encoded_input += PAD_CODEWORD_0
            else:
                transformed_encoded_input += PAD_CODEWORD_1
            counter += 1
        return transformed_encoded_input
    

    def generate_blocks(self, encoded_input: bytes):
        """
        Method to process the encoded input, generate error codewords and then concatenate 
        them in blocks to prepare the QR code image generation.
        The codewords need to be generated for each block and appended at the end of it.
        This method will then iterate over each block per version & error correction level, 
        split the data into different blocks and then 
        add the error codewords as required. Following the specifications, Reed-Solomon 
        error correction requires long polynomial division,
        which requires two polinomials: one for the data and another one defined as the prime
        modulus polynomial x^8 + x^4 + x^3 + x^2 + 1 for
        Galois Field GF(256). This field guarantees that any operation done in elements within
        it fits in a 8-bit codeword.
        the following steps are applied:
        1) convert the data codewords as the coefficient of the polynomials being used
        2) convert the data codewords polynomial to alpha notation (same notation used in ISO 18004)
        3) to avoid the lead term of the data codeword and the generator polynomial does not decrease 
           too much, we add the difference of each exponent with the number of error codewords: 
           if the lead x is x^15 in data code words, for QR 1-M for example we multiply the whole data 
           polynomial by x^10, where 10 is the number of error codewords (and therefore the lead exponent
           of the generator polynomial), and the generator polynomial by x^15 (which is x^25 - x^10).
           Both will have at the end x^25. This is allowd in Galois field operations and by
           doing so, we'll avoid issues to keep track of the exponents that we need to decrease.
        CHANGE in 22/07/2025
        - version (int): QR Code Version and error_correction_level (QRErrorCorrectionLevel) are
          now based on the instance value (as it should have been).

        Args:
            encoded_input (bytes): information already encoded as a stream of bytes.
        """
        # TODO dividir esse método em múltiplas chamadas refatoradas.
        # tem que ter mais dois métodos: um pra gerar o data codeword e outro que chama esses dois.
        codeword_block_structure = self.error_correction_level.get_number_and_struct_of_error_correction_blocks(self.version)
        offset = 0
        curr_block_no = 1
        total_block_data_codewords = []
        total_block_error_codewords = []
        total_num_blocks = 0
        # max_data_codeword_size and max_error_codeword_size will be required for the interleaving algo later on.
        max_data_codeword_size = 0
        max_error_codeword_size = 0
        for num_blocks, block in codeword_block_structure:
            total_codewords = block.total_codewords()
            data_codewords = block.data_codewords()
            error_codewords = total_codewords - data_codewords
            total_num_blocks += num_blocks
            max_data_codeword_size = max(max_data_codeword_size, data_codewords)
            max_error_codeword_size = max(max_error_codeword_size, error_codewords)
            for block in range(num_blocks):
                curr_block_data_coefficients = []
                # add the data codewords of the encoded data into blocks.
                offset_limit_for_block = curr_block_no * data_codewords * 8 # the upper bound of the number of codewords for the current block, in bits
                while offset < offset_limit_for_block:
                    curr_block_data_coefficients.append(int(encoded_input[offset:min(offset + 8, offset_limit_for_block)], 2))
                    offset += 8
                # this is where the error codeblocks are added.
                # the step by step is a bit more difficult than it should be. In fact, you need to understand a bit better the log and antilog table
                # to manipulate the exponents since the whole operation is divided in modulo 2 bytewise operation with 285 1001010
                generator_polynomial = PolynomialOperations.generate_generator_polynomial(error_codewords)
                data_polynomial = IntPolynomial([Term(coefficient, len(curr_block_data_coefficients) - exponent - 1) for exponent, coefficient in enumerate(curr_block_data_coefficients)])
                error_correction_codewords = PolynomialOperations.divide(data_polynomial, generator_polynomial)
                total_block_data_codewords.append(curr_block_data_coefficients)
                error_correction_coefficients = PolynomialOperations.get_int_values_from_alpha(error_correction_codewords)
                total_block_error_codewords.append(error_correction_coefficients)
                curr_block_no += 1
        resulting_blocks = []
        for col in range(max_data_codeword_size):
            for block in range(total_num_blocks):
                # interleave the data codewords
                if col >= len(total_block_data_codewords[block]):
                    # some blocks might have more codewords than other
                    # ignore the null position in the one with less data.
                    continue
                resulting_blocks.append(total_block_data_codewords[block][col])
        for col in range(max_error_codeword_size):
            for block in range(total_num_blocks):
                if col >= len(total_block_error_codewords[block]):
                    # some blocks might have more codewords than other 
                    # ignore the null position in the one with less data.
                    continue
                resulting_blocks.append(total_block_error_codewords[block][col])
        resulting_blocks_bin = [ bin(data)[2:].zfill(8) for data in resulting_blocks]
        padding = ['0' for _ in range(self.get_remainder_bits())]
        resulting_blocks_bin.append("".join(padding))
        return bytes("".join(resulting_blocks_bin), encoding='utf-8')

    def generate_encoded_data(self, input_str: str):
        """Method to encode a input string in the correct data format, generate its codewords
           outputting data ready to be entered into the QR Code symbol.

        Args:
            input_str (str): data to which will be generated the QR code symbol

        Returns:
            codeword_stream (bytes): the bytestream consisting of data and error codewords
        """
        encoded_data = self.encode_input(input_str)
        codeword_stream = self.generate_blocks(encoded_data)
        return codeword_stream

