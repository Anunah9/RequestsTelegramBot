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
    

