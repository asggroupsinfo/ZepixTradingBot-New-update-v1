Microsoft Windows [Version 10.0.20348.4294]
(c) Microsoft Corporation. All rights reserved.

C:\Users\Administrator>git clone https://github.com/asggroupsinfo/ZepixTradingBot-New-v10
Cloning into 'ZepixTradingBot-New-v10'...
remote: Enumerating objects: 7710, done.
remote: Counting objects: 100% (7710/7710), done.
remote: Compressing objects: 100% (5516/5516), done.
remote: Total 7710 (delta 2061), reused 7710 (delta 2061), pack-reused 0 (from 0)
Receiving objects: 100% (7710/7710), 43.73 MiB | 16.57 MiB/s, done.
Resolving deltas: 100% (2061/2061), done.

C:\Users\Administrator>cd ZepixTradingBot-New-v10

C:\Users\Administrator\ZepixTradingBot-New-v10>pip install -r requirements.txt
Requirement already satisfied: fastapi==0.104.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 1)) (0.104.1)
Requirement already satisfied: uvicorn==0.24.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 2)) (0.24.0)
Requirement already satisfied: python-multipart==0.0.6 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 3)) (0.0.6)
Requirement already satisfied: requests==2.31.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 4)) (2.31.0)
Requirement already satisfied: httpx==0.25.2 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 5)) (0.25.2)
Requirement already satisfied: pydantic==2.5.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 6)) (2.5.0)
Requirement already satisfied: pydantic-core==2.14.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 7)) (2.14.1)
Requirement already satisfied: python-dotenv==1.0.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 8)) (1.0.0)
Requirement already satisfied: aiohttp==3.9.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 9)) (3.9.1)
Requirement already satisfied: numpy==1.26.4 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 10)) (1.26.4)
Requirement already satisfied: MetaTrader5==5.0.5328 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 11)) (5.0.5328)
Requirement already satisfied: psutil==5.9.6 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 13)) (5.9.6)
Requirement already satisfied: anyio<4.0.0,>=3.7.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from fastapi==0.104.1->-r requirements.txt (line 1)) (3.7.1)
Requirement already satisfied: starlette<0.28.0,>=0.27.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from fastapi==0.104.1->-r requirements.txt (line 1)) (0.27.0)
Requirement already satisfied: typing-extensions>=4.8.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from fastapi==0.104.1->-r requirements.txt (line 1)) (4.15.0)
Requirement already satisfied: click>=7.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from uvicorn==0.24.0->-r requirements.txt (line 2)) (8.3.0)
Requirement already satisfied: h11>=0.8 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from uvicorn==0.24.0->-r requirements.txt (line 2)) (0.16.0)
Requirement already satisfied: charset-normalizer<4,>=2 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from requests==2.31.0->-r requirements.txt (line 4)) (3.4.4)
Requirement already satisfied: idna<4,>=2.5 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from requests==2.31.0->-r requirements.txt (line 4)) (3.11)
Requirement already satisfied: urllib3<3,>=1.21.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from requests==2.31.0->-r requirements.txt (line 4)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from requests==2.31.0->-r requirements.txt (line 4)) (2025.10.5)
Requirement already satisfied: httpcore==1.* in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx==0.25.2->-r requirements.txt (line 5)) (1.0.9)
Requirement already satisfied: sniffio in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx==0.25.2->-r requirements.txt (line 5)) (1.3.1)
Requirement already satisfied: annotated-types>=0.4.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from pydantic==2.5.0->-r requirements.txt (line 6)) (0.7.0)
Requirement already satisfied: attrs>=17.3.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from aiohttp==3.9.1->-r requirements.txt (line 9)) (25.4.0)
Requirement already satisfied: multidict<7.0,>=4.5 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from aiohttp==3.9.1->-r requirements.txt (line 9)) (6.7.0)
Requirement already satisfied: yarl<2.0,>=1.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from aiohttp==3.9.1->-r requirements.txt (line 9)) (1.22.0)
Requirement already satisfied: frozenlist>=1.1.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from aiohttp==3.9.1->-r requirements.txt (line 9)) (1.8.0)
Requirement already satisfied: aiosignal>=1.1.2 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from aiohttp==3.9.1->-r requirements.txt (line 9)) (1.4.0)
Requirement already satisfied: colorama in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from click>=7.0->uvicorn==0.24.0->-r requirements.txt (line 2)) (0.4.6)
Requirement already satisfied: propcache>=0.2.1 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from yarl<2.0,>=1.0->aiohttp==3.9.1->-r requirements.txt (line 9)) (0.4.1)

[notice] A new release of pip is available: 25.0.1 -> 25.3
[notice] To update, run: python.exe -m pip install --upgrade pip

