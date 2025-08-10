""" Class to create the QR Code format information
    as per Section 7.9 of the ISO 18004
"""

from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel

class QRCodeFormatInfoEncoder:
    """Class to calculate the QR Code format information, for the
       areas reserved in the QR code symbol
       The format information is a 15-bit sequence containing the first
       5 bits as the data bits (consisting of the mask applied and
       a ECL indicator as in Table 12)  and 10 error correction caclulation for
       the format information
    """

    def __init__(self, ecl_indicator: QRErrorCorrectionLevel):
        self.mask_id = None
        self.ecl_indicator = ecl_indicator.get_binary_indicator()

    def set_mask(self, mask: str):
        """ Method to set tue mask id after the best mask is calculated

        Args:
            mask (str): Mask id from Section 7.8.2, in a bin string format
        """
        if len(mask) != 3 or not 0 <= int(mask, base=2) <= 7:
            raise ValueError(("Invalid mask id. It needs to be a valid bit"
                              "string denoting a value in the range [0, 7]"))
        self.mask_id = mask

    def get_data_bits(self):
        """Getter method of the 5-bit data string of the format info.

        Returns:
            str: Bit string containing the mask id and the ECL indicator
                 used for this QR code.
        """
        return self.ecl_indicator + self.mask_id

    def get_format_information_bits(self):
        """Method to calculate the resulting value of the format information
           after dividing the data polynomial (as a bit string) by the
           generator polynomial (as a bit string)

        Returns:
            str : the resulting information bits 
        """
        XOR_BINARY_STRING = '101010000010010'
        resulting_str = self.calculate_bit_information()
        format_info_bits = []
        for index, xor_bit in enumerate(XOR_BINARY_STRING):
            if resulting_str[index] != xor_bit:
                format_info_bits.append('1')
            else:
                format_info_bits.append('0')
        return "".join(format_info_bits)


    def calculate_bit_information(self):
        """Method to calculate the bit information following 
           Annex C of ISO 18004.
           this will require the polynomial division of the generator polynomial 
           G(X) = x^10 + x^8 + x^5 + x^4 + x^2 + x + 1 which is the same division
           implemented previously for the general error correction codes for the data in
           the QR code, which needs to be done under a Galois Field of 256. BUT this
           is far easier as the coefficients are always zero or one, so we can cut
           a lot of work here.
           Therefore we will not reuse the same abstraction as it adds a bit of complexity
           to the same operation. 
        
        Returns
            str: A bit string containing the 15 bits of the format information after the
                 division procedure by the generator polynomial
        """
        X_10_RESULT = '0000000000'
        XOR_BINARY_STRING = '101010000010010'
        generator_polynomial = '10100110111'
        data_bits = self.get_data_bits()
        # note that this is equivalent to multiplying the 5-bit data polynomial by x^10, as all coefficients are either 0 or 1.
        data_polynomial = (data_bits+ X_10_RESULT).lstrip('0')
        #generator_polynomial += "".join(['0' for _ in range(len(data_polynomial) - len(generator_polynomial))])
        division_quocient = self.divide_format_polynomials(data_polynomial, generator_polynomial)
        mask_string = data_bits + division_quocient
        xor_mask_string = []
        for index, mask_string_char in enumerate(mask_string):
            if mask_string_char != XOR_BINARY_STRING[index]:
                xor_mask_string.append("1")
            else:
                xor_mask_string.append("0")
        return "".join(xor_mask_string)

    def divide_format_polynomials(self, dividend: str, divisor: str):
        """ Method to divide the format data polynomial by the generator polynomial """
        MIN_DIVISOR_SIZE = 10
        len_dividend = len(dividend)
        len_divisor = len(divisor)
        next_dividend = None
        while len_dividend > MIN_DIVISOR_SIZE:
            next_dividend = []
            padding_divisor = "".join(['0' for _ in range(len_dividend - len_divisor)])
            padded_divisor = divisor + padding_divisor
            # simulate the xor operation with strings
            for index in range(len_dividend):
                if dividend[index] != padded_divisor[index]:
                    next_dividend.append('1')
                else:
                    next_dividend.append('0')
            dividend = "".join(next_dividend).lstrip('0')
            len_dividend = len(dividend)
        # if the resulting bit sequence has less than 10 bits, we need to pad it
        # by adding zeroes to the left, so its value remains unchainged (MSB 
        # did not change).
        padding_correction = ['0' for _ in range(MIN_DIVISOR_SIZE - len_dividend)]
        return "".join(padding_correction) + dividend
