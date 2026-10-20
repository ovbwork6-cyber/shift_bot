import calendar
import os
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont

# --- 15-ДЕННИЙ ЦИКЛ ЗМІННОСТІ (Anchor: 2026-01-01) ---
SHIFT_PATTERNS = {
    'А': [1, 0, 0, 3, 3, 3, 0, 0, 2, 2, 2, 0, 0, 1, 1],
    'Б': [0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3],
    'В': [0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 2, 2, 2, 0],
    'Г': [3, 3, 3, 0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0],
    'Д': [2, 2, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 2]
}

ANCHOR_DATE = date(2026, 1, 1)

MONTHS_UA = [
    "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
]
UKR_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
SHIFTS = ['А', 'Б', 'В', 'Г', 'Д']

# Кольори для місячного графіка (кружечки)
COLORS_CIRCLE = {
    1: (255, 0, 0),       # 1 - Нічна (Червоний)
    2: (0, 150, 0),       # 2 - Ранкова (Зелений)
    3: (255, 150, 0),     # 3 - Вечірня (Помаранчевий)
    0: (220, 220, 220)    # Вихідний (Сірий)
}

# Кольори для плаката на рік (як на фото оригіналу)
COLOR_HEADER_WEEKDAY = (212, 118, 59)   # Терракотовий/Помаранчевий для буднів
COLOR_HEADER_WEEKEND = (30, 115, 190)   # Синій для вихідних (Сб, Нд)
COLOR_SHIFT_WORK = (212, 118, 59)      # Помаранчева заливка клітинки зі зміною
COLOR_SHIFT_OFF = (240, 240, 240)       # Світло-сіра клітинка для вихідного
COLOR_MONTH_TITLE = (40, 90, 160)       # Синій колір місяців

# Завантаження кириличного шрифту
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 32)
    FONT_HEADER = ImageFont.truetype(FONT_PATH, 16)
    FONT_DAY = ImageFont.truetype(FONT_PATH, 18)
    FONT_CELL = ImageFont.truetype(FONT_PATH, 12)
    FONT_LEGEND = ImageFont.truetype(FONT_PATH, 15)
except Exception:
    FONT_TITLE = FONT_HEADER = FONT_DAY = FONT_CELL = FONT_LEGEND = ImageFont.load_default()

def get_shift_code(shift_letter: str, target_date: date) -> int:
    """Зациклений розрахунок номеру зміни (1, 2, 3 або 0) на будь-яку дату"""
    delta_days = (target_date - ANCHOR_DATE).days
    idx = delta_days % 15
    return SHIFT_PATTERNS[shift_letter][idx]

def get_status(shift_letter: str, date_obj: datetime) -> str:
    code = get_shift_code(shift_letter, date_obj.date())
    if code == 0:
        return "Вихідний ☕"
    return f"Зміна №{code} 🛠"

# --- 1. ГРАФІК НА МІСЯЦЬ (ПОТОЧНИЙ ТА НАСТУПНИЙ) ---
def draw_month_image(shift_letter: str, year: int, month: int) -> str:
    width, height = 600, 580
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    title_text = f"{MONTHS_UA[month]} {year} | Зміна {shift_letter}"
    draw.text((width // 2, 35), title_text, fill="black", font=FONT_TITLE, anchor="mm")

    start_x, step_x = 50, 75
    start_y = 85
    for i, day_name in enumerate(UKR_DAYS):
        draw.text((start_x + i * step_x + 25, start_y), day_name, fill="gray", font=FONT_HEADER, anchor="mm")

    cal = calendar.monthcalendar(year, month)
    radius = 22
    curr_y = start_y + 45

    for week in cal:
        for i, day in enumerate(week):
            if day == 0:
                continue
            x = start_x + i * step_x + 25
            y = curr_y + 20
            dt = date(year, month, day)
            code = get_shift_code(shift_letter, dt)
            
            color = COLORS_CIRCLE[code]
            text_color = "white" if code in [1, 2, 3] else "black"

            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            draw.text((x, y), str(day), fill=text_color, font=FONT_DAY, anchor="mm")
        curr_y += 55

    legend_y = height - 45
    items = [(COLORS_CIRCLE[1], "Зміна №1"), (COLORS_CIRCLE[2], "Зміна №2"), (COLORS_CIRCLE[3], "Зміна №3"), (COLORS_CIRCLE[0], "Вихідний")]
    leg_x = 45
    for color, label in items:
        draw.rectangle([leg_x, legend_y, leg_x + 20, legend_y + 20], fill=color, outline="black")
        draw.text((leg_x + 28, legend_y + 10), label, fill="black", font=FONT_LEGEND, anchor="lm")
        leg_x += 135

    os.makedirs("static", exist_ok=True)
    file_path = f"static/month_{shift_letter}_{year}_{month}.png"
    img.save(file_path)
    return file_path

# --- 2. ЗАГАЛЬНИЙ ГРАФІК НА РІК ДЛЯ DCS (ЯК НА ФОТО ОРИГІНАЛУ) ---
def generate_year_file(user_shift: str, year: int) -> str:
    cell_w, cell_h = 24, 18
    margin_left = 130
    margin_top = 80
    month_block_h = cell_h * 6 + 6

    width = margin_left + 31 * cell_w + 30
    height = margin_top + 12 * month_block_h + 40

    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Головний заголовок плаката
    draw.text((width // 2, 40), f"ГРАФІК {year} РІК", fill=(30, 115, 190), font=FONT_TITLE, anchor="mm")

    current_y = margin_top

    for month in range(1, 13):
        # Назва місяця
        draw.rectangle([10, current_y, margin_left - 30, current_y + cell_h - 1], fill=(220, 230, 242), outline="gray")
        draw.text((margin_left // 2 - 10, current_y + cell_h // 2), MONTHS_UA[month], fill=COLOR_MONTH_TITLE, font=FONT_HEADER, anchor="mm")

        days_in_m = calendar.monthrange(year, month)[1]

        # Дні місяця (1..31) в шапці
        for day in range(1, 32):
            x = margin_left + (day - 1) * cell_w
            if day <= days_in_m:
                dt = date(year, month, day)
                is_weekend = dt.weekday() >= 5
                bg_color = COLOR_HEADER_WEEKEND if is_weekend else COLOR_HEADER_WEEKDAY
                draw.rectangle([x, current_y, x + cell_w - 1, current_y + cell_h - 1], fill=bg_color, outline="white")
                draw.text((x + cell_w // 2, current_y + cell_h // 2), str(day), fill="white", font=FONT_CELL, anchor="mm")
            else:
                draw.rectangle([x, current_y, x + cell_w - 1, current_y + cell_h - 1], fill=(200, 200, 200), outline="gray")

        # Рядки для всіх 5 змін (А, Б, В, Г, Д)
        for s_idx, s_letter in enumerate(SHIFTS):
            row_y = current_y + (s_idx + 1) * cell_h
            
            # Літера зміни
            draw.rectangle([margin_left - 25, row_y, margin_left - 1, row_y + cell_h - 1], fill=(240, 240, 240), outline="gray")
            draw.text((margin_left - 13, row_y + cell_h // 2), s_letter, fill="black", font=FONT_CELL, anchor="mm")

            for day in range(1, 32):
                x = margin_left + (day - 1) * cell_w
                if day <= days_in_m:
                    dt = date(year, month, day)
                    code = get_shift_code(s_letter, dt)
                    
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
