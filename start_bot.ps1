$PythonExe = "C:\Users\xazra\AppData\Local\Programs\PythonEmbed\python.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🔬 GISTOLOGIYA TELEGRAM BOT (@Gistalogiya_bot)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $PythonExe)) {
    Write-Host "[XATOLIK] Python topilmadi: $PythonExe" -ForegroundColor Red
    pause
    exit
}

Set-Location $ScriptDir
Write-Host "Bot serveri ishga tushirilmoqda..." -ForegroundColor Yellow
& $PythonExe bot.py
