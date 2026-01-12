# API Response Formats

## Overview

This document describes all response formats used by the Zepix Trading Bot API endpoints, webhook responses, and Telegram message formats.

---

## 1. Webhook Endpoint Responses

### POST /webhook

#### Success Response
```json
{
  "status": "success",
  "message": "Alert processed"
}
```

**Status Code:** `200 OK`

**When:** Alert is successfully validated and processed by the trading engine.

---

#### Rejection Response (Validation Failed)
```json
{
  "status": "rejected",
  "message": "Alert validation failed"
}
```

**Status Code:** `200 OK`

**When:** Alert fails validation (invalid format, missing fields, invalid signal type, etc.)

---

#### Rejection Response (Processing Failed)
```json
{
  "status": "rejected",
  "message": "Alert processing failed"
}
```

**Status Code:** `200 OK`

**When:** Alert is valid but processing fails (trend mismatch, risk limits exceeded, etc.)

---

#### Error Response
```json
{
  "detail": "Webhook processing error: [error message]"
}
```

**Status Code:** `400 Bad Request`

**When:** Exception occurs during webhook processing (malformed JSON, server error, etc.)

---

#### Scanner Request Response
```json
{
  "detail": "Not found"
}
```

**Status Code:** `404 Not Found`

**When:** Request matches security scanner patterns (vendor/phpunit, .env, .git, etc.)

---

## 2. Health Check Endpoint

### GET /health

#### Success Response
```json
{
  "status": "healthy",
  "version": "2.0",
  "timestamp": "2025-01-18T12:34:56.789Z",
  "daily_loss": 150.0,
  "lifetime_loss": 500.0,
  "mt5_connected": true,
  "features": {
    "fixed_lots": true,
    "reentry_system": true,
    "sl_hunting_protection": true,
    "1_1_rr": true
  }
}
```

**Status Code:** `200 OK`

**Fields:**
- `status`: Always "healthy" if endpoint is reachable
- `version`: Bot version string
- `timestamp`: ISO 8601 UTC timestamp
- `daily_loss`: Current daily loss amount (float)
- `lifetime_loss`: Total lifetime loss amount (float)
- `mt5_connected`: Boolean indicating MT5 connection status
- `features`: Object with feature flags

---

## 3. Statistics Endpoint

### GET /stats

#### Success Response
```json
{
  "daily_profit": 250.0,
  "daily_loss": 150.0,
  "lifetime_loss": 500.0,
  "total_trades": 45,
  "winning_trades": 28,
  "win_rate": 62.22,
  "current_risk_tier": "10000",
  "risk_parameters": {
    "daily_loss_limit": 400.0,
    "max_total_loss": 1000.0
  },
  "trading_paused": false,
  "simulation_mode": false,
  "lot_size": 0.1,
  "balance": 9264.90
}
```

**Status Code:** `200 OK`

**Fields:**
- `daily_profit`: Total profit today (float)
- `daily_loss`: Total loss today (float)
- `lifetime_loss`: Cumulative lifetime loss (float)
- `total_trades`: Total number of trades executed (int)
- `winning_trades`: Number of winning trades (int)
- `win_rate`: Win rate percentage (float, 0-100)
- `current_risk_tier`: Current risk tier based on balance (string: "5000", "10000", "25000", "50000", "100000")
- `risk_parameters`: Object with risk limits for current tier
- `trading_paused`: Boolean indicating if trading is paused
- `simulation_mode`: Boolean indicating if simulation mode is active
- `lot_size`: Current lot size being used (float)
- `balance`: Current account balance (float)

---

## 4. Status Endpoint

### GET /status

#### Success Response
```json
{
  "status": "running",
  "trading_paused": false,
  "simulation_mode": false,
  "daily_profit": 250.0,
  "daily_loss": 150.0,
  "lifetime_loss": 500.0,
  "total_trades": 45,
  "winning_trades": 28,
  "win_rate": 62.22,
  "open_trades": [
    {
      "symbol": "XAUUSD",
      "entry": 4025.50,
      "sl": 4020.00,
      "tp": 4035.25,
      "lot_size": 0.1,
      "direction": "buy",
      "strategy": "LOGIC1",
      "status": "open",
      "trade_id": 123456,
      "open_time": "2025-01-18T10:30:00",
      "close_time": null,
      "pnl": null,
      "chain_id": "XAUUSD_abc123",
      "chain_level": 1,
      "is_re_entry": false,
      "order_type": "TP_TRAIL",
      "profit_chain_id": null,
      "profit_level": 0
    }
  ],
  "active_chains": 2,
  "active_profit_chains": 1
}
```

