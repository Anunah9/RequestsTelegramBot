from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def main_menu_keybord() -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""
    kb = [
        [KeyboardButton(text="Регистрация")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard
