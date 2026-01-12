# PLUGIN VERSIONING & COMPATIBILITY SYSTEM

**Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Production-Ready Specification  
**Priority:** 🟡 MEDIUM (Required for Safe Plugin Updates)

---

## 🎯 PURPOSE

Implement **semantic versioning** and **compatibility checks** for V3 and V6 plugins to enable safe updates, rollbacks, and A/B testing without breaking the system.

**Key Features:**
1. **Semantic Versioning:** MAJOR.MINOR.PATCH (e.g., 3.2.1, 6.1.0)
2. **Compatibility Matrix:** Track which plugin versions work together
3. **Safe Updates:** Prevent incompatible plugin combinations
4. **Rollback Support:** Revert to previous stable versions
5. **A/B Testing:** Run old and new versions side-by-side

---

## 📋 SEMANTIC VERSIONING RULES

### **Version Format: MAJOR.MINOR.PATCH**

```
V3.2.1
│ │ │
│ │ └─ PATCH: Bug fixes, no API changes
│ └─── MINOR: New features, backward compatible
└───── MAJOR: Breaking changes, API incompatible
```

**Version Increment Rules:**

| Change Type | Increment | Example | Compatibility |
|------------|-----------|---------|---------------|
| Bug fix | PATCH | 3.2.0 → 3.2.1 | ✅ Fully compatible |
| New feature (compatible) | MINOR | 3.2.1 → 3.3.0 | ✅ Backward compatible |
| Breaking change | MAJOR | 3.3.0 → 4.0.0 | ❌ Incompatible |

**Examples:**
- `3.0.0` → `3.0.1`: Fixed hybrid SL calculation bug
- `3.0.1` → `3.1.0`: Added multi-timeframe trend support
- `3.1.0` → `4.0.0`: Changed signal format (breaking)

---

## 🏗️ PLUGIN VERSIONING ARCHITECTURE

```python
@dataclass
class PluginVersion:
    """
    Represents a plugin version
    """
    plugin_id: str             # 'combined_v3', 'price_action_1m'
    major: int                 # 3, 6
    minor: int                 # 0, 1, 2
    patch: int                 # 0, 1, 2
    
    build_date: datetime       # When this version was built
    commit_hash: str           # Git commit hash
    author: str                # Who released this version
    
    # Compatibility constraints
    requires_api_version: str  # Min ServiceAPI version required
    requires_db_schema: str    # Min DB schema version required
    
    # Feature flags
    features: List[str]        # ['hybrid_sl', 'trend_pulse']
    deprecated: bool           # Is this version deprecated?
    
    @property
    def version_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: 'PluginVersion') -> bool:
        """
        Check if this version is compatible with another
        
        Rules:
        - Same MAJOR version = compatible
        - Different MAJOR = incompatible
        """
        if self.plugin_id != other.plugin_id:
            return True  # Different plugins don't conflict
        
        return self.major == other.major
    
    def __str__(self):
        return f"{self.plugin_id} v{self.version_string}"
    
    def __lt__(self, other):
        """Enable version comparison"""
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
```

---

## 📦 PLUGIN REGISTRY WITH VERSIONING

