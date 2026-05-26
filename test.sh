#!/bin/zsh
set -e

echo "Создаем изолированное окружение для тестов..."
python3 -m venv .temp_venv
source .temp_venv/bin/activate

echo "Устанавливаем зависимости..."
pip install -r requirements.txt

echo "Запускаем pytest..."
python3 -m pytest tests/

echo "Все тесты успешно пройдены!"
