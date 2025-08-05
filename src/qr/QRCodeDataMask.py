""" Module to provide QR Code data masking functionalities"""

import sys
import math
from typing import List, TYPE_CHECKING
from src.qr.utils import QRCodeConstants

# required to avoid circular import from a typing POV
# this module only refers to QRCodeImage for Type Hints
if TYPE_CHECKING:
    from src.qr.QRCodeImage import QRCodeImage

class QRCodeMasker:
    """Class to provide Data masking features as defined in Section 7.8 of ISO 18004
    The objective is to make the QR Code symbol easier to read to 
    avoid patterns that appears in the finder functions as much as possible
    (i.e., 1011101 - look at this as column oriented)
    Therefore, there are seven data mask patterns to be applied. 
    The procedure will be as follows:
    1) get all modules in the data allocation area (i.e., excluding function patterns)
    2) a) according to the data mask pattern, apply a specific operator and if the condition
    holds for (i, j) - respectively the row and column of the current module, set it
    as a dark module, else light module to construct the data mask patterns
    b) apply the xor of the module (i, j) of the data mask pattern with the data pattern. The XOR is
    then carried over the other mask patterns
    3) Evaluate the penalty of each of the masks and store the best result. 
    """
    @staticmethod
    def apply_mask(qr_code_ref: "QRCodeImage"):
        """Method to apply the mask pattern according with the 8 types
           described in Section 7.8.2, table 10

        Args:
            qr_code_ref (QRCodeImage): QR Code Symbol (image) generated
                                       with everything positioned so far

        Returns:
            best_mask (List[List[int]]): the result of the data mask with less penalty
        """
        qr_code_symbol = qr_code_ref.get_matrix()
        lowest_penalty = sys.maxsize
        best_mask = None
        best_mask_id = -1
        for mask in range(8):
            mask_matrix = QRCodeMasker._get_mask_matrix(mask, qr_code_ref)
            for row in range(len(mask_matrix)):
                for col in range(len(mask_matrix[0])):
                    if (row, col) in qr_code_ref.get_restricted_areas():
                        # reserved areas should not be xor'd with the mask.
                        mask_matrix[row][col] = qr_code_symbol[row][col]
                    else:
                        mask_matrix[row][col] = mask_matrix[row][col] ^ qr_code_symbol[row][col]
            penalty = QRCodeMasker._calculate_penalty(mask_matrix)
            if lowest_penalty > penalty:
                best_mask = QRCodeMask(mask_matrix, mask)
                lowest_penalty = penalty
        return best_mask

    @staticmethod
    def _get_mask_matrix(mask: int, qr_code_ref = "QRCodeImage"):
        qr_code_symbol = qr_code_ref.get_matrix()
        mask_matrix = [[0 for _ in range(len(qr_code_symbol))] for _ in range(len(qr_code_symbol))]
        rows = len(mask_matrix)
        cols = len(mask_matrix[0])
        for row in range(rows):
            for col in range(cols):
                if (mask == 0 and (row + col) % 2 == 0
                    or mask == 1 and row % 2 == 0
                    or mask == 2 and col % 3 == 0
                    or mask == 3 and (row + col) % 3 == 0
                    or mask == 4 and ((row // 2) + (col // 3)) % 2 == 0
                    or mask == 5 and (((row * col) % 2) + ((row * col) % 3)) == 0
                    or mask == 6 and (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
                    or mask == 7 and ((row + col) % 2 + ((row * col) % 3)) % 2 == 0):
                    mask_matrix[row][col] = 1
        return mask_matrix

    @staticmethod
    def _calculate_penalty(mask_matrix: List[List[int]]):
        """ Method to calculate the penalties according to the four undesired
            features. For more details, see Section 7.8.3

        Args:
            mask_matrix (List[List[int]]): result of the data mask pattern applied to the
                                           data codeword matrix
        """
        N_1 = 3
        N_2 = 3
        N_3 = 40
        N_4 = 10
        total_penalty = 0
        # Feature: adjacent modules in row/column in same color (N1)
        # TODO optimization on how this is being checked 
        rows = len(mask_matrix)
        cols = len(mask_matrix[0])
        # as the same modules cannot be reused in the same check, we'll mark it a set with the cells already visited for this check
        visited = [[0 for _ in range(cols)] for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                if visited[row][col]:
                    continue
                visited[row][col] = 1
                row_penalty = 0
                # check in row (vertical)
                row_index = row + 1
                while (row_index < rows and 
                       mask_matrix[row_index][col] == mask_matrix[row_index - 1][col]):
                    visited[row_index][col] = 1
                    row_penalty += 1
                    row_index += 1
                #check in col
                col_penalty = 0
                col_index = col + 1
                while (col_index < cols and 
                       mask_matrix[row][col_index] == mask_matrix[row][col_index - 1]):
                    visited[row][col_index - 1] = 1
                    col_penalty += 1
                    col_index += 1
                total_penalty += (row_penalty - 5) + N_1 if row_penalty >= 5 else 0
                total_penalty += (col_penalty - 5) + N_1 if col_penalty >= 5 else 0

        # Feature: block of module in same color (N2)
        # find all square blocs, and count how many blocks fit in there
        # NOTE: ISO 18004 does not specify how overlapping blocks should be taken in account
        # so we'll consider all 2x2 blocks, even overlapping ones. by doing so we can
        # count all occurrences, even the ones that we'd have more 2x2 blocks fitting into
        # e.g., 4 2x2 blocks in a 3x3 block of dark modules
        for row in range(rows):
            for col in range(cols):
                start_cell = mask_matrix[row][col]
                # increase one dimension to check if we have a valid 2x2 block
                if (row + 1 < rows and col + 1 < cols and
                    mask_matrix[row + 1][col] == start_cell and
                    mask_matrix[row][col + 1] == start_cell and
                    mask_matrix[row + 1][col + 1] == start_cell):
                    total_penalty += N_2
                
        # Feature: 1:1:3:1:1 ratio (dark:light:dark:light:dark)
        # pattern in row/column, preceded of followed by light area 4 modules wide
        pattern_11311_found = False
        for row in range(rows):
            for col in range(cols):
                # vertical check
                if (mask_matrix[row][col] == 1 and
                    row + 1 < rows and mask_matrix[row + 1][col] == 0 and
                    row + 2 < rows and mask_matrix[row + 2][col] == 1 and
                    row + 3 < rows and mask_matrix[row + 3][col] == 1 and
                    row + 4 < rows and mask_matrix[row + 4][col] == 1 and
                    row + 5 < rows and mask_matrix[row + 5][col] == 0 and
                    row + 6 < rows and mask_matrix[row + 6][col] == 1 and
                    QRCodeMasker._check_vertical_light_modules(mask_matrix, row, col)):
                    total_penalty += N_3
                # horizontal check
                if (not pattern_11311_found and
                    mask_matrix[row][col] == 1 and
                    row + 1 < rows and mask_matrix[row + 1][col] == 0 and
                    row + 2 < rows and mask_matrix[row + 2][col] == 1 and
                    row + 3 < rows and mask_matrix[row + 3][col] == 1 and
                    row + 4 < rows and mask_matrix[row + 4][col] == 1 and
                    row + 5 < rows and mask_matrix[row + 5][col] == 0 and
                    row + 6 < rows and mask_matrix[row + 6][col] == 1 and
                    QRCodeMasker._check_vertical_light_modules(mask_matrix, row, col)):
                    total_penalty += N_3
        # Feature: Proportional of dark modules in entire symbol.
        dark_modules = 0
        for row in range(rows):
            for col in range(cols):
                dark_modules += mask_matrix[row][col] & 1
        ratio_dark_to_light = (dark_modules / rows) * 100
        ratio_lower_multiple = math.floor(ratio_dark_to_light / 5) * 5
        ratio_upper_multiple = math.ceil(ratio_dark_to_light / 5) * 5
        distance_factor_lower = abs(ratio_lower_multiple - 50) / 5
        distance_factor_upper = abs(ratio_upper_multiple - 50) / 5
        total_penalty += N_4 * min(distance_factor_lower, distance_factor_upper)
        return total_penalty

    @staticmethod
    def _check_vertical_light_modules(mask_matrix: List[List[int]], row: int, col: int):
        """ Method to check whether there's four blank cells before or after the current column 

        Args:
            mask_matrix (List[List[int]]): QR code symbol masked
            row (int): starting row of the pattern
            col (int): starting col of the pattern
        """
        for curr_row in range(row - 1, row - 5, -1):
            if curr_row < 0:
                return False
            if mask_matrix[curr_row][col] != QRCodeConstants.LIGHT_MODULE:
                return False
        for curr_row in range(row + 1, row + 5):
            if curr_row >= len(mask_matrix):
                return False
            if mask_matrix[curr_row][col] != QRCodeConstants.LIGHT_MODULE:
                return False
        return True

    @staticmethod
    def _check_horizontal_light_modules(mask_matrix: List[List[int]], row: int, col: int):
        """ Method to check whether there's four blank cells before or after the current column 

        Args:
            mask_matrix (List[List[int]]): QR code symbol masked
            row (int): starting row of the pattern
            col (int): starting col of the pattern
        """
        for curr_col in range(col - 1, col - 5, -1):
            if curr_col < 0:
                return False
            if mask_matrix[row][curr_col] != QRCodeConstants.LIGHT_MODULE:
                return False
        for curr_col in range(col + 1, row + 5):
            if curr_col >= len(mask_matrix):
                return False
            if mask_matrix[row][curr_col] != QRCodeConstants.LIGHT_MODULE:
                return False
        return True

class QRCodeMask():
    """Data Class to hold reference of a QR Code mask pattern picked
       this class will have the reference to the resulting matrix after appyling 
       the mask pattern, as well as teh ID of the mask used (ranging from 0 to 7 - 111)
    """

    def __init__(self, data: List[List[int]], mask_id: bin):
        self._mask_id = bin(mask_id) if isinstance(mask_id, int) else mask_id
        self._data = data

    def get_masked_matrix(self):
        """Getter method to return the result of the data mask application
           to the matrix

        Returns:
            self._data (List[List[int]]): a matrix denoting the encoded data
                                          after applying the data mask procedure 
        """
        return self._data

    def get_mask_id(self):
        """Getter method to return the result of the data mask id application
           to the matrix.
           according to the Section 7.8, there are 7 different mask patterns
           ranging from 0 to 7

        Returns:
            self._data (List[List[int]]): a matrix denoting the encoded data
                                          after applying the data mask procedure 
        """
        return self._mask_id
