import base64
import os
import struct
from Crypto.Cipher import AES
import requests
import settings


def encrypt_telegram_id(telegram_id: int) -> str:
    key = settings.SECRET_KEY
    data = struct.pack(">Q", telegram_id)
    nonce = os.urandom(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    ciphertext = cipher.encrypt(data)
    token = base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")
    return token


def ticket_create(text: str, department: int, telegram_id: int) -> requests.Response:
    """Функция создания заявки"""
    token = encrypt_telegram_id(telegram_id)
    print({"text": text, "department": department})
    response = requests.post(
        settings.BASE_URL + "/api/v1/tickets/create_ticket",
        json={"text": text, "department": department},
        headers={"X-Custom-Token": token},
    )
    print(response, f"body: {response.json()}")
    return response.json()
