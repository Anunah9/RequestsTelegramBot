import functools
import aiosqlite
from typing import Optional


class AsyncDataBase:
    _instance: Optional["AsyncDataBase"] = None

    @staticmethod
    def is_connected(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self._connection is None:
                await self.connect()
                # raise ConnectionError(
                #     "Database connection is not established. Call `connect()` first."
                # )
            return await func(self, *args, **kwargs)

        return wrapper

    def __new__(cls, db_path: str):
        if cls._instance is None:
            cls._instance = super(AsyncDataBase, cls).__new__(cls)
            cls._instance._db_path = db_path
            cls._instance._connection = None
        return cls._instance

    async def connect(self) -> None:
        if self._connection is None:
            self._connection = await aiosqlite.connect(self._db_path)

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

    @is_connected
    async def get_user_from_db(self, telegram_id: int) -> tuple:
        async with self._connection.execute(
            "SELECT * FROM Users WHERE telegram_id=?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()

    @is_connected
    async def __add_user_to_db(self, user_obj: dict):
        await self._connection.execute(
            "INSERT INTO Users VALUES (?, ?, ?, ?, ?)", [i[1] for i in user_obj.items()]
        )
        await self._connection.commit()

    @is_connected
    async def register_new_user(self, user_obj: dict) -> bool:
        """Функция регистрации нового пользователя"""
        if all([bool(i[1]) for i in user_obj.items()]):
            await self.__add_user_to_db(user_obj)
            return True
        else:
            raise Exception("User data not comlete:", print(user_obj.items()))

    @is_connected
    async def get_roles_dict(self) -> dict:
        """Получение словаря с ролями"""
        async with self._connection.execute("SELECT * FROM Roles") as cursor:
            return [role[0] for role in await cursor.fetchall()]

    @is_connected
    async def get_rights_set(self, role) -> set:
        """Получение словаря с ролями"""
        async with self._connection.execute(
            f"SELECT * FROM Rights WHERE role={role}"
        ) as cursor:
            return set(await cursor.fetchall()[2::])
