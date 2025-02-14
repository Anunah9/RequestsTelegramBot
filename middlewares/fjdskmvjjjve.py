from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable, Union
from aiogram.types import TelegramObject
from assets.department import Department, AsyncDepartmentRepository
from assets.user import User
from assets.db import AsyncDataBase
from random import randint


class ms4all(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        random = randint(0, 1000)
        if random == 420:
            await event.answer("R2ppdGsgeWZbZXE=")
        result = await handler(event, data)
        return result
