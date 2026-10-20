import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Таблиця користувачів
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (user_id INTEGER PRIMARY KEY, shift TEXT)''')
    # Персональні відпустки
    cur.execute('''CREATE TABLE IF NOT EXISTS vacations 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, start_date TEXT, end_date TEXT)''')
    # Персональні лікарняні
    cur.execute('''CREATE TABLE IF NOT EXISTS sick_leaves 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, start_date TEXT, end_date TEXT)''')
    # Персональні додаткові зміни
    cur.execute('''CREATE TABLE IF NOT EXISTS extra_shifts 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, shift_date TEXT, shift_type TEXT)''')
    conn.commit()
    conn.close()

def set_user_shift(user_id, shift):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO users (user_id, shift) VALUES (?, ?)', (user_id, shift))
    conn.commit()
    conn.close()

def get_user_shift(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT shift FROM users WHERE user_id = ?', (user_id,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else None

# Персональні відпустки
def add_vacation(user_id, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO vacations (user_id, start_date, end_date) VALUES (?, ?, ?)', (user_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_user_vacations(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, start_date, end_date FROM vacations WHERE user_id = ? ORDER BY start_date', (user_id,))
    res = cur.fetchall()
    conn.close()
    return res

# Персональні лікарняні
def add_sick_leave(user_id, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO sick_leaves (user_id, start_date, end_date) VALUES (?, ?, ?)', (user_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_user_sick_leaves(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, start_date, end_date FROM sick_leaves WHERE user_id = ? ORDER BY start_date', (user_id,))
    res = cur.fetchall()
    conn.close()
    return res

# Персональні додаткові зміни
def add_extra_shift(user_id, shift_date, shift_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO extra_shifts (user_id, shift_date, shift_type) VALUES (?, ?, ?)', (user_id, shift_date, shift_type))
    conn.commit()
    conn.close()

def get_user_extra_shifts(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, shift_date, shift_type FROM extra_shifts WHERE user_id = ? ORDER BY shift_date', (user_id,))
    res = cur.fetchall()
    conn.close()
    return res
