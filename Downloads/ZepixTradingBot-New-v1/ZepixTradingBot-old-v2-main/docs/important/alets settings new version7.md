🎯 COMPLETE TRADINGVIEW ALERT SETUP - 18 ALERTS
Updated: Dec 02, 2025
Bot Compatible: Zepix Trading Bot v7

📋 QUICK SUMMARY
Category	Count	Priority	Purpose
BIAS	4	🔴 CRITICAL	LOGIC3 foundation (1H entries)
TREND	6	🔴 CRITICAL	LOGIC1/2 foundation
ENTRY	6	🔴 CRITICAL	Trade execution signals
EXIT	2	🟡 RECOMMENDED	Early exit warnings
TOTAL	18		
🌐 WEBHOOK CONFIGURATION
URL: http://3.110.221.62/webhook
Method: POST
Content-Type: application/json
All Alerts Must Use:

Frequency: Once Per Bar Close
Expiration: Open-ended (or 1 bar)
Webhook URL: http://3.110.221.62/webhook
1️⃣ BIAS ALERTS (4 alerts) - 🔴 CRITICAL
Purpose: Foundation for LOGIC3 (1H entry signals)
Indicator: [Screener] Full Bullish Alert / [Screener] Full Bearish Alert

1D Bullish BIAS
Chart: XAUUSD, 1D timeframe
Indicator Condition: [Screener] Full Bullish Alert
Alert Name: 1D BIAS BULL - XAUUSD
Message:

{"type": "bias", "symbol": "{{ticker}}", "signal": "bull", "tf": "1d", "price": {{close}}, "strategy": "ZepixPremium"}
1D Bearish BIAS
Chart: XAUUSD, 1D timeframe
Indicator Condition: [Screener] Full Bearish Alert
Alert Name: 1D BIAS BEAR - XAUUSD
Message:

{"type": "bias", "symbol": "{{ticker}}", "signal": "bear", "tf": "1d", "price": {{close}}, "strategy": "ZepixPremium"}
1H Bullish BIAS
Chart: XAUUSD, 1H timeframe
Indicator Condition: [Screener] Full Bullish Alert
Alert Name: 1H BIAS BULL - XAUUSD
Message:

