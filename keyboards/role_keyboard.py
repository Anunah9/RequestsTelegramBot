from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from assets.db import AsyncDataBase


async def choose_role_keyboard():
    db = AsyncDataBase("./db.db")
    roles = await db.get_roles_dict()
    print(roles)
    builder = ReplyKeyboardBuilder()
    for _, btn in roles.items():

        builder.add(KeyboardButton(text=btn))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
