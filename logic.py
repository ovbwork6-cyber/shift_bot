import calendar
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Кольори змін
COLOR_NIGHT = (255, 0, 0)        # 1 - Нічна (Червоний)
COLOR_MORNING = (0, 150, 0)      # 2 - Ранкова (Зелений)
COLOR_EVENING = (255, 150, 0)    # 3 - Вечірня (Помаранчевий)
COLOR_OFF = (220, 220, 220)      # Вихідний (Сірий)

# Надійне підключення шрифту з підтримкою кирилиці
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 28)
    FONT_HEADER = ImageFont.truetype(FONT_PATH, 18)
    FONT_DAY = ImageFont.truetype(FONT_PATH, 18)
    FONT_LEGEND = ImageFont.truetype(FONT_PATH, 16)
    FONT_SMALL = ImageFont.truetype(FONT_PATH, 12)
except Exception:
    FONT_TITLE = FONT_HEADER = FONT_DAY = FONT_LEGEND = FONT_SMALL = ImageFont.load_default()

UKR_MONTHS = [
    "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
]
UKR_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

def get_shift_for_day(shift_letter: str, date_obj: datetime) -> str:
    base_date = datetime(2026, 1, 1)
    delta_days = (date_obj - base_date).days
    shift_offset = {"А": 0, "Б": 2, "В": 4, "Г": 6, "Д": 8}.get(shift_letter, 0)
    cycle_day = (delta_days + shift_offset) % 12
    
    if cycle_day in [0, 1, 2]:
        return "1"  # Нічна
    elif cycle_day in [3, 4, 5]:
        return "2"  # Ранкова
    elif cycle_day in [6, 7, 8]:
        return "3"  # Вечірня
    return "0"      # Вихідний

# --- ГЕНЕРАЦІЯ ОДНОГО МІСЯЦЯ (КРУЖЕЧКИ) ---
def draw_month_image(shift_letter: str, year: int, month: int) -> str:
    width, height = 600, 650
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    title_text = f"{UKR_MONTHS[month]} {year} | Зміна {shift_letter}"
    draw.text((width // 2, 40), title_text, fill="black", font=FONT_TITLE, anchor="mm")

    start_x, step_x = 50, 75
    start_y = 100
    for i, day_name in enumerate(UKR_DAYS):
        draw.text((start_x + i * step_x + 25, start_y), day_name, fill="gray", font=FONT_HEADER, anchor="mm")

    cal = calendar.monthcalendar(year, month)
    radius = 24
    curr_y = start_y + 40

    for week in cal:
        for i, day in enumerate(week):
            if day == 0:
                continue
            x = start_x + i * step_x + 25
            y = curr_y + 25
            dt = datetime(year, month, day)
            shift_type = get_shift_for_day(shift_letter, dt)
            
            color = COLOR_NIGHT if shift_type == "1" else (
                COLOR_MORNING if shift_type == "2" else (
                COLOR_EVENING if shift_type == "3" else COLOR_OFF
            ))
            text_color = "white" if shift_type in ["1", "2", "3"] else "black"

            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            draw.text((x, y), str(day), fill=text_color, font=FONT_DAY, anchor="mm")
        curr_y += 60

    legend_y = height - 50
    items = [(COLOR_NIGHT, "Зміна №1"), (COLOR_MORNING, "Зміна №2"), (COLOR_EVENING, "Зміна №3"), (COLOR_OFF, "Вихідний")]
    leg_x = 40
    for color, label in items:
        draw.rectangle([leg_x, legend_y, leg_x + 20, legend_y + 20], fill=color, outline="black")
        draw.text((leg_x + 30, legend_y + 10), label, fill="black", font=FONT_LEGEND, anchor="lm")
        leg_x += 135

    os.makedirs("static", exist_ok=True)
    file_path = f"static/month_{shift_letter}_{year}_{month}.png"
    img.save(file_path)
    return file_path

# --- ГЕНЕРАЦІЯ РІЧНОГО ГРАФІКА З КОЛЬОРОВИМИ ЗМІНАМИ ---
def generate_year_file(shift_letter: str, year: int) -> str:
    cell_w, cell_h = 28, 22
    margin_x, margin_y = 120, 80
    width = margin_x + 31 * cell_w + 40
    height = margin_y + 12 * cell_h + 80

    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Заголовок
    draw.text((width // 2, 35), f"Графік чергувань на {year} рік | Зміна {shift_letter}", fill="black", font=FONT_TITLE, anchor="mm")

    # Шапка днів (1..31)
    for day in range(1, 32):
        x = margin_x + (day - 1) * cell_w
        draw.text((x + cell_w // 2, margin_y - 15), str(day), fill="black", font=FONT_SMALL, anchor="mm")

    # Сітка та кольорові клітинки змін для кожного місяця
    for month in range(1, 13):
        y = margin_y + (month - 1) * cell_h
        draw.text((20, y + cell_h // 2), UKR_MONTHS[month], fill="black", font=FONT_HEADER, anchor="lm")
        
        days_in_m = calendar.monthrange(year, month)[1]
        for day in range(1, 31):
            x = margin_x + (day - 1) * cell_w
            if day <= days_in_m:
                dt = datetime(year, month, day)
                shift_type = get_shift_for_day(shift_letter, dt)
                color = COLOR_NIGHT if shift_type == "1" else (
                    COLOR_MORNING if shift_type == "2" else (
                    COLOR_EVENING if shift_type == "3" else COLOR_OFF
                ))
                text_color = "white" if shift_type in ["1", "2", "3"] else "black"
                
                # Замальовуємо клітинку кольором зміни
                draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill=color, outline="gray")
                draw.text((x + cell_w // 2, y + cell_h // 2), shift_type if shift_type != "0" else "В", fill=text_color, font=FONT_SMALL, anchor="mm")
            else:
                draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill=(240, 240, 240))

    os.makedirs("static", exist_ok=True)
    file_path = f"static/year_{shift_letter}_{year}.png"
    img.save(file_path)
    return file_path
