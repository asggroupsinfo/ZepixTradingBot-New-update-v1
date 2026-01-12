#!/usr/bin/env pwsh
# Verify all diagnostic command fixes are correctly applied

Write-Host ""
Write-Host "🔍 VERIFYING DIAGNOSTIC COMMAND FIXES" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Verify no bot_activity.log references
Write-Host "📋 Check 1: Verifying no bot_activity.log references..." -ForegroundColor Yellow
$badRefs = Select-String -Path "src/menu/command_executor.py" -Pattern "bot_activity\.log" -Quiet
if ($badRefs) {
    Write-Host "   ❌ FAILED: Found bot_activity.log references!" -ForegroundColor Red
    Select-String -Path "src/menu/command_executor.py" -Pattern "bot_activity\.log" | ForEach-Object {
        Write-Host "      Line $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Red
    }
    $allGood = $false
} else {
    Write-Host "   ✅ PASSED: No bot_activity.log references found" -ForegroundColor Green
}
Write-Host ""

# Check 2: Verify bot.log is being used
Write-Host "📋 Check 2: Verifying bot.log is correctly referenced..." -ForegroundColor Yellow
$goodRefs = Select-String -Path "src/menu/command_executor.py" -Pattern 'log_file = "logs/bot\.log"'
if ($goodRefs.Count -ge 3) {
    Write-Host "   ✅ PASSED: Found $($goodRefs.Count) correct bot.log references" -ForegroundColor Green
    $goodRefs | ForEach-Object {
        Write-Host "      Line $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ FAILED: Expected 3+ bot.log references, found $($goodRefs.Count)" -ForegroundColor Red
    $allGood = $false
}
Write-Host ""

# Check 3: Verify admin restriction is removed
Write-Host "📋 Check 3: Verifying admin restriction is removed from clear_old_logs..." -ForegroundColor Yellow
$adminCheck = Select-String -Path "src/menu/command_executor.py" -Pattern "Only admins can clear logs" -Quiet
if ($adminCheck) {
    Write-Host "   ❌ FAILED: Admin restriction still present!" -ForegroundColor Red
    Select-String -Path "src/menu/command_executor.py" -Pattern "Only admins can clear logs" | ForEach-Object {
        Write-Host "      Line $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Red
    }
    $allGood = $false
} else {
    Write-Host "   ✅ PASSED: Admin restriction removed" -ForegroundColor Green
}
Write-Host ""

# Check 4: Verify backup file detection is updated
Write-Host "📋 Check 4: Verifying backup file detection uses bot.log..." -ForegroundColor Yellow
$backupCheck = Select-String -Path "src/menu/command_executor.py" -Pattern 'filename\.startswith\("bot\.log"\)'
if ($backupCheck.Count -ge 2) {
    Write-Host "   ✅ PASSED: Backup detection correctly looks for bot.log.* files" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  WARNING: Expected 2+ backup detection references, found $($backupCheck.Count)" -ForegroundColor Yellow
}
Write-Host ""

# Check 5: Verify Python cache status
Write-Host "📋 Check 5: Checking for Python cache files..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Path "src" -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
$pycacheDirs = Get-ChildItem -Path "src" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue

if ($pycFiles.Count -gt 0 -or $pycacheDirs.Count -gt 0) {
    Write-Host "   ⚠️  WARNING: Found cached files that may prevent fixes from loading!" -ForegroundColor Yellow
    Write-Host "      .pyc files: $($pycFiles.Count)" -ForegroundColor Gray
    Write-Host "      __pycache__ dirs: $($pycacheDirs.Count)" -ForegroundColor Gray
    Write-Host "      Run restart_bot_with_fixes.ps1 to clear cache" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ PASSED: No Python cache files found" -ForegroundColor Green
}
Write-Host ""

# Check 6: Verify log files exist
Write-Host "📋 Check 6: Verifying log files exist..." -ForegroundColor Yellow
if (Test-Path "logs/bot.log") {
    $logInfo = Get-Item "logs/bot.log"
    $logLines = (Get-Content "logs/bot.log" | Measure-Object -Line).Lines
    $logSizeMB = [math]::Round($logInfo.Length / 1MB, 2)
    Write-Host "   ✅ bot.log exists:" -ForegroundColor Green
    Write-Host "      Size: $logSizeMB MB ($($logInfo.Length) bytes)" -ForegroundColor Gray
    Write-Host "      Lines: $logLines" -ForegroundColor Gray
    Write-Host "      Modified: $($logInfo.LastWriteTime)" -ForegroundColor Gray
    
    if ($logLines -lt 100) {
        Write-Host "      ⚠️  WARNING: Low line count, may not contain much data" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ FAILED: logs/bot.log does not exist!" -ForegroundColor Red
    $allGood = $false
}
Write-Host ""

if (Test-Path "logs/bot_activity.log") {
    $oldLogInfo = Get-Item "logs/bot_activity.log"
    $oldLogLines = (Get-Content "logs/bot_activity.log" | Measure-Object -Line).Lines
    Write-Host "   ℹ️  bot_activity.log exists (old file, should NOT be used):" -ForegroundColor Cyan
    Write-Host "      Size: $($oldLogInfo.Length) bytes" -ForegroundColor Gray
    Write-Host "      Lines: $oldLogLines" -ForegroundColor Gray
}
Write-Host ""

# Final summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Code fixes are correctly applied." -ForegroundColor Green
    Write-Host "Next step: Restart bot to load new code" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run: .\restart_bot_with_fixes.ps1" -ForegroundColor Cyan
} else {
    Write-Host "❌ SOME CHECKS FAILED!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Review errors above and fix issues before restarting bot" -ForegroundColor Yellow
}
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
