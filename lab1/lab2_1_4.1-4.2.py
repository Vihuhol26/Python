# lab_1_4.py
# Обработка последовательности целых чисел

# Считываем последовательность чисел, разделенных пробелами
input_str = input("Введите последовательность целых чисел через пробел: ")

# Инициализируем переменные
index = 0
sum_numbers = 0
count = 0
current_number_str = ""

# Обрабатываем последовательность с помощью while
while index < len(input_str):
    if input_str[index] != " ":
        current_number_str += input_str[index]
    else:
        if current_number_str:  # если строка не пустая
            number = int(current_number_str)
            sum_numbers += number
            count += 1
            current_number_str = ""
    index += 1

# Обрабатываем последнее число, если оно есть
if current_number_str:
    number = int(current_number_str)
    sum_numbers += number
    count += 1

# Выводим результаты
print(f"Сумма всех чисел последовательности: {sum_numbers}")
print(f"Количество всех чисел последовательности: {count}")
