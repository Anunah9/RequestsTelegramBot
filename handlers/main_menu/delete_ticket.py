from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.user import UserState
# from middlewares.check_user_right import CheckUserRight


router = Router()

@router.message(F.text == "Удалить заявку")
async def delete_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции удаления заявки")
