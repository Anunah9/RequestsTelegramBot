from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def choose_subdivisions_kb(subdivisions_list: list[dict]) -> ReplyKeyboardMarkup:

    builder = ReplyKeyboardBuilder()
    for btn in subdivisions_list:
        builder.add(KeyboardButton(text=btn.get("name")))
    builder.add(KeyboardButton(text="Завершить"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
