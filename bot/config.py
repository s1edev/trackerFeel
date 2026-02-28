import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mood_tracker.db")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Yekaterinburg")
MOOD_CHECK_TIME = os.getenv("MOOD_CHECK_TIME", "20:30")

# Канал для обязательной подписки
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID канала (начинается с @ или -100...)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # Username канала для ссылки (без @)
