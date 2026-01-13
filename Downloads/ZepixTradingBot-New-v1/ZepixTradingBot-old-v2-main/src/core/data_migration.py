"""
Document 26: Data Migration Scripts & Strategies

Complete V2 to V5 Migration System with:
1. MigrationManager - Orchestrator for the full migration process
2. DataMapper - Transform V2 flat structure -> V5 Relational Schema
3. UserMigrator - Migrate users, permissions, and sessions
4. TradeHistoryMigrator - Archive old trades into Central DB
5. ConfigMigrator - Convert old config.json to new modular format
6. BackupManager - Automatic backup before migration (safety nets)
7. MigrationVerifier - Row count checks and data integrity verification
8. RollbackManager - One-click restore if migration fails
"""

import sqlite3
import os
import json
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class MigrationStatus(Enum):
    """Migration status enum"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    SKIPPED = "SKIPPED"


class MigrationPhase(Enum):
    """Migration phase enum"""
    BACKUP = "BACKUP"
    SCHEMA = "SCHEMA"
    DATA = "DATA"
    VERIFICATION = "VERIFICATION"
    CLEANUP = "CLEANUP"


class DataType(Enum):
    """Data type for migration"""
    USERS = "USERS"
    TRADES = "TRADES"
    ORDERS = "ORDERS"
    SESSIONS = "SESSIONS"
    CONFIG = "CONFIG"
    PERMISSIONS = "PERMISSIONS"
    ALERTS = "ALERTS"
    CHAINS = "CHAINS"


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class MigrationRecord:
    """Record of a single migration"""
    version: str
    description: str
    applied_at: Optional[datetime] = None
    checksum: str = ""
    execution_time_ms: int = 0
    status: MigrationStatus = MigrationStatus.PENDING
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "description": self.description,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "checksum": self.checksum,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status.value,
            "error_message": self.error_message
        }


@dataclass
class BackupInfo:
    """Information about a backup"""
    backup_id: str
    source_path: str
    backup_path: str
    created_at: datetime
    size_bytes: int
    checksum: str
    is_valid: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "backup_id": self.backup_id,
            "source_path": self.source_path,
            "backup_path": self.backup_path,
            "created_at": self.created_at.isoformat(),
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "is_valid": self.is_valid
        }


@dataclass
class VerificationResult:
    """Result of migration verification"""
    is_valid: bool
    source_count: int
    target_count: int
    missing_records: int = 0
    extra_records: int = 0
    data_type: DataType = DataType.TRADES
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "source_count": self.source_count,
            "target_count": self.target_count,
            "missing_records": self.missing_records,
            "extra_records": self.extra_records,
            "data_type": self.data_type.value,
            "details": self.details
        }


@dataclass
class MigrationResult:
    """Result of a migration operation"""
    success: bool
    phase: MigrationPhase
    message: str
    records_processed: int = 0
    records_failed: int = 0
    execution_time_ms: int = 0
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "phase": self.phase.value,
            "message": self.message,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "execution_time_ms": self.execution_time_ms,
            "details": self.details
        }


@dataclass
class MigrationPlan:
    """Plan for a complete migration"""
    source_db: str
    target_dbs: List[str]
    phases: List[MigrationPhase]
    data_types: List[DataType]
    backup_enabled: bool = True
    verification_enabled: bool = True
    dry_run: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_db": self.source_db,
            "target_dbs": self.target_dbs,
            "phases": [p.value for p in self.phases],
            "data_types": [d.value for d in self.data_types],
            "backup_enabled": self.backup_enabled,
            "verification_enabled": self.verification_enabled,
            "dry_run": self.dry_run
        }


# ============================================================================
# BACKUP MANAGER
# ============================================================================

class BackupManager:
    """
    Manages database backups before migration.
    Safety net for automatic backup and restore.
    """
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._backups: Dict[str, BackupInfo] = {}
    
    async def create_backup(self, db_path: str, backup_suffix: str = "") -> BackupInfo:
        """Create a backup of the database"""
        source_path = Path(db_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{source_path.stem}_{timestamp}{backup_suffix}"
        backup_path = self.backup_dir / f"{backup_id}.db.bak"
        
        logger.info(f"Creating backup: {backup_path}")
        
        shutil.copy2(source_path, backup_path)
        
        size_bytes = backup_path.stat().st_size
        checksum = self._calculate_checksum(backup_path)
        
        backup_info = BackupInfo(
            backup_id=backup_id,
            source_path=str(source_path),
            backup_path=str(backup_path),
            created_at=datetime.now(),
            size_bytes=size_bytes,
            checksum=checksum,
            is_valid=True
        )
        
        self._backups[backup_id] = backup_info
        
        logger.info(f"Backup created: {backup_id} ({size_bytes} bytes)")
        
        return backup_info
    
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore a database from backup"""
        if backup_id not in self._backups:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        backup_info = self._backups[backup_id]
        backup_path = Path(backup_info.backup_path)
        source_path = Path(backup_info.source_path)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        current_checksum = self._calculate_checksum(backup_path)
        if current_checksum != backup_info.checksum:
            logger.error(f"Backup checksum mismatch: {backup_id}")
            return False
        
        logger.info(f"Restoring backup: {backup_id} -> {source_path}")
        
        shutil.copy2(backup_path, source_path)
        
        logger.info(f"Backup restored: {backup_id}")
        
        return True
    
    async def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        if backup_id not in self._backups:
            return False
        
        backup_info = self._backups[backup_id]
        backup_path = Path(backup_info.backup_path)
        
        if not backup_path.exists():
            backup_info.is_valid = False
            return False
        
        current_checksum = self._calculate_checksum(backup_path)
        is_valid = current_checksum == backup_info.checksum
        backup_info.is_valid = is_valid
        
        return is_valid
    
    async def list_backups(self) -> List[BackupInfo]:
        """List all backups"""
        return list(self._backups.values())
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup"""
        if backup_id not in self._backups:
            return False
        
        backup_info = self._backups[backup_id]
        backup_path = Path(backup_info.backup_path)
        
        if backup_path.exists():
            backup_path.unlink()
        
        del self._backups[backup_id]
        
        logger.info(f"Backup deleted: {backup_id}")
        
        return True
    
    async def cleanup_old_backups(self, max_age_days: int = 7) -> int:
        """Clean up backups older than max_age_days"""
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        deleted = 0
        
        for backup_id in list(self._backups.keys()):
            backup_info = self._backups[backup_id]
            if backup_info.created_at.timestamp() < cutoff:
                await self.delete_backup(backup_id)
                deleted += 1
        
        return deleted
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()


# ============================================================================
# DATA MAPPER
# ============================================================================

class DataMapper:
    """
    Transform V2 flat structure to V5 Relational Schema.
    Maps old table structures to new normalized tables.
    """
    
    def __init__(self):
        self._mappings: Dict[str, Dict[str, str]] = {}
        self._transformers: Dict[str, Callable] = {}
        self._setup_default_mappings()
    
    def _setup_default_mappings(self):
        """Setup default V2 to V5 column mappings"""
        self._mappings["trades"] = {
            "id": "id",
            "ticket": "ticket",
            "symbol": "symbol",
            "type": "order_type",
            "lots": "lots",
            "open_price": "entry_price",
            "close_price": "exit_price",
            "sl": "stop_loss",
            "tp": "take_profit",
            "profit": "profit",
            "commission": "commission",
            "swap": "swap",
            "open_time": "opened_at",
            "close_time": "closed_at",
            "magic": "magic_number",
            "comment": "comment"
        }
        
        self._mappings["orders"] = {
            "id": "id",
            "ticket": "ticket",
            "symbol": "symbol",
            "type": "order_type",
            "lots": "lots",
            "price": "entry_price",
            "sl": "stop_loss",
            "tp": "take_profit",
            "status": "status",
            "time": "created_at"
        }
        
        self._mappings["users"] = {
            "id": "id",
            "telegram_id": "telegram_id",
            "username": "username",
            "first_name": "first_name",
            "last_name": "last_name",
            "is_admin": "is_admin",
            "is_active": "is_active",
            "created_at": "created_at"
        }
        
        self._mappings["sessions"] = {
            "id": "id",
            "user_id": "user_id",
            "session_token": "session_token",
            "created_at": "created_at",
            "expires_at": "expires_at",
            "is_active": "is_active"
        }
    
    def add_mapping(self, table: str, old_column: str, new_column: str):
        """Add a column mapping"""
        if table not in self._mappings:
            self._mappings[table] = {}
        self._mappings[table][old_column] = new_column
    
    def add_transformer(self, table: str, transformer: Callable):
        """Add a row transformer function"""
        self._transformers[table] = transformer
    
    def get_mapping(self, table: str) -> Dict[str, str]:
        """Get column mapping for a table"""
        return self._mappings.get(table, {})
    
    async def map_row(self, table: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map a single row from V2 to V5 format"""
        mapping = self.get_mapping(table)
        
        if not mapping:
            return row
        
        mapped_row = {}
        for old_col, new_col in mapping.items():
            if old_col in row:
                mapped_row[new_col] = row[old_col]
        
        if table in self._transformers:
            mapped_row = self._transformers[table](mapped_row)
        
        return mapped_row
    
    async def map_rows(self, table: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple rows from V2 to V5 format"""
        mapped_rows = []
        for row in rows:
            mapped_row = await self.map_row(table, row)
            mapped_rows.append(mapped_row)
        return mapped_rows
    
    def get_v5_schema(self, table: str) -> str:
        """Get V5 schema for a table"""
        schemas = {
            "trades": """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL DEFAULT 'v3_combined',
                    ticket INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    lots REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    profit REAL DEFAULT 0,
                    commission REAL DEFAULT 0,
                    swap REAL DEFAULT 0,
                    opened_at DATETIME,
                    closed_at DATETIME,
                    magic_number INTEGER,
                    comment TEXT,
                    status TEXT DEFAULT 'OPEN',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "orders": """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL DEFAULT 'v3_combined',
                    ticket INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    lots REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    status TEXT DEFAULT 'PENDING',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "sessions": """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """,
            "permissions": """
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    permission_name TEXT NOT NULL,
                    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    granted_by INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """,
            "trade_history": """
                CREATE TABLE IF NOT EXISTS trade_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_id INTEGER,
                    plugin_id TEXT,
                    ticket INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    lots REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    profit REAL DEFAULT 0,
                    commission REAL DEFAULT 0,
                    swap REAL DEFAULT 0,
                    opened_at DATETIME,
                    closed_at DATETIME,
                    magic_number INTEGER,
                    comment TEXT,
                    migrated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source_db TEXT
                )
            """
        }
        return schemas.get(table, "")


# ============================================================================
# USER MIGRATOR
# ============================================================================

class UserMigrator:
    """
    Migrate users, permissions, and sessions from V2 to V5.
    """
    
    def __init__(self, data_mapper: DataMapper):
        self.data_mapper = data_mapper
        self._migrated_users: Dict[int, int] = {}
    
    async def migrate_users(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection
    ) -> MigrationResult:
        """Migrate all users from V2 to V5"""
        start_time = datetime.now()
        records_processed = 0
        records_failed = 0
        
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            target_cursor.execute(self.data_mapper.get_v5_schema("users"))
            target_conn.commit()
            
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not source_cursor.fetchone():
                return MigrationResult(
                    success=True,
                    phase=MigrationPhase.DATA,
                    message="No users table in source database",
                    records_processed=0
                )
            
            source_cursor.execute("SELECT * FROM users")
            columns = [desc[0] for desc in source_cursor.description]
            
            for row in source_cursor.fetchall():
                try:
                    row_dict = dict(zip(columns, row))
                    mapped_row = await self.data_mapper.map_row("users", row_dict)
                    
                    cols = ", ".join(mapped_row.keys())
                    placeholders = ", ".join(["?" for _ in mapped_row])
                    
                    target_cursor.execute(
                        f"INSERT OR REPLACE INTO users ({cols}) VALUES ({placeholders})",
                        list(mapped_row.values())
                    )
                    
                    if "id" in row_dict and "id" in mapped_row:
                        self._migrated_users[row_dict["id"]] = mapped_row["id"]
                    
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Failed to migrate user: {e}")
                    records_failed += 1
            
            target_conn.commit()
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=records_failed == 0,
                phase=MigrationPhase.DATA,
                message=f"Migrated {records_processed} users",
                records_processed=records_processed,
                records_failed=records_failed,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"User migration failed: {e}")
            return MigrationResult(
                success=False,
                phase=MigrationPhase.DATA,
                message=f"User migration failed: {e}",
                records_processed=records_processed,
                records_failed=records_failed
            )
    
    async def migrate_permissions(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection
    ) -> MigrationResult:
        """Migrate user permissions from V2 to V5"""
        start_time = datetime.now()
        records_processed = 0
        records_failed = 0
        
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            target_cursor.execute(self.data_mapper.get_v5_schema("permissions"))
            target_conn.commit()
            
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permissions'")
            if not source_cursor.fetchone():
                return MigrationResult(
                    success=True,
                    phase=MigrationPhase.DATA,
                    message="No permissions table in source database",
                    records_processed=0
                )
            
            source_cursor.execute("SELECT * FROM permissions")
            columns = [desc[0] for desc in source_cursor.description]
            
            for row in source_cursor.fetchall():
                try:
                    row_dict = dict(zip(columns, row))
                    
                    if "user_id" in row_dict and row_dict["user_id"] in self._migrated_users:
                        row_dict["user_id"] = self._migrated_users[row_dict["user_id"]]
                    
                    cols = ", ".join(row_dict.keys())
                    placeholders = ", ".join(["?" for _ in row_dict])
                    
                    target_cursor.execute(
                        f"INSERT OR REPLACE INTO permissions ({cols}) VALUES ({placeholders})",
                        list(row_dict.values())
                    )
                    
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Failed to migrate permission: {e}")
                    records_failed += 1
            
            target_conn.commit()
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=records_failed == 0,
                phase=MigrationPhase.DATA,
                message=f"Migrated {records_processed} permissions",
                records_processed=records_processed,
                records_failed=records_failed,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Permission migration failed: {e}")
            return MigrationResult(
                success=False,
                phase=MigrationPhase.DATA,
                message=f"Permission migration failed: {e}",
                records_processed=records_processed,
                records_failed=records_failed
            )
    
    async def migrate_sessions(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection
    ) -> MigrationResult:
        """Migrate user sessions from V2 to V5"""
        start_time = datetime.now()
        records_processed = 0
        records_failed = 0
        
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            target_cursor.execute(self.data_mapper.get_v5_schema("sessions"))
            target_conn.commit()
            
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            if not source_cursor.fetchone():
                return MigrationResult(
                    success=True,
                    phase=MigrationPhase.DATA,
                    message="No sessions table in source database",
                    records_processed=0
                )
            
            source_cursor.execute("SELECT * FROM sessions")
            columns = [desc[0] for desc in source_cursor.description]
            
            for row in source_cursor.fetchall():
                try:
                    row_dict = dict(zip(columns, row))
                    mapped_row = await self.data_mapper.map_row("sessions", row_dict)
                    
                    if "user_id" in mapped_row and mapped_row["user_id"] in self._migrated_users:
                        mapped_row["user_id"] = self._migrated_users[mapped_row["user_id"]]
                    
                    cols = ", ".join(mapped_row.keys())
                    placeholders = ", ".join(["?" for _ in mapped_row])
                    
                    target_cursor.execute(
                        f"INSERT OR REPLACE INTO sessions ({cols}) VALUES ({placeholders})",
                        list(mapped_row.values())
                    )
                    
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Failed to migrate session: {e}")
                    records_failed += 1
            
            target_conn.commit()
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=records_failed == 0,
                phase=MigrationPhase.DATA,
                message=f"Migrated {records_processed} sessions",
                records_processed=records_processed,
                records_failed=records_failed,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Session migration failed: {e}")
            return MigrationResult(
                success=False,
                phase=MigrationPhase.DATA,
                message=f"Session migration failed: {e}",
                records_processed=records_processed,
                records_failed=records_failed
            )
    
    def get_user_id_mapping(self) -> Dict[int, int]:
        """Get mapping of old user IDs to new user IDs"""
        return self._migrated_users.copy()


# ============================================================================
# TRADE HISTORY MIGRATOR
# ============================================================================

class TradeHistoryMigrator:
    """
    Archive old trades into the Central DB (trade_history table).
    """
    
    def __init__(self, data_mapper: DataMapper):
        self.data_mapper = data_mapper
        self._migrated_trades: int = 0
    
    async def migrate_trades(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection,
        source_db_name: str = "v2_database"
    ) -> MigrationResult:
        """Migrate all trades from V2 to V5 trade_history"""
        start_time = datetime.now()
        records_processed = 0
        records_failed = 0
        
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            target_cursor.execute(self.data_mapper.get_v5_schema("trade_history"))
            target_conn.commit()
            
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
            if not source_cursor.fetchone():
                return MigrationResult(
                    success=True,
                    phase=MigrationPhase.DATA,
                    message="No trades table in source database",
                    records_processed=0
                )
            
            source_cursor.execute("SELECT * FROM trades")
            columns = [desc[0] for desc in source_cursor.description]
            
            for row in source_cursor.fetchall():
                try:
                    row_dict = dict(zip(columns, row))
                    mapped_row = await self.data_mapper.map_row("trades", row_dict)
                    
                    mapped_row["original_id"] = row_dict.get("id")
                    mapped_row["source_db"] = source_db_name
                    mapped_row["migrated_at"] = datetime.now().isoformat()
                    
                    if "plugin_id" not in mapped_row:
                        mapped_row["plugin_id"] = "v3_combined"
                    
                    cols = ", ".join(mapped_row.keys())
                    placeholders = ", ".join(["?" for _ in mapped_row])
                    
                    target_cursor.execute(
                        f"INSERT INTO trade_history ({cols}) VALUES ({placeholders})",
                        list(mapped_row.values())
                    )
                    
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Failed to migrate trade: {e}")
                    records_failed += 1
            
            target_conn.commit()
            self._migrated_trades = records_processed
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=records_failed == 0,
                phase=MigrationPhase.DATA,
                message=f"Archived {records_processed} trades to trade_history",
                records_processed=records_processed,
                records_failed=records_failed,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Trade migration failed: {e}")
            return MigrationResult(
                success=False,
                phase=MigrationPhase.DATA,
                message=f"Trade migration failed: {e}",
                records_processed=records_processed,
                records_failed=records_failed
            )
    
    async def migrate_orders(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection
    ) -> MigrationResult:
        """Migrate orders from V2 to V5"""
        start_time = datetime.now()
        records_processed = 0
        records_failed = 0
        
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            target_cursor.execute(self.data_mapper.get_v5_schema("orders"))
            target_conn.commit()
            
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            if not source_cursor.fetchone():
                return MigrationResult(
                    success=True,
                    phase=MigrationPhase.DATA,
                    message="No orders table in source database",
                    records_processed=0
                )
            
            source_cursor.execute("SELECT * FROM orders")
            columns = [desc[0] for desc in source_cursor.description]
            
            for row in source_cursor.fetchall():
                try:
                    row_dict = dict(zip(columns, row))
                    mapped_row = await self.data_mapper.map_row("orders", row_dict)
                    
                    if "plugin_id" not in mapped_row:
                        mapped_row["plugin_id"] = "v3_combined"
                    
                    cols = ", ".join(mapped_row.keys())
                    placeholders = ", ".join(["?" for _ in mapped_row])
                    
                    target_cursor.execute(
                        f"INSERT OR REPLACE INTO orders ({cols}) VALUES ({placeholders})",
                        list(mapped_row.values())
                    )
                    
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Failed to migrate order: {e}")
                    records_failed += 1
            
            target_conn.commit()
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=records_failed == 0,
                phase=MigrationPhase.DATA,
                message=f"Migrated {records_processed} orders",
                records_processed=records_processed,
                records_failed=records_failed,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Order migration failed: {e}")
            return MigrationResult(
                success=False,
                phase=MigrationPhase.DATA,
                message=f"Order migration failed: {e}",
                records_processed=records_processed,
                records_failed=records_failed
            )
    
    def get_migrated_trade_count(self) -> int:
        """Get count of migrated trades"""
        return self._migrated_trades


# ============================================================================
# CONFIG MIGRATOR
# ============================================================================

class ConfigMigrator:
    """
    Convert old config.json values to new modular config format.
    """
    
    def __init__(self):
        self._old_config: Dict[str, Any] = {}
        self._new_config: Dict[str, Any] = {}
    
    async def load_old_config(self, config_path: str) -> bool:
        """Load old config.json file"""
        try:
            with open(config_path, 'r') as f:
                self._old_config = json.load(f)
            logger.info(f"Loaded old config from {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load old config: {e}")
            return False
    
    async def migrate_config(self) -> Dict[str, Any]:
        """Migrate old config to new modular format"""
        self._new_config = {
            "version": "5.0",
            "migrated_at": datetime.now().isoformat(),
            "system": {},
            "trading": {},
            "telegram": {},
            "plugins": {},
            "risk": {},
            "database": {}
        }
        
        self._migrate_system_config()
        self._migrate_trading_config()
        self._migrate_telegram_config()
        self._migrate_plugin_config()
        self._migrate_risk_config()
        self._migrate_database_config()
        
        return self._new_config
    
    def _migrate_system_config(self):
        """Migrate system configuration"""
        old = self._old_config
        
        self._new_config["system"] = {
            "debug": old.get("debug", False),
            "log_level": old.get("log_level", "INFO"),
            "timezone": old.get("timezone", "Asia/Kolkata"),
            "health_check_interval": old.get("health_check_interval", 30),
            "max_workers": old.get("max_workers", 4)
        }
    
    def _migrate_trading_config(self):
        """Migrate trading configuration"""
        old = self._old_config
        
        self._new_config["trading"] = {
            "enabled": old.get("trading_enabled", True),
            "symbols": old.get("symbols", []),
            "default_lot_size": old.get("lot_size", 0.01),
            "max_positions": old.get("max_positions", 10),
            "max_daily_trades": old.get("max_daily_trades", 50),
            "trading_hours": {
                "start": old.get("trading_start", "00:00"),
                "end": old.get("trading_end", "23:59")
            },
            "mt5": {
                "server": old.get("mt5_server", ""),
                "login": old.get("mt5_login", 0),
                "timeout": old.get("mt5_timeout", 60000)
            }
        }
    
    def _migrate_telegram_config(self):
        """Migrate Telegram configuration"""
        old = self._old_config
        
        self._new_config["telegram"] = {
            "enabled": old.get("telegram_enabled", True),
            "bots": {
                "controller": {
                    "token": old.get("telegram_token", ""),
                    "enabled": True
                },
                "notifier": {
                    "token": old.get("notifier_token", old.get("telegram_token", "")),
                    "enabled": True
                },
                "analytics": {
                    "token": old.get("analytics_token", old.get("telegram_token", "")),
                    "enabled": True
                }
            },
            "admin_ids": old.get("admin_ids", []),
            "allowed_users": old.get("allowed_users", []),
            "rate_limit": {
                "messages_per_second": old.get("rate_limit", 30),
                "burst_limit": old.get("burst_limit", 20)
            }
        }
    
    def _migrate_plugin_config(self):
        """Migrate plugin configuration"""
        old = self._old_config
        
        self._new_config["plugins"] = {
            "v3_combined": {
                "enabled": old.get("v3_enabled", True),
                "database": "zepix_combined.db",
                "settings": {
                    "logic1_enabled": old.get("logic1_enabled", True),
                    "logic2_enabled": old.get("logic2_enabled", True),
                    "logic3_enabled": old.get("logic3_enabled", True),
                    "dual_order_enabled": old.get("dual_order", True),
                    "hybrid_sl_enabled": old.get("hybrid_sl", True)
                }
            },
            "v6_price_action": {
                "enabled": old.get("v6_enabled", False),
                "database": "zepix_price_action.db",
                "settings": {
                    "timeframes": old.get("v6_timeframes", ["1M", "5M", "15M", "1H"])
                }
            }
        }
    
    def _migrate_risk_config(self):
        """Migrate risk configuration"""
        old = self._old_config
        
        self._new_config["risk"] = {
            "max_risk_per_trade_pct": old.get("risk_per_trade", 2.0),
            "max_daily_loss_pct": old.get("max_daily_loss", 5.0),
            "max_drawdown_pct": old.get("max_drawdown", 20.0),
            "stop_loss": {
                "default_pips": old.get("default_sl_pips", 50),
                "max_pips": old.get("max_sl_pips", 100)
            },
            "take_profit": {
                "default_pips": old.get("default_tp_pips", 100),
                "max_pips": old.get("max_tp_pips", 500)
            }
        }
    
    def _migrate_database_config(self):
        """Migrate database configuration"""
        old = self._old_config
        
        self._new_config["database"] = {
            "central": {
                "path": "databases/zepix_bot.db",
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "v3_combined": {
                "path": old.get("database_path", "databases/zepix_combined.db")
            },
            "v6_price_action": {
                "path": "databases/zepix_price_action.db"
            }
        }
    
    async def save_new_config(self, output_dir: str) -> Dict[str, str]:
        """Save new modular config files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        main_config_path = output_path / "config.json"
        with open(main_config_path, 'w') as f:
            json.dump(self._new_config, f, indent=2)
        saved_files["main"] = str(main_config_path)
        
        for section in ["system", "trading", "telegram", "plugins", "risk", "database"]:
            section_path = output_path / f"{section}_config.json"
            with open(section_path, 'w') as f:
                json.dump({section: self._new_config[section]}, f, indent=2)
            saved_files[section] = str(section_path)
        
        logger.info(f"Saved {len(saved_files)} config files to {output_dir}")
        
        return saved_files
    
    def get_old_config(self) -> Dict[str, Any]:
        """Get old config"""
        return self._old_config.copy()
    
    def get_new_config(self) -> Dict[str, Any]:
        """Get new config"""
        return self._new_config.copy()


