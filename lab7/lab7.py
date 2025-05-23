from triangle_func import get_triangle_type, IncorrectTriangleSides
from triangle_class import Triangle

if __name__ == '__main__':
    print("Пример использования функции и класса:")
    try:
        print("Функция: ", get_triangle_type(3, 3, 3))  # equilateral
        triangle = Triangle(3, 4, 5)
        print("Класс: ", triangle.triangle_type())      # nonequilateral
        print("Периметр: ", triangle.perimeter())       # 12
    except IncorrectTriangleSides as err:
        print("Ошибка:", err)
