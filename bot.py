import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, cancel, help
from handlers.main_menu import create_order, main_menu, edit_order, send_order


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    TOKEN = os.getenv("TOKEN")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(
        cancel.router,
        help.router,
        start.router,
        create_order.router,
        main_menu.router,
        edit_order.router,
        send_order.router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
