# DATABASE MIGRATION SCRIPTS & STRATEGIES

**Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Production-Ready Migration Framework  
**Priority:** 🟡 MEDIUM (Required for Safe Schema Evolution)

---

## 🎯 PURPOSE

Provide **safe, reversible, and version-controlled** database schema migrations for the 3-database architecture without downtime or data loss.

**Migration Scenarios:**
1. **Schema Changes:** Adding/modifying tables, columns, indexes
2. **Data Transformations:** Changing data formats, splitting/merging tables
3. **Version Upgrades:** V3 → V3.1, V6.0 → V6.1
4. **Emergency Rollbacks:** Reverting failed migrations

---

## 🏗️ MIGRATION FRAMEWORK ARCHITECTURE

```
/migrations/
├── /combined_v3/          # V3 Combined Logic DB migrations
│   ├── 001_initial_schema.sql
│   ├── 002_add_hybrid_sl.sql
│   └── rollback/
│       └── 002_rollback_hybrid_sl.sql
├── /price_action_v6/      # V6 Price Action DB migrations
│   ├── 001_initial_schema.sql
│   ├── 002_add_trend_pulse.sql
│   └── rollback/
│       └── 002_rollback_trend_pulse.sql
├── /central_system/       # Central Bot DB migrations
│   ├── 001_initial_schema.sql
│   └── rollback/
└── migration_manager.py   # Automated migration runner
```

---

## 📜 MIGRATION SCRIPT TEMPLATE

```sql
-- Migration: 002_add_hybrid_sl.sql
-- Database: zepix_combined.db
-- Applied: 2026-01-12
-- Description: Add hybrid SL columns to orders table

-- MIGRATION METADATA
-- Version: 002
-- Requires: 001_initial_schema.sql
-- Author: System
-- Reversible: YES

-- PRE-CHECKS
-- Ensure table exists
SELECT CASE 
    WHEN NOT EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='orders')
    THEN RAISE(ABORT, 'orders table does not exist')
END;

-- START TRANSACTION
BEGIN TRANSACTION;

-- MIGRATION STEPS
ALTER TABLE orders ADD COLUMN hybrid_sl_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE orders ADD COLUMN hybrid_sl_pips REAL DEFAULT 0;
ALTER TABLE orders ADD COLUMN order_a_ticket INTEGER;
ALTER TABLE orders ADD COLUMN order_b_ticket INTEGER;

-- CREATE INDEX for performance
CREATE INDEX IF NOT EXISTS idx_orders_hybrid_sl 
ON orders(hybrid_sl_enabled) 
WHERE hybrid_sl_enabled = TRUE;

-- UPDATE SCHEMA VERSION
INSERT INTO schema_migrations (version, applied_at, description)
VALUES ('002', CURRENT_TIMESTAMP, 'Add hybrid SL columns');

-- VERIFY MIGRATION
SELECT CASE
    WHEN NOT EXISTS (
        SELECT 1 FROM pragma_table_info('orders') 
        WHERE name = 'hybrid_sl_enabled'
    )
    THEN RAISE(ABORT, 'Migration verification failed: column not created')
END;

COMMIT;

-- POST-MIGRATION CHECKS
SELECT '✅ Migration 002 applied successfully' AS status;
SELECT COUNT(*) AS total_orders FROM orders;
```

---

## 🔄 ROLLBACK SCRIPT TEMPLATE

```sql
-- Rollback: 002_rollback_hybrid_sl.sql
-- Database: zepix_combined.db
-- Description: Remove hybrid SL columns

BEGIN TRANSACTION;

-- BACKUP DATA (if needed)
CREATE TABLE IF NOT EXISTS orders_backup_002 AS
SELECT * FROM orders;

-- REMOVE COLUMNS (SQLite limitation workaround)
-- SQLite doesn't support DROP COLUMN, so we recreate the table

-- Step 1: Create new table without hybrid SL columns
CREATE TABLE orders_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    ticket INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    order_type TEXT NOT NULL,
    lots REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl REAL,
    tp REAL,
    status TEXT DEFAULT 'OPEN',
    opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME,
    profit REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    -- Note: hybrid_sl columns removed
);

-- Step 2: Copy data (excluding hybrid SL columns)
INSERT INTO orders_new (
    id, plugin_id, ticket, symbol, order_type, lots, 
    entry_price, sl, tp, status, opened_at, closed_at, profit, created_at
)
SELECT 
    id, plugin_id, ticket, symbol, order_type, lots,
    entry_price, sl, tp, status, opened_at, closed_at, profit, created_at
FROM orders;

-- Step 3: Drop old table
DROP TABLE orders;

-- Step 4: Rename new table
ALTER TABLE orders_new RENAME TO orders;

-- Step 5: Recreate indexes (without hybrid SL index)
CREATE INDEX idx_orders_plugin ON orders(plugin_id);
CREATE INDEX idx_orders_ticket ON orders(ticket);
CREATE INDEX idx_orders_status ON orders(status);

-- Step 6: Remove migration record
DELETE FROM schema_migrations WHERE version = '002';

COMMIT;

SELECT '✅ Migration 002 rolled back successfully' AS status;
```

