import os
import logging
import shutil
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from config import CHANNEL_ID, CHANNEL_USERNAME

logger = logging.getLogger(__name__)

router = Router()

ADMIN_ID = 6023070081


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def is_subscribed(user_id: int, bot) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    if not CHANNEL_ID:
        return True  # Если канал не настроен, считаем что подписан

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return True  # При ошибке пропускаем


def get_subscribe_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой подписки"""
    channel_link = f"https://t.me/{CHANNEL_USERNAME}" if CHANNEL_USERNAME else "#"
    keyboard = [
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_link)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("download_db"))
async def cmd_download_db(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды")
        return

    if not await is_subscribed(message.from_user.id, message.bot):
        await message.answer(
            "❌ Для использования этой команды необходимо подписаться на канал",
            reply_markup=get_subscribe_keyboard()
        )
        return

    db_path = os.path.join(os.path.dirname(__file__), "..", "mood_tracker.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        await message.answer(f"❌ База данных не найдена\nПуть: {db_path}")
        return

    try:
        await message.answer("📤 Отправляю базу данных...")
        with open(db_path, "rb") as db_file:
            await message.answer_document(
                document=types.FSInputFile(db_path),
                caption="🗄️ mood_tracker.db"
            )
        logger.info(f"Admin {message.from_user.id} downloaded the database")
    except Exception as e:
        logger.error(f"Error sending database: {e}")
        await message.answer(f"❌ Ошибка при отправке: {e}")


@router.message(Command("upload_db"))
async def cmd_upload_db(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды")
        return

    if not await is_subscribed(message.from_user.id, message.bot):
        await message.answer(
            "❌ Для использования этой команды необходимо подписаться на канал",
            reply_markup=get_subscribe_keyboard()
        )
        return

    # Проверяем, есть ли документ в reply
    if not (message.reply_to_message and message.reply_to_message.document):
        await message.answer(
            "📋 Ответьте на сообщение с файлом .db командой /upload_db"
        )
        return

    document = message.reply_to_message.document
    await process_db_upload(message, document)


# Обработка документа без команды - если админ просто отправил .db файл
@router.message(F.document.file_name.endswith(".db"))
async def handle_db_document(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    if not await is_subscribed(message.from_user.id, message.bot):
        await message.answer(
            "❌ Для загрузки базы данных необходимо подписаться на канал",
            reply_markup=get_subscribe_keyboard()
        )
        return

    await process_db_upload(message, message.document)


async def process_db_upload(message: types.Message, document):
    logger.info(f"Processing DB upload from user {message.from_user.id}")
    logger.info(f"Document: {document.file_name}, file_id: {document.file_id}")

    await message.answer("📥 Загружаю базу данных...")

    db_path = os.path.join(os.path.dirname(__file__), "..", "mood_tracker.db")
    db_path = os.path.abspath(db_path)
    backup_path = f"{db_path}.backup"

    logger.info(f"Database path: {db_path}")

    try:
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            logger.info("Backup created")

        file = await message.bot.get_file(document.file_id)
        logger.info(f"Telegram file path: {file.file_path}")

        await message.bot.download_file(file.file_path, destination=db_path)
        logger.info(f"File downloaded to {db_path}, size: {os.path.getsize(db_path)} bytes")

        await message.answer("✅ База данных успешно заменена!\n\n📁 Старая версия сохранена как `mood_tracker.db.backup`", parse_mode="Markdown")
        logger.info(f"Admin {message.from_user.id} uploaded new database")

    except Exception as e:
        logger.error(f"Error uploading database: {e}", exc_info=True)
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            logger.info("Restored from backup")
        await message.answer(f"❌ Ошибка при загрузке: {e}\n\nВосстановлена предыдущая версия")
