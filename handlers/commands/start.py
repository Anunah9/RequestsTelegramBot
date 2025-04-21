from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from services.logger import logger
from keyboards.main_menu_kb import main_menu_kb
from services.selectors import get_user_detailed

from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def greet_new_user(message: Message, state: FSMContext):
    user: dict = get_user_detailed(message.chat.id)
    print(user) 

    if user:
        logger.info(str(message.chat.id) + " " + message.text)
        greeting_text = f"Добрый день, {user.get("first_name")} {user.get("last_name")}, этот бот предназначен для работы с заявками."
        await message.answer(
            greeting_text, reply_markup=await main_menu_kb(message.chat.id)
        )
    else:
        register_text = "К сожалению я не могу найти вас в базе пользователей, поэтому пожалуйста перед началом зарегистрируйтесь."
        await message.answer(register_text)
        # Установка состояния на set_name и переход к логике регистрации.
        await message.answer(f"Для регистрации в боте обратитесь в поддержку. Ваш telegram id: {message.chat.id}")