---

## 🐍 MIGRATION MANAGER (Python)

```python
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Automated database migration manager
    """
    
    def __init__(self, db_path: str, migrations_dir: str):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.conn = None
    
    def initialize_migration_tracking(self):
        """Create schema_migrations table if not exists"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at DATETIME NOT NULL,
                description TEXT,
                checksum TEXT,
                execution_time_ms INTEGER
            )
        """)
        
        self.conn.commit()
        logger.info(f"✅ Migration tracking initialized for {self.db_path}")
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of migrations not yet applied"""
        cursor = self.conn.cursor()
        
        # Get applied versions
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        applied_versions = {row[0] for row in cursor.fetchall()}
        
        # Get all migration files
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        # Filter out applied migrations
        pending = []
        for file in migration_files:
            version = file.stem.split('_')[0]  # Extract version from filename
            if version not in applied_versions:
                pending.append(str(file))
        
        return pending
    
    def apply_migration(self, migration_file: str) -> Tuple[bool, str]:
        """Apply a single migration file"""
        try:
            start_time = datetime.now()
            
            # Read migration SQL
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Extract metadata from comments
            version = Path(migration_file).stem.split('_')[0]
            description = self._extract_description(sql)
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.sha256(sql.encode()).hexdigest()
            
            logger.info(f"🔄 Applying migration {version}: {description}")
            
            # Execute migration
            cursor = self.conn.cursor()
            cursor.executescript(sql)
            
            # Calculate execution time
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            logger.info(f"✅ Migration {version} applied in {execution_time_ms}ms")
            
            return True, f"Migration {version} applied successfully"
            
        except Exception as e:
            self.conn.rollback()
            error_msg = f"❌ Migration {version} failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def rollback_migration(self, version: str) -> Tuple[bool, str]:
        """Rollback a specific migration"""
        try:
            rollback_file = self.migrations_dir / 'rollback' / f"{version}_rollback.sql"
            
            if not rollback_file.exists():
                return False, f"Rollback script not found for version {version}"
            
            logger.info(f"⏪ Rolling back migration {version}")
            
            # Read rollback SQL
            with open(rollback_file, 'r') as f:
                sql = f.read()
            
            # Execute rollback
            cursor = self.conn.cursor()
            cursor.executescript(sql)
            
            logger.info(f"✅ Migration {version} rolled back successfully")
            
            return True, f"Migration {version} rolled back"
            
        except Exception as e:
            self.conn.rollback()
            error_msg = f"❌ Rollback {version} failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def migrate_to_latest(self) -> dict:
        """Apply all pending migrations"""
        self.initialize_migration_tracking()
        
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ Database is up to date")
            return {
                'status': 'UP_TO_DATE',
                'applied': 0,
                'failed': 0
            }
        
        logger.info(f"📋 Found {len(pending)} pending migrations")
        
        results = {
            'status': 'SUCCESS',
            'applied': 0,
            'failed': 0,
            'migrations': []
        }
        
        for migration_file in pending:
            success, message = self.apply_migration(migration_file)
            
            results['migrations'].append({
                'file': migration_file,
                'success': success,
                'message': message
            })
            
            if success:
                results['applied'] += 1
            else:
                results['failed'] += 1
                results['status'] = 'PARTIAL'
                break  # Stop on first failure
        
        self.conn.close()
        
        return results
    
    def get_current_version(self) -> str:
        """Get latest applied migration version"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT version FROM schema_migrations 
            ORDER BY version DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        return result[0] if result else "000"
    
    def _extract_description(self, sql: str) -> str:
        """Extract description from migration SQL comments"""
        for line in sql.split('\n'):
            if line.startswith('-- Description:'):
                return line.replace('-- Description:', '').strip()
        return "No description"

# Usage Example
if __name__ == '__main__':
    # Migrate V3 Combined DB
    v3_manager = MigrationManager(
        db_path='databases/zepix_combined.db',
        migrations_dir='migrations/combined_v3'
    )
    
    v3_results = v3_manager.migrate_to_latest()
    print(f"V3 DB Migration: {v3_results['status']}")
    print(f"Applied: {v3_results['applied']}, Failed: {v3_results['failed']}")
    
    # Migrate V6 Price Action DB
    v6_manager = MigrationManager(
        db_path='databases/zepix_price_action.db',
        migrations_dir='migrations/price_action_v6'
    )
    
    v6_results = v6_manager.migrate_to_latest()
    print(f"V6 DB Migration: {v6_results['status']}")
```

