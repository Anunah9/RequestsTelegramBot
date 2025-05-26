import os
from typing import Optional
import aiogram
from aiogram import types
from aiogram.enums import InputMediaType
from aiogram.exceptions import TelegramAPIError
import logging
from aiogram.types import (
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile,
)
from callbacks import SendMessageKbCallback
from settings import BASE_URL


logger = logging.getLogger(__name__)


def keyboard_builder(
    type: str, target_level: str, ticket_id: int
) -> InlineKeyboardMarkup | None:

    if type == "ticket":
        if target_level == "workers":
            create_report_cb = SendMessageKbCallback(
                ticket_id=int(ticket_id), action="create_report"
            )
            accept_ticket_cb = SendMessageKbCallback(
                ticket_id=int(ticket_id), action="accept_ticket"
            )
            add_comment_cb = SendMessageKbCallback(
                ticket_id=int(ticket_id), action="add_comment"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Подтвердить получение",
                            callback_data=accept_ticket_cb.pack(),
                        ),
                        InlineKeyboardButton(
                            text="Добавить комментарий",
                            callback_data=add_comment_cb.pack(),
                        ),
                        InlineKeyboardButton(
                            text="Создать отчёт",
                            callback_data=create_report_cb.pack(),
                        ),
                    ]
                ]
            )
        elif target_level == "distance_heads":
            keyboard = None
        elif target_level == "heads_and_dispatchers":
            cb3 = SendMessageKbCallback(
                ticket_id=int(ticket_id), action="set_subdivissions"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Выбрать подразделения",
                            callback_data=cb3.pack(),
                        ),
                    ]
                ]
            )
        else:
            keyboard = None

    return keyboard


async def send_message_to_user(
    bot: aiogram.Bot,
    ticket_id: int,
    user_id: int,
    text: str,
    type: Optional[str] = None,
    target_level: Optional[str] = None,
    attachments: Optional[list[str]] = None,
) -> bool:
    """
    Отправляет сообщение пользователю с идентификатором user_id.
    Возвращает True/False в зависимости от успеха отправки.

    :param type: Тип отправляемого сообщения: ticket - заявка, report - отчет
    :param target_level: Уровень отправки department - на уровень отдела, subdivision - уровень подразделения
    """
    print("Ticket id = ", ticket_id)
    if type and target_level:
        keyboard = keyboard_builder(
            type=type, target_level=target_level, ticket_id=ticket_id
        )
    else:
        keyboard = None
    try:
        if not attachments:
            await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)
            return True
        else:
            print(attachments)

            await bot.send_message(chat_id=user_id, text=text)
            attachments = [
                types.InputMediaPhoto(
                    type=InputMediaType.PHOTO, media=FSInputFile("/app" + url)
                )
                for url in attachments
            ]
            print(attachments)
            if len(attachments) > 1:
                # отправляем альбомом
                await bot.send_media_group(chat_id=user_id, media=attachments)
            else:
                single_media: types.InputMediaPhoto = attachments[0]
                await bot.send_photo(
                    chat_id=user_id,
                    photo=single_media.media,
                    caption=single_media.caption or None,
                )

            return True

    except TelegramAPIError as e:
        logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        return False
