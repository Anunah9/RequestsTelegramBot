from assets.db import AsyncDataBase

class AsyncDepartmentRepository:
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_department_list(self):
        async with self.db._connection.execute(
            "SELECT * FROM Departments",
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
            return await cursor.fetchone()
        

class Deparment:
    def __init__(self, respository):
        self.repository: AsyncDepartmentRepository = respository
    
    async def connect(self):
        self.repository.connect()

    async def get_department_list(self):
        return await self.repository.get_department_list()

    async def get_department_by_id(self, department_id):
        return await self.repository.get_department_by_id(department_id)

    async def get_department_id(self, department):
        return await self.repository.get_department_id(department)

    async def add_to_departments(self, order_id, department_id):
        return await self.repository.add_to_departments(order_id, department_id)