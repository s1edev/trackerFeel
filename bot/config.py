import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Use absolute path for database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "mood_tracker.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Yekaterinburg")
MOOD_CHECK_TIME = os.getenv("MOOD_CHECK_TIME", "20:30")

# Канал для обязательной подписки
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID канала (начинается с @ или -100...)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # Username канала для ссылки (без @)