**Status Code:** `200 OK`

**Fields:**
- All fields from `/stats` endpoint
- `open_trades`: Array of open trade objects (see Trade Object format below)
- `active_chains`: Number of active re-entry chains (int)
- `active_profit_chains`: Number of active profit booking chains (int)

**Trade Object Format:**
```json
{
  "symbol": "string (e.g., XAUUSD, EURUSD)",
  "entry": "float (entry price)",
  "sl": "float (stop loss price)",
  "tp": "float (take profit price)",
  "lot_size": "float (lot size)",
  "direction": "string (buy or sell)",
  "strategy": "string (LOGIC1, LOGIC2, or LOGIC3)",
  "status": "string (open or closed)",
  "trade_id": "integer or null (MT5 trade ID)",
  "open_time": "string (ISO 8601 datetime)",
  "close_time": "string or null (ISO 8601 datetime)",
  "pnl": "float or null (profit/loss)",
  "chain_id": "string or null (re-entry chain ID)",
  "chain_level": "integer (chain level, 1-based)",
  "is_re_entry": "boolean",
  "order_type": "string or null (TP_TRAIL or PROFIT_TRAIL)",
  "profit_chain_id": "string or null (profit booking chain ID)",
  "profit_level": "integer (profit booking level, 0-4)"
}
```

---

## 5. Trading Control Endpoints

### POST /pause

#### Success Response
```json
{
  "status": "success",
  "message": "Trading paused"
}
```

**Status Code:** `200 OK`

---

### POST /resume

#### Success Response
```json
{
  "status": "success",
  "message": "Trading resumed"
}
```

**Status Code:** `200 OK`

---

## 6. Trend Management Endpoints

### GET /trends

#### Success Response
```json
{
  "status": "success",
  "trends": {
    "XAUUSD": {
      "5m": "BULLISH",
      "15m": "BEARISH",
      "1h": "BULLISH",
      "1d": "NEUTRAL"
    },
    "EURUSD": {
      "5m": "NEUTRAL",
      "15m": "NEUTRAL",
      "1h": "NEUTRAL",
      "1d": "NEUTRAL"
    }
  }
}
```

**Status Code:** `200 OK`

**Fields:**
- `trends`: Object with symbol keys, each containing timeframe trends
- Trend values: `"BULLISH"`, `"BEARISH"`, or `"NEUTRAL"`

---

### POST /set_trend

#### Success Response
```json
{
  "status": "success",
  "message": "Trend set for XAUUSD 1h: BULLISH"
}
```

**Status Code:** `200 OK`

---

#### Error Response
```json
{
  "status": "error",
  "message": "Error message here"
}
```

**Status Code:** `200 OK`

---

## 7. Re-entry Chains Endpoint

### GET /chains

#### Success Response
```json
{
  "status": "success",
  "chains": [
    {
      "chain_id": "XAUUSD_abc123",
      "symbol": "XAUUSD",
      "direction": "buy",
      "original_entry": 4025.50,
      "original_sl_distance": 5.50,
      "current_level": 2,
      "max_level": 2,
      "total_profit": 0.0,
      "trades": [123456, 123457],
      "status": "active",
      "created_at": "2025-01-18T10:30:00",
      "last_update": "2025-01-18T11:00:00",
      "trend_at_creation": {
        "1h": "BULLISH",
        "15m": "BULLISH"
      },
      "metadata": {
        "sl_system_used": "sl-1",
        "sl_reduction_percent": 0,
        "original_sl_pips": 55.0,
        "applied_sl_pips": 55.0
      }
    }
  ]
}
```

**Status Code:** `200 OK`

**Fields:**
- `chains`: Array of re-entry chain objects
- Chain status: `"active"`, `"completed"`, or `"stopped"`

---

## 8. Lot Size Configuration Endpoints

### GET /lot_config

#### Success Response
```json
{
  "fixed_lots": {
    "5000": 0.05,
    "10000": 0.1,
    "25000": 1.0,
    "100000": 5.0
  },
  "manual_overrides": {
    "5000": 0.1
  },
  "current_balance": 9264.90,
  "current_lot": 0.1
}
```

**Status Code:** `200 OK`

**Fields:**
- `fixed_lots`: Object mapping tier (string) to lot size (float)
- `manual_overrides`: Object with manual lot size overrides
- `current_balance`: Current account balance (float)
- `current_lot`: Current lot size being used (float)

---

### POST /set_lot_size

#### Success Response
```json
{
  "status": "success",
  "message": "Lot size set: $10000 → 0.15"
}
```

**Status Code:** `200 OK`

