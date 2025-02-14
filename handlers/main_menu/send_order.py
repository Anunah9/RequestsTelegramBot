from keyboards.choose_departments_kb import choose_departments_kb
from keyboards.choose_subdivisions_kb import choose_subdivisions_kb
from aiogram.filters.callback_data import CallbackData
from middlewares.check_user_right import CheckUserRight
from keyboards.main_menu_kb import main_menu_kb
from aiogram.fsm.context import FSMContext
from assets.department import Department, AsyncDepartmentRepository
from assets.subdivision import AsyncSubdivisionRepository, Subdivision
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from assets.order import AsyncOrderRepository, Order, OrderStates
from aiogram import F, Router
from typing import Optional
from handlers.main_menu import set_departments
from handlers.main_menu import set_subdivissions


class OrderService:
    def __init__(self, state: FSMContext):
        self.state = state
        self.department_repo = AsyncDepartmentRepository("./db.db")
        self.order_repo = AsyncOrderRepository("./db.db")
        self.subdivision_repo = AsyncSubdivisionRepository("./db.db")

    async def get_order_info(self, order_id):
        order = Order(repository=self.order_repo)
        choosen_order = await order.get_order_by_id(order_id)
        return choosen_order


router = Router()
router.include_routers(set_departments.router, set_subdivissions.router)
router.message.middleware(CheckUserRight("send_order"))


