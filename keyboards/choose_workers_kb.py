from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from assets.worker import Worker, AsyncWorkerRepository


async def choose_workers_keyboard():
    repository = AsyncWorkerRepository("./db.db")
    await repository.connect()
    workers = Worker(respository=repository)
    workers_list = await workers.get_workers_list()
    print(workers_list)
    builder = ReplyKeyboardBuilder()
    for btn in workers_list:
        builder.add(KeyboardButton(text=" ".join(btn)))
    builder.add(KeyboardButton(text="Завершить"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
