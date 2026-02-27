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

# 1. Команда СТАРТ
@router.message(Command("start"))
async def start_handler(message: Message):
    print(f"DEBUG: Спроба надіслати текст користувачу {message.from_user.id}")
    try:
        # Надсилаємо ТЕКСТ БЕЗ КЛАВІАТУРИ для тесту
        await message.answer("Тест зв'язку: Я тебе бачу!")
        print("DEBUG: Текст успішно надіслано")
    except Exception as e:
        print(f"DEBUG: Помилка відправки: {e}")


# 2. Кнопка НАЗАД
@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message):
    await message.answer("Головне меню:", reply_markup=kb.main_menu())

# 3. ПОТОЧНИЙ МІСЯЦЬ
@router.message(F.text == "📅 Поточний місяць")
async def show_this_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: 
        return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {now.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

# 4. НАСТУПНИЙ МІСЯЦЬ
@router.message(F.text == "➡️ Наступний місяць")
async def show_next_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: 
        return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    next_m = datetime.now() + relativedelta(months=1)
    path = logic.draw_month_image(shift, next_m.year, next_m.month)
    await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {next_m.strftime('%m.%Y')}")
    if os.path.exists(path): os.remove(path)

# 5. РІЧНІ ГРАФІКИ (2026-2027)
@router.message(F.text.in_({"🗓️ Поточний рік", "🚀 Наступний рік"}))
async def show_year_graph(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: 
        return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    year = datetime.now().year if "Поточний" in message.text else datetime.now().year + 1
    path = logic.generate_year_file(shift, year) 
    await message.answer_document(FSInputFile(path), caption=f"Графік на {year} рік")
    if os.path.exists(path): os.remove(path)

# --- ТВОЯ НОВА ЧАСТИНА ТУТ (В КІНЦІ) ---

# 6. ВИКЛИК МЕНЮ ВИБОРУ ЗМІН
@router.message(F.text == "⚙️ Змінити зміну")
async def change_shift_req(message: Message):
    await message.answer("Оберіть свою зміну:", reply_markup=kb.shift_selection())

# 7. ОБРОБКА ВИБОРУ (А, Б, В, Г, Д)
@router.message(F.text.startswith("Зміна"))
async def set_user_shift(message: Message):
    try:
        # Витягуємо літеру (А, Б...)
        shift_letter = message.text.split(" ")[1] 
        database.save_user_shift(message.from_user.id, shift_letter)
        await message.answer(f"✅ Зміну {shift_letter} збережено!", reply_markup=kb.main_menu())
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")
