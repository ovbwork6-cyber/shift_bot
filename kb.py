from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def start_kb():
    buttons = [[KeyboardButton(text=f"Зміна {l}") for l in ["А", "Б", "В", "Г", "Д"]]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def menu_kb():
    kb = [
        [KeyboardButton(text="📆 Поточний місяць"), KeyboardButton(text="➡️ Наступний місяць")],
        [KeyboardButton(text="🗓️ Поточний рік (DCS)"), KeyboardButton(text="🚀 Наступний рік (DCS)")],
        [KeyboardButton(text="🏖️ Мої відпустки"), KeyboardButton(text="🏥 Лікарняні")],
        [KeyboardButton(text="➕ Додаткова зміна"), KeyboardButton(text="⚙️ Змінити зміну")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def vacation_menu():
    buttons = [[InlineKeyboardButton(text="➕ Додати відпустку", callback_data="add_vacation")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def sick_menu():
    buttons = [[InlineKeyboardButton(text="➕ Додати лікарняний", callback_data="add_sick")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
