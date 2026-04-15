import pytest
import sys

def test_python_version():
    assert sys.version_info.major >= 3

def test_import_fastapi():
    import fastapi
    assert fastapi.__version__ is not None

def test_app_exists():
    import os
    assert os.path.exists('app/main.py')
