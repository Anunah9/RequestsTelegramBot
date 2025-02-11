from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable, Union
from aiogram.types import TelegramObject
from assets.department import Department, AsyncDepartmentRepository
from assets.user import User
from assets.db import AsyncDataBase


class CheckUserRight(BaseMiddleware):
    def __init__(self, right):
        self.right = right

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_data = data["event_from_user"]
        user = User(user_data.id)
        await user.connect()
        await user.update_user_info_from_db()
        department_repo = AsyncDepartmentRepository("./db.db")
        department = Department(department_repo)
        # department_id, department_name = 
        user_role = user.role  # Предположим, что в объекте User есть поле role
        data["user_role"] = user_role  # Добавляем в data
        data["user_department"] = await department.get_department_by_id(user.department)
        if self.right in [i[0] for i in user.rights]:
            result = await handler(event, data)
            return result
        else:
            await event.answer("У вас нет прав для этого действия", show_alert=True)
        return
