import asyncio
import time
from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable, Union
from aiogram.types import TelegramObject
from random import randint, random

from services.states import ReportStates


class HandleGroupMediaMessage(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        print(getattr(event, "media_group_id", None))
        if (
            getattr(event, "media_group_id", None)
            and data.get("state") == ReportStates.add_photo
        ):
            data.setdefault("media_group_list", {})
            data["media_group_list"].setdefault(event.media_group_id, []).append(event)
            await asyncio.sleep()
            if not data.get("stop_flag"):
                print(data.get("stop_flag"))
                result = await handler(event, data)
                data["stop_flag"] = True
                return result
