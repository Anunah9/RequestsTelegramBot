from aiogram.filters.callback_data import CallbackData


class SendMessageKbCallback(CallbackData, prefix="request"):
    ticket_id: int
    action: str
