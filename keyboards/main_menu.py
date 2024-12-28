from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keybord(rights: set) -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""

    builder = ReplyKeyboardBuilder()
    print(rights)
    for btn in rights["rights"]:
        builder.add(KeyboardButton(btn))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
