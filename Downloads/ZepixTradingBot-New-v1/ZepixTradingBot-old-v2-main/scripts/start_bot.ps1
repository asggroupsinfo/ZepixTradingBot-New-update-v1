# Zepix Trading Bot - Start Script
# This script starts the bot with visible logs

$env:PYTHONIOENCODING = "utf-8"

Write-Host "=== ZEPIX TRADING BOT - STARTING ===" -ForegroundColor Green
Write-Host ""
Write-Host "Bot starting on port 5000..." -ForegroundColor Yellow
Write-Host "All execution logs will appear below." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Cyan
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Change to project directory
Set-Location "C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-old-v2-main\ZepixTradingBot-old-v2-main"

# Start the bot
python src/main.py --port 5000