C:\Users\Administrator\ZepixTradingBot-New-v10>python src/main.py --host 0.0.0.0 --port 80
[EVENT-LOOP] Set WindowsProactorEventLoopPolicy on Windows
[LOGGING CONFIG] Loaded saved log level: INFO
[LOGGING CONFIG] Loaded trading_debug: True
═══════════════════════════════════════
🚀 BOT STARTING - LOGGING LEVEL: INFO
═══════════════════════════════════════
2025-12-07 14:58:09 - __main__ - INFO - Bot starting with logging level: INFO
[LOGGING CONFIG] Loaded saved log level: INFO
[LOGGING CONFIG] Loaded trading_debug: True
[UNCAUGHT-EXCEPTION] ModuleNotFoundError: No module named 'pandas'
  File "C:\Users\Administrator\ZepixTradingBot-New-v10\src\main.py", line 167, in <module>
    from src.core.trading_engine import TradingEngine
  File "C:\Users\Administrator\ZepixTradingBot-New-v10\src\core\trading_engine.py", line 13, in <module>
    from src.managers.reentry_manager import ReEntryManager
  File "C:\Users\Administrator\ZepixTradingBot-New-v10\src\managers\reentry_manager.py", line 4, in <module>
    from src.utils.trend_analyzer import TrendAnalyzer
  File "C:\Users\Administrator\ZepixTradingBot-New-v10\src\utils\trend_analyzer.py", line 1, in <module>
    import pandas as pd

C:\Users\Administrator\ZepixTradingBot-New-v10>pip install pandas==2.1.4 python-telegram-bot==20.7
Collecting pandas==2.1.4
  Downloading pandas-2.1.4-cp312-cp312-win_amd64.whl.metadata (18 kB)
Collecting python-telegram-bot==20.7
  Downloading python_telegram_bot-20.7-py3-none-any.whl.metadata (15 kB)
Requirement already satisfied: numpy<2,>=1.26.0 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from pandas==2.1.4) (1.26.4)
Collecting python-dateutil>=2.8.2 (from pandas==2.1.4)
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting pytz>=2020.1 (from pandas==2.1.4)
  Downloading pytz-2025.2-py2.py3-none-any.whl.metadata (22 kB)
Collecting tzdata>=2022.1 (from pandas==2.1.4)
  Downloading tzdata-2025.2-py2.py3-none-any.whl.metadata (1.4 kB)
Requirement already satisfied: httpx~=0.25.2 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from python-telegram-bot==20.7) (0.25.2)
Requirement already satisfied: anyio in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx~=0.25.2->python-telegram-bot==20.7) (3.7.1)
Requirement already satisfied: certifi in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx~=0.25.2->python-telegram-bot==20.7) (2025.10.5)
Requirement already satisfied: httpcore==1.* in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx~=0.25.2->python-telegram-bot==20.7) (1.0.9)
Requirement already satisfied: idna in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx~=0.25.2->python-telegram-bot==20.7) (3.11)
Requirement already satisfied: sniffio in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpx~=0.25.2->python-telegram-bot==20.7) (1.3.1)
Requirement already satisfied: h11>=0.16 in c:\users\administrator\appdata\local\programs\python\python312\lib\site-packages (from httpcore==1.*->httpx~=0.25.2->python-telegram-bot==20.7) (0.16.0)
Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas==2.1.4)
  Downloading six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Downloading pandas-2.1.4-cp312-cp312-win_amd64.whl (10.5 MB)
   ---------------------------------------- 10.5/10.5 MB 108.9 MB/s eta 0:00:00
Downloading python_telegram_bot-20.7-py3-none-any.whl (552 kB)
   ---------------------------------------- 552.6/552.6 kB 18.2 MB/s eta 0:00:00
Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Downloading pytz-2025.2-py2.py3-none-any.whl (509 kB)
Downloading tzdata-2025.2-py2.py3-none-any.whl (347 kB)
Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Installing collected packages: pytz, tzdata, six, python-dateutil, python-telegram-bot, pandas
Successfully installed pandas-2.1.4 python-dateutil-2.9.0.post0 python-telegram-bot-20.7 pytz-2025.2 six-1.17.0 tzdata-2025.2

[notice] A new release of pip is available: 25.0.1 -> 25.3
[notice] To update, run: python.exe -m pip install --upgrade pip

C:\Users\Administrator\ZepixTradingBot-New-v10>python src/main.py --host 0.0.0.0 --port 80
[EVENT-LOOP] Set WindowsProactorEventLoopPolicy on Windows
[LOGGING CONFIG] Loaded saved log level: INFO
[LOGGING CONFIG] Loaded trading_debug: True
═══════════════════════════════════════
🚀 BOT STARTING - LOGGING LEVEL: INFO
═══════════════════════════════════════
2025-12-07 15:02:51 - __main__ - INFO - Bot starting with logging level: INFO
[LOGGING CONFIG] Loaded saved log level: INFO
[LOGGING CONFIG] Loaded trading_debug: True
Config loaded - MT5 Login: 308646228, Server: XMGlobal-MT5 6
2025-12-07 15:02:58 - src.managers.recovery_window_monitor - INFO - ✅ RecoveryWindowMonitor initialized
2025-12-07 15:02:58 - src.managers.profit_protection_manager - INFO -
Profit Protection Settings Loaded:
├─ Enabled: True
├─ Mode: ⚖️ BALANCED
├─ Multiplier: 6.0x
├─ Min Threshold: $20.0
├─ Order A: ON ✅
└─ Order B: ON ✅

