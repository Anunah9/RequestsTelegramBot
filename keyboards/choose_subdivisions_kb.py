from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def choose_subdivisions_kb(department_id: int):

    subdivision_list = ["f", "a", "as"]
    builder = ReplyKeyboardBuilder()
    for btn in subdivision_list:
        builder.add(KeyboardButton(text=btn[1]))
    builder.add(KeyboardButton(text="Завершить"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
