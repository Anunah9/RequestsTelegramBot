from dataclasses import dataclass
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message
from services.order import TicketStates
from aiogram.fsm.context import FSMContext

from handlers.ticket import send_ticket

router = Router()


@router.message(TicketStates.set_subdivisions)
async def set_subdivisions(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if message.text == "Завершить":
        await message.answer("Принято.")
        print(state_data.get("subdivisions"))
        await send_ticket.process_selected_order(message, state)
    else:
        subs = state_data.get("subdivisions")
        if subs:
            await state.update_data(subdivisions=[*subs, message.text])
        else:
            await state.update_data(
                subdivisions=[
                    message.text,
                ]
            )
