from cryptography.fernet import Fernet
import requests
from keyboards.complete_create_order_kb import complete_create_order_kb
from keyboards.choose_departments_kb import choose_departments_kb
from middlewares.check_user_right import CheckUserRight
from keyboards.main_menu_kb import main_menu_kb
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from assets.order import Order, OrderStates
from aiogram import F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import settings
from assets.utils import encrypt_telegram_id

router = Router()
router.message.middleware(CheckUserRight("create_order"))


@router.message(F.text == "Создать заявку")
async def create_order(message: Message, state: FSMContext, user_role, user_department):
    await state.update_data(
        {"user_role": user_role, "user_department": user_department}
    )
    await message.answer("Введите текст заявки")
    await state.set_state(OrderStates.set_text)


@router.message(OrderStates.set_text)
async def set_order_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        f"Текст заявки: {message.text}\n",
        reply_markup=complete_create_order_kb(),
    )
    await state.set_state(OrderStates.end_creation_order)


def create_order(text: str, telegram_id: int) -> requests.Response:
    token = encrypt_telegram_id(telegram_id)
    # print({"text": text}, {"X-Custom-Token": token})
    return requests.post(
        settings.BASE_URL + "/api/v1/tickets/create_ticket",
        json={"text": text},
        headers={"X-Custom-Token": token},
    )


# TODO Сделать сообщение о закрытии заявки
# TODO Сделать проверку на закрытие заявки при создании отчета


@router.callback_query(
    F.data == "complete_creation_order", OrderStates.end_creation_order
)
async def complete_creation_order(
    callback: CallbackQuery,
    state: FSMContext,
):
    order_data = await state.get_data()
    new_order = Order(
        callback.message.chat.id,
        text=order_data["text"],
    )
    print(
        "Response from creation order:",
        create_order(text=order_data.get("text"), telegram_id=callback.message.chat.id),
    )
    await new_order.add_new_order()
    await state.update_data(selected_order_id=new_order.order_id)
    await callback.message.answer(
        text=f"Заявка добавлена\n Её ID - {new_order.order_id}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Отправить заявку",
                        callback_data="send_order_from_creation_order",
                    )
                ]
            ]
        ),
    )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    await callback.answer(reply_markup=await main_menu_kb(callback.from_user.id))
