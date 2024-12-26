from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable, Union
from aiogram.types import TelegramObject
from assets.user import User
from assets.db import AsyncDataBase
from assets.rights import RIGHTS


class CheckUserRight(BaseMiddleware):
    def __init__(self, right):
        self.right = right

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        db = AsyncDataBase("./db.db")
        await db.connect()
        user_data = data["event_from_user"]
        print(user_data)
        user = User(*(await db.get_user_from_db(user_data.id)))
        print(user.get_user_data())
        print(self.right)
        print(RIGHTS[user.role])
        if self.right in RIGHTS[user.role]["rights"]:
            result = await handler(event, data)
            return result
        else:
            await event.answer("У вас нет прав для этого действия", show_alert=True)
        return
