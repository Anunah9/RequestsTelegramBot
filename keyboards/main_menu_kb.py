from typing import Optional, Tuple
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import requests
from services.services import encrypt_telegram_id

from settings import BASE_URL


def get_user_rights(user_id: int) -> Optional[dict]:
    auth_token = encrypt_telegram_id(user_id)
    url = BASE_URL + "/api/v1/auth_service/get_user_rights"
    headers = {"X-Custom-Token": auth_token}
    response = requests.get(url, headers=headers)

    try:
        return response.json()
    except Exception as exc:
        raise exc


async def main_menu_kb(user_id) -> ReplyKeyboardMarkup:
    """Клавиатура основного меню для пользователя"""
    user_rights: list[dict] = get_user_rights(user_id).get("rights")
    # print(user_rights)
    builder = ReplyKeyboardBuilder()
    for btn in user_rights:
        ru = btn.get("ru")
        if ru:
            btn = ru 
        builder.add(KeyboardButton(text=btn))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
