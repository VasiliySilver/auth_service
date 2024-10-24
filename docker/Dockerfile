# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY ./src ./src
COPY ./shared ./shared

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app/src

# Команда для запуска приложения
CMD ["uvicorn", "service_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

