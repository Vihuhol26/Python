import sys

# 1. Считываем одномерный массив из параметров командной строки
input_array = [int(x) for x in sys.argv[1:]]

# Проверяем, не пустой ли массив
if not input_array:
    print("Массив пуст. Пожалуйста, укажите элементы массива как аргументы командной строки.")
    sys.exit(1)

print("Первоначальный массив:", ' '.join(map(str, input_array)))

# 2. Поиск повторяющихся элементов
element_counts = {}
repeats = set()

for num in input_array:
    if num in element_counts:
        repeats.add(num)
    else:
        element_counts[num] = 1

if repeats:
    print("Повторяющиеся элементы:", ' '.join(map(str, sorted(repeats))))
else:
    print("Повторяющиеся элементы отсутствуют")

# 3. Преобразование массива
transformed_array = []
for num in input_array:
    if num < 10:
        transformed_array.append(0)
    elif num > 20:
        transformed_array.append(1)
    else:
        transformed_array.append(num)

# 4. Вывод результатов
print("Преобразованный массив:", ' '.join(map(str, transformed_array)))

