import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

import database
import kb
import logic

router = Router()

ADMIN_ID = 701568112  # Ваш ID адміністратора

class VacationState(StatesGroup):
    waiting_for_dates = State()

class SickState(StatesGroup):
    waiting_for_dates = State()

class ExtraShiftState(StatesGroup):
    waiting_for_date = State()

# 1. КОМАНДА /start ТА АВТОРИЗАЦІЯ
@router.message(Command("start"))
async def start_handler(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift:
        await message.answer(
            "Привіт! Я допоможу тобі з графіком.\nСпочатку обери свою зміну:", 
            reply_markup=kb.shift_selection()
        )
    else:
        await message.answer(
            f"Привіт! Твоя зміна: {shift}. Що хочеш подивитись?", 
            reply_markup=kb.main_menu()
        )

@router.message(F.text == "Вітаю!")
async def auth_handler(message: Message):
    database.authorize_user(message.from_user.id)
    shift = database.get_user_shift(message.from_user.id)
    if not shift:
        await message.answer("✅ Доступ надано! Обери свою зміну:", reply_markup=kb.shift_selection())
    else:
        await message.answer("✅ Вітаю! Вхід успішний.", reply_markup=kb.main_menu())

# 2. НАВІГАЦІЯ ТА ГРАФІКИ
@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message):
    await message.answer("Головне меню:", reply_markup=kb.main_menu())

@router.message(F.text.in_({"📆 Поточний місяць", "📅 Поточний місяць"}))
async def show_this_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift:
        return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    photo = FSInputFile(path)
    await message.answer_photo(photo, caption=f"Графік на {now.strftime('%m.%Y')} (Зміна {shift})")
    if os.path.exists(path):
        os.remove(path)

@router.message(F.text.in_({"➡️ Наступний місяць", "▶️ Наступний місяць"}))
async def show_next_month(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift:
        return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    now = datetime.now()
    next_m = now.month % 12 + 1
    next_y = now.year + (1 if next_m == 1 else 0)
    path = logic.draw_month_image(shift, next_y, next_m)
    photo = FSInputFile(path)
    await message.answer_photo(photo, caption=f"Графік на {next_m:02d}.{next_y} (Зміна {shift})")
    if os.path.exists(path):
        os.remove(path)

@router.message(F.text.in_({"🗓️ Поточний рік", "🚀 Наступний рік", "🗓️ 2026 рік", "🚀 2027 рік"}))
async def show_year_graph(message: Message):
    shift = database.get_user_shift(message.from_user.id)
    if not shift: 
        return await message.answer("Спочатку оберіть зміну!", reply_markup=kb.shift_selection())
    
    current_year = datetime.now().year
    target_year = current_year if ("Поточний" in message.text or "2026" in message.text) else current_year + 1
    path = logic.generate_year_file(shift, target_year) 
    await message.answer_photo(FSInputFile(path), caption=f"📋 Ваш графік на {target_year} рік (Зміна {shift})")
    if os.path.exists(path):
        os.remove(path)

# 3. ВІДПУСТКИ, ЛІКАРНЯНІ ТА ДОДАТКОВІ ЗМІНИ
@router.message(F.text == "🏖️ Мої відпустки")
async def show_vacations(message: Message):
    vacs = database.get_user_vacations(message.from_user.id)
    res = "<b>Ваші відпустки:</b>\n" + ("\n".join([f"• з {s} по {e}" for _, s, e in vacs]) if vacs else "Немає доданих відпусток.")
    await message.answer(res, parse_mode="HTML", reply_markup=kb.vacation_menu())

@router.message(F.text == "🏥 Лікарняні")
async def show_sick_leaves(message: Message):
    sicks = database.get_user_sick_leaves(message.from_user.id)
    res = "<b>Ваші лікарняні:</b>\n" + ("\n".join([f"• з {s} по {e}" for _, s, e in sicks]) if sicks else "Немає доданих лікарняних.")
    await message.answer(res, parse_mode="HTML", reply_markup=kb.sick_menu())

@router.message(F.text == "➕ Додаткова зміна")
async def add_extra_shift_req(message: Message):
    await message.answer("Оберіть тип додаткової зміни:", reply_markup=kb.extra_shift_types_menu())

@router.message(F.text == "⚙️ Змінити зміну")
async def change_shift_req(message: Message):
    await message.answer("Оберіть свою зміну:", reply_markup=kb.shift_selection())

@router.message(F.text.startswith("Зміна"))
async def set_user_shift(message: Message):
    try:
        shift_letter = message.text.split(" ")[1] 
        database.save_user_shift(message.from_user.id, shift_letter)
        await message.answer(f"✅ Зміну {shift_letter} збережено!", reply_markup=kb.main_menu())
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")

# 4. CALLBACK-ОБРОБНИКИ ДЛЯ СТАНІВ (FSM)
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
        await message.answer("✅ Відпустку збережено!", reply_markup=kb.main_menu())
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
        await message.answer("✅ Лікарняний збережено!", reply_markup=kb.main_menu())
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
        await message.answer("❌ Формат дати: YYYY-MM-DD")

# 5. АДМІН-ПАНЕЛЬ
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                count = await cursor.fetchone()
            
            async with db.execute("SELECT user_id FROM users LIMIT 5") as cursor:
                rows = await cursor.fetchall()
                users_list = "\n".join([f"• ID: {row[0]}" for row in rows])

        await message.answer(
            f"📊 <b>Адмін-панель Shift Bot</b>\n\n"
            f"👤 Всього користувачів: <b>{count[0]}</b>\n\n"
            f"Останні активні ID:\n{users_list if users_list else 'Список порожній'}\n\n"
            f"🚀 Статус сервера: <b>Online</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Помилка БД: {e}")
