from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from assets.department import Department, AsyncDepartmentRepository


async def choose_departments_kb():
    repository = AsyncDepartmentRepository("./db.db")
    await repository.connect()
    department = Department(respository=repository)
    departments_list = await department.get_department_list()
    builder = ReplyKeyboardBuilder()
    for btn in departments_list:
        builder.add(KeyboardButton(text=btn[1]))
    builder.add(KeyboardButton(text="Завершить"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
