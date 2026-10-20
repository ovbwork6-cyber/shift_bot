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

@router.message(Command("start"))
async def start(msg: Message):
    database.init_db()
    shift = database.get_user_shift(msg.from_user.id)
    if not shift:
        await msg.answer("Вітаю! Обери свою зміну:", reply_markup=kb.start_kb())
    else:
        await msg.answer(f"Привіт! Твоя зміна: {shift}. Оберіть потрібну дію:", reply_markup=kb.menu_kb())

@router.message(F.text.startswith("Зміна "))
async def save_shift(msg: Message):
    shift = msg.text.split(" ")[1]
    database.set_user_shift(msg.from_user.id, shift)
    await msg.answer(f"Зміну {shift} збережено!", reply_markup=kb.menu_kb())

@router.message(F.text == "⚙️ Змінити зміну")
async def change_shift(msg: Message):
    await msg.answer("Оберіть нову зміну:", reply_markup=kb.start_kb())

# --- МІСЯЧНІ ГРАФІКИ ---
@router.message(F.text == "📆 Поточний місяць")
async def show_current_month(msg: Message):
    shift = database.get_user_shift(msg.from_user.id)
    if not shift:
        return await msg.answer("Спочатку обери зміну!")
    now = datetime.now()
    path = logic.draw_month_image(shift, now.year, now.month)
    await msg.answer_photo(FSInputFile(path), caption=f"Твій графік на {now.month:02d}.{now.year}")
    if os.path.exists(path):
        os.remove(path)

@router.message(F.text == "➡️ Наступний місяць")
async def show_next_month(msg: Message):
    shift = database.get_user_shift(msg.from_user.id)
    if not shift:
        return await msg.answer("Спочатку обери зміну!")
    now = datetime.now()
    next_m = now.month % 12 + 1
    next_y = now.year + (1 if next_m == 1 else 0)
    path = logic.draw_month_image(shift, next_y, next_m)
    await msg.answer_photo(FSInputFile(path), caption=f"Твій графік на {next_m:02d}.{next_y}")
    if os.path.exists(path):
        os.remove(path)

# --- РІЧНІ ГРАФІКИ ДЛЯ DCS ---
@router.message(F.text.in_({"🗓️ Поточний рік (DCS)", "🚀 Наступний рік (DCS)"}))
async def show_year_dcs(msg: Message):
    shift = database.get_user_shift(msg.from_user.id)
    if not shift:
        return await msg.answer("Спочатку обери зміну!")
    
    current_year = datetime.now().year
    target_year = current_year if "Поточний" in msg.text else current_year + 1
    
    await msg.answer(f"Генерую загальний графік DCS на {target_year} рік...")
    path = logic.generate_year_file(shift, target_year)
    await msg.answer_photo(FSInputFile(path), caption=f"📋 Загальний графік DCS на {target_year} рік (Твоя зміна: {shift})")
    if os.path.exists(path):
        os.remove(path)

# --- ПЕРСОНАЛЬНІ ВІДПУСТКИ (ПРИВ'ЯЗАНІ ДО Telegram ID) ---
@router.message(F.text == "🏖️ Мої відпустки")
async def show_vacations(msg: Message):
    vacs = database.get_user_vacations(msg.from_user.id)
    res = "<b>Ваші відпустки:</b>\n" + ("\n".join([f"• з {s} по {e}" for _, s, e in vacs]) if vacs else "Немає доданих відпусток.")
    await msg.answer(res, parse_mode="HTML", reply_markup=kb.vacation_menu())

@router.callback_query(F.data == "add_vacation")
async def start_add_vacation(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введіть дати відпустки (наприклад: <code>2026-06-01 2026-06-14</code>):", parse_mode="HTML")
    await state.set_state(VacationState.waiting_for_dates)
    await call.answer()

@router.message(VacationState.waiting_for_dates)
async def process_vacation_dates(msg: Message, state: FSMContext):
    try:
        s_date, e_date = msg.text.strip().split()
        database.add_vacation(msg.from_user.id, s_date, e_date)
        await msg.answer("✅ Відпустку збережено у вашому персональному профілі!", reply_markup=kb.menu_kb())
        await state.clear()
    except Exception:
        await msg.answer("❌ Формат: YYYY-MM-DD YYYY-MM-DD")

# --- ПЕРСОНАЛЬНІ ЛІКАРНЯНІ (ПРИВ'ЯЗАНІ ДО Telegram ID) ---
@router.message(F.text == "🏥 Лікарняні")
async def show_sick_leaves(msg: Message):
    sicks = database.get_user_sick_leaves(msg.from_user.id)
    res = "<b>Ваші лікарняні:</b>\n" + ("\n".join([f"• з {s} по {e}" for _, s, e in sicks]) if sicks else "Немає доданих лікарняних.")
    await msg.answer(res, parse_mode="HTML", reply_markup=kb.sick_menu())

@router.callback_query(F.data == "add_sick")
async def start_add_sick(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введіть дати лікарняного (наприклад: <code>2026-03-10 2026-03-15</code>):", parse_mode="HTML")
    await state.set_state(SickState.waiting_for_dates)
    await call.answer()

@router.message(SickState.waiting_for_dates)
async def process_sick_dates(msg: Message, state: FSMContext):
    try:
        s_date, e_date = msg.text.strip().split()
        database.add_sick_leave(msg.from_user.id, s_date, e_date)
        await msg.answer("✅ Лікарняний збережено у вашому персональному профілі!", reply_markup=kb.menu_kb())
        await state.clear()
    except Exception:
        await msg.answer("❌ Формат: YYYY-MM-DD YYYY-MM-DD")
