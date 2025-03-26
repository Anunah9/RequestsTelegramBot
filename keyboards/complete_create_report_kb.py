from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def complete_create_report_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Редактировать отчет", callback_data="edit_report")
    )
    builder.add(
        InlineKeyboardButton(
            text="Завершить создание отчета", callback_data="complete_creation_report"
        )
    )

    return builder.as_markup()