---

## 🧪 MIGRATION TESTING STRATEGY

```python
import pytest
import sqlite3
import tempfile
import shutil

class TestMigrations:
    """Test migration scripts"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary test database"""
        temp_dir = tempfile.mkdtemp()
        db_path = f"{temp_dir}/test.db"
        yield db_path
        shutil.rmtree(temp_dir)
    
    def test_migration_002_apply(self, temp_db):
        """Test applying migration 002"""
        # Setup: Apply migration 001 (initial schema)
        manager = MigrationManager(temp_db, 'migrations/combined_v3')
        manager.apply_migration('migrations/combined_v3/001_initial_schema.sql')
        
        # Act: Apply migration 002
        success, msg = manager.apply_migration('migrations/combined_v3/002_add_hybrid_sl.sql')
        
        # Assert
        assert success, f"Migration failed: {msg}"
        
        # Verify columns exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(orders)")
        columns = {row[1] for row in cursor.fetchall()}
        
        assert 'hybrid_sl_enabled' in columns
        assert 'hybrid_sl_pips' in columns
        assert 'order_a_ticket' in columns
        assert 'order_b_ticket' in columns
    
    def test_migration_002_rollback(self, temp_db):
        """Test rolling back migration 002"""
        # Setup: Apply migrations 001 and 002
        manager = MigrationManager(temp_db, 'migrations/combined_v3')
        manager.apply_migration('migrations/combined_v3/001_initial_schema.sql')
        manager.apply_migration('migrations/combined_v3/002_add_hybrid_sl.sql')
        
        # Act: Rollback migration 002
        success, msg = manager.rollback_migration('002')
        
        # Assert
        assert success, f"Rollback failed: {msg}"
        
        # Verify columns removed
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(orders)")
        columns = {row[1] for row in cursor.fetchall()}
        
        assert 'hybrid_sl_enabled' not in columns
```

---

## 📊 MIGRATION STATUS TELEGRAM COMMAND

```python
@telegram_handler('/migration_status')
async def show_migration_status(update, context):
    """Show migration status for all databases"""
    
    dbs = {
        'V3 Combined': 'databases/zepix_combined.db',
        'V6 Price Action': 'databases/zepix_price_action.db',
        'Central System': 'databases/zepix_bot.db'
    }
    
    text = "🗄️ <b>Database Migration Status</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for name, db_path in dbs.items():
        manager = MigrationManager(db_path, f'migrations/{name.lower().replace(" ", "_")}')
        manager.initialize_migration_tracking()
        
        current_version = manager.get_current_version()
        pending = manager.get_pending_migrations()
        
        status_emoji = "🟢" if len(pending) == 0 else "🟡"
        
        text += f"{status_emoji} <b>{name}</b>\n"
        text += f"├ Current Version: {current_version}\n"
        text += f"├ Pending Migrations: {len(pending)}\n"
        
        if pending:
            text += "└ Next: " + Path(pending[0]).stem + "\n\n"
        else:
            text += "└ Status: Up to date ✅\n\n"
    
    await update.message.reply_text(text, parse_mode='HTML')
```

---

## ✅ COMPLETION CHECKLIST

- [x] Migration script SQL template
- [x] Rollback script SQL template
- [x] `MigrationManager` Python class
- [x] Migration tracking table schema
- [x] Pending migrations detection
- [x] Apply/rollback functionality
- [x] Migration testing framework
- [x] Telegram `/migration_status` command
- [x] Folder structure for organized migrations

**Status:** ✅ READY FOR IMPLEMENTATION
