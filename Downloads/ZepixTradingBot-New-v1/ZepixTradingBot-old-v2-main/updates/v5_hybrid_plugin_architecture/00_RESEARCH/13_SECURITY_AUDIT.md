# 13_SECURITY_AUDIT.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Identify security risks in plugin architecture and define mitigation strategies.

---

## 🔒 THREAT MODEL

### **Threat 1: Malicious Plugin**

**Scenario:** User accidentally loads a malicious plugin that:
- Steals MT5 credentials
- Places unauthorized trades
- Deletes database
- Sends spam via Telegram

**Likelihood:** Low (plugins created by user)  
**Impact:** Critical

**Mitigation:**
1. **Code Review Required:** Manual review before loading
2. **Plugin Sandboxing:** Restrict imports
3. **ServiceAPI Permissions:** Plugin can only access its own data
4. **Audit Logging:** Log all plugin actions

---

### **Threat 2: Plugin Accessing Other Plugin Data**

**Scenario:** Plugin A tries to read/modify Plugin B's database.

**Mitigation:**
```python
class PluginDatabase:
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id
        self.db_path = f"data/zepix_{plugin_id}.db"
    
    def query(self, sql):
        # Ensure only accessing own DB
        if "{other_plugin_id}" in sql:
            raise SecurityError("Cross-plugin access denied")
```

---

### **Threat 3: Telegram Token Leak**

**Scenario:** Tokens exposed in config.json pushed to GitHub.

**Mitigation:**
1. **Environment Variables:** Move tokens to `.env`
2. **Gitignore:** Ensure `config.json` and `.env` ignored
3. **Token Rotation:** Rotate tokens quarterly
4. **BotFather Settings:** Restrict bot to specific chat IDs

---

### **Threat 4: SQL Injection via Plugin**

**Scenario:** Plugin constructs unsafe SQL queries.

**Mitigation:**
```python
# BAD
def get_trades(symbol):
    query = f"SELECT * FROM trades WHERE symbol = '{symbol}'"
    return db.query(query)  # Injectable!

# GOOD
def get_trades(symbol):
    query = "SELECT * FROM trades WHERE symbol = ?"
    return db.query(query, (symbol,))  # Parameterized
```

**Enforcement:** Linter rules to detect string concatenation in SQL

---

### **Threat 5: Unauthorized Order Placement**

**Scenario:** Plugin places orders outside its allocated risk limits.

**Mitigation:**
```python
class OrderExecutionService:
    def place_order(self, plugin_id, lot_size, ...):
        # Check plugin's daily limit
        daily_stats = self.db.get_plugin_daily_stats(plugin_id)
        if daily_stats["daily_loss"] > plugin.max_daily_loss:
            raise SecurityError("Daily loss limit exceeded")
        
        # Check lot size limit
        if lot_size > plugin.max_lot_size:
            raise SecurityError("Lot size exceeds plugin limit")
```

---

## 🛡️ SECURITY CONTROLS

### **1. Plugin Import Restrictions**

```python
# Whitelist of allowed imports
ALLOWED_IMPORTS = [
    "typing", "datetime", "json", "math",
    "src.core.plugin_system",
    # ... core modules only
]

BLOCKED_IMPORTS = [
    "os", "sys", "subprocess",  # System access
    "socket", "requests",        # Network access
    "pickle", "marshal"          # Unsafe serialization
]

def validate_plugin_imports(plugin_code):
    """Scan plugin code for dangerous imports"""
    for line in plugin_code.split("\n"):
        if line.startswith("import") or "from" in line:
            for blocked in BLOCKED_IMPORTS:
                if blocked in line:
                    raise SecurityError(
                        f"Plugin uses blocked import: {blocked}"
                    )
```

---

### **2. ServiceAPI Permission Model**

```python
class ServiceAPI:
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id
        self._permissions = self._load_permissions(plugin_id)
    
    def place_order(self, ...):
        if "place_orders" not in self._permissions:
            raise PermissionError("Plugin not authorized to place orders")
```

**Permission Types:**
- `read_market_data`
- `place_orders`
- `modify_orders`
- `close_orders`
- `read_own_trades`
- `send_notifications`

**Default:** All permissions granted (for now)  
**Future:** Granular permissions per plugin

---

### **3. Audit Logging**

```python
class AuditLog:
    def log_plugin_action(self, plugin_id, action, details):
        """
        Logs security-relevant actions.
        """
        self.db.execute("""
            INSERT INTO audit_log 
            (timestamp, plugin_id, action, details)
            VALUES (?, ?, ?, ?)
        """, (datetime.now(), plugin_id, action, json.dumps(details)))
```

**Logged Actions:**
- Order placed
- Order modified
- Order closed
- Database accessed
- Config accessed
- Telegram message sent

---

### **4. Secrets Management**

**Current (Insecure):**
```json
{
  "telegram_token": "8526101969:AAF9fqQlPbNUkb1fg3vylwG4uDNiz-Z9IY4",
  "mt5_password": "Fast@@2801@@!!!"
}
```

**Future (Secure):**
```bash
# .env file (gitignored)
TELEGRAM_TOKEN=8526101969:AAF9fqQlPbNUkb1fg3vylwG4uDNiz-Z9IY4
MT5_PASSWORD=Fast@@2801@@!!!

# config.json only has references
{
  "telegram_token": "${TELEGRAM_TOKEN}",
  "mt5_password": "${MT5_PASSWORD}"
}
```

---

## 🔍 SECURITY CHECKLIST

### **Pre-Deployment**
- [ ] All tokens moved to environment variables
- [ ] `.env` file in `.gitignore`
- [ ] No credentials in Git history
- [ ] Plugin code reviewed manually
- [ ] ServiceAPI permissions configured

### **Runtime**
- [ ] Audit logging enabled
- [ ] Daily audit log review
- [ ] Anomaly detection (unusual trade volumes)
- [ ] Rate limiting on Telegram bots

### **Incident Response**
- [ ] Telegram bot suspension procedure documented
- [ ] Database backup/restore tested
- [ ] Emergency shutdown command (`/emergency_stop`)

---

## ✅ DECISION

**APPROVED:** Implement plugin sandboxing, ServiceAPI permissions, and audit logging.

**Critical Next Steps:**
1. Move secrets to `.env`
2. Implement import validation
3. Add audit logging
