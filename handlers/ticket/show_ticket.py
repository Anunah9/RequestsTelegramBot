from datetime import date
from aiogram import F, Router
from aiogram.types import Message
import requests
from aiogram.filters import Command

from services.selectors import ticket_list
from settings import BASE_URL


# from middlewares.check_user_right import CheckUserRight

router = Router()
# router.message.middleware(CheckUserRight("get_all_orders"))


def build_ticket_message(
    *, ticket_id: int, ticket_text: str, created_at: date, status: str
) -> str:
    """Формирует текст сообщения по информации о заявке"""
    # print(STATUSES.get(status, "NaN"))
    return (
        f"ID заявки: {ticket_id}\n"
        f"Текст заявки: {ticket_text}\n"
        f"Статус заявки: {status}\n"
        f"Создана: {created_at}"
    )


@router.message(Command("tickets"))
@router.message(F.text == "Просмотреть заявки")
async def show_ticket_handler(
    message: Message,
) -> None:
    await message.answer("Заявки:")

    tickets: list[dict] = ticket_list(telegram_id=message.chat.id)

    for ticket in tickets:
        ticket_message = build_ticket_message(
            ticket_id=ticket.get("id"),
            ticket_text=ticket.get("text"),
            created_at=ticket.get("created_at"),
            status=ticket.get("status"),
        )

        await message.answer(ticket_message)
