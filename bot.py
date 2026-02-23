import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
import uvicorn
from contextlib import asynccontextmanager

# Твої модулі
import config as bot_config
import handlers
import database

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримуємо токен з Environment Variables Render
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено в налаштуваннях Render!")

# Ініціалізація бота (з підтримкою HTML)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Підключаємо роутер з handlers.py
dp.include_router(handlers.router)

# Обробник Webhook від Telegram
async def webhook(request: Request) -> Response:
    try:
        update_data = await request.json()
        from aiogram.types import Update
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return Response(status_code=200)
    except Exception as e:
        logging.error(f"Помилка Webhook: {e}")
        return Response(status_code=500)

# Перевірка працездатності для Render (Health Check)
async def health(request: Request) -> Response:
    return Response(content="OK", media_type="text/plain")

# Керування життєвим циклом програми
@asynccontextmanager
async def lifespan(app: Starlette):
    # Дії при запуску
    database.init_db()
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        webhook_url = f"{render_url}/webhook"
        await bot.set_webhook(url=webhook_url)
        logging.info(f"🚀 Webhook встановлено на: {webhook_url}")
    yield
    # Дії при вимкненні (закриваємо сесії)
    logging.info("Shutting down...")
    await bot.delete_webhook()
    await bot.session.close()

# Створення Web-додатка
app = Starlette(lifespan=lifespan, routes=[
    Route("/webhook", webhook, methods=["POST"]),
    Route("/health", health, methods=["GET"]),
])

if __name__ == "__main__":
    # Отримуємо порт, який видає Render
    PORT = int(os.environ.get('PORT', 8000))
    # Запускаємо сервер uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
