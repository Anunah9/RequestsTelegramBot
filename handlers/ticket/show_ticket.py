from datetime import date
from typing import Optional
from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
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

    next_page = callback_data.next_page
    previous_page = callback_data.previous_page
    action = callback_data.action
    if action == "next_page":
        page = next_page
    elif action == "previous_page":
        page = previous_page
    else:
        page = None
    paginated_response = get_ticket_list(
        telegram_id=callback.message.chat.id, status=callback_data.filter, page=page
    )
    next_page = paginated_response.get("next")
    previous_page = paginated_response.get("previous")
    cb_next = FilterTicketsCallback(
        filter=callback_data.filter,
        next_page=next_page,
        previous_page=previous_page,
        action="next_page",
    )
    cb_prev = FilterTicketsCallback(
        filter=callback_data.filter,
        next_page=next_page,
        previous_page=previous_page,
        action="previous_page",
    )
    count = paginated_response.get("count")
    pages = round(count / 10)
    tickets: list[dict] = paginated_response.get("results")
    tickets_list = [
        f"Страница {1 if not previous_page else previous_page+1} из {pages}",
    ]
    for ticket in tickets:
        ticket_message = build_ticket_message(
            ticket_id=ticket.get("id"),
            ticket_text=ticket.get("text"),
            created_at=ticket.get("created_at"),
            status=ticket.get("status"),
            report_text=ticket.get("report_text"),
        )
        tickets_list.append(ticket_message)

        # await callback.message.answer(ticket_message)
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=cb_prev.pack()),
                InlineKeyboardButton(text="Вперед", callback_data=cb_next.pack()),
            ]
        ]
    )
    if action in ("next_page", "previous_page"):
        await callback.message.edit_text(
            text="\n----------------------------------------------------\n".join(
                tickets_list
            ),
            reply_markup=inline_kb,
        )
    else:
        await callback.message.answer("Заявки:")
        await callback.message.answer(
            "\n----------------------------------------------------\n".join(
                tickets_list
            ),
            reply_markup=inline_kb,
        )
    await callback.answer()
