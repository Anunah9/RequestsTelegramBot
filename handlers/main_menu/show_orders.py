from aiogram import F, Router
from aiogram.types import Message
from assets.order import Order, AsyncOrderRepository
from aiogram.filters import Command

router = Router()


@router.message(Command("orders"))
async def show_orders(message: Message):
    await message.answer("Заявки:")
    repo = AsyncOrderRepository("./db.db")
    order_obj = Order(repo)
    orders = await order_obj.get_order_list()
    print(orders)
