@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo The web environment is not installed yet.
  echo.
  echo Run these commands from this directory:
  echo   python -m venv .venv
  echo   .venv\Scripts\python.exe -m pip install -r requirements-web.txt
  echo.
  pause
  exit /b 1
)

echo Starting Classic CompuServe at http://127.0.0.1:8000
echo Press Ctrl+C in this window to stop it.
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" web_app.py
endlocal
