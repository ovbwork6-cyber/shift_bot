from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from aiogram import F, types
from aiogram.types import Message, FSInputFile
import logic, database, kb

# 1. Поточний місяць
@router.message(F.text == "📅 Поточний місяць")
async def show_this_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Оберіть зміну!")
    
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    await message.answer_photo(FSInputFile(path), caption=f"Твій графік на {now.strftime('%m.%Y')}")
    os.remove(path)

# 2. Наступний місяць
@router.message(F.text == "➡️ Наступний місяць")
async def show_next_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: return await message.answer("Оберіть зміну!")
    
    # Розрахунок наступного місяця через dateutil
    next_m = datetime.now() + relativedelta(months=1)
    path = logic.draw_month_image(shift, next_m.year, next_m.month)
    await message.answer_photo(FSInputFile(path), caption=f"Графік на {next_m.strftime('%m.%Y')}")
    os.remove(path)

# 3. Поточний та наступний рік
@router.message(F.text.in_({"🗓️ Поточний рік", "🚀 Наступний рік"}))
async def show_year_graph(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    year = datetime.now().year if "Поточний" in message.text else datetime.now().year + 1
    
    # Використовуємо твою функцію для генерації файлу
    path = logic.generate_year_file(shift, year) 
    await message.answer_document(FSInputFile(path), caption=f"Графік на {year} рік (файл)")
    os.remove(path)