# ============================================================================
# MIGRATION VERIFIER
# ============================================================================

class MigrationVerifier:
    """
    Verify migration integrity with row count checks and data validation.
    """
    
    def __init__(self):
        self._verification_results: List[VerificationResult] = []
    
    async def verify_row_counts(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection,
        table_mappings: Dict[str, str]
    ) -> List[VerificationResult]:
        """Verify row counts match between source and target"""
        results = []
        
        for source_table, target_table in table_mappings.items():
            result = await self._verify_table_count(
                source_conn, target_conn, source_table, target_table
            )
            results.append(result)
            self._verification_results.append(result)
        
        return results
    
    async def _verify_table_count(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection,
        source_table: str,
        target_table: str
    ) -> VerificationResult:
        """Verify row count for a single table"""
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            source_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{source_table}'")
            if not source_cursor.fetchone():
                return VerificationResult(
                    is_valid=True,
                    source_count=0,
                    target_count=0,
                    details={"message": f"Source table {source_table} does not exist"}
                )
            
            source_cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            source_count = source_cursor.fetchone()[0]
            
            target_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
            if not target_cursor.fetchone():
                return VerificationResult(
                    is_valid=False,
                    source_count=source_count,
                    target_count=0,
                    missing_records=source_count,
                    details={"message": f"Target table {target_table} does not exist"}
                )
            
            target_cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
            target_count = target_cursor.fetchone()[0]
            
            is_valid = source_count == target_count
            missing = max(0, source_count - target_count)
            extra = max(0, target_count - source_count)
            
            return VerificationResult(
                is_valid=is_valid,
                source_count=source_count,
                target_count=target_count,
                missing_records=missing,
                extra_records=extra,
                details={
                    "source_table": source_table,
                    "target_table": target_table
                }
            )
            
        except Exception as e:
            logger.error(f"Verification failed for {source_table} -> {target_table}: {e}")
            return VerificationResult(
                is_valid=False,
                source_count=0,
                target_count=0,
                details={"error": str(e)}
            )
    
    async def verify_data_integrity(
        self,
        source_conn: sqlite3.Connection,
        target_conn: sqlite3.Connection,
        table: str,
        key_column: str = "id"
    ) -> VerificationResult:
        """Verify data integrity by comparing key columns"""
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            source_cursor.execute(f"SELECT {key_column} FROM {table}")
            source_keys = {row[0] for row in source_cursor.fetchall()}
            
            target_cursor.execute(f"SELECT {key_column} FROM {table}")
            target_keys = {row[0] for row in target_cursor.fetchall()}
            
            missing = source_keys - target_keys
            extra = target_keys - source_keys
            
            is_valid = len(missing) == 0
            
            return VerificationResult(
                is_valid=is_valid,
                source_count=len(source_keys),
                target_count=len(target_keys),
                missing_records=len(missing),
                extra_records=len(extra),
                details={
                    "table": table,
                    "key_column": key_column,
                    "missing_keys": list(missing)[:10],
                    "extra_keys": list(extra)[:10]
                }
            )
            
        except Exception as e:
            logger.error(f"Data integrity verification failed for {table}: {e}")
            return VerificationResult(
                is_valid=False,
                source_count=0,
                target_count=0,
                details={"error": str(e)}
            )
    
    async def generate_verification_report(self) -> Dict[str, Any]:
        """Generate a verification report"""
        total_results = len(self._verification_results)
        valid_results = sum(1 for r in self._verification_results if r.is_valid)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_verifications": total_results,
            "passed": valid_results,
            "failed": total_results - valid_results,
            "success_rate": (valid_results / total_results * 100) if total_results > 0 else 0,
            "results": [r.to_dict() for r in self._verification_results]
        }
    
    def get_results(self) -> List[VerificationResult]:
        """Get all verification results"""
        return self._verification_results.copy()
    
    def clear_results(self):
        """Clear verification results"""
        self._verification_results.clear()


