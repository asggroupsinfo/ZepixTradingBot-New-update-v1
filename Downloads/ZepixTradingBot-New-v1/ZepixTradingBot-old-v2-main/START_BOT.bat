@echo off
cd /d "%~dp0"
echo ========================================
echo ZEPIX TRADING BOT - STARTING...
echo ========================================
echo.

REM Start the bot
python start_bot_standalone.py

echo.
echo ========================================
echo BOT STOPPED
echo ========================================
pause