```python
class VersionedPluginRegistry:
    """
    Enhanced plugin registry with version management
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.active_plugins = {}    # plugin_id -> PluginVersion
        self.available_versions = {} # plugin_id -> List[PluginVersion]
        
        self._load_plugin_versions()
    
    def _load_plugin_versions(self):
        """Load all available plugin versions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plugin_id, major, minor, patch, build_date, 
                   commit_hash, author, requires_api_version, 
                   requires_db_schema, features, deprecated
            FROM plugin_versions
            ORDER BY major DESC, minor DESC, patch DESC
        """)
        
        for row in cursor.fetchall():
            plugin_id = row[0]
            version = PluginVersion(
                plugin_id=plugin_id,
                major=row[1],
                minor=row[2],
                patch=row[3],
                build_date=datetime.fromisoformat(row[4]),
                commit_hash=row[5],
                author=row[6],
                requires_api_version=row[7],
                requires_db_schema=row[8],
                features=json.loads(row[9]),
                deprecated=bool(row[10])
            )
            
            if plugin_id not in self.available_versions:
                self.available_versions[plugin_id] = []
            
            self.available_versions[plugin_id].append(version)
        
        conn.close()
    
    def register_plugin(
        self,
        plugin_id: str,
        version: PluginVersion,
        force: bool = False
    ) -> bool:
        """
        Register a specific plugin version as active
        
        Returns:
            True if registration successful, False if incompatible
        """
        # Check compatibility with currently active plugins
        for active_id, active_version in self.active_plugins.items():
            if not version.is_compatible_with(active_version):
                logger.error(
                    f"❌ {version} is incompatible with active {active_version}"
                )
                if not force:
                    return False
        
        # Check API and DB schema requirements
        current_api_version = self._get_api_version()
        current_db_schema = self._get_db_schema_version()
        
        if not self._meets_requirements(version, current_api_version, current_db_schema):
            logger.error(
                f"❌ {version} requires API {version.requires_api_version} "
                f"and DB schema {version.requires_db_schema}"
            )
            if not force:
                return False
        
        # Register plugin
        self.active_plugins[plugin_id] = version
        
        logger.info(f"✅ Registered {version}")
        
        return True
    
    def upgrade_plugin(
        self,
        plugin_id: str,
        target_version: str
    ) -> Tuple[bool, str]:
        """
        Upgrade plugin to a specific version
        
        Args:
            plugin_id: Plugin identifier
            target_version: Target version string (e.g., '3.2.0')
        
        Returns:
            (success, message)
        """
        current = self.active_plugins.get(plugin_id)
        
        if not current:
            return False, f"Plugin {plugin_id} not currently active"
        
        # Find target version
        target = self._find_version(plugin_id, target_version)
        
        if not target:
            return False, f"Version {target_version} not found for {plugin_id}"
        
        # Check if downgrade
        if target < current:
            logger.warning(
                f"⚠️ Downgrading {plugin_id} from {current.version_string} "
                f"to {target.version_string}"
            )
        
        # Check compatibility
        if not current.is_compatible_with(target):
            return False, (
                f"Version {target_version} is incompatible with "
                f"current version {current.version_string} (MAJOR version mismatch)"
            )
        
        # Perform upgrade
        success = self.register_plugin(plugin_id, target, force=False)
        
        if success:
            return True, f"✅ Upgraded {plugin_id} to {target.version_string}"
        else:
            return False, f"❌ Upgrade failed for {plugin_id}"
    
    def rollback_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """
        Rollback plugin to previous stable version
        """
        current = self.active_plugins.get(plugin_id)
        
        if not current:
            return False, f"Plugin {plugin_id} not currently active"
        
        # Get previous stable version (same MAJOR, lower MINOR/PATCH, not deprecated)
        available = sorted(
            [v for v in self.available_versions[plugin_id] 
             if v.major == current.major and v < current and not v.deprecated],
            reverse=True
        )
        
        if not available:
            return False, f"No rollback version found for {plugin_id}"
        
        previous = available[0]
        
        # Perform rollback
        success = self.register_plugin(plugin_id, previous, force=True)
        
        if success:
            return True, f"✅ Rolled back {plugin_id} to {previous.version_string}"
        else:
            return False, f"❌ Rollback failed for {plugin_id}"
    
    def get_active_version(self, plugin_id: str) -> PluginVersion:
        """Get currently active version of plugin"""
        return self.active_plugins.get(plugin_id)
    
    def list_available_versions(self, plugin_id: str) -> List[PluginVersion]:
        """List all available versions of plugin"""
        return sorted(
            self.available_versions.get(plugin_id, []),
            reverse=True
        )
    
    def _find_version(self, plugin_id: str, version_string: str) -> PluginVersion:
        """Find specific version by version string"""
        major, minor, patch = map(int, version_string.split('.'))
        
        for version in self.available_versions.get(plugin_id, []):
            if version.major == major and version.minor == minor and version.patch == patch:
                return version
        
        return None
    
    def _meets_requirements(
        self,
        version: PluginVersion,
        api_version: str,
        db_schema: str
    ) -> bool:
        """Check if plugin version meets system requirements"""
        # Compare versions (simplified)
        return (
            api_version >= version.requires_api_version and
            db_schema >= version.requires_db_schema
        )
    
    def _get_api_version(self) -> str:
        """Get current ServiceAPI version"""
        # Implementation would check actual API version
        return "1.0.0"
    
    def _get_db_schema_version(self) -> str:
        """Get current database schema version"""
        # Implementation would check actual DB schema
        return "1.0.0"
```

---

