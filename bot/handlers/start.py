import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from keyboards import get_main_menu, get_back_keyboard
from scheduler import add_user
from config import CHANNEL_ID, CHANNEL_USERNAME

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


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery, bot: Bot):
    """Обработчик кнопки 'Я подписался'"""
    user_id = callback.from_user.id
    
    if not CHANNEL_ID:
        await callback.answer("Канал не настроен", show_alert=True)
        return
    
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        is_subscribed = member.status in ["member", "administrator", "creator"]
        
        if is_subscribed:
            await callback.message.answer(
                "✅ Спасибо за подписку!\n\nВыберите действие:",
                reply_markup=get_main_menu()
            )
            logger.info(f"User {user_id} subscribed and accessed the bot")
        else:
            channel_link = f"https://t.me/{CHANNEL_USERNAME}" if CHANNEL_USERNAME else "#"
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_link)],
                    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
                ]
            )
            await callback.message.answer(
                "❌ Вы ещё не подписаны. Пожалуйста, подпишитесь на канал",
                reply_markup=keyboard
            )
            logger.info(f"User {user_id} tried to verify subscription but not subscribed")
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id}: {e}")
        await callback.answer("Ошибка проверки подписки. Попробуйте позже", show_alert=True)
    
    await callback.answer()


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
