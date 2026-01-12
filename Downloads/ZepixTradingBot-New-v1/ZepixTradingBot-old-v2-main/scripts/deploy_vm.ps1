# ZepixTradingBot - Automated Windows VM Deployment Script
# Run this script as Administrator on your Windows VM

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ZepixTradingBot v2.0 - Auto Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Please run this script as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Configuration
$REPO_URL = "https://github.com/asggroupsinfo/ZepixTradingBot-old-v6.git"
$INSTALL_DIR = "C:\ZepixTradingBot"
$PYTHON_MIN_VERSION = "3.12"

Write-Host "[1/10] Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Cyan
    
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 12)) {
            Write-Host "WARNING: Python 3.12+ recommended. Current: $major.$minor" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "ERROR: Python not found! Please install Python 3.12+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[2/10] Checking Git installation..." -ForegroundColor Green
try {
    $gitVersion = git --version 2>&1
    Write-Host "Found: $gitVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Git not found! Please install Git for Windows" -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[3/10] Checking MetaTrader 5..." -ForegroundColor Green
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-Host "MetaTrader 5 is running" -ForegroundColor Cyan
} else {
    Write-Host "WARNING: MetaTrader 5 not running!" -ForegroundColor Yellow
    Write-Host "Please start MT5 and login with account 308646228" -ForegroundColor Yellow
}

Write-Host "[4/10] Cloning repository..." -ForegroundColor Green
if (Test-Path $INSTALL_DIR) {
    Write-Host "Installation directory exists. Removing old files..." -ForegroundColor Yellow
    Remove-Item -Path $INSTALL_DIR -Recurse -Force -ErrorAction SilentlyContinue
}

try {
    git clone $REPO_URL $INSTALL_DIR
    Write-Host "Repository cloned successfully" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Failed to clone repository!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[5/10] Changing to installation directory..." -ForegroundColor Green
Set-Location $INSTALL_DIR

Write-Host "[6/10] Creating virtual environment..." -ForegroundColor Green
try {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[7/10] Activating virtual environment..." -ForegroundColor Green
try {
    # Set execution policy for current user
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & "$INSTALL_DIR\venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated" -ForegroundColor Cyan
} catch {
    Write-Host "WARNING: Could not activate virtual environment" -ForegroundColor Yellow
}

Write-Host "[8/10] Installing dependencies..." -ForegroundColor Green
Write-Host "This may take several minutes..." -ForegroundColor Yellow
try {
    & "$INSTALL_DIR\venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$INSTALL_DIR\venv\Scripts\pip.exe" install -r requirements.txt
    Write-Host "Dependencies installed successfully" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[9/10] Configuring firewall..." -ForegroundColor Green
try {
    $firewallRule = Get-NetFirewallRule -DisplayName "ZepixBot Webhook" -ErrorAction SilentlyContinue
    if ($firewallRule) {
        Write-Host "Firewall rule already exists" -ForegroundColor Cyan
    } else {
        New-NetFirewallRule -DisplayName "ZepixBot Webhook" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow | Out-Null
        Write-Host "Firewall rule created for port 8000" -ForegroundColor Cyan
    }
} catch {
    Write-Host "WARNING: Could not create firewall rule" -ForegroundColor Yellow
    Write-Host "You may need to manually allow port 8000" -ForegroundColor Yellow
}

Write-Host "[10/10] Verifying installation..." -ForegroundColor Green

# Check .env file
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "✗ .env file missing!" -ForegroundColor Red
}

# Check config file
if (Test-Path "config\config.json") {
    Write-Host "✓ config.json found" -ForegroundColor Green
} else {
    Write-Host "✗ config.json missing!" -ForegroundColor Red
}

# Check main script
if (Test-Path "run_bot.py") {
    Write-Host "✓ run_bot.py found" -ForegroundColor Green
} else {
    Write-Host "✗ run_bot.py missing!" -ForegroundColor Red
}

# Test MT5 connection
Write-Host "`nTesting MT5 connection..." -ForegroundColor Green
try {
    $mt5Test = & "$INSTALL_DIR\venv\Scripts\python.exe" -c "import MetaTrader5 as mt5; mt5.initialize(); info = mt5.account_info(); print(f'Account: {info.login}' if info else 'Not logged in'); mt5.shutdown()"
    Write-Host $mt5Test -ForegroundColor Cyan
} catch {
    Write-Host "WARNING: Could not test MT5 connection" -ForegroundColor Yellow
    Write-Host "Make sure MT5 is running and logged in" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation Directory: $INSTALL_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the bot:" -ForegroundColor Yellow
Write-Host "1. Make sure MetaTrader 5 is running and logged in (Account: 308646228)" -ForegroundColor White
Write-Host "2. Open PowerShell and run:" -ForegroundColor White
Write-Host "   cd $INSTALL_DIR" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   python run_bot.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or run directly:" -ForegroundColor White
Write-Host "   $INSTALL_DIR\venv\Scripts\python.exe $INSTALL_DIR\run_bot.py" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to create auto-start service
Write-Host "Do you want to configure auto-start on Windows boot? (Y/N)" -ForegroundColor Yellow
$autoStart = Read-Host

if ($autoStart -eq "Y" -or $autoStart -eq "y") {
    Write-Host "`nConfiguring auto-start..." -ForegroundColor Green
    
    try {
        $action = New-ScheduledTaskAction -Execute "$INSTALL_DIR\venv\Scripts\python.exe" -Argument "$INSTALL_DIR\run_bot.py" -WorkingDirectory $INSTALL_DIR
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        
        # Remove existing task if exists
        Unregister-ScheduledTask -TaskName "ZepixTradingBot" -Confirm:$false -ErrorAction SilentlyContinue
        
        # Create new task
        Register-ScheduledTask -TaskName "ZepixTradingBot" -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
        
        Write-Host "✓ Auto-start configured successfully!" -ForegroundColor Green
        Write-Host "  Bot will start automatically on Windows boot" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To manage the scheduled task:" -ForegroundColor Yellow
        Write-Host "  Start: Start-ScheduledTask -TaskName 'ZepixTradingBot'" -ForegroundColor Cyan
        Write-Host "  Stop:  Stop-ScheduledTask -TaskName 'ZepixTradingBot'" -ForegroundColor Cyan
        Write-Host "  Remove: Unregister-ScheduledTask -TaskName 'ZepixTradingBot'" -ForegroundColor Cyan
        
    } catch {
        Write-Host "✗ Failed to configure auto-start" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Do you want to start the bot now? (Y/N)" -ForegroundColor Yellow
$startNow = Read-Host

if ($startNow -eq "Y" -or $startNow -eq "y") {
    Write-Host "`nStarting ZepixTradingBot..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Yellow
    Write-Host ""
    & "$INSTALL_DIR\venv\Scripts\python.exe" "$INSTALL_DIR\run_bot.py"
} else {
    Write-Host ""
    Write-Host "Setup complete! Start the bot when ready." -ForegroundColor Green
    Write-Host ""
}

Read-Host "Press Enter to exit"
