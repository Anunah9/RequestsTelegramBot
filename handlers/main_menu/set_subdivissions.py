from aiogram import Router, F
from aiogram.types import Message
from assets.order import OrderStates
from aiogram.fsm.context import FSMContext

from handlers.main_menu import send_order

router = Router()


@router.message(OrderStates.set_subdivisions)
async def set_subdivisions(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if message.text == "Завершить":
        await message.answer("Принято.")
        await send_order.process_selected_order(message, state)
    else:
        if state_data.get("subdivisions"):
            await state.update_data(
                subdivisions=[*await state.get_value("subdivisions"), message.text]
            )
        else:
            await state.update_data(
                subdivisions=[
                    message.text,
                ]
            )