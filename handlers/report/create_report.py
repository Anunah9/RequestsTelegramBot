import asyncio
from curses import nonl
import functools
import pprint
from typing import Any, Awaitable, BinaryIO, Callable, List
from aiogram.utils.media_group import MediaGroupBuilder
from keyboards.complete_create_report_kb import complete_create_report_kb
from keyboards.main_menu_kb import main_menu_kb
from aiogram.fsm.context import FSMContext
from aiogram.types import File, Message, CallbackQuery, PhotoSize, message
from aiogram import F, Router
from callbacks import SendMessageKbCallback
from middlewares.group_media_middleware import HandleGroupMediaMessage
from services.selectors import is_report_exist
from services.services import add_report_photo, report_create
from services.states import ReportStates


router = Router()
# router.message.middleware(HandleGroupMediaMessage())


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
        await message.answer("Введите текст отчёта:")
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
    pprint.pprint(message.photo)
    pprint.pprint(message.text)
    pprint.pprint(message)
    print(message.media_group_id)
    await message.answer(
        f"Текст отчёта: {message.text}\n",
        reply_markup=complete_create_report_kb(),
    )

    await state.set_state(ReportStates.end_creation_report)


@router.callback_query(F.data == "add_photo")
async def report_choose_photo(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    await callback.message.answer("Отправьте фото:")
    await state.set_state(ReportStates.add_photo)


def handle_group_media(func) -> Callable[..., any]:
    """
    Декоратор собирает все сообщения с одним media_group_id,
    ждёт небольшую задержку (например, 0.1 секунды), чтобы успеть добавить все фото,
    и только затем вызывает func с полным списком album_list.
    """

    # Словарь «media_group_id → состояние группы»
    # В качестве состояния храним:
    #   • album_list: list[PhotoSize]
    #   • timer_task: asyncio.Task, которая по таймауту вызовет реальный хендлер
    #   • lock: bool, чтобы понять, запущена ли уже задача вызова хендлера (чтобы второй раз не запускать)
    groups: dict[str, dict] = {}

    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        nonlocal groups

        # 1) Если у сообщения нет media_group_id → одиночное фото, обрабатываем сразу
        if not message.media_group_id:
            # Можно сразу вызвать func, передав ему album_list из одного фото
            single_album = [message.photo]
            return await func(message, *args, **kwargs, album_list=single_album)

        # 2) Если пришло фото из группы (media_group_id ≠ None):
        group_id = message.media_group_id

        # Получаем или создаём состояние для этой группы
        state = groups.get(group_id)
        if state is None:
            state = {
                "album_list": [],  # список PhotoSize
                "timer_task": None,  # asyncio.Task, который через таймаут вызовет func
                "lock": False,  # флаг, что задача на вызов func уже запущена
            }
            groups[group_id] = state

        # Добавляем текущую фотографию в список группы
        state["album_list"].append(message.photo)

        # Если ещё не запущен таймер (lock == False), то создаём задачу, которая через небольшой TIMEOUT
        # вызовет наш реальный хендлер с полным album_list. lock → True, чтобы второй раз задачу не создать
        if not state["lock"]:
            state["lock"] = True

            async def _delayed_call():
                # Ждём, скажем, 0.1 секунды, чтобы Telegram успел отправить все сообщения группы
                await asyncio.sleep(0.1)

                # Берём накопленный список
                collected = state["album_list"]

                # Вызываем оригинальный хендлер (передав ему все нужные параметры).
                # Обратите внимание: message мы передаём последний (или первый) пришедший message;
                # при необходимости можно хранить первый message из группы в отдельном поле.
                await func(message, *args, **kwargs, album_list=collected)
                print("Groups before:", groups)
                # После выполнения очищаем состояние группы
                del groups[group_id]
                print("Groups after:", groups)

            # Запускаем задачу в фоновом режиме (чтобы текущий wrapper его не «блокировал»)
            state["timer_task"] = asyncio.create_task(_delayed_call())
        return

    return wrapper


@router.message(ReportStates.add_photo)
@handle_group_media
async def report_add_photo(
    message: Message, state: FSMContext, album_list: list[PhotoSize], **kwargs
) -> None:
    report_data = await state.get_data()
    pprint.pprint(album_list)
    print(f"Количество фотографий в хендлере: {len(album_list)}")
    await state.update_data(report_photo=album_list)

    await message.answer(
        text="Фотки пришли",
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
    print(report_data, "in complete report creation")
    report_creation_response: dict = await report_create(
        ticket_id=report_data.get("ticket_id"),
        text=report_data.get("text"),
        telegram_id=callback.from_user.id,
    )
    await callback.message.answer(
        text=f"Отчёт добавлен\n Его ID - {report_creation_response.get("id")}",
    )
    if report_data.get("report_photo"):
        report_photo_addition_reponse = await add_report_photo(
            report_id=report_creation_response.get("id"),
            photo_album=report_data.get("report_photo"),
            telegram_id=callback.from_user.id,
        )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    await state.clear()
    await callback.answer(reply_markup=await main_menu_kb(callback.from_user.id))
