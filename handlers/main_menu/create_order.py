from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from assets.order import Order, OrderStates
from assets.department import Department, AsyncDepartmentRepository
from assets.worker import Worker, AsyncWorkerRepository
from keyboards.complete_create_order import complete_create_order
from keyboards.choose_departments import choose_departments_keyboard
from keyboards.choose_workers import choose_workers_keyboard
from middlewares.check_user_right import CheckUserRight
from keyboards.main_menu import main_menu_keyboard

# TODO Добавить отмену создания заявки, через команду, и через кнопку в конце создания
# TODO Добавить отмену любого действия через команду /cancel

router = Router()
router.message.middleware(CheckUserRight("create_order"))


@router.message(F.text == "Создать заявку")
async def create_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции создания заявки\nВведите текст заявки")
    await state.set_state(OrderStates.set_text)


@router.message(OrderStates.set_text)
async def set_order_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        "Принято. Теперь введите пожалуйста целевый отделы",
        reply_markup=await choose_departments_keyboard(),
    )
    await message.answer(
        "Когда закончите вводить отделы отправьте 'Завершить' в чат.",
    )
    await state.set_state(OrderStates.set_departments)
    await state.update_data(departments=[])


@router.message(OrderStates.set_departments)
async def set_order_departments(message: Message, state: FSMContext):

    if message.text == "Завершить":
        await message.answer(
            "Принято. Теперь введите пожалуйста работников",
            reply_markup=await choose_workers_keyboard(),
        )
        await message.answer(
            "Когда закончите вводить работников отправьте 'Завершить' в чат.",
        )
        await state.update_data(workers=[])
        await state.set_state(OrderStates.set_workers)
    else:
        await state.update_data(
            departments=[*await state.get_value("departments"), message.text]
        )


@router.message(OrderStates.set_workers)
async def set_order_workers(message: Message, state: FSMContext):

    if message.text == "Завершить":
        await message.answer("Принято.")
        state_data = await state.get_data()
        text = state_data["text"]
        departments = state_data["departments"]
        workers = state_data["workers"]
        await message.answer(
            f"Текст заявки: {text}\nОтделы: {departments}\nРаботники: {workers}",
            reply_markup=complete_create_order(),
        )
        # Move to callback from btn

    else:
        await state.update_data(
            workers=[*await state.get_value("workers"), message.text]
        )


@router.callback_query(F.data == "complete_creation_order", OrderStates.set_workers)
async def complete_creation_order(callback: CallbackQuery, state: FSMContext):
    order_data = await state.get_data()

    new_order = Order(
        text=order_data["text"],
    )

    await new_order.add_new_order()

    order_id = new_order.order_id

    department_rep = AsyncDepartmentRepository("./db.db")
    department = Department(department_rep)
    await department.add_to_departments(order_id, order_data["departments"])

    worker_rep = AsyncWorkerRepository("./db.db")
    worker = Worker(worker_rep)
    await worker.add_to_workers(order_id, order_data["workers"])

    await state.clear()
    await callback.message.answer(
        text=f"Заявка добавлена\n Её ID - {new_order.order_id}\nЧтобы открыть основное меню используйте /main_menu",
        reply_markup=await main_menu_keyboard(callback.id),
    )
