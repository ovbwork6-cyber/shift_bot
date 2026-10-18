import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database
import kb
import logic

router = Router()

class VacationState(StatesGroup):
    waiting_for_dates = State()

class SickState(StatesGroup):
    waiting_for_dates = State()

class ExtraShiftState(StatesGroup):
    waiting_for_date = State()

# Авторизація по слову "Вітаю!"
@router.message(F.text == "Вітаю!")
async def auth_handler(message: Message):
    database.authorize_user(message.from_user.id)
    shift = database.get_user_shift(message.from_user.id)
    if not shift:
        await message.answer("✅ Доступ надано! Обери свою зміну:", reply_markup=kb.shift_selection())
    else:
        await message.answer("✅ Вітаю! Вхід успішний.", reply_markup=kb.main_menu())

# Перевірка авторизації для всіх команд
@router.message()
async def check_auth_middleware(message: Message, state: FSMContext):
    if not database.is_user_authorized(message.from_user.id):
        return await message.answer("🔒 Вхід обмежено. Введіть пароль-вітання для доступу.")

    # Логіка команд для авторизованих користувачів
    text = message.text

    if text == "📅 Поточний місяць":
        shift = database.get_user_shift(message.from_user.id)
        if not shift: return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
        now = datetime.now()
        path = logic.generate_year_file(shift, now.year, user_id=message.from_user.id)
        await message.answer_photo(FSInputFile(path), caption=f"Ваш графік на {now.strftime('%m.%Y')}")
        if os.path.exists(path): os.remove(path)

    elif text in {"🗓️ Поточний рік", "🚀 Наступний рік", f"🗓️ {datetime.now().year} рік", f"🚀 {datetime.now().year + 1} рік"}:
        shift = database.get_user_shift(message.from_user.id)
        if not shift: return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
        current_year = datetime.now().year
        target_year = current_year if ("Поточний" in text or str(current_year) in text) else current_year + 1
        path = logic.generate_year_file(shift, target_year, user_id=message.from_user.id)
        await message.answer_photo(FSInputFile(path), caption=f"📋 Ваш графік на {target_year} рік (Зміна {shift})")
        if os.path.exists(path): os.remove(path)

    elif text == "🏖️ Мої відпустки":
        vacs = database.get_user_vacations(message.from_user.id)
        res = "<b>Ваші відпустки:</b>\n" + ("\n".join([f"• з {s} по {e}" for _, s, e in vacs]) if vacs else "Немає доданих відпусток.")
        await message.answer(res, parse_mode="HTML", reply_markup=kb.vacation_menu())

    elif text == "🏥 Лікарняні":
        sicks = database.get_user_sick_leaves(message.from_user.id)
        res = "<b>Ваші лікарняні:</b>\n" + ("\n".join([f"• з {s} по {e}" for _, s, e in sicks]) if sicks else "Немає доданих лікарняних.")
        await message.answer(res, parse_mode="HTML", reply_markup=kb.sick_menu())

    elif text == "➕ Додаткова зміна":
        await message.answer("Оберіть тип додаткової зміни:", reply_markup=kb.extra_shift_types_menu())

    elif text == "⚙️ Змінити зміну":
        await message.answer("Оберіть свою зміну:", reply_markup=kb.shift_selection())

    elif text and text.startswith("Зміна"):
        shift_letter = text.split(" ")[1]
        database.save_user_shift(message.from_user.id, shift_letter)
        await message.answer(f"✅ Зміну {shift_letter} збережено!", reply_markup=kb.main_menu())

# Callbacks для додавання відпусток, лікарняних та дод. змін
@router.callback_query(F.data == "add_vacation")
async def start_add_vacation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введіть дати відпустки (наприклад: <code>2026-06-01 2026-06-14</code>):", parse_mode="HTML")
    await state.set_state(VacationState.waiting_for_dates)
    await callback.answer()

