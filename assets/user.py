try:
    from assets.db import AsyncDataBase
    from assets.rights import RIGHTS
except:
    from db import AsyncDataBase
    from rights import RIGHTS
from aiogram.fsm.state import StatesGroup, State

from typing import Optional, Dict, Tuple
import asyncio
from abc import ABC, abstractmethod


class UserState(StatesGroup):
    # Переименовать в RegisterStates
    start_register = State()
    set_name = State()
    set_surname = State()
    set_department = State()
    set_role = State()

    # Возможно нужно перенести в класс MainMenuStates


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


# Реализация репозитория на основе AsyncDataBase
class AsyncDatabaseUserRepository(UserRepository):
    def __init__(self, db_path: str):
        self.db = AsyncDataBase(db_path)

    async def connect(self):
        await self.db.connect()

    async def get_user(
        self, telegram_id: int
    ) -> Optional[Tuple[int, str, str, str, int]]:
        return await self.db.get_user_from_db(telegram_id)

    async def register_user(self, user_obj: Dict) -> bool:
        return await self.db.register_new_user(user_obj)


# Изменение класса User для использования абстракции
class User:
    def __init__(
        self,
        telegram_id: int,
        name: str = None,
        surname: str = None,
        department: str = None,
        role: int = None,
    ):
        self.telegram_id = telegram_id
        self.name = name
        self.surname = surname
        self.department = department
        self.role = role
        self.rights: set
        self.repository = AsyncDatabaseUserRepository("./db.db")
        

    async def update_user_info_from_db(self):
        user_data = await self.repository.get_user(self.telegram_id)
        if user_data:
            _, self.name, self.surname, self.department, self.role = user_data
            self.rights = RIGHTS.get(self.role, set())

    async def is_registered(self) -> bool:
        return bool(await self.repository.get_user(self.telegram_id))

    def get_user_data(self) -> dict:
        return self.__dict__


# Пример использования
async def main():
    user = User(telegram_id=123456)
    await user.update_user_info_from_db()
    print(user.get_user_data())


# Запуск
if __name__ == "__main__":
      asyncio.run(main())
