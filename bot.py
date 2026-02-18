import os
import asyncio
import logging
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Імпортуємо ваші модулі
import config
import handlers
import database

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримуємо токен з оточення
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено в змінних оточення!")

# Render надає цю змінну автоматично
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')
PORT = int(os.environ.get('PORT', 8000))

# Ініціалізація бази даних
database.init_db()

# Створюємо додаток
application = Application.builder().token(TOKEN).updater(None).build()

# Додаємо ваші обробники з handlers.py
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handlers.start(update, context)  # викликає вашу логіку

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handlers.help(update, context)

# Додайте всі ваші команди
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
# ... додайте інші команди

# Додайте обробник повідомлень (якщо є)
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))

async def main():
    # Встановлюємо вебхук
    webhook_url = f"{RENDER_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Вебхук встановлено на {webhook_url}")
    
    # Обробник для Telegram вебхуків
    async def telegram_webhook(request: Request) -> Response:
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.update_queue.put(update)
            return Response()
        except Exception as e:
            logger.error(f"Помилка вебхука: {e}")
            return Response(status_code=500)
    
    # Health check для Render (щоб сервіс не перезапускався) [citation:4]
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")
    
    # Створюємо веб-додаток
    starlette_app = Starlette(routes=[
        Route("/webhook", telegram_webhook, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),
        Route("/healthcheck", health_check, methods=["GET"]),  # Render іноді використовує це
    ])
    
    # Запускаємо веб-сервер
    import uvicorn
    server = uvicorn.Server(uvicorn.Config(
        starlette_app, 
        host="0.0.0.0", 
        port=PORT,
        log_level="info"
    ))
    
    async with application:
        await application.start()
        await server.serve()
        await application.stop()

if __name__ == "__main__":
    asyncio.run(main())