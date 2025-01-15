from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def choose_departments_keyboard(departments):
    builder = ReplyKeyboardBuilder()
    for btn in departments:
        builder.add(KeyboardButton(text=btn))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
