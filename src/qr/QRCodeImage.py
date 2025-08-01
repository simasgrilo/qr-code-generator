""" Module to generate the QR Code Imagering"""


from src.qr.QRCodeEncoder import QRCodeEncoder

# module constants to avoid having magic numbers
DARK_MODULE = 1
LIGHT_MODULE = 0
RESERVED_CONTROL_MODULES = 2
AVAILABLE_MODULE = 9

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
       26/06/2025 - added the following convention for better data allocation
       1: dark modules
       0: light modules
       2: reserved modules for control data (format information area)
       9: THE DATA AREA FOR THE DATA/ERROR CODEWORDS.
       previous version considered light modules and available modules for data both as 0
       which would confuse the algorithm of data positioning (especially in the
       irregular scenarios)
       This approach was done to have a cleaner data allocation 
       within the data area of the QR code symbol.
    """

    def __init__(self, version: int, encoder: QRCodeEncoder):
        """Initializes the QRCodeImage class by assigning a whiteboard
           full blank data matrix for the qr code image.
           the notation that this class follows is the same terminology 
           as in the ISO 18004:
           - blank module: 0
           - dark module: 1.

        Args:
            version (int): QR Code version
        """
        if not isinstance(version, int) or not 1 <= version <= 40:
            raise ValueError((f'Invalid version provided: {version}.'
                              'Supported versions are between 1 and 40'))
        self._version = version
        self._matrix = self._init_matrix(version)
        self._encoder = encoder

    def _init_matrix(self, version: int):
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
        return [ [ 9 for _ in range(qr_symbol_size) ] for _ in range(qr_symbol_size) ]

    def get_matrix(self):
        """ Getter for the matrix structure.

        Returns:
            List[[list[int]]: A matrix denoting the QR Code symbol structure
        """
        return self._matrix

    def position_finder_patterns(self):
        """ Helper method to position the finder patterns to the QRCodeImage's matrix
            as per section 6.3.3, it has always a fixed size of 3 * 5 * 7 based on the
            three cocentered squares for each of the symbols. this is why there are 
            values based on the difference of the QR code symbol's amount of modules
            and the position they appear.
            Change - 26/06/2025: for better data adequation, 0 are now manually set. so
            this method will also set the separator pattern
        """
        # top left finder
        for index in range(7):
            self._matrix[0][index] = DARK_MODULE
            self._matrix[6][index] = DARK_MODULE
            self._matrix[index][0] = DARK_MODULE
            self._matrix[index][6] = DARK_MODULE
        for index in range(1, 6):
            self._matrix[index][1] = LIGHT_MODULE
            self._matrix[index][5] = LIGHT_MODULE
            self._matrix[1][index] = LIGHT_MODULE
            self._matrix[5][index] = LIGHT_MODULE
        for row in range(2, 5):
            for col in range(2, 5):
                self._matrix[row][col] = DARK_MODULE
        # separator for the top left finder:
        for row in range(8):
            self._matrix[7][row] = LIGHT_MODULE
            self._matrix[row][7] = LIGHT_MODULE

        # bottom left finder:
        boundary = len(self._matrix) - DARK_MODULE
        for index in range(7):
            self._matrix[boundary][index] = DARK_MODULE
            self._matrix[boundary - 6][index] = DARK_MODULE
            self._matrix[boundary - 6 + index][0] = DARK_MODULE
            self._matrix[boundary - 6 + index][6] = DARK_MODULE
        for index in range(1, 6):
            self._matrix[boundary - 1][index] = LIGHT_MODULE
            self._matrix[boundary - 5][index] = LIGHT_MODULE
            self._matrix[boundary - 6 + index][1] = LIGHT_MODULE
            self._matrix[boundary - 6 + index][5] = LIGHT_MODULE
        for row in range(boundary - 4, boundary - 1):
            for col in range(2, 5):
                self._matrix[row][col] = DARK_MODULE
        # separator for the bottom left finder:
        for row in range(8):
            self._matrix[boundary - 7][row] = LIGHT_MODULE
            self._matrix[boundary - 7 + row][7] = LIGHT_MODULE

        # top right finder
        for index in range(boundary - 6, boundary):
            self._matrix[0][index] = DARK_MODULE
            self._matrix[6][index] = DARK_MODULE
        for row in range(7):
            self._matrix[row][boundary - 6] = 1
            self._matrix[row][boundary] = DARK_MODULE
        for index in range(boundary - 5, boundary):
            self._matrix[boundary - index][boundary - 5] = LIGHT_MODULE
            self._matrix[boundary - index][boundary - 1] = LIGHT_MODULE
            self._matrix[1][index] = LIGHT_MODULE
            self._matrix[5][index] = LIGHT_MODULE
        for row in range(2, 5):
            for col in range(boundary - 4, boundary - 1):
                self._matrix[row][col] = DARK_MODULE
        for row in range(boundary - 7, boundary + 1):
            self._matrix[7][row] = LIGHT_MODULE
            self._matrix[row - (boundary - 7)][boundary - 7] = LIGHT_MODULE

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

    def get_alignment_pattern_center(self):
        """ Method to retrieve the center for each alignment pattern, 
            depending on the QR code version this was within method 
            position_alignment_pattern but it was moved to allow unit testing.

        Returns:
            List[int]: A list containing the possible row and columns combinations
                       to be the center module of the possible alignment patterns
        """
        # the following are starting center (dark central module)
        # of the alignment patterns to be created.
        # note that they have a calculation pattern
        # that could be derived based on the version
        # but for simplification purposes,
        # it's the same row/column relation as in table E.1 of the ISO
        alignment_pattern_center = {1: [], 2: [6, 18], 3:[6,22], 4: [6, 26], 5: [6,30], 6: [6,34],
                                    7: [6,22,38], 8: [6, 24, 42], 9: [6,26,46], 10: [6, 28, 50],
                                    11: [6, 30, 54], 12: [6,32,58], 13: [6, 34, 62],
                                    14: [6, 26, 60, 74], 15: [6, 26, 48, 70],
                                    16: [6, 26, 50, 74], 17: [6, 30, 54, 78],
                                    18: [6, 30, 56, 82], 19: [6, 30, 58, 86], 20: [6, 43, 62, 90],
                                    21: [6, 28, 50, 72, 94], 22: [6, 26, 50, 74, 98],
                                    23: [6, 30, 54, 78, 102], 24: [6, 34, 58, 80, 106],
                                    25: [6, 23, 58, 84, 110],
                                    26: [6, 30, 58, 86, 114], 27: [6, 34, 62, 90, 118],
                                    28: [6, 26, 50, 74, 98, 122], 29: [6, 30, 54, 78, 102, 126],
                                    30: [6, 26, 52, 78, 104, 130], 31: [6, 30, 67, 82, 108, 134],
                                    32: [6, 34, 60, 86, 112, 138], 33: [6, 30, 58, 86, 114, 142],
                                    34: [6, 34, 62, 90, 118, 146],
                                    35: [6, 30, 54, 78, 102, 126, 150],
                                    36: [6, 24, 50, 76, 102, 128, 154],
                                    37: [6, 28, 54, 80, 106, 132, 158],
                                    38: [6, 32, 58, 84, 110, 136, 162],
                                    39: [6, 26, 54, 82, 110, 138, 166],
                                    40: [6, 30, 58, 86, 114, 142, 170]
        }
        return alignment_pattern_center[self._version]

    def position_alignment_pattern(self):
        """ Method to add the alignment pattern based on Annex E of ISO 18004, considering every 
            possible centre of the pattern. Note that the overlap check needs to be done before
            positioning it in the matrix.
            For more details regarding this pattern, see Section 6 of the ISO.
        """
        alignment_patterns = self.get_alignment_pattern_center()
        for center in alignment_patterns:
            for next_center in alignment_patterns:
                row, col = center, next_center
                if self._check_overlap(row, col):
                    continue
                self._matrix[row][col] = DARK_MODULE
                top_left = (row - 2, col - 2) # goes right
                top_right = (row - 2, col + 2) # goes down
                bot_left = (row + 2, col - 2) # goes up
                bot_right = (row + 2, col + 2) # goes left
                for offset in range(5):
                    self._matrix[top_left[0]][top_left[1] + offset] = DARK_MODULE
                    self._matrix[top_right[0] + offset][top_right[1]] = DARK_MODULE
                    self._matrix[bot_left[0] - offset][bot_left[1]] = DARK_MODULE
                    self._matrix[bot_right[0]][bot_right[1] - offset] = DARK_MODULE
                # light modules
                for offset in range(3):
                    # add or remove 1 to position in the inner light modules 3x3 square:
                    self._matrix[top_left[0] + 1][top_left[1] + 1 + offset] = LIGHT_MODULE
                    self._matrix[top_right[0] + offset + 1][top_right[1] - 1] = LIGHT_MODULE
                    self._matrix[bot_left[0] - offset - 1][bot_left[1] + 1] = LIGHT_MODULE
                    self._matrix[bot_right[0] - 1][bot_right[1] - offset -1 ] = LIGHT_MODULE
    def _check_overlap(self, row: int, col: int):
        """Method to check whether positioning the alignment pattern centered at (row, col)
           overlaps with any other pattern (mainly finder pattern)

        Args:
            row (int): row number of the center module
            col (int): col number of the center module

        Returns:
            _type_: _description_
        """
        if self._matrix[row][col] == DARK_MODULE:
            return True
        # consider the square edges as the starting verification points:
        top_left = (row - 2, col - 2) # goes right
        top_right = (row - 2, col + 2) # goes down
        bot_left = (row + 2, col - 2) # goes up
        bot_right = (row + 2, col + 2) # goes left
        for offset in range(5):
            if (self._matrix[top_left[0]][top_left[1] + offset] != AVAILABLE_MODULE or
                self._matrix[top_right[0] + offset][top_right[1]] != AVAILABLE_MODULE or
                self._matrix[bot_left[0] - offset][bot_left[1]] != AVAILABLE_MODULE or
                self._matrix[bot_right[0]][bot_right[1] - offset] != AVAILABLE_MODULE):
                return True
        return False

    def position_dark_module(self):
        """Method to position the dark module, always at the right side of the
           separator pattern of the bottom left finder pattern
        """
        dark_module_row = len(self._matrix) - 8
        dark_module_col = 8
        self._matrix[dark_module_row][dark_module_col] = DARK_MODULE

    def reserve_control_modules(self):
        """ Method to reserve the modules based on the data encoding pattern
            the information will depend on the input, therefore we can't assign at this moment
            (e.g., character code indicator, encoding mode, etc.) 
        """
        size = len(self._matrix) - 1
        if 1 <= self._version <= 7:
            for row in range(9):
                # this segregation is required as the control part of the left top finder function
                # has 9 reserved modules, the other two have only 8 modules
                self._matrix[8][row] = RESERVED_CONTROL_MODULES if self._matrix[8][row] != DARK_MODULE else 1
                self._matrix[row][8] = RESERVED_CONTROL_MODULES if self._matrix[row][8] != DARK_MODULE else 1
            for row in range(8):
                self._matrix[8][size - row] = RESERVED_CONTROL_MODULES
                # bottom left finder pattern - skip the dark module
                self._matrix[size - row][8] = RESERVED_CONTROL_MODULES if self._matrix[size - row][8] == AVAILABLE_MODULE else 1
        else:
            # 8 - 3: 8 is 7 modules from the finder pattern + one module of the separator
            # the other 3 is the range.
            offset = 11
            for row in range(3):
                for col in range(6):
                    self._matrix[size - (offset + row)][col] = RESERVED_CONTROL_MODULES
            for row in range(6):
                for col in range(3):
                    self._matrix[row][size - offset + col] = RESERVED_CONTROL_MODULES

    def position_codewords(self, encoded_input: bytes):
        """Main method for positioning each of the codewords.
           this method implements the logic described in Section 7.7.3 of the ISO.
           the implementation describes the following key concepts:
           1) the sequence of bit placement in the column must be from the right to left,
              starting at the end of the QR code symbol (n - 1, n - 1) up to the leftmost
              available part, going either upwards or downwards (like a 'S' shaped race track)
              a) the bit stream will be considered as it is: a bit stream. each
                 bit will be placed in the next significant available module, always considering
                 the order of a codeword (8-bit sequence) from the most significant bit to the
                 least significant bit.
           2) the most significant bit of each codeword will be placed at the
              first avaiable module position.
              this depends on the current direction of the codewords being placed.
              The positioning is ALWAYS from the most significant bit to the least significant
              bit
           3) a bit placement can be either regular or irregular: regular ones  occupy a range
              of either 2 x 4 modules or 4 x 2 (depending on the positioning of the modules),
              while irregular ones will follow along the column of some object 
              (see figure 18 for an example) whenever it matches a boundary of a finder pattern
              or an alignment pattern.
            when using irregular symbols, we'll position the most significant bits in 
            the right hand size if downwards, else we'll position it at the left hand side (upwards)
            For the current implementation, we'll be able to identify whether the current module
            has already previously being allocated to some of the control functions (finder,
            timing, alignment, etc.) by simply checking whether the current module is either 0 or 1,
            and by its position on the QR Code symbol's matricial representation

        Args:
            encoded_input (bytes): bytestream of all codewords correctly encoded, interleaved
                                   and constructed with the corresponding error codewords.
        """
        # row and col denotes the next module available
        size = len(self._matrix)
        DARK_MODULE_POS = ((4 * self._version + 9), 8) # coordinate of the dark module
        row, col = size - 1, size - 1 # the pair (row, col) is the next available module,
                                      # and that's what essentially will be
                                      # changing during the allocation procedure
        qr_matrix = self._matrix
        direction = -1 # -1 for upwards, 1 for downwards. This way we can
                       # just add direction to the row.
        index = 0
        col_orientation = 0 # 0 for right column, 1 for left column
        while index < len(encoded_input):
            # determine where the bits will be set before placing them can save time:
            # depending on the position, it's possible to reach a
            # function pattern and a irregular symbol needs to be considered.
            # we'll start by considerign first the assignemtn of simple upward and downwards,
            # and then at each of the directions, we'll check whether it's
            # a regular or irregular symbol.
            # before positioning, check whether the next available pos is valid
            # (i.e, not 0, 1 or 2). with the followign approach:
            # 1) if it's an alignment function:
            # a. if BOTH of the columns goes through it,  ignore and start above it
            # b. if ONLY ONE of the colums is going through it, this means that it
            # will be only the dark modules that form its boundary (1).
            # follow by the column that has available modules (9's)
            # 2) if it's the boundary of the module or a finder pattern
            # a. position the bit by rotating it towards the next
            if (row == size and direction == 1):
                # case: end of symbol was found: move upwards
                row -= 1
                direction = -1
                col -= 2
            if (row < 0 and direction == -1):
                # case: end of symbol was found: move downwards
                row += 1
                direction = 1
                col -= 2
            while ((qr_matrix[row][col] == RESERVED_CONTROL_MODULES and qr_matrix[row][col - 1] == LIGHT_MODULE) or
                   (row, col) == DARK_MODULE_POS):
                # case: the reserved area for the QR code metadata at the right of the
                # left lower finder patter was found. Also, skip the dark control module
                row += direction
            if ((qr_matrix[row][col] == LIGHT_MODULE and qr_matrix[row][col - 1] == LIGHT_MODULE) or
                (qr_matrix[row][col] == RESERVED_CONTROL_MODULES and qr_matrix[row][col - 1] == RESERVED_CONTROL_MODULES)):
                if direction == -1:
                    # case: hit the reserved area for the QR code metadata or the separator pattern
                    # or for the reserved area for version information of the right upper
                    # finder pattern. Position the next possible module two units at the left
                    # of the current one, and at the previous row.
                    row += 1
                    direction = 1
                else:
                    # case: hit the reserved area for the QR code metadata or the separator pattern
                    # of the left bottom finder pattern - the opposite direction of the case above.
                    row -= 1
                    direction = -1
                col -= 2
            if (qr_matrix[row][col] == DARK_MODULE and qr_matrix[row][col - 1] == DARK_MODULE):
                # case: hit an alignment pattern for both modules: skip these:
                while row < size and qr_matrix[row][col] == DARK_MODULE or qr_matrix[row][col] == LIGHT_MODULE:
                    row += direction
            if (qr_matrix[row][col] == DARK_MODULE and qr_matrix[row][col - 1] == LIGHT_MODULE and row == 6):
                # case: hit one of the timing patterns: skip the current bit:
                row += direction
            if (qr_matrix[row][col] == LIGHT_MODULE and qr_matrix[row - 1][col] == DARK_MODULE and col == 6):
                col -= direction
            while (qr_matrix[row][col - 1] == AVAILABLE_MODULE and qr_matrix[row][col] == DARK_MODULE) and direction == -1:
                # case: hit the left border of an alignment pattern while going up
                # position the column left of the pattern boundary as the next avaliable module
                col -= 1
                qr_matrix[row][col] = int(encoded_input[index])
                index += 1
                row += direction
                col += 1
            while (qr_matrix[row][col] == DARK_MODULE and qr_matrix[row][col + 1] == AVAILABLE_MODULE) and direction == 1:
                # case: hit the right border of an alignment pattern while going down.
                # position the column right of the pattern boundary as the next available module
                col += 1
                qr_matrix[row][col] = int(encoded_input[index])
                index += 1
                row += direction
                col -= 1
            qr_matrix[row][col] = int(encoded_input[index])
            if col_orientation:
                col += 1
                row += direction
                col_orientation -= 1
            else:
                col -= 1
                col_orientation += 1
            index += 1

    def add_control_data(self):
        """ Utility method to enhance testability of the features that add control data
            (e.g., alignment pattern, timing pattern, finder pattern, etc.)
        """
        self.position_finder_patterns()
        self.position_alignment_pattern()
        self.position_timing_pattern()
        self.position_dark_module()
        self.reserve_control_modules()

    def generate_matrix(self, encoded_input: bytes):
        """Method to generate the QR Code symbol with all the function patterns,
           data and error codewords
        """
        self.add_control_data()
        self.position_codewords(encoded_input)
        return self._matrix

    def create_qr_code(self, data: str):
        """ Method to create the image. This method will call other methods
           for the following function composition:
           1) encode the input
           2) generate the matrix with all positioning
           3) generate the QR data as an image. - to be implemented
        """
        # Model the bit stream as a finite sequence of bits to be positioned
        # on the grid. We can:
        # a) consider it as a bit-string and iterate char by char (more intuitive, bit slower)
        # b) consider it as a bytestream (or integers)
        # Therefore, the conversion below is done to consider a bit stream.
        bytes_data = self._encoder.generate_encoded_data(data)
        bytes_data = bin(int(bytes_data, base=2))[2:]
        self.generate_matrix(bytes_data)
