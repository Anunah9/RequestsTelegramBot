from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.main_menu_kb import main_menu_kb

router = Router()


@router.message(Command("help"))
async def cancel(message: Message):
    """Отправляет информационное сообщение со всеми командами"""
    help_message = (
        "/start - Запускает бота. Отправляет основное меню\n"
        "/main_menu - Отправляет основное меню\n"
        "/cancel - Отменяет любое действие, очищает состояние, возвращает в основное меню\n"
    )
    await message.answer(help_message, reply_markup=await main_menu_kb(message.chat.id))
