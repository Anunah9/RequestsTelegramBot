from assets.db import AsyncDataBase
from aiogram.fsm.state import StatesGroup, State
from assets.rights import RIGHTS


class User:

    db = AsyncDataBase("./db.db")

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

    async def update_user_info_from_db(self):
        _, self.name, self.surname, self.department, self.role = (
            await self.db.get_user_from_db(self.telegram_id)
        )
        self.rights = RIGHTS[self.role]

    async def is_registered(self) -> bool:
        """Проверяет зарегистрирован ли пользователь"""
        await self.db.connect()
        return bool(await self.db.get_user_from_db(self.telegram_id)) or False

    def get_user_data(self) -> dict:
        """Возвращает словарь с атрибутами класса"""
        return self.__dict__


class UserState(StatesGroup):
    # Переименовать в RegisterStates
    start_register = State()
    set_name = State()
    set_surname = State()
    set_department = State()
    set_role = State()

    # Возможно нужно перенести в класс MainMenuStates

