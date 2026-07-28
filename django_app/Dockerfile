# ==========================================
# ЕТАП 1: Компилиране (Builder)
# ==========================================
FROM python:3.14-slim AS builder
WORKDIR /app

# Копиране на uv от GitHub
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Копиране на зависимостите
COPY requirements.txt .

# ДЕВОПС СТАНДАРТ: Създаване на виртуална среда (venv) на фиксирано място
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV

# Инсталиране на пакетите директно във виртуалната среда
# (Без --target, оставяме uv да подреди библиотеките и изпълнимите файлове правилно)
RUN uv pip install --no-cache -r requirements.txt

# ==========================================
# ЕТАП 2: Продукция (Runner)
# ==========================================
FROM python:3.14-slim
WORKDIR /app

# Копираме цялата виртуална среда от Етап 1
COPY --from=builder /opt/venv /opt/venv

# АКТИВИРАНЕ: Добавяме виртуалната среда към системния път глобално
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Копираме кода на приложението
COPY . /app

# СИГУРНОСТ: Изпълнение като non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

RUN python manage.py collectstatic --no-input
# Стартиране през Gunicorn (който вече гарантирано е в $PATH)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]