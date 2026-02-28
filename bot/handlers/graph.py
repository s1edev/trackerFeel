import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile

from database import SessionLocal
from models import MoodEntry
from graph_service import generate_mood_graph
from keyboards import get_back_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "menu_graph")
async def cmd_graph(callback: CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"User {user_id} requested mood graph")

    db = SessionLocal()
    try:
        entries = (
            db.query(MoodEntry)
            .filter(MoodEntry.user_id == user_id)
            .order_by(MoodEntry.created_at.desc())
            .limit(30)
            .all()
        )

        if not entries:
            logger.info(f"No entries found for user {user_id}")
            try:
                await callback.message.edit_text(
                    "📊 График настроения\n\n"
                    "У тебя пока нет записей.\n\n"
                    "Начни вести дневник — и я покажу визуализацию!",
                    reply_markup=get_back_keyboard(),
                )
            except Exception:
                await callback.message.answer(
                    "📊 График настроения\n\n"
                    "У тебя пока нет записей.\n\n"
                    "Начни вести дневник — и я покажу визуализацию!",
                    reply_markup=get_back_keyboard(),
                )
            await callback.answer()
            return

        entries = list(reversed(entries))
        logger.info(f"Generating graph with {len(entries)} entries for user {user_id}")

        try:
            graph_buffer = generate_mood_graph(entries)
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=BufferedInputFile(graph_buffer.read(), filename="mood_graph.png"),
                caption="📈 Твой график настроения за последние 30 дней",
                reply_markup=get_back_keyboard(),
            )
            logger.info(f"Sent mood graph to user {user_id}")
        except Exception as e:
            logger.error(f"Error generating graph for user {user_id}: {e}")
            try:
                await callback.message.edit_text(
                    "📊 График настроения\n\n"
                    "Произошла ошибка при построении графика. Попробуй позже.",
                    reply_markup=get_back_keyboard(),
                )
            except Exception:
                await callback.message.answer(
                    "📊 График настроения\n\n"
                    "Произошла ошибка при построении графика. Попробуй позже.",
                    reply_markup=get_back_keyboard(),
                )

    finally:
        db.close()
        await callback.answer()
