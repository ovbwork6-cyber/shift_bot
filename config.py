import os
import os.path

# Токен бота та ID адміна
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 701568112))

# Шляхи та база даних
DB_NAME = "users.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

def get_image_path(filename):
    return os.path.join(STATIC_DIR, filename)
