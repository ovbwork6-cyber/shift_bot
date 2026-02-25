from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    # Робимо кнопки максимально простими для першого тесту
    kb_list = [
        [KeyboardButton(text="📅 Поточний місяць"), KeyboardButton(text="➡️ Наступний місяць")],
        [KeyboardButton(text="🗓️ Поточний рік"), KeyboardButton(text="🚀 Наступний рік")],
        [KeyboardButton(text="⚙️ Змінити зміну")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)

def shift_selection():
    # Твої 5 змін А, Б, В, Г, Д
    shifts = [
        [KeyboardButton(text="Зміна А"), KeyboardButton(text="Зміна Б")],
        [KeyboardButton(text="Зміна В"), KeyboardButton(text="Зміна Г")],
        [KeyboardButton(text="Зміна Д")],
        [KeyboardButton(text="⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=shifts, resize_keyboard=True)
