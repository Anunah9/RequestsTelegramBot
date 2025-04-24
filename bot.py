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
from handlers.ticket import show_ticket, create_ticket, set_subdivisions, add_comment
from handlers.report import create_report, accept_ticket
from services.logger import logger
import settings
import uvicorn
from fastapi import FastAPI
from endpoints import send_message_router

bot = Bot(
    token=settings.TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def configure_bot():

    dp = Dispatcher(storage=MemoryStorage())

    await bot.delete_webhook(drop_pending_updates=True)

    ticket_routers = [
        create_ticket.router,
        show_ticket.router,
        set_subdivisions.router,
        add_comment.router,
    ]
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
app.state.bot = bot


async def configure_fast_api_server():
    app.include_router(send_message_router.router, prefix="/api", tags=["messages"])
    config = uvicorn.Config(app, host="0.0.0.0", port=8005, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    await asyncio.gather(
        configure_bot(),
        configure_fast_api_server(),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # Устанавливаем 'bot' в 'app.state' перед запуском
    if not hasattr(app.state, "bot"):
        app.state.bot = (
            bot  # На случай если __main__ выполняется до глобального присвоения
        )

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Приложение останавливается...")
    finally:
        print("Приложение завершило работу.")
