import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestGetTriangleType(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(5, 5, 5), "equilateral")

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(5, 5, 3), "isosceles")

    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")

    def test_incorrect(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 10)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 3)
