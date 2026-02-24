import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Створюємо таблицю, якщо її немає
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            shift TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_shift(user_id: int, shift: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Використовуємо REPLACE, щоб оновлювати дані
    cursor.execute('INSERT OR REPLACE INTO users (user_id, shift) VALUES (?, ?)', (user_id, shift))
    conn.commit()
    conn.close()

def get_user_shift(user_id: int):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT shift FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
