from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from services.services import encrypt_telegram_id
import requests
import settings


async def choose_department_kb(departments_list) -> ReplyKeyboardMarkup:

    builder = ReplyKeyboardBuilder()
    for btn in departments_list:
        builder.add(KeyboardButton(text=btn))
    # builder.add(KeyboardButton(text="Завершить"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
