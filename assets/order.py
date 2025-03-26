from asyncio import Condition
from collections.abc import Iterable
import datetime
import random
from sqlite3 import Row
from typing import Dict, Optional
from aiogram.fsm.state import StatesGroup, State
import aiosqlite
from assets.db import AsyncDataBase

STATUSES = {
    1: "Создана",
    2: "Принята",
    3: "Закрыта",
}
# TODO Сделать обработку ошибок в получении id из бд
# TODO Сделать lower() при получении id из бд


class OrderStates(StatesGroup):
    # Состояния для работы с заявками
    set_text = State()
    end_creation_order = State()
    set_departments = State()
    set_status = State()
    set_workers = State()

    # Edit states
    get_order_id = State()
    set_edited_order_text = State()
    change_order_for_send = State()
    set_subdivisions = State()

    waiting_for_order_id = State()


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

    async def get_order_list_from_db(
        self,
        allowed_statuses: Optional[tuple] = None,
        department: Optional[int] = None,
        subdivision: Optional[int] = None,
    ) -> Iterable[Row]:

        joins = f"JOIN {"OrderDepartments od" if department else ""} {"," if department and subdivision else ""}  {"OrderSubdivisions os" if subdivision else ""}"
        subdivision_filter = (
            f"os.order_fk=Orders.id AND os.subdivision_fk={subdivision}"
        )
        status_filter = f"status IN {allowed_statuses}"
        department_filter = (
            f"od.order_fk=Orders.id AND od.department_fk={department[0]} "
        )
        query = f"SELECT * FROM Orders {joins if subdivision or department else ""} WHERE {status_filter if allowed_statuses else ""} {"AND" if (subdivision or department) and allowed_statuses else ""} {department_filter if department else ""} {"AND" if subdivision and department else ""} {subdivision_filter if subdivision else ""}"
        print(query)
        async with self.db._connection.execute(query) as cursor:
            return await cursor.fetchall()

    async def get_max_order_id(self):
        async with self.db._connection.execute("SELECT MAX(id) FROM Orders") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

    async def add_to_orders_table(self, order_id, text, status, created_at, created_by):
        async with self.db._connection.execute(
            "INSERT INTO Orders VALUES (?, ?, ?, ?, ?)",
            (order_id, text, status, created_at, created_by),
        ) as cursor:
            await self.db._connection.commit()
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


# TODO Заменить статус на текстовое определение
# TODO Добавить инлайн кнопку ответа на заявку


class Order:
    def __init__(self, telegram_id=None, text=None, repository=None):
        self.created_by: int = telegram_id
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

    async def get_order_list(
        self,
        allowed_statuses: Optional[int] = None,
        deparment: Optional[int] = None,
        subdivision: Optional[int] = None,
    ):
        """Возвращает список всех заявок с заданным статусом и по заданному отделу.
        По умолчанию возвращает все заявки"""
        return await self.repository.get_order_list_from_db(
            allowed_statuses, deparment, subdivision
        )

    async def get_max_order_id(self):
        return await self.repository.get_max_order_id()

    async def get_order_by_id(self, order_id):
        return await self.repository.get_order_by_id(order_id=order_id)

    async def add_new_order(self):
        max_order_id = await self.repository.get_max_order_id()
        print(max_order_id)
        if not max_order_id:
            self.order_id = 1
        else:
            self.order_id = max_order_id + 1
        current_status = 1
        created_at = datetime.datetime.now()

        await self.repository.add_to_orders_table(
            self.order_id, self.text, current_status, created_at, self.created_by
        )
