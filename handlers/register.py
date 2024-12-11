from aiogram import types
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from assets.user import UserState, User
from assets.db import AsyncDataBase
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.role_keyboard import choose_role_keyboard
from aiogram.types import ReplyKeyboardRemove

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
    await message.answer(
        "Принято. Теперь введите пожалуйста вашу роль.",
        reply_markup=await choose_role_keyboard(),
    )
    await state.set_state(UserState.set_role)


@router.message(UserState.set_role, F.text)
async def input_role(message: Message, state: FSMContext):
    role_str = message.text
    role_dict = await AsyncDataBase("./db.db").get_roles_dict()
    role = list(filter(lambda x: x[1] == role_str, role_dict.items()))
    if role:

        await state.update_data(role=role[0])
        await message.answer("Принято. Теперь введите пожалуйста ваш отдел.")
        await state.set_state(UserState.set_department)
    else:
        message.answer(
            "Что-то пошло не так. Пожалуйста повторите ввод.",
            reply_markup=await choose_role_keyboard(),
        )


@router.message(UserState.set_department, F.text)
async def input_surname(message: Message, state: FSMContext):
    await state.update_data(department=message.text)
    await message.answer("Принято.")

    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Завершить", callback_data="end_registration")
    )
    await message.answer(
        "Все данные введены. Завершить регистрацию?", reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "end_registration", UserState.set_department)
async def end_registration(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await callback.message.answer(
        f"ФИО: {user_data['name']} {user_data['surname']}\nВаш отдел {user_data['department']} Ваша роль: {user_data['role'][1]}"
    )
    db = AsyncDataBase("./db.db")
    user = User(
        callback.message.chat.id,
        user_data["name"],
        user_data["surname"],
        user_data["department"],
        int(user_data["role"][0]),
    )
    await db.register_new_user(user.get_user_data())
    await state.clear()
    await callback.answer(text="Спасибо за регистрацию.\nПриятного пользования")
