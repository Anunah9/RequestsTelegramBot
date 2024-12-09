from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.start_keyboard import start_keybord
from assets.user import User

router = Router()


@router.message(Command("start"))
async def greet_new_user(message: Message):
    greeting_text = f"Добрый день, {message.chat.username}, этот бот предназначен для работы с заявками."
    await message.answer(
        greeting_text,
    )
    user = User(message.chat.id)
    if not await user.is_registered():
        register_text = "К сожалению я не могу найти вас в базе пользователей, поэтому пожалуйста перед началом зарегистрируйтесь."
        await message.answer(register_text, reply_markup=start_keybord())
    else:
        registered_text = f"Добро пожаловать {user.surname} {user.name}"
        await message.answer(register_text, reply_markup=start_keybord())