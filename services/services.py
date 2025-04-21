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
    cipher = AES.new(key.encode('UTF-8'), AES.MODE_CTR, nonce=nonce)
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


def update_target_subdivisions_list(
    subdivisions: set, subdivision_name: str, subdivisions_list: list[dict]
) -> set:
    subdivision_id = next(
        (
            subdivision["id"]
            for subdivision in subdivisions_list
            if subdivision.get("name") == subdivision_name
        ),
        None,
    )
    print(subdivision_id)
    if subdivision_id:
        subdivisions.add(subdivision_id)
    return subdivisions


def ticket_subdivisions_update(
    telegram_id: int, subdivisions: set[int], ticket_id: int
) -> dict:
    """Функция обновления подразделений заявки"""
    token = encrypt_telegram_id(telegram_id)
    data = {"ticket_id": ticket_id, "subdivisions": list(subdivisions)}
    print(data)
    response = requests.patch(
        settings.BASE_URL + "/api/v1/tickets/set_subdivisions",
        json=data,
        headers={"X-Custom-Token": token},
    )
    print(response, f"body: {response.json()}")
    return response.json()


async def report_create(ticket_id: int, text: str, telegram_id: int):
    token = encrypt_telegram_id(telegram_id)
    headers = {"X-Custom-Token": token}
    url = settings.BASE_URL + "api/v1/report/create_report"
    json = {"ticket_id": ticket_id, "text": text}
    print("------------------------------------------------------", json)
    response = requests.post(url=url, json=json, headers=headers)
    print(response, f"body: {response.json()}")
    return response.json()


def accept_ticket(telegram_id: int, ticket_id: int):
    url = settings.BASE_URL + "api/v1/tickets/change_status"
    token = encrypt_telegram_id(telegram_id)
    headers = {"X-Custom-Token": token}
    json = {"ticket_id": ticket_id, "status": "Recieved"}
    print(json)
    response = requests.patch(url=url, json=json, headers=headers)
    print(response, f"body: {response.json()}")
    return response.json()
