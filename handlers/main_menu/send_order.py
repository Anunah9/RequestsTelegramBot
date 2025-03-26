from aiogram import F, Router
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from typing import Optional, Tuple

# Импорт кастомных модулей и репозиториев
from assets.user import User
from handlers.cancel import main_menu_kb
from keyboards.choose_departments_kb import choose_departments_kb
from keyboards.choose_subdivisions_kb import choose_subdivisions_kb
from middlewares.check_user_right import CheckUserRight
from assets.department import Department, AsyncDepartmentRepository
from assets.subdivision import AsyncSubdivisionRepository, Subdivision
from assets.order import AsyncOrderRepository, Order, OrderStates
from handlers.main_menu import set_departments, set_subdivissions


class OrderService:
    """Сервис для работы с заявками"""

    def __init__(self, state: FSMContext):
        self.state = state
        self.department_repo = AsyncDepartmentRepository("./db.db")
        self.order_repo = AsyncOrderRepository("./db.db")
        self.subdivision_repo = AsyncSubdivisionRepository("./db.db")

    async def get_order_info(self, order_id: int) -> Order:
        order = Order(repository=self.order_repo)
        return await order.get_order_by_id(order_id)

    async def get_latest_order_id(self) -> Optional[int]:
        # TODO: Реализовать получение последнего ID заявки
        # Если заявка отсутствует, вернуть None
        raise Exception("Not implemented yet")
        pass


def build_order_message(order_info: tuple) -> str:
    """Формирует текст сообщения по информации о заявке"""
    order_id, text, status, created_at, _ = order_info
    return (
        f"ID заявки: {order_id}\n"
        f"Текст заявки: {text}\n"
        f"Статус заявки: {status}\n"
        f"Создана: {created_at}"
    )


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
async def handle_select_latest_order(
    callback: CallbackQuery, state: FSMContext, user_role: str, user_department: Tuple
):
    """Обрабатывает выбор последней заявки"""
    order_service = OrderService(state)
    latest_order_id = await order_service.get_latest_order_id()
    if latest_order_id is None:
        await callback.answer("Нет доступных заявок для отправки.")
        return

    await state.update_data(
        selected_order_id=latest_order_id,
        user_role=user_role,
        user_department=user_department,
    )
    await callback.answer("Выбрана последняя заявка.")
    await process_selected_order(callback.message, state)


@router.callback_query(F.data == "enter_order_id")
async def handle_enter_order_id(callback: CallbackQuery, state: FSMContext):
    """Переводит пользователя в режим ввода ID заявки"""
    await callback.message.answer("Введите ID заявки:")
    await state.set_state(OrderStates.waiting_for_order_id)
    await callback.answer()


@router.message(OrderStates.waiting_for_order_id)
async def process_manual_order_id(
    message: Message, state: FSMContext, user_role: str, user_department: Tuple
):
    """Обрабатывает ввод ID заявки пользователем"""
    if not message.text:
        raise Exception(f"Empty message text: {message.text}")
    order_id_str = message.text.strip()
    if not order_id_str.isdigit():
        await message.answer("Некорректный ID. Введите число.")
        return

    order_id = int(order_id_str)
    await state.update_data(
        selected_order_id=order_id,
        user_role=user_role,
        user_department=user_department,
    )
    await process_selected_order(message, state)


