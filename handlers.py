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

# Команда /start
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привіт! Оберіть потрібний графік:", reply_markup=kb.main_menu())

# Повернення в головне меню
@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message):
    await message.answer("Головне меню:", reply_markup=kb.main_menu())

@router.message(F.text == "📅 Поточний місяць")
async def show_this_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {now.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

@router.message(F.text == "➡️ Наступний місяць")
async def show_next_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    next_m = datetime.now() + relativedelta(months=1)
    path = logic.draw_month_image(shift, next_m.year, next_m.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {next_m.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

@router.message(F.text == "🗓️ Поточний рік")
@router.message(F.text == "🚀 Наступний рік")
async def show_year_graph(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    year = datetime.now().year if "Поточний" in message.text else datetime.now().year + 1
    
    path = logic.generate_year_file(shift, year) 
    await message.answer_document(FSInputFile(path), caption=f"Графік на {year} рік")
    if os.path.exists(path): os.remove(path)

@router.message(F.text == "⚙️ Змінити зміну")
async def change_shift_req(message: Message):
    # ВИПРАВЛЕНО: назва функції тепер точно збігається з kb.py
    await message.answer("Оберіть свою зміну:", reply_markup=kb.shift_selection())

# Обробник вибору конкретної зміни (Зміна 1, 2, 3, 4)
@router.message(F.text.startswith("Зміна"))
async def set_user_shift(message: Message):
    shift_num = int(message.text.split(" ")[А])
    database.save_user_shift(message.from_user.id, shift_num)
    await message.answer(f"Зміну №{shift_num} збережено!", reply_markup=kb.main_menu())
