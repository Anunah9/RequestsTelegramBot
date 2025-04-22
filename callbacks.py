from typing import Optional
from aiogram.filters.callback_data import CallbackData


class SendMessageKbCallback(CallbackData, prefix="request"):
    ticket_id: int
    action: str


class FilterTicketsCallback(CallbackData, prefix="view_tickets"):
    filter: Optional[str]

