from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def start_keybord() -> ReplyKeyboardMarkup:
    """Клавиатура команды /start"""
    kb = [
        [KeyboardButton(text="Регистрация")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard
