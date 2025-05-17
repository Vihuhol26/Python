def capitalize_words(input_string):
    result = []
    capitalize_next = True  # Флаг для следующего символа

    for char in input_string:
        # Проверяем, является ли символ русской буквой (строчной или заглавной)
        is_lower_ru = 'а' <= char <= 'я' or char == 'ё'
        is_upper_ru = 'А' <= char <= 'Я' or char == 'Ё'

        if is_lower_ru or is_upper_ru:
            if capitalize_next:
                # Делаем заглавной (если строчная)
                if is_lower_ru:
                    if char == 'ё':
                        new_char = 'Ё'
                    else:
                        # Смещение в Unicode между 'а' и 'А' = 32
                        new_char = chr(ord(char) - 32)
                    result.append(new_char)
                else:
                    result.append(char)  # Уже заглавная
                capitalize_next = False
            else:
                # Делаем строчной (если заглавная)
                if is_upper_ru:
                    if char == 'Ё':
                        new_char = 'ё'
                    else:
                        # Смещение в Unicode между 'А' и 'а' = 32
                        new_char = chr(ord(char) + 32)
                    result.append(new_char)
                else:
                    result.append(char)  # Уже строчная
        else:
            result.append(char)
            # Если символ не буква, следующий должен быть заглавной
            capitalize_next = True

    return ''.join(result)


# Пример использования
input_string = input("Введите строку: ")
output_string = capitalize_words(input_string)
print("Результат:", output_string)
