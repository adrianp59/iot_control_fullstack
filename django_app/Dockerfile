# ==========================================
# ЕТАП 1: Компилиране и събиране на зависимостите (Debian Bookworm / glibc)
# ==========================================
FROM astral-sh/uv:0.6-python3.14-bookworm-slim AS builder
WORKDIR /app

# Копиране на изискванията за проекта
COPY requirements.txt .

# Инсталиране на пакетите с uv директно в указана папка
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-cache -r requirements.txt --target /app/packages

# ==========================================
# ЕТАП 2: Минимален, сигурен и лек Image за изпълнение
# ==========================================
FROM python:3.14.4-slim
WORKDIR /app

# Копиране на инсталираните пакети от предходния етап (сочещи към python3.14!)
COPY --from=builder /app/packages /usr/local/lib/python3.14/site-packages
COPY . /app

# Дефиниране на системните променливи за Python 3.14
ENV PYTHONPATH=/usr/local/lib/python3.14/site-packages
ENV PYTHONUNBUFFERED=1

# СИГУРНОСТ: Създаване и изпълнение като non-root потребител в Debian
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Стартиране на уеб сървъра Gunicorn
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
