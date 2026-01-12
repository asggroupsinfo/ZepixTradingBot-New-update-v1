# Grant Port 80 Permission for ZepixTradingBot
# This script must be run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ZepixTradingBot - Port 80 Permission" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Granting permission for port 80..." -ForegroundColor Green

try {
    # Grant permission to use port 80
    netsh http add urlacl url=http://+:80/ user=Everyone
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "SUCCESS!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Port 80 permission granted successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now run the bot without Administrator:" -ForegroundColor White
        Write-Host "  cd C:\Users\Administrator\ZepixTradingBot-old-v6" -ForegroundColor Cyan
        Write-Host "  python src/main.py --host 0.0.0.0 --port 80" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "WARNING: Command returned non-zero exit code" -ForegroundColor Yellow
        Write-Host "Permission may already be granted or command failed" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to grant permission" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
