# 🧠 15_NEURAL_ARCHITECTURE.md - The Zero-Touch Autonomous System

## 1. Core Concept: The Hybrid "Brain & Body" Model

This architecture implements a strict **Separation of Concerns** to achieve a truly autonomous, "Zero-Touch" trading system.

*   **The Body (Python Bot)**: Becomes a "Dumb Execution Engine". It makes **NO decisions**. It simply listens for commands, executes trades via MT5, and reports status. It is exposed via a lightweight REST API (FastAPI/Flask).
*   **The Brain (n8n)**: The "Autonomous Intelligence". It handles ALL logic, news filtering, AI analysis, decision making, and even system maintenance. It runs on a separate server (or cloud) and controls the Body via API.

**Why this works:** The user never needs to touch the Python code to change strategy or fix logic. All logic updates happen visually in n8n workflows.

---

## 2. The 4 Autonomous Workflows (n8n Agents)

These 4 workflows replace the traditional internal "Agents".

### 🕵️‍♂️ Workflow A: The AI Analyst (Signal Processor)
*   **Trigger**: TradingView Webhook (Raw Signal: "Buy EURUSD").
*   **Step 1**: n8n calls Bot API (`GET /candles?symbol=EURUSD`) to get latest OHLC data.
*   **Step 2**: n8n sends Data + Signal to **OpenAI GPT-4 API**.
    *   *Prompt*: "Analyze this support/resistance structure. Is this Buy signal valid? Reply YES/NO."
*   **Step 3 (Decision)**:
    *   If GPT says **NO**: n8n stops. (Trade Filtered).
    *   If GPT says **YES**: n8n calls Bot API (`POST /execute_trade`).
*   **Result**: High-IQ filtering of every single trade without complex Python logic.

### 📰 Workflow B: The News Analyst (Risk Sentinel)
*   **Trigger**: Scheduled (Every 15 Minutes).
*   **Step 1**: Fetch **Forex Factory Calendar API** (or similar).
*   **Step 2 (Logic)**: Filter for "Red Folder" (High Impact) events happening in `< 30 mins`.
*   **Step 3 (Action)**:
    *   **If Danger Found**: Call Bot API (`POST /settings` -> `{"trading_enabled": false}`).
    *   **If Safe**: Call Bot API (`POST /settings` -> `{"trading_enabled": true}`).
*   **Result**: Automatic, calendar-aware "Kill Switch" that requires no manual toggle.

### 👮‍♂️ Workflow C: The Manager (Dynamic Risk)
*   **Trigger**: Webhook from Bot (On Trade Close).
*   **Step 1**: n8n calls Bot API (`GET /stats`).
*   **Step 2 (Logic)**: Analyze Daily Drawdown.
    *   *Rule*: `If DailyDrawdown > 3%`.
*   **Step 3 (Action)**:
    *   **If Breach**: Call Bot API (`POST /settings` -> `{"risk_multiplier": 0.5}`). (Halve the lot size).
    *   **If Recovered**: Restores risk multiplier to `1.0`.
*   **Result**: Auto-scaling risk management that reacts to account health in real-time.

### 🛠️ Workflow D: The Developer (The Self-Healer)
*   **Trigger**: Interval (Every 5 Mins) OR Bot Error Webhook (500 Status).
*   **Step 1 (Health Check)**: Call Bot API (`GET /health`).
*   **Step 2 (Diagnosis)**:
    *   **Scenario 1 (Timeout)**: Bot is frozen.
        *   *Action*: n8n executes **SSH Command** to server: `systemctl restart zepix-bot`.
    *   **Scenario 2 (Specific Error)**: Log says "Invalid Stop Loss".
        *   *Action*: n8n calls Bot API (`POST /settings` -> `{"sl_strategy": "default"}`). (Reverts to safe config).
*   **Result**: The system detects its own crashes and restarts itself. It detects configuration errors and "heals" its own config.

---

## 3. Required Python API Endpoints (The "Body" Interface)

To support this architecture, the Python bot must expose these endpoints:

| Method | Endpoint | Purpose | Payload Example |
| :--- | :--- | :--- | :--- |
| **GET** | `/health` | heartbeat | n/a |
| **GET** | `/stats` | Account balance, daily PnL | n/a |
| **GET** | `/candles` | Get recent OHLC data | `?symbol=EURUSD&n=20` |
| **POST** | `/execute_trade` | Place a trade (Blind execution) | `{"symbol": "EURUSD", "action": "buy", "sl": 1.100, "lot": 0.1}` |
| **POST** | `/settings` | Update configuration hot-swap | `{"trading_enabled": true, "risk_multiplier": 0.5}` |

---

## 4. Zero-Touch Confirmation

Once this system is deployed:
1.  **No Coding**: You change strategy prompts in OpenAI, not Python code.
2.  **No Monitoring**: The "Developer" workflow restarts the bot if it crashes.
3.  **No Panic**: The "News Analyst" pauses the bot before news hits.
4.  **No Blowups**: The "Manager" cuts risk automatically if you start losing.

**Status**: Architecture Defined. Ready for Implementation.
