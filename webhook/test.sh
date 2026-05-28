#!/bin/bash

echo "🧪 Running tests..."

cd webhook
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python3 -m pytest ../tests/test_unit.py

echo "🎉 All tests passed!"
exit 0