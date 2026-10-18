from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import database
import logic

scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

async def check_and_send_notifications(bot):
    now = datetime.now()
    today_date = now.date()
    tomorrow_date = today_date + timedelta(days=1)
    
    users = database.get_all_users()
    for user_id, shift in users:
        # Перевірка на сьогодні та завтра
        today_status = logic.get_shift_status(shift, datetime.combine(today_date, datetime.min.time()))
        tomorrow_status = logic.get_shift_status(shift, datetime.combine(tomorrow_date, datetime.min.time()))
        
        current_hour = now.hour

        # 1. Нічна зміна (Зміна №1) - нагадування о 17:00 в день початку нічної зміни
        if today_status == "1" and current_hour == 17:
            await bot.send_message(user_id, "🔔 <b>Нагадування!</b> Сьогодні ввечері у вас <b>Нічна зміна (Зміна №1)</b>!")

        # 2. Ранкова зміна (Зміна №2) - нагадування о 20:00 напередодні
        if tomorrow_status == "2" and current_hour == 20:
            await bot.send_message(user_id, "🔔 <b>Нагадування!</b> Завтра о 07:00 ранку у вас <b>Ранкова зміна (Зміна №2)</b>!")

        # 3. Вечірня зміна (Зміна №3) - нагадування о 09:00 ранку в день зміни
        if today_status == "3" and current_hour == 9:
            await bot.send_message(user_id, "🔔 <b>Нагадування!</b> Сьогодні ввечері у вас <b>Вечірня зміна (Зміна №3)</b>!")

def setup_scheduler(bot):
    # Запуск перевірки щогодини
    scheduler.add_job(check_and_send_notifications, "cron", minute=0, args=[bot])
    scheduler.start()
