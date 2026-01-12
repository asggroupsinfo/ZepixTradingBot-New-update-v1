# 13_CODE_REVIEW_GUIDELINES.md

**Version:** 1.0  
**Date:** 2026-01-12

---

## 🎯 CODE REVIEW OBJECTIVES

1. Ensure code quality and maintainability
2. Catch bugs before deployment
3. Share knowledge across team
4. Enforce architectural standards

---

## ✅ UNIVERSAL CODE REVIEW CHECKLIST

### **Functionality**
- [ ] Code does what it's supposed to do
- [ ] All edge cases handled
- [ ] Error handling comprehensive
- [ ] No logic regressions

### **Code Quality**
- [ ] Follows PEP 8 (Python) style guide
- [ ] Functions < 50 lines
- [ ] Classes have single responsibility
- [ ] No code duplication
- [ ] Magic numbers replaced with constants

### **Security**
- [ ] No hardcoded credentials
- [ ] SQL injection prevention (parameterized queries)
- [ ] Input validation present
- [ ] Sensitive data not logged

### **Testing**
- [ ] Unit tests added/updated
- [ ] Test coverage > 80%
- [ ] Tests actually test the logic
- [ ] No commented-out test code

### **Documentation**
- [ ] Docstrings for all public methods
- [ ] Complex logic has inline comments
- [ ] README updated if needed
- [ ] API docs updated

---

## 🔌 PLUGIN-SPECIFIC REVIEW

### **Plugin Structure**
- [ ] Follows template structure
- [ ] `config.json` properly formatted
- [ ] README.md explains plugin purpose
- [ ] Version number semantic (1.0.0)

### **Plugin Code Quality**
```python
# GOOD
class MyPlugin(BaseLogicPlugin):
    """
    Clear description of what this plugin does.
    """
    
    async def on_signal_received(self, signal):
        """
        Process entry signals with trend validation.
        
        Args:
            signal: Dict containing TradingView alert data
            
        Returns:
            bool: True if trade placed, False if skipped
        """
        if not self._should_process(signal):
            return False
        
        return await self._place_trade(signal)

# BAD
class MyPlugin(BaseLogicPlugin):
    async def on_signal_received(self, s):  # Unclear param name
        # No docstring
        if s["symbol"] == "XAUUSD" and s["direction"] == "BUY":  # Hardcoded
            # Place trade logic...
```

### **ServiceAPI Usage**
- [ ] Uses ServiceAPI, not direct MT5 access
- [ ] Passes `plugin_id` correctly
- [ ] Handles service errors gracefully
- [ ] No attempts to bypass security

**Example:**
```python
# GOOD
lot_size = await self.service_api.risk.calculate_lot_size(
    symbol=signal["symbol"],
    risk_percentage=self.config["risk_percentage"],
    stop_loss_pips=signal["sl_pips"]
)

# BAD
lot_size = 0.10  # Hardcoded, no risk calculation
```

---

## 🛡️ SECURITY REVIEW CHECKLIST

### **Secrets Management**
- [ ] No tokens in code
- [ ] No passwords in config
- [ ] Environment variables used
- [ ] `.env` file in `.gitignore`

### **Data Access**
- [ ] Plugin only accesses own database
- [ ] No cross-plugin queries
- [ ] SQL queries parameterized
- [ ] No raw SQL string concatenation

### **Plugin Sandboxing**
- [ ] No `import os`, `import sys`
- [ ] No subprocess calls
- [ ] No file system access (except own DB)
- [ ] No network requests (except via ServiceAPI)

---

## 📊 PERFORMANCE REVIEW

### **Efficiency**
- [ ] No N+1 query problems
- [ ] Database queries optimized
- [ ] Heavy operations async
- [ ] No blocking I/O in event loop

### **Resource Usage**
- [ ] No memory leaks
- [ ] Connections properly closed
- [ ] No infinite loops
- [ ] Proper error cleanup