# ============================================================================
# ROLLBACK MANAGER
# ============================================================================

class RollbackManager:
    """
    One-click restore if migration fails.
    """
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self._rollback_points: Dict[str, str] = {}
    
    async def create_rollback_point(self, db_path: str, point_name: str) -> str:
        """Create a rollback point before migration"""
        backup_info = await self.backup_manager.create_backup(db_path, f"_rollback_{point_name}")
        self._rollback_points[point_name] = backup_info.backup_id
        logger.info(f"Created rollback point: {point_name}")
        return backup_info.backup_id
    
    async def rollback_to_point(self, point_name: str) -> bool:
        """Rollback to a specific point"""
        if point_name not in self._rollback_points:
            logger.error(f"Rollback point not found: {point_name}")
            return False
        
        backup_id = self._rollback_points[point_name]
        success = await self.backup_manager.restore_backup(backup_id)
        
        if success:
            logger.info(f"Rolled back to point: {point_name}")
        else:
            logger.error(f"Rollback failed for point: {point_name}")
        
        return success
    
    async def rollback_all(self) -> Dict[str, bool]:
        """Rollback all databases to their rollback points"""
        results = {}
        
        for point_name in self._rollback_points:
            success = await self.rollback_to_point(point_name)
            results[point_name] = success
        
        return results
    
    async def list_rollback_points(self) -> Dict[str, str]:
        """List all rollback points"""
        return self._rollback_points.copy()
    
    async def delete_rollback_point(self, point_name: str) -> bool:
        """Delete a rollback point"""
        if point_name not in self._rollback_points:
            return False
        
        backup_id = self._rollback_points[point_name]
        success = await self.backup_manager.delete_backup(backup_id)
        
        if success:
            del self._rollback_points[point_name]
        
        return success
    
    async def cleanup_rollback_points(self) -> int:
        """Clean up all rollback points"""
        deleted = 0
        
        for point_name in list(self._rollback_points.keys()):
            if await self.delete_rollback_point(point_name):
                deleted += 1
        
        return deleted


