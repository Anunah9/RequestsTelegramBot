import base64
from ctypes.util import test
import os
import struct
import requests
import settings
from Crypto.Cipher import AES


def encrypt_telegram_id(telegram_id: int) -> str:
    # Ключ должен быть длиной 16, 24 или 32 байта (например, settings.SECRET_KEY_AES)
    key = settings.SECRET_KEY
    # Преобразуем telegram_id в 8 байт (big-endian)
    data = struct.pack(">Q", telegram_id)
    # Генерируем nonce, например, 8 байт (для CTR nonce можно выбирать произвольным, но он должен быть уникальным для каждой операции)
    nonce = os.urandom(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    ciphertext = cipher.encrypt(data)
    # Объединяем nonce и шифротекст, затем кодируем в URL-safe base64
    token = base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")
    return token


def decrypt_telegram_id(token: str) -> int:
    key = (
        settings.SECRET_KEY
    )  # Ключ должен соответствовать тому, что использовался при шифровании
    # Декодируем URL-safe base64
    data = base64.urlsafe_b64decode(token.encode("utf-8"))
    # Извлекаем nonce (первые 8 байт) и шифротекст
    nonce = data[:8]
    ciphertext = data[8:]
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    decrypted_data = cipher.decrypt(ciphertext)
    # Преобразуем 8 байт в целое число (big-endian)
    telegram_id = struct.unpack(">Q", decrypted_data)[0]
    return telegram_id


def create_order(text: str, telegram_id: int) -> requests.Response:
    token = encrypt_telegram_id(telegram_id)
    print(
        settings.BASE_URL + "/api/v1/tickets/create_ticket",
    )
    print({"text": text}, {"X-Custom-Token": token})
    return requests.post(
        settings.BASE_URL + "/api/v1/tickets/create_ticket",
        json={"text": text},
        headers={"X-Custom-Token": token},
    )


def main():
    # 1026190640
    token = 1026190640
    # encrypted_token = encrypt_telegram_id(token)
    # print(encrypted_token)
    response = create_order("Сломалась жопа", token)
    print(response)
    # print(decrypt_telegram_id(encrypted_token))


main()
