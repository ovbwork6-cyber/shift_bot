import calendar
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Спроба завантажити чіткий системний шрифт
try:
    FONT_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    FONT_HEADER = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    FONT_DAY = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    FONT_LEGEND = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    FONT_TITLE = FONT_HEADER = FONT_DAY = FONT_LEGEND = ImageFont.load_default()

# Кольори змін
COLOR_NIGHT = (255, 0, 0)      # 1 - Нічна (Червоний)
COLOR_MORNING = (0, 150, 0)    # 2 - Ранкова (Зелений)
COLOR_EVENING = (255, 150, 0)  # 3 - Вечірня (Помаранчевий)
COLOR_OFF = (220, 220, 220)    # Вихідний (Сірий)

UKR_MONTHS = [
    "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
]

UKR_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

def get_shift_for_day(shift_letter: str, date_obj: datetime) -> str:
    """
    Тут має бути ваша логіка розрахунку зміни (1, 2, 3 або 0/вихідний).
    Поповертає '1', '2', '3' або '0'.
    """
    # Приклад алгоритму (замініть на свою точну логіку циклу зміності):
    base_date = datetime(2026, 1, 1)
    delta_days = (date_obj - base_date).days
    
    # Приклад 4-бригадного циклу (222, 111, 333, вихідні)
    shift_offset = {"А": 0, "Б": 2, "В": 4, "Г": 6, "Д": 8}.get(shift_letter, 0)
    cycle_day = (delta_days + shift_offset) % 12
    
    if cycle_day in [0, 1, 2]:
        return "1"  # Нічна
    elif cycle_day in [3, 4, 5]:
        return "2"  # Ранкова
    elif cycle_day in [6, 7, 8]:
        return "3"  # Вечірня
    return "0"      # Вихідний

def draw_month_image(shift_letter: str, year: int, month: int) -> str:
    width, height = 600, 650
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Заголовок
    title_text = f"{UKR_MONTHS[month]} {year} | Зміна {shift_letter}"
    draw.text((width // 2, 40), title_text, fill="black", font=FONT_TITLE, anchor="mm")

    # Дні тижня
    start_x = 50
    step_x = 75
    start_y = 100
    for i, day_name in enumerate(UKR_DAYS):
        draw.text((start_x + i * step_x + 25, start_y), day_name, fill="gray", font=FONT_HEADER, anchor="mm")

    # Календар
    cal = calendar.monthcalendar(year, month)
    radius = 24
    curr_y = start_y + 40

    for week in cal:
        for i, day in enumerate(week):
            if day == 0:
                continue
            
            x = start_x + i * step_x + 25
            y = curr_y + 25
            
            # Визначення типу зміни
            dt = datetime(year, month, day)
            shift_type = get_shift_for_day(shift_letter, dt)
            
            if shift_type == "1":
                color = COLOR_NIGHT
                text_color = "white"
            elif shift_type == "2":
                color = COLOR_MORNING
                text_color = "white"
            elif shift_type == "3":
                color = COLOR_EVENING
                text_color = "white"
            else:
                color = COLOR_OFF
                text_color = "black"

            # Малюємо круг
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            # Текст числа
            draw.text((x, y), str(day), fill=text_color, font=FONT_DAY, anchor="mm")

        curr_y += 60

    # Легенда знизу
    legend_y = height - 50
    items = [
        (COLOR_NIGHT, "Зміна №1"),
        (COLOR_MORNING, "Зміна №2"),
        (COLOR_EVENING, "Зміна №3"),
        (COLOR_OFF, "Вихідний")
    ]
    
    leg_x = 40
    for color, label in items:
        draw.rectangle([leg_x, legend_y, leg_x + 20, legend_y + 20], fill=color, outline="black")
        draw.text((leg_x + 30, legend_y + 10), label, fill="black", font=FONT_LEGEND, anchor="lm")
        leg_x += 135

    # Збереження зображення
    os.makedirs("static", exist_ok=True)
    file_path = f"static/month_{shift_letter}_{year}_{month}.png"
    img.save(file_path)
    return file_path

# Аліас для підтримки річного файлу або прямих викликів
def generate_year_file(user_shift: str, year: int) -> str:
    now = datetime.now()
    return draw_month_image(user_shift, year, now.month)
