# lab_1_1.py
# Нахождение минимального из трех чисел

# Считываем три числа с клавиатуры
num1 = float(input("Введите первое число: "))
num2 = float(input("Введите второе число: "))
num3 = float(input("Введите третье число: "))

# Находим минимальное число
min_num = num1
if num2 < min_num:
    min_num = num2
if num3 < min_num:
    min_num = num3

# Выводим результат
print(f"Минимальное число среди введенных: {min_num}")
