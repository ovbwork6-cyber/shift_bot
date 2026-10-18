from datetime import datetime
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    curr_yr = datetime.now().year
    next_yr = curr_yr + 1
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Поточний місяць"), KeyboardButton(text="➡️ Наступний місяць")],
            [KeyboardButton(text=f"🗓️ {curr_yr} рік"), KeyboardButton(text=f"🚀 {next_yr} рік")],
            [KeyboardButton(text="🏖️ Мої відпустки"), KeyboardButton(text="🏥 Лікарняні")],
            [KeyboardButton(text="➕ Додаткова зміна"), KeyboardButton(text="⚙️ Змінити зміну")]
        ],
        resize_keyboard=True
    )

def shift_selection():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Зміна А"), KeyboardButton(text="Зміна Б")],
            [KeyboardButton(text="Зміна В"), KeyboardButton(text="Зміна Г")],
            [KeyboardButton(text="Зміна Д")]
        ],
        resize_keyboard=True
    )

def vacation_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати відпустку", callback_data="add_vacation")]
        ]
    )

def sick_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати лікарняний", callback_data="add_sick")]
        ]
    )

def extra_shift_types_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌙 Нічна (Зміна №1)", callback_data="extra_1")],
            [InlineKeyboardButton(text="🌅 Ранкова (Зміна №2)", callback_data="extra_2")],
            [InlineKeyboardButton(text="🌆 Вечірня (Зміна №3)", callback_data="extra_3")]
        ]
    )
