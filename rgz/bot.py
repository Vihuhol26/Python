import asyncio
import asyncpg
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния
class Reg(StatesGroup):
    name = State()

class AddOp(StatesGroup):
    type = State()
    sum = State()
    date = State()

class ViewOps(StatesGroup):
    start = State()
    end = State()
    currency = State()

# Подключение к БД
async def db_connect():
    return await asyncpg.connect(DB_URL)

# /start
@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Я бот учёта финансов. Введите /reg, чтобы начать.")

# /reg
@dp.message(F.text == "/reg")
async def reg(message: types.Message, state: FSMContext):
    db = await db_connect()
    user = await db.fetchrow("SELECT * FROM users WHERE chat_id = $1", message.chat.id)
    if user:
        await message.answer("Вы уже зарегистрированы.")
    else:
        await message.answer("Введите ваше имя:")
        await state.set_state(Reg.name)

@dp.message(Reg.name)
async def reg_name(message: types.Message, state: FSMContext):
    db = await db_connect()
    await db.execute("INSERT INTO users (chat_id, name) VALUES ($1, $2)", message.chat.id, message.text)
    await message.answer("Регистрация завершена.")
    await state.clear()

# /add_operation
@dp.message(F.text == "/add_operation")
async def add_op(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Доход")],
        [KeyboardButton(text="Расход")]
    ])
    await message.answer("Выберите тип операции:", reply_markup=kb)
    await state.set_state(AddOp.type)

@dp.message(AddOp.type)
async def op_type(message: types.Message, state: FSMContext):
    if message.text not in ["Доход", "Расход"]:
        await message.answer("Пожалуйста, выберите из кнопок.")
        return
    await state.update_data(type=message.text)
    await message.answer("Введите сумму:")
    await state.set_state(AddOp.sum)

@dp.message(AddOp.sum)
async def op_sum(message: types.Message, state: FSMContext):
    try:
        s = float(message.text)
        await state.update_data(sum=s)
        await message.answer("Введите дату (ГГГГ-ММ-ДД):")
        await state.set_state(AddOp.date)
    except ValueError:
        await message.answer("Неверный формат суммы. Введите число.")

@dp.message(AddOp.date)
async def op_date(message: types.Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%Y-%m-%d").date()
        data = await state.get_data()
        db = await db_connect()
        await db.execute(
            "INSERT INTO operations (chat_id, type_operation, sum, date) VALUES ($1, $2, $3, $4)",
            message.chat.id, data["type"], data["sum"], date
        )
        await message.answer("Операция сохранена.")
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД.")

# /operations
@dp.message(F.text == "/operations")
async def operations(message: types.Message, state: FSMContext):
    await message.answer("Введите начальную дату (ГГГГ-ММ-ДД):")
    await state.set_state(ViewOps.start)

@dp.message(ViewOps.start)
async def start_date(message: types.Message, state: FSMContext):
    try:
        start = datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(start=start)
        await message.answer("Введите конечную дату (ГГГГ-ММ-ДД):")
        await state.set_state(ViewOps.end)
    except ValueError:
        await message.answer("Неверный формат даты.")

@dp.message(ViewOps.end)
async def end_date(message: types.Message, state: FSMContext):
    try:
        end = datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(end=end)
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text="USD")],
            [KeyboardButton(text="EUR")],
            [KeyboardButton(text="RUB")]
        ])
        await message.answer("Выберите валюту:", reply_markup=kb)
        await state.set_state(ViewOps.currency)
    except ValueError:
        await message.answer("Неверный формат даты.")

@dp.message(ViewOps.currency)
async def view_currency(message: types.Message, state: FSMContext):
    currency = message.text.upper()
    data = await state.get_data()
    start = data.get("start")
    end = data.get("end")

    rate = 1
    if currency != "RUB":
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:5000/rate?currency={currency}") as resp:
                if resp.status == 200:
                    rate_data = await resp.json()
                    rate = rate_data.get("rate", 1)
                else:
                    await message.answer("Ошибка получения курса валют.")
                    return

    db = await db_connect()
    rows = await db.fetch(
        "SELECT * FROM operations WHERE chat_id = $1 AND date BETWEEN $2 AND $3",
        message.chat.id, start, end
    )

    if not rows:
        await message.answer("Нет операций за указанный период.")
    else:
        text = "Ваши операции:\n"
        for row in rows:
            conv = float(row["sum"]) / rate
            text += f"{row['date']} — {conv:.2f} {currency} — {row['type_operation']}\n"
        await message.answer(text)
    await state.clear()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())