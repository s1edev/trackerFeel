import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.types import ErrorEvent

from config import CHANNEL_ID, CHANNEL_USERNAME

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """Middleware для проверки подписки пользователя на канал"""

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Пропускаем проверку если CHANNEL_ID не настроен
        if not CHANNEL_ID:
            return await handler(event, data)

        # Получаем user_id из события
        if isinstance(event, Message):
            user_id = event.from_user.id
            bot = event.bot
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            bot = event.bot
        elif isinstance(event, ErrorEvent):
            # Для ошибок пытаемся получить user_id из события
            if isinstance(event.event, (Message, CallbackQuery)):
                user_id = event.event.from_user.id
                bot = event.bot
            else:
                return await handler(event, data)
        else:
            return await handler(event, data)

        # Проверяем подписку
        try:
            logger.debug(f"Checking subscription for user {user_id} in channel {CHANNEL_ID}")
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            logger.debug(f"User {user_id} status: {member.status}")
            is_subscribed = member.status in ["member", "administrator", "creator"]
            
            if not is_subscribed:
                # Пользователь не подписан - показываем сообщение с кнопкой подписки
                channel_link = self._get_channel_link()
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_link)],
                        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
                    ]
                )
                
                if isinstance(event, Message):
                    await event.answer(
                        "❌ Для использования бота необходимо подписаться на канал",
                        reply_markup=keyboard
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "❌ Для использования бота необходимо подписаться на канал",
                        show_alert=True
                    )
                    logger.info(f"User {user_id} tried to use bot but not subscribed")
                return None
            
        except Exception as e:
            logger.error(f"Error checking subscription for user {user_id}: {e}")
            # При ошибке пропускаем пользователя

        return await handler(event, data)
    
    def _get_channel_link(self) -> str:
        """Генерирует ссылку на канал из CHANNEL_USERNAME"""
        if CHANNEL_USERNAME:
            return f"https://t.me/{CHANNEL_USERNAME}"
        elif CHANNEL_ID:
            # Если username нет, пробуем сгенерировать из ID
            if CHANNEL_ID.startswith('@'):
                return f"https://t.me/{CHANNEL_ID.replace('@', '')}"
            else:
                # Для числовых ID ссылка может не работать без username
                return "#"
        return "#"
