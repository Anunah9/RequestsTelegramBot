from dataclasses import dataclass
from email import message
import stat
from typing import Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from callbacks import SendMessageKbCallback
from handlers.main_menu import main_menu
from keyboards.choose_subdivisions_kb import choose_subdivisions_kb
from keyboards.main_menu_kb import main_menu_kb
from services.selectors import get_departments_list, get_subdivisions_list
from services.services import (
    ticket_subdivisions_update,
    update_target_subdivisions_list,
)
from services.states import TicketStates
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(F.text == "Добавить подразделения заявке")
async def manual_choose_ticket_for_subdivision_set(message: Message, state: FSMContext):
    await message.answer("Введите ID заявки:")
    await state.set_state(TicketStates.get_ticket_id)


@router.message(TicketStates.get_ticket_id)
async def get_ticket_id_from_user(message: Message, state: FSMContext):
    ticket_id = int(message.text)
    await state.update_data(ticket_id=ticket_id)
    state_data = await state.get_data()
    subdivisions_list: list[dict] = state_data.get("subdivisions_list")
    if not subdivisions_list:
        subdivisions_list = get_subdivisions_list(telegram_id=message.chat.id)
        await state.update_data(subdivisions_list=subdivisions_list)
    await message.answer(
        "Принято. Выберите пожалуйста подразделения",
        reply_markup=await choose_subdivisions_kb(subdivisions_list=subdivisions_list),
    )
    await state.set_state(TicketStates.set_subdivisions)


@router.callback_query(SendMessageKbCallback.filter(F.action == "set_subdivissions"))
async def get_ticket_id_from_user(
    callback: CallbackQuery,
    callback_data: SendMessageKbCallback,
    state: FSMContext,
):
    ticket_id = callback_data.ticket_id
    await state.update_data(ticket_id=ticket_id)
    state_data = await state.get_data()
    subdivisions_list: list[dict] = state_data.get("subdivisions_list")
    if not subdivisions_list:
        subdivisions_list = get_subdivisions_list(telegram_id=callback.message.chat.id)
        await state.update_data(subdivisions_list=subdivisions_list)
    await callback.message.answer(
        "Принято. Выберите пожалуйста подразделения",
        reply_markup=await choose_subdivisions_kb(subdivisions_list=subdivisions_list),
    )
    await state.set_state(TicketStates.set_subdivisions)


@router.message(TicketStates.set_subdivisions)
async def set_subdivisions_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    target_subdivisions: set[dict] = state_data.setdefault("subdivisions", set())
    subdivisions_list: list[dict] = await state.get_value("subdivisions_list")
    if message.text != "Завершить":
        target_subdivisions = update_target_subdivisions_list(
            subdivisions=target_subdivisions,
            subdivision_name=message.text,
            subdivisions_list=subdivisions_list,
        )

        state_data["subdivisions"] = target_subdivisions
        await state.update_data(state_data)
        await message.answer("Подразделение добавлено.")
    elif message.text == "Завершить":

        ticket_id = state_data.get("ticket_id")
        ticket_subdivisions_update(
            message.chat.id, target_subdivisions, ticket_id=ticket_id
        )
        await message.answer(
            "Принято.", reply_markup=await main_menu_kb(message.chat.id)
        )
        await state.clear()
