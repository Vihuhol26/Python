from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
from dotenv import load_dotenv
import os
import requests
import asyncio

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///currency.db")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Flask-приложение и база данных
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)

class Currency(db.Model):
    code = db.Column(db.String(10), primary_key=True)
    rate = db.Column(db.Float, nullable=False)

# Создание таблиц
with app.app_context():
    db.create_all()

# Роут для добавления или обновления валюты
@app.route("/manage_currency", methods=["POST"])
def manage_currency():
    data = request.get_json()
    code = data["code"].upper()
    rate = float(data["rate"])
    currency = Currency.query.get(code) or Currency(code=code, rate=rate)
    currency.rate = rate
    db.session.add(currency)
    db.session.commit()
    return f"Валюта {code} сохранена с курсом {rate}"

# Роут для конвертации
@app.route("/convert", methods=["POST"])
def convert_currency():
    data = request.get_json()
    code = data["code"].upper()
    amount = float(data["amount"])
    currency = Currency.query.get(code)
    if not currency:
        return f"Валюта {code} не найдена", 404
    result = amount * currency.rate
    return f"{amount} {code} = {result:.2f} RUB"

# Aiogram: Telegram-бот
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(F.text.startswith("/manage_currency"))
async def handle_manage_currency(msg: types.Message):
    try:
        _, code, rate = msg.text.split()
        res = requests.post(
            f"http://localhost:{FLASK_PORT}/manage_currency",
            json={"code": code, "rate": float(rate)}
        )
        await msg.answer(res.text)
    except Exception as e:
        await msg.answer("Ошибка. Используй формат: /manage_currency USD 89.5")

@dp.message(F.text.startswith("/convert"))
async def handle_convert(msg: types.Message):
    try:
        _, code, amount = msg.text.split()
        res = requests.post(
            f"http://localhost:{FLASK_PORT}/convert",
            json={"code": code, "amount": float(amount)}
        )
        await msg.answer(res.text)
    except Exception as e:
        await msg.answer("Ошибка. Используй формат: /convert USD 100")

# Запуск Flask и Telegram-бота
def run_flask():
    app.run(port=FLASK_PORT)

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Запуск Flask-сервера и Telegram-бота...")
    Thread(target=run_flask).start()
    asyncio.run(run_bot())
