""" Module to generate the QR Code Imagering"""

class QRCodeImage:
    """Main class to generate the codeword placement in an image
       It follows the implementation steps of Section 7.7 in ISO 18004,
       starting with the matrix generation in Section 6 (details about
       the QR matrix before addiong the quiet zone, for example, are 
       in Section 6)
       
       The organization of each data that needs to be added to the QR 
       code symbol (timing pattern, finder, alignment, data and error 
       codewords, quiet zone, etc.) will be defined in different methods
       to allow better understanding and maintainability of the code.
    """
    
    def __init__(self, version: int):
        """Initializes the QRCodeImage class by assigning a whiteboard
           full blank data matrix for the qr code image.
           the notation that this class follows is the same terminology as in the ISO 18004, including
           blank module: 0
           dark module: 1.

        Args:
            version (int): _description_
        """
        if not isinstance(version, int) or not 1 <= version <= 40:
            raise ValueError(f'Invalid version provided: {version}. Supported versions are between 1 and 40')
        self._version = version
        self._matrix = self._get_matrix(version)

    def _get_matrix(self, version: int):
        """ Method to construct the matrix that will contain all modules and patters as 
            per Sections 6 and 7.7 the matrix's size (i.e., quantity of modules) can be
            found in Table 1.

        Args:
            version (int): QR Code Version

        Returns:
            List[List[int]]: a 2-dimensional array denoting the data 
                               matrix which is the basis for the QR code
                               image generation
        """
        qr_symbol_size = (4 * (version - 1)) + 21
        return [ [ 0 for _ in range(qr_symbol_size) ] for _ in range(qr_symbol_size) ]

    def position_finder_patterns(self):
        """ Helper method to position the finder patterns to the QRCodeImage's matrix
            as per section 6.3.3, it has always a fixed size of 3 * 5 * 7 based on the
            three cocentered squares for each of the symbols. this is why there are 
            values based on the difference of the QR code symbol's amount of modules
            and the position they appear.
        """
        # top left finder
        for index in range(7):
            self._matrix[0][index] = 1
            self._matrix[6][index] = 1
            self._matrix[index][0] = 1
            self._matrix[index][6] = 1
        for row in range(2, 5):
            for col in range(2, 5):
                self._matrix[row][col] = 1
        
        # bottom left finder:
        boundary = len(self._matrix) - 1
        for index in range(7):
            self._matrix[boundary][index] = 1
            self._matrix[boundary - 6][index] = 1
            self._matrix[boundary - 6 + index][0] = 1
            self._matrix[boundary - 6 + index][6] = 1
        for row in range(boundary - 4, boundary - 1):
            for col in range(2, 5):
                self._matrix[row][col] = 1
                
        # top right finder
        for index in range(boundary - 6, boundary):
            self._matrix[0][index] = 1
            self._matrix[6][index] = 1
        for row in range(7):
            self._matrix[row][boundary - 6] = 1
            self._matrix[row][boundary] = 1
        for row in range(2, 5):
            for col in range(boundary - 4, boundary - 1):
                self._matrix[row][col] = 1
    
    def position_timing_pattern(self):
        """Adds the timing pattern to the QR symbol as in Section 6.3.5. This is required to support
           the decoding process to help the scanner to recognize where exactly is the data to be
           decoded 
        """
        size = len(self._matrix)
        bit = 1
        for row in range(6, size - 6):
            self._matrix[row][6] = bit
            self._matrix[6][row] = bit
            bit = 1 - bit
            
    def position_alignment_pattern(self):
        """ Method to add the alignment pattern based on Annex E of ISO 18004, considering every possible centre
            of the pattern. Note that the overlap check needs to be done before positioning it in the matrix.
            For more details regarding this pattern, see Section 6 of the ISO.
        """
        alignment_pattern_num = {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 6, 8: 6, 9: 6, 10: 6, 11: 6, 12: 6,
                                 13: 6, 14: 13, 15: 13, 16: 13, 17: 13, 18: 13, 19: 13, 20: 13,
                                 21: 22, 22: 22, 23: 22, 24: 22, 25: 22, 26: 22, 27: 22, 28: 33,
                                 29: 33, 30: 33, 31: 33, 32: 33, 33: 33, 34: 33, 35: 46, 36: 46,
                                 37: 46, 38: 46, 39: 46, 40: 46
        }
        # the follwing are starting center (dark central bit) of the alignment patterns to be created.
        # note that they have a calculation pattern that could be derived based on the version 
        # but for simplification purposes, it's the same row/column relation as in table E.1 of the ISO
        alignment_pattern_center = {1: [], 2: [6, 18], 3:[6,22], 4: [6, 26], 5: [6,30], 6: [6,34], 7: [6,22,38], 
                                    8: [6, 24, 42], 9: [6,26,46], 10: [6, 28, 50], 11: [6, 30, 54], 12: [6,32,58],
                                    13: [6, 34, 62], 14: [6, 26, 60, 74], 15: [6, 26, 48, 70], 16: [6, 26, 50, 74], 17: [6, 30, 54, 78],
                                    18: [6, 30, 56, 82], 19: [6, 30, 58, 86], 20: [6, 43, 62, 90], 21: [6, 28, 50, 72, 94], 
                                    22: [6, 26, 50, 74, 98], 23: [6, 30, 54, 78, 102], 24: [6, 34, 58, 80, 106], 25: [6, 23, 58, 84, 110],
                                    26: [6, 30, 58, 86, 114], 27: [6, 34, 62, 90, 118], 28: [6, 26, 50, 74, 98, 122],
                                    29: [6, 30, 54, 78, 102, 126], 30: [6, 26, 52, 78, 104, 130], 31: [6, 30, 67, 82, 108, 134],
                                    32: [6, 34, 60, 86, 112, 138], 33: [6, 30, 58, 86, 114, 142], 34: [6, 34, 62, 90, 118, 146],
                                    35: [6, 30, 54, 78, 102, 126, 150], 36: [6, 24, 50, 76, 102, 128, 154],
                                    37: [6, 28, 54, 80, 106, 132, 158], 38: [6, 32, 58, 84, 110, 136, 162],
                                    39: [6, 26, 54, 82, 110, 138, 166], 40: [6, 30, 58, 86, 114, 142, 170]
        }
        alignment_patterns = alignment_pattern_center[self._version]
        for center in alignment_patterns:
            for next_center in alignment_patterns:
                row, col = center, next_center
                if self._check_overlap(row, col):
                    continue
                self._matrix[row][col] = 1
                for left in range(row - 2, row + 3):
                    self._matrix[left][col - 2] = 1
                    self._matrix[row + 2][left] = 1
                    self._matrix[row - 2][left] = 1
                    self._matrix[left][col + 2] = 1

    def _check_overlap(self, row: int, col: int):
        """Method to check whether positioning the alignment pattern centered at (row, col)
           overlaps with any other pattern (mainly finder pattern)

        Args:
            row (int): row number of the center module
            col (int): col number of the center module

        Returns:
            _type_: _description_
        """
        if self._matrix[row][col] == 1:
            return True
        for left in range(row - 2, row + 3):
            if self._matrix[left][col - 2] or self._matrix[col + 2][left] or self._matrix[row - 2][left] or self._matrix[row + 2][left]:
                return True
        return False

    def position_dark_module(self):
        """Method to position the dark module, always at the right side of the
           separator pattern of the bottom left finder pattern
        """
        dark_module_row = len(self._matrix) - 7
        dark_module_col = 8
        self._matrix[dark_module_row][dark_module_col] = 1
        
    def reserve_control_modules(self):
        """ Method to reserve the modules based on the data encoding pattern
            the information will depend on the input, therefore we can't assign at this moment
            (e.g., character code indicator, encoding mode, etc.) 
        """
        size = len(self._matrix)
        if 1 <= self._version <= 7:
            for row in range(9):
                self._matrix[8][row] = 2
                self._matrix[row][8] = 2
                self._matrix[8][size - row - 1] = 2
                # bottom left finder pattern - skip the dark module
                self._matrix[size - row - 1][8] = 2 if self._matrix[size - row - 1][8] == 0 else 1
        else:
            # 8 - 3: 8 is 7 modules from the finder pattern + one module of the separator
            # the other 3 is the range.
            offset = 11 
            for row in range(3):
                for col in range(6):
                    self._matrix[size - (offset + row)][col] = 2
            for row in range(6):
                for col in range(3):
                    self._matrix[row][size - offset + col] = 2

    def generate_matrix(self):
        self.position_finder_patterns()
        self.position_alignment_pattern()
        self.position_timing_pattern()
        self.position_dark_module()
        self.reserve_control_modules()
        pass
qr = QRCodeImage(8)
print(qr.generate_matrix())