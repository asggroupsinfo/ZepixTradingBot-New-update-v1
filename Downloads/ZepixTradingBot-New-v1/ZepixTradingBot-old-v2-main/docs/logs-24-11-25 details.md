Microsoft Windows [Version 10.0.20348.4294]
(c) Microsoft Corporation. All rights reserved.

C:\Users\Administrator>cd ZepixTradingBot-New-v4

C:\Users\Administrator\ZepixTradingBot-New-v4>python src/main.py --host 0.0.0.0 --port 80
[LOGGING CONFIG] Loaded saved log level: INFO
[LOGGING CONFIG] Loaded trading_debug: False
Config loaded - MT5 Login: 308646228, Server: XMGlobal-MT5 6
[OK] Dependencies set immediately in TelegramBot
==================================================
ZEPIX TRADING BOT v2.0
==================================================
Starting server on 0.0.0.0:80
Features enabled:
+ Fixed lot sizes
+ Re-entry system
+ SL hunting protection
+ 1:1.5 Risk-Reward
+ Progressive SL reduction
==================================================
←[32mINFO←[0m:     Started server process [←[36m1140←[0m]
←[32mINFO←[0m:     Waiting for application startup.
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1mhttp://0.0.0.0:80←[0m (Press CTRL+C to quit)
======================================================================
STARTING ZEPIX TRADING BOT v2.0
======================================================================
Initializing components...
SUCCESS: MT5 connection established
Account Balance: $9264.90
Account: 308646228 | Server: XMGlobal-MT5 6
SUCCESS: Trend manager set in Telegram bot
SUCCESS: Trading engine initialized successfully
SUCCESS: Price monitor service started
SUCCESS: Profit booking manager initialized
[OK] Trade monitor started
[OK] Telegram polling thread started
SUCCESS: Telegram bot polling started
DEBUG: handle_dashboard called with message: {'message_id': 8534}
DEBUG: Sending dashboard, message_id=8534
DEBUG: _send_dashboard called, message_id=None
DEBUG: Dashboard sent successfully, message_id=8535
DEBUG: Dashboard sent successfully with message_id=8535
DEBUG: Parsed param - type: mode, command: simulation_mode, value: status
🛑 [PARAM SELECTION] START - param_type=mode, value=status, command=simulation_mode
[PARAM SELECTION] Stored param: mode=status, All params: {'mode': 'status'}
[PARAM SELECTION] Final stored params after preservation: {'mode': 'status'}
[PARAM SELECTION] All params collected. Final params: {'mode': 'status'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: simulation_mode
[CONFIRMATION] Showing confirmation for simulation_mode with params: {'mode': 'status'}
[CONFIRMATION] Confirm button callback: execute_simulation_mode
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=simulation_mode, Params={'mode': 'status'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: simulation_mode with params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'simulation_mode' with params: {'mode': 'status'}
[VALIDATE] Required params for simulation_mode: ['mode']
[VALIDATE] Validating param 'mode' with value: status
[VALIDATE PARAM] Validating 'mode' = 'status'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'validation': <function <lambda> at 0x000001DB2B583F60>}
[VALIDATE PARAM] Converted to lowercase: status -> status
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'mode' validation PASSED
[VALIDATE] Parameter 'mode' validation passed
[VALIDATE] All parameters validated successfully for simulation_mode
[MENU EXECUTION] User 2139792302 executing command: simulation_mode with params: {'mode': 'status'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_simulation_mode of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_simulation_mode of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for simulation_mode
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_simulation_mode of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'mode': 'status'}
📨 CALLING HANDLER with formatted_params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/simulation_mode status', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'mode': 'status'}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler simulation_mode returned (no exception)
🎯 HANDLER RETURNED: Command simulation_mode completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command simulation_mode executed successfully
✅ EXECUTION SUCCESS: simulation_mode
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for simulation_mode
[MENU EXECUTION] Returning True for simulation_mode
DEBUG: Parsed param - type: mode, command: simulation_mode, value: off
🛑 [PARAM SELECTION] START - param_type=mode, value=off, command=simulation_mode
[PARAM SELECTION] Stored param: mode=off, All params: {'mode': 'off'}
[PARAM SELECTION] Final stored params after preservation: {'mode': 'off'}
[PARAM SELECTION] All params collected. Final params: {'mode': 'off'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: simulation_mode
[CONFIRMATION] Showing confirmation for simulation_mode with params: {'mode': 'off'}
[CONFIRMATION] Confirm button callback: execute_simulation_mode
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=simulation_mode, Params={'mode': 'off'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: simulation_mode with params: {'mode': 'off'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'simulation_mode' with params: {'mode': 'off'}
[VALIDATE] Required params for simulation_mode: ['mode']
[VALIDATE] Validating param 'mode' with value: off
[VALIDATE PARAM] Validating 'mode' = 'off'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'validation': <function <lambda> at 0x000001DB2B583F60>}
[VALIDATE PARAM] Converted to lowercase: off -> off
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'mode' validation PASSED
[VALIDATE] Parameter 'mode' validation passed
[VALIDATE] All parameters validated successfully for simulation_mode
[MENU EXECUTION] User 2139792302 executing command: simulation_mode with params: {'mode': 'off'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_simulation_mode of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_simulation_mode of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for simulation_mode
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_simulation_mode of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'mode': 'off'}
📨 CALLING HANDLER with formatted_params: {'mode': 'off'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/simulation_mode off', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'mode': 'off'}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler simulation_mode returned (no exception)
🎯 HANDLER RETURNED: Command simulation_mode completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command simulation_mode executed successfully
✅ EXECUTION SUCCESS: simulation_mode
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for simulation_mode
[MENU EXECUTION] Returning True for simulation_mode
DEBUG: handle_dashboard called with message: {'message_id': 8535}
DEBUG: Sending dashboard, message_id=8535
DEBUG: _send_dashboard called, message_id=None
DEBUG: Dashboard sent successfully, message_id=8540
DEBUG: Dashboard sent successfully with message_id=8540
WARNING: Telegram API error: Status 400, Response: {"ok":false,"error_code":400,"description":"Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 68"}
WARNING: Telegram API error: Status 400, Response: {"ok":false,"error_code":400,"description":"Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 68"}
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=status, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: status with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'status' with params: {}
[VALIDATE] Required params for status: []
[VALIDATE] All parameters validated successfully for status
[MENU EXECUTION] User 2139792302 executing command: status with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B67B740>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B67B740> is callable
[MENU EXECUTION] About to call handler for status
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B67B740>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler status returned (no exception)
🎯 HANDLER RETURNED: Command status completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command status executed successfully
✅ EXECUTION SUCCESS: status
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for status
[MENU EXECUTION] Returning True for status
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=show_trends, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: show_trends with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'show_trends' with params: {}
[VALIDATE] Required params for show_trends: []
[VALIDATE] All parameters validated successfully for show_trends
[MENU EXECUTION] User 2139792302 executing command: show_trends with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A45E0>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A45E0> is callable
[MENU EXECUTION] About to call handler for show_trends
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A45E0>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler show_trends returned (no exception)
🎯 HANDLER RETURNED: Command show_trends completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command show_trends executed successfully
✅ EXECUTION SUCCESS: show_trends
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for show_trends
[MENU EXECUTION] Returning True for show_trends
DEBUG: Parsed param - type: symbol, command: set_trend, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_trend
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_trend, value: 5m
🛑 [PARAM SELECTION] START - param_type=timeframe, value=5m, command=set_trend
[PARAM SELECTION] Stored param: timeframe=5m, All params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '5m'}
🔄 [PARAM SELECTION] More parameters needed. Next param: trend
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: trend, command: set_trend, value: BEARISH
🛑 [PARAM SELECTION] START - param_type=trend, value=BEARISH, command=set_trend
[PARAM SELECTION] Stored param: trend=BEARISH, All params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_trend
[CONFIRMATION] Showing confirmation for set_trend with params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
[CONFIRMATION] Confirm button callback: execute_set_trend
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=set_trend, Params={'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: set_trend with params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'set_trend' with params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
[VALIDATE] Required params for set_trend: ['symbol', 'timeframe', 'trend']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x000001DB2B5831A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 5m
[VALIDATE PARAM] Validating 'timeframe' = '5m'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['1m', '5m', '15m', '1h', '4h', '1d'], 'validation': <function <lambda> at 0x000001DB2B583380>}
[VALIDATE PARAM] Converted to lowercase: 5m -> 5m
[VALIDATE PARAM] Checking valid_values: ['1m', '5m', '15m', '1h', '4h', '1d']
[VALIDATE PARAM] Value '5m' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] Validating param 'trend' with value: BEARISH
[VALIDATE PARAM] Validating 'trend' = 'BEARISH'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO'], 'validation': <function <lambda> at 0x000001DB2B583880>}
[VALIDATE PARAM] Converted to uppercase: BEARISH -> BEARISH
[VALIDATE PARAM] Checking valid_values: ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO']
[VALIDATE PARAM] Value 'BEARISH' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'trend' validation PASSED
[VALIDATE] Parameter 'trend' validation passed
[VALIDATE] All parameters validated successfully for set_trend
[MENU EXECUTION] User 2139792302 executing command: set_trend with params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_set_trend of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_set_trend of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for set_trend
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_set_trend of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
📨 CALLING HANDLER with formatted_params: {'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/set_trend XAUUSD 5m BEARISH', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'symbol': 'XAUUSD', 'timeframe': '5m', 'trend': 'BEARISH'}
SUCCESS: Trend updated: XAUUSD 5m -> BEARISH (MANUAL)
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler set_trend returned (no exception)
🎯 HANDLER RETURNED: Command set_trend completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command set_trend executed successfully
✅ EXECUTION SUCCESS: set_trend
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for set_trend
[MENU EXECUTION] Returning True for set_trend
DEBUG: Parsed param - type: symbol, command: set_auto, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_auto
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_auto, value: 5m
🛑 [PARAM SELECTION] START - param_type=timeframe, value=5m, command=set_auto
[PARAM SELECTION] Stored param: timeframe=5m, All params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '5m'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '5m'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_auto
[CONFIRMATION] Showing confirmation for set_auto with params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
[CONFIRMATION] Confirm button callback: execute_set_auto
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=set_auto, Params={'symbol': 'XAUUSD', 'timeframe': '5m'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: set_auto with params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'set_auto' with params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
[VALIDATE] Required params for set_auto: ['symbol', 'timeframe']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x000001DB2B5831A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 5m
[VALIDATE PARAM] Validating 'timeframe' = '5m'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['1m', '5m', '15m', '1h', '4h', '1d'], 'validation': <function <lambda> at 0x000001DB2B583380>}
[VALIDATE PARAM] Converted to lowercase: 5m -> 5m
[VALIDATE PARAM] Checking valid_values: ['1m', '5m', '15m', '1h', '4h', '1d']
[VALIDATE PARAM] Value '5m' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] All parameters validated successfully for set_auto
[MENU EXECUTION] User 2139792302 executing command: set_auto with params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_set_auto of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_set_auto of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for set_auto
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_set_auto of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
📨 CALLING HANDLER with formatted_params: {'symbol': 'XAUUSD', 'timeframe': '5m'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/set_auto XAUUSD 5m', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'symbol': 'XAUUSD', 'timeframe': '5m'}
SUCCESS: Mode set to AUTO for XAUUSD 5m
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler set_auto returned (no exception)
🎯 HANDLER RETURNED: Command set_auto completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command set_auto executed successfully
✅ EXECUTION SUCCESS: set_auto
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for set_auto
[MENU EXECUTION] Returning True for set_auto
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=trend_matrix, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: trend_matrix with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'trend_matrix' with params: {}
[VALIDATE] Required params for trend_matrix: []
[VALIDATE] All parameters validated successfully for trend_matrix
[MENU EXECUTION] User 2139792302 executing command: trend_matrix with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A47C0>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A47C0> is callable
[MENU EXECUTION] About to call handler for trend_matrix
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A47C0>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler trend_matrix returned (no exception)
🎯 HANDLER RETURNED: Command trend_matrix completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command trend_matrix executed successfully
✅ EXECUTION SUCCESS: trend_matrix
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for trend_matrix
[MENU EXECUTION] Returning True for trend_matrix
DEBUG: Parsed param - type: mode, command: tp_system, value: status
🛑 [PARAM SELECTION] START - param_type=mode, value=status, command=tp_system
[PARAM SELECTION] Stored param: mode=status, All params: {'mode': 'status'}
[PARAM SELECTION] Final stored params after preservation: {'mode': 'status'}
[PARAM SELECTION] All params collected. Final params: {'mode': 'status'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: tp_system
[CONFIRMATION] Showing confirmation for tp_system with params: {'mode': 'status'}
[CONFIRMATION] Confirm button callback: execute_tp_system
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=tp_system, Params={'mode': 'status'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: tp_system with params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'tp_system' with params: {'mode': 'status'}
[VALIDATE] Required params for tp_system: ['mode']
[VALIDATE] Validating param 'mode' with value: status
[VALIDATE PARAM] Validating 'mode' = 'status'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'validation': <function <lambda> at 0x000001DB2B583F60>}
[VALIDATE PARAM] Converted to lowercase: status -> status
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'mode' validation PASSED
[VALIDATE] Parameter 'mode' validation passed
[VALIDATE] All parameters validated successfully for tp_system
[MENU EXECUTION] User 2139792302 executing command: tp_system with params: {'mode': 'status'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_tp_system of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_tp_system of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for tp_system
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_tp_system of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'mode': 'status'}
📨 CALLING HANDLER with formatted_params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/tp_system status', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'mode': 'status'}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler tp_system returned (no exception)
🎯 HANDLER RETURNED: Command tp_system completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command tp_system executed successfully
✅ EXECUTION SUCCESS: tp_system
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for tp_system
[MENU EXECUTION] Returning True for tp_system
DEBUG: Parsed param - type: mode, command: sl_hunt, value: status
🛑 [PARAM SELECTION] START - param_type=mode, value=status, command=sl_hunt
[PARAM SELECTION] Stored param: mode=status, All params: {'mode': 'status'}
[PARAM SELECTION] Final stored params after preservation: {'mode': 'status'}
[PARAM SELECTION] All params collected. Final params: {'mode': 'status'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: sl_hunt
[CONFIRMATION] Showing confirmation for sl_hunt with params: {'mode': 'status'}
[CONFIRMATION] Confirm button callback: execute_sl_hunt
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=sl_hunt, Params={'mode': 'status'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: sl_hunt with params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'sl_hunt' with params: {'mode': 'status'}
[VALIDATE] Required params for sl_hunt: ['mode']
[VALIDATE] Validating param 'mode' with value: status
[VALIDATE PARAM] Validating 'mode' = 'status'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'validation': <function <lambda> at 0x000001DB2B583F60>}
[VALIDATE PARAM] Converted to lowercase: status -> status
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'mode' validation PASSED
[VALIDATE] Parameter 'mode' validation passed
[VALIDATE] All parameters validated successfully for sl_hunt
[MENU EXECUTION] User 2139792302 executing command: sl_hunt with params: {'mode': 'status'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_sl_hunt of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_sl_hunt of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for sl_hunt
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_sl_hunt of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'mode': 'status'}
📨 CALLING HANDLER with formatted_params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/sl_hunt status', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'mode': 'status'}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler sl_hunt returned (no exception)
🎯 HANDLER RETURNED: Command sl_hunt completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command sl_hunt executed successfully
✅ EXECUTION SUCCESS: sl_hunt
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for sl_hunt
[MENU EXECUTION] Returning True for sl_hunt
DEBUG: Parsed param - type: mode, command: exit_continuation, value: status
🛑 [PARAM SELECTION] START - param_type=mode, value=status, command=exit_continuation
[PARAM SELECTION] Stored param: mode=status, All params: {'mode': 'status'}
[PARAM SELECTION] Final stored params after preservation: {'mode': 'status'}
[PARAM SELECTION] All params collected. Final params: {'mode': 'status'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: exit_continuation
[CONFIRMATION] Showing confirmation for exit_continuation with params: {'mode': 'status'}
[CONFIRMATION] Confirm button callback: execute_exit_continuation
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=exit_continuation, Params={'mode': 'status'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: exit_continuation with params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'exit_continuation' with params: {'mode': 'status'}
[VALIDATE] Required params for exit_continuation: ['mode']
[VALIDATE] Validating param 'mode' with value: status
[VALIDATE PARAM] Validating 'mode' = 'status'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'validation': <function <lambda> at 0x000001DB2B583F60>}
[VALIDATE PARAM] Converted to lowercase: status -> status
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'mode' validation PASSED
[VALIDATE] Parameter 'mode' validation passed
[VALIDATE] All parameters validated successfully for exit_continuation
[MENU EXECUTION] User 2139792302 executing command: exit_continuation with params: {'mode': 'status'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_exit_continuation of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_exit_continuation of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for exit_continuation
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_exit_continuation of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'mode': 'status'}
📨 CALLING HANDLER with formatted_params: {'mode': 'status'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/exit_continuation status', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}, 'mode': 'status'}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler exit_continuation returned (no exception)
🎯 HANDLER RETURNED: Command exit_continuation completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command exit_continuation executed successfully
✅ EXECUTION SUCCESS: exit_continuation
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for exit_continuation
[MENU EXECUTION] Returning True for exit_continuation
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=view_risk_caps, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: view_risk_caps with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'view_risk_caps' with params: {}
[VALIDATE] Required params for view_risk_caps: []
[VALIDATE] All parameters validated successfully for view_risk_caps
[MENU EXECUTION] User 2139792302 executing command: view_risk_caps with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A5940>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A5940> is callable
[MENU EXECUTION] About to call handler for view_risk_caps
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A5940>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler view_risk_caps returned (no exception)
🎯 HANDLER RETURNED: Command view_risk_caps completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command view_risk_caps executed successfully
✅ EXECUTION SUCCESS: view_risk_caps
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for view_risk_caps
[MENU EXECUTION] Returning True for view_risk_caps
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=lot_size_status, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: lot_size_status with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'lot_size_status' with params: {}
[VALIDATE] Required params for lot_size_status: []
[VALIDATE] All parameters validated successfully for lot_size_status
[MENU EXECUTION] User 2139792302 executing command: lot_size_status with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A40E0>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A40E0> is callable
[MENU EXECUTION] About to call handler for lot_size_status
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A40E0>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler lot_size_status returned (no exception)
🎯 HANDLER RETURNED: Command lot_size_status completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command lot_size_status executed successfully
✅ EXECUTION SUCCESS: lot_size_status
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for lot_size_status
[MENU EXECUTION] Returning True for lot_size_status
WARNING: Telegram API error: Status 400, Response: {"ok":false,"error_code":400,"description":"Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 160"}
WARNING: Telegram API error: Status 400, Response: {"ok":false,"error_code":400,"description":"Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 160"}
WARNING: Telegram API error: Status 400, Response: {"ok":false,"error_code":400,"description":"Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 160"}
DEBUG: Parsed param - type: balance, command: set_risk_tier, value: 10000
🛑 [PARAM SELECTION] START - param_type=balance, value=10000, command=set_risk_tier
[PARAM SELECTION] Stored param: balance=10000, All params: {'balance': '10000'}
[PARAM SELECTION] Final stored params after preservation: {'balance': '10000'}
🔄 [PARAM SELECTION] More parameters needed. Next param: daily
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=profit_status, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: profit_status with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'profit_status' with params: {}
[VALIDATE] Required params for profit_status: []
[VALIDATE] All parameters validated successfully for profit_status
[MENU EXECUTION] User 2139792302 executing command: profit_status with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A6CA0>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A6CA0> is callable
[MENU EXECUTION] About to call handler for profit_status
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A6CA0>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/profit_status', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler profit_status returned (no exception)
🎯 HANDLER RETURNED: Command profit_status completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command profit_status executed successfully
✅ EXECUTION SUCCESS: profit_status
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for profit_status
[MENU EXECUTION] Returning True for profit_status
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=profit_sl_status, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: profit_sl_status with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'profit_sl_status' with params: {}
[VALIDATE] Required params for profit_sl_status: []
[VALIDATE] All parameters validated successfully for profit_sl_status
[MENU EXECUTION] User 2139792302 executing command: profit_sl_status with params: {}
✅ HANDLER FOUND: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A40E0>
✅ HANDLER VERIFIED: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A40E0> is callable
[MENU EXECUTION] About to call handler for profit_sl_status
[MENU EXECUTION] Handler function: <function CommandExecutor.execute_command.<locals>.<lambda> at 0x000001DB2B6A40E0>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
📨 MESSAGE CREATED: {'text': '/profit_sl_status', 'message_id': None, 'from': {'id': 2139792302}, 'chat': {'id': 2139792302}}
🎯 HANDLER RESULT: None
[MENU EXECUTION] Handler profit_sl_status returned (no exception)
🎯 HANDLER RETURNED: Command profit_sl_status completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command profit_sl_status executed successfully
✅ EXECUTION SUCCESS: profit_sl_status
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for profit_sl_status
[MENU EXECUTION] Returning True for profit_sl_status
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=health_status, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: health_status with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'health_status' with params: {}
[VALIDATE] Required params for health_status: []
[VALIDATE] All parameters validated successfully for health_status
[MENU EXECUTION] User 2139792302 executing command: health_status with params: {}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_health_status of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_health_status of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for health_status
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_health_status of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
🎯 HANDLER RESULT: True
[MENU EXECUTION] Handler health_status returned (no exception)
🎯 HANDLER RETURNED: Command health_status completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command health_status executed successfully
✅ EXECUTION SUCCESS: health_status
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for health_status
[MENU EXECUTION] Returning True for health_status
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=export_current_session, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: export_current_session with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'export_current_session' with params: {}
[VALIDATE] Required params for export_current_session: []
[VALIDATE] All parameters validated successfully for export_current_session
[MENU EXECUTION] User 2139792302 executing command: export_current_session with params: {}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_export_current_session of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_export_current_session of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for export_current_session
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_export_current_session of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
2025-11-23 21:50:04 - src.menu.command_executor - WARNING - send_document method not available in telegram_bot
🎯 HANDLER RESULT: True
[MENU EXECUTION] Handler export_current_session returned (no exception)
🎯 HANDLER RETURNED: Command export_current_session completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command export_current_session executed successfully
✅ EXECUTION SUCCESS: export_current_session
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for export_current_session
[MENU EXECUTION] Returning True for export_current_session
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
Webhook received: {
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "buy",
  "tf": "5m",
  "price": 4072.28,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'entry', 'symbol': 'XAUUSD', 'signal': 'buy', 'tf': '5m', 'price': 4072.28, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
[2025-11-23 23:10:01] 🔔 Processing entry alert | Symbol: XAUUSD, TF: 5m
[2025-11-23 23:10:01] ❌ Signal BULLISH doesn't match trend BEARISH
Webhook received: {
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "sell",
  "tf": "5m",
  "price": 4056.375,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'entry', 'symbol': 'XAUUSD', 'signal': 'sell', 'tf': '5m', 'price': 4056.375, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
[2025-11-24 01:10:01] 🔔 Processing entry alert | Symbol: XAUUSD, TF: 5m
[2025-11-24 01:10:01] 🔔 Trade execution starting | Symbol: XAUUSD, Direction: BEARISH
SUCCESS: Order placed successfully: Ticket #478384306
SUCCESS: Order placed successfully: Ticket #478384307
Auto-reconciliation: Position 478384307 already closed in MT5
SUCCESS: Position 478384307 already closed (not found in MT5)
Trade Closed: XAUUSD SELL
   Entry: 4056.37500 -> Close: 4052.27000
   Pips: 410.5 | PnL: $20.53
   Reason: MT5_AUTO_CLOSED
2025-11-24 01:11:59 - src.managers.profit_booking_manager - WARNING - Chain PROFIT_XAUUSD_4b3bcde1 has missing order: 478384307 (check 1/3)
2025-11-24 01:12:59 - src.managers.profit_booking_manager - WARNING - Marking chain PROFIT_XAUUSD_4b3bcde1 as STALE - all orders missing after 3 checks
Webhook received: {
  "type": "trend",
  "symbol": "XAUUSD",
  "signal": "bear",
  "tf": "15m",
  "price": 4054.565,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'trend', 'symbol': 'XAUUSD', 'signal': 'bear', 'tf': '15m', 'price': 4054.565, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
SUCCESS: Trend updated: XAUUSD 15m -> BEARISH (AUTO)
2025-11-24 01:15:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:15:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:16:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:17:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:18:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:19:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:20:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:21:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:22:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:23:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:24:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:25:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:26:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:27:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:28:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:29:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:30:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:31:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:32:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:33:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:34:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:35:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:36:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:37:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:38:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:39:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:40:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:41:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:42:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:43:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:44:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:45:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:46:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:47:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:48:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:49:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:50:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:51:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:52:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:53:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:54:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:55:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:56:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 01:57:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
Auto-reconciliation: Position 478384306 already closed in MT5
SUCCESS: Position 478384306 already closed (not found in MT5)
Trade Closed: XAUUSD SELL
   Entry: 4056.37500 -> Close: 4043.29500
   Pips: 1308.0 | PnL: $65.40
   Reason: MT5_AUTO_CLOSED
Webhook received: {
  "type": "trend",
  "symbol": "XAUUSD",
  "signal": "bear",
  "tf": "15m",
  "price": 4044.235,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'trend', 'symbol': 'XAUUSD', 'signal': 'bear', 'tf': '15m', 'price': 4044.235, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
SUCCESS: Trend updated: XAUUSD 15m -> BEARISH (AUTO)
Webhook received: {
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "buy",
  "tf": "5m",
  "price": 4053.51,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'entry', 'symbol': 'XAUUSD', 'signal': 'buy', 'tf': '5m', 'price': 4053.51, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
[2025-11-24 03:35:01] 🔔 Processing entry alert | Symbol: XAUUSD, TF: 5m
[2025-11-24 03:35:01] ❌ Signal BULLISH doesn't match trend BEARISH
[MENU EXECUTION] Empty params detected, attempting recovery...
🚨 DEBUG EXECUTE: Command=export_current_session, Params={}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: export_current_session with params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'export_current_session' with params: {}
[VALIDATE] Required params for export_current_session: []
[VALIDATE] All parameters validated successfully for export_current_session
[MENU EXECUTION] User 2139792302 executing command: export_current_session with params: {}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_export_current_session of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_export_current_session of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for export_current_session
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_export_current_session of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {}
📨 CALLING HANDLER with formatted_params: {}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
2025-11-24 07:17:22 - src.menu.command_executor - WARNING - send_document method not available in telegram_bot
🎯 HANDLER RESULT: True
[MENU EXECUTION] Handler export_current_session returned (no exception)
🎯 HANDLER RETURNED: Command export_current_session completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command export_current_session executed successfully
✅ EXECUTION SUCCESS: export_current_session
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for export_current_session
[MENU EXECUTION] Returning True for export_current_session
DEBUG: Parsed param - type: date, command: export_by_date, value: 2025-11-23
🛑 [PARAM SELECTION] START - param_type=date, value=2025-11-23, command=export_by_date
[PARAM SELECTION] Stored param: date=2025-11-23, All params: {'date': '2025-11-23'}
[PARAM SELECTION] Final stored params after preservation: {'date': '2025-11-23'}
[PARAM SELECTION] All params collected. Final params: {'date': '2025-11-23'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: export_by_date
[CONFIRMATION] Showing confirmation for export_by_date with params: {'date': '2025-11-23'}
[CONFIRMATION] Confirm button callback: execute_export_by_date
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
🚨 DEBUG EXECUTE: Command=export_by_date, Params={'date': '2025-11-23'}, User=2139792302
[MENU EXECUTION] User 2139792302 executing command: export_by_date with params: {'date': '2025-11-23'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': False, 'handler_complete': False, 'success': False}
[VALIDATE] Validating command 'export_by_date' with params: {'date': '2025-11-23'}
[VALIDATE] Required params for export_by_date: ['date']
[VALIDATE] Validating param 'date' with value: 2025-11-23
[VALIDATE PARAM] Validating 'date' = '2025-11-23'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'YYYY-MM-DD', 'valid_values': [{'value': '2025-11-23', 'display': '23-11-2025'}, {'value': '2025-11-22', 'display': '22-11-2025'}, {'value': '2025-11-21', 'display': '21-11-2025'}, {'value': '2025-11-20', 'display': '20-11-2025'}, {'value': '2025-11-19', 'display': '19-11-2025'}, {'value': '2025-11-18', 'display': '18-11-2025'}, {'value': '2025-11-17', 'display': '17-11-2025'}], 'validation': <function <lambda> at 0x000001DB2B5D47C0>}
[VALIDATE PARAM] Checking valid_values: [{'value': '2025-11-23', 'display': '23-11-2025'}, {'value': '2025-11-22', 'display': '22-11-2025'}, {'value': '2025-11-21', 'display': '21-11-2025'}, {'value': '2025-11-20', 'display': '20-11-2025'}, {'value': '2025-11-19', 'display': '19-11-2025'}, {'value': '2025-11-18', 'display': '18-11-2025'}, {'value': '2025-11-17', 'display': '17-11-2025'}]
[VALIDATE PARAM] Extracted values from dicts: ['2025-11-23', '2025-11-22', '2025-11-21', '2025-11-20', '2025-11-19', '2025-11-18', '2025-11-17']
[VALIDATE PARAM] Value '2025-11-23' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'date' validation PASSED
[VALIDATE] Parameter 'date' validation passed
[VALIDATE] All parameters validated successfully for export_by_date
[MENU EXECUTION] User 2139792302 executing command: export_by_date with params: {'date': '2025-11-23'}
✅ HANDLER FOUND: <bound method CommandExecutor._execute_export_by_date of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
✅ HANDLER VERIFIED: <bound method CommandExecutor._execute_export_by_date of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>> is callable
[MENU EXECUTION] About to call handler for export_by_date
[MENU EXECUTION] Handler function: <bound method CommandExecutor._execute_export_by_date of <src.menu.command_executor.CommandExecutor object at 0x000001DB2B578C80>>
[MENU EXECUTION] Formatted params: {'date': '2025-11-23'}
📨 CALLING HANDLER with formatted_params: {'date': '2025-11-23'}
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': False, 'success': False}
2025-11-24 07:17:58 - src.menu.command_executor - WARNING - send_document method not available in telegram_bot
🎯 HANDLER RESULT: True
[MENU EXECUTION] Handler export_by_date returned (no exception)
🎯 HANDLER RETURNED: Command export_by_date completed
📊 EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': False}
[MENU EXECUTION] [OK] Command export_by_date executed successfully
✅ EXECUTION SUCCESS: export_by_date
📊 FINAL EXECUTION STEPS: {'validation': True, 'handler_call': True, 'handler_complete': True, 'success': True}
[MENU EXECUTION] Marking execution as SUCCESS for export_by_date
[MENU EXECUTION] Returning True for export_by_date
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
Webhook received: {
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "buy",
  "tf": "15m",
  "price": 4063.995,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'entry', 'symbol': 'XAUUSD', 'signal': 'buy', 'tf': '15m', 'price': 4063.995, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
[2025-11-24 07:45:02] 🔔 Processing entry alert | Symbol: XAUUSD, TF: 15m
[2025-11-24 07:45:02] ❌ Signal BULLISH doesn't match trend BEARISH
Webhook received: {
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "sell",
  "tf": "5m",
  "price": 4067.025,
  "strategy": "ZepixPremium"
}
ALERT: Received alert: {'type': 'entry', 'symbol': 'XAUUSD', 'signal': 'sell', 'tf': '5m', 'price': 4067.025, 'strategy': 'ZepixPremium'}
SUCCESS: Alert validation successful
[2025-11-24 10:40:02] 🔔 Processing entry alert | Symbol: XAUUSD, TF: 5m
[2025-11-24 10:40:02] 🔔 Trade execution starting | Symbol: XAUUSD, Direction: BEARISH
SUCCESS: Order placed successfully: Ticket #478672265
SUCCESS: Order placed successfully: Ticket #478672266
Auto-reconciliation: Position 478672266 already closed in MT5
SUCCESS: Position 478672266 already closed (not found in MT5)
Trade Closed: XAUUSD SELL
   Entry: 4067.02500 -> Close: 4069.13500
   Pips: -211.0 | PnL: $-10.55
   Reason: MT5_AUTO_CLOSED
2025-11-24 10:42:29 - src.managers.profit_booking_manager - WARNING - Chain PROFIT_XAUUSD_96773477 has missing order: 478672266 (check 1/3)
2025-11-24 10:43:29 - src.managers.profit_booking_manager - WARNING - Marking chain PROFIT_XAUUSD_96773477 as STALE - all orders missing after 3 checks
2025-11-24 10:45:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:45:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:46:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:47:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:48:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:49:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:50:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
←[33mWARNING←[0m:  Invalid HTTP request received.
2025-11-24 10:51:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:51:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:52:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:53:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:54:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:55:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
←[33mWARNING←[0m:  Invalid HTTP request received.
2025-11-24 10:56:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:56:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:57:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:58:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 10:59:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:00:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:01:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:02:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:03:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:04:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:05:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:06:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:07:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:08:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:09:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:10:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:11:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:12:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:13:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:14:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:15:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:16:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:17:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:18:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:19:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:20:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:21:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:22:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:23:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:24:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:25:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:26:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:27:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:28:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:29:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:30:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:31:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:32:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:33:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:34:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:35:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:36:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:37:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:38:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:39:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:40:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:41:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:42:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:43:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:44:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:45:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:46:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:47:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:48:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:49:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:50:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:51:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:52:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:53:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:54:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:55:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:56:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:57:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:58:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 11:59:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:00:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:01:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:02:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:03:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:30 - asyncio - ERROR - Exception in callback _ProactorBasePipeTransport._call_connection_lost(None)
handle: <Handle _ProactorBasePipeTransport._call_connection_lost(None)>
Traceback (most recent call last):
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\events.py", line 88, in _run
    self._context.run(self._callback, *self._args)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\proactor_events.py", line 165, in _call_connection_lost
    self._sock.shutdown(socket.SHUT_RDWR)
ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
2025-11-24 12:04:31 - asyncio - ERROR - Exception in callback _ProactorBasePipeTransport._call_connection_lost(None)
handle: <Handle _ProactorBasePipeTransport._call_connection_lost(None)>
Traceback (most recent call last):
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\events.py", line 88, in _run
    self._context.run(self._callback, *self._args)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\proactor_events.py", line 165, in _call_connection_lost
    self._sock.shutdown(socket.SHUT_RDWR)
ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
2025-11-24 12:04:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:04:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:05:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:06:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:07:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:08:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:09:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:10:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:11:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:12:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:13:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:14:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:15:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:16:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:17:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:18:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:19:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:20:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:21:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:22:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:23:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:24:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:25:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:26:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:27:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:28:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:29:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:30:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:31:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:32:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:33:55 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:00 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:05 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:10 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:15 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:20 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:25 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:30 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:35 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:40 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:45 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
2025-11-24 12:34:50 - src.managers.timeframe_trend_manager - WARNING - 🔍 [ALIGNMENT_CHECK] XAUUSD ZepixPremium: ❌ Unknown logic
←[33mWARNING←[0m:  Invalid HTTP request received.
←[33mWARNING←[0m:  Invalid HTTP request received.
Auto-reconciliation: Position 478672265 already closed in MT5
SUCCESS: Position 478672265 already closed (not found in MT5)
Trade Closed: XAUUSD SELL
   Entry: 4067.02500 -> Close: 4075.00500
   Pips: -798.0 | PnL: $-39.90
   Reason: MT5_AUTO_CLOSED
DEBUG: handle_dashboard called with message: {'message_id': 8566}
DEBUG: Sending dashboard, message_id=8566
DEBUG: _send_dashboard called, message_id=None
DEBUG: Dashboard sent successfully, message_id=8567
DEBUG: Dashboard sent successfully with message_id=8567
2025-11-24 18:22:08 - asyncio - ERROR - Exception in callback _ProactorReadPipeTransport._loop_reading(<_OverlappedF...ed result=133>)
handle: <Handle _ProactorReadPipeTransport._loop_reading(<_OverlappedF...ed result=133>)>
Traceback (most recent call last):
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\events.py", line 88, in _run
    self._context.run(self._callback, *self._args)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\proactor_events.py", line 325, in _loop_reading
    self._data_received(data, length)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\asyncio\proactor_events.py", line 274, in _data_received
    self._protocol.data_received(data)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 182, in data_received
    self.handle_events()
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 191, in handle_events
    self.send_400_response(msg)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 301, in send_400_response
    output = self.conn.send(event)
             ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\h11\_connection.py", line 538, in send
    data_list = self.send_with_data_passthrough(event)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\h11\_connection.py", line 563, in send_with_data_passthrough
    self._process_event(self.our_role, event)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\h11\_connection.py", line 284, in _process_event
    self._cstate.process_event(role, type(event), server_switch_event)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\h11\_state.py", line 291, in process_event
    self._fire_event_triggered_transitions(role, _event_type)
  File "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\h11\_state.py", line 309, in _fire_event_triggered_transitions
    raise LocalProtocolError(
h11._util.LocalProtocolError: can't handle event type Response when role=SERVER and state=CLOSED
