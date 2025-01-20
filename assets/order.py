import datetime
import random
from typing import List, Optional, Tuple, Union
from aiogram.fsm.state import StatesGroup, State
from assets.db import AsyncDataBase

STATUSES = {1: "Создана", 2: "Отправлена", 3: "Принята", 4: "В работе", 5: "Закрыта"}
# TODO Сделать обработку ошибок в получении id из бд
# TODO Сделать lower() при получении id из бд
# TODO Переделать это под инлайн кнопки и switch inline query


class OrderStates(StatesGroup):
    # Состояния для работы с заявками
    set_text = State()
    set_departments = State()
    set_status = State()
    set_workers = State()


class AsyncOrderRepository:
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_order_list(self):
        async with self.db._connection.execute(
            "SELECT * FROM Orders",
        ) as cursor:
            return await cursor.fetchall()

    async def get_order_by_id(self, order_id):
        async with self.db._connection.execute(
            "SELECT * FROM Orders WHERE id=?", (order_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_max_order_id(self):
        async with self.db._connection.execute("SELECT MAX(id) FROM Orders") as cursor:
            return await cursor.fetchone()

    async def add_to_orders_table(self, order_id, text, status, created_at):
        async with self.db._connection.execute(
            "INSERT INTO Orders VALUES (?, ?, ?, ?)",
            (order_id, text, status, created_at),
        ) as cursor:
            return await cursor.fetchone()


class Order:
    def __init__(self, text, repository=None):
        self.order_id: int
        self.text: str = text
        self.status: str = 1
        self.repository = repository or AsyncOrderRepository("./db.db")

    async def get_order_id(self):
        self.order_id = await self.repository.get_max_order_id() + 1

    async def get_order_list(self) -> Optional[Tuple[int, str, str, str]]:
        return await self.repository.get_order_list_from_db()

    async def get_order_by_id(self, order_id):
        return await self.repository.get_order_by_id(order_id=order_id)

    async def add_new_order(self):
        (max_order_id,) = await self.repository.get_max_order_id()
        self.order_id = max_order_id + 1
        current_status = 1
        created_at = datetime.datetime.now()

        await self.repository.add_to_orders_table(
            self.order_id, self.text, current_status, created_at
        )

        
