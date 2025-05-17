import os
import threading
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import telebot
import requests

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Параметры подключения к PostgreSQL из переменных окружения или задайте тут напрямую
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DBNAME = os.getenv("PG_DBNAME", "your_db")
PG_USER = os.getenv("PG_USER", "your_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "your_password")

def get_pg_connection():
    return psycopg2.connect(
        dbname=PG_DBNAME,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )

# Инициализация базы (создание таблицы currencies)
def init_db():
    conn = get_pg_connection()
    cur = conn.cursor()
    # Таблица currencies
    cur.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id SERIAL PRIMARY KEY,
            currency_name VARCHAR(50) UNIQUE NOT NULL,
            rate NUMERIC NOT NULL
        );
    """)
    # Таблица админов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            chat_id BIGINT PRIMARY KEY
        );
    """)
    conn.commit()

    # Вставляем конкретный админский chat_id (строка из задания)
    admin_chat_id = '1928526473'  # как строка, чтобы точно соответствовать
    cur.execute("SELECT chat_id FROM admins WHERE chat_id = %s", (admin_chat_id,))
    if not cur.fetchone():
        # Используем именно эту строку
        cur.execute("INSERT INTO admins (chat_id) VALUES ('1928526473');")
        conn.commit()

    cur.close()
    conn.close()


# currency-manager (порт 5001)

app1 = Flask('currency_manager')

@app1.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    name = data.get('currency_name')
    rate = data.get('rate')

    if not name or rate is None:
        return jsonify({'error': 'Неверные данные'}), 400

    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Валюта уже существует'}), 400

        cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (name, rate))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Валюта успешно добавлена'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app1.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    name = data.get('currency_name')
    rate = data.get('rate')

    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Валюта не найдена'}), 404

        cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, name))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Курс обновлен'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app1.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    name = data.get('currency_name')

    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Валюта не найдена'}), 404

        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (name,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Валюта удалена'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# data-manager (порт 5002)

app2 = Flask('data_manager')

@app2.route('/convert')
def convert_currency():
    name = request.args.get('currency_name')
    amount = request.args.get('amount', type=float)

    if not name or amount is None:
        return jsonify({'error': 'Неверные параметры'}), 400

    try:
        conn = get_pg_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (name,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({'error': 'Валюта не найдена'}), 404

        converted = round(float(row['rate']) * amount, 2)
        return jsonify({'converted': converted}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app2.route('/currencies')
def get_all_currencies():
    try:
        conn = get_pg_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Бот

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'menu'])
def start_command(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/get_currencies', '/convert')
    if is_admin(message.chat.id):
        markup.add('/manage_currency')
    bot.send_message(message.chat.id, "Выберите команду: ", reply_markup=markup, )

@bot.message_handler(commands=['manage_currency'])
def manage_currency(message):
    if not is_admin(message.chat.id):
        bot.send_message(message.chat.id, "Извините, эта команда доступна только администраторам.")
        return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("Добавить", callback_data="add"),
        telebot.types.InlineKeyboardButton("Удалить", callback_data="delete"),
        telebot.types.InlineKeyboardButton("Обновить", callback_data="update"),
    )
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

def is_admin(chat_id: int) -> bool:
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM admins WHERE chat_id = %s", (chat_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None
    except Exception:
        return False

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "add":
        bot.send_message(chat_id, "Введите название валюты:")
        bot.register_next_step_handler_by_chat_id(chat_id, step_add_name)
    elif call.data == "delete":
        bot.send_message(chat_id, "Введите название валюты для удаления:")
        bot.register_next_step_handler_by_chat_id(chat_id, step_delete)
    elif call.data == "update":
        bot.send_message(chat_id, "Введите название валюты для обновления:")
        bot.register_next_step_handler_by_chat_id(chat_id, step_update_name)

def step_add_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Введите курс:")
    bot.register_next_step_handler(message, lambda m: add_currency(name, m.text, message.chat.id))

def add_currency(name, rate, chat_id):
    try:
        r = requests.post("http://localhost:5001/load", json={"currency_name": name, "rate": float(rate)})
        bot.send_message(chat_id, r.json().get("message", "Ошибка"))
    except Exception:
        bot.send_message(chat_id, "Ошибка при добавлении валюты")

def step_delete(message):
    name = message.text
    try:
        r = requests.post("http://localhost:5001/delete", json={"currency_name": name})
        if r.status_code == 404:
            bot.send_message(message.chat.id, "Нет такой валюты")
        elif r.status_code == 200:
            bot.send_message(message.chat.id, "Валюта успешно удалена")
        else:
            bot.send_message(message.chat.id, "Ошибка: " + r.json().get("error", "Неизвестная ошибка"))
    except Exception:
        bot.send_message(message.chat.id, "Ошибка при удалении валюты")


def step_update_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Введите новый курс:")
    bot.register_next_step_handler(message, lambda m: update_currency(name, m.text, message.chat.id))

def update_currency(name, rate, chat_id):
    try:
        r = requests.post("http://localhost:5001/update_currency", json={"currency_name": name, "rate": float(rate)})
        bot.send_message(chat_id, r.json().get("message", "Ошибка"))
    except Exception:
        bot.send_message(chat_id, "Ошибка при обновлении валюты")

@bot.message_handler(commands=['get_currencies'])
def get_currencies(message):
    try:
        r = requests.get("http://localhost:5002/currencies")
        data = r.json()
        text = "\n".join([f"{item['currency_name']}: {item['rate']}" for item in data])
        bot.send_message(message.chat.id, text or "Список пуст")
    except Exception:
        bot.send_message(message.chat.id, "Ошибка получения данных")

@bot.message_handler(commands=['convert'])
def convert_command(message):
    bot.send_message(message.chat.id, "Введите название валюты:")
    bot.register_next_step_handler(message, step_convert_name)

def step_convert_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Введите сумму:")
    bot.register_next_step_handler(message, lambda m: perform_conversion(name, m.text, message.chat.id))

def perform_conversion(name, amount, chat_id):
    try:
        r = requests.get("http://localhost:5002/convert", params={"currency_name": name, "amount": float(amount)})
        bot.send_message(chat_id, f"Сумма в рублях: {r.json()['converted']}")
    except Exception:
        bot.send_message(chat_id, "Ошибка при конвертации")

# Запуск

if __name__ == '__main__':
    init_db()

    # Запускаем микросервисы в отдельных потоках
    threading.Thread(target=lambda: app1.run(port=5001)).start()
    threading.Thread(target=lambda: app2.run(port=5002)).start()

    # Запускаем бота
    bot.infinity_polling()
