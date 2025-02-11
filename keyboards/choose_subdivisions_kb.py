from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from assets.subdivision import Subdivision, AsyncSubdivisionRepository


async def choose_subdivisions_kb():
    repository = AsyncSubdivisionRepository("./db.db")
    await repository.connect()
    subdivision = Subdivision(respository=repository)
    subdivision_list = await subdivision.get_subdivision_list()
    builder = ReplyKeyboardBuilder()
    for btn in subdivision_list:
        builder.add(KeyboardButton(text=btn[1]))
    builder.add(KeyboardButton(text="Завершить"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
