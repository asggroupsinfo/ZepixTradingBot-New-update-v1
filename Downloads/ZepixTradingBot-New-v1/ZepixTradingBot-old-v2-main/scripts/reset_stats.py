#!/usr/bin/env python3
"""
Emergency Manual Stats Reset Script
Fix for: Daily Loss Persistence Bug

Usage: python scripts/reset_stats.py
"""

import json
import os
import sys
from datetime import date

# Determine stats file path
STATS_FILE = "data/stats.json"

def main():
    print("=" * 60)
    print("EMERGENCY STATS RESET SCRIPT")
    print("=" * 60)
    print()
    
    # Check if file exists
    if not os.path.exists(STATS_FILE):
        print(f"⚠️  Stats file not found: {STATS_FILE}")
        print("Creating new stats file...")
        create_fresh_stats()
        return
    
    # Read current stats
    try:
        with open(STATS_FILE, 'r') as f:
            current_stats = json.load(f)
        
        print("📊 Current Stats:")
        print(f"   Date: {current_stats.get('date', 'N/A')}")
        print(f"   Daily Loss: ${current_stats.get('daily_loss', 0):.2f}")
        print(f"   Daily Profit: ${current_stats.get('daily_profit', 0):.2f}")
        print(f"   Lifetime Loss: ${current_stats.get('lifetime_loss', 0):.2f}")
        print(f"   Total Trades: {current_stats.get('total_trades', 0)}")
        print(f"   Winning Trades: {current_stats.get('winning_trades', 0)}")
        print()
        
    except Exception as e:
        print(f"❌ Error reading stats file: {e}")
        print("File may be corrupted. Creating fresh stats...")
        create_fresh_stats()
        return
    
    # Confirm reset
    print("⚠️  WARNING: This will reset daily loss and profit to $0.00")
    print("   Lifetime loss and trade counts will be preserved.")
    print()
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Reset cancelled.")
        return
    
    # Reset daily stats
    try:
        current_stats['date'] = str(date.today())
        current_stats['daily_loss'] = 0.0
        current_stats['daily_profit'] = 0.0
        
        # Write back to file
        with open(STATS_FILE, 'w') as f:
            json.dump(current_stats, f, indent=4)
        
        # Verify write
        with open(STATS_FILE, 'r') as f:
            verify_stats = json.load(f)
        
        if verify_stats.get('daily_loss') == 0.0:
            print()
            print("✅ SUCCESS: Daily stats reset and verified!")
            print()
            print("📊 Updated Stats:")
            print(f"   Daily Loss: ${verify_stats.get('daily_loss', 0):.2f}")
            print(f"   Daily Profit: ${verify_stats.get('daily_profit', 0):.2f}")
            print(f"   Lifetime Loss: ${verify_stats.get('lifetime_loss', 0):.2f}")
            print()
            print("✅ Bot can now accept new trades.")
            print("   Restart bot if it's currently running.")
        else:
            print("❌ ERROR: Verification failed. Daily loss not reset.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ ERROR: Failed to reset stats: {e}")
        sys.exit(1)

def create_fresh_stats():
    """Create a fresh stats file"""
    fresh_stats = {
        "date": str(date.today()),
        "daily_loss": 0.0,
        "daily_profit": 0.0,
        "lifetime_loss": 0.0,
        "total_trades": 0,
        "winning_trades": 0
    }
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        
        with open(STATS_FILE, 'w') as f:
            json.dump(fresh_stats, f, indent=4)
        
        print(f"✅ Created fresh stats file: {STATS_FILE}")
        print("   All values set to zero.")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create stats file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
