from keyboards.complete_create_order_kb import complete_create_order
from keyboards.choose_departments_kb import choose_departments_keyboard
from middlewares.check_user_right import CheckUserRight
from keyboards.main_menu_kb import main_menu_keyboard
from aiogram.fsm.context import FSMContext
from assets.department import Department, AsyncDepartmentRepository
from aiogram.types import Message, CallbackQuery
from assets.order import AsyncOrderRepository, Order, OrderStates
from aiogram import F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
router.message.middleware(CheckUserRight("send_order"))


async def get_order_info(order_id=-1):
    order_rep = AsyncOrderRepository("./db.db")
    order = Order(repository=order_rep)
    if order_id == -1:
        order_id = await order.get_max_order_id()
    choosen_order = await order.get_order_by_id(order_id)
    department_rep = AsyncDepartmentRepository("./db.db")
    department = Department(department_rep)
    departments = await department.get_departments_by_order_id(order_id)
    return choosen_order, departments


@router.message(F.text == "Разослать заявку")
async def send_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции отправки заявки.")
    order_info, departments = await get_order_info()
    await state.update_data(order=order_info, departments=departments)
    await message.answer(
        f"Последняя добавленная заявка: \n{order_info}\n{departments}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Подтвердить отправку", callback_data="confirm_send"
                    )
                ],
            ]
        ),
    )
    await message.answer("Если хотите сменить заявку просто введите ID.")
    await state.set_state(OrderStates.change_order_for_send)


@router.message(OrderStates.change_order_for_send)
async def change_order_to_send(message: Message, state: FSMContext):
    order_id = message.text
    order_info, departments = await get_order_info(order_id=order_id)
    await state.update_data(order=order_info, departments=departments)
    await message.answer(
        f"Выбранная заявка: \n{order_info}\n{departments}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Подтвердить отправку", callback_data="confirm_send"
                    )
                ],
            ]
        ),
    )
    await message.answer("Если хотите сменить заявку просто введите ID.")
    await state.set_state(OrderStates.change_order_for_send)


@router.callback_query(F.data == "confirm_send")
async def complete_creation_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_info = data["order"]
    departments = data["departments"]

    repository = AsyncDepartmentRepository("./db.db")
    department = Department(repository)

    # Формируем текст сообщения
    message_text = f"Текущая заявка:\n{order_info}"

    for department_id, _ in departments:
        target = await department.get_department_dispatcher(department_id)
        print(target)
        if target:
            try:
                # Распаковываем данные диспетчера
                telegram_id, name, surname = target
                print(telegram_id, name, surname)
                # Отправляем сообщение
                await callback.message.bot.send_message(
                    chat_id=telegram_id, text=message_text
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {telegram_id}: {e}")

    await state.clear()
    await callback.answer("Заявка успешно отправлена!")
