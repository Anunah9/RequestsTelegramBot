from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def edit_order_keyboard():
    builder = InlineKeyboardBuilder()
    editable = [
        ("Текст заявки", "edit_text"),
        # ("Отделы", "edit_departments"),
        # ("Работники", "edit_workers"),
    ]
    for btn in editable:
        builder.add(InlineKeyboardButton(text=btn[0], callback_data=btn[1]))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
