from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def start_kb():
    buttons = [[KeyboardButton(text=f"Зміна {l}") for l in "АБВГД"]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def menu_kb():
    kb = [
        [KeyboardButton(text="Мій графік на сьогодні")],
        [KeyboardButton(text="Графік на місяць")],
        [KeyboardButton(text="Графік на рік (файл)")], # Додана кнопка
        [KeyboardButton(text="Змінити зміну")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

