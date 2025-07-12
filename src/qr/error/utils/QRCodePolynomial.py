""" This module will hold math concepts to implement the polynomial multiplication division required to generate the error codewords
    and all polynomial-related operations with the encoding
"""

import math
from collections import defaultdict
from typing import List
from abc import ABC, abstractmethod

class Alpha:
    """Class modelling the alpha notation for Galois Field GF(256)
    """

    _MAX_GF_256_EXPONENT = 255

    def __init__(self, exponent: int):
        if exponent > self._MAX_GF_256_EXPONENT:
            exponent = exponent % 256 + math.floor(exponent / 256)
        self._exponent = exponent
        
    def __str__(self):
        return f'a^{self._exponent}'
    
    def get_exponent(self) -> int:
        return self._exponent

class AlphaOperations:
    """Class to model the Alpha Operations like Log and Antilog to determine exponent & integer based on the operation,
       but that does not belong to an Alpha instance itself.
    """
    #TODO this class needs to be globally avalable for all classes that manipula this.
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlphaOperations, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        self._log_table = self.initialize_log_table()
        self._antilog_table = self.initialize_antilog_table()
    
    def initialize_log_table(self):
        """ Method to statically store the log table used to calculate Alpha exponents in Galois Field of 255 GF(255)
        """
        PRIMITIVE_POLYNOMIAL = 0b100011101
        log_table_value = {0 : 1}
        value = 1
        for i in range(256):
            log_table_value[i] = value
            value = value << 1
            if value >= 256:
                value = value ^ PRIMITIVE_POLYNOMIAL 
        return log_table_value

    def get_log_from_alpha(self,  exponent: int):
        return self._log_table[exponent]

    def initialize_antilog_table(self):
        """Method to store the antilog table used to calculate integer back to the alpha exponents
           based on the log operation initialized in method initialize_log_table, we can calculate back
           by applying the definition of antilog : a^x = b, then antilog of a is x.
           once the log table is calculated, it's a matter of applying the antilog operation by inverting 
        Raises:
            ValueError: Raised when the value is outside of possible integers in a Galois field GF(255): 1 <= integer <= 255

        Returns:
            antilog_table_value: Table containing the conversion of integers back to Alpha notation and its coefficients
        """
        calculation_antilog_table = {}
        for key, value in self._log_table.items():
            calculation_antilog_table[value] = key
        # fix: normalization of exponent to match 1 back to 0
        calculation_antilog_table[1] = 0
        antilog_table = {}
        # the for below can be extinguished, but this is just for the sake of readability.
        for exponent in range(1, 256):
            antilog_table[exponent] = calculation_antilog_table[exponent]
        return antilog_table

    def get_antilog_from_alpha(self, exponent: int):
        return self._antilog_table[exponent] if exponent > 0 else 0

class Term:
    """Class to model a term of the polynomial. 
       This class needs to have both the alpha exponent and the x exponent
    """

    def __init__(self, coefficient: Alpha | int, x_exponent: int):
        if (not isinstance(coefficient, int)) and (not isinstance(coefficient, Alpha) or coefficient.get_exponent() < 0 or x_exponent < 0):
            raise ValueError(f"Illegal values for eiher {coefficient} or {x_exponent}")
        self.coefficient = coefficient
        self._x_exponent = x_exponent

    def __str__(self):
        return f'{str(self.coefficient)} * x^{self._x_exponent}'

    def get_coefficient(self):
        return self.coefficient

    def get_x_exponent(self):
        return self._x_exponent

class Polynomial(ABC):
    """Abstract class to model polynomials. In our scenario, polynomials can be in integer notation or using alpha notation to denote each coefficient
       of the polynomial.
    """
    coefficients: None

    def __init__(self, *args):
        """Allows the construction of a polynomial using either a list of coefficients or scalars.
           the following possible parameters will be accepted by the constructor:
           1) a List of Terms (pairs (Alpha, integer) as in class Term)
           2) a single Term 
           3) a sequence of Terms (Alpha, Integer)
           Anything different from this will be ignored.
        """
        if len(args) == 1:
            val = args[0]
            if isinstance(val, list):
                self._validate_coefficient_list(val)
                self.coefficients = val
            elif isinstance(val, Term):
                self.coefficients = [val]
        else:
            coefficients = []
            for elem in args:
                self._validate_single_coefficient(elem)
                coefficients.append(elem)
            self.coefficients = coefficients
            
        
    def get_coefficients(self):
        """Method to retrieve a list of coefficients of the polynomial
        
        Returns:
            self._coefficients (List[Alpha | int]): List of coefficients of the polynomial. The exact type depends on the concrete class
        """
        return self.coefficients

    @abstractmethod
    def _validate_single_coefficient(self, elem):
        pass

    def _validate_coefficient_list(self, coefficient_list: List[Term]):
        for term in coefficient_list:
            if not isinstance(term, Term):
                raise ValueError(f'{term} has incorrect type. It should be an instance of Term, but it is an instance of {type(term)}')
    
    def __str__(self):
        """Pretty printer for printing a polynomial in a friendly format: a^i * x^n + a^j * x^(n - 1) + ... + a^z * x^0
        
        Returns:
            (str) : a string containing all terms that are part of the coefficient
        """
        return " + ".join([str(term) for term in self.coefficients])

