import sys

def main():
    # 1. Считываем массив
    if len(sys.argv) > 1:  # Если есть аргументы командной строки
        try:
            original_array = [int(arg) for arg in sys.argv[1:]]
        except ValueError:
            print("Ошибка: все аргументы должны быть целыми числами")
            return
    else:  # Если аргументов нет - запрашиваем ввод
        input_str = input("Введите элементы массива через пробел: ")
        try:
            original_array = [int(num) for num in input_str.split()]
        except ValueError:
            print("Ошибка: введите только целые числа, разделенные пробелами")
            return

    if not original_array:
        print("Ошибка: массив не может быть пустым")
        return

    print(f"\nИсходный массив ({len(original_array)} элементов): {original_array}")

    # 2. Поиск повторяющихся элементов
    duplicates = []
    seen = set()
    for num in original_array:
        if num in seen and num not in duplicates:
            duplicates.append(num)
        seen.add(num)

    if duplicates:
        print("Повторяющиеся элементы:", duplicates)
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

    # 4. Вывод результатов
    print("\nРезультаты:")
    print("Исходный массив:", original_array)
    print("Преобразованный массив:", transformed_array)

if __name__ == "__main__":
    main()