---

#### Error Response
```json
{
  "status": "error",
  "message": "Error message here"
}
```

**Status Code:** `200 OK`

---

## 9. Statistics Reset Endpoint

### POST /reset_stats

#### Success Response
```json
{
  "status": "success",
  "message": "Stats reset successfully"
}
```

**Status Code:** `200 OK`

---

#### Error Response
```json
{
  "status": "error",
  "message": "Error message here"
}
```

**Status Code:** `200 OK`

---

## 10. Telegram Message Formats

### Success Messages

#### Trade Execution Success
```
✅ *Trade Executed Successfully*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
Direction: BUY
Entry: 4025.50
SL: 4020.00
TP: 4035.25
Lot Size: 0.1
Strategy: LOGIC1

Order A (TP Trail): ✅ Placed
Order B (Profit Trail): ✅ Placed
```

#### Trend Update
```
📊 XAUUSD 1H Trend Updated: BULLISH
```

#### Mode Change
```
✅ *Profit SL Mode Changed Successfully!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Previous Mode: SL-1.1
• New Mode: SL-2.1
• Status: ✅ Active

Profit booking SL system has been updated.
```

---

### Error Messages

#### Parameter Validation Failed
```
❌ *Parameter Validation Failed*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command: `profit_sl_mode`
Error: Missing required parameter: profit_sl_mode

Please check your input and try again.
```

#### Command Execution Failed
```
❌ *Command Execution Failed*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command: `/profit_sl_mode`

❌ Parameters were lost. Please try again:
1. Go back to menu
2. Select command again
3. Select required parameters: profit_sl_mode
4. Click Confirm
```

#### Session Expired
```
⚠️ *Session Expired*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This command button is from a previous session.

Please start fresh:
1. Click '🏠 Main Menu' below
2. Navigate to the command again
3. Select parameters
4. Click Confirm
```

---

### Status Messages

#### Bot Status
```
🤖 *Bot Status*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: ✅ Running
Mode: LIVE TRADING
Trading: ✅ Active

Daily P&L: +$250.00
Lifetime Loss: $500.00

Open Trades: 2
Active Chains: 1
```

#### Risk Caps
```
🛡️ *Risk Management*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tier: $10,000
Daily Loss Limit: $400.00
Current Daily Loss: $150.00
Remaining: $250.00

Lifetime Loss Limit: $1,000.00
Current Lifetime Loss: $500.00
Remaining: $500.00
```

---

## 11. Common Response Patterns

### Standard Success Pattern
```json
{
  "status": "success",
  "message": "Operation completed successfully"
}
```

### Standard Error Pattern
```json
{
  "status": "error",
  "message": "Error description here"
}
```

### Standard Status Pattern
```json
{
  "status": "success",
  "data": { /* response data */ }
}
```

---

## 12. HTTP Status Codes

| Status Code | Meaning | Usage |
|------------|---------|-------|
| `200 OK` | Request successful | All successful operations |
| `400 Bad Request` | Invalid request | Malformed JSON, validation errors |
| `404 Not Found` | Resource not found | Invalid endpoint, scanner requests |
| `500 Internal Server Error` | Server error | Unhandled exceptions (rare) |

---

## 13. Response Headers

All responses include standard HTTP headers:
- `Content-Type: application/json`
- `Content-Length: [size]`

---

## 14. Error Response Details

### Validation Error
```json
{
  "detail": "Field validation failed: [field] must be [requirement]"
}
```

### Processing Error
```json
{
  "detail": "Processing error: [error description]"
}
```

### Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

---

## Notes

1. **All timestamps** are in ISO 8601 format with UTC timezone (e.g., `2025-01-18T12:34:56.789Z`)

2. **All monetary values** are in USD and represented as floats (e.g., `150.0` for $150.00)

3. **All prices** are represented as floats with appropriate decimal precision (e.g., `4025.50` for XAUUSD)

4. **Boolean values** are always lowercase: `true` or `false`

5. **Null values** are represented as `null` (not `None` or empty string)

6. **Arrays** are always returned even if empty: `[]`

7. **Objects** are always returned even if empty: `{}`

---

## Example: Complete Request-Response Flow

### Request
```http
POST /webhook HTTP/1.1
Host: your-server.com:80
Content-Type: application/json

{
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "buy",
  "tf": "5m",
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

### Success Response
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 45

{
  "status": "success",
  "message": "Alert processed"
}
```

### Rejection Response
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 55

{
  "status": "rejected",
  "message": "Alert validation failed"
}
```

---

**Last Updated:** 2025-01-18  
**Version:** 2.0

