import unittest
import pytest

class IncorrectTriangleSides(Exception):
    """Исключение при некорректных сторонах треугольника."""
    pass

# Функция определения типа треугольника
def get_triangle_type(a, b, c):
    """Определяет тип треугольника по длинам сторон."""
    if a <= 0 or b <= 0 or c <= 0 or a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Невозможные длины сторон для треугольника.")
    
    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"

# Класс Triangle
class Triangle:
    """Класс, описывающий треугольник."""
    def __init__(self, a, b, c):
        if a <= 0 or b <= 0 or c <= 0 or a + b <= c or a + c <= b or b + c <= a:
            raise IncorrectTriangleSides("Невозможные длины сторон для треугольника.")
        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):
        """Возвращает тип треугольника."""
        if self.a == self.b == self.c:
            return "equilateral"
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"
        else:
            return "nonequilateral"

    def perimeter(self):
        """Возвращает периметр треугольника."""
        return self.a + self.b + self.c

# Тесты для функции — unittest
import unittest

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

# Тесты для класса — pytest
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
    import pytest
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 10)


# Пример использования
if __name__ == '__main__':
    print("Пример использования функции и класса:")
    try:
        print("Функция: ", get_triangle_type(3, 3, 3))  # equilateral
        triangle = Triangle(3, 4, 5)
        print("Класс: ", triangle.triangle_type())      # nonequilateral
        print("Периметр: ", triangle.perimeter())       # 12
    except IncorrectTriangleSides as err:
        print("Ошибка:", err)

    # Запуск unittest
    print("\nЗапуск модульных тестов (unittest):")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
