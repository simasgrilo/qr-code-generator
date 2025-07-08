

from unittest import TestCase
from src.qr.error.utils.QRCodePolynomial import Term, Alpha, Polynomial, PolynomialOperations 


class TestQRCodeErrorCodewordPolynomial(TestCase):
    
    def setUp(self):
        self.maxDiff = None
        return super().setUp()
    
    def test_multiply_two_polynomials(self):
        p1 = Polynomial([Term(Alpha(0), 1), Term(Alpha(0), 0)])
        p2 = Polynomial([Term(Alpha(0), 1), Term(Alpha(1), 0)])
        self.assertEqual(str(PolynomialOperations.multiply(p1, p2)), 'a^0 * x^2 + a^25 * x^1 + a^1 * x^0' )
    
    def test_create_polynomial(self):
        polynomial = PolynomialOperations.generate_generator_polynomial(2)
        self.assertEqual(str(polynomial), 'a^0 * x^2 + a^25 * x^1 + a^1 * x^0')
        
    def test_create_polynomial_generator_three_(self):
        polynomial = PolynomialOperations.generate_generator_polynomial(5)
        self.assertEqual(str(polynomial), 'a^0 * x^5 + a^113 * x^4 + a^164 * x^3 + a^166 * x^2 + a^119 * x^1 + a^10 * x^0')
        
    def test_create_more_factors_generator_polynomial(self):
        polynomial = PolynomialOperations.generate_generator_polynomial(18)
        self.assertEqual(str(polynomial), """a^0 * x^18 + a^215 * x^17 + a^234 * x^16 + a^158 * x^15 + a^94 * x^14 + a^184 * x^13 + 
                                             a^97 * x^12 + a^118 * x^11 + a^170 * x^10 + a^79 * x^9 + a^187 * x^8 + a^152 * x^7 + a^148 * x^6 + a^252 * x^5 + 
                                             a^179 * x^4 + a^5 * x^3 + a^98 * x^2 + a^96 * x^1 + a^153 * x^0""")