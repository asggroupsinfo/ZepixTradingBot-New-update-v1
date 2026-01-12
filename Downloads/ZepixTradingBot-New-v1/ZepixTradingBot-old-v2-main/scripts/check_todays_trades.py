import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('data/trading_bot.db')
cursor = conn.cursor()

# Query all trades from today
cursor.execute("""
    SELECT symbol, direction, entry_price, exit_price, pnl, 
           open_time, close_time, status, strategy
    FROM trades 
    WHERE DATE(open_time) = DATE('now', 'localtime')
    ORDER BY open_time
""")

trades = cursor.fetchall()

print("="*70)
print("📊 TRADES FROM TODAY (December 13, 2025)")
print("="*70)

if not trades:
    print("No trades found for today")
else:
    total_pnl = 0
    wins = 0
    losses = 0
    
    for i, trade in enumerate(trades, 1):
        symbol, direction, entry, exit_p, pnl, open_t, close_t, status, strategy = trade
        print(f"\nTrade #{i}:")
        print(f"  Time: {open_t} to {close_t}")
        print(f"  {symbol} {direction.upper()}")
        print(f"  Entry: {entry} | Exit: {exit_p if exit_p else 'N/A'}")
        print(f"  P&L: ${pnl if pnl else 0:.2f}")
        print(f"  Status: {status} | Strategy: {strategy}")
        
        if pnl:
            total_pnl += pnl
            if pnl > 0:
                wins += 1
            else:
                losses += 1
    
    print("\n" + "="*70)
    print("📈 SUMMARY:")
    print("="*70)
    print(f"Total Trades: {len(trades)}")
    print(f"Wins: {wins} | Losses: {losses}")
    if len(trades) > 0:
        win_rate = (wins / len(trades)) * 100
        print(f"Win Rate: {win_rate:.1f}%")
    print(f"Total P&L: ${total_pnl:.2f}")
    print("="*70)

conn.close()
