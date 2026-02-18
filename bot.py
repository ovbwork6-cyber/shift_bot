import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
import uvicorn

# Ваші модулі
import config
import handlers
import database

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримуємо токен
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено!")

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Підключаємо ваші обробники з handlers.py
# Якщо там є Router, то:
dp.include_router(handlers.router)

# Або якщо там просто функції - додайте їх вручну:
# dp.message.register(handlers.start, Command("start"))
# dp.message.register(handlers.help_command, Command("help"))

# Веб-сервер для вебхуків
async def webhook(request: Request) -> Response:
    try:
        update = await request.json()
        await dp.feed_webhook_update(bot, update)
        return Response()
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return Response(status_code=500)

async def health(request: Request) -> Response:
    return Response(content="OK", media_type="text/plain")

# Ініціалізація бази даних
database.init_db()

async def main():
    # Отримуємо URL від Render
    RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/webhook"
        await bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook встановлено на {webhook_url}")
    
    # Створюємо веб-додаток
    app = Starlette(routes=[
        Route("/webhook", webhook, methods=["POST"]),
        Route("/health", health, methods=["GET"]),
    ])
    
    # Запускаємо сервер
    PORT = int(os.environ.get('PORT', 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
