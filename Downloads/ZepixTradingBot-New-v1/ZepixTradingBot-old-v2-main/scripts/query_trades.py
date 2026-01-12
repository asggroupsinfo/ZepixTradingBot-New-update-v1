import sqlite3

# Connect to database
conn = sqlite3.connect('data/trading_bot.db')
cursor = conn.cursor()

print('=' * 80)
print('📊 TRADES DATA (00:29 - 01:04)')
print('=' * 80)

# Get all today's trades
cursor.execute("""
    SELECT trade_id, symbol, direction, entry_price, exit_price, pnl, close_time 
    FROM trades 
    WHERE close_time LIKE '2025-12-13%'
    AND status='closed'
    ORDER BY close_time
""")

all_trades = cursor.fetchall()

# Filter by time
filtered_trades = []
for trade in all_trades:
    close_time_str = trade[6]
    time_part = close_time_str.split('T')[1].split('.')[0]
    hour, minute, _ = map(int, time_part.split(':'))
    
    if (hour == 0 and minute >= 29) or (hour == 1 and minute <= 4):
        filtered_trades.append(trade)

print(f'\n✅ Found {len(filtered_trades)} trades\n')

total_profit = 0
total_loss = 0
wins = 0
losses = 0

for i, row in enumerate(filtered_trades, 1):
    trade_id, symbol, direction, entry, exit_val, pnl, close_time = row
    
    time_str = close_time.split('T')[1].split('.')[0]
    status_icon = "💰" if pnl > 0 else "❌"
    
    print(f'{i}. {status_icon} Trade #{trade_id}')
    print(f'   {symbol} {direction.upper()} @ {time_str}')
    print(f'   Entry: {entry} → Exit: {exit_val}')
    print(f'   PnL: ${pnl:.2f}')
    print()
    
    if pnl > 0:
        total_profit += pnl
        wins += 1
    else:
        total_loss += pnl
        losses += 1

net_pnl = total_profit + total_loss

print('=' * 80)
print('📈 SUMMARY (00:29 - 01:04):')
print('=' * 80)
print(f'💰 Total Profit: ${total_profit:.2f}')
print(f'❌ Total Loss: ${total_loss:.2f}')
print(f'📊 Net P&L: ${net_pnl:.2f}')
print(f'🎯 Trades: {wins} wins, {losses} losses')
if wins + losses > 0:
    print(f'📈 Win Rate: {(wins/(wins+losses)*100):.1f}%')
print('=' * 80)

conn.close()
