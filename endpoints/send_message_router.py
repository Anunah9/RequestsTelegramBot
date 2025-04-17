from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


# Импортируем функцию отправки из services
from services.send_message import send_message_to_user

router = APIRouter()


class MessageBody(BaseModel):
    type: Optional[str] = (
        None  # Тип отправляемого сообщения: ticket - заявка, report - отчет
    )
    target_level: Optional[str] = (
        None  # Уровень отправки department - на уровень отдела, subdivision - уровень подразделения
    )
    user_ids: list[int]
    text: str
    ticket_id: int


@router.post("/send_message")
async def bulk_send_message(body: MessageBody) -> dict[str, str]:
    """
    Рассылка сообщения пользователям
    Пример:
    POST /api/send_message
    {
      "type": "ticket", # Не всегда
      "target_level": "distance_heads", # Не всегда
      "user_ids": [123456789, 124512, 12341254],
      "text": "Привет!",
      "ticket_id: 5
    }
    """
    print(body.model_dump())
    for id in body.user_ids:

        success = await send_message_to_user(
            user_id=id,
            text=body.text,
            type=body.type,
            target_level=body.target_level,
            ticket_id=body.ticket_id,
        )
        if not success:
            raise HTTPException(
                status_code=500, detail="Не удалось отправить сообщение"
            )
    return {"status": "Message sent successfully"}
