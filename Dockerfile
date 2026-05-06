FROM python:3.12-slim

# Аргумент для передачи на этапе сборки
ARG DEPLOY_REF=unknown

# Переменная окружения внутри контейнера
ENV DEPLOY_REF=$DEPLOY_REF

WORKDIR /app

# Установка зависимостей проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Перенос исходного кода в контейнер
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY config.json .

# Прослушиваемый порт приложения
EXPOSE 8181

# Точка входа: запуск сервеса на всех интерфейсах
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
