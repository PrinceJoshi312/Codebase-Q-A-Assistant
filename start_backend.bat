@echo off
set PYTHONPATH=.
python -m uvicorn src.api:app --host 0.0.0.0 --port 12345
