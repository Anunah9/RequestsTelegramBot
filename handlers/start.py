from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main_menu import main_menu_keybord
from assets.user import User
from handlers import register
from aiogram.fsm.context import FSMContext
from assets.user import User, UserState

router = Router()
router.include_router(register.router)


@router.message(Command("start"))
async def greet_new_user(message: Message, state: FSMContext):
    greeting_text = f"Добрый день, {message.chat.username}, этот бот предназначен для работы с заявками."
    await message.answer(
        greeting_text,
    )
    user = User(message.chat.id)
    if not await user.is_registered():
        register_text = "К сожалению я не могу найти вас в базе пользователей, поэтому пожалуйста перед началом зарегистрируйтесь."
        await message.answer(register_text)
        # Установка состояния на set_name и переход к логике регистрации.
        await message.answer("Для регистрации в боте введите пожалуйста свое имя:")
        await state.set_state(UserState.start_register)

    else:
        await user.update_user_info_from_db()
        registered_text = f"Добро пожаловать {user.surname} {user.name}"
        await message.answer(
            registered_text, reply_markup=main_menu_keybord(user.rights)
        )


