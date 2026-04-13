FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код и статику
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY config.json .

# Открываем порт 8181
EXPOSE 8181

# Запуск на 0.0.0.0 обязателен для работы внутри контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
