from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

router = Router()

import logic
import database
import kb

# Команда /start - обов'язково для ініціалізації меню
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привіт! Оберіть потрібний графік:", reply_markup=kb.main_menu())

@router.message(F.text == "📅 Поточний місяць")
async def show_this_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Спочатку оберіть зміну!")
    
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {now.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

@router.message(F.text == "➡️ Наступний місяць")
async def show_next_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Спочатку оберіть зміну!")
    
    next_m = datetime.now() + relativedelta(months=1)
    path = logic.draw_month_image(shift, next_m.year, next_m.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {next_m.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

@router.message(F.text == "🗓️ Поточний рік")
@router.message(F.text == "🚀 Наступний рік")
async def show_year_graph(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Спочатку оберіть зміну!")
    
    # Логіка для 2026 та 2027 років
    year = datetime.now().year if "Поточний" in message.text else datetime.now().year + 1
    
    path = logic.generate_year_file(shift, year) 
    await message.answer_document(FSInputFile(path), caption=f"Графік на {year} рік")
    if os.path.exists(path): os.remove(path)

@router.message(F.text == "⚙️ Змінити зміну")
async def change_shift_req(message: Message):
    await message.answer("Оберіть свою зміну:", reply_markup=kb.shift_menu()) # Переконайся, що функція так називається в kb.py
