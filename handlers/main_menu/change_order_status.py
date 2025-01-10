from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from assets.user import UserState
from middlewares.check_user_right import CheckUserRight


router = Router()
router.message.middleware(CheckUserRight("change_order_status"))
## Сделать мидлварь для проверки пользователя


@router.message(F.text == "Изменить статус заявки")
async def create_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции создания заявки")
