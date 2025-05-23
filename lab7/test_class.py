import pytest
from triangle_class import Triangle
from triangle_func import IncorrectTriangleSides

def test_triangle_class_equilateral():
    t = Triangle(5, 5, 5)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 15

def test_triangle_class_isosceles():
    t = Triangle(5, 5, 3)
    assert t.triangle_type() == "isosceles"

def test_triangle_class_nonequilateral():
    t = Triangle(3, 4, 5)
    assert t.triangle_type() == "nonequilateral"

def test_triangle_class_invalid():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 10)
