import functools
import aiosqlite
from typing import Optional


class AsyncDataBase:
    _instance: Optional["AsyncDataBase"] = None

    @staticmethod
    def is_connected(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._connection is None:
                raise ConnectionError("Database connection is not established. Call `connect()` first.")
            return func(self, *args, **kwargs)
        return wrapper
    
    def __new__(cls, db_path: str):
        if cls._instance is None:
            cls._instance = super(AsyncDataBase, cls).__new__(cls)
            cls._instance._db_path = db_path
            cls._instance._connection = None
        return cls._instance

    async def connect(self):
        if self._connection is None:
            self._connection = await aiosqlite.connect(self._db_path)
    
    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

    @is_connected
    async def get_user_from_db(self, telegram_id: int):
        async with self._connection.execute("SELECT * FROM Users WHERE telegram_id=?", (telegram_id,)) as cursor:
            return await cursor.fetchone()
        
    @is_connected
    async def add_user_to_db(self, user_obj: list):
        async with self._connection.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?)", user_obj) as cursor:
            return await cursor.fetchone()

    
