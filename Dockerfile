# 1. Базовый образ с Python
FROM python:3.9-slim

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем всё приложение
COPY . .

# 5. Указываем правильный порт
EXPOSE 8181

# 6. Команда запуска
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
