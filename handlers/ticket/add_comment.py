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
from services.services import set_comment
from services.states import TicketStates

router = Router()


@router.message(F.text == "Добавить комментарий")
async def choose_ticket_id_handler(message: Message, state: FSMContext):
    await message.answer("Введите ID заявки:")
    await state.set_state(TicketStates.get_ticket_id_for_set_comment)


@router.message(TicketStates.get_ticket_id_for_set_comment)
async def set_ticket_id_handler(message: Message, state: FSMContext):
    await state.update_data(ticket_id=message.text)
    await message.answer("Введите текст комментария:")
    await state.set_state(TicketStates.set_comment)


@router.callback_query(SendMessageKbCallback.filter(F.action == "add_comment"))
async def set_comment_btn_handler(
    callback: CallbackQuery,
    callback_data: SendMessageKbCallback,
    state: FSMContext,
):
    ticket_id = callback_data.ticket_id
    await state.update_data(ticket_id=ticket_id)
    await callback.message.answer("Введите текст комментария:")
    await state.set_state(TicketStates.set_comment)
    await callback.answer()


@router.message(TicketStates.set_comment)
async def set_comment_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить", callback_data="complete_set_comment"
                )
            ]
        ]
    )
    await message.answer(
        f"Текст комментария: {message.text}\n",
        reply_markup=inline_kb,
    )

    await state.set_state(TicketStates.end_set_comment)


@router.callback_query(F.data == "complete_set_comment", TicketStates.end_set_comment)
async def complete_set_comment(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    comment_data = await state.get_data()

    set_comment(
        ticket_id=comment_data.get("ticket_id"),
        comment_text=comment_data.get("text"),
        telegram_id=callback.from_user.id,
    )
    await callback.message.answer(
        text=f"Комментарий добавлен",
    )

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await state.clear()
    await callback.answer(reply_markup=await main_menu_kb(callback.from_user.id))
