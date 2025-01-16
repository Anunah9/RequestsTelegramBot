from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main_menu import main_menu_keybord
from assets.user import User

from assets.user import User

router = Router()


@router.message(Command("main_menu"))
async def main_menu_handler(message: Message):

    await message.answer(reply_markup=await main_menu_keybord())
