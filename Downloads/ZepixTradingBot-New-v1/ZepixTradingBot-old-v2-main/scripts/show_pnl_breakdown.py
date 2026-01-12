import sqlite3

# Connect to database
conn = sqlite3.connect('data/trading_bot.db')
cursor = conn.cursor()

# Query all trades from today
cursor.execute("""
    SELECT pnl
    FROM trades 
    WHERE DATE(open_time) = DATE('now', 'localtime')
    AND status = 'closed'
    ORDER BY open_time
""")

trades = cursor.fetchall()

total_profit = 0
total_loss = 0
wins = 0
losses = 0

for trade in trades:
    pnl = trade[0]
    if pnl and pnl > 0:
        total_profit += pnl
        wins += 1
    elif pnl and pnl < 0:
        total_loss += pnl
        losses += 1

net_pnl = total_profit + total_loss

print("="*60)
print("💰 PROFIT & LOSS BREAKDOWN")
print("="*60)
print(f"✅ Total Profit:  ${total_profit:.2f} ({wins} winning trades)")
print(f"❌ Total Loss:    ${total_loss:.2f} ({losses} losing trades)")
print("-"*60)
print(f"📊 Net P&L:       ${net_pnl:.2f}")
print("="*60)
print(f"🎯 Win Rate:      {(wins/(wins+losses)*100):.1f}%")
print("="*60)

conn.close()
