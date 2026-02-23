from datetime import datetime, timedelta

# Функція-помічник для розрахунку наступного місяця
def get_next_month_details():
    now = datetime.now()
    # Якщо зараз грудень, наступний місяць — січень наступного року
    next_month_date = (now.replace(day=28) + timedelta(days=5))
    return next_month_date.year, next_month_date.month

# 1. Поточний місяць
@router.message(F.text == "📅 Поточний місяць")
async def show_this_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    await message.answer_photo(FSInputFile(path), caption=f"Графік на {now.strftime('%m.%Y')}")
    os.remove(path)

# 2. Наступний місяць
@router.message(F.text == "➡️ Наступний місяць")
async def show_next_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    next_year, next_month = get_next_month_details()
    path = logic.draw_month_image(shift, next_year, next_month)
    await message.answer_photo(FSInputFile(path), caption=f"Графік на {next_month:02d}.{next_year}")
    os.remove(path)

# 3. Поточний рік (текстовий файл або довга картинка)
@router.message(F.text == "🗓️ Поточний рік")
async def show_this_year(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    year = datetime.now().year
    path = logic.generate_year_file(shift, year) # Твоя функція для .txt
    await message.answer_document(FSInputFile(path), caption=f"Графік на весь {year} рік")
    os.remove(path)

# 4. Наступний рік
@router.message(F.text == "🚀 Наступний рік")
async def show_next_year(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    year = datetime.now().year + 1
    path = logic.generate_year_file(shift, year)
    await message.answer_document(FSInputFile(path), caption=f"Графік на весь {year} рік")
    os.remove(path)
