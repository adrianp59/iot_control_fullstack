FROM python:3.14-slim AS builder
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY requirements.txt .

ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV

RUN uv pip install --no-cache -r requirements.txt

FROM python:3.14-slim
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY . /app

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Gunicorn entry point for the application
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]