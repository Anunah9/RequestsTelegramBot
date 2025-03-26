from typing import Tuple
from aiogram import F, Router
from aiogram.types import Message
from assets.order import Order, AsyncOrderRepository
from aiogram.filters import Command
from assets.order import STATUSES
from middlewares.check_user_right import CheckUserRight

router = Router()
router.message.middleware(CheckUserRight("get_all_orders"))


def build_order_message(order_info: tuple) -> str:
    """Формирует текст сообщения по информации о заявке"""
    order_id, text, status, created_at, *_ = order_info
    # print(STATUSES.get(status, "NaN"))
    return (
        f"ID заявки: {order_id}\n"
        f"Текст заявки: {text}\n"
        f"Статус заявки: {STATUSES.get(int(status), "NaN")}\n"
        f"Создана: {created_at}"
    )


@router.message(Command("orders"))
@router.message(F.text == "Показать все заявки")
async def show_orders(
    message: Message, user_role: str, user_department: Tuple, user_subdivision: int
) -> None:
    await message.answer("Заявки:")

    repo = AsyncOrderRepository("./db.db")
    order_obj = Order(repo)
    if user_subdivision != 1:
        kwargs = {"subdivision": user_subdivision, "allowed_statuses": (1, 2)}
    else:
        kwargs = {}
    orders = await order_obj.get_order_list(deparment=user_department, **kwargs)

    # print("orderrs:", orders)
    for order in orders:
        order_message = build_order_message(order)
        # print(order_message)
        await message.answer(order_message)
    # print(orders)
