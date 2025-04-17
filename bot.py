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
from endpoints import send_message_router
from handlers.commands import start, cancel, help
from handlers.main_menu import (
    main_menu,
)
from handlers.ticket import show_ticket, create_ticket, set_subdivisions
from handlers.report import create_report, accept_ticket
from services.logger import logger
import yaml
from fastapi import FastAPI
import uvicorn


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


# Создание экземпляра телеграм бота
TOKEN = load_token_from_yaml("config.yaml")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def configure_bot():

    dp = Dispatcher(storage=MemoryStorage())

    await bot.delete_webhook(drop_pending_updates=True)

    ticket_routers = [create_ticket.router, show_ticket.router, set_subdivisions.router]
    report_routers = [create_report.router, accept_ticket.router]
    command_routers = [cancel.router, help.router, start.router]

    dp.include_routers(
        *command_routers,
        *ticket_routers,
        *report_routers,
        main_menu.router,
    )
    await dp.start_polling(bot)


# Создание экземпляра фаст апи приложения
app = FastAPI()


async def configure_fast_api_server():
    app.include_router(send_message_router.router, prefix="/api", tags=["messages"])
    config = uvicorn.Config(app, host="127.0.0.1", port=8005, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    await asyncio.gather(
        configure_bot(),
        configure_fast_api_server(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершаюсь")
