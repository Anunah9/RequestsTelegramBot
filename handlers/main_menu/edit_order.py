from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from assets.order import OrderStates, Order, AsyncOrderRepository
from assets.worker import AsyncWorkerRepository, Worker
from middlewares.check_user_right import CheckUserRight
from keyboards.edit_order_kb import edit_order_keyboard
from keyboards.main_menu_kb import main_menu_keyboard


router = Router()
router.message.middleware(CheckUserRight("edit_order"))


@router.message(F.text == "Редактировать заявку")
async def start_edit_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции редактирования заявки")
    await message.answer("Введите ID заявки которую хотите отредактировать.")
    await state.set_state(OrderStates.get_order_id)


@router.message(OrderStates.get_order_id)
async def choose_editable_value(message: Message, state: FSMContext):
    await state.update_data(order_id=message.text)
    await message.answer(
        "Выберите что вы хотите отредактировать.", reply_markup=edit_order_keyboard()
    )


@router.callback_query(F.data == "edit_text")
async def edit_text(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    repository = AsyncOrderRepository("./db.db")
    order_obj = Order(repository=repository)
    await state.update_data(order=order_obj)
    text = await order_obj.get_order_by_id(data["order_id"])
    await callback.message.answer(f"Текст заявки: {text[1]}")
    await callback.message.answer("Введите новый текст заявки: ")
    await state.set_state(OrderStates.set_edited_order_text)


@router.message(OrderStates.set_edited_order_text)
async def complete_edit_order_text(message: Message, state: FSMContext):
    data = await state.get_data()
    order = data["order"]
    await order.edit_text_order(data["order_id"], message.text)
    text = await order.get_order_by_id(data["order_id"])
    await message.answer(
        f"Текст заявки: {text[1]}",
        reply_markup=await main_menu_keyboard(message.chat.id),
    )
    await state.clear()


## TODO Доделать
@router.callback_query(F.data == "edit_workers")
async def edit_text(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    repository = AsyncWorkerRepository("./db.db")
    worker_obj = Worker(repository=repository)
    await state.update_data(order=worker_obj)
    text = await worker_obj.get_workers_by_order_id(data["order_id"])
    await callback.message.answer(f"Работники: {text[1]}")
    await callback.message.answer("Введите новый текст заявки: ")
    await state.set_state(OrderStates.set_edited_order_text)


@router.message(OrderStates.set_edited_order_text)
async def complete_edit_order_text(message: Message, state: FSMContext):
    data = await state.get_data()
    order = data["order"]
    await order.edit_text_order(data["order_id"], message.text)
    text = await order.get_order_by_id(data["order_id"])
    await message.answer(f"Текст заявки: {text[1]}")
