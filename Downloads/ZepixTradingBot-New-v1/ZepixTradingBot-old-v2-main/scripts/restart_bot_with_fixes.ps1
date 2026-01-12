#!/usr/bin/env pwsh
# Restart bot with all fixes applied - clears Python cache and reloads code

Write-Host "🔄 RESTARTING BOT WITH FIXED DIAGNOSTIC COMMANDS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop running bot
Write-Host "⏹️  Stopping running bot processes..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*venv*" } | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "✅ Bot stopped" -ForegroundColor Green
Write-Host ""

# Step 2: Clear Python cache to force reload
Write-Host "🗑️  Clearing Python cache files..." -ForegroundColor Yellow
$cacheCount = 0

# Remove __pycache__ directories
Get-ChildItem -Path "src" -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    $cacheCount++
    Write-Host "   Removed: $($_.FullName)" -ForegroundColor Gray
}

# Remove .pyc files
Get-ChildItem -Path "src" -Recurse -Filter "*.pyc" | ForEach-Object {
    Remove-Item $_.FullName -Force
    $cacheCount++
}

Write-Host "✅ Cleared $cacheCount cache files/directories" -ForegroundColor Green
Write-Host ""

# Step 3: Display what was fixed
Write-Host "🔧 FIXES APPLIED:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ export_logs      → Now reads logs/bot.log (REAL data, 1600+ lines)" -ForegroundColor Green
Write-Host "✅ log_file_size    → Now reads logs/bot.log (correct statistics)" -ForegroundColor Green
Write-Host "✅ error_stats      → Now reads logs/bot.log (real errors)" -ForegroundColor Green
Write-Host "✅ health_status    → Now checks logs/bot.log size" -ForegroundColor Green
Write-Host "✅ clear_old_logs   → Admin restriction REMOVED (owner access)" -ForegroundColor Green
Write-Host "✅ Backup detection → Now checks bot.log.1, bot.log.2, etc." -ForegroundColor Green
Write-Host ""

# Step 4: Restart bot with new code
Write-Host "🚀 Starting bot with fixed code..." -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Start bot
.\venv\Scripts\python.exe -m src.main
