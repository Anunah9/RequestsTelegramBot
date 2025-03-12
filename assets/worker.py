from assets.db import AsyncDataBase


class AsyncWorkerRepository:
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_workers_list(self):
        async with self.db._connection.execute(
            "SELECT name, surname FROM Users WHERE role_fk=?", ("Рабочий",)
        ) as cursor:
            return await cursor.fetchall()

    async def get_worker_by_id(self, worker_id):
        async with self.db._connection.execute(
            "SELECT * FROM Users WHERE id=?", (worker_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_worker_id(self, worker: str):
        """Возвращает id работника по его имени"""
        async with self.db._connection.execute(
            "SELECT telegram_id FROM Users WHERE name=? AND surname=?",
            worker.split(" "),
        ) as cursor:
            return await cursor.fetchone()

    async def add_to_workers_table(self, order_id, worker_id):
        async with self.db._connection.execute(
            "INSERT INTO OrderWorkers VALUES (?, ?)", (order_id, worker_id)
        ) as cursor:
            return await cursor.fetchone()

    # Не доделано
    # async def get_workers_by_order_id(order_id):
    #     async with self.db._connection.execute(
    #         "SELECT name, surname FROM Users WHERE name=? AND surname=?",
    #         worker.split(" "),
    #     ) as cursor:
    #         return await cursor.fetchone()

    async def edit_workers_by_order_id(self, order_id, workers):
        pass


class Worker:
    def __init__(self, respository):
        self.repository: AsyncWorkerRepository = respository

    async def connect(self):
        await self.repository.connect()

    async def get_workers_list(self):
        return await self.repository.get_workers_list()

    async def get_worker_by_id(self, worker_id):
        return await self.repository.get_worker_by_id(worker_id)

    async def get_worker_id(self, worker):
        return await self.repository.get_worker_id(worker)

    async def get_workers_by_order_id(self, order_id):
        return await self.repository.get_workers_by_order_id(order_id)

    async def _add_to_workers_table(self, order_id, worker_id):
        return await self.repository.add_to_workers_table(order_id, worker_id)

    async def add_to_workers(self, order_id, workers):
        #  Получаем id каждого работника заявки
        worker_ids = []
        for worker in workers:
            worker_ids.append(*await self.repository.get_worker_id(worker))
        #  Добавляем в таблицу OrderWorkers
        for worker_id in worker_ids:
            await self._add_to_workers_table(order_id, worker_id)
        await self.repository.db.commit()
        #  Получаем id отделов
