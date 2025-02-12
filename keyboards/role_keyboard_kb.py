from typing import Iterable
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def choose_from_list_keyboard(items: dict):
    builder = ReplyKeyboardBuilder()
    for btn in items:
        builder.add(KeyboardButton(text=btn))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
