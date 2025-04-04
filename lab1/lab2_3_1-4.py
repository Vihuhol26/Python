import sys


def main():
    # 1. Считываем массив из параметров командной строки
    if len(sys.argv) < 2:
        print("Ошибка: не указаны элементы массива")
        return

    try:
        # Преобразуем аргументы в целые числа (первые аргумент - имя файла, пропускаем)
        original_array = [int(arg) for arg in sys.argv[1:]]
    except ValueError:
        print("Ошибка: все элементы должны быть целыми числами")
        return

    n = len(original_array)
    print(f"Введён массив из {n} элементов")

    # 2. Поиск повторяющихся элементов
    duplicates = []
    seen = set()
    for num in original_array:
        if num in seen and num not in duplicates:
            duplicates.append(num)
        seen.add(num)

    if duplicates:
        print("Повторяющиеся элементы:", " ".join(map(str, duplicates)))
    else:
        print("Повторяющиеся элементы отсутствуют")

    # 3. Преобразование массива
    transformed_array = []
    for num in original_array:
        if num < 10:
            transformed_array.append(0)
        elif num > 20:
            transformed_array.append(1)
        else:
            transformed_array.append(num)

    # 4. Вывод массивов
    print("Первоначальный массив:", " ".join(map(str, original_array)))
    print("Преобразованный массив:", " ".join(map(str, transformed_array)))


if __name__ == "__main__":
    main()
