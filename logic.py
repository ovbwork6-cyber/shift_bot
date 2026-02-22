from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import calendar
import os

# 1. Отримуємо шлях до папки, де лежить сам файл logic.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. З'єднуємо шлях до папки з назвою файлу шрифту
# Це гарантує, що бот знайде файл незалежно від того, де запущений
font_path = os.path.join(current_dir, "arial.ttf")

def draw_month_image(shift, year, month):
    # ... твій код ...
    
    try:
        # Тепер використовуємо змінну font_path
        font_title = ImageFont.truetype(font_path, 28)
        font_days = ImageFont.truetype(font_path, 20)
        font_legend = ImageFont.truetype(font_path, 18)
    except OSError:
        # Якщо файл шрифту все одно не знайдено (наприклад, забув завантажити)
        print(f"Помилка: не знайдено шрифт за шляхом {font_path}")
        font_title = font_days = font_legend = ImageFont.load_default()

# Ваші дані змін (цикл 15 днів)
SHIFT_DATA = {
    'А': [1, 0, 0, 3, 3, 3, 0, 0, 2, 2, 2, 0, 0, 1, 1],
    'Б': [0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3],
    'В': [0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 2, 2, 2, 0],
    'Г': [3, 3, 3, 0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0],
    'Д': [2, 2, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 2]
}

ANCHOR_DATE = datetime(2026, 1, 1)

WEEKDAYS_UA = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Нд"}
MONTHS_UA = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень", 5: "Травень", 6: "Червень",
    7: "Липень", 8: "Серпень", 9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень"
}
# Кольори для змін
COLORS = {
    1: (255, 0, 0),   # Червоний (Зміна 1)
    2: (0, 153, 0),   # Зелений (Зміна 2)
    3: (255, 153, 0),     # Помаранчевий (Зміна 3)
    0: (220, 220, 220)  # Світло-сірий (Вихідний)
}

def get_status(shift, date_obj):
    """Розраховує статус зміни на конкретну дату"""
    delta = (date_obj - ANCHOR_DATE).days
    idx = delta % 15
    status_code = SHIFT_DATA[shift][idx]
    
    if status_code == 0:
        return "Вихідний ☕"
    return f"Зміна №{status_code} 🛠"

def draw_month_image(shift, year, month):
    # Збільшуємо висоту (H) з 450 до 550, щоб помістилася легенда
    W, H = 600, 550 
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_days = ImageFont.truetype("arial.ttf", 20)
        font_legend = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = font_days = font_legend = ImageFont.load_default()

    # --- Малюємо заголовок та календар (код залишається тим самим) ---
    month_name = MONTHS_UA[month]
    draw.text((W/2, 30), f"{month_name} {year} | Зміна {shift}", fill=(0,0,0), font=font_title, anchor="mm")

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    for i, day in enumerate(weekdays):
        draw.text((70 + i*75, 80), day, fill=(100,100,100), font=font_days, anchor="mm")

    cal = calendar.monthcalendar(year, month)
    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            if day == 0: continue
            x, y = 70 + c*75, 130 + r*60
            date_obj = datetime(year, month, day)
            delta = (date_obj - ANCHOR_DATE).days
            status_code = SHIFT_DATA[shift][delta % 15]
            
            draw.ellipse([x-22, y-22, x+22, y+22], fill=COLORS[status_code])
            text_color = (255,255,255) if status_code != 0 else (0,0,0)
            draw.text((x, y), str(day), fill=text_color, font=font_days, anchor="mm")

    # --- НОВИЙ БЛОК: МАЛЮЄМО ЛЕГЕНДУ ---
    start_y = 480  # Координата Y для початку легенди
    legend_items = [
        (1, "Зміна №1"), (2, "Зміна №2"), 
        (3, "Зміна №3"), (0, "Вихідний")
    ]
    
    # Малюємо елементи легенди в один рядок
    for i, (code, label) in enumerate(legend_items):
        lx = 50 + i * 140  # Відступ між елементами
        # Малюємо маленький кольоровий квадратик або кружечок
        draw.rectangle([lx, start_y, lx+20, start_y+20], fill=COLORS[code], outline=(0,0,0))
        # Малюємо текст поруч
        draw.text((lx + 30, start_y + 10), label, fill=(0,0,0), font=font_legend, anchor="lm")

    filename = f"month_{shift}.png"
    img.save(filename)
    return filename

def generate_year_file(shift, year):
    """Генерує .txt файл з графіком на весь рік"""
    filename = f"schedule_{shift}_{year}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"ГРАФІК РОБОТИ НА {year} РІК (ЗМІНА {shift})\n")
        f.write("="*45 + "\n")
        
        for month in range(1, 13):
            f.write(f"\n--- {MONTHS_UA[month].upper()} ---\n")
            days_in_month = calendar.monthrange(year, month)[1]
            
            for day in range(1, days_in_month + 1):
                date_obj = datetime(year, month, day)
                day_name = WEEKDAYS_UA[date_obj.weekday()]
                status = get_status(shift, date_obj)
                f.write(f"{day:02d}.{month:02d} ({day_name}) - {status}\n")
            f.write("-" * 20 + "\n")
            
    return filename