{"type": "bias", "symbol": "{{ticker}}", "signal": "bull", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
1H Bearish BIAS
Chart: XAUUSD, 1H timeframe
Indicator Condition: [Screener] Full Bearish Alert
Alert Name: 1H BIAS BEAR - XAUUSD
Message:

{"type": "bias", "symbol": "{{ticker}}", "signal": "bear", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
2️⃣ TREND ALERTS (6 alerts) - 🔴 CRITICAL
Purpose: Foundation for LOGIC1/2 (5M and 15M entries)
Indicator: [Screener] Full Bullish Alert / [Screener] Full Bearish Alert

1H Bullish TREND
Chart: XAUUSD, 1H timeframe
Indicator Condition: [Screener] Full Bullish Alert
Alert Name: 1H TREND BULL - XAUUSD
Message:

{"type": "trend", "symbol": "{{ticker}}", "signal": "bull", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
1H Bearish TREND
Chart: XAUUSD, 1H timeframe
Indicator Condition: [Screener] Full Bearish Alert
Alert Name: 1H TREND BEAR - XAUUSD
Message:

{"type": "trend", "symbol": "{{ticker}}", "signal": "bear", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
15M Bullish TREND
Chart: XAUUSD, 15M timeframe
Indicator Condition: [Screener] Full Bullish Alert
Alert Name: 15M TREND BULL - XAUUSD
Message:

{"type": "trend", "symbol": "{{ticker}}", "signal": "bull", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
15M Bearish TREND
Chart: XAUUSD, 15M timeframe
Indicator Condition: [Screener] Full Bearish Alert
Alert Name: 15M TREND BEAR - XAUUSD
Message:

{"type": "trend", "symbol": "{{ticker}}", "signal": "bear", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
5M Bullish TREND (Optional)
Chart: XAUUSD, 5M timeframe
Indicator Condition: [Screener] Full Bullish Alert
Alert Name: 5M TREND BULL - XAUUSD
Message:

{"type": "trend", "symbol": "{{ticker}}", "signal": "bull", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
5M Bearish TREND (Optional)
Chart: XAUUSD, 5M timeframe
Indicator Condition: [Screener] Full Bearish Alert
Alert Name: 5M TREND BEAR - XAUUSD
Message:

{"type": "trend", "symbol": "{{ticker}}", "signal": "bear", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
3️⃣ ENTRY ALERTS (6 alerts) - 🔴 CRITICAL
Purpose: Trade execution signals
Indicator: Zepix Premium - Signals and Overlays Zero Lag Overlays

5M BUY Entry (LOGIC1)
Chart: XAUUSD, 5M timeframe
Indicator Condition: Bullish Entry Signals
Alert Name: 5M ENTRY BUY - XAUUSD
Message:

{"type": "entry", "symbol": "{{ticker}}", "signal": "buy", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
5M SELL Entry (LOGIC1)
Chart: XAUUSD, 5M timeframe
Indicator Condition: Bearish Entry Signals
Alert Name: 5M ENTRY SELL - XAUUSD
Message:

{"type": "entry", "symbol": "{{ticker}}", "signal": "sell", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
15M BUY Entry (LOGIC2)
Chart: XAUUSD, 15M timeframe
Indicator Condition: Bullish Entry Signals
Alert Name: 15M ENTRY BUY - XAUUSD
Message:

{"type": "entry", "symbol": "{{ticker}}", "signal": "buy", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
15M SELL Entry (LOGIC2)
Chart: XAUUSD, 15M timeframe
Indicator Condition: Bearish Entry Signals
Alert Name: 15M ENTRY SELL - XAUUSD
Message:

{"type": "entry", "symbol": "{{ticker}}", "signal": "sell", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
1H BUY Entry (LOGIC3)
Chart: XAUUSD, 1H timeframe
Indicator Condition: Bullish Entry Signals
Alert Name: 1H ENTRY BUY - XAUUSD
Message:

{"type": "entry", "symbol": "{{ticker}}", "signal": "buy", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
1H SELL Entry (LOGIC3)
Chart: XAUUSD, 1H timeframe
Indicator Condition: Bearish Entry Signals
Alert Name: 1H ENTRY SELL - XAUUSD
Message:

{"type": "entry", "symbol": "{{ticker}}", "signal": "sell", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
4️⃣ EXIT ALERTS (2 alerts) - 🟡 RECOMMENDED
Purpose: Early exit warnings before reversal
Indicator: Zepix Premium - Signals and Overlays Zero Lag Overlays

5M Bullish EXIT
Chart: XAUUSD, 5M timeframe
Indicator Condition: Bullish Exit Appeared
Alert Name: 5M EXIT BULL - XAUUSD
Message:

{"type": "exit", "symbol": "{{ticker}}", "signal": "bull", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
5M Bearish EXIT
Chart: XAUUSD, 5M timeframe
Indicator Condition: Bearish Exit Appeared
Alert Name: 5M EXIT BEAR - XAUUSD
Message:

{"type": "exit", "symbol": "{{ticker}}", "signal": "bear", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
⚙️ TRADINGVIEW ALERT SETTINGS (All Alerts)
✅ Condition: [As specified above]
✅ Options: Once Per Bar Close
✅ Expiration time: Open-ended
✅ Alert actions:
   ✅ Webhook URL: http://3.110.221.62/webhook
   ❌ Notify on App: OFF
   ❌ Show popup: OFF
   ❌ Send email: OFF
   ❌ Play sound: OFF
✅ Alert name: [As specified above]
✅ Message: [JSON as specified above]
📊 INDICATOR MAPPING GUIDE
For BIAS and TREND Alerts:
Use Indicator: Zepix Premium - Signals and Overlays Zero Lag Overlays
→ Section: Screener
→ Conditions:

[Screener] Full Bullish Alert → BULL signal
[Screener] Full Bearish Alert → BEAR signal
For ENTRY Alerts:
Use Indicator: Zepix Premium - Signals and Overlays Zero Lag Overlays
→ Section: Entry Signals
→ Conditions:

Bullish Entry Signals → BUY signal
Bearish Entry Signals → SELL signal
For EXIT Alerts:
Use Indicator: Zepix Premium - Signals and Overlays Zero Lag Overlays
→ Section: Exit Signals
→ Conditions:

Bullish Exit Appeared → BULL exit
Bearish Exit Appeared → BEAR exit
🎯 BOT LOGIC REQUIREMENTS
LOGIC1 (5M Entries):
Required Alignment: 1H TREND + 15M TREND
Entry: 5M entry signal matches aligned direction
LOGIC2 (15M Entries):
Required Alignment: 1H TREND + 15M TREND
Entry: 15M entry signal matches aligned direction
LOGIC3 (1H Entries):
Required Alignment: 1D BIAS + 1H BIAS/TREND
Entry: 1H entry signal matches aligned direction
✅ VERIFICATION CHECKLIST
After setting up alerts:

 BIAS Count: 4 alerts (1D BULL/BEAR, 1H BULL/BEAR)
 TREND Count: 6 alerts (1H BULL/BEAR, 15M BULL/BEAR, 5M optional)
 ENTRY Count: 6 alerts (5M/15M/1H BUY/SELL)
 Webhook URL: Correct in ALL alerts
 Frequency: "Once Per Bar Close" in ALL alerts
 JSON Format: No typos, proper {{ticker}} and {{close}} placeholders
🔧 TROUBLESHOOTING
Alert Not Triggering:
Check indicator is added to chart
Verify timeframe matches alert timeframe
Confirm "Once Per Bar Close" is selected
Bot Not Receiving:
Test webhook: curl -X POST http://3.110.221.62/webhook -d '{"type":"test"}'
Check bot logs for "Webhook received"
Verify IP address is correct
Alert Triggers But No Trade:
Check trend alignment via /trend_matrix
Verify all required timeframe trends are set
Ensure trends are in AUTO mode, not MANUAL
📝 SETUP PRIORITY
Phase 1 (Minimum for Testing):
1. Add 4 BIAS alerts (1D, 1H)
2. Add 6 TREND alerts (1H, 15M)
3. Add 2 ENTRY alerts (1H BUY/SELL for LOGIC3 test)
Total: 12 alerts
Phase 2 (Full Production):
4. Add remaining 4 ENTRY alerts (5M, 15M)
5. Add 2 EXIT alerts (5M)
Total: 18 alerts
Document Version: 2.0
Last Updated: Dec 02, 2025
Compatible With: Zepix Trading Bot v7