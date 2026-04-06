FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для сборки mysql-connector и работы тестов
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ проект (важно для тестов, папок testlib и tests)
COPY . .

# Устанавливаем браузеры для тестов UI (Playwright)
RUN playwright install --with-deps chromium

# Открываем порт приложения
EXPOSE 8181

# Указываем Python, где искать твои модули (папку app и testlib)
ENV PYTHONPATH=/app

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
