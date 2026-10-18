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

import config
import handlers
import database
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)

TOKEN = config.TOKEN
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(handlers.router)

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

async def health(request: Request) -> Response:
    return Response(content="OK", media_type="text/plain")

@asynccontextmanager
async def lifespan(app: Starlette):
    database.init_db()
    setup_scheduler(bot) # Запуск автонагадувань
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        webhook_url = f"{render_url}/webhook"
        await bot.set_webhook(url=webhook_url)
        logging.info(f"🚀 Webhook встановлено на: {webhook_url}")
    yield
    await bot.delete_webhook()
    await bot.session.close()

app = Starlette(lifespan=lifespan, routes=[
    Route("/webhook", webhook, methods=["POST"]),
    Route("/health", health, methods=["GET"]),
])

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