# ============================================================================
# MIGRATION MANAGER (ORCHESTRATOR)
# ============================================================================

class MigrationManager:
    """
    Orchestrator for the full V2 to V5 migration process.
    Coordinates all migration components.
    """
    
    def __init__(
        self,
        source_db_path: str,
        target_db_path: str,
        backup_dir: str = "backups",
        migrations_dir: str = "migrations"
    ):
        self.source_db_path = source_db_path
        self.target_db_path = target_db_path
        self.migrations_dir = Path(migrations_dir)
        
        self.backup_manager = BackupManager(backup_dir)
        self.data_mapper = DataMapper()
        self.user_migrator = UserMigrator(self.data_mapper)
        self.trade_migrator = TradeHistoryMigrator(self.data_mapper)
        self.config_migrator = ConfigMigrator()
        self.verifier = MigrationVerifier()
        self.rollback_manager = RollbackManager(self.backup_manager)
        
        self._migration_history: List[MigrationRecord] = []
        self._current_phase: Optional[MigrationPhase] = None
        self._is_running: bool = False
        
        self._source_conn: Optional[sqlite3.Connection] = None
        self._target_conn: Optional[sqlite3.Connection] = None
    
    async def initialize_migration_tracking(self):
        """Create schema_migrations table if not exists"""
        if self._target_conn is None:
            self._target_conn = sqlite3.connect(self.target_db_path)
        
        cursor = self._target_conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at DATETIME NOT NULL,
                description TEXT,
                checksum TEXT,
                execution_time_ms INTEGER,
                status TEXT DEFAULT 'COMPLETED'
            )
        """)
        
        self._target_conn.commit()
        logger.info(f"Migration tracking initialized for {self.target_db_path}")
    
    async def get_pending_migrations(self) -> List[str]:
        """Get list of migrations not yet applied"""
        if self._target_conn is None:
            self._target_conn = sqlite3.connect(self.target_db_path)
        
        cursor = self._target_conn.cursor()
        
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        applied_versions = {row[0] for row in cursor.fetchall()}
        
        if not self.migrations_dir.exists():
            return []
        
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        pending = []
        for file in migration_files:
            version = file.stem.split('_')[0]
            if version not in applied_versions:
                pending.append(str(file))
        
        return pending
    
    async def apply_migration(self, migration_file: str) -> MigrationResult:
        """Apply a single migration file"""
        start_time = datetime.now()
        
        try:
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            version = Path(migration_file).stem.split('_')[0]
            description = self._extract_description(sql)
            
            checksum = hashlib.sha256(sql.encode()).hexdigest()
            
            logger.info(f"Applying migration {version}: {description}")
            
            if self._target_conn is None:
                self._target_conn = sqlite3.connect(self.target_db_path)
            
            cursor = self._target_conn.cursor()
            cursor.executescript(sql)
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            cursor.execute("""
                INSERT OR REPLACE INTO schema_migrations 
                (version, applied_at, description, checksum, execution_time_ms, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (version, datetime.now().isoformat(), description, checksum, execution_time_ms, "COMPLETED"))
            
            self._target_conn.commit()
            
            record = MigrationRecord(
                version=version,
                description=description,
                applied_at=datetime.now(),
                checksum=checksum,
                execution_time_ms=execution_time_ms,
                status=MigrationStatus.COMPLETED
            )
            self._migration_history.append(record)
            
            logger.info(f"Migration {version} applied in {execution_time_ms}ms")
            
            return MigrationResult(
                success=True,
                phase=MigrationPhase.SCHEMA,
                message=f"Migration {version} applied successfully",
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            if self._target_conn:
                self._target_conn.rollback()
            
            error_msg = f"Migration failed: {e}"
            logger.error(error_msg)
            
            return MigrationResult(
                success=False,
                phase=MigrationPhase.SCHEMA,
                message=error_msg
            )
    
    async def rollback_migration(self, version: str) -> MigrationResult:
        """Rollback a specific migration"""
        try:
            rollback_file = self.migrations_dir / 'rollback' / f"{version}_rollback.sql"
            
            if not rollback_file.exists():
                return MigrationResult(
                    success=False,
                    phase=MigrationPhase.SCHEMA,
                    message=f"Rollback script not found for version {version}"
                )
            
            logger.info(f"Rolling back migration {version}")
            
            with open(rollback_file, 'r') as f:
                sql = f.read()
            
            if self._target_conn is None:
                self._target_conn = sqlite3.connect(self.target_db_path)
            
            cursor = self._target_conn.cursor()
            cursor.executescript(sql)
            
            cursor.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
            
            self._target_conn.commit()
            
            logger.info(f"Migration {version} rolled back successfully")
            
            return MigrationResult(
                success=True,
                phase=MigrationPhase.SCHEMA,
                message=f"Migration {version} rolled back"
            )
            
        except Exception as e:
            if self._target_conn:
                self._target_conn.rollback()
            
            error_msg = f"Rollback failed: {e}"
            logger.error(error_msg)
            
            return MigrationResult(
                success=False,
                phase=MigrationPhase.SCHEMA,
                message=error_msg
            )
    
    async def migrate_to_latest(self) -> Dict[str, Any]:
        """Apply all pending migrations"""
        await self.initialize_migration_tracking()
        
        pending = await self.get_pending_migrations()
        
        if not pending:
            logger.info("Database is up to date")
            return {
                'status': 'UP_TO_DATE',
                'applied': 0,
                'failed': 0
            }
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        results = {
            'status': 'SUCCESS',
            'applied': 0,
            'failed': 0,
            'migrations': []
        }
        
        for migration_file in pending:
            result = await self.apply_migration(migration_file)
            
            results['migrations'].append(result.to_dict())
            
            if result.success:
                results['applied'] += 1
            else:
                results['failed'] += 1
                results['status'] = 'PARTIAL'
                break
        
        return results
    
    async def run_full_migration(
        self,
        config_path: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Run the complete V2 to V5 migration"""
        self._is_running = True
        start_time = datetime.now()
        
        results = {
            "started_at": start_time.isoformat(),
            "dry_run": dry_run,
            "phases": {},
            "success": True
        }
        
        try:
            self._current_phase = MigrationPhase.BACKUP
            logger.info("Phase 1: Creating backups...")
            
            if not dry_run:
                await self.rollback_manager.create_rollback_point(
                    self.source_db_path, "source_pre_migration"
                )
                
                if os.path.exists(self.target_db_path):
                    await self.rollback_manager.create_rollback_point(
                        self.target_db_path, "target_pre_migration"
                    )
            
            results["phases"]["backup"] = {"status": "completed"}
            
            self._current_phase = MigrationPhase.SCHEMA
            logger.info("Phase 2: Applying schema migrations...")
            
            if not dry_run:
                schema_result = await self.migrate_to_latest()
                results["phases"]["schema"] = schema_result
                
                if schema_result.get("status") == "PARTIAL":
                    results["success"] = False
                    return results
            else:
                results["phases"]["schema"] = {"status": "skipped (dry run)"}
            
            self._current_phase = MigrationPhase.DATA
            logger.info("Phase 3: Migrating data...")
            
            if not dry_run:
                self._source_conn = sqlite3.connect(self.source_db_path)
                self._target_conn = sqlite3.connect(self.target_db_path)
                
                user_result = await self.user_migrator.migrate_users(
                    self._source_conn, self._target_conn
                )
                results["phases"]["users"] = user_result.to_dict()
                
                perm_result = await self.user_migrator.migrate_permissions(
                    self._source_conn, self._target_conn
                )
                results["phases"]["permissions"] = perm_result.to_dict()
                
                session_result = await self.user_migrator.migrate_sessions(
                    self._source_conn, self._target_conn
                )
                results["phases"]["sessions"] = session_result.to_dict()
                
                trade_result = await self.trade_migrator.migrate_trades(
                    self._source_conn, self._target_conn, "v2_database"
                )
                results["phases"]["trades"] = trade_result.to_dict()
                
                order_result = await self.trade_migrator.migrate_orders(
                    self._source_conn, self._target_conn
                )
                results["phases"]["orders"] = order_result.to_dict()
            else:
                results["phases"]["data"] = {"status": "skipped (dry run)"}
            
            if config_path and os.path.exists(config_path):
                logger.info("Migrating configuration...")
                
                if not dry_run:
                    await self.config_migrator.load_old_config(config_path)
                    new_config = await self.config_migrator.migrate_config()
                    
                    config_dir = Path(self.target_db_path).parent / "config"
                    saved_files = await self.config_migrator.save_new_config(str(config_dir))
                    
                    results["phases"]["config"] = {
                        "status": "completed",
                        "files": saved_files
                    }
                else:
                    results["phases"]["config"] = {"status": "skipped (dry run)"}
            
            self._current_phase = MigrationPhase.VERIFICATION
            logger.info("Phase 4: Verifying migration...")
            
            if not dry_run:
                table_mappings = {
                    "users": "users",
                    "trades": "trade_history",
                    "orders": "orders"
                }
                
                verification_results = await self.verifier.verify_row_counts(
                    self._source_conn, self._target_conn, table_mappings
                )
                
                verification_report = await self.verifier.generate_verification_report()
                results["phases"]["verification"] = verification_report
                
                if verification_report["failed"] > 0:
                    logger.warning(f"Verification found {verification_report['failed']} issues")
            else:
                results["phases"]["verification"] = {"status": "skipped (dry run)"}
            
            self._current_phase = MigrationPhase.CLEANUP
            logger.info("Phase 5: Cleanup...")
            
            results["phases"]["cleanup"] = {"status": "completed"}
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            results["success"] = False
            results["error"] = str(e)
            
            if not dry_run:
                logger.info("Attempting rollback...")
                rollback_results = await self.rollback_manager.rollback_all()
                results["rollback"] = rollback_results
        
        finally:
            self._is_running = False
            
            if self._source_conn:
                self._source_conn.close()
                self._source_conn = None
            
            if self._target_conn:
                self._target_conn.close()
                self._target_conn = None
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        results["completed_at"] = datetime.now().isoformat()
        results["execution_time_ms"] = execution_time
        
        return results
    
    async def get_current_version(self) -> str:
        """Get latest applied migration version"""
        if self._target_conn is None:
            self._target_conn = sqlite3.connect(self.target_db_path)
        
        cursor = self._target_conn.cursor()
        
        try:
            cursor.execute("""
                SELECT version FROM schema_migrations 
                ORDER BY version DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            return result[0] if result else "000"
        except:
            return "000"
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        current_version = await self.get_current_version()
        pending = await self.get_pending_migrations()
        
        return {
            "current_version": current_version,
            "pending_migrations": len(pending),
            "is_running": self._is_running,
            "current_phase": self._current_phase.value if self._current_phase else None,
            "history": [r.to_dict() for r in self._migration_history]
        }
    
    def _extract_description(self, sql: str) -> str:
        """Extract description from migration SQL comments"""
        for line in sql.split('\n'):
            if line.startswith('-- Description:'):
                return line.replace('-- Description:', '').strip()
        return "No description"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get migration statistics"""
        return {
            "total_migrations": len(self._migration_history),
            "successful": sum(1 for r in self._migration_history if r.status == MigrationStatus.COMPLETED),
            "failed": sum(1 for r in self._migration_history if r.status == MigrationStatus.FAILED),
            "is_running": self._is_running,
            "current_phase": self._current_phase.value if self._current_phase else None
        }


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_migration_manager(
    source_db: str,
    target_db: str,
    backup_dir: str = "backups",
    migrations_dir: str = "migrations"
) -> MigrationManager:
    """Factory function to create a MigrationManager"""
    return MigrationManager(
        source_db_path=source_db,
        target_db_path=target_db,
        backup_dir=backup_dir,
        migrations_dir=migrations_dir
    )


def create_backup_manager(backup_dir: str = "backups") -> BackupManager:
    """Factory function to create a BackupManager"""
    return BackupManager(backup_dir)


def create_data_mapper() -> DataMapper:
    """Factory function to create a DataMapper"""
    return DataMapper()


def create_config_migrator() -> ConfigMigrator:
    """Factory function to create a ConfigMigrator"""
    return ConfigMigrator()


def create_verifier() -> MigrationVerifier:
    """Factory function to create a MigrationVerifier"""
    return MigrationVerifier()
