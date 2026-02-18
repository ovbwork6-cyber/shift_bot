import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (user_id INTEGER PRIMARY KEY, shift TEXT)''')
    conn.commit()
    conn.close()

def set_user_shift(user_id, shift):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', (user_id, shift))
    conn.commit()
    conn.close()

def get_user_shift(user_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT shift FROM users WHERE user_id = ?', (user_id,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else None