**Example:**
```python
# GOOD
async def get_all_trades(self):
    """Efficient single query"""
    return await self.db.query(
        "SELECT * FROM trades WHERE status = ?",
        ("OPEN",)
    )

# BAD
async def get_all_trades(self):
    """Inefficient multiple queries"""
    all_trades = []
    for ticket in self.get_all_tickets():  # N+1 problem
        trade = await self.db.get_trade(ticket)
        all_trades.append(trade)
    return all_trades
```

---

## 🧪 TEST REVIEW CHECKLIST

### **Test Quality**
- [ ] Tests are independent
- [ ] Tests are deterministic
- [ ] No sleep() calls
- [ ] Mock external dependencies
- [ ] Assert meaningful values

**Example:**
```python
# GOOD
def test_lot_size_calculation():
    """Test accurate lot size calculation"""
    service = RiskManagementService(config, mt5, db)
    
    lot = service.calculate_lot_size(
        plugin_id="test",
        symbol="XAUUSD",
        risk_percentage=1.5,
        stop_loss_pips=10.0,
        account_balance=10000.0  # Fixed balance for test
    )
    
    assert lot == 0.15  # Precise assertion

# BAD
def test_lot_size():
    lot = service.calc_lot(...)
    assert lot > 0  # Too vague
```

---

## 🔄 MIGRATION CODE REVIEW

### **Backward Compatibility**
- [ ] Existing functionality unchanged
- [ ] Legacy code still works
- [ ] Config changes documented
- [ ] Migration path clear

### **Data Migration**
- [ ] Backup before migration
- [ ] Rollback procedure tested
- [ ] Data integrity verified
- [ ] No data loss

---

## 📝 DOCUMENTATION REVIEW

### **Code Comments**
```python
# GOOD
def calculate_dual_lots(self, alert, multiplier):
    """
    Calculates lot sizes for Order A and Order B.
    
    Order A uses risk-based calculation.
    Order B is 2x Order A with fixed SL.
    
    Args:
        alert: TradingView alert data
        multiplier: Config-based lot multiplier
        
    Returns:
        tuple: (lot_a, lot_b)
    """

# BAD
def calc_lots(a, m):  # No docstring, unclear params
    l1 = a.lot * m
    l2 = l1 * 2
    return l1, l2
```

### **README Quality**
- [ ] Clear purpose statement
- [ ] Installation instructions
- [ ] Configuration guide
- [ ] Usage examples
- [ ] Troubleshooting section

---

## 🚨 COMMON CODE SMELLS

### **Anti-Patterns to Reject:**

❌ **God Class** (class doing too much)
❌ **Long Method** (function > 50 lines)
❌ **Magic Numbers** (0.10, 500, etc. without constants)
❌ **Global State** (mutable global variables)
❌ **Dead Code** (commented-out code)
❌ **Catch-All Exceptions** (`except Exception: pass`)
❌ **Premature Optimization** (complex code for tiny gain)

---

## ✅ APPROVAL CRITERIA

**Code is approved when:**
- [ ] All checklist items pass
- [ ] No critical issues
- [ ] < 3 minor issues
- [ ] Tests pass
- [ ] Documentation complete

**Minor Issue Examples:**
- Missing docstring
- Suboptimal variable name
- Minor code duplication

**Critical Issue Examples:**
- Security vulnerability
- Logic bug
- No error handling
- Breaking change without migration

---

## 🔄 REVIEW PROCESS

1. **Author:** Submit PR with description
2. **Reviewer:** 
   - Run through checklist
   - Test locally
   - Leave comments
3. **Author:** Address feedback
4. **Reviewer:** Re-review
5. **Approval:** Merge to main

**Timeline:** Reviews within 24 hours

---

## 🎯 REVIEWER RESPONSIBILITIES

- Be constructive, not critical
- Explain why, not just what
- Appreciate good code
- Share knowledge
- Focus on important issues

---

## ✅ FINAL SIGN-OFF

**Before merging:**
- [ ] All conversations resolved
- [ ] CI/CD pipeline green
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Deployment plan ready
