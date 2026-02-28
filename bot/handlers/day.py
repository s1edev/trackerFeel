import logging
import re
from datetime import datetime, timezone, timedelta

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database import SessionLocal
from models import MoodEntry
from config import TIMEZONE
from keyboards import get_back_keyboard

logger = logging.getLogger(__name__)

router = Router()

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Таймзона Тюмени (UTC+5)
USER_TZ = timezone(timedelta(hours=5))


class DateState(StatesGroup):
    waiting_for_date = State()


@router.callback_query(F.data == "menu_date")
async def start_date_lookup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DateState.waiting_for_date)
    try:
        await callback.message.edit_text(
            "📅 Поиск по дате\n\n"
            "Введите дату в формате ГГГГ-ММ-ДД\n"
            "Пример: 2026-02-20",
            reply_markup=get_back_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            "📅 Поиск по дате\n\n"
            "Введите дату в формате ГГГГ-ММ-ДД\n"
            "Пример: 2026-02-20",
            reply_markup=get_back_keyboard(),
        )
    await callback.answer()


@router.message(DateState.waiting_for_date)
async def process_date_from_state(message: Message, state: FSMContext):
    date_str = message.text.strip()
    await handle_date_lookup(message, date_str)
    await state.clear()


@router.message(F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def process_date_auto(message: Message):
    """Автоматическая обработка даты в любом сообщении"""
    date_str = message.text.strip()
    await handle_date_lookup(message, date_str)


async def handle_date_lookup(message: Message, date_str: str):
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested day lookup: {date_str}")

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logger.warning(f"User {user_id} provided invalid date: {date_str}")
        await message.answer(
            "❌ Некорректная дата.\n\n"
            "Проверьте, что дата существует.",
            reply_markup=get_back_keyboard(),
        )
        return

    db = SessionLocal()
    try:
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        entries = (
            db.query(MoodEntry)
            .filter(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_of_day,
                MoodEntry.created_at <= end_of_day,
            )
            .order_by(MoodEntry.created_at.desc())
            .all()
        )

        if entries:
            logger.info(f"Found {len(entries)} entries for user {user_id} on {date_str}")
            
            # Конвертируем время в локальное (Тюмень, UTC+5)
            entries_text = []
            for i, entry in enumerate(entries, 1):
                local_time = entry.created_at.replace(tzinfo=timezone.utc).astimezone(USER_TZ)
                entries_text.append(
                    f"{'─' * 20}\n"
                    f"📝 Запись #{i}\n\n"
                    f"😊 Настроение: {entry.mood}\n\n"
                    f"📝 Описание:\n{entry.text}\n\n"
                    f"⏰ Время: {local_time.strftime('%H:%M')}"
                )
            
            await message.answer(
                f"📅 Записи за {date_str}\n\n" + "\n\n".join(entries_text),
                reply_markup=get_back_keyboard(),
            )
        else:
            logger.info(f"No entries found for user {user_id} on {date_str}")
            await message.answer(
                f"📅 Запись за {date_str}\n\n"
                "За эту дату записей нет.",
                reply_markup=get_back_keyboard(),
            )

    finally:
        db.close()
