@echo off
echo Starting Main + Dashboard...

:: If your main loop is now embedded inside app_server.py, 
:: you might not even need this first line anymore!
start cmd /k python main.py

:: UPDATED: Changed 'app:app' to 'app_server:app'
start cmd /k python -m uvicorn app_server:app --reload --port 8000

echo Both services started.
pause