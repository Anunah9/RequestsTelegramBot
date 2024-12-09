from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from assets.user import UserState

router = Router()


@router.message(StateFilter(None), Command("register"))
async def cmd_registration(message: Message, state: FSMContext):
    await message.answer("Для регистрации в боте введите пожалуйста свое имя:")
    await state.set_state(UserState.set_name)


@router.message(UserState.set_name, F.text)
async def input_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Принято. Теперь введите пожалуйста вашу фамилию.")
    await state.set_state(UserState.set_surname)


@router.message(UserState.set_surname, F.text)
async def input_name(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer("Принято. Теперь введите пожалуйста вашу должность.")
    await state.set_state(UserState.set_department)


@router.message(UserState.set_department, F.text)
async def input_surname(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer("Принято.")
    await message.answer(
        f"ФИО: {user_data['name']} {user_data['surname']}\nВаша должность {message.text}"
    )
    await state.clear()


