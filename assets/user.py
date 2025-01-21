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

# TODO Убрать ненужную таблицу Workers так как уже есть таблица User

# Реализация репозитория на основе AsyncDataBase
class AsyncUserRepository:
    db: AsyncDataBase = None

    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_user(self, telegram_id: int) -> tuple:
        async with self.db._connection.execute(
            "SELECT * FROM Users WHERE telegram_id=?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def __add_user_to_db(self, user_obj: Tuple):
        await self.db._connection.execute(
            "INSERT INTO Users VALUES (?, ?, ?, ?, ?)", user_obj
        )
        await self.db._connection.commit()

    async def register_user(self, user_obj: Tuple) -> bool:
        """Функция регистрации нового пользователя"""
        if all([bool(i) for i in user_obj]):
            await self.__add_user_to_db(user_obj)
            return True
        else:
            raise Exception("User data not comlete:", print(user_obj.items()))

    async def get_roles(self) -> List:
        """Получение словаря с ролями"""
        async with self.db._connection.execute("SELECT * FROM Roles") as cursor:
            return [role[0] for role in await cursor.fetchall()]

    async def get_user_right(self, user_id) -> Tuple:
        """Получение словаря с правами роли"""

        async with self.db._connection.execute(
            "SELECT rr.permission_name, definition, role_fk FROM RoleRights rr JOIN (RightsDefinitions rd, Users us) WHERE role_fk=role_name AND rr.permission_name=rd.name AND us.telegram_id=?",
            (user_id,),
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

    async def connect(self):
        await self.repository.connect()

    async def update_user_info_from_db(self):
        user_data = await self.repository.get_user(self.telegram_id)
        if user_data:
            _, self.name, self.surname, self.department, self.role = user_data

            self.rights = await self.repository.get_user_right(self.telegram_id)

    async def is_registered(self) -> bool:
        return bool(await self.repository.get_user(self.telegram_id))

    def get_user_data(self) -> dict:
        return self.__dict__

    async def get_user_rigths(self):
        return await self.repository.get_user_right(self.telegram_id)

    async def get_roles(self):
        return await self.repository.get_roles()


async def main():
    user = User(telegram_id=123456)
    await user.update_user_info_from_db()
    print(user.get_user_data())


if __name__ == "__main__":
    asyncio.run(main())
