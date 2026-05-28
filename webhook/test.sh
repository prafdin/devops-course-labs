#!/bin/bash

echo "🧪 Running tests..."

# Проверяем что есть ракетка на сайте
if grep -q "🚀" webhook/index.html; then
    echo "✅ Rocket emoji found on site"
else
    echo "❌ Rocket emoji missing - site is not ready for launch!"
    exit 1
fi

echo "🎉 All tests passed!"
exit 0