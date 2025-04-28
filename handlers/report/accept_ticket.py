from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from callbacks import SendMessageKbCallback
from services.services import accept_ticket
import settings


router = Router()


@router.callback_query(SendMessageKbCallback.filter(F.action == "accept_ticket"))
async def accept_ticket_btn_handler(
    callback: CallbackQuery,
    callback_data: SendMessageKbCallback,
    state: FSMContext,
):
    ticket_id = callback_data.ticket_id
    print(ticket_id)
    response = accept_ticket(telegram_id=callback.from_user.id, ticket_id=ticket_id)
    if response.get("success"):
        await callback.message.answer("Заявка принята!")
    else:
        await callback.message.answer("Что-то пошло не так")
    current_markup = callback.message.reply_markup
    if current_markup and current_markup.inline_keyboard:
        for row in current_markup.inline_keyboard:
            for button in row:
                if button.callback_data == callback.data:
                    # ну и просто удаляем её
                    row.remove(button)
    await callback.message.edit_reply_markup(reply_markup=current_markup)
    await callback.answer()
