from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def complete_create_order_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Редактировать заявку", callback_data="edit_order")
    )
    builder.add(
        InlineKeyboardButton(
            text="Завершить создание заявки", callback_data="complete_creation_order"
        )
    )

    return builder.as_markup()
