from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Импортируем функцию отправки из services
from services.send_message import send_message_to_user

router = APIRouter()


class MessageBody(BaseModel):
    type: str
    user_ids: list[int]
    text: str


@router.post("/send_message")
async def bulk_send_message(body: MessageBody) -> dict[str, str]:
    """
    Рассылка сообщения пользователям
    Пример:
    POST /api/send_message
    {
      "type": "ticket",
      "user_ids": [123456789, 124512, 12341254],
      "text": "Привет!"
    }
    """
    for id in body.user_ids:
        success = await send_message_to_user(id, body.text)
        if not success:
            raise HTTPException(
                status_code=500, detail="Не удалось отправить сообщение"
            )
    return {"status": "Message sent successfully"}
