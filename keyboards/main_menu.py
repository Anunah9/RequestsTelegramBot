from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from assets.rights import RIGHTS_ASSERTIONS


def main_menu_keybord(rights: set) -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""

    builder = ReplyKeyboardBuilder()
    print(rights)
    for btn in rights["rights"]:
        builder.add(KeyboardButton(text=RIGHTS_ASSERTIONS[btn]))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
