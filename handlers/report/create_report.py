from keyboards.complete_create_report_kb import complete_create_report_kb
from keyboards.main_menu_kb import main_menu_kb
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from callbacks import SendMessageKbCallback
from services.selectors import is_report_exist
from services.services import report_create
from services.states import ReportStates


router = Router()


@router.message(F.text == "Создать отчет")
async def create_report(message: Message, state: FSMContext):

    await message.answer("Введите ID заявки")
    await state.set_state(ReportStates.choose_order_id)


@router.message(ReportStates.choose_order_id)
async def set_order_id(message: Message, state: FSMContext) -> None:
    if is_report_exist(ticket_id=message.text, telegram_id=message.chat.id):
        await message.answer("Заявка уже закрыта!")
        await state.clear()
    else:
        await state.update_data(ticket_id=message.text)
        await message.answer("Введите текст отчета:")
        await state.set_state(ReportStates.set_text)


@router.callback_query(SendMessageKbCallback.filter(F.action == "create_report"))
async def create_report_btn_handler(
    callback: CallbackQuery,
    callback_data: SendMessageKbCallback,
    state: FSMContext,
):
    ticket_id = callback_data.ticket_id
    if is_report_exist(ticket_id=ticket_id, telegram_id=callback.message.chat.id):
        await callback.message.answer("Заявка уже закрыта!")
        await state.clear()
        await callback.answer()
    else:
        await state.update_data(ticket_id=ticket_id)
        await callback.message.answer("Введите текст отчёта:")
        await state.set_state(ReportStates.set_text)
        await callback.answer()


@router.message(ReportStates.set_text)
async def set_report_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await message.answer(
        f"Текст отчёта: {message.text}\n",
        reply_markup=complete_create_report_kb(),
    )

    await state.set_state(ReportStates.end_creation_report)


@router.callback_query(
    F.data == "complete_creation_report", ReportStates.end_creation_report
)
async def complete_creation_report(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    report_data = await state.get_data()

    report_creation_response: dict = await report_create(
        ticket_id=report_data.get("ticket_id"),
        text=report_data.get("text"),
        telegram_id=callback.from_user.id,
    )
    await callback.message.answer(
        text=f"Отчёт добавлен\n Его ID - {report_creation_response.get("id")}",
    )

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await state.clear()
    await callback.answer(reply_markup=await main_menu_kb(callback.from_user.id))
