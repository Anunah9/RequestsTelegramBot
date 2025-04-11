from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main_menu_kb import main_menu_kb

router = Router()


@router.message(Command("main_menu"))
async def main_menu_handler(message: Message) -> None:
    await message.answer(
        text="Выберите действие.",
        reply_markup=await main_menu_kb(message.chat.id),
    )
