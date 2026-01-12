# DASHBOARD TECHNICAL SPECIFICATION

**Version:** 1.0  
**Date:** 2026-01-12  
**Phase:** 6 (Optional Dashboard)  
**Status:** Complete Specification

---

## 🎯 DASHBOARD OVERVIEW

**Purpose:** Web-based monitoring and control interface for Zepix Trading Bot

**Access:** `http://localhost:5000` (local) or secured remote URL

**Tech Stack:**
- **Backend:** Flask/FastAPI (Python)
- **Frontend:** React/Vue.js with WebSockets
- **Database:** Read from `zepix_bot.db` (aggregated data)
- **Real-time:** WebSocket for live updates

---

## 📊 DASHBOARD FEATURES

### **1. Real-Time Monitoring**

**Main Dashboard View:**
```
┌────────────────────────────────────────────────┐
│  ZEPIX TRADING BOT - LIVE DASHBOARD           │
├────────────────────────────────────────────────┤
│  Status: 🟢 ACTIVE    Uptime: 3d 15h 22m      │
│  Total P&L: +$2,450.00  Today: +$125.50       │
├────────────────────────────────────────────────┤
│  [V3 Combined]  [V6 1M]  [V6 5M]  [V6 15M] [V6 1H] │
│     Active        Active    Active   Active    Active│
│   5 trades      2 trades  1 trade  1 trade  0 trades│
│   +$120.00      +$45.00   -$15.00  +$25.00    $0.00 │
├────────────────────────────────────────────────┤
│  OPEN POSITIONS (9)                            │
│  ┌──────────────────────────────────────────┐ │
│  │ XAUUSD BUY 0.10 | Entry: 2030.50         │ │
│  │ Plugin: combined_v3 | Logic: LOGIC2      │ │
│  │ P&L: +$55.00 (+5.5 pips) | Age: 2h 15m   │ │
│  │ [CLOSE] [MODIFY SL] [BOOK PROFIT]        │ │
│  └──────────────────────────────────────────┘ │
│  [... more positions ...]                     │
├────────────────────────────────────────────────┤
│  RECENT ALERTS (Live Feed)                     │
│  ● 17:42 | V3 Institutional_Launchpad | BUY   │
│  ● 17:40 | V6 TREND_PULSE | 15m Update        │
│  ● 17:38 | V3 Exit_Bullish | Position Closed  │
└────────────────────────────────────────────────┘
```

---

### **2. Plugin Management**

**Plugin Control Panel:**
```json
{
  "combined_v3": {
    "status": "active",
    "shadow_mode": false,
    "enabled": true,
    "controls": [
      "Enable/Disable",
      "Shadow Mode Toggle",
      "Config Reload",
      "View Logs"
    ],
    "stats": {
      "total_trades": 145,
      "win_rate": 67.5,
      "avg_profit": 15.2
    }
  }
}
```

**Features:**
- Enable/Disable plugins without restart
- Toggle shadow mode per plugin
- View plugin-specific logs
- Reload configuration
- Performance metrics per plugin

---

### **3. Trade History & Analytics**

**Advanced Filtering:**
- Date range picker
- Plugin filter (V3, V6 1M, V6 5M, etc.)
- Symbol filter
- Direction filter (BUY/SELL)
- Status filter (OPEN/CLOSED)
- P&L range filter

**Export Options:**
- CSV export
- PDF report generation
- Excel export with charts
- JSON data dump

**Analytics Charts:**
1. **P&L Over Time** (Line chart)
2. **Win Rate by Plugin** (Bar chart)
3. **Trade Distribution** (Pie chart)
4. **Drawdown Analysis** (Area chart)
5. **Symbol Performance** (Heatmap)

---

### **4. Configuration Management**

**Live Config Editor:**
```javascript
// Edit plugin config in browser
{
  "combined_v3": {
    "settings": {
      "max_lot_size": 1.0,  // Editable
      "daily_loss_limit": 500.0,  // Editable
      "supported_symbols": ["XAUUSD"]  // Editable
    }
  }
}

// Save → Reload plugin → Confirm changes
```

**Features:**
- JSON editor with syntax highlighting
- Validation before save
- Rollback to previous config
- Config version history
- Apply changes without restart (hot reload)

---

### **5. System Controls**

**Emergency Controls:**
- 🔴 **EMERGENCY STOP ALL** - Close all positions immediately
- ⏸️ **PAUSE BOT** - Stop accepting new signals
- ▶️ **RESUME BOT** - Resume normal operation
- 🔄 **RESTART PLUGIN** - Restart specific plugin
- 🔄 **RESTART BOT** - Full bot restart

**Telegram Integration:**
- Test notification send
- View bot status
- Check connections
- Send custom message

---

## 🔧 BACKEND API ENDPOINTS

### **GET /api/status**
```json
{
  "bot_status": "active",
  "uptime_seconds": 315720,
  "plugins": [
    {"id": "combined_v3", "status": "active", "trades": 5},
    {"id": "price_action_1m", "status": "active", "trades": 2}
  ]
}
```

### **GET /api/trades?plugin=combined_v3&status=open**
```json
{
  "trades": [
    {
      "id": 145,
      "plugin_id": "combined_v3",
      "symbol": "XAUUSD",
      "direction": "BUY",
      "lot_size": 0.10,
      "entry_price": 2030.50,
      "current_price": 2036.00,
      "profit_dollars": 55.00,
      "profit_pips": 5.5,
      "status": "OPEN"
    }
  ]
}
```

### **POST /api/trades/{id}/close**
Close specific trade from dashboard.

### **POST /api/plugins/{id}/toggle**
Enable/disable plugin.

### **POST /api/emergency/stop_all**
Emergency stop all trading.

### **WebSocket /ws/live**
Real-time updates for:
- New alerts received
- Positions opened/closed
- P&L updates
- Plugin status changes

---

## 🎨 FRONTEND COMPONENTS

### **React Component Structure:**
```
/src/dashboard/
├── App.jsx (Main layout)
├── components/
│   ├── Header.jsx (Status bar)
│   ├── PluginCard.jsx (Per-plugin stats)
│   ├── TradeList.jsx (Open positions)
│   ├── AlertFeed.jsx (Live alerts)
│   ├── Charts/
│   │   ├── PnLChart.jsx
│   │   ├── WinRateChart.jsx
│   │   └── DrawdownChart.jsx
│   ├── Controls/
│   │   ├── EmergencyStop.jsx
│   │   └── PluginToggle.jsx
│   └── ConfigEditor.jsx
├── services/
│   ├── api.js (API calls)
│   └── websocket.js (Live updates)
└── styles/
    └── dashboard.css
```

---

## 🔐 SECURITY

**Authentication:**
- Basic Auth with username/password
- Session-based (expires after 1 hour)
- HTTPS required for remote access

**Authorization:**
- Read-only mode (view only)
- Operator mode (close trades, toggle plugins)
- Admin mode (full control, config editing)

**Rate Limiting:**
- Max 100 requests/minute per IP
- Emergency stops limited to 1/minute

---

## 📱 RESPONSIVE DESIGN

**Mobile Support:**
- Responsive layout (Bootstrap/Tailwind)
- Mobile-optimized charts
- Touch-friendly controls
- PWA support (add to home screen)

---

## 🎯 DASHBOARD LAUNCH CHECKLIST

- [ ] Flask/FastAPI backend setup
- [ ] React frontend built
- [ ] WebSocket connection tested
- [ ] All API endpoints functional
- [ ] Authentication working
- [ ] Charts rendering correctly
- [ ] Mobile responsive
- [ ] Emergency controls tested
- [ ] Documentation complete

**Status:** OPTIONAL (Phase 6) - Can be implemented after core bot is stable
