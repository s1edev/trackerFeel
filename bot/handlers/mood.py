import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database import SessionLocal
from models import MoodEntry
from keyboards import get_mood_keyboard, get_back_keyboard
from ai_service import analyze_mood

logger = logging.getLogger(__name__)

router = Router()


class MoodState(StatesGroup):
    waiting_for_mood = State()
    waiting_for_text = State()


MOOD_OPTIONS = [
    "😄 Отличное",
    "🙂 Хорошее",
    "😐 Нормальное",
    "😔 Плохое",
    "😢 Очень плохое",
]


@router.callback_query(F.data == "menu_mood")
async def start_mood_entry(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "Как твоё настроение сейчас?\n\nВыберите вариант:",
        )
    except Exception:
        await callback.message.answer(
            "Как твоё настроение сейчас?\n\nВыберите вариант:",
        )
    await callback.message.answer(
        "Выберите настроение:",
        reply_markup=get_mood_keyboard(),
    )
    await callback.answer()


@router.message(F.text.in_(MOOD_OPTIONS))
async def process_mood(message: Message, state: FSMContext):
    mood = message.text
    user_id = message.from_user.id
    logger.info(f"User {user_id} selected mood: {mood}")

    await state.update_data(mood=mood)
    await state.set_state(MoodState.waiting_for_text)

    await message.answer(
        "Расскажи, как прошёл твой день?\n\nПиши кратко — главное, честно.",
        reply_markup=get_back_keyboard(),
    )


@router.message(MoodState.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    text = message.text.strip()
    user_id = message.from_user.id

    if not text or len(text) < 3:
        await message.answer(
            "Напиши хоть пару слов о своём дне.\n\nЭто важно для анализа.",
            reply_markup=get_back_keyboard(),
        )
        return

    logger.info(f"User {user_id} submitted day description: {text[:50]}...")

    data = await state.get_data()
    mood = data.get("mood")

    if not mood:
        logger.error(f"User {user_id} has no mood in state")
        await message.answer("Произошла ошибка. Начни заново.")
        await state.clear()
        return

    db = SessionLocal()
    try:
        entry = MoodEntry(
            user_id=user_id,
            mood=mood,
            text=text,
            created_at=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        logger.info(f"Saved mood entry {entry.id} for user {user_id}")

        recent_entries = (
            db.query(MoodEntry)
            .filter(MoodEntry.user_id == user_id)
            .order_by(MoodEntry.created_at.desc())
            .limit(7)
            .all()
        )
        recent_entries = [e for e in recent_entries if e.id != entry.id][:7]

        await message.answer("Сохраняю запись и анализирую настроение...")
        analysis = await analyze_mood(mood, text, recent_entries)

        # Удаляем сообщение с текстом дня
        try:
            await message.delete()
        except Exception:
            pass

        if analysis:
            logger.info(f"Generated analysis for user {user_id}")
            await message.answer(
                f"✨ Готово!\n\n"
                f"📈 {analysis['trend']}\n\n"
                f"💭 {analysis['quote']}\n\n"
                "Запись сохранена в дневнике настроения.",
                reply_markup=get_back_keyboard(),
            )
        else:
            await message.answer(
                "✅ Запись сохранена!\n\nАнализ временно недоступен.",
                reply_markup=get_back_keyboard(),
            )

    finally:
        db.close()
        await state.clear()
