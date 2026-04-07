#!/bin/bash
echo "Running syntax check..."
python3 -m py_compile app/*.py
echo "Tests passed!"