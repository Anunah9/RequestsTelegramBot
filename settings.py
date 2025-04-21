import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000/")
SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN = os.getenv("TOKEN")
