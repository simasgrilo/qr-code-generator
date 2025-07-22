""" Unit test modules for QRCode polynomial operations (Module QRCodePolynomial)"""

from unittest import TestCase
from src.qr.error.utils.QRCodePolynomial import Term, Alpha, AlphaPolynomial, PolynomialOperations, IntPolynomial


class TestQRCodeErrorCodewordPolynomial(TestCase):
    """Test class for polynomial instantiation and all polynomial related operations for data and error codewords processing"""   

    def test_multiply_two_polynomials(self):
        """Method to test the polynomial multiplication of two Alpha Polynomials"""
        p1 = AlphaPolynomial([Term(Alpha(0), 1), Term(Alpha(0), 0)])
        p2 = AlphaPolynomial([Term(Alpha(0), 1), Term(Alpha(1), 0)])
        self.assertEqual(str(PolynomialOperations.multiply(p1, p2)),
                         'a^0 * x^2 + a^25 * x^1 + a^1 * x^0' )

    def test_only_alpha_poly_can_multiply(self):
        """Method to test that the multiplication only supports AlphaPolynomial as its parameters"""
        p1 = IntPolynomial([Term(0, 1), Term(0, 0)])
        p2 = AlphaPolynomial([Term(Alpha(0), 1), Term(Alpha(1), 0)])
        with self.assertRaises(ValueError):
            PolynomialOperations.multiply(p1, p2)

    def test_create_polynomial(self):
        """Method to test a basic generator polynomial creation of the same values as
           Annex A of ISO 18004 with two error codewords
        """
        polynomial = PolynomialOperations.generate_generator_polynomial(2)
        self.assertEqual(str(polynomial), 'a^0 * x^2 + a^25 * x^1 + a^1 * x^0')

    def test_create_polynomial_generator_five_(self):
        """Method to test a basic generator polynomial creation of the same values as
           Annex A of ISO 18004 with five error codewords
        """
        polynomial = PolynomialOperations.generate_generator_polynomial(5)
        self.assertEqual(str(polynomial), 
                         'a^0 * x^5 + a^113 * x^4 + a^164 * x^3 + a^166 * x^2 + a^119 * x^1 + a^10 * x^0')

    def test_create_more_factors_generator_polynomial(self):
        """Method to test a basic generator polynomial creation of the same values as
           Annex A of ISO 18004 with eightteen error codewords
        """
        polynomial = PolynomialOperations.generate_generator_polynomial(18)
        self.assertEqual(str(polynomial), """a^0 * x^18 + a^215 * x^17 + a^234 * x^16 + a^158 * x^15 + a^94 * x^14 + a^184 * x^13 + a^97 * x^12 + a^118 * x^11 + a^170 * x^10 + a^79 * x^9 + a^187 * x^8 + a^152 * x^7 + a^148 * x^6 + a^252 * x^5 + a^179 * x^4 + a^5 * x^3 + a^98 * x^2 + a^96 * x^1 + a^153 * x^0""")

    def test_int_polynomial_creation(self):
        """Method to create a basic integer polynomial (i.e., with integer coefficients)"""
        polynomial = IntPolynomial([Term(2,1), Term(1,0)])
        self.assertEqual(str(polynomial), "2 * x^1 + 1 * x^0")

    def test_int_conversion(self):
        """Method to convert a IntPolynomial to its couterpart in alpha notation"""
        int_polynomial = IntPolynomial([Term(1,2), Term(3, 1), Term(2, 0)])
        alpha_polynomial = PolynomialOperations.convert_int_to_alpha(int_polynomial)
        self.assertEqual(str(alpha_polynomial), 'a^0 * x^2 + a^25 * x^1 + a^1 * x^0')

    #TODO tests for int to alpha, alpha to int, e outros métodos novos inseridos em QRCodePolynomial
    def test_convert_alpha_poly_to_int(self):
        """Method to convert a polynomial in Alpha notation to an integer notation."""
        alpha_polynomial = PolynomialOperations.generate_generator_polynomial(10)
        self.assertEqual(str(PolynomialOperations.convert_alpha_to_int(alpha_polynomial)),
                         '1 * x^10 + 216 * x^9 + 194 * x^8 + 159 * x^7 + 111 * x^6 + 199 * x^5 + 94 * x^4 + 95 * x^3 + 113 * x^2 + 157 * x^1 + 193 * x^0')

    def test_unit_test_xor_values(self):
        int_poly_1 = IntPolynomial([Term(32,25) , Term(2,24) , Term(101,23) , Term(10,22) , 
                                    Term(97,21) , Term(197,20) , Term(15,19) , Term(47,18) ,
                                    Term(134,17) , Term(74,16) , Term(5,15)])
        int_poly_2 = IntPolynomial ([Term(32,25) , Term(91,24) , Term(11,23) , Term(120,22) ,
                                     Term(209,21) , Term(114,20) , Term(220,19) , Term(77,18) , 
                                     Term(67,17) , Term(64,16) , Term(236,15) , Term(17,14) ,
                                     Term(236,13) , Term(17,12) , Term(236,11) , Term(17,10)])
        self.assertEqual(str(PolynomialOperations.xor_int(int_poly_1, int_poly_2)),
                         str(IntPolynomial([Term(89,24) , Term(110,23) , Term(114,22) , Term(176,21) ,
                          Term(183,20) , Term(211,19) , Term(98,18) , Term(197,17) ,
                          Term(10,16) , Term(233,15) , Term(17,14) , Term(236,13) ,
                          Term(17,12) , Term(236,11) , Term(17,10)])))

