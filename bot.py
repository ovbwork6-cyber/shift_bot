import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
import handlers
import database
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(handlers.router)

async def main():
    # Ініціалізація бази даних та планировщика
    database.init_db()
    setup_scheduler(bot)

    # Видаляємо всі застряглі оновлення та скидаємо Webhook
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info("🚀 Бот заповнений і починає слухати повідомлення (Polling)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
