from assets.db import AsyncDataBase


class User:
    name = None
    surname = None
    db = AsyncDataBase("./db.db")

    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
    
    async def is_registered(self) -> bool:
        await self.db.connect()
        return bool(await self.db.get_user_from_db(self.telegram_id)) or False
