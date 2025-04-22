from typing import Optional
import requests
from services.services import encrypt_telegram_id
import settings


def get_subdivisions_list(telegram_id) -> dict:
    auth_token = encrypt_telegram_id(telegram_id)
    url = settings.BASE_URL + "api/v1/common/subdivisions_list"
    headers = {"X-Custom-Token": auth_token}
    response = requests.get(url, headers=headers)
    try:
        print(response, response.json())
        return response.json()
    except Exception as exc:
        raise exc


def get_departments_list(telegram_id):
    auth_token = encrypt_telegram_id(telegram_id)
    url = settings.BASE_URL + "api/v1/common/departments_list"
    headers = {"X-Custom-Token": auth_token}
    response = requests.get(url, headers=headers)
    try:
        return response.json()
    except Exception as exc:
        raise exc


def get_ticket_list(telegram_id: int, status: Optional[str]= None, page: Optional[int] = None) -> dict:
    """Возвращает заявки доступные этому пользователю"""
    token = encrypt_telegram_id(telegram_id)
    params = {}
    if status:
        params["status"] = status
    if page:
        params["page"] = page
    response = requests.get(
        settings.BASE_URL + "/api/v1/tickets/tickets_list",
        headers={"X-Custom-Token": token},
        params=params
    )
    if response.status_code != 200:
        print(response, f"body: {response.json()}")
        raise Exception(response.json())
    else:
        return response.json()


def get_user_detailed(telegram_id: int) -> requests.Response:
    """Возвращает заявки доступные этому пользователю"""
    token = encrypt_telegram_id(telegram_id)
    url = settings.BASE_URL + "/api/v1/user/user_detailed"
    response = requests.get(
        url=url,
        headers={"X-Custom-Token": token},
    )
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_user_rights(user_id: int) -> Optional[dict]:
    auth_token = encrypt_telegram_id(user_id)
    url = settings.BASE_URL + "/api/v1/user/user_rights_list"
    headers = {"X-Custom-Token": auth_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        return {}



def is_report_exist(ticket_id: int, telegram_id: int):
    """Функция проверки на существование отчета по заявке"""
    url = settings.BASE_URL + "/api/v1/report/is_report_exist"
    params = {"ticket_id": ticket_id}
    token = encrypt_telegram_id(telegram_id)
    headers = {"X-Custom-Token": token}
    response = requests.get(url=url, params=params, headers=headers)
    is_exist = response.json().get("is_exist")
    return is_exist
