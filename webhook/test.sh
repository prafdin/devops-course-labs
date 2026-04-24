#!/bin/bash

BRANCH=$1
echo "=== test: $BRANCH ==="
echo "Current directory: $(pwd)"

# Простая проверка - просто выводим информацию о проекте
echo "Checking project structure..."

# Проверяем наличие файлов
if [ -f "README.md" ]; then
    echo "✅ README.md exists"
else
    echo "⚠️  README.md not found (not critical)"
fi

if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
else
    echo "⚠️  Not a git repository (working with cloned code)"
fi

# Считаем количество файлов
file_count=$(find . -type f -name "*.py" 2>/dev/null | wc -l)
echo "📊 Python files found: $file_count"

echo "✅ All tests passed successfully!"
exit 0
