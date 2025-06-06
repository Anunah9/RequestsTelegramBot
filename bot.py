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
from handlers.main_menu import (
    create_order,
    main_menu,
    edit_order,
    send_order,
    show_orders,
    create_report,
)
from assets.logger import logger
import yaml


def load_token_from_yaml(file_path: str) -> str:
    """Загружает TOKEN из YAML-файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return data.get("TOKEN", "")
    except FileNotFoundError:
        print("Файл не найден.")
    except yaml.YAMLError as e:
        print(f"Ошибка при чтении YAML: {e}")
    return ""


async def main() -> None:
    TOKEN = load_token_from_yaml("config.yaml")

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
        show_orders.router,
        create_report.router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
