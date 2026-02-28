from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📊 График", callback_data="menu_graph", style="primary"),
            InlineKeyboardButton(text="📅 По дате", callback_data="menu_date", style="primary"),
        ],
        [
            InlineKeyboardButton(text="✍️ Записать день", callback_data="menu_mood", style="success"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_mood_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="😄 Отличное")],
        [KeyboardButton(text="🙂 Хорошее")],
        [KeyboardButton(text="😐 Нормальное")],
        [KeyboardButton(text="😔 Плохое")],
        [KeyboardButton(text="😢 Очень плохое")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def get_back_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="⬅ Назад", callback_data="menu_back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)