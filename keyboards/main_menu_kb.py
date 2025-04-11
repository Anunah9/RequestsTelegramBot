from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from services.selectors import get_user_rights


async def main_menu_kb(user_id) -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""
    user_rights: list[dict] = get_user_rights(user_id).get("rights")
    builder = ReplyKeyboardBuilder()
    for btn in user_rights:
        ru = btn.get("ru")
        if ru:
            btn = ru
        builder.add(KeyboardButton(text=btn))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
