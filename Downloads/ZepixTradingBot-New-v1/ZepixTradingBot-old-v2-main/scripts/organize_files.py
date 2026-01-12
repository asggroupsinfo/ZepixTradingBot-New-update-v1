#!/usr/bin/env python3
"""
Organize project files into proper folder structure
"""
import os
import shutil
from pathlib import Path

def organize_files():
    """Move files to appropriate folders"""
    root = Path(".")
    docs = root / "docs"
    reports = docs / "reports"
    logs_dir = root / "logs"
    
    # Create directories
    docs.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    # Files to move to docs/
    docs_files = [
        "COMPREHENSIVE_BOT_ANALYSIS.md",
        "CRITICAL_FIXES_SUMMARY.md",
        "SYMBOL_COMPATIBILITY_VERIFICATION.md",
        "IMPLEMENTATION_COMPLETE_SUMMARY.md",
        "VERIFICATION_SUMMARY.md",
        "BOT_DEPLOYMENT_VERIFICATION_REPORT.md",
        "CODE_LEVEL_TEST_REPORT.md",
        "FINAL_BOT_VERIFICATION_REPORT.md",
        "IMPLEMENTATION_VERIFICATION_REPORT.md",
        "LOG_ANALYSIS_REPORT.md",
    ]
    
    # Files to move to docs/reports/
    reports_files = [
        "BOT_DEPLOYMENT_VERIFICATION_REPORT.md",
        "CODE_LEVEL_TEST_REPORT.md",
        "FINAL_BOT_VERIFICATION_REPORT.md",
        "IMPLEMENTATION_VERIFICATION_REPORT.md",
        "LOG_ANALYSIS_REPORT.md",
    ]
    
    # Files to move to logs/
    logs_files = [
        "log-2.md",
    ]
    
    moved = 0
    for file in docs_files:
        src = root / file
        if src.exists() and src.is_file():
            dst = docs / file
            if not dst.exists():
                try:
                    shutil.move(str(src), str(dst))
                    print(f"Moved: {file} -> docs/")
                    moved += 1
                except Exception as e:
                    print(f"Error moving {file}: {e}")
    
    for file in reports_files:
        src = root / file
        if src.exists() and src.is_file():
            dst = reports / file
            if not dst.exists():
                try:
                    shutil.move(str(src), str(dst))
                    print(f"Moved: {file} -> docs/reports/")
                    moved += 1
                except Exception as e:
                    print(f"Error moving {file}: {e}")
    
    for file in logs_files:
        src = root / file
        if src.exists() and src.is_file():
            dst = logs_dir / file
            if not dst.exists():
                try:
                    shutil.move(str(src), str(dst))
                    print(f"Moved: {file} -> logs/")
                    moved += 1
                except Exception as e:
                    print(f"Error moving {file}: {e}")
    
    print(f"\n✅ Organized {moved} files")

if __name__ == "__main__":
    organize_files()

