#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

PROJECT_DIR="${PROJECT_PATH:-/home/Roman/Desktop/catty-reminders-app}"
BRANCH="${1:-lab1}"
TEST_LOG="$PROJECT_DIR/test_results.log"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Запуск тестов для ветки: $BRANCH${NC}"
echo -e "${BLUE}========================================${NC}"

cd "$PROJECT_DIR"

git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

COMMIT_HASH=$(git rev-parse --short HEAD)
echo -e "${BLUE}Тестируем коммит: $COMMIT_HASH${NC}"

if [ ! -d "tests" ]; then
    echo -e "${YELLOW}Папка tests не найдена - пропускаем тестирование${NC}"
    exit 0
fi

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    pip install --quiet pytest pytest-cov
    if [ -f "requirements.txt" ]; then
        pip install --quiet -r requirements.txt
    fi
fi

echo -e "${BLUE}Запуск pytest...${NC}"

TEST_COUNT=$(find tests -name "test_*.py" 2>/dev/null | wc -l)

if [ "$TEST_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}Тестовые файлы не найдены - проверка базовой загрузки приложения${NC}"
    
    if python3 -c "import app.main" 2>/dev/null; then
        echo -e "${GREEN}Приложение успешно импортируется${NC}"
        exit 0
    else
        echo -e "${RED}Ошибка импорта приложения${NC}"
        exit 1
    fi
else
    pytest tests -v --tb=short --maxfail=1 2>&1 | tee "$TEST_LOG"
    TEST_RESULT=${PIPESTATUS[0]}
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}Все тесты пройдены успешно!${NC}"
        exit 0
    else
        echo -e "${RED}Тесты не пройдены!${NC}"
        echo -e "${RED}Проверьте $TEST_LOG для деталей${NC}"
        exit 1
    fi
fi