class AlphaPolynomial(Polynomial):
    """Class to model a Polynomial as a list of coefficients of the form Alpha(x), 3).
       this class exclusively models polynomials of form a^n * x^n + a^(n - 1) * x^(n - 1)... (single variable)
       This is a special Polynomial to model only alpha
       Note: THE SEMANTICS OF EACH COEFFICIENT OF THIS CLASS WILL BE AUTOMATICALLY CASTED TO ALPHA TYPE.
    """

    def _validate_single_coefficient(self, elem: Term):
        if not isinstance(elem, Term):
            raise ValueError(f"{elem} is not a valid coefficient for a Polynomial in GF(255)")

class IntPolynomial(Polynomial):
    """Class to model an integer polynomial (i.e., integer coefficients), complementing the Alpha polynomial implementation
       This will be further used in the data codeword creation.
    """

    def _validate_single_coefficient(self, elem: int):
        if not isinstance(elem, int):
            raise ValueError(f"{elem} is not a valid integer to form a data codeword")

class PolynomialOperations:
    """Class to model all polynomial opreations required in section 7.5.2 to create the error codewords based on the ISO Specification
       Namely, we'll need to convert the data codeword to a polynomial structure A, obtain the generator polynomial structure B,
       and divide A by B using XOR to subtract when removing coefficients from the structure. The remainter is our codeword. 
       It is worth noting that these polynomials are subject to Galois field GF(256) and therefore some special properties apply, like the structures, the fact that 
       the prime modulo polynomial x^8 + x^4 + x^3 + x^2 + 1.
       The range of operations of this class also includes getting the xor for every power of two in the galois field GF(256) with 100011101 (285)
    """

    alpha_calculator = AlphaOperations()

    GF_255_PRIME_MODULUS_POLYNOMIAL = 285

    GF_255_XOR_CACHE = {}

    @staticmethod
    def divide(dividend: AlphaPolynomial, divisor: AlphaPolynomial):
        """Long polynomial division in the mathematical sense. In the QR code ISO 18004,
           this is required to create the error codewords as the remainder of the division of 
           the data codeword polynomial by the generator polynomial.
           The steps will follow the procedure required as follows:
           1) convert an AlphaPolynomial's coefficients to integer to perform the division
           2) instead of adding the resulting polynomial's coefficients, we will apply XOR as the operation in GF(255)

        Args:
            dividend (AlphaPolynomial): dividend of the operation. In this case, will be called with the data codeword polynomial
            divisor (AlphaPolynomial): divisor of the operation. In this case, it will be called with the generator codeword polynomial.
        """
        if not isinstance(dividend, AlphaPolynomial) or isinstance(divisor, AlphaPolynomial):
            raise ValueError("Polynomial division is only supported for AlphaPolynomial type")

    @staticmethod
    def multiply(polynomial_1: AlphaPolynomial, polynomial_2: AlphaPolynomial) -> AlphaPolynomial:
        """Algorithm to multiply two polinomials.
           it uses a hash to group the x exponents as the key, and all the coefficients that multiply each of these X's
           this effectively allows us to calculate the polynomial at the end by adding all the coefficients as soon as they are found
           with the corresponding X.

        Args:
            polynomial_1 (Polynomial): First term of multiplication
            polynomial_2 (Polynomial): Second term of multiplication

        Returns:
            new_polynomial (Polynomial): The product of polynomial_1 with polynomial_2.
        """
        if not isinstance(polynomial_1, AlphaPolynomial) or not isinstance(polynomial_2, AlphaPolynomial):
            raise ValueError(f"Polynomials have invalid type. both must have type AlphaPolynomial but they have {type(polynomial_1)} and {type(polynomial_2)}")
        polynomial_1_coefs = polynomial_1.get_coefficients()
        polynomial_2_coefs = polynomial_2.get_coefficients()
        new_polynomial = []
        x_coefficients = defaultdict(list) # hash map of x coefficients to group alpha coefficients
        for term_p1 in polynomial_1_coefs:
            for term_p2 in polynomial_2_coefs:
                coef_alpha_p1 = term_p1.get_coefficient().get_exponent()
                x_alpha_p1 =  term_p1.get_x_exponent()
                coef_alpha_p2 = term_p2.get_coefficient().get_exponent()
                x_alpha_p2 = term_p2.get_x_exponent()
                sum_alpha = coef_alpha_p1 + coef_alpha_p2
                sum_x = x_alpha_p1 + x_alpha_p2
                x_coefficients[sum_x].append(sum_alpha)
        # process each alpha coefficient before building the polynomial
        for key, value in x_coefficients.items():
            alpha_sum = PolynomialOperations._calculate_alpha_coefficient_sum(value)
            new_polynomial.append(Term(Alpha(alpha_sum), key))
        return AlphaPolynomial(new_polynomial)

    @staticmethod
    def _calculate_alpha_coefficient_sum(alpha_coefficients: List[int]) -> Alpha:
        """Method to calculate the sum of alpha coefficients using XOR and the bit size correction (0 <= i <= 255), for any a^i.
           the algorithm is as follows:
           1) iterates over the list of obtained exponents by adding similar terms (as in standard polynomial addition)
           2) if any of the exponents is greater than 255, normalize it by getting the remanider of exponent by 256 and adding it by the floor of the division of 256 (GF(256))
           3) xor all the normalized exponents. apply the same normalization rules if xor'ing results in an exponent greater than 255.

        Args:
            alpha_coefficients (List[int]): List of all coefficients to be added for a single x coefficient

        Returns:
            Alpha: a new alpha coefficient obtained after adding every alpha coefficient of the sabe x base (x^i).
        """
        calculator = PolynomialOperations.alpha_calculator
        n = len(alpha_coefficients)
        normalized_alpha_coefficients = []
        for exponent in alpha_coefficients:
            normalized_coefficient = exponent if exponent < 255 else exponent % 256 + math.floor(exponent / 256)
            normalized_alpha_coefficients.append(normalized_coefficient)
        if n == 1:
            return normalized_alpha_coefficients[0]
        antilog_alpha_coefficients = [ calculator.get_log_from_alpha(exponent) for exponent in normalized_alpha_coefficients ]
        coefficients_sum = antilog_alpha_coefficients[0]
        for index in range(1, n):
            if coefficients_sum >= 256:
                coefficients_sum = coefficients_sum % 256 + math.floor(coefficients_sum / 256)
            coefficients_sum = coefficients_sum ^ antilog_alpha_coefficients[index]
        return calculator.get_antilog_from_alpha(coefficients_sum)
            

    @staticmethod
    def generate_generator_polynomial(n: int) -> AlphaPolynomial:
        """Method to create the polynomial generators for n codewords as per the ISO standards

        Args:
            n (int): number of codewords required

        Returns:
            Polynomial: a Polynomial of degree n to satisfy the conditions
        """
        polynomial = AlphaPolynomial([Term(Alpha(0), 1), Term(Alpha(0), 0)]) # a0x1 + a0x0
        for i in range(1, n):
            next_polynomial = AlphaPolynomial([Term(Alpha(0), 1), Term(Alpha(i), 0)])
            polynomial = PolynomialOperations.multiply(polynomial, next_polynomial)
        return polynomial
    
    @staticmethod
    def convert_int_to_alpha(int_polynomial: IntPolynomial) -> AlphaPolynomial:
        """Method to convert an IntPolynomial to an AlphaPolynomial object. This will
           be useful in the multiplication process part of the error codeword generation

        Args:
            int_polynomial (IntPolynomial): Polynomial with integer coefficients

        Returns:
            AlphaPolynomial: the same polynonial with alpha coefficients.
        """
        calculator = PolynomialOperations.alpha_calculator
        coefficients = [ (term.get_coefficient(), term.get_x_exponent()) for term in int_polynomial.get_coefficients() ]
        # create a list of terms with the converted alpha value (Int -> Alpha):
        alpha_terms = [Term(Alpha(calculator.get_antilog_from_alpha(coefficient)), x_exponent) for coefficient, x_exponent in coefficients]
        return AlphaPolynomial(alpha_terms)
    
int_polynomial = IntPolynomial([Term(1,2), Term(3, 1), Term(2, 0)])
alpha_polynomial = PolynomialOperations.convert_int_to_alpha(int_polynomial)