2025-12-07 15:02:58 - src.managers.profit_protection_manager - INFO - ✅ ProfitProtectionManager initialized
2025-12-07 15:02:58 - src.managers.sl_reduction_optimizer - INFO -
SL Reduction Settings Loaded:
├─ Enabled: True
├─ Strategy: ⚖️ BALANCED
├─ Reduction: 30%
└─ Description: Recommended for most conditions

2025-12-07 15:02:58 - src.managers.sl_reduction_optimizer - INFO - ✅ SLReductionOptimizer initialized
✅ Fine-Tune managers initialized (Recovery Monitor, Profit Protection, SL Optimizer)
✅ Autonomous System Manager initialized
2025-12-07 15:02:58 - src.menu.fine_tune_menu_handler - INFO - ✅ FineTuneMenuHandler initialized (Compatible Mode)
✅ TelegramBot: Fine-Tune Menu Handler initialized
✅ TelegramBot: Re-entry Menu Handler initialized
✅ TelegramBot: Profit Booking Menu Handler initialized
[OK] Dependencies set immediately in TelegramBot
[INFO] Web server port 80 will be used if available
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
[UVICORN] Starting Uvicorn server...
[UVICORN] Starting Uvicorn with default settings...
←[32mINFO←[0m:     Started server process [←[36m7876←[0m]
←[32mINFO←[0m:     Waiting for application startup.
======================================================================
STARTING ZEPIX TRADING BOT v2.0
======================================================================
Initializing components...
2025-12-07 15:02:58 - src.menu.fine_tune_menu_handler - INFO - ✅ FineTuneMenuHandler initialized (Compatible Mode)
✅ TelegramBot: Fine-Tune Menu Handler initialized
✅ TelegramBot: Re-entry Menu Handler initialized
✅ TelegramBot: Profit Booking Menu Handler initialized
SUCCESS: MT5 connection established
Account Balance: $9243.59
Account: 308646228 | Server: XMGlobal-MT5 6
2025-12-07 15:03:17 - src.clients.telegram_bot - INFO - SUCCESS: Trend manager set in Telegram bot
2025-12-07 15:03:17 - src.core.trading_engine - INFO - 📋 [RE-ENTRY_CONFIG] Startup Configuration:
  SL Hunt Enabled: True
  TP Re-entry Enabled: True
  Exit Continuation Enabled: True
  Monitor Interval: 5s
  SL Hunt Offset: 1.0 pips
  TP Continuation Gap: 2.0 pips
  Max Chain Levels: 5
  SL Reduction Per Level: 0.3
2025-12-07 15:03:17 - src.services.price_monitor_service - INFO - ✅ Price Monitor Service started successfully - Task created: <Task pending name='Task-3' coro=<PriceMonitorService._monitor_loop() running at C:\Users\Administrator\ZepixTradingBot-New-v10\src\services\price_monitor_service.py:129>>, is_running: True
2025-12-07 15:03:17 - src.core.trading_engine - INFO - ✅ Price Monitor Service confirmed running after initialization
2025-12-07 15:03:17 - src.managers.profit_booking_manager - INFO - SUCCESS: Recovered 0 profit booking chains from database
SUCCESS: Trading engine initialized successfully
SUCCESS: Price monitor service started
SUCCESS: Profit booking manager initialized
[OK] Injected trend_manager and telegram_bot into alert_processor
[OK] Trade monitor started
[POLLING-THREAD] Polling thread started
[OK] Telegram polling thread started
[LIFESPAN] Yielding control - bot is now running
======================================================================
✅✅✅ BOT IS LIVE NOW - READY FOR TELEGRAM COMMANDS ✅✅✅
======================================================================
←[32mINFO←[0m:     Application startup complete.
2025-12-07 15:03:18 - src.clients.telegram_bot - INFO - [POLLING] Starting polling loop...
2025-12-07 15:03:18 - src.clients.telegram_bot - INFO - SUCCESS: Telegram bot polling started
←[32mINFO←[0m:     Uvicorn running on ←[1mhttp://0.0.0.0:80←[0m (Press CTRL+C to quit)
[POLLING-THREAD] Polling thread exited
2025-12-07 15:03:51 - src.clients.telegram_bot - WARNING - [POLLING] HTTP 409 #1: Webhook conflict - attempting recovery
2025-12-07 15:03:52 - src.clients.telegram_bot - INFO - [POLLING] HTTP 409 Recovery: Webhook cleared
2025-12-07 15:04:23 - src.clients.telegram_bot - WARNING - [POLLING] HTTP 409 #1: Webhook conflict - attempting recovery
2025-12-07 15:04:23 - src.clients.telegram_bot - INFO - [POLLING] HTTP 409 Recovery: Webhook cleared
2025-12-07 15:05:26 - src.clients.telegram_bot - WARNING - [POLLING] HTTP 409 #1: Webhook conflict - attempting recovery
2025-12-07 15:05:27 - src.clients.telegram_bot - INFO - [POLLING] HTTP 409 Recovery: Webhook cleared
2025-12-07 15:06:30 - src.clients.telegram_bot - WARNING - [POLLING] HTTP 409 #1: Webhook conflict - attempting recovery
2025-12-07 15:06:31 - src.clients.telegram_bot - INFO - [POLLING] HTTP 409 Recovery: Webhook cleared
2025-12-07 15:07:34 - src.clients.telegram_bot - WARNING - [POLLING] HTTP 409 #1: Webhook conflict - attempting recovery
2025-12-07 15:07:35 - src.clients.telegram_bot - INFO - [POLLING] HTTP 409 Recovery: Webhook cleared
←[32mINFO←[0m:     27.0.217.192:41669 - "←[1mGET /boaform/admin/formLogin?username=user&psd=user HTTP/1.0←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     37.120.246.132:49625 - "←[1mGET /.git/config HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wp-content/plugins/hellopress/wp_filemanager.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wp-includes/rest-api/alfa-rex.php7 HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /widgets.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /b.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /admin.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /autoload_classmap.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wp-activate.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /db.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /gecko.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /abe.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /bs1.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /cc.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /css.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /cloud.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /bless.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /radio.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /cong.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /bak.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /as.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /404.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /link.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /makeasmtp.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /file.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /chosen.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wp.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /uana.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /lock360.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /a.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /api.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /inc.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /atomlib.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ioxi-rex4.php7 HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /moon.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wp-info.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /warm.PhP7 HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ws.php7 HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /rss.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /pekok.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /elp.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wp-aa.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /cart.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /compare.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /shop.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /api.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /222.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /atom.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /case.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /docs.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ios.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /click.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /lv.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /inputs.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /alfa.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /byp.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /goat1.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /f.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /max.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /m.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /as.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /v.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /bless.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /vv.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /0.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /jp.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /2.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /goods.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /manager.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /new.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /info.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /doc.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /go.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /mail.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /11.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /conflg.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /xmrlpc.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /asas.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ioxi-o.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /about.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /akcc.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /zxl.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /r.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ar.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /js.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /file1.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /mar.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /123.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /321.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /simple.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /classwithtostring.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /al.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /xx.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /jga.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /num.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ty.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /buy.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /abcd.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /c.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /xo.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /dlu.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /rk2.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wso.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /we.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /karak.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /content.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /406.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /mariju.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /k.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /cache.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /zfile.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /NewFile.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /des.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /ant.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /jlex.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /mini.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /fm.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /1.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /wpc.php?p= HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /lc.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /mlex.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
←[32mINFO←[0m:     4.190.219.59:8207 - "←[1mGET /nc4.php HTTP/1.1←[0m" ←[31m404 Not Found←[0m
[MENU EXECUTION] Empty params detected, attempting recovery...
2025-12-07 18:37:33 - src.menu.command_executor - INFO - EXECUTING: trend_matrix with params {} for user 2139792302
[VALIDATE] Validating command 'trend_matrix' with params: {}
[VALIDATE] Required params for trend_matrix: []
[VALIDATE] All parameters validated successfully for trend_matrix
2025-12-07 18:37:33 - src.menu.command_executor - INFO - CALLING HANDLER: trend_matrix with formatted params: {}
2025-12-07 18:37:33 - src.menu.command_executor - INFO - EXECUTION SUCCESS: trend_matrix executed successfully for user 2139792302
DEBUG: Parsed param - type: symbol, command: set_trend, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_trend
[PARAM SELECTION] Cleaned value: 'XAUUSD' -> 'XAUUSD'
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_trend, value: 15m
🛑 [PARAM SELECTION] START - param_type=timeframe, value=15m, command=set_trend
[PARAM SELECTION] Cleaned value: '15m' -> '15m'
[PARAM SELECTION] Stored param: timeframe=15m, All params: {'symbol': 'XAUUSD', 'timeframe': '15m'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '15m'}
🔄 [PARAM SELECTION] More parameters needed. Next param: trend
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: trend, command: set_trend, value: BEARISH
🛑 [PARAM SELECTION] START - param_type=trend, value=BEARISH, command=set_trend
[PARAM SELECTION] Cleaned value: 'BEARISH' -> 'BEARISH'
[PARAM SELECTION] Stored param: trend=BEARISH, All params: {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_trend
[CONFIRMATION] Showing confirmation for set_trend with params: {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'}
[CONFIRMATION] Confirm button callback: execute_set_trend
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
2025-12-07 18:37:58 - src.menu.command_executor - INFO - EXECUTING: set_trend with params {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'} for user 2139792302
[VALIDATE] Validating command 'set_trend' with params: {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'}
[VALIDATE] Required params for set_trend: ['symbol', 'timeframe', 'trend']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x00000157E3A562A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 15m
[VALIDATE PARAM] Validating 'timeframe' = '15m'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['15m', '1h', '1d'], 'validation': <function <lambda> at 0x00000157E3A56480>}
[VALIDATE PARAM] Converted to lowercase: 15m -> 15m
[VALIDATE PARAM] Checking valid_values: ['15m', '1h', '1d']
[VALIDATE PARAM] Value '15m' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] Validating param 'trend' with value: BEARISH
[VALIDATE PARAM] Validating 'trend' = 'BEARISH'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO'], 'validation': <function <lambda> at 0x00000157E3A56C00>}
[VALIDATE PARAM] Converted to uppercase: BEARISH -> BEARISH
[VALIDATE PARAM] Checking valid_values: ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO']
[VALIDATE PARAM] Value 'BEARISH' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'trend' validation PASSED
[VALIDATE] Parameter 'trend' validation passed
[VALIDATE] All parameters validated successfully for set_trend
2025-12-07 18:37:58 - src.menu.command_executor - INFO - CALLING HANDLER: set_trend with formatted params: {'symbol': 'XAUUSD', 'timeframe': '15m', 'trend': 'BEARISH'}
SUCCESS: Trend updated: XAUUSD 15m -> BEARISH (MANUAL)
2025-12-07 18:37:59 - src.menu.command_executor - INFO - EXECUTION SUCCESS: set_trend executed successfully for user 2139792302
DEBUG: Parsed param - type: symbol, command: set_trend, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_trend
[PARAM SELECTION] Cleaned value: 'XAUUSD' -> 'XAUUSD'
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_trend, value: 1h
🛑 [PARAM SELECTION] START - param_type=timeframe, value=1h, command=set_trend
[PARAM SELECTION] Cleaned value: '1h' -> '1h'
[PARAM SELECTION] Stored param: timeframe=1h, All params: {'symbol': 'XAUUSD', 'timeframe': '1h'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '1h'}
🔄 [PARAM SELECTION] More parameters needed. Next param: trend
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: trend, command: set_trend, value: BEARISH
🛑 [PARAM SELECTION] START - param_type=trend, value=BEARISH, command=set_trend
[PARAM SELECTION] Cleaned value: 'BEARISH' -> 'BEARISH'
[PARAM SELECTION] Stored param: trend=BEARISH, All params: {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_trend
[CONFIRMATION] Showing confirmation for set_trend with params: {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'}
[CONFIRMATION] Confirm button callback: execute_set_trend
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
2025-12-07 18:38:24 - src.menu.command_executor - INFO - EXECUTING: set_trend with params {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'} for user 2139792302
[VALIDATE] Validating command 'set_trend' with params: {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'}
[VALIDATE] Required params for set_trend: ['symbol', 'timeframe', 'trend']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x00000157E3A562A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 1h
[VALIDATE PARAM] Validating 'timeframe' = '1h'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['15m', '1h', '1d'], 'validation': <function <lambda> at 0x00000157E3A56480>}
[VALIDATE PARAM] Converted to lowercase: 1h -> 1h
[VALIDATE PARAM] Checking valid_values: ['15m', '1h', '1d']
[VALIDATE PARAM] Value '1h' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] Validating param 'trend' with value: BEARISH
[VALIDATE PARAM] Validating 'trend' = 'BEARISH'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO'], 'validation': <function <lambda> at 0x00000157E3A56C00>}
[VALIDATE PARAM] Converted to uppercase: BEARISH -> BEARISH
[VALIDATE PARAM] Checking valid_values: ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO']
[VALIDATE PARAM] Value 'BEARISH' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'trend' validation PASSED
[VALIDATE] Parameter 'trend' validation passed
[VALIDATE] All parameters validated successfully for set_trend
2025-12-07 18:38:24 - src.menu.command_executor - INFO - CALLING HANDLER: set_trend with formatted params: {'symbol': 'XAUUSD', 'timeframe': '1h', 'trend': 'BEARISH'}
SUCCESS: Trend updated: XAUUSD 1h -> BEARISH (MANUAL)
2025-12-07 18:38:24 - src.menu.command_executor - INFO - EXECUTION SUCCESS: set_trend executed successfully for user 2139792302
DEBUG: Parsed param - type: symbol, command: set_trend, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_trend
[PARAM SELECTION] Cleaned value: 'XAUUSD' -> 'XAUUSD'
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_trend, value: 1d
🛑 [PARAM SELECTION] START - param_type=timeframe, value=1d, command=set_trend
[PARAM SELECTION] Cleaned value: '1d' -> '1d'
[PARAM SELECTION] Stored param: timeframe=1d, All params: {'symbol': 'XAUUSD', 'timeframe': '1d'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '1d'}
🔄 [PARAM SELECTION] More parameters needed. Next param: trend
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: trend, command: set_trend, value: BEARISH
🛑 [PARAM SELECTION] START - param_type=trend, value=BEARISH, command=set_trend
[PARAM SELECTION] Cleaned value: 'BEARISH' -> 'BEARISH'
[PARAM SELECTION] Stored param: trend=BEARISH, All params: {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_trend
[CONFIRMATION] Showing confirmation for set_trend with params: {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'}
[CONFIRMATION] Confirm button callback: execute_set_trend
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
2025-12-07 18:38:47 - src.menu.command_executor - INFO - EXECUTING: set_trend with params {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'} for user 2139792302
[VALIDATE] Validating command 'set_trend' with params: {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'}
[VALIDATE] Required params for set_trend: ['symbol', 'timeframe', 'trend']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x00000157E3A562A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 1d
[VALIDATE PARAM] Validating 'timeframe' = '1d'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['15m', '1h', '1d'], 'validation': <function <lambda> at 0x00000157E3A56480>}
[VALIDATE PARAM] Converted to lowercase: 1d -> 1d
[VALIDATE PARAM] Checking valid_values: ['15m', '1h', '1d']
[VALIDATE PARAM] Value '1d' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] Validating param 'trend' with value: BEARISH
[VALIDATE PARAM] Validating 'trend' = 'BEARISH'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO'], 'validation': <function <lambda> at 0x00000157E3A56C00>}
[VALIDATE PARAM] Converted to uppercase: BEARISH -> BEARISH
[VALIDATE PARAM] Checking valid_values: ['BULLISH', 'BEARISH', 'NEUTRAL', 'AUTO']
[VALIDATE PARAM] Value 'BEARISH' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'trend' validation PASSED
[VALIDATE] Parameter 'trend' validation passed
[VALIDATE] All parameters validated successfully for set_trend
2025-12-07 18:38:47 - src.menu.command_executor - INFO - CALLING HANDLER: set_trend with formatted params: {'symbol': 'XAUUSD', 'timeframe': '1d', 'trend': 'BEARISH'}
SUCCESS: Trend updated: XAUUSD 1d -> BEARISH (MANUAL)
2025-12-07 18:38:48 - src.menu.command_executor - INFO - EXECUTION SUCCESS: set_trend executed successfully for user 2139792302
DEBUG: Parsed param - type: symbol, command: set_auto, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_auto
[PARAM SELECTION] Cleaned value: 'XAUUSD' -> 'XAUUSD'
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_auto, value: 15m
🛑 [PARAM SELECTION] START - param_type=timeframe, value=15m, command=set_auto
[PARAM SELECTION] Cleaned value: '15m' -> '15m'
[PARAM SELECTION] Stored param: timeframe=15m, All params: {'symbol': 'XAUUSD', 'timeframe': '15m'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '15m'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '15m'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_auto
[CONFIRMATION] Showing confirmation for set_auto with params: {'symbol': 'XAUUSD', 'timeframe': '15m'}
[CONFIRMATION] Confirm button callback: execute_set_auto
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
2025-12-07 18:39:09 - src.menu.command_executor - INFO - EXECUTING: set_auto with params {'symbol': 'XAUUSD', 'timeframe': '15m'} for user 2139792302
[VALIDATE] Validating command 'set_auto' with params: {'symbol': 'XAUUSD', 'timeframe': '15m'}
[VALIDATE] Required params for set_auto: ['symbol', 'timeframe']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x00000157E3A562A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 15m
[VALIDATE PARAM] Validating 'timeframe' = '15m'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['15m', '1h', '1d'], 'validation': <function <lambda> at 0x00000157E3A56480>}
[VALIDATE PARAM] Converted to lowercase: 15m -> 15m
[VALIDATE PARAM] Checking valid_values: ['15m', '1h', '1d']
[VALIDATE PARAM] Value '15m' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] All parameters validated successfully for set_auto
2025-12-07 18:39:09 - src.menu.command_executor - INFO - CALLING HANDLER: set_auto with formatted params: {'symbol': 'XAUUSD', 'timeframe': '15m'}
SUCCESS: Mode set to AUTO for XAUUSD 15m
2025-12-07 18:39:10 - src.menu.command_executor - INFO - EXECUTION SUCCESS: set_auto executed successfully for user 2139792302
DEBUG: Parsed param - type: symbol, command: set_auto, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_auto
[PARAM SELECTION] Cleaned value: 'XAUUSD' -> 'XAUUSD'
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_auto, value: 1h
🛑 [PARAM SELECTION] START - param_type=timeframe, value=1h, command=set_auto
[PARAM SELECTION] Cleaned value: '1h' -> '1h'
[PARAM SELECTION] Stored param: timeframe=1h, All params: {'symbol': 'XAUUSD', 'timeframe': '1h'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '1h'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '1h'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_auto
[CONFIRMATION] Showing confirmation for set_auto with params: {'symbol': 'XAUUSD', 'timeframe': '1h'}
[CONFIRMATION] Confirm button callback: execute_set_auto
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
2025-12-07 18:39:33 - src.menu.command_executor - INFO - EXECUTING: set_auto with params {'symbol': 'XAUUSD', 'timeframe': '1h'} for user 2139792302
[VALIDATE] Validating command 'set_auto' with params: {'symbol': 'XAUUSD', 'timeframe': '1h'}
[VALIDATE] Required params for set_auto: ['symbol', 'timeframe']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x00000157E3A562A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 1h
[VALIDATE PARAM] Validating 'timeframe' = '1h'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['15m', '1h', '1d'], 'validation': <function <lambda> at 0x00000157E3A56480>}
[VALIDATE PARAM] Converted to lowercase: 1h -> 1h
[VALIDATE PARAM] Checking valid_values: ['15m', '1h', '1d']
[VALIDATE PARAM] Value '1h' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] All parameters validated successfully for set_auto
2025-12-07 18:39:33 - src.menu.command_executor - INFO - CALLING HANDLER: set_auto with formatted params: {'symbol': 'XAUUSD', 'timeframe': '1h'}
SUCCESS: Mode set to AUTO for XAUUSD 1h
2025-12-07 18:39:34 - src.menu.command_executor - INFO - EXECUTION SUCCESS: set_auto executed successfully for user 2139792302
DEBUG: Parsed param - type: symbol, command: set_auto, value: XAUUSD
🛑 [PARAM SELECTION] START - param_type=symbol, value=XAUUSD, command=set_auto
[PARAM SELECTION] Cleaned value: 'XAUUSD' -> 'XAUUSD'
[PARAM SELECTION] Stored param: symbol=XAUUSD, All params: {'symbol': 'XAUUSD'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD'}
🔄 [PARAM SELECTION] More parameters needed. Next param: timeframe
🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)
✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)
DEBUG: Parsed param - type: timeframe, command: set_auto, value: 1d
🛑 [PARAM SELECTION] START - param_type=timeframe, value=1d, command=set_auto
[PARAM SELECTION] Cleaned value: '1d' -> '1d'
[PARAM SELECTION] Stored param: timeframe=1d, All params: {'symbol': 'XAUUSD', 'timeframe': '1d'}
[PARAM SELECTION] Final stored params after preservation: {'symbol': 'XAUUSD', 'timeframe': '1d'}
[PARAM SELECTION] All params collected. Final params: {'symbol': 'XAUUSD', 'timeframe': '1d'}, showing confirmation
✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN
🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)
🛑 [CONFIRMATION] START - Showing confirmation for command: set_auto
[CONFIRMATION] Showing confirmation for set_auto with params: {'symbol': 'XAUUSD', 'timeframe': '1d'}
[CONFIRMATION] Confirm button callback: execute_set_auto
[CONFIRMATION] About to display confirmation screen (NOT executing command)
[CONFIRMATION] Confirmation screen displayed. Result: True
✅ [CONFIRMATION] Confirmation screen shown successfully
🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.
✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)
🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button
2025-12-07 18:39:54 - src.menu.command_executor - INFO - EXECUTING: set_auto with params {'symbol': 'XAUUSD', 'timeframe': '1d'} for user 2139792302
[VALIDATE] Validating command 'set_auto' with params: {'symbol': 'XAUUSD', 'timeframe': '1d'}
[VALIDATE] Required params for set_auto: ['symbol', 'timeframe']
[VALIDATE] Validating param 'symbol' with value: XAUUSD
[VALIDATE PARAM] Validating 'symbol' = 'XAUUSD'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'uppercase', 'valid_values': ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY'], 'validation': <function <lambda> at 0x00000157E3A562A0>}
[VALIDATE PARAM] Converted to uppercase: XAUUSD -> XAUUSD
[VALIDATE PARAM] Checking valid_values: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
[VALIDATE PARAM] Value 'XAUUSD' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'symbol' validation PASSED
[VALIDATE] Parameter 'symbol' validation passed
[VALIDATE] Validating param 'timeframe' with value: 1d
[VALIDATE PARAM] Validating 'timeframe' = '1d'
[VALIDATE PARAM] Param definition: {'type': 'string', 'format': 'lowercase', 'valid_values': ['15m', '1h', '1d'], 'validation': <function <lambda> at 0x00000157E3A56480>}
[VALIDATE PARAM] Converted to lowercase: 1d -> 1d
[VALIDATE PARAM] Checking valid_values: ['15m', '1h', '1d']
[VALIDATE PARAM] Value '1d' is in valid_values
[VALIDATE PARAM] Validation function passed
[VALIDATE PARAM] Parameter 'timeframe' validation PASSED
[VALIDATE] Parameter 'timeframe' validation passed
[VALIDATE] All parameters validated successfully for set_auto
2025-12-07 18:39:54 - src.menu.command_executor - INFO - CALLING HANDLER: set_auto with formatted params: {'symbol': 'XAUUSD', 'timeframe': '1d'}
SUCCESS: Mode set to AUTO for XAUUSD 1d
2025-12-07 18:39:54 - src.menu.command_executor - INFO - EXECUTION SUCCESS: set_auto executed successfully for user 2139792302
[MENU EXECUTION] Empty params detected, attempting recovery...
2025-12-07 18:40:14 - src.menu.command_executor - INFO - EXECUTING: trend_matrix with params {} for user 2139792302
[VALIDATE] Validating command 'trend_matrix' with params: {}
[VALIDATE] Required params for trend_matrix: []
[VALIDATE] All parameters validated successfully for trend_matrix
2025-12-07 18:40:14 - src.menu.command_executor - INFO - CALLING HANDLER: trend_matrix with formatted params: {}
2025-12-07 18:40:15 - src.menu.command_executor - INFO - EXECUTION SUCCESS: trend_matrix executed successfully for user 2139792302
2025-12-07 18:40:28 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:40:33 - src.menu.reentry_menu_handler - INFO - Handling toggle callback: toggle_autonomous
2025-12-07 18:40:33 - src.menu.reentry_menu_handler - INFO - Autonomous mode toggled: False → True
2025-12-07 18:40:35 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:40:38 - src.menu.reentry_menu_handler - INFO - Handling toggle callback: toggle_tp_continuation
2025-12-07 18:40:38 - src.menu.reentry_menu_handler - INFO - TP Continuation toggled: False → True
2025-12-07 18:40:40 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:40:44 - src.menu.reentry_menu_handler - INFO - Handling toggle callback: toggle_sl_hunt
2025-12-07 18:40:44 - src.menu.reentry_menu_handler - INFO - SL Hunt toggled: False → True
2025-12-07 18:40:46 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:40:48 - src.menu.reentry_menu_handler - INFO - Handling toggle callback: toggle_exit_continuation
2025-12-07 18:40:48 - src.menu.reentry_menu_handler - INFO - Exit Continuation toggled: False → True
2025-12-07 18:40:50 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:41:07 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
Unknown callback_data: reentry_advanced
2025-12-07 18:41:25 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
Unknown callback_data: reentry_advanced
←[32mINFO←[0m:     101.32.218.31:40672 - "←[1mHEAD /Core/Skin/Login.aspx HTTP/1.1←[0m" ←[31m404 Not Found←[0m
[MENU EXECUTION] Empty params detected, attempting recovery...
2025-12-07 18:41:58 - src.menu.command_executor - INFO - EXECUTING: sl_status with params {} for user 2139792302
[VALIDATE] Validating command 'sl_status' with params: {}
[VALIDATE] Required params for sl_status: []
[VALIDATE] All parameters validated successfully for sl_status
2025-12-07 18:41:58 - src.menu.command_executor - INFO - CALLING HANDLER: sl_status with formatted params: {}
2025-12-07 18:41:58 - src.menu.command_executor - INFO - EXECUTION SUCCESS: sl_status executed successfully for user 2139792302
2025-12-07 18:42:07 - src.menu.profit_booking_menu_handler - INFO - Profit Booking menu shown to user 2139792302 (Mode: SL-2.1)
2025-12-07 18:42:21 - src.menu.reentry_menu_handler - INFO - Handling toggle callback: toggle_profit_sl_hunt
2025-12-07 18:42:22 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:42:39 - src.menu.profit_booking_menu_handler - INFO - Profit Booking menu shown to user 2139792302 (Mode: SL-2.1)
2025-12-07 18:42:46 - src.menu.reentry_menu_handler - INFO - Handling toggle callback: toggle_profit_sl_hunt
2025-12-07 18:42:47 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
INFO: Message 676 not found or not modified, sending new message instead
2025-12-07 18:44:47 - src.managers.profit_protection_manager - INFO -
🔄 PROFIT PROTECTION MODE CHANGED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Old Mode: ⚖️ BALANCED
├─ Multiplier: 6.0x
└─ Min Threshold: $20.0

New Mode: ⚖️ BALANCED
├─ Multiplier: 6.0x
├─ Min Threshold: $20.0
└─ Description: Recommended for most traders
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INFO: Message 678 not found or not modified, sending new message instead
Callback query handler error: 'ProfitProtectionManager' object has no attribute 'modes'
←[32mINFO←[0m:     49.51.166.228:55730 - "←[1mGET / HTTP/1.1←[0m" ←[31m404 Not Found←[0m
Unknown callback_data: fine_tune_menu
2025-12-07 18:53:40 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
Unknown callback_data: reentry_advanced
2025-12-07 18:54:51 - src.menu.reentry_menu_handler - INFO - Re-entry menu shown to user 2139792302
2025-12-07 18:55:02 - src.menu.profit_booking_menu_handler - INFO - Profit Booking menu shown to user 2139792302 (Mode: SL-2.1)
2025-12-07 18:55:48 - src.menu.profit_booking_menu_handler - INFO - Profit SL mode changed: SL-2.1 → SL-1.1
2025-12-07 18:55:50 - src.menu.profit_booking_menu_handler - INFO - Profit Booking menu shown to user 2139792302 (Mode: SL-1.1)
2025-12-07 18:55:54 - src.menu.profit_booking_menu_handler - INFO - Profit SL mode changed: SL-1.1 → SL-2.1
2025-12-07 18:55:56 - src.menu.profit_booking_menu_handler - INFO - Profit Booking menu shown to user 2139792302 (Mode: SL-2.1)
