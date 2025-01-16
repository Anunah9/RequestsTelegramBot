from assets.db import AsyncDataBase


class AsyncWorkerRepository:
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_workers_list(self):
        async with self.db._connection.execute(
            "SELECT * FROM Workers",
        ) as cursor:
            return await cursor.fetchall()

    async def get_worker_by_id(self, worker_id):
        async with self.db._connection.execute(
            "SELECT * FROM Workers WHERE id=?", (worker_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_worker_id(self, worker: str):
        """Возвращает id работника по его имени"""
        async with self.db._connection.execute(
            "SELECT id FROM Workers WHERE name=?", (worker,)
        ) as cursor:
            return await cursor.fetchone()

    async def add_to_workers_table(self, order_id, worker_id):
        async with self.db._connection.execute(
            "INSERT INTO OrderWorkers VALUES (?, ?)", (order_id, worker_id)
        ) as cursor:
            return await cursor.fetchone()



class Worker:
    def __init__(self, respository):
        self.repository: AsyncWorkerRepository = respository
    
    async def connect(self):
        self.repository.connect()

    async def get_workers_list(self):
        return await self.repository.get_workers_list()

    async def get_worker_by_id(self, worker_id):
        return await self.repository.get_worker_by_id(worker_id)

    async def get_worker_id(self, worker):
        return await self.repository.get_worker_id(worker)

    async def add_to_workers_table(self, order_id, worker_id):
        return await self.repository.add_to_departments(order_id, worker_id)