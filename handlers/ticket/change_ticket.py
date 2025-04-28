from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.fsm.context import FSMContext

from callbacks import SendMessageKbCallback
from keyboards.main_menu_kb import main_menu_kb
from services.services import edit_ticket
from services.states import TicketStates

router = Router()


@router.message(F.text == "Изменить заявку")
async def choose_ticket_id_handler(message: Message, state: FSMContext):
    await message.answer("Введите ID заявки:")
    await state.set_state(TicketStates.get_ticket_id_for_edit_ticket)


@router.message(TicketStates.get_ticket_id_for_edit_ticket)
async def set_ticket_id_handler(message: Message, state: FSMContext):
    await state.update_data(ticket_id=message.text)
    await message.answer("Введите новый текст заявки:")
    await state.set_state(TicketStates.edit_ticket)


# @router.callback_query(SendMessageKbCallback.filter(F.action == "add_comment"))
# async def set_comment_btn_handler(
#     callback: CallbackQuery,
#     callback_data: SendMessageKbCallback,
#     state: FSMContext,
# ):
#     ticket_id = callback_data.ticket_id
#     await state.update_data(ticket_id=ticket_id)
#     await callback.message.answer("Введите текст комментария:")
#     await state.set_state(TicketStates.set_comment)
#     await callback.answer()


@router.message(TicketStates.edit_ticket)
async def set_edited_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить", callback_data="complete_edit_ticket"
                )
            ]
        ]
    )
    await message.answer(
        f"Новый текст заявки: {message.text}\n",
        reply_markup=inline_kb,
    )

    await state.set_state(TicketStates.end_edit_ticket)


@router.callback_query(F.data == "complete_edit_ticket", TicketStates.end_edit_ticket)
async def complete_set_comment(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    edit_data = await state.get_data()

    ticket_id = await state.get_value("ticket_id")
    edit_ticket(
        ticket_id=ticket_id,
        edited_text=edit_data.get("text"),
        telegram_id=callback.message.chat.id,
    )
    await callback.message.answer(
        text=f"Заявка изменена.",
    )

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await state.clear()
    await callback.answer(reply_markup=await main_menu_kb(callback.from_user.id))
