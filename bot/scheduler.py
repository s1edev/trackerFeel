import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TIMEZONE, MOOD_CHECK_TIME
from keyboards import get_main_menu

logger = logging.getLogger(__name__)

# Хранилище ID пользователей для рассылки
active_users = set()


def add_user(user_id: int):
    active_users.add(user_id)


def remove_user(user_id: int):
    active_users.discard(user_id)


class MoodScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=ZoneInfo(TIMEZONE))
        self._job_added = False

    def start(self):
        if not self._job_added:
            hour, minute = map(int, MOOD_CHECK_TIME.split(":"))
            self.scheduler.add_job(
                self._send_mood_check,
                CronTrigger(hour=hour, minute=minute),
                id="daily_mood_check",
                replace_existing=True,
            )
            self._job_added = True
        self.scheduler.start()
        logger.info(f"Scheduled daily mood check at {MOOD_CHECK_TIME} {TIMEZONE}")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    async def _send_mood_check(self):
        from main import bot

        count = 0
        errors = 0

        for user_id in list(active_users):
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text="Как прошло твоё настроение сегодня? 🌟\n\n"
                         "Пару минут рефлексии помогут лучше понять себя.",
                    reply_markup=get_main_menu(),
                )
                count += 1
                logger.info(f"Sent mood check to user {user_id}")
            except Exception as e:
                errors += 1
                logger.error(f"Error sending mood check to user {user_id}: {e}")
                # Если бот заблокирован, удаляем пользователя
                if "blocked" in str(e).lower():
                    remove_user(user_id)

        logger.info(f"Daily mood check completed: {count} sent, {errors} errors")


scheduler = MoodScheduler()
