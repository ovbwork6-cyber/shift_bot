import sqlite3
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Таблиця користувачів з прапорцем авторизації
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            shift TEXT,
            is_authorized INTEGER DEFAULT 0
        )
    ''')
    # Відпустки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_date TEXT,
            end_date TEXT
        )
    ''')
    # Лікарняні
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sick_leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_date TEXT,
            end_date TEXT
        )
    ''')
    # Додаткові зміни
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extra_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            shift_date TEXT,
            shift_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_user_authorized(user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_authorized FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def authorize_user(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, is_authorized) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET is_authorized=1", (user_id,))
    conn.commit()
    conn.close()

def save_user_shift(user_id: int, shift: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET shift = ? WHERE user_id = ?", (shift, user_id))
    conn.commit()
    conn.close()

def get_user_shift(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT shift FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, shift FROM users WHERE is_authorized = 1 AND shift IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Відпустки
def add_vacation(user_id: int, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vacations (user_id, start_date, end_date) VALUES (?, ?, ?)", (user_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_user_vacations(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, start_date, end_date FROM vacations WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Лікарняні
def add_sick_leave(user_id: int, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sick_leaves (user_id, start_date, end_date) VALUES (?, ?, ?)", (user_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_user_sick_leaves(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, start_date, end_date FROM sick_leaves WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Додаткові зміни
def add_extra_shift(user_id: int, shift_date: str, shift_type: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO extra_shifts (user_id, shift_date, shift_type) VALUES (?, ?, ?)", (user_id, shift_date, shift_type))
    conn.commit()
    conn.close()

def get_user_extra_shifts(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, shift_date, shift_type FROM extra_shifts WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
