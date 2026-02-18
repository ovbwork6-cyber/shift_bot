import os

# Токен береться з оточення (додамо на Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Шляхи до файлів
import os.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DB_PATH = os.path.join(BASE_DIR, 'users.db')

# Для зображень використовуйте:
def get_image_path(filename):
    return os.path.join(STATIC_DIR, filename)