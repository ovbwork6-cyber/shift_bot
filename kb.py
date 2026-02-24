from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    keyboard = [
        [KeyboardButton(text="📅 Поточний місяць"), KeyboardButton(text="➡️ Наступний місяць")],
        [KeyboardButton(text="🗓️ Поточний рік"), KeyboardButton(text="🚀 Наступний рік")],
        [KeyboardButton(text="⚙️ Змінити зміну")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def shift_selection():
    keyboard = [
        [KeyboardButton(text="Зміна А"), KeyboardButton(text="Зміна Б")],
        [KeyboardButton(text="Зміна В"), KeyboardButton(text="Зміна Г")],
        [KeyboardButton(text="Зміна Д")],
        [KeyboardButton(text="⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
