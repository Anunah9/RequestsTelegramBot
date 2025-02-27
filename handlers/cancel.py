from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.main_menu_kb import main_menu_kb

router = Router()


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    """Отменяет текущее действие, очищает состояние, снимает состояние, возварщает в очновное меню"""
    await state.clear()
    await message.answer(
        "Действие отменено.", reply_markup=await main_menu_kb(message.chat.id)
    )
