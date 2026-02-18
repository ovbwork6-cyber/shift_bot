from aiogram import F, Router
from aiogram.types import Message, FSInputFile  # ДОДАНО FSInputFile сюди
from aiogram.filters import Command
from datetime import datetime
import calendar
import logic, database, kb
import os

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    database.init_db()
    await msg.answer("Вітаю! Обери свою зміну:", reply_markup=kb.start_kb())

@router.message(F.text.startswith("Зміна "))
async def save_shift(msg: Message):
    shift = msg.text[-1]
    database.set_user_shift(msg.from_user.id, shift)
    await msg.answer(f"Зміну {shift} збережено!", reply_markup=kb.menu_kb())

@router.message(F.text == "Мій графік на сьогодні")
async def today_work(msg: Message):
    shift = database.get_user_shift(msg.from_user.id)
    if not shift:
        return await msg.answer("Спочатку обери зміну!")
    res = logic.get_status(shift, datetime.now())
    await msg.answer(f"Сьогодні ({datetime.now().strftime('%d.%m')}): **{res}**", parse_mode="Markdown")

@router.message(F.text == "Змінити зміну")
async def change(msg: Message):
    await msg.answer("Обери нову зміну:", reply_markup=kb.start_kb())

# Обробник для ГРАФІКА НА МІСЯЦЬ (виводить текст у чат)
@router.message(F.text == "Графік на місяць")
async def show_month_img(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift:
        return await message.answer("Спочатку обери зміну!")

    now = datetime.now()
    # Створюємо картинку
    path = logic.draw_month_image(shift, now.year, now.month)
    
    # Відправляємо як фото
    photo = FSInputFile(path)
    await message.answer_photo(photo, caption=f"Твій графік на цей місяць")
    
    # Видаляємо тимчасовий файл
    os.remove(path)

# Обробник для ГРАФІКА НА РІК (відправляє файл)
@router.message(F.text == "Графік на рік (файл)")
async def send_year_file(msg: Message):
    shift = database.get_user_shift(msg.from_user.id)
    if not shift:
        return await msg.answer("Спочатку обери зміну!")
        
    await msg.answer("Генерую файл на 2026 рік, зачекайте...")
    
    # ВИКЛИКАЄМО ФАЙЛОВУ ГЕНЕРАЦІЮ (logic.generate_year_file)
    file_path = logic.generate_year_file(shift, 2026)
    
    document = FSInputFile(file_path)
    await msg.answer_document(document, caption=f"Твій графік на 2026 рік (Зміна {shift})")
    
    if os.path.exists(file_path):
        os.remove(file_path)