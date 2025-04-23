from dis import pretty_flags
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class SendMessageKbCallback(CallbackData, prefix="request"):
    ticket_id: int
    action: str


class FilterTicketsCallback(CallbackData, prefix="view_tickets"):
    filter: Optional[str] = None
    next_page: Optional[int] = None
    previous_page: Optional[int] = None
    action: Optional[str] = None
