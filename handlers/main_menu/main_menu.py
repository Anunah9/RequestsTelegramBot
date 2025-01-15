from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main_menu import main_menu_keybord
from assets.user import User

from assets.user import User, UserState

router = Router()

@router.message(Command("main_menu"))
async def main_menu_handler(message: Message):
    greeting_text = f"Добрый день, {message.chat.username}, этот бот предназначен для работы с заявками."
    await message.answer(
        greeting_text,
    )
    user = User(message.chat.id)
    await user.connect()

    await user.update_user_info_from_db()
    registered_text = f"Добро пожаловать {user.surname} {user.name}"
    await message.answer(
        registered_text, reply_markup=main_menu_keybord(user.rights)
    )