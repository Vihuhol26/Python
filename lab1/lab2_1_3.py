# lab_1_3.py
# Генерация последовательности умножений

# Считываем вещественное число
m = float(input("Введите вещественное число m: "))

# Генерируем и выводим последовательность
print("Последовательность:")
for i in range(1, 11):
    print(f"{i} * {m} = {i * m}")
