# Telegram Commands Test Checklist

## All 47 Telegram Commands to Test

### Basic Commands (3)
- [ ] `/start` - Bot information
- [ ] `/status` - System status  
- [ ] `/help` - Command list

### Trading Logic Commands (4)
- [ ] `/logic_status` - All 3 trading logics status
- [ ] `/logic1 [on/off/status]` - Logic 1 control
- [ ] `/logic2 [on/off/status]` - Logic 2 control
- [ ] `/logic3 [on/off/status]` - Logic 3 control

### Re-entry System Commands (3)
- [ ] `/tp_system [on/off/status]` - TP re-entry system
- [ ] `/sl_hunt [on/off/status]` - SL hunt system
- [ ] `/exit_continuation [on/off/status]` - Exit continuation

### Profit Booking Commands (2)
- [ ] `/profit_status` - Profit booking chains status
- [ ] `/profit_booking [on/off]` - Enable/disable profit booking

### Dual Order Commands (1)
- [ ] `/dual_order_status` - Dual order system status

### Risk Management Commands (4)
- [ ] `/risk_status` - Risk management status
- [ ] `/clear_loss_data` - Clear loss limits
- [ ] `/daily_loss_limit [amount]` - Set daily loss limit
- [ ] `/lifetime_loss_limit [amount]` - Set lifetime loss limit

### Configuration Commands (10+)
- [ ] `/config` - Show configuration
- [ ] `/set_config [key] [value]` - Set configuration
- [ ] `/symbol_config [symbol]` - Symbol configuration
- [ ] `/sl_system [status]` - SL system status
- [ ] `/rr_ratio [ratio]` - Set risk-reward ratio
- [ ] `/lot_size [size]` - Set lot size
- [ ] `/account_tier` - Show account tier
- [ ] `/volatility [symbol]` - Show symbol volatility
- [ ] `/pip_size [symbol]` - Show pip size
- [ ] `/pip_value [symbol]` - Show pip value

### Trading Control Commands (4)
- [ ] `/pause` - Pause trading
- [ ] `/resume` - Resume trading
- [ ] `/trades` - List open trades
- [ ] `/close_all` - Close all trades

### Analytics Commands (5+)
- [ ] `/stats` - Trading statistics
- [ ] `/performance` - Performance metrics
- [ ] `/win_rate` - Win rate statistics
- [ ] `/profit_loss` - Profit/loss summary
- [ ] `/chain_stats` - Chain statistics

### System Commands (5+)
- [ ] `/restart` - Restart bot
- [ ] `/shutdown` - Shutdown bot
- [ ] `/logs` - View recent logs
- [ ] `/version` - Bot version
- [ ] `/uptime` - Bot uptime

### Additional Commands
- [ ] All other commands found in telegram_bot.py

## Test Procedure

1. Start bot: `python src/main.py --port 5000`
2. Open Telegram bot
3. Test each command one by one
4. Verify response is correct
5. Check for errors in logs
6. Mark as complete when verified

## Expected Results

- All commands should respond within 2 seconds
- No error messages in responses
- Commands should return expected data
- Invalid commands should show helpful error messages

