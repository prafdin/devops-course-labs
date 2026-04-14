FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /catty-reminders-app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Открываем порт приложения
EXPOSE 8181

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
