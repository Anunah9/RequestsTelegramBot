from typing import Optional
import requests
from services.services import encrypt_telegram_id
import settings


def get_departments_list(telegram_id):
    auth_token = encrypt_telegram_id(telegram_id)
    url = settings.BASE_URL + "api/v1/common/departments_list"
    headers = {"X-Custom-Token": auth_token}
    response = requests.get(url, headers=headers)
    try:
        return response.json()
    except Exception as exc:
        raise exc


def ticket_list(telegram_id: int) -> requests.Response:
    """Возвращает заявки доступные этому пользователю"""
    token = encrypt_telegram_id(telegram_id)
    response = requests.get(
        settings.BASE_URL + "/api/v1/tickets/",
        headers={"X-Custom-Token": token},
    )
    print(response, f"body: {response.json()}")
    return response.json()


def user_detailed(telegram_id: int) -> requests.Response:
    """Возвращает заявки доступные этому пользователю"""
    token = encrypt_telegram_id(telegram_id)
    url = settings.BASE_URL + "/api/v1/auth_service/user_detailed"
    response = requests.get(
        url=url,
        headers={"X-Custom-Token": token},
    )
    return response.json()


def get_user_rights(user_id: int) -> Optional[dict]:
    auth_token = encrypt_telegram_id(user_id)
    url = settings.BASE_URL + "/api/v1/auth_service/user_rights_list"
    headers = {"X-Custom-Token": auth_token}
    response = requests.get(url, headers=headers)

    try:
        return response.json()
    except Exception as exc:
        raise exc
