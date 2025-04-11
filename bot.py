import asyncio
import logging
import sys
import os
from typing import final
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.commands import start, cancel, help
from handlers.main_menu import (
    main_menu,
)
from handlers.ticket import (
    send_ticket,
    show_ticket,
    create_ticket,
)
from handlers.report import create_report
from services.logger import logger
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

    ticket_routers = [
        create_ticket.router,
        show_ticket.router,
    ]
    report_routers = []
    command_routers = [cancel.router, help.router, start.router]

    dp.include_routers(
        *command_routers,
        *ticket_routers,
        *report_routers,
        main_menu.router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершаюсь")
