from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    keyboard = [
        [KeyboardButton(text="📅 Поточний місяць"), KeyboardButton(text="➡️ Наступний місяць")],
        [KeyboardButton(text="🗓️ Поточний рік"), KeyboardButton(text="🚀 Наступний рік")],
        [KeyboardButton(text="⚙️ Змінити зміну")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
