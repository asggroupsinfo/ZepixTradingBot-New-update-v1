# File Organization Script - Clean up root directory
# Moves documentation files to proper folders

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "ZEPIX TRADING BOT - FILE ORGANIZATION" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Create necessary folders
Write-Host "Step 1: Creating folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "docs\verification-reports" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\guides" -Force | Out-Null
Write-Host "✓ Folders created successfully" -ForegroundColor Green
Write-Host ""

# Move verification reports
Write-Host "Step 2: Moving verification reports..." -ForegroundColor Yellow
$verificationFiles = @(
    "ACTUAL_ERRORS_VERIFICATION.md",
    "BOT_RUNNING_SUCCESS.md",
    "COMMAND_VERIFICATION.md",
    "CONFIG_SAVE_FIX.md",
    "DIAGNOSTIC_COMMANDS_VERIFICATION.md",
    "DOCUMENTATION_FINAL_CORRECTION.md",
    "DOCUMENTATION_UPDATE_SUMMARY.md",
    "ERRORS_AND_FIXES.md",
    "FINAL_PRODUCTION_VERIFICATION.md",
    "FIXES_COMPLETED.md",
    "PROFIT_BOOKING_CORRECTED.md",
    "REAL_FEATURES_VERIFICATION.md"
)

$movedCount = 0
foreach ($file in $verificationFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\verification-reports\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Gray
        $movedCount++
    }
}
Write-Host "✓ Moved $movedCount verification reports" -ForegroundColor Green
Write-Host ""

# Move guides
Write-Host "Step 3: Moving guides..." -ForegroundColor Yellow
$guideFiles = @(
    "COMPLETE_COMMANDS_LIST.md",
    "DIAGNOSTIC_COMMANDS_TEST_GUIDE.md",
    "DIAGNOSTIC_FIXES_README.md",
    "IMPLEMENTATION_GUIDE_5_NEW_COMMANDS.md",
    "QUICK_START.md",
    "TELEGRAM_TESTING_GUIDE_HINDI.md"
)

$movedCount = 0
foreach ($file in $guideFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\guides\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Gray
        $movedCount++
    }
}
Write-Host "✓ Moved $movedCount guides" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "ORGANIZATION COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files organized into:" -ForegroundColor White
Write-Host "  • docs\verification-reports\" -ForegroundColor Cyan
Write-Host "  • docs\guides\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Main documentation kept in root:" -ForegroundColor White
Write-Host "  • ZEPIX __TRADING_BOT_v2 _COMPLETE_DOCUMETAION.md" -ForegroundColor Yellow
Write-Host "  • README.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Project structure is now clean! ✓" -ForegroundColor Green
