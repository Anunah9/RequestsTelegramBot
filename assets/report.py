import datetime
from sqlite3 import Row
from sre_parse import State
from types import CoroutineType
from typing import Any

from aiogram.fsm.state import StatesGroup
from assets.db import AsyncDataBase
from aiogram.fsm.state import State


class ReportStates(StatesGroup):
    # Состояния для работы с заявками
    set_text = State()
    choose_order_id = State()
    end_creation_report = State()
    set_departments = State()
    set_status = State()

    # Edit states
    get_report_id = State()
    set_edited_report_text = State()
    change_report_for_send = State()

    waiting_for_report_id = State()


class ReportRepository:
    def __init__(self, db_path: str) -> None:
        self.db = AsyncDataBase(db_path)

    async def connect(self) -> None:
        await self.db.connect()

    async def create_report(
        self, order_id, text, created_at, updated_at, author
    ) -> Row | None:
        async with self.db._connection.execute(
            f"INSERT INTO Report (order_id, text, created_at, updated_at, author) VALUES (?,?,?,?,?)",
            (order_id, text, created_at, updated_at, author),
        ) as cursor:
            await self.db._connection.commit()
            return cursor.lastrowid


class Report:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def create_report(
        self, order_id, text, author
    ) -> CoroutineType[Any, Any, Row | None]:
        created_at = updated_at = datetime.datetime.now()
        return await self.repository.create_report(
            order_id, text, created_at, updated_at, author
        )
