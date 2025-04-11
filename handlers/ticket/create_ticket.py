from cryptography.fernet import Fernet
import requests
from keyboards.complete_create_ticket_kb import complete_create_order_kb
from keyboards.choose_department_kb import choose_department_kb
from keyboards.main_menu_kb import main_menu_kb

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from services.selectors import get_departments_list
from services.states import TicketStates
from aiogram import F, Router
from services.services import ticket_create

router = Router()


@router.message(F.text == "Создать заявку")
async def start_create_ticket_handler(
    message: Message,
    state: FSMContext,
):
    await message.answer("Введите текст заявки")
    await state.set_state(TicketStates.set_ticket_text)


@router.message(TicketStates.set_ticket_text)
async def set_order_text_handler(message: Message, state: FSMContext):
    await state.update_data(ticket_text=message.text)
    departments_list: list[dict] = get_departments_list(message.chat.id)
    await state.update_data(departments_list=departments_list)

    await message.answer(
        "Введите пожалуйста целевой отдел",
        reply_markup=await choose_department_kb(
            departments_list=[dep.get("name") for dep in departments_list]
        ),
    )
    await state.set_state(TicketStates.set_department)


@router.message(TicketStates.set_department)
async def set_department_handler(message: Message, state: FSMContext):
    departments_list: list[dict] = await state.get_value("departments_list")
    (department_id,) = tuple(
        department.get("id")
        for department in departments_list
        if department.get("name") == message.text
    )
    await state.update_data(department_id=department_id)
    ticket_text = await state.get_value("ticket_text")

    await message.answer(
        f"Текст заявки: {ticket_text}\nОтдел:{message.text}",
        reply_markup=complete_create_order_kb(),
    )
    await state.set_state(TicketStates.end_creation_order)


@router.callback_query(
    F.data == "complete_creation_order", TicketStates.end_creation_order
)
async def complete_creation_order_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    order_data = await state.get_data()

    department_id = order_data.get("department_id")
    ticket_text = order_data.get("ticket_text")
    response_data: dict = ticket_create(
        text=ticket_text, telegram_id=callback.message.chat.id, department=department_id
    )

    await callback.message.answer(
        text=f"Заявка добавлена\n Её ID - {response_data.get("id", None)}",
    )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    await callback.answer(reply_markup=await main_menu_kb(callback.from_user.id))
