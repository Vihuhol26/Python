import asyncio
import os
import asyncpg
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class Form(StatesGroup):
    currency_name = State()
    currency_rate = State()
    delete_currency = State()
    edit_name = State()
    edit_rate = State()
    conv_currency = State()
    conv_amount = State()

menu = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Добавить валюту", callback_data="add"),
    InlineKeyboardButton(text="Удалить валюту", callback_data="del"),
    InlineKeyboardButton(text="Изменить курс", callback_data="edit")
]])

async def get_connection():
    return await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="lab5",
        host=os.getenv("DB_HOST")
    )

async def is_admin(user_id):
    conn = await get_connection()
    result = await conn.fetchval("SELECT 1 FROM admins WHERE chat_id = $1", str(user_id))
    await conn.close()
    return bool(result)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def start(message: Message):
    if await is_admin(message.from_user.id):
        await message.answer("Добро пожаловать, админ:\n/manage_currency\n/get_currencies\n/convert")
    else:
        await message.answer("Привет! Доступные команды:\n/get_currencies\n/convert")

@dp.message(Command("manage_currency"))
async def manage(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("Нет доступа к команде")
        return
    await message.answer("Выберите действие:", reply_markup=menu)

@dp.callback_query(F.data == "add")
async def add_currency(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название валюты:")
    await state.set_state(Form.currency_name)

@dp.message(Form.currency_name)
async def input_name(message: Message, state: FSMContext):
    conn = await get_connection()
    exists = await conn.fetchval("SELECT 1 FROM currencies WHERE LOWER(currency_name) = LOWER($1)", message.text)
    await conn.close()
    if exists:
        await message.answer("Данная валюта уже существует.")
        await state.clear()
    else:
        await state.update_data(currency_name=message.text)
        await message.answer("Введите курс к рублю:")
        await state.set_state(Form.currency_rate)

@dp.message(Form.currency_rate)
async def add_currency_rate(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        rate = float(message.text)
        conn = await get_connection()
        await conn.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)",
            data["currency_name"], rate
        )
        await conn.close()
        await message.answer(f"Валюта: {data['currency_name']} успешно добавлена.")
    except ValueError:
        await message.answer("Ошибка: курс валюты должен быть числом. Попробуйте ещё раз.")
        return
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении валюты: {e}")
    finally:
        await state.clear()

@dp.callback_query(F.data == "del")
async def del_currency(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название валюты:")
    await state.set_state(Form.delete_currency)

@dp.message(Form.delete_currency)
async def confirm_del(message: Message, state: FSMContext):
    conn = await get_connection()
    exists = await conn.fetchval("SELECT 1 FROM currencies WHERE LOWER(currency_name) = LOWER($1)", message.text)
    if exists:
        await conn.execute("DELETE FROM currencies WHERE LOWER(currency_name) = LOWER($1)", message.text)
        await message.answer(f"Валюта {message.text} удалена.")
    else:
        await message.answer(f"Валюта {message.text} не найдена.")
    await conn.close()
    await state.clear()

@dp.callback_query(F.data == "edit")
async def edit_currency(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название валюты:")
    await state.set_state(Form.edit_name)

@dp.message(Form.edit_name)
async def get_edit_name(message: Message, state: FSMContext):
    await state.update_data(currency_name=message.text)
    await message.answer("Введите новый курс:")
    await state.set_state(Form.edit_rate)

@dp.message(Form.edit_rate)
async def get_edit_rate(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        rate = float(message.text)
        conn = await get_connection()
        exists = await conn.fetchval("SELECT 1 FROM currencies WHERE LOWER(currency_name) = LOWER($1)", data["currency_name"])
        if not exists:
            await message.answer("Валюта не найдена.")
            await conn.close()
            await state.clear()
            return
        await conn.execute(
            "UPDATE currencies SET rate = $1 WHERE LOWER(currency_name) = LOWER($2)",
            rate, data["currency_name"]
        )
        await conn.close()
        await message.answer(f"Курс валюты {data['currency_name']} изменён.")
    except ValueError:
        await message.answer("Ошибка: курс валюты должен быть числом. Попробуйте ещё раз.")
        return
    except Exception as e:
        await message.answer(f"Произошла ошибка при изменении курса: {e}")
    finally:
        await state.clear()

@dp.message(Command("get_currencies"))
async def get_all(message: Message):
    conn = await get_connection()
    rows = await conn.fetch("SELECT currency_name, rate FROM currencies")
    await conn.close()
    if rows:
        await message.answer("\n".join([f"{r['currency_name']}: {r['rate']}₽" for r in rows]))
    else:
        await message.answer("Список валют пуст.")

@dp.message(Command("convert"))
async def convert(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(Form.conv_currency)

@dp.message(Form.conv_currency)
async def conv_step1(message: Message, state: FSMContext):
    currency_name = message.text
    conn = await get_connection()
    rate = await conn.fetchval(
        "SELECT rate FROM currencies WHERE LOWER(currency_name) = LOWER($1)",
        currency_name
    )
    await conn.close()

    if rate is None:
        await message.answer("Валюта не найдена. Попробуйте снова с /convert.")
        await state.clear()
        return

    await state.update_data(cur=currency_name, rate=rate)
    await message.answer("Введите сумму:")
    await state.set_state(Form.conv_amount)


@dp.message(Form.conv_amount)
async def convert_amount_input(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        amount = float(message.text)
        conn = await get_connection()
        rate = await conn.fetchval(
            "SELECT rate FROM currencies WHERE LOWER(currency_name) = LOWER($1)",
            data["cur"]
        )
        await conn.close()
        if rate is None:
            await message.answer("Валюта не найдена.")
            await state.clear()
            return
        total = amount * float(rate)
        await message.answer(f"Сумма в рублях: {total:.2f}")
    except ValueError:
        await message.answer("Ошибка: сумма должна быть числом. Попробуйте снова с /convert")
        return
    except Exception as e:
        await message.answer(f"Произошла ошибка при конвертации: {e}")
    finally:
        await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
