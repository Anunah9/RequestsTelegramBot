from bot import bot
from aiogram.exceptions import TelegramAPIError
import logging


logger = logging.getLogger(__name__)


async def send_message_to_user(user_id: int, text: str) -> bool:
    """
    Отправляет сообщение пользователю с идентификатором user_id.
    Возвращает True/False в зависимости от успеха отправки.
    """
    try:
        await bot.send_message(chat_id=user_id, text=text)
        return True
    except TelegramAPIError as e:
        logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        return False
