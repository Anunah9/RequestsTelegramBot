from datetime import date
from typing import Optional
from aiogram import F, Router
from aiogram.types import Message
import requests
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from services.selectors import get_ticket_list
from settings import BASE_URL
from callbacks import FilterTicketsCallback
from keyboards.filter_view_tickets_kb import filter_view_tickets_kb

# from middlewares.check_user_right import CheckUserRight

router = Router()
# router.message.middleware(CheckUserRight("get_all_orders"))


def build_ticket_message(
    *,
    ticket_id: int,
    ticket_text: str,
    created_at: date,
    status: str,
    report_text: Optional[str],
) -> str:
    """Формирует текст сообщения по информации о заявке"""
    # print(STATUSES.get(status, "NaN"))
    text = (
        f"ID заявки: {ticket_id}\n",
        f"Текст заявки: {ticket_text}\n",
        f"Статус заявки: {status}\n",
        f"Отчёт по заявке: {report_text}\n" if report_text else "",
        f"Создана: {created_at}",
    )
    return "".join(text)


@router.message(Command("tickets"))
@router.message(F.text == "Просмотреть заявки")
async def choose_filter(message: Message):
    await message.answer(
        text="Выберите интересующую категорию заявок",
        reply_markup=filter_view_tickets_kb(),
    )


@router.callback_query(FilterTicketsCallback.filter())
async def show_ticket_handler(
    callback: CallbackQuery,
    callback_data: FilterTicketsCallback,
    state: FSMContext,
) -> None:
    await callback.message.answer("Заявки:")

    tickets: list[dict] = get_ticket_list(
        telegram_id=callback.message.chat.id, status=callback_data.filter
    )

    for ticket in tickets:
        ticket_message = build_ticket_message(
            ticket_id=ticket.get("id"),
            ticket_text=ticket.get("text"),
            created_at=ticket.get("created_at"),
            status=ticket.get("status"),
            report_text=ticket.get("report_text"),
        )

        await callback.message.answer(ticket_message)
    await callback.message.answer(
        "----------------------------------------------------"
    )
    await callback.answer()
