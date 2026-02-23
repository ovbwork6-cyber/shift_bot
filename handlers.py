from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# ТУТ ПОМИЛКА: Треба обов'язково створити об'єкт роутера
router = Router()

# Імпортуємо ваші модулі (перевірте назви файлів)
import logic
import database
import kb

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
    
    # Вираховуємо наступний місяць
    next_m = datetime.now() + relativedelta(months=1)
    path = logic.draw_month_image(shift, next_m.year, next_m.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {next_m.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

# Додайте аналогічні обробники для "🗓️ Поточний рік" та "🚀 Наступний рік"

# 3. Поточний та наступний рік
@router.message(F.text.in_({"🗓️ Поточний рік", "🚀 Наступний рік"}))
async def show_year_graph(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    year = datetime.now().year if "Поточний" in message.text else datetime.now().year + 1
    
    # Використовуємо твою функцію для генерації файлу
    path = logic.generate_year_file(shift, year) 
    await message.answer_document(FSInputFile(path), caption=f"Графік на {year} рік (файл)")
    os.remove(path)
