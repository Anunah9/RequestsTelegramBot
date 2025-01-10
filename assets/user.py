import functools
from assets.db import AsyncDataBase
from aiogram.fsm.state import StatesGroup, State
from typing import List, Optional, Dict, Tuple
import asyncio
from abc import ABC, abstractmethod


class UserState(StatesGroup):
    # Переименовать в RegisterStates
    start_register = State()
    set_name = State()
    set_surname = State()
    set_department = State()
    set_role = State()


# Абстракция репозитория для работы с пользователями
class UserRepository(ABC):
    @abstractmethod
    async def get_user(
        self, telegram_id: int
    ) -> Optional[Tuple[int, str, str, str, int]]:
        """Получает пользователя по telegram_id."""
        pass

    @abstractmethod
    async def register_user(self, user_obj: Dict) -> bool:
        """Регистрирует нового пользователя."""
        pass

    @abstractmethod
    async def get_user_right(self, role: str) -> Optional[Tuple]:
        pass


# Реализация репозитория на основе AsyncDataBase
class AsyncUserRepository:
    db: AsyncDataBase = None

    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    @db.is_connected
    async def get_user_from_db(self, telegram_id: int) -> tuple:
        async with self._connection.execute(
            "SELECT * FROM Users WHERE telegram_id=?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()

    @db.is_connected
    async def __add_user_to_db(self, user_obj: Tuple):
        await self._connection.execute(
            "INSERT INTO Users VALUES (?, ?, ?, ?, ?)", user_obj
        )
        await self._connection.commit()

    @db.is_connected
    async def register_user(self, user_obj: Tuple) -> bool:
        """Функция регистрации нового пользователя"""
        if all([bool(i) for i in user_obj]):
            await self.__add_user_to_db(user_obj)
            return True
        else:
            raise Exception("User data not comlete:", print(user_obj.items()))

    @db.is_connected
    async def get_roles(self) -> List:
        """Получение словаря с ролями"""
        async with self._connection.execute("SELECT * FROM Roles") as cursor:
            return [role[0] for role in await cursor.fetchall()]

    @db.is_connected
    async def get_user_right(self, role: str) -> Tuple:
        """Получение словаря с правами роли"""

        async with self._connection.execute(
            "SELECT rr.permission_name, definition FROM RoleRights rr JOIN (RightsDefinitions) WHERE rr.permission_name=name AND role_name=?",
            (role,),
        ) as cursor:
            return await cursor.fetchall()


class User:
    def __init__(
        self,
        telegram_id: int,
    ):
        self.telegram_id = telegram_id
        self.name: str
        self.surname: str
        self.department: str
        self.role: str
        self.rights: Tuple
        self.repository = AsyncUserRepository("./db.db")

    async def update_user_info_from_db(self):
        user_data = await self.repository.get_user(self.telegram_id)
        if user_data:
            _, self.name, self.surname, self.department, self.role = user_data

            self.rights = await self.repository.get_user_right(self.role)

    async def is_registered(self) -> bool:
        return bool(await self.repository.get_user(self.telegram_id))

    def get_user_data(self) -> dict:
        return self.__dict__

    async def get_user_rigths(self):
        return await self.repository.get_user_right(self.role)

    async def get_roles(self):
        return await self.repository.get_roles()


async def main():
    user = User(telegram_id=123456)
    await user.update_user_info_from_db()
    print(user.get_user_data())


if __name__ == "__main__":
    asyncio.run(main())
