# 1. Базовый образ с Python 3.11
FROM python:3.11-slim

# 2. Устанавливаем зависимости системы, включая postgresql-client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 3. Создаём рабочую директорию
WORKDIR /app

# 4. Копируем зависимости
COPY requirements.txt .

# 5. Устанавливаем Python зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копируем весь проект
COPY . .

# 7. Переменные окружения
ENV PYTHONUNBUFFERED=1

# 8. Команда запуска (docker-compose её может переопределять)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]