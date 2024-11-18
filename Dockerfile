# Базовый образ
FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev gcc libxml2-dev libxslt-dev \
    libcairo2 libpango1.0-0 libjpeg62-turbo-dev libpng-dev \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt /app/

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . /app/

# Команда для запуска контейнера
CMD ["bash", "-c", "alembic upgrade head && python main.py"]
