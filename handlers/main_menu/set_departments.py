from aiogram import Router, F
from aiogram.types import Message
from assets.order import OrderStates
from aiogram.fsm.context import FSMContext
from handlers.main_menu import send_order

router = Router()


@router.message(OrderStates.set_departments)
async def set_departments(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if message.text == "Завершить":
        await message.answer("Принято.")
        await send_order.process_selected_order(message, state)
    else:
        deps = state_data.get("departments")
        if deps:
            await state.update_data(
                departments=[*deps, message.text]
            )
        else:
            await state.update_data(
                departments=[
                    message.text,
                ]
            )
