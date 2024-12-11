from assets.db import AsyncDataBase
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class User:
    name = None
    surname = None
    department = None
    role = None
    db = AsyncDataBase("./db.db")

    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id

    async def is_registered(self) -> bool:
        await self.db.connect()
        return bool(await self.db.get_user_from_db(self.telegram_id)) or False
    
    def get_user_data(self) -> dict:
        return {
            'telegram_id': self.telegram_id,
            'name': self.name,
            'surname': self.surname,
            'department': self.department,
            'role': self.role
        }

    async def register_new_user(self) -> bool:
        user_obj = self.get_user_data()
        if all([bool(i[1]) for i in user_obj.items()]):
            await self.db.add_user_to_db(user_obj)
            return True
        else:
            raise Exception("User data not comlete")
            


class UserState(StatesGroup):
    set_name = State()
    set_surname = State()
    set_department = State()
