import enum
from src.qr.error.QRCodeCodewordBlock import QRCodeCodewordBlock as Block

class QRErrorCorrectionLevel(enum.Enum):
    """
    Enum representing the QR Code error correction levels.
    """
    L = "L"  # Low (7% of codewords can be restored)
    M = "M"  # Medium (15% of codewords can be restored)
    Q = "Q"  # Quartile (25% of codewords can be restored)
    H = "H"  # High (30% of codewords can be restored)

    def __str__(self):
        return self.value
    
    
    def get_number_of_data_codewords(self, version: int):
        """
        Method to retrieve the codeword per error correction level
        Args:
            version (int): version of the QR code being generated.
        """
        codeword_map = {
            1:  {'L': 55,  'M': 44,  'Q': 34,  'H': 26},
            2:  {'L': 55,  'M': 44,  'Q': 34,  'H': 26},
            3:  {'L': 55,  'M': 44,  'Q': 34,  'H': 26},
            4:  {'L': 80,  'M': 64,  'Q': 48,  'H': 36},
            5:  {'L': 108, 'M': 86,  'Q': 62,  'H': 46},
            6:  {'L': 136, 'M': 108, 'Q': 76,  'H': 60},
            7:  {'L': 156, 'M': 124, 'Q': 88,  'H': 66},
            8:  {'L': 194, 'M': 154, 'Q': 110, 'H': 86},
            9:  {'L': 232, 'M': 182, 'Q': 132, 'H': 100},
            10: {'L': 274, 'M': 216, 'Q': 154, 'H': 122},
            11: {'L': 324, 'M': 254, 'Q': 180, 'H': 140},
            12: {'L': 370, 'M': 290, 'Q': 206, 'H': 158},
            13: {'L': 428, 'M': 334, 'Q': 244, 'H': 180},
            14: {'L': 461, 'M': 365, 'Q': 261, 'H': 197},
            15: {'L': 523, 'M': 415, 'Q': 295, 'H': 223},
            16: {'L': 589, 'M': 453, 'Q': 325, 'H': 253},
            17: {'L': 647, 'M': 507, 'Q': 367, 'H': 283},
            18: {'L': 721, 'M': 563, 'Q': 397, 'H': 313},
            19: {'L': 795, 'M': 627, 'Q': 445, 'H': 341},
            20: {'L': 861, 'M': 669, 'Q': 485, 'H': 385},
            21: {'L': 932, 'M': 714, 'Q': 512, 'H': 406},
            22: {'L': 1006,'M': 782, 'Q': 568, 'H': 442},
            23: {'L': 1094,'M': 860, 'Q': 614, 'H': 464},
            24: {'L': 1174,'M': 914, 'Q': 664, 'H': 514},
            25: {'L': 1276,'M': 1000,'Q': 718, 'H': 538},
            26: {'L': 1370,'M': 1062,'Q': 754, 'H': 596},
            27: {'L': 1468,'M': 1128,'Q': 808, 'H': 628},
            28: {'L': 1531,'M': 1193,'Q': 871, 'H': 661},
            29: {'L': 1631,'M': 1267,'Q': 911, 'H': 701},
            30: {'L': 1735,'M': 1373,'Q': 985, 'H': 745},
            31: {'L': 1843,'M': 1455,'Q': 1033,'H': 793},
            32: {'L': 1955,'M': 1541,'Q': 1115,'H': 845},
            33: {'L': 2071,'M': 1631,'Q': 1171,'H': 901},
            34: {'L': 2191,'M': 1725,'Q': 1231,'H': 961},
            35: {'L': 2306,'M': 1812,'Q': 1286,'H': 986},
            36: {'L': 2434,'M': 1914,'Q': 1354,'H': 1054},
            37: {'L': 2566,'M': 1992,'Q': 1426,'H': 1096},
            38: {'L': 2702,'M': 2102,'Q': 1502,'H': 1142},
            39: {'L': 2812,'M': 2216,'Q': 1582,'H': 1222},
            40: {'L': 2956,'M': 2334,'Q': 1666,'H': 1276},
        }
        return codeword_map[version][str(self)]
    
    def get_numbers_of_bits_per_codewords(self, version: int) -> int:
        """
        Returns the number of bits per codeword based on the current version and error correction level
        Args:
            version (int): QR code version, Supports range from 1 to 40

        Returns:
            int: _description_
        """
        return self.get_number_of_data_codewords(version) * 8
    
    def get_total_number_of_codewords(self, version: int):
        """Method to implement the retrieval of the total of codewords"

        Args:
            version (int): QR code version 
        """
        total_codewords = {
            1: 26,
            2: 44,
            3: 70,
            4: 100,
            5: 134,
            6: 172,
            7: 196,
            8: 242,
            9: 292,
            10: 346,
            11: 404,
            12: 466,
            13: 532,
            14: 581,
            15: 655,
            16: 733,
            17: 815,
            18: 901,
            19: 991,
            20: 1085,
            21: 1156,
            22: 1258,
            23: 1364,
            24: 1474,
            25: 1588,
            26: 1706,
            27: 1828,
            28: 1921,
            29: 2051,
            30: 2185,
            31: 2323,
            32: 2465,
            33: 2611,
            34: 2761,
            35: 2876,
            36: 3034,
            37: 3196,
            38: 3362,
            39: 3532,
            40: 3706
        }
        return total_codewords[version]
        
    def get_number_of_error_correction_codewords(self, version: int):
        """Method to retrieve the number of error correction codewords. there are two possibilites to do so:
            1) encode table 9 from ISO, or
            2) derive from the total number of codewords and the number of data codewords
        Args:
            version (int): QR code version
        """
        return self.get_total_number_of_codewords(version) - self.get_number_of_data_codewords(version)
    
    def get_number_and_struct_of_error_correction_blocks(self, version: int):
        """Method to retrieve the number of error correction blocks (ecb) per QR Code version. According to the ISO, in table 9, the last two columns
           define the structure of how many codewords and how they are distributed per number of blocks.
           Table 9 is modelled as the dictionary below with the following structure:
           {
               version: {
                   <error_correction_level>: [(<no_of_blocks>, (<total_codewords_per_block>, <data_codewords_per_block>, <error_correction_capacity>))]
               }
           }
           This means that for a specific version and error correction level, one can retrieve how many blocks we need to have and each block's structure. From the ISO, 
           for a given pair (version, error correction level) there will be at most two groups. Therefore, the modelling of the dictionary below will have values with an array
           of length at most two to hold the information of how many blocks and their corresponding structure.
           As an example:

            4: {"L": [(1, (100,80,10))], "M": [(2, (50,32,9))], "Q": [(2, (50,24,13))], "H": [(4, (44,16,14))]},
            for version 4, error correction level M we'll have two blocks, where each block will have 50 codewords, 32 of data and 18 for error. adding everything we have:
            100 codewords, 64 data codewords and 36 error correction codewords, just like the ISO.

        Args:
            version (int): QR code version
        """
        #TODO THIS IS NOT COMPLETE!!!
        if version > 5:
            raise ValueError(f'{version} still not implemented. Please contact the system administratior for more clarifications')
        blocks_and_ecc_per_block = {
            1: {"L": [(1, Block(26,19,2))], "M": [(1, Block(26,16,4))], "Q": [(1, Block(26,13,6))], "H": [(1, Block(26,9,8))]},
            2: {"L": [(1, Block(44,34,4))], "M": [(1, Block(44,28,8))], "Q": [(1, Block(44,22,11))], "H": [(1, Block(44,16,14))]},
            3: {"L": [(1, Block(70,55,7))], "M": [(1, Block(44,28,8))], "Q": [(1, Block(44,22,11))], "H": [(1, Block(44,16,14))]},
            4: {"L": [(1, Block(100,80,10))], "M": [(2, Block(50,32,9))], "Q": [(2, Block(50,24,13))], "H": [(4, Block(44,16,14))]},
            5: {"L": [(1, Block(134,108,13))], 
                "M": [(2, Block(67,43,12))], 
                "Q": [(2, Block(33,15,9)), (2, Block(34,16,9))], 
                "H": [(2, Block(33,11,9)), (2, Block(34,12,9))]},
            6: 172,
            7: 196,
            8: 242,
            9: 292,
            10: 346,
            11: 404,
            12: 466,
            13: 532,
            14: 581,
            15: 655,
            16: 733,
            17: 815,
            18: 901,
            19: 991,
            20: 1085,
            21: 1156,
            22: 1258,
            23: 1364,
            24: 1474,
            25: 1588,
            26: 1706,
            27: 1828,
            28: 1921,
            29: 2051,
            30: 2185,
            31: 2323,
            32: 2465,
            33: 2611,
            34: 2761,
            35: 2876,
            36: 3034,
            37: 3196,
            38: 3362,
            39: 3532,
            40: 3706
        }
        return blocks_and_ecc_per_block[version][str(self)]