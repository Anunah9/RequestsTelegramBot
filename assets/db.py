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

    async def commit(self) -> None:
        """Фиксирует изменения в базе данных."""
        if self._connection:
            await self._connection.commit()

    @staticmethod
    def ensure_connection(func):
        """Декоратор для проверки и установки соединения с базой данных."""

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self._connection is None:
                await self.connect()
            return await func(self, *args, **kwargs)

        return wrapper
