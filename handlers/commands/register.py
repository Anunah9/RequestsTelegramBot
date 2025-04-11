# from aiogram import types
# from aiogram import Router, F
# from aiogram.types import Message
# from aiogram.filters import StateFilter
# from aiogram.fsm.context import FSMContext
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from keyboards.role_keyboard_kb import choose_from_list_keyboard
# from keyboards.main_menu_kb import main_menu_kb
# from services.subdivision import AsyncSubdivisionRepository, Subdivision
# from services.department import AsyncDepartmentRepository, Department

# router = Router()


# class Registration:
#     def __init__(self):
#         self.db_path = "./db.db"
#         self.department_repo = AsyncDepartmentRepository(self.db_path)
#         self.department_obj = Department(self.department_repo)
#         self.subdivision_repo = AsyncSubdivisionRepository(self.db_path)
#         self.subdivision_obj = Subdivision(self.subdivision_repo)
#         self.repository = AsyncDataBase("./db.db")
#         self.user = User()


#     def convert_to_names(self, items):

#         return [i[1] for i in items]

#     async def get_roles(self) -> list:
#         return await self.user.get_roles()

#     async def get_departments(self):
#         return await self.department_obj.get_department_list()

#     async def get_departments_names(self):
#         return self.convert_to_names(await self.department_obj.get_department_list())

#     async def get_subdivisions(self, department_id):
#         return await self.subdivision_obj.get_subdivision_list(
#             department_id=department_id
#         )

#     async def get_subdivisions_names(self, department_id):

#         return self.convert_to_names(
#             await self.subdivision_obj.get_subdivision_list(department_id=department_id)
#         )


# @router.message(StateFilter(UserState.start_register))
# async def cmd_registration(message: Message, state: FSMContext):
#     register_obj = Registration()
#     await state.update_data(register_obj=register_obj)
#     await message.answer("Для регистрации в боте введите пожалуйста свое имя (Только имя без фамилии):")
#     await state.set_state(UserState.set_name)


# @router.message(UserState.set_name, F.text)
# async def input_name(message: Message, state: FSMContext):
#     register_obj = Registration()
#     await state.update_data(register_obj=register_obj)
#     await state.update_data(name=message.text)

#     # Переходим к следующему шагу
#     await message.answer("Принято. Теперь введите пожалуйста вашу фамилию.")
#     await state.set_state(UserState.set_surname)


# @router.message(UserState.set_surname, F.text)
# async def input_surname(message: Message, state: FSMContext, ):
#     await state.update_data(surname=message.text)

#     # Переходим к следующему шагу
#     register_obj: Registration = await state.get_value("register_obj")
#     await message.answer(
#         "Принято. Теперь введите пожалуйста вашу роль.",
#         reply_markup=await choose_from_list_keyboard(await register_obj.get_roles()),
#     )
#     await state.set_state(UserState.set_role)


# @router.message(UserState.set_role, F.text)
# async def input_role(message: Message, state: FSMContext):
#     role_str = message.text
#     register_obj: Registration = await state.get_value("register_obj")
#     roles = await register_obj.get_roles()
#     if role_str not in roles:
#         message.answer(
#             "Что-то пошло не так. Пожалуйста повторите ввод.",
#             reply_markup=await choose_from_list_keyboard(roles),
#         )
#         return
#     await state.update_data(role=role_str)

#     # Переходим к следующему шагу
#     await message.answer(
#         "Принято. Теперь введите пожалуйста ваш отдел.",
#         reply_markup=await choose_from_list_keyboard(
#             await register_obj.get_departments_names()
#         ),
#     )
#     await state.set_state(UserState.set_department)


# @router.message(UserState.set_department, F.text)
# async def input_department(message: Message, state: FSMContext):
#     """Получение данных об отделе пользователя"""

#     register_obj: Registration = await state.get_value("register_obj")
#     if not await register_obj.department_obj.check_department_name(message.text):
#         message.answer(
#             "Что-то пошло не так. Пожалуйста повторите ввод.",
#             reply_markup=await choose_from_list_keyboard(
#                 await register_obj.get_departments_names()
#             ),
#         )
#         return

#     await state.update_data(department=message.text)
#     department_id = (await register_obj.department_obj.get_id_by_name(message.text))[0]
#     await state.update_data(department_id=department_id)
#     await message.answer(
#         "Принято. Теперь введите пожалуйста подразделение",
#         reply_markup=await choose_from_list_keyboard(
#             await register_obj.get_subdivisions_names(department_id)
#         ),
#     )
#     await state.set_state(UserState.set_subdivision)


# @router.message(UserState.set_subdivision, F.text)
# async def input_subdivision(message: Message, state: FSMContext):
#     """Получение данных о подразделении пользователя"""

#     register_obj: Registration = await state.get_value("register_obj")

#     department_id = await state.get_value("department_id")
#     if not await register_obj.subdivision_obj.check_subdivision_name(message.text):
#         message.answer(
#             "Что-то пошло не так. Пожалуйста повторите ввод.",
#             reply_markup=await choose_from_list_keyboard(
#                 await register_obj.get_subdivisions_names(department_id)
#             ),
#         )
#         return

#     await state.update_data(subdivision=message.text)

#     # Переходим к следующему шагу
#     await move_to_end_registration(message, state)


# async def move_to_end_registration(message: Message, state: FSMContext):
#     builder = InlineKeyboardBuilder()
#     builder.add(
#         types.InlineKeyboardButton(text="Завершить", callback_data="end_registration")
#     )
#     await message.answer(
#         "Все данные введены. Завершить регистрацию?", reply_markup=builder.as_markup()
#     )
#     await state.set_state(UserState.end_registration)


# @router.callback_query(F.data == "end_registration", UserState.end_registration)
# async def end_registration(callback: types.CallbackQuery, state: FSMContext):
#     user_data = await state.get_data()
#     await callback.message.answer(
#         f"ФИО: {user_data['name']} {user_data['surname']}\nВаш отдел {user_data['department']} Ваша роль: {user_data['role']}, Ваше подразделение: {user_data["subdivision"]}"
#     )
#     repository = AsyncUserRepository("./db.db")
#     register_obj: Registration = await state.get_value("register_obj")
#     department_id = await register_obj.department_obj.get_id_by_name(
#         user_data["department"]
#     )

#     subdivision_id = await register_obj.subdivision_obj.get_id_by_name(
#         user_data["subdivision"]
#     )
#     await repository.register_user(
#         (
#             callback.message.chat.id,
#             user_data["name"],
#             user_data["surname"],
#             user_data["role"],
#             department_id[0],
#             subdivision_id[0],
#         )
#     )
#     await state.clear()
#     await callback.answer(
#         text="Спасибо за регистрацию.\nПриятного пользования",
#         reply_markup=await main_menu_kb(callback.message.chat.id),
#     )