@router.message(VacationState.waiting_for_dates)
async def process_vacation_dates(message: Message, state: FSMContext):
    try:
        s_date, e_date = message.text.strip().split()
        database.add_vacation(message.from_user.id, s_date, e_date)
        await message.answer(f"✅ Відпустку збережено!", reply_markup=kb.main_menu())
        await state.clear()
    except Exception:
        await message.answer("❌ Формат: YYYY-MM-DD YYYY-MM-DD")

@router.callback_query(F.data == "add_sick")
async def start_add_sick(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введіть дати лікарняного (наприклад: <code>2026-03-10 2026-03-15</code>):", parse_mode="HTML")
    await state.set_state(SickState.waiting_for_dates)
    await callback.answer()

@router.message(SickState.waiting_for_dates)
async def process_sick_dates(message: Message, state: FSMContext):
    try:
        s_date, e_date = message.text.strip().split()
        database.add_sick_leave(message.from_user.id, s_date, e_date)
        await message.answer(f"✅ Лікарняний збережено!", reply_markup=kb.main_menu())
        await state.clear()
    except Exception:
        await message.answer("❌ Формат: YYYY-MM-DD YYYY-MM-DD")

@router.callback_query(F.data.startswith("extra_"))
async def start_add_extra(callback: CallbackQuery, state: FSMContext):
    shift_type = callback.data.split("_")[1]
    await state.update_data(extra_type=shift_type)
    await callback.message.answer("Введіть дату додаткової зміни (наприклад: <code>2026-05-20</code>):", parse_mode="HTML")
    await state.set_state(ExtraShiftState.waiting_for_date)
    await callback.answer()

@router.message(ExtraShiftState.waiting_for_date)
async def process_extra_date(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        d_str = message.text.strip()
        database.add_extra_shift(message.from_user.id, d_str, data['extra_type'])
        await message.answer(f"✅ Додаткову зміну ({data['extra_type']}) на {d_str} збережено!", reply_markup=kb.main_menu())
        await state.clear()
    except Exception:
        await message.answer("❌ Формат дати: YYYY-MM-DD")from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

router = Router()

import logic
import database
import kb
import aiosqlite  # Додай, якщо немає
ADMIN_ID = 701568112  # ЗАМІНИ ЦЕ НА СВІЙ РЕАЛЬНИЙ ID

# 1. Команда СТАРТ з перевіркою зміни
@router.message(Command("start"))
async def start_handler(message: Message):
    print(f"DEBUG: Отримано команду start від {message.from_user.id}")
    
    # Перевіряємо, чи є вже зміна у базі
    shift = database.get_user_shift(message.from_user.id)
    
    if not shift:
        # Якщо новий користувач — відправляємо на вибір зміни
        await message.answer(
            "Привіт! Я допоможу тобі з графіком.\nСпочатку обери свою зміну:", 
            reply_markup=kb.shift_selection()
        )
    else:
        # Якщо старий користувач — просто вітаємо і даємо головне меню
        await message.answer(
            f"Привіт! Твоя зміна: {shift}. Що хочеш подивитись?", 
            reply_markup=kb.main_menu()
        )

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

# --- АДМІН-ПАНЕЛЬ ---

@router.message(Command("admin"))
async def admin_panel(message: Message):
    # Перевірка: чи це ти?
    if message.from_user.id != ADMIN_ID:
        return # Бот просто проігнорує повідомлення від інших

    try:
        # Підключаємося до твоєї бази даних
        async with aiosqlite.connect("users.db") as db:
            # Рахуємо кількість користувачів
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                count = await cursor.fetchone()
            
            # (Опціонально) Отримуємо імена останніх 5 користувачів
            # Припускаємо, що в таблиці є колонки user_id або username
            async with db.execute("SELECT user_id FROM users LIMIT 5") as cursor:
                rows = await cursor.fetchall()
                users_list = "\n".join([f"• ID: {row[0]}" for row in rows])

        await message.answer(
            f"📊 **Адмін-панель Shift Bot**\n\n"
            f"👤 Всього користувачів: **{count[0]}**\n\n"
            f"Последні активні ID:\n{users_list if users_list else 'Список порожній'}\n\n"
            f"🚀 Статус сервера: **Online**"
        )
    except Exception as e:
        await message.answer(f"❌ Помилка БД: {e}")
