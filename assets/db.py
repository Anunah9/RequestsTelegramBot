import functools
import aiosqlite
from typing import Optional


class AsyncDataBase:
    _instance: Optional["AsyncDataBase"] = None

    def __new__(cls, db_path: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db_path = db_path
            cls._instance._connection = None
        return cls._instance

    async def connect(self) -> None:
        """Устанавливает подключение к базе данных."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self._db_path)

    async def close(self) -> None:
        """Закрывает подключение к базе данных."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    def get_connection(self) -> aiosqlite.Connection:
        """Возвращает текущее соединение."""
        if self._connection is None:
            raise ConnectionError("Соединение с базой данных не установлено.")
        return self._connection

    @staticmethod
    def is_connected(func):
        """Автоматически устанавливает соединение с бд при его отсутствии"""

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self._connection is None:
                await self.connect()
            return await func(self, *args, **kwargs)

        return wrapper
