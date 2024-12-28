from typing import List, Union
from aiogram.fsm.state import StatesGroup, State
from assets.user import User
STATUSES = {
    1: "Создана",
    2: "Отправлена",
    3: "Принята",
    4: "В работе",
    5: "Закрыта"
}


class OrderStates(StatesGroup):
    # Состояния для работы с заявками
    set_text = State()
    set_departments = State()
    set_status = State()
    set_workers = State()


class Order:
    def __init__(self, text, status: str):
        self.text: str = text
        self.department: Union[str, list]
        self.status: str = status
        self.workers: Union[User|List]


