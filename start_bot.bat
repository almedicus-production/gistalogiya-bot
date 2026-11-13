@echo off
title Gistologiya Telegram Bot (@Gistalogiya_bot)
chcp 65001 > nul
echo ========================================================
echo  🔬 GISTOLOGIYA TELEGRAM BOTNI ISHGA TUSHIRISH
echo  Telegram: @Gistalogiya_bot
echo ========================================================
echo.

set PYTHON_EXE=C:\Users\xazra\AppData\Local\Programs\PythonEmbed\python.exe

if not exist "%PYTHON_EXE%" (
    echo [XATOLIK] Python topilmadi: %PYTHON_EXE%
    pause
    exit /b
)

echo Bot ishga tushirilmoqda...
cd /d "%~dp0"
"%PYTHON_EXE%" bot.py

pause
