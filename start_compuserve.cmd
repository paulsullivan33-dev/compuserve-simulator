@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 compuserve.py
) else (
  python compuserve.py
)
if errorlevel 1 (
  echo.
  echo CompuServe simulation ended with an error.
  pause
)
endlocal
