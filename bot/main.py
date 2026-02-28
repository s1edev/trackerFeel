import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import Base, engine
from scheduler import scheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def register_handlers():
    from handlers.start import router as start_router
    from handlers.mood import router as mood_router
    from handlers.graph import router as graph_router
    from handlers.day import router as day_router
    from handlers.admin import router as admin_router

    dp.include_router(start_router)
    dp.include_router(mood_router)
    dp.include_router(graph_router)
    dp.include_router(day_router)
    dp.include_router(admin_router)


async def on_startup():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    logger.info("Starting scheduler...")
    scheduler.start()
    logger.info("Scheduler started - daily mood check at 20:30")


async def on_shutdown():
    logger.info("Shutting down scheduler...")
    scheduler.stop()
    logger.info("Closing bot session...")
    await bot.session.close()


def main():
    register_handlers()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    logger.info("Starting bot in polling mode...")
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
