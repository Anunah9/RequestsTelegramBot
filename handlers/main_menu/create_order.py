from keyboards.complete_create_order_kb import complete_create_order_kb
from keyboards.choose_departments_kb import choose_departments_kb
from middlewares.check_user_right import CheckUserRight
from keyboards.main_menu_kb import main_menu_kb
from aiogram.fsm.context import FSMContext
from assets.department import Department, AsyncDepartmentRepository
from aiogram.types import Message, CallbackQuery
from assets.order import Order, OrderStates
from aiogram import F, Router


router = Router()
router.message.middleware(CheckUserRight("create_order"))


@router.message(F.text == "Создать заявку")
async def create_order(message: Message, state: FSMContext):
    await message.answer("Вы в функции создания заявки\nВведите текст заявки")
    await state.set_state(OrderStates.set_text)


@router.message(OrderStates.set_text)
async def set_order_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        f"Текст заявки: {message.text}\n",
        reply_markup=complete_create_order_kb(),
    )


@router.callback_query(F.data == "complete_creation_order", OrderStates.set_text)
async def complete_creation_order(callback: CallbackQuery, state: FSMContext):
    order_data = await state.get_data()

    new_order = Order(
        text=order_data["text"],
    )
    await new_order.add_new_order()
    await state.clear()
    await callback.message.answer(
        text=f"Заявка добавлена\n Её ID - {new_order.order_id}\nЧтобы открыть основное меню используйте /main_menu",
        reply_markup=await main_menu_kb(callback.from_user.id),
    )
    await callback.answer()
