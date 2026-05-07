FROM python:3.14.4-slim

# Настройки на средата
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Инсталиране на зависимости
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Копиране на проекта
COPY . /code/
