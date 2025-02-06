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

    # Edit states
    get_order_id = State()
    set_edited_order_text = State()
    change_order_for_send = State()


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

    async def edit_order_text(self, order_id, text):
        async with self.db._connection.execute(
            "UPDATE Orders SET text=? WHERE id=?",
            (text, order_id),
        ) as cursor:
            await self.db._connection.commit()
            return await cursor.fetchone()

    async def change_order_status(self, order_id, status):
        async with self.db._connection.execute(
            "UPDATE Orders SET status=? WHERE id=?",
            (status, order_id),
        ) as cursor:
            await self.db._connection.commit()
            return await cursor.fetchone()


class Order:
    def __init__(self, text=None, repository=None):
        self.order_id: int
        self.text: str = text
        self.status: str = 1
        self.repository = repository or AsyncOrderRepository("./db.db")

    def set_order_text(self, text):
        self.text = text

    async def edit_text_order(self, order_id, text):
        return await self.repository.edit_order_text(order_id, text)

    async def change_order_status(self, order_id, status):
        return await self.repository.change_order_status(order_id, status)

    async def get_order_list(self):
        return await self.repository.get_order_list_from_db()

    async def get_max_order_id(self):
        return (await self.repository.get_max_order_id())[0]

    async def get_last_order(self):
        return await self.repository.get_order_by_id(await self.get_max_order_id())

    async def get_order_by_id(self, order_id):
        return await self.repository.get_order_by_id(order_id=order_id)

    async def add_new_order(self):
        max_order_id = await self.repository.get_max_order_id()
        print(max_order_id)
        if not max_order_id:
            self.order_id = 1
        else:
            self.order_id = max_order_id[0] + 1
        current_status = 1
        created_at = datetime.datetime.now()

        await self.repository.add_to_orders_table(
            self.order_id, self.text, current_status, created_at
        )
