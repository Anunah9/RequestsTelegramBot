from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks import FilterTicketsCallback


def filter_view_tickets_kb():
    btns = [
        [
            InlineKeyboardButton(
                text="Созданные",
                callback_data=FilterTicketsCallback(filter="Created").pack(),
            ),
            InlineKeyboardButton(
                text="Принятые",
                callback_data=FilterTicketsCallback(filter="Received").pack(),
            ),
            InlineKeyboardButton(
                text="Закрытые",
                callback_data=FilterTicketsCallback(filter="Closed").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Все", callback_data=FilterTicketsCallback(filter=None).pack()
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=btns)
    return keyboard
