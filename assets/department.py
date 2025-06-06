from typing import Tuple
from assets.db import AsyncDataBase

# TODO Наследовать классы worker, department, subdivision от одного абстрактного класса


class AsyncDepartmentRepository:
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_department_list(self) -> dict:
        async with self.db._connection.execute(
            "SELECT * FROM Departments",
        ) as cursor:
            return await cursor.fetchall()

    async def get_departments_by_order_id(self, order_id):
        async with self.db._connection.execute(
            "SELECT department_fk, name FROM OrderDepartments JOIN Departments WHERE order_fk=? AND department_fk=id",
            (order_id,),
        ) as cursor:
            return await cursor.fetchall()

    async def get_department_by_id(self, department_id):
        async with self.db._connection.execute(
            "SELECT * FROM Departments WHERE id=?", (department_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_department_id(self, department):
        async with self.db._connection.execute(
            "SELECT id FROM Departments WHERE name=?", (department,)
        ) as cursor:
            return await cursor.fetchone()

    async def add_to_departments(self, order_id, department_id):
        async with self.db._connection.execute(
            "INSERT INTO OrderDepartments VALUES (?, ?)",
            (order_id, department_id),
        ) as cursor:
            print(f"INSERT INTO OrderDepartments VALUES ({order_id}, {department_id})")
            return await cursor.fetchone()

    async def get_department_dispatcher(self, department_id: int):
        async with self.db._connection.execute(
            'SELECT telegram_id, name, surname FROM Users WHERE department_fk=? AND role_fk="Диспетчер"',
            (department_id,),
        ) as cursor:
            return await cursor.fetchone()


class Department:
    def __init__(self, respository):
        self.repository: AsyncDepartmentRepository = respository

    async def connect(self):
        self.repository.connect()

    async def get_department_list(self) -> dict:
        return await self.repository.get_department_list()

    async def get_department_by_id(self, department_id):
        return await self.repository.get_department_by_id(department_id)

    async def get_departments_by_order_id(self, order_id):
        return await self.repository.get_departments_by_order_id(order_id)

    async def get_id_by_name(self, department):
        return await self.repository.get_department_id(department)

    async def check_department_name(self, name):
        return bool(await self.repository.get_department_id(name))

    async def _add_to_departments_table(self, order_id, department_id):
        return await self.repository.add_to_departments(order_id, department_id)

    async def add_to_departments(self, order_id, departments: Tuple):
        department_ids = []
        for department in departments:
            department_ids.append(*await self.repository.get_department_id(department))
        #  Добавляем в таблицу OrderWorkers
        for department_id in department_ids:
            await self._add_to_departments_table(order_id, department_id)
        await self.repository.db.commit()
        return 0

    async def get_department_dispatcher(self, department_id: int):
        return await self.repository.get_department_dispatcher(department_id)
