import calendar
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import database

SHIFTS = ["А", "Б", "В", "Г", "Д"]
MONTH_NAMES_UA = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]

BASE_DATE = datetime(2026, 1, 1)
SHIFT_OFFSETS = {"А": 0, "Б": 1, "В": 2, "Г": 3, "Д": 4}

def get_shift_status(shift_letter: str, date_obj: datetime) -> str:
    delta = (date_obj - BASE_DATE).days
    offset = SHIFT_OFFSETS.get(shift_letter, 0)
    cycle_day = (delta + offset) % 5
    if cycle_day == 0: return "1" # Нічна
    elif cycle_day == 1: return "2" # Ранкова
    elif cycle_day == 2: return "3" # Вечірня
    else: return ""

def generate_year_file(user_shift: str, year: int, user_id: int = None) -> str:
    vacations, sicks, extras = [], [], {}
    if user_id:
        for _, s_str, e_str in database.get_user_vacations(user_id):
            try: vacations.append((datetime.strptime(s_str, "%Y-%m-%d").date(), datetime.strptime(e_str, "%Y-%m-%d").date()))
            except ValueError: pass
        for _, s_str, e_str in database.get_user_sick_leaves(user_id):
            try: sicks.append((datetime.strptime(s_str, "%Y-%m-%d").date(), datetime.strptime(e_str, "%Y-%m-%d").date()))
            except ValueError: pass
        for _, d_str, stype in database.get_user_extra_shifts(user_id):
            try: extras[datetime.strptime(d_str, "%Y-%m-%d").date()] = stype
            except ValueError: pass

    col_w_month, col_w_shift, col_w_day, row_h = 140, 50, 38, 30
    margin_x, margin_y = 40, 100

    img_w = margin_x * 2 + col_w_month + col_w_shift + 31 * col_w_day
    img_h = margin_y * 2 + 12 * (6 * row_h) + 60

    img = Image.new("RGB", (img_w, img_h), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 52)
        font_cell = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arialbd.ttf", 18)
    except Exception:
        font_title = font_cell = font_bold = ImageFont.load_default()

    draw.text((img_w // 2 - 250, 25), f"ГРАФІК {year} РІК", fill=(15, 82, 186), font=font_title)

    COLOR_BLUE_HEADER = (25, 118, 210)
    COLOR_ORANGE_HEADER = (224, 86, 36)
    COLOR_VACATION = (76, 175, 80)     # Зелений відпустка
    COLOR_SICK = (33, 150, 243)         # Синій лікарняний
    COLOR_EXTRA = (255, 152, 0)         # Помаранчевий дод. зміна
    COLOR_GRID = (0, 0, 0)

    curr_y = margin_y

    draw.rectangle([margin_x, curr_y, margin_x + col_w_month, curr_y + row_h], outline=COLOR_GRID)
    draw.text((margin_x + 35, curr_y + 5), "Місяць", fill="black", font=font_bold)
    draw.rectangle([margin_x + col_w_month, curr_y, margin_x + col_w_month + col_w_shift, curr_y + row_h], outline=COLOR_GRID)
    draw.text((margin_x + col_w_month + 8, curr_y + 5), "Зміна", fill="black", font=font_bold)
    draw.rectangle([margin_x + col_w_month + col_w_shift, curr_y, margin_x + col_w_month + col_w_shift + 31 * col_w_day, curr_y + row_h], outline=COLOR_GRID)
    draw.text((margin_x + col_w_month + col_w_shift + 400, curr_y + 5), "Число місяця", fill=(15, 82, 186), font=font_bold)

    curr_y += row_h

    for m in range(1, 13):
        days_in_month = calendar.monthrange(year, m)[1]
        draw.rectangle([margin_x, curr_y, margin_x + col_w_month + col_w_shift, curr_y + row_h], outline=COLOR_GRID)
        draw.text((margin_x + 25, curr_y + 5), MONTH_NAMES_UA[m-1], fill=(15, 82, 186), font=font_bold)

        for d in range(1, 32):
            dx = margin_x + col_w_month + col_w_shift + (d - 1) * col_w_day
            if d <= days_in_month:
                dt = datetime(year, m, d)
                bg_col = COLOR_ORANGE_HEADER if dt.weekday() >= 5 else COLOR_BLUE_HEADER
                draw.rectangle([dx, curr_y, dx + col_w_day, curr_y + row_h], fill=bg_col, outline=COLOR_GRID)
                draw.text((dx + (10 if d < 10 else 4), curr_y + 5), str(d), fill="white", font=font_bold)
            else:
                draw.rectangle([dx, curr_y, dx + col_w_day, curr_y + row_h], fill=(210, 210, 210), outline=COLOR_GRID)

        curr_y += row_h

        for sh in SHIFTS:
            sh_bg = (255, 235, 156) if sh == user_shift else "white"
            draw.rectangle([margin_x + col_w_month, curr_y, margin_x + col_w_month + col_w_shift, curr_y + row_h], fill=sh_bg, outline=COLOR_GRID)
            draw.text((margin_x + col_w_month + 18, curr_y + 5), sh, fill=(200, 0, 0) if sh == user_shift else (15, 82, 186), font=font_bold)

            for d in range(1, 32):
                dx = margin_x + col_w_month + col_w_shift + (d - 1) * col_w_day
                if d <= days_in_month:
                    dt = datetime(year, m, d).date()
                    is_vac = any(v_s <= dt <= v_e for v_s, v_e in vacations) if sh == user_shift else False
                    is_sick = any(s_s <= dt <= s_e for s_s, s_e in sicks) if sh == user_shift else False
                    has_extra = dt in extras if sh == user_shift else False

                    val = get_shift_status(sh, datetime(year, m, d))
                    
                    cell_fill = "white"
                    txt = val
                    if is_sick:
                        cell_fill, txt = COLOR_SICK, "Л"
                    elif is_vac:
                        cell_fill, txt = COLOR_VACATION, "В"
                    elif has_extra:
                        cell_fill, txt = COLOR_EXTRA, f"Д{extras[dt]}"

                    draw.rectangle([dx, curr_y, dx + col_w_day, curr_y + row_h], fill=cell_fill, outline=COLOR_GRID)
                    draw.text((dx + (8 if len(txt)>1 else 12), curr_y + 5), txt, fill="white" if cell_fill != "white" else "black", font=font_cell)
                else:
                    draw.rectangle([dx, curr_y, dx + col_w_day, curr_y + row_h], fill=(210, 210, 210), outline=COLOR_GRID)

            curr_y += row_h

    out_path = f"graphic_{year}_{user_shift}.png"
    img.save(out_path)
    return out_path
