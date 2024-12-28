import functools
import aiosqlite
from typing import List, Optional, Tuple


class AsyncDataBase:
    _instance: Optional["AsyncDataBase"] = None

    @staticmethod
    def is_connected(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self._connection is None:
                await self.connect()
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
    async def __add_user_to_db(self, user_obj: Tuple):
        await self._connection.execute(
            "INSERT INTO Users VALUES (?, ?, ?, ?, ?)", user_obj
        )
        await self._connection.commit()

    @is_connected
    async def register_new_user(self, user_obj: Tuple) -> bool:
        """Функция регистрации нового пользователя"""
        if all([bool(i) for i in user_obj]):
            await self.__add_user_to_db(user_obj)
            return True
        else:
            raise Exception("User data not comlete:", print(user_obj.items()))

    @is_connected
    async def get_roles(self) -> List:
        """Получение словаря с ролями"""
        async with self._connection.execute("SELECT * FROM Roles") as cursor:
            return [role[0] for role in await cursor.fetchall()]

    @is_connected
    async def get_rights_set(self, role) -> Tuple:
        """Получение словаря с правами роли"""

        async with self._connection.execute(
            'SELECT rr.permission_name, definition FROM RoleRights rr JOIN (RightsDefinitions) WHERE rr.permission_name=name AND role_name=?',
            (role,),
        ) as cursor:
            return await cursor.fetchall()