async def ask_order_selection(message: Message):
    """Спрашивает, какую заявку хочет отправить пользователь"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Выбрать последнюю заявку", callback_data="select_latest_order"
                ),
                InlineKeyboardButton(
                    text="Ввести ID вручную", callback_data="enter_order_id"
                ),
            ]
        ]
    )
    await message.answer("Выберите заявку для отправки:", reply_markup=keyboard)


@router.callback_query(F.data == "select_latest_order")
async def select_latest_order(
    callback: CallbackQuery, state: FSMContext, user_role, user_department
):
    """Обрабатывает выбор последней заявки"""
    order_service = OrderService(state)

    callback.answer("В разработке")
    order_id = (
        await order_service.get_order_id_for_send()
    )  # Получаем ID последней заявки
    await state.update_data(
        selected_order_id=order_id, user_role=user_role, user_department=user_department
    )
    await callback.answer("Выбрана последняя заявка.")
    await process_selected_order(callback.message, state, order_id)


@router.callback_query(F.data == "enter_order_id")
async def enter_order_id(callback: CallbackQuery, state: FSMContext):
    """Переводит пользователя в состояние ввода ID заявки"""
    await callback.message.answer("Введите ID заявки:")
    await state.set_state(OrderStates.waiting_for_order_id)
    await callback.answer()


@router.message(OrderStates.waiting_for_order_id)
async def process_manual_order_id(
    message: Message, state: FSMContext, user_role, user_department: tuple
):
    """Обрабатывает введенный ID заявки"""
    order_id = message.text.strip()

    if not order_id.isdigit():
        await message.answer("Некорректный ID. Введите число.")
        return

    order_id = int(order_id)
    await state.update_data(
        selected_order_id=order_id, user_role=user_role, user_department=user_department
    )
    await process_selected_order(message, state)


@router.callback_query(F.data == "send_order_from_creation_order")
async def process_selected_order_inline_btn(callback: CallbackQuery, state: FSMContext):
    await process_selected_order(message=callback.message, state=state)
    await callback.answer()


async def process_selected_order(message: Message, state: FSMContext):
    """Обрабатывает заявку после выбора пользователем"""

    user_data = await state.get_data()
    print("---------------", user_data)
    user_role = user_data.get("user_role")
    user_department_id, user_department = user_data.get("user_department")
    order_id = user_data.get("selected_order_id")

    order_service = OrderService(state)

    order_info = await order_service.get_order_info(order_id)
    await state.update_data(order=order_info)
    await message.answer(str(order_info))  # Отправляем информацию по заявке

    confirm_send_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить и отправить",
                    callback_data="confirm_send",
                )
            ]
        ]
    )

    if user_role == "Диспетчер" and user_department == "Центральное Хозяйство":
        if "departments" not in user_data.keys():
            await message.answer(
                "Введите отделы, если закончили введите Завершить.",
                reply_markup=await choose_departments_kb(),
            )
            await state.set_state(OrderStates.set_departments)
        else:
            await state.update_data(target="departments")
            await message.answer(
                f"Выбранные отделы: {user_data.get("departments")}",
                reply_markup=confirm_send_kb,
            )

            # Рассылка каждому диспетчеру отдела

    elif user_role == "Диспетчер":
        # await message.answer("UNDER CONSTRUCTION")
        if "subdivisions" not in user_data.keys():
            await message.answer(
                "Введите отделы, если закончили введите Завершить.",
                reply_markup=await choose_subdivisions_kb(user_department_id),
            )
            await state.set_state(OrderStates.set_subdivisions)
        else:
            await state.update_data(target="subdivisions")
            await message.answer(
                f"Выбранные отделы: {user_data.get("subdivisions")}",
                reply_markup=confirm_send_kb,
            )


@router.message(F.text == "Разослать заявку")
async def enter_send_function(
    message: Message,
):
    message.answer("Вы в функции отправки заявки")
    await ask_order_selection(message)


###########################################--UNDER CONSTRACTION--###################################################


async def send_to_departments_dispatcher(callback: CallbackQuery, state: FSMContext):
    repository = AsyncDepartmentRepository("./db.db")
    department_obj = Department(repository)

    data = await state.get_data()
    order_info = data["order"]

    message_text = f"Текущая заявка:\n{order_info}"

    for department in data.get("departments"):
        department_id = await department_obj.get_id_by_name(department)
        if department_id:
            department_id = department_id[0]
        else:
            print("пошел нахуй")
        target = await department_obj.get_info_by_id(department_id)
        print(target)
        if target:
            # try:
            # Распаковываем данные диспетчера
            telegram_id, name, surname = target
            print(telegram_id, name, surname)
            print(order_info[0])
            # Отправляем сообщение
            await callback.message.bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Подтвердить получение",
                                callback_data=ConfirmRecieptCallbackFactory(
                                    order_id=order_info[0]
                                ).pack(),
                            )
                        ]
                    ]
                ),
            )


async def send_to_subdivisions_workers(callback: CallbackQuery, state: FSMContext):
    repository = AsyncSubdivisionRepository("./db.db")
    subdivision_obj = Subdivision(repository)
    # Формируем текст сообщения
    data = await state.get_data()
    order_info = data["order"]
    message_text = f"Текущая заявка:\n{order_info}"
    user_department_id, user_deparment_name = data.get("user_department")
    for subdivision_name in data.get("subdivisions"):
        subdivision_id = await subdivision_obj.get_id_by_name(subdivision_name)
        if subdivision_id:
            subdivision_id = subdivision_id[0]
        else:
            print("пошел нахуй")

        target = await subdivision_obj.get_info_by_id(
            subdivision_id, user_department_id
        )
        print(target)
        if target:
            # try:
            # Распаковываем данные диспетчера
            telegram_id, name, surname = target
            print(telegram_id, name, surname)
            print(order_info[0])
            # Отправляем сообщение
            await callback.message.bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Подтвердить получение",
                                callback_data=ConfirmRecieptCallbackFactory(
                                    order_id=order_info[0]
                                ).pack(),
                            )
                        ]
                    ]
                ),
            )


@router.callback_query(F.data == "confirm_send")
async def complete_creation_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("target") == "departments":
        await send_to_departments_dispatcher(callback, state)

    elif data.get("target") == "subdivisions":
        await send_to_subdivisions_workers(callback, state)

    await state.clear()
    await callback.answer("Заявка успешно отправлена!")


class ConfirmRecieptCallbackFactory(CallbackData, prefix="confirm_receipt"):
    order_id: Optional[int] = None


@router.callback_query(ConfirmRecieptCallbackFactory.filter())
async def confirm_receipt(
    callback: CallbackQuery, callback_data: ConfirmRecieptCallbackFactory
):
    repository = AsyncOrderRepository("./db.db")
    order = Order(repository=repository)
    await order.change_order_status(callback_data.order_id, status=2)
    await callback.answer("Готово")
