# Базовый образ с Python
FROM python:3.11-slim

ARG DEPLOY_REF
ENV DEPLOY_REF=$DEPLOY_REF

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файла зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание директории для данных
RUN mkdir -p /app/data

# Открытие порта
EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
