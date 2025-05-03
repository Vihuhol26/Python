import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram import Router
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Временное хранилище курсов
currency_data = {}

# Состояния
class Save(StatesGroup):
    name = State()
    rate = State()

class Convert(StatesGroup):
    name = State()
    amount = State()

# СТАРТ
@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Используй /save_currency или /convert.")

# /save_currency
@router.message(Command("save_currency"))
async def save_currency(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(Save.name)

@router.message(Save.name)
async def save_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.upper())
    await message.answer("Введите курс к рублю:")
    await state.set_state(Save.rate)

@router.message(Save.rate)
async def save_rate(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        currency_data[data["name"]] = float(message.text)
        await message.answer(f"Сохранено: 1 {data['name']} = {message.text} руб.")
    except:
        await message.answer("Ошибка! Введите число.")
    await state.clear()

# /convert
@router.message(Command("convert"))
async def convert_start(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(Convert.name)

@router.message(Convert.name)
async def convert_name(message: Message, state: FSMContext):
    name = message.text.upper()
    if name not in currency_data:
        await message.answer("Такой валюты нет. Сначала сохраните её.")
        await state.clear()
        return
    await state.update_data(name=name)
    await message.answer("Введите сумму в этой валюте:")
    await state.set_state(Convert.amount)

@router.message(Convert.amount)
async def convert_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        result = float(message.text) * currency_data[data["name"]]
        await message.answer(f"{message.text} {data['name']} = {result:.2f} руб.")
    except:
        await message.answer("Ошибка! Введите число.")
    await state.clear()

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
