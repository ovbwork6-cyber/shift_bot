import calendar
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Данi змiн
SHIFT_DATA = {
    'А': [1, 0, 0, 3, 3, 3, 0, 0, 2, 2, 2, 0, 0, 1, 1],
    'Б': [0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3],
    'В': [0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 2, 2, 2, 0],
    'Г': [3, 3, 3, 0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0],
    'Д': [2, 2, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 2]
}

ANCHOR_DATE = datetime(2026, 1, 1)

MONTHS_UA = [
    "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
]
SHIFTS = ['А', 'Б', 'В', 'Г', 'Д']

# Кольори згідно з фото оригіналу
COLOR_HEADER_WEEKDAY = (212, 118, 59)   # Помаранчевий/терракотовий для буднів
COLOR_HEADER_WEEKEND = (30, 115, 190)   # Яскраво-синій для вихідних (Сб/Нд)
COLOR_SHIFT_WORK = (212, 118, 59)      # Помаранчева заливка для робочих змін (1, 2, 3)
COLOR_SHIFT_OFF = (235, 235, 235)       # Світло-сірий для вихідних
COLOR_MONTH_TITLE = (40, 90, 160)       # Синій колір для назв місяців

# Завантаження шрифту
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 34)
    FONT_HEADER = ImageFont.truetype(FONT_PATH, 16)
    FONT_CELL = ImageFont.truetype(FONT_PATH, 13)
except Exception:
    FONT_TITLE = FONT_HEADER = FONT_CELL = ImageFont.load_default()

def get_shift_code(shift_letter, date_obj):
    delta_days = (date_obj.date() - ANCHOR_DATE.date()).days
    idx = delta_days % 15
    return SHIFT_DATA[shift_letter][idx]

def draw_month_image(shift_letter, year, month):
    # Залишається ваша робоча функція для місяця з кружечками
    pass

def generate_year_file(user_shift: str, year: int) -> str:
    cell_w, cell_h = 24, 18
    margin_left = 130
    margin_top = 80
    month_block_h = cell_h * 6 + 6  # 1 рядок чисел + 5 рядків змін (А..Д)

    width = margin_left + 31 * cell_w + 30
    height = margin_top + 12 * month_block_h + 40

    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Великий заголовок зверху
    draw.text((width // 2, 40), f"ГРАФІК {year} РІК", fill=(30, 115, 190), font=FONT_TITLE, anchor="mm")

    current_y = margin_top

    for month in range(1, 13):
        # Колонка «Місяць / Зміна»
        draw.rectangle([10, current_y, margin_left - 30, current_y + cell_h - 1], fill=(220, 230, 242), outline="gray")
        draw.text((margin_left // 2 - 10, current_y + cell_h // 2), MONTHS_UA[month], fill=COLOR_MONTH_TITLE, font=FONT_HEADER, anchor="mm")

        days_in_m = calendar.monthrange(year, month)[1]

        # Шапка чисел днів (1..31): Сині для вихідних, Помаранчеві для буднів
        for day in range(1, 32):
            x = margin_left + (day - 1) * cell_w
            if day <= days_in_m:
                dt = datetime(year, month, day)
                is_weekend = dt.weekday() >= 5
                bg_color = COLOR_HEADER_WEEKEND if is_weekend else COLOR_HEADER_WEEKDAY
                draw.rectangle([x, current_y, x + cell_w - 1, current_y + cell_h - 1], fill=bg_color, outline="white")
                draw.text((x + cell_w // 2, current_y + cell_h // 2), str(day), fill="white", font=FONT_CELL, anchor="mm")
            else:
                draw.rectangle([x, current_y, x + cell_w - 1, current_y + cell_h - 1], fill=(200, 200, 200), outline="gray")

        # 5 рядків змін (А, Б, В, Г, Д)
        for s_idx, s_letter in enumerate(SHIFTS):
            row_y = current_y + (s_idx + 1) * cell_h
            
            # Позначка букви зміни збоку
            draw.rectangle([margin_left - 25, row_y, margin_left - 1, row_y + cell_h - 1], fill=(240, 240, 240), outline="gray")
            draw.text((margin_left - 13, row_y + cell_h // 2), s_letter, fill="black", font=FONT_CELL, anchor="mm")

            for day in range(1, 32):
                x = margin_left + (day - 1) * cell_w
                if day <= days_in_m:
                    dt = datetime(year, month, day)
                    code = get_shift_code(s_letter, dt)
                    
                    # Помаранчева заливка для робочих змін (1, 2, 3), сіра для вихідного
                    cell_bg = COLOR_SHIFT_WORK if code in [1, 2, 3] else COLOR_SHIFT_OFF
                    text_str = str(code) if code != 0 else ""
                    
                    draw.rectangle([x, row_y, x + cell_w - 1, row_y + cell_h - 1], fill=cell_bg, outline="gray")
                    if text_str:
                        draw.text((x + cell_w // 2, row_y + cell_h // 2), text_str, fill="black", font=FONT_CELL, anchor="mm")
                else:
                    draw.rectangle([x, row_y, x + cell_w - 1, row_y + cell_h - 1], fill=(180, 180, 180), outline="gray")

        current_y += month_block_h

    os.makedirs("static", exist_ok=True)
    file_path = f"static/year_DCS_{year}.png"
    img.save(file_path)
    return file_path
