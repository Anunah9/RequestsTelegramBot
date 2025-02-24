from assets.db import AsyncDataBase


class AsyncSubdivisionRepository:
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_subdivision_list(self, department_id):
        async with self.db._connection.execute(
            "SELECT * FROM Subdivisions WHERE department_fk=?", (department_id,)
        ) as cursor:
            return await cursor.fetchall()

    async def get_subdivisions_by_order_id(self, order_id):
        async with self.db._connection.execute(
            "SELECT subdivision_fk, name FROM OrderSubdivisions JOIN Subdivisions WHERE order_fk=? AND subdivision_fk=id",
            (order_id,),
        ) as cursor:
            return await cursor.fetchall()

    async def get_subdivision_by_id(self, subdivision_id):
        async with self.db._connection.execute(
            "SELECT * FROM Subdivisions WHERE id=?", (subdivision_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_subdivision_id(self, subdivision):
        async with self.db._connection.execute(
            "SELECT id FROM Subdivisions WHERE name=?", (subdivision,)
        ) as cursor:
            return await cursor.fetchone()

    async def add_to_subdivisions(self, order_id, subdivision_id):
        async with self.db._connection.execute(
            "INSERT INTO OrderSubdivisions VALUES (?, ?)",
            (order_id, subdivision_id),
        ) as cursor:
            return await cursor.fetchone()

    async def get_subdivision_worker(
        self, subdivision: int, department: int, role: str
    ):
        async with self.db._connection.execute(
            "SELECT telegram_id, name, surname FROM Users WHERE subdivision_fk=? AND department_fk=? AND role_fk=?",
            (subdivision, department, role),
        ) as cursor:
            return await cursor.fetchone()


class Subdivision:
    def __init__(self, respository):
        self.repository: AsyncSubdivisionRepository = respository

    async def connect(self):
        self.repository.connect()

    async def get_subdivision_list(self, department_id):
        return await self.repository.get_subdivision_list(department_id)

    async def get_subdivision_by_id(self, subdivision_id):
        return await self.repository.get_subdivision_by_id(subdivision_id)

    async def get_subdivisions_by_order_id(self, order_id):
        return await self.repository.get_subdivisions_by_order_id(order_id)

    async def get_id_by_name(self, subdivision):
        return await self.repository.get_subdivision_id(subdivision)

    async def check_subdivision_name(self, name):
        return bool(await self.repository.get_subdivision_id(name))

    async def _add_to_subdivisions_table(self, order_id, subdivision_id):
        return await self.repository.add_to_subdivisions(order_id, subdivision_id)

    async def add_to_subdivisions(self, order_id, subdivisions):
        subdivision_ids = []
        for subdivision in subdivisions:
            subdivision_ids.append(
                *await self.repository.get_subdivision_id(subdivision)
            )
        #  Добавляем в таблицу OrderWorkers
        for subdivision_id in subdivision_ids:
            await self._add_to_subdivisions_table(order_id, subdivision_id)
        await self.repository.db.commit()
        return 0

    async def get_subdivision_worker(
        self, subdivision: int, department: int, role: str
    ):
        """Возвращает работника подразделения из выбранного отдела."""
        # TODO Добавить выбор должности
        return await self.repository.get_subdivision_worker(
            subdivision, department, role
        )
