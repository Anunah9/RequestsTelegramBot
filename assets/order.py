import datetime
import random
from typing import List, Optional, Tuple, Union
from aiogram.fsm.state import StatesGroup, State
from assets.db import AsyncDataBase

STATUSES = {1: "Создана", 2: "Отправлена", 3: "Принята", 4: "В работе", 5: "Закрыта"}


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

    async def get_worker_id(self, worker: tuple):
        """Возвращает id работника по его имени"""
        async with self.db._connection.execute(
            "SELECT id FROM Workers WHERE name=?", (worker,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_department_id(self, department):
        async with self.db._connection.execute(
            "SELECT id FROM Departments WHERE name=?", (department,)
        ) as cursor:
            return await cursor.fetchone()

    async def add_to_workers_table(self, order_id, worker_id):
        async with self.db._connection.execute(
            "INSERT INTO OrderWorkers VALUES (?, ?)", (order_id, worker_id)
        ) as cursor:
            return await cursor.fetchone()

    async def add_to_departments(self, order_id, department_id):
        async with self.db._connection.execute(
            "INSERT INTO OrderDepartments VALUES (?, ?)", (order_id, department_id)
        ) as cursor:
            return await cursor.fetchone()


class Order:
    def __init__(self, text, departments, workers, repository=None):
        self.order_id: int
        self.text: str = text
        self.departments: Union[str, list] = departments
        self.status: str = 1
        self.workers: Union[List] = workers
        self.repository = repository or AsyncOrderRepository("./db.db")

    async def update_order_id(self):
        self.order_id = await self.repository.get_max_order_id() + 1

    async def get_order_list(self) -> Optional[Tuple[int, str, str, str]]:
        return await self.repository.get_order_list_from_db()

    async def get_order_by_id(self, order_id):
        return await self.repository.get_order_by_id(order_id=order_id)

    ## TODO Отправлять клавиатуру с отделами и работниками чтобы заранее определять id отделов и работников. Чтобы не приходилось определять id через запросы к бд

    async def add_new_order(self):
        (max_order_id,) = await self.repository.get_max_order_id()
        order_id = max_order_id + 1
        current_status = 1
        created_at = datetime.datetime.now()

        await self.repository.add_to_orders_table(
            order_id, self.text, current_status, created_at
        )

        #  Получаем id каждого работника заявки
        worker_ids = []
        for worker in self.workers:
            worker_ids.append(*await self.repository.get_worker_id(worker))
        #  Добавляем в таблицу OrderWorkers
        for worker_id in worker_ids:
            await self.repository.add_to_workers_table(order_id, worker_id)

        #  Получаем id отделов
        department_ids = []
        for department in self.departments:
            department_ids.append(*await self.repository.get_department_id(department))
        #  Добавляем в таблицу OrderWorkers
        for department_id in department_ids:
            await self.repository.add_to_departments(order_id, department_id)
        await self.repository.db.commit()
        return 0
        # return await self.repository.add_new_order()