@router.callback_query(F.data == "send_order_from_creation_order")
async def handle_send_order_inline(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия кнопки отправки заявки из окна создания заявки"""
    await process_selected_order(callback.message, state)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await callback.answer()


async def process_selected_order(message: Message, state: FSMContext):
    """Обрабатывает заявку после её выбора пользователем"""
    user_data = await state.get_data()
    user_role = user_data.get("user_role")
    user_department = user_data.get("user_department")
    if not user_department:
        raise Exception(f"Empty user department: {user_department}")
    user_department_id, user_department_name = user_department
    order_id = user_data.get("selected_order_id", -1)
    if not (isinstance(order_id, int) or order_id > 0):
        raise Exception("Order id must be natural value")

    order_service = OrderService(state)
    order_info = await order_service.get_order_info(order_id)
    await state.update_data(order=order_info)
    print(order_info)
    # Отправляем информацию о заявке
    await message.answer(build_order_message(order_info))

    confirm_send_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить и отправить", callback_data="confirm_send"
                )
            ]
        ]
    )

    # В зависимости от роли и подразделения запрашиваем дополнительные данные
    if user_role == "Диспетчер" and user_department_name == "Центральное Хозяйство":
        if "departments" not in user_data:
            await message.answer(
                "Введите отделы, если закончили введите Завершить.",
                reply_markup=await choose_departments_kb(),
            )
            await state.set_state(OrderStates.set_departments)
        else:
            await state.update_data(target="departments")
            selected_departments = user_data.get("departments")
            await message.answer(
                f"Выбранные отделы: {selected_departments}",
                reply_markup=confirm_send_kb,
            )
    elif user_role == "Диспетчер":
        if "subdivisions" not in user_data:
            await message.answer(
                "Введите отделы, если закончили введите Завершить.",
                reply_markup=await choose_subdivisions_kb(user_department_id),
            )
            await state.set_state(OrderStates.set_subdivisions)
        else:
            await state.update_data(target="subdivisions")
            selected_subdivisions = user_data.get("subdivisions")
            await message.answer(
                f"Выбранные отделы: {selected_subdivisions}",
                reply_markup=confirm_send_kb,
            )


@router.message(F.text == "Разослать заявку")
async def enter_send_function(message: Message):
    """Вход в функцию отправки заявки"""
    await message.answer("Вы в функции отправки заявки")
    await ask_order_selection(message)


async def notify_department(callback: CallbackQuery, state: FSMContext):
    """Уведомляет диспетчеров отделов о заявке"""
    data = await state.get_data()
    order_info: tuple = data.get("order", ())
    if not order_info:
        raise Exception("Empty order info")
    order_id = order_info[0]
    message_text = build_order_message(order_info)

    department_repo = AsyncDepartmentRepository("./db.db")
    department_obj = Department(department_repo)
    selected_departments = data.get("departments", [])

    # Добавляем заявку в отделы
    await department_obj.add_to_departments(order_id, departments=selected_departments)

    for department in selected_departments:
        dept_id_tuple = await department_obj.get_id_by_name(department)
        if not dept_id_tuple:
            # Здесь можно добавить логирование ошибки
            continue
        department_id = dept_id_tuple[0]
        target = await department_obj.get_department_dispatcher(department_id)
        if target:
            telegram_id, _, _ = target
            await callback.message.bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Подтвердить получение",
                                callback_data=ConfirmRecieptCallbackFactory(
                                    order_id=order_id
                                ).pack(),
                            )
                        ]
                    ]
                ),
            )


async def notify_subdivisions(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Уведомляет работников подразделений о заявке"""
    data = await state.get_data()
    order_info: tuple = data.get("order", ())
    if not order_info:
        raise Exception("Empty order info")
    order_id = order_info[0]
    message_text = build_order_message(order_info)

    subdivision_repo = AsyncSubdivisionRepository("./db.db")
    subdivision_obj = Subdivision(subdivision_repo)
    selected_subdivisions = data.get("subdivisions", [])

    user_department = data.get("user_department")
    if not user_department:
        raise Exception(f"Empty user department: {user_department}")
    user_department_id = user_department[0]

    department_repo = AsyncDepartmentRepository("./db.db")
    department_obj = Department(department_repo)
    # Добавляем заявку в службу определяя по службе диспетчера
    await department_obj.add_to_departments(order_id, departments=(user_department[1],))
    # Добавляем заявку в подразделения
    await subdivision_obj.add_to_subdivisions(
        order_id, subdivisions=selected_subdivisions
    )

    for subdivision in selected_subdivisions:
        subdiv_id_tuple = await subdivision_obj.get_id_by_name(subdivision)
        if not subdiv_id_tuple:
            # Здесь можно добавить логирование ошибки
            continue
        subdivision_id = subdiv_id_tuple[0]
        # Уведомляем для каждой целевой роли
        for target_role in [
            "Начальник сектора",
            "Начальник участка",
            "Ведущий инженер",
        ]:
            target = await subdivision_obj.get_subdivision_worker(
                subdivision_id, user_department_id, target_role
            )
            if target:
                telegram_id, _, _ = target
                await callback.message.bot.send_message(
                    chat_id=telegram_id,
                    text=message_text,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="Подтвердить получение",
                                    callback_data=ConfirmRecieptCallbackFactory(
                                        order_id=order_id
                                    ).pack(),
                                )
                            ]
                        ]
                    ),
                )


@router.callback_query(F.data == "confirm_send")
async def complete_order_sending(callback: CallbackQuery, state: FSMContext):
    """Завершает отправку заявки, уведомляя нужных получателей"""
    data = await state.get_data()
    target = data.get("target")
    if target == "departments":
        await notify_department(callback, state)
    elif target == "subdivisions":
        await notify_subdivisions(callback, state)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await state.clear()

    await callback.message.answer(
        "Заявка успешно отправлена!",
        reply_markup=await main_menu_kb(callback.message.chat.id),
    )
    await callback.answer()


class ConfirmRecieptCallbackFactory(CallbackData, prefix="confirm_receipt"):
    order_id: Optional[int] = None


@router.callback_query(ConfirmRecieptCallbackFactory.filter())
async def confirm_receipt(
    callback: CallbackQuery, callback_data: ConfirmRecieptCallbackFactory
):
    """Изменяет статус заявки после подтверждения получения"""
    order_repo = AsyncOrderRepository("./db.db")
    order = Order(repository=order_repo)
    order_info = await order.get_order_by_id(callback_data.order_id)
    print(order_info)
    user = User(callback.message.chat.id)
    await user.update_user_info_from_db()

    order_message = (
        f"Заявка #{order_info[0]} получена. Получатель {user.name} {user.surname}"
    )

    await order.change_order_status(callback_data.order_id, status=2)
    print(order_info[-1])
    await callback.message.bot.send_message(order_info[-1], order_message)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await callback.answer("Готово")
