import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import get_main_menu, get_back_keyboard
from scheduler import add_user

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    add_user(user_id)
    logger.info(f"User {user_id} started the bot")
    await message.answer(
        "Привет! 👋\n\n"
        "Я помогу тебе отслеживать настроение и замечать важные паттерны.\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu(),
    )


@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text(
            "Выберите действие:",
            reply_markup=get_main_menu(),
        )
    except Exception:
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_menu(),
        )
    await callback.answer()


@router.callback_query(F.data == "menu_back_from_mood")
async def menu_back_from_mood(callback: CallbackQuery, state: FSMContext):
    from main import bot
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Выберите действие:",
        reply_markup=get_main_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_back_from_graph")
async def menu_back_from_graph(callback: CallbackQuery, state: FSMContext):
    from main import bot
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Выберите действие:",
        reply_markup=get_main_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text(
            "Выберите действие:",
            reply_markup=get_back_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_back_keyboard(),
        )
    await callback.answer()
