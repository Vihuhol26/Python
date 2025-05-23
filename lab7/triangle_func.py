class IncorrectTriangleSides(Exception):
    """Исключение при некорректных сторонах треугольника."""
    pass

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
