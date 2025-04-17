# Базовый образ
FROM python:alpine

WORKDIR /app
ARG UID=10002
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
# Создаем непривилегированного пользователя

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1