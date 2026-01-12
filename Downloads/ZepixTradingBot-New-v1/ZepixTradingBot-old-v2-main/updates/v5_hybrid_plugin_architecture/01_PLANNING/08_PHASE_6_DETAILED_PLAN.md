# 08_PHASE_6_DETAILED_PLAN.md

**Phase:** 6 - UI Dashboard (Optional)  
**Duration:** Week 5-6 (Optional)  
**Dependencies:** Phases 1-5 complete  
**Status:** Not Started (Optional Feature)

---

## 🎯 PHASE OBJECTIVES

1. Create web-based dashboard for bot management
2. Enable/disable plugins via UI
3. View real-time performance metrics
4. Optional: Plugin marketplace

---

## 📋 OVERVIEW

**Note:** This phase is OPTIONAL. Core functionality is complete without it. Dashboard provides convenience but is not required for trading.

---

## 🌐 DASHBOARD FEATURES

### **Feature 1: Plugin Management UI**

**Endpoint:** `/admin/plugins`

**Features:**
- List all installed plugins
- Enable/disable toggle
- View plugin status (running, stopped, error)
- Configure plugin settings
- Upload new plugins (advanced)

**UI Mockup:**
```
┌──────────────────────────────────────┐
│ ZEPIX BOT - PLUGIN DASHBOARD         │
├──────────────────────────────────────┤
│                                      │
│ ✅ combined_v3         [ENABLED]    │
│    Status: Running                   │
│    Trades Today: 12                  │
│    P&L: +$250.50                     │
│    [Configure] [Disable] [Logs]      │
│                                      │
│ ⭕ price_action_v6     [DISABLED]   │
│    Status: Stopped                   │
│    [Enable] [Configure]              │
│                                      │
│ [+ Add New Plugin]                   │
└──────────────────────────────────────┘
```

---

### **Feature 2: Real-Time Metrics Dashboard**

**Endpoint:** `/dashboard`

**Widgets:**
- Open trades count
- Today's P&L
- Active plugins
- System health
- Live trade feed

**Tech Stack:**
- Backend: FastAPI
- Frontend: React or Vue.js
- Real-time: WebSockets

---

### **Feature 3: Configuration Editor**

**Endpoint:** `/admin/config`

**Features:**
- Edit `config.json` via UI
- Syntax validation
- Preview changes
- Apply without restart (hot-reload)

---

## 🛠️ IMPLEMENTATION (If Approved)

### **6.1: FastAPI REST Endpoints**

```python
# src/api/admin_routes.py

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/admin")

@router.get("/plugins")
async def list_plugins():
    """Returns all plugins with status"""
    plugins = plugin_registry.get_all_plugins()
    return [
        {
            "id": p.plugin_id,
            "name": p.metadata["name"],
            "version": p.metadata["version"],
            "enabled": p.enabled,
            "status": p.get_status(),
            "stats": p.get_stats()
        }
        for p in plugins
    ]

@router.post("/plugins/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """Enables a plugin"""
    success = plugin_registry.enable_plugin(plugin_id)
    if not success:
        raise HTTPException(404, "Plugin not found")
    return {"message": f"Plugin {plugin_id} enabled"}

@router.get("/metrics")
async def get_metrics():
    """Returns system metrics"""
    return {
        "open_trades": trading_engine.get_open_trades_count(),
        "daily_pnl": trading_engine.get_daily_pnl(),
        "active_plugins": plugin_registry.get_active_count(),
        "uptime": trading_engine.get_uptime()
    }
```

---

### **6.2: Frontend Dashboard (React)**

```jsx
// src/dashboard/App.jsx

function PluginDashboard() {
    const [plugins, setPlugins] = useState([]);
    
    useEffect(() => {
        fetch('/admin/plugins')
            .then(r => r.json())
            .then(setPlugins);
    }, []);
    
    const togglePlugin = async (pluginId, enable) => {
        const endpoint = enable ? 'enable' : 'disable';
        await fetch(`/admin/plugins/${pluginId}/${endpoint}`, {
            method: 'POST'
        });
        // Reload plugins
        fetchPlugins();
    };
    
    return (
        <div>
            <h1>Plugin Management</h1>
            {plugins.map(plugin => (
                <PluginCard 
                    key={plugin.id}
                    plugin={plugin}
                    onToggle={togglePlugin}
                />
            ))}
        </div>
    );
}
```

---

## 🚀 DEPLOYMENT (If Implemented)

**Serve dashboard alongside bot:**

```python
# src/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# API routes
app.include_router(admin_routes.router)

# Serve React build
app.mount("/", StaticFiles(directory="dashboard/build", html=True))
```

**Access:** `http://localhost:8000/dashboard`

---

## ✅ DECISION

**Status:** OPTIONAL / DEFERRED

**Recommendation:** Skip for now, implement after core system stable.

**If implemented later:**
- Duration: 1 week
- Requires frontend skills
- Not critical for trading operation