## 📊 DATABASE SCHEMA

```sql
-- Plugin versions table
CREATE TABLE plugin_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    
    build_date DATETIME NOT NULL,
    commit_hash TEXT NOT NULL,
    author TEXT NOT NULL,
    
    requires_api_version TEXT NOT NULL,
    requires_db_schema TEXT NOT NULL,
    
    features TEXT NOT NULL,  -- JSON array
    deprecated BOOLEAN DEFAULT FALSE,
    
    release_notes TEXT,
    
    UNIQUE(plugin_id, major, minor, patch)
);

-- Plugin version history (track which versions were used when)
CREATE TABLE plugin_version_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    version_string TEXT NOT NULL,
    activated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deactivated_at DATETIME,
    reason TEXT,  -- 'upgrade', 'rollback', 'migration'
    
    INDEX idx_plugin_history (plugin_id, activated_at)
);
```

---

## 📱 TELEGRAM VERSION MANAGEMENT COMMANDS

```python
@telegram_handler('/version')
async def show_plugin_versions(update, context):
    """Show current plugin versions"""
    
    text = "📦 <b>Active Plugin Versions</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for plugin_id, version in plugin_registry.active_plugins.items():
        text += f"📌 <b>{plugin_id}</b>\n"
        text += f"├ Version: <code>{version.version_string}</code>\n"
        text += f"├ Released: {version.build_date.strftime('%Y-%m-%d')}\n"
        text += f"├ Features: {', '.join(version.features)}\n"
        text += f"└ Commit: <code>{version.commit_hash[:8]}</code>\n\n"
    
    await update.message.reply_text(text, parse_mode='HTML')

@telegram_handler('/upgrade')
async def upgrade_plugin_command(update, context):
    """Upgrade plugin: /upgrade <plugin_id> <version>"""
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "Usage: /upgrade <plugin_id> <version>\n"
            "Example: /upgrade combined_v3 3.2.0"
        )
        return
    
    plugin_id = context.args[0]
    target_version = context.args[1]
    
    success, message = plugin_registry.upgrade_plugin(plugin_id, target_version)
    
    await update.message.reply_text(message, parse_mode='HTML')

@telegram_handler('/rollback')
async def rollback_plugin_command(update, context):
    """Rollback plugin: /rollback <plugin_id>"""
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "Usage: /rollback <plugin_id>\n"
            "Example: /rollback combined_v3"
        )
        return
    
    plugin_id = context.args[0]
    
    success, message = plugin_registry.rollback_plugin(plugin_id)
    
    await update.message.reply_text(message, parse_mode='HTML')
```

---

## 🧪 VERSION TESTING STRATEGY

```python
import pytest

def test_version_compatibility():
    """Test version compatibility checks"""
    v3_0_0 = PluginVersion(
        plugin_id='combined_v3',
        major=3, minor=0, patch=0,
        # ... other fields
    )
    
    v3_1_0 = PluginVersion(
        plugin_id='combined_v3',
        major=3, minor=1, patch=0,
        # ... other fields
    )
    
    v4_0_0 = PluginVersion(
        plugin_id='combined_v3',
        major=4, minor=0, patch=0,
        # ... other fields
    )
    
    # Same major version = compatible
    assert v3_0_0.is_compatible_with(v3_1_0)
    assert v3_1_0.is_compatible_with(v3_0_0)
    
    # Different major version = incompatible
    assert not v3_0_0.is_compatible_with(v4_0_0)
    assert not v4_0_0.is_compatible_with(v3_0_0)

def test_version_comparison():
    """Test version ordering"""
    v1 = PluginVersion(plugin_id='test', major=3, minor=0, patch=0, ...)
    v2 = PluginVersion(plugin_id='test', major=3, minor=1, patch=0, ...)
    v3 = PluginVersion(plugin_id='test', major=3, minor=1, patch=1, ...)
    
    assert v1 < v2
    assert v2 < v3
    assert not v3 < v1
```

---

## ✅ COMPLETION CHECKLIST

- [x] `PluginVersion` dataclass with semantic versioning
- [x] `VersionedPluginRegistry` implementation
- [x] Compatibility checking logic
- [x] Upgrade/rollback functionality
- [x] Database schema for version tracking
- [x] Telegram commands (/version, /upgrade, /rollback)
- [x] Version testing framework

**Status:** ✅ READY FOR IMPLEMENTATION
