from typing import Tuple
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from assets.user import User


async def main_menu_keyboard(user_id) -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""
    print(user_id)
    user = User(user_id)
    await user.connect()
    rights = await user.get_user_rigths()
    builder = ReplyKeyboardBuilder()
    for btn in rights:
        name = btn[1]
        builder.add(KeyboardButton(text=name))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
