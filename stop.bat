@echo off
setlocal

cd /d "%~dp0"

echo Stopping CaptUReFraud services...
docker compose down

echo.
echo Services stopped.
pause