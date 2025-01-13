from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from assets.user import UserState
from assets.order import Order, OrderStates
from keyboards.complete_create_order import complete_create_order
from middlewares.check_user_right import CheckUserRight


router = Router()
router.message.middleware(CheckUserRight("create_order"))
## Сделать мидлварь для проверки пользователя


@router.message(F.text == "Создать заявку")
async def create_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции создания заявки\nВведите текст заявки")
    await state.set_state(OrderStates.set_text)


@router.message(OrderStates.set_text)
async def set_order_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Принято. Теперь введите пожалуйста целевый отделы")
    await state.set_state(OrderStates.set_departments)
    await state.update_data(departments=[])


@router.message(OrderStates.set_departments)
async def set_order_departments(message: Message, state: FSMContext):
    # TODO Поменять порядок if-ов чтобы следовать логике
    if message.text == "Нет":
        await message.answer("Принято. Теперь введите пожалуйста работников")
        await state.update_data(workers=[])
        await state.set_state(OrderStates.set_workers)
    elif message.text == "Да":
        await message.answer("Введите название отдела")
    else:
        await state.update_data(
            departments=[*await state.get_value("departments"), message.text]
        )
        await message.answer(
            "Добавить еще отделы?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
                resize_keyboard=True,
            ),
        )


@router.message(OrderStates.set_workers)
async def set_order_workers(message: Message, state: FSMContext):
    # TODO Сделать функцию для создания клавиатуры из данных полученных с бд
    # TODO Поменять порядок if-ов чтобы следовать логике
    if message.text == "Нет":
        await message.answer("Принято.")
        state_data = await state.get_data()
        text = state_data["text"]
        departments = state_data["departments"]
        workers = state_data["workers"]
        await message.answer(
            f"Текст заявки: {text}\nОтделы: {departments}\nРаботники: {workers}",
            reply_markup=complete_create_order(),
        )
        new_order = Order(text=text, departments=departments, workers=workers)
        await new_order.add_new_order()

    elif message.text == "Да":
        await message.answer("Введите имя сотрудника.")
    else:
        await state.update_data(
            workers=[*await state.get_value("workers"), message.text]
        )
        await message.answer(
            "Добавить еще работников?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
                resize_keyboard=True,
            ),
        )
