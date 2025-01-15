from typing import Tuple
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keybord(rights: Tuple) -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""
    
    builder = ReplyKeyboardBuilder()
    for btn in rights:
        name = btn[1]
        builder.add(KeyboardButton(text=name))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
