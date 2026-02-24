from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    keyboard = [
        [KeyboardButton(text="📅 Поточний місяць"), KeyboardButton(text="➡️ Наступний місяць")],
        [KeyboardButton(text="🗓️ Поточний рік"), KeyboardButton(text="🚀 Наступний рік")],
        [KeyboardButton(text="⚙️ Змінити зміну")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ДОДАЙ ЦЮ ФУНКЦІЮ (її не вистачало):
def shift_selection():
    keyboard = [
        [KeyboardButton(text="Зміна 1"), KeyboardButton(text="Зміна 2")],
        [KeyboardButton(text="Зміна 3"), KeyboardButton(text="Зміна 4")],
        [KeyboardButton(text="⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
