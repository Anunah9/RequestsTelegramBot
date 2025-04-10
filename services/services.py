import base64
import os
import struct
from Crypto.Cipher import AES
import settings


def encrypt_telegram_id(telegram_id: int) -> str:
    key = settings.SECRET_KEY
    data = struct.pack(">Q", telegram_id)
    nonce = os.urandom(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    ciphertext = cipher.encrypt(data)
    token = base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")
    return token
