"""
Test Suite for Document 26: Data Migration Scripts & Strategies

Tests all migration components including:
1. MigrationManager - Orchestrator for the full migration process
2. DataMapper - Transform V2 flat structure -> V5 Relational Schema
3. UserMigrator - Migrate users, permissions, and sessions
4. TradeHistoryMigrator - Archive old trades into Central DB
5. ConfigMigrator - Convert old config.json to new modular format
6. BackupManager - Automatic backup before migration (safety nets)
7. MigrationVerifier - Row count checks and data integrity verification
8. RollbackManager - One-click restore if migration fails
"""

import sys
import os
import asyncio
import tempfile
import sqlite3
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# MODULE STRUCTURE TESTS
# ============================================================================

class TestDataMigrationModuleStructure:
    """Test that all required classes and enums exist in data_migration module"""
    
    def test_module_imports(self):
        """Test that data_migration module can be imported"""
        from core import data_migration
        assert data_migration is not None
    
    def test_migration_status_enum_exists(self):
        """Test MigrationStatus enum exists"""
        from core.data_migration import MigrationStatus
        assert MigrationStatus is not None
    
    def test_migration_phase_enum_exists(self):
        """Test MigrationPhase enum exists"""
        from core.data_migration import MigrationPhase
        assert MigrationPhase is not None
    
    def test_data_type_enum_exists(self):
        """Test DataType enum exists"""
        from core.data_migration import DataType
        assert DataType is not None
    
    def test_migration_record_exists(self):
        """Test MigrationRecord dataclass exists"""
        from core.data_migration import MigrationRecord
        assert MigrationRecord is not None
    
    def test_backup_info_exists(self):
        """Test BackupInfo dataclass exists"""
        from core.data_migration import BackupInfo
        assert BackupInfo is not None
    
    def test_verification_result_exists(self):
        """Test VerificationResult dataclass exists"""
        from core.data_migration import VerificationResult
        assert VerificationResult is not None
    
    def test_migration_result_exists(self):
        """Test MigrationResult dataclass exists"""
        from core.data_migration import MigrationResult
        assert MigrationResult is not None
    
    def test_migration_plan_exists(self):
        """Test MigrationPlan dataclass exists"""
        from core.data_migration import MigrationPlan
        assert MigrationPlan is not None
    
    def test_backup_manager_exists(self):
        """Test BackupManager class exists"""
        from core.data_migration import BackupManager
        assert BackupManager is not None
    
    def test_data_mapper_exists(self):
        """Test DataMapper class exists"""
        from core.data_migration import DataMapper
        assert DataMapper is not None
    
    def test_user_migrator_exists(self):
        """Test UserMigrator class exists"""
        from core.data_migration import UserMigrator
        assert UserMigrator is not None
    
    def test_trade_history_migrator_exists(self):
        """Test TradeHistoryMigrator class exists"""
        from core.data_migration import TradeHistoryMigrator
        assert TradeHistoryMigrator is not None
    
    def test_config_migrator_exists(self):
        """Test ConfigMigrator class exists"""
        from core.data_migration import ConfigMigrator
        assert ConfigMigrator is not None
    
    def test_migration_verifier_exists(self):
        """Test MigrationVerifier class exists"""
        from core.data_migration import MigrationVerifier
        assert MigrationVerifier is not None
    
    def test_rollback_manager_exists(self):
        """Test RollbackManager class exists"""
        from core.data_migration import RollbackManager
        assert RollbackManager is not None
    
    def test_migration_manager_exists(self):
        """Test MigrationManager class exists"""
        from core.data_migration import MigrationManager
        assert MigrationManager is not None


# ============================================================================
# ENUM TESTS
# ============================================================================

class TestMigrationStatusEnum:
    """Test MigrationStatus enum values"""
    
    def test_migration_status_values(self):
        """Test all MigrationStatus values exist"""
        from core.data_migration import MigrationStatus
        
        assert MigrationStatus.PENDING.value == "PENDING"
        assert MigrationStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert MigrationStatus.COMPLETED.value == "COMPLETED"
        assert MigrationStatus.FAILED.value == "FAILED"
        assert MigrationStatus.ROLLED_BACK.value == "ROLLED_BACK"
        assert MigrationStatus.SKIPPED.value == "SKIPPED"


class TestMigrationPhaseEnum:
    """Test MigrationPhase enum values"""
    
    def test_migration_phase_values(self):
        """Test all MigrationPhase values exist"""
        from core.data_migration import MigrationPhase
        
        assert MigrationPhase.BACKUP.value == "BACKUP"
        assert MigrationPhase.SCHEMA.value == "SCHEMA"
        assert MigrationPhase.DATA.value == "DATA"
        assert MigrationPhase.VERIFICATION.value == "VERIFICATION"
        assert MigrationPhase.CLEANUP.value == "CLEANUP"


class TestDataTypeEnum:
    """Test DataType enum values"""
    
    def test_data_type_values(self):
        """Test all DataType values exist"""
        from core.data_migration import DataType
        
        assert DataType.USERS.value == "USERS"
        assert DataType.TRADES.value == "TRADES"
        assert DataType.ORDERS.value == "ORDERS"
        assert DataType.SESSIONS.value == "SESSIONS"
        assert DataType.CONFIG.value == "CONFIG"
        assert DataType.PERMISSIONS.value == "PERMISSIONS"


# ============================================================================
# DATACLASS TESTS
# ============================================================================

class TestMigrationRecord:
    """Test MigrationRecord dataclass"""
    
    def test_creation(self):
        """Test creating MigrationRecord"""
        from core.data_migration import MigrationRecord, MigrationStatus
        
        record = MigrationRecord(
            version="001",
            description="Initial schema"
        )
        
        assert record.version == "001"
        assert record.description == "Initial schema"
        assert record.status == MigrationStatus.PENDING
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.data_migration import MigrationRecord
        
        record = MigrationRecord(
            version="001",
            description="Initial schema"
        )
        
        data = record.to_dict()
        
        assert "version" in data
        assert "description" in data
        assert "status" in data


class TestBackupInfo:
    """Test BackupInfo dataclass"""
    
    def test_creation(self):
        """Test creating BackupInfo"""
        from core.data_migration import BackupInfo
        
        info = BackupInfo(
            backup_id="test_backup_001",
            source_path="/path/to/source.db",
            backup_path="/path/to/backup.db.bak",
            created_at=datetime.now(),
            size_bytes=1024,
            checksum="abc123"
        )
        
        assert info.backup_id == "test_backup_001"
        assert info.size_bytes == 1024
        assert info.is_valid is True
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.data_migration import BackupInfo
        
        info = BackupInfo(
            backup_id="test_backup_001",
            source_path="/path/to/source.db",
            backup_path="/path/to/backup.db.bak",
            created_at=datetime.now(),
            size_bytes=1024,
            checksum="abc123"
        )
        
        data = info.to_dict()
        
        assert "backup_id" in data
        assert "source_path" in data
        assert "checksum" in data


class TestVerificationResult:
    """Test VerificationResult dataclass"""
    
    def test_creation(self):
        """Test creating VerificationResult"""
        from core.data_migration import VerificationResult
        
        result = VerificationResult(
            is_valid=True,
            source_count=100,
            target_count=100
        )
        
        assert result.is_valid is True
        assert result.source_count == 100
        assert result.target_count == 100
        assert result.missing_records == 0
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.data_migration import VerificationResult
        
        result = VerificationResult(
            is_valid=True,
            source_count=100,
            target_count=100
        )
        
        data = result.to_dict()
        
        assert "is_valid" in data
        assert "source_count" in data
        assert "target_count" in data


class TestMigrationResult:
    """Test MigrationResult dataclass"""
    
    def test_creation(self):
        """Test creating MigrationResult"""
        from core.data_migration import MigrationResult, MigrationPhase
        
        result = MigrationResult(
            success=True,
            phase=MigrationPhase.DATA,
            message="Migration completed"
        )
        
        assert result.success is True
        assert result.phase == MigrationPhase.DATA
        assert result.message == "Migration completed"
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.data_migration import MigrationResult, MigrationPhase
        
        result = MigrationResult(
            success=True,
            phase=MigrationPhase.DATA,
            message="Migration completed"
        )
        
        data = result.to_dict()
        
        assert "success" in data
        assert "phase" in data
        assert "message" in data


class TestMigrationPlan:
    """Test MigrationPlan dataclass"""
    
    def test_creation(self):
        """Test creating MigrationPlan"""
        from core.data_migration import MigrationPlan, MigrationPhase, DataType
        
        plan = MigrationPlan(
            source_db="/path/to/source.db",
            target_dbs=["/path/to/target.db"],
            phases=[MigrationPhase.BACKUP, MigrationPhase.DATA],
            data_types=[DataType.USERS, DataType.TRADES]
        )
        
        assert plan.source_db == "/path/to/source.db"
        assert len(plan.target_dbs) == 1
        assert plan.backup_enabled is True
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.data_migration import MigrationPlan, MigrationPhase, DataType
        
        plan = MigrationPlan(
            source_db="/path/to/source.db",
            target_dbs=["/path/to/target.db"],
            phases=[MigrationPhase.BACKUP],
            data_types=[DataType.USERS]
        )
        
        data = plan.to_dict()
        
        assert "source_db" in data
        assert "target_dbs" in data
        assert "phases" in data


# ============================================================================
# BACKUP MANAGER TESTS
# ============================================================================

class TestBackupManager:
    """Test BackupManager class"""
    
    def test_creation(self):
        """Test creating BackupManager"""
        from core.data_migration import BackupManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BackupManager(backup_dir=tmpdir)
            assert manager is not None
            assert manager.backup_dir.exists()
    
    def test_create_backup(self):
        """Test creating a backup"""
        from core.data_migration import BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.execute("INSERT INTO test VALUES (1)")
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                manager = BackupManager(backup_dir=backup_dir)
                
                backup_info = await manager.create_backup(db_path)
                
                assert backup_info is not None
                assert backup_info.is_valid is True
                assert os.path.exists(backup_info.backup_path)
        
        asyncio.run(run_test())
    
    def test_restore_backup(self):
        """Test restoring a backup"""
        from core.data_migration import BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.execute("INSERT INTO test VALUES (1)")
                conn.commit()
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                manager = BackupManager(backup_dir=backup_dir)
                
                backup_info = await manager.create_backup(db_path)
                
                conn = sqlite3.connect(db_path)
                conn.execute("INSERT INTO test VALUES (2)")
                conn.commit()
                conn.close()
                
                success = await manager.restore_backup(backup_info.backup_id)
                
                assert success is True
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test")
                count = cursor.fetchone()[0]
                conn.close()
                
                assert count == 1
        
        asyncio.run(run_test())
    
    def test_verify_backup(self):
        """Test verifying backup integrity"""
        from core.data_migration import BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                manager = BackupManager(backup_dir=backup_dir)
                
                backup_info = await manager.create_backup(db_path)
                
                is_valid = await manager.verify_backup(backup_info.backup_id)
                
                assert is_valid is True
        
        asyncio.run(run_test())
    
    def test_list_backups(self):
        """Test listing backups"""
        from core.data_migration import BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                manager = BackupManager(backup_dir=backup_dir)
                
                await manager.create_backup(db_path, "_first")
                await manager.create_backup(db_path, "_second")
                
                backups = await manager.list_backups()
                
                assert len(backups) == 2
        
        asyncio.run(run_test())
    
    def test_delete_backup(self):
        """Test deleting a backup"""
        from core.data_migration import BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                manager = BackupManager(backup_dir=backup_dir)
                
                backup_info = await manager.create_backup(db_path)
                
                success = await manager.delete_backup(backup_info.backup_id)
                
                assert success is True
                
                backups = await manager.list_backups()
                assert len(backups) == 0
        
        asyncio.run(run_test())


# ============================================================================
# DATA MAPPER TESTS
# ============================================================================

class TestDataMapper:
    """Test DataMapper class"""
    
    def test_creation(self):
        """Test creating DataMapper"""
        from core.data_migration import DataMapper
        
        mapper = DataMapper()
        assert mapper is not None
    
    def test_default_mappings(self):
        """Test default column mappings exist"""
        from core.data_migration import DataMapper
        
        mapper = DataMapper()
        
        trades_mapping = mapper.get_mapping("trades")
        assert "ticket" in trades_mapping
        assert "symbol" in trades_mapping
        
        users_mapping = mapper.get_mapping("users")
        assert "telegram_id" in users_mapping
    
    def test_add_mapping(self):
        """Test adding custom mapping"""
        from core.data_migration import DataMapper
        
        mapper = DataMapper()
        mapper.add_mapping("custom_table", "old_col", "new_col")
        
        mapping = mapper.get_mapping("custom_table")
        assert mapping["old_col"] == "new_col"
    
    def test_map_row(self):
        """Test mapping a single row"""
        from core.data_migration import DataMapper
        
        async def run_test():
            mapper = DataMapper()
            
            old_row = {
                "id": 1,
                "ticket": 12345,
                "symbol": "EURUSD",
                "type": "BUY",
                "lots": 0.1
            }
            
            mapped_row = await mapper.map_row("trades", old_row)
            
            assert "ticket" in mapped_row
            assert "symbol" in mapped_row
            assert mapped_row["order_type"] == "BUY"
        
        asyncio.run(run_test())
    
    def test_map_rows(self):
        """Test mapping multiple rows"""
        from core.data_migration import DataMapper
        
        async def run_test():
            mapper = DataMapper()
            
            old_rows = [
                {"id": 1, "ticket": 12345, "symbol": "EURUSD", "type": "BUY", "lots": 0.1},
                {"id": 2, "ticket": 12346, "symbol": "GBPUSD", "type": "SELL", "lots": 0.2}
            ]
            
            mapped_rows = await mapper.map_rows("trades", old_rows)
            
            assert len(mapped_rows) == 2
            assert mapped_rows[0]["order_type"] == "BUY"
            assert mapped_rows[1]["order_type"] == "SELL"
        
        asyncio.run(run_test())
    
    def test_get_v5_schema(self):
        """Test getting V5 schema"""
        from core.data_migration import DataMapper
        
        mapper = DataMapper()
        
        trades_schema = mapper.get_v5_schema("trades")
        assert "CREATE TABLE" in trades_schema
        assert "ticket" in trades_schema
        
        users_schema = mapper.get_v5_schema("users")
        assert "CREATE TABLE" in users_schema
        assert "telegram_id" in users_schema


# ============================================================================
# USER MIGRATOR TESTS
# ============================================================================

class TestUserMigrator:
    """Test UserMigrator class"""
    
    def test_creation(self):
        """Test creating UserMigrator"""
        from core.data_migration import UserMigrator, DataMapper
        
        mapper = DataMapper()
        migrator = UserMigrator(mapper)
        assert migrator is not None
    
    def test_migrate_users(self):
        """Test migrating users"""
        from core.data_migration import UserMigrator, DataMapper
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        first_name TEXT,
                        is_admin BOOLEAN DEFAULT FALSE
                    )
                """)
                source_conn.execute(
                    "INSERT INTO users VALUES (1, 123456, 'testuser', 'Test', 1)"
                )
                source_conn.commit()
                
                target_conn = sqlite3.connect(target_db)
                
                mapper = DataMapper()
                migrator = UserMigrator(mapper)
                
                result = await migrator.migrate_users(source_conn, target_conn)
                
                assert result.success is True
                assert result.records_processed == 1
                
                cursor = target_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                
                assert count == 1
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_migrate_users_no_table(self):
        """Test migrating users when source table doesn't exist"""
        from core.data_migration import UserMigrator, DataMapper
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                target_conn = sqlite3.connect(target_db)
                
                mapper = DataMapper()
                migrator = UserMigrator(mapper)
                
                result = await migrator.migrate_users(source_conn, target_conn)
                
                assert result.success is True
                assert result.records_processed == 0
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_get_user_id_mapping(self):
        """Test getting user ID mapping"""
        from core.data_migration import UserMigrator, DataMapper
        
        mapper = DataMapper()
        migrator = UserMigrator(mapper)
        
        mapping = migrator.get_user_id_mapping()
        assert isinstance(mapping, dict)


# ============================================================================
# TRADE HISTORY MIGRATOR TESTS
# ============================================================================

class TestTradeHistoryMigrator:
    """Test TradeHistoryMigrator class"""
    
    def test_creation(self):
        """Test creating TradeHistoryMigrator"""
        from core.data_migration import TradeHistoryMigrator, DataMapper
        
        mapper = DataMapper()
        migrator = TradeHistoryMigrator(mapper)
        assert migrator is not None
    
    def test_migrate_trades(self):
        """Test migrating trades to trade_history"""
        from core.data_migration import TradeHistoryMigrator, DataMapper
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("""
                    CREATE TABLE trades (
                        id INTEGER PRIMARY KEY,
                        ticket INTEGER,
                        symbol TEXT,
                        type TEXT,
                        lots REAL,
                        open_price REAL,
                        profit REAL
                    )
                """)
                source_conn.execute(
                    "INSERT INTO trades VALUES (1, 12345, 'EURUSD', 'BUY', 0.1, 1.1000, 50.0)"
                )
                source_conn.execute(
                    "INSERT INTO trades VALUES (2, 12346, 'GBPUSD', 'SELL', 0.2, 1.2500, -25.0)"
                )
                source_conn.commit()
                
                target_conn = sqlite3.connect(target_db)
                
                mapper = DataMapper()
                migrator = TradeHistoryMigrator(mapper)
                
                result = await migrator.migrate_trades(source_conn, target_conn, "v2_test")
                
                assert result.success is True
                assert result.records_processed == 2
                
                cursor = target_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM trade_history")
                count = cursor.fetchone()[0]
                
                assert count == 2
                
                cursor.execute("SELECT source_db FROM trade_history LIMIT 1")
                source = cursor.fetchone()[0]
                assert source == "v2_test"
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_migrate_orders(self):
        """Test migrating orders"""
        from core.data_migration import TradeHistoryMigrator, DataMapper
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("""
                    CREATE TABLE orders (
                        id INTEGER PRIMARY KEY,
                        ticket INTEGER,
                        symbol TEXT,
                        type TEXT,
                        lots REAL,
                        price REAL
                    )
                """)
                source_conn.execute(
                    "INSERT INTO orders VALUES (1, 12345, 'EURUSD', 'BUY', 0.1, 1.1000)"
                )
                source_conn.commit()
                
                target_conn = sqlite3.connect(target_db)
                
                mapper = DataMapper()
                migrator = TradeHistoryMigrator(mapper)
                
                result = await migrator.migrate_orders(source_conn, target_conn)
                
                assert result.success is True
                assert result.records_processed == 1
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_get_migrated_trade_count(self):
        """Test getting migrated trade count"""
        from core.data_migration import TradeHistoryMigrator, DataMapper
        
        mapper = DataMapper()
        migrator = TradeHistoryMigrator(mapper)
        
        count = migrator.get_migrated_trade_count()
        assert count == 0


# ============================================================================
# CONFIG MIGRATOR TESTS
# ============================================================================

class TestConfigMigrator:
    """Test ConfigMigrator class"""
    
    def test_creation(self):
        """Test creating ConfigMigrator"""
        from core.data_migration import ConfigMigrator
        
        migrator = ConfigMigrator()
        assert migrator is not None
    
    def test_load_old_config(self):
        """Test loading old config file"""
        from core.data_migration import ConfigMigrator
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "config.json")
                
                old_config = {
                    "debug": True,
                    "telegram_token": "123456:ABC",
                    "symbols": ["EURUSD", "GBPUSD"],
                    "lot_size": 0.01
                }
                
                with open(config_path, 'w') as f:
                    json.dump(old_config, f)
                
                migrator = ConfigMigrator()
                success = await migrator.load_old_config(config_path)
                
                assert success is True
                
                loaded = migrator.get_old_config()
                assert loaded["debug"] is True
                assert loaded["telegram_token"] == "123456:ABC"
        
        asyncio.run(run_test())
    
    def test_migrate_config(self):
        """Test migrating config to new format"""
        from core.data_migration import ConfigMigrator
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "config.json")
                
                old_config = {
                    "debug": True,
                    "log_level": "DEBUG",
                    "telegram_token": "123456:ABC",
                    "telegram_enabled": True,
                    "symbols": ["EURUSD", "GBPUSD"],
                    "lot_size": 0.01,
                    "risk_per_trade": 2.0,
                    "max_daily_loss": 5.0
                }
                
                with open(config_path, 'w') as f:
                    json.dump(old_config, f)
                
                migrator = ConfigMigrator()
                await migrator.load_old_config(config_path)
                
                new_config = await migrator.migrate_config()
                
                assert "version" in new_config
                assert new_config["version"] == "5.0"
                assert "system" in new_config
                assert "trading" in new_config
                assert "telegram" in new_config
                assert "plugins" in new_config
                assert "risk" in new_config
                assert "database" in new_config
                
                assert new_config["system"]["debug"] is True
                assert new_config["system"]["log_level"] == "DEBUG"
        
        asyncio.run(run_test())
    
    def test_save_new_config(self):
        """Test saving new modular config files"""
        from core.data_migration import ConfigMigrator
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "config.json")
                output_dir = os.path.join(tmpdir, "new_config")
                
                old_config = {"debug": True, "telegram_token": "123456:ABC"}
                
                with open(config_path, 'w') as f:
                    json.dump(old_config, f)
                
                migrator = ConfigMigrator()
                await migrator.load_old_config(config_path)
                await migrator.migrate_config()
                
                saved_files = await migrator.save_new_config(output_dir)
                
                assert "main" in saved_files
                assert os.path.exists(saved_files["main"])
                
                assert "system" in saved_files
                assert "trading" in saved_files
                assert "telegram" in saved_files
        
        asyncio.run(run_test())
    
    def test_get_new_config(self):
        """Test getting new config"""
        from core.data_migration import ConfigMigrator
        
        migrator = ConfigMigrator()
        new_config = migrator.get_new_config()
        assert isinstance(new_config, dict)


# ============================================================================
# MIGRATION VERIFIER TESTS
# ============================================================================

class TestMigrationVerifier:
    """Test MigrationVerifier class"""
    
    def test_creation(self):
        """Test creating MigrationVerifier"""
        from core.data_migration import MigrationVerifier
        
        verifier = MigrationVerifier()
        assert verifier is not None
    
    def test_verify_row_counts_match(self):
        """Test verifying row counts when they match"""
        from core.data_migration import MigrationVerifier
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("CREATE TABLE users (id INTEGER)")
                source_conn.execute("INSERT INTO users VALUES (1)")
                source_conn.execute("INSERT INTO users VALUES (2)")
                source_conn.commit()
                
                target_conn = sqlite3.connect(target_db)
                target_conn.execute("CREATE TABLE users (id INTEGER)")
                target_conn.execute("INSERT INTO users VALUES (1)")
                target_conn.execute("INSERT INTO users VALUES (2)")
                target_conn.commit()
                
                verifier = MigrationVerifier()
                
                results = await verifier.verify_row_counts(
                    source_conn, target_conn, {"users": "users"}
                )
                
                assert len(results) == 1
                assert results[0].is_valid is True
                assert results[0].source_count == 2
                assert results[0].target_count == 2
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_verify_row_counts_mismatch(self):
        """Test verifying row counts when they don't match"""
        from core.data_migration import MigrationVerifier
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("CREATE TABLE users (id INTEGER)")
                source_conn.execute("INSERT INTO users VALUES (1)")
                source_conn.execute("INSERT INTO users VALUES (2)")
                source_conn.execute("INSERT INTO users VALUES (3)")
                source_conn.commit()
                
                target_conn = sqlite3.connect(target_db)
                target_conn.execute("CREATE TABLE users (id INTEGER)")
                target_conn.execute("INSERT INTO users VALUES (1)")
                target_conn.commit()
                
                verifier = MigrationVerifier()
                
                results = await verifier.verify_row_counts(
                    source_conn, target_conn, {"users": "users"}
                )
                
                assert len(results) == 1
                assert results[0].is_valid is False
                assert results[0].source_count == 3
                assert results[0].target_count == 1
                assert results[0].missing_records == 2
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_verify_data_integrity(self):
        """Test verifying data integrity"""
        from core.data_migration import MigrationVerifier
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")
                source_conn.execute("INSERT INTO users VALUES (1)")
                source_conn.execute("INSERT INTO users VALUES (2)")
                source_conn.commit()
                
                target_conn = sqlite3.connect(target_db)
                target_conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")
                target_conn.execute("INSERT INTO users VALUES (1)")
                target_conn.execute("INSERT INTO users VALUES (2)")
                target_conn.commit()
                
                verifier = MigrationVerifier()
                
                result = await verifier.verify_data_integrity(
                    source_conn, target_conn, "users", "id"
                )
                
                assert result.is_valid is True
                
                source_conn.close()
                target_conn.close()
        
        asyncio.run(run_test())
    
    def test_generate_verification_report(self):
        """Test generating verification report"""
        from core.data_migration import MigrationVerifier
        
        async def run_test():
            verifier = MigrationVerifier()
            
            report = await verifier.generate_verification_report()
            
            assert "generated_at" in report
            assert "total_verifications" in report
            assert "passed" in report
            assert "failed" in report
        
        asyncio.run(run_test())
    
    def test_clear_results(self):
        """Test clearing verification results"""
        from core.data_migration import MigrationVerifier
        
        verifier = MigrationVerifier()
        verifier.clear_results()
        
        results = verifier.get_results()
        assert len(results) == 0


# ============================================================================
# ROLLBACK MANAGER TESTS
# ============================================================================

class TestRollbackManager:
    """Test RollbackManager class"""
    
    def test_creation(self):
        """Test creating RollbackManager"""
        from core.data_migration import RollbackManager, BackupManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_manager = BackupManager(backup_dir=tmpdir)
            rollback_manager = RollbackManager(backup_manager)
            assert rollback_manager is not None
    
    def test_create_rollback_point(self):
        """Test creating a rollback point"""
        from core.data_migration import RollbackManager, BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                backup_manager = BackupManager(backup_dir=backup_dir)
                rollback_manager = RollbackManager(backup_manager)
                
                backup_id = await rollback_manager.create_rollback_point(
                    db_path, "pre_migration"
                )
                
                assert backup_id is not None
                
                points = await rollback_manager.list_rollback_points()
                assert "pre_migration" in points
        
        asyncio.run(run_test())
    
    def test_rollback_to_point(self):
        """Test rolling back to a point"""
        from core.data_migration import RollbackManager, BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.execute("INSERT INTO test VALUES (1)")
                conn.commit()
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                backup_manager = BackupManager(backup_dir=backup_dir)
                rollback_manager = RollbackManager(backup_manager)
                
                await rollback_manager.create_rollback_point(db_path, "pre_migration")
                
                conn = sqlite3.connect(db_path)
                conn.execute("INSERT INTO test VALUES (2)")
                conn.execute("INSERT INTO test VALUES (3)")
                conn.commit()
                conn.close()
                
                success = await rollback_manager.rollback_to_point("pre_migration")
                
                assert success is True
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test")
                count = cursor.fetchone()[0]
                conn.close()
                
                assert count == 1
        
        asyncio.run(run_test())
    
    def test_rollback_all(self):
        """Test rolling back all databases"""
        from core.data_migration import RollbackManager, BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db1_path = os.path.join(tmpdir, "test1.db")
                db2_path = os.path.join(tmpdir, "test2.db")
                
                conn1 = sqlite3.connect(db1_path)
                conn1.execute("CREATE TABLE test (id INTEGER)")
                conn1.close()
                
                conn2 = sqlite3.connect(db2_path)
                conn2.execute("CREATE TABLE test (id INTEGER)")
                conn2.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                backup_manager = BackupManager(backup_dir=backup_dir)
                rollback_manager = RollbackManager(backup_manager)
                
                await rollback_manager.create_rollback_point(db1_path, "db1_pre")
                await rollback_manager.create_rollback_point(db2_path, "db2_pre")
                
                results = await rollback_manager.rollback_all()
                
                assert "db1_pre" in results
                assert "db2_pre" in results
        
        asyncio.run(run_test())
    
    def test_delete_rollback_point(self):
        """Test deleting a rollback point"""
        from core.data_migration import RollbackManager, BackupManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test.db")
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                backup_dir = os.path.join(tmpdir, "backups")
                backup_manager = BackupManager(backup_dir=backup_dir)
                rollback_manager = RollbackManager(backup_manager)
                
                await rollback_manager.create_rollback_point(db_path, "pre_migration")
                
                success = await rollback_manager.delete_rollback_point("pre_migration")
                
                assert success is True
                
                points = await rollback_manager.list_rollback_points()
                assert "pre_migration" not in points
        
        asyncio.run(run_test())


# ============================================================================
# MIGRATION MANAGER TESTS
# ============================================================================

class TestMigrationManager:
    """Test MigrationManager class"""
    
    def test_creation(self):
        """Test creating MigrationManager"""
        from core.data_migration import MigrationManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = os.path.join(tmpdir, "source.db")
            target_db = os.path.join(tmpdir, "target.db")
            
            conn = sqlite3.connect(source_db)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()
            
            manager = MigrationManager(
                source_db_path=source_db,
                target_db_path=target_db,
                backup_dir=os.path.join(tmpdir, "backups")
            )
            
            assert manager is not None
            assert manager.backup_manager is not None
            assert manager.data_mapper is not None
            assert manager.user_migrator is not None
            assert manager.trade_migrator is not None
            assert manager.config_migrator is not None
            assert manager.verifier is not None
            assert manager.rollback_manager is not None
    
    def test_initialize_migration_tracking(self):
        """Test initializing migration tracking"""
        from core.data_migration import MigrationManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                conn = sqlite3.connect(source_db)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                manager = MigrationManager(
                    source_db_path=source_db,
                    target_db_path=target_db,
                    backup_dir=os.path.join(tmpdir, "backups")
                )
                
                await manager.initialize_migration_tracking()
                
                conn = sqlite3.connect(target_db)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
                )
                result = cursor.fetchone()
                conn.close()
                
                assert result is not None
        
        asyncio.run(run_test())
    
    def test_get_current_version(self):
        """Test getting current migration version"""
        from core.data_migration import MigrationManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                conn = sqlite3.connect(source_db)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                manager = MigrationManager(
                    source_db_path=source_db,
                    target_db_path=target_db,
                    backup_dir=os.path.join(tmpdir, "backups")
                )
                
                await manager.initialize_migration_tracking()
                
                version = await manager.get_current_version()
                
                assert version == "000"
        
        asyncio.run(run_test())
    
    def test_get_migration_status(self):
        """Test getting migration status"""
        from core.data_migration import MigrationManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                conn = sqlite3.connect(source_db)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                manager = MigrationManager(
                    source_db_path=source_db,
                    target_db_path=target_db,
                    backup_dir=os.path.join(tmpdir, "backups")
                )
                
                await manager.initialize_migration_tracking()
                
                status = await manager.get_migration_status()
                
                assert "current_version" in status
                assert "pending_migrations" in status
                assert "is_running" in status
        
        asyncio.run(run_test())
    
    def test_get_stats(self):
        """Test getting migration statistics"""
        from core.data_migration import MigrationManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = os.path.join(tmpdir, "source.db")
            target_db = os.path.join(tmpdir, "target.db")
            
            conn = sqlite3.connect(source_db)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()
            
            manager = MigrationManager(
                source_db_path=source_db,
                target_db_path=target_db,
                backup_dir=os.path.join(tmpdir, "backups")
            )
            
            stats = manager.get_stats()
            
            assert "total_migrations" in stats
            assert "successful" in stats
            assert "failed" in stats
            assert "is_running" in stats
    
    def test_run_full_migration_dry_run(self):
        """Test running full migration in dry run mode"""
        from core.data_migration import MigrationManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT
                    )
                """)
                source_conn.execute("INSERT INTO users VALUES (1, 123456, 'testuser')")
                source_conn.commit()
                source_conn.close()
                
                manager = MigrationManager(
                    source_db_path=source_db,
                    target_db_path=target_db,
                    backup_dir=os.path.join(tmpdir, "backups")
                )
                
                results = await manager.run_full_migration(dry_run=True)
                
                assert results["dry_run"] is True
                assert results["success"] is True
        
        asyncio.run(run_test())


# ============================================================================
# FACTORY FUNCTION TESTS
# ============================================================================

class TestFactoryFunctions:
    """Test factory functions"""
    
    def test_create_migration_manager(self):
        """Test create_migration_manager factory"""
        from core.data_migration import create_migration_manager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = os.path.join(tmpdir, "source.db")
            target_db = os.path.join(tmpdir, "target.db")
            
            conn = sqlite3.connect(source_db)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()
            
            manager = create_migration_manager(source_db, target_db)
            
            assert manager is not None
    
    def test_create_backup_manager(self):
        """Test create_backup_manager factory"""
        from core.data_migration import create_backup_manager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = create_backup_manager(tmpdir)
            assert manager is not None
    
    def test_create_data_mapper(self):
        """Test create_data_mapper factory"""
        from core.data_migration import create_data_mapper
        
        mapper = create_data_mapper()
        assert mapper is not None
    
    def test_create_config_migrator(self):
        """Test create_config_migrator factory"""
        from core.data_migration import create_config_migrator
        
        migrator = create_config_migrator()
        assert migrator is not None
    
    def test_create_verifier(self):
        """Test create_verifier factory"""
        from core.data_migration import create_verifier
        
        verifier = create_verifier()
        assert verifier is not None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for data migration system"""
    
    def test_full_migration_flow(self):
        """Test complete migration flow"""
        from core.data_migration import MigrationManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        first_name TEXT,
                        is_admin BOOLEAN DEFAULT FALSE
                    )
                """)
                source_conn.execute(
                    "INSERT INTO users VALUES (1, 123456, 'user1', 'User', 1)"
                )
                source_conn.execute(
                    "INSERT INTO users VALUES (2, 789012, 'user2', 'Test', 0)"
                )
                
                source_conn.execute("""
                    CREATE TABLE trades (
                        id INTEGER PRIMARY KEY,
                        ticket INTEGER,
                        symbol TEXT,
                        type TEXT,
                        lots REAL,
                        open_price REAL,
                        profit REAL
                    )
                """)
                source_conn.execute(
                    "INSERT INTO trades VALUES (1, 12345, 'EURUSD', 'BUY', 0.1, 1.1000, 50.0)"
                )
                source_conn.commit()
                source_conn.close()
                
                manager = MigrationManager(
                    source_db_path=source_db,
                    target_db_path=target_db,
                    backup_dir=os.path.join(tmpdir, "backups")
                )
                
                results = await manager.run_full_migration()
                
                assert results["success"] is True
                assert "phases" in results
        
        asyncio.run(run_test())
    
    def test_migration_with_config(self):
        """Test migration with config file"""
        from core.data_migration import MigrationManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                source_db = os.path.join(tmpdir, "source.db")
                target_db = os.path.join(tmpdir, "target.db")
                config_path = os.path.join(tmpdir, "config.json")
                
                source_conn = sqlite3.connect(source_db)
                source_conn.execute("CREATE TABLE test (id INTEGER)")
                source_conn.close()
                
                old_config = {
                    "debug": True,
                    "telegram_token": "123456:ABC",
                    "symbols": ["EURUSD"]
                }
                with open(config_path, 'w') as f:
                    json.dump(old_config, f)
                
                manager = MigrationManager(
                    source_db_path=source_db,
                    target_db_path=target_db,
                    backup_dir=os.path.join(tmpdir, "backups")
                )
                
                results = await manager.run_full_migration(config_path=config_path)
                
                assert results["success"] is True
        
        asyncio.run(run_test())


# ============================================================================
# DOCUMENT 26 REQUIREMENTS TESTS
# ============================================================================

class TestDocument26Requirements:
    """Test Document 26 specific requirements"""
    
    def test_migration_manager_orchestrator(self):
        """Test Migration Manager is the orchestrator"""
        from core.data_migration import MigrationManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MigrationManager(
                source_db_path=os.path.join(tmpdir, "source.db"),
                target_db_path=os.path.join(tmpdir, "target.db")
            )
            
            assert hasattr(manager, 'run_full_migration')
            assert hasattr(manager, 'migrate_to_latest')
            assert hasattr(manager, 'rollback_migration')
    
    def test_data_mapping_v2_to_v5(self):
        """Test Data Mapping transforms V2 to V5"""
        from core.data_migration import DataMapper
        
        mapper = DataMapper()
        
        trades_mapping = mapper.get_mapping("trades")
        assert "type" in trades_mapping
        assert trades_mapping["type"] == "order_type"
        
        assert hasattr(mapper, 'map_row')
        assert hasattr(mapper, 'map_rows')
    
    def test_user_migration_implemented(self):
        """Test User Migration is implemented"""
        from core.data_migration import UserMigrator
        
        from core.data_migration import DataMapper
        mapper = DataMapper()
        migrator = UserMigrator(mapper)
        
        assert hasattr(migrator, 'migrate_users')
        assert hasattr(migrator, 'migrate_permissions')
        assert hasattr(migrator, 'migrate_sessions')
    
    def test_trade_history_migration_implemented(self):
        """Test Trade History Migration is implemented"""
        from core.data_migration import TradeHistoryMigrator
        
        from core.data_migration import DataMapper
        mapper = DataMapper()
        migrator = TradeHistoryMigrator(mapper)
        
        assert hasattr(migrator, 'migrate_trades')
        assert hasattr(migrator, 'migrate_orders')
    
    def test_config_migration_implemented(self):
        """Test Config Migration is implemented"""
        from core.data_migration import ConfigMigrator
        
        migrator = ConfigMigrator()
        
        assert hasattr(migrator, 'load_old_config')
        assert hasattr(migrator, 'migrate_config')
        assert hasattr(migrator, 'save_new_config')
    
    def test_safety_nets_backup_implemented(self):
        """Test Safety Nets (automatic backup) is implemented"""
        from core.data_migration import BackupManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BackupManager(backup_dir=tmpdir)
            
            assert hasattr(manager, 'create_backup')
            assert hasattr(manager, 'restore_backup')
            assert hasattr(manager, 'verify_backup')
    
    def test_verification_row_counts_implemented(self):
        """Test Verification (row count checks) is implemented"""
        from core.data_migration import MigrationVerifier
        
        verifier = MigrationVerifier()
        
        assert hasattr(verifier, 'verify_row_counts')
        assert hasattr(verifier, 'verify_data_integrity')
        assert hasattr(verifier, 'generate_verification_report')
    
    def test_rollback_one_click_implemented(self):
        """Test Rollback (one-click restore) is implemented"""
        from core.data_migration import RollbackManager, BackupManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_manager = BackupManager(backup_dir=tmpdir)
            rollback_manager = RollbackManager(backup_manager)
            
            assert hasattr(rollback_manager, 'create_rollback_point')
            assert hasattr(rollback_manager, 'rollback_to_point')
            assert hasattr(rollback_manager, 'rollback_all')


class TestDocument26Summary:
    """Summary tests for Document 26 implementation"""
    
    def test_all_components_importable(self):
        """Test all components can be imported"""
        from core.data_migration import (
            MigrationStatus,
            MigrationPhase,
            DataType,
            MigrationRecord,
            BackupInfo,
            VerificationResult,
            MigrationResult,
            MigrationPlan,
            BackupManager,
            DataMapper,
            UserMigrator,
            TradeHistoryMigrator,
            ConfigMigrator,
            MigrationVerifier,
            RollbackManager,
            MigrationManager,
            create_migration_manager,
            create_backup_manager,
            create_data_mapper,
            create_config_migrator,
            create_verifier
        )
        
        assert all([
            MigrationStatus, MigrationPhase, DataType,
            MigrationRecord, BackupInfo, VerificationResult,
            MigrationResult, MigrationPlan,
            BackupManager, DataMapper, UserMigrator,
            TradeHistoryMigrator, ConfigMigrator,
            MigrationVerifier, RollbackManager, MigrationManager,
            create_migration_manager, create_backup_manager,
            create_data_mapper, create_config_migrator, create_verifier
        ])
    
    def test_migration_manager_has_all_components(self):
        """Test MigrationManager has all required components"""
        from core.data_migration import MigrationManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MigrationManager(
                source_db_path=os.path.join(tmpdir, "source.db"),
                target_db_path=os.path.join(tmpdir, "target.db")
            )
            
            assert manager.backup_manager is not None
            assert manager.data_mapper is not None
            assert manager.user_migrator is not None
            assert manager.trade_migrator is not None
            assert manager.config_migrator is not None
            assert manager.verifier is not None
            assert manager.rollback_manager is not None
    
    def test_v2_to_v5_schema_transformation(self):
        """Test V2 to V5 schema transformation is defined"""
        from core.data_migration import DataMapper
        
        mapper = DataMapper()
        
        trades_schema = mapper.get_v5_schema("trades")
        assert "plugin_id" in trades_schema
        
        users_schema = mapper.get_v5_schema("users")
        assert "telegram_id" in users_schema
        
        trade_history_schema = mapper.get_v5_schema("trade_history")
        assert "migrated_at" in trade_history_schema
        assert "source_db" in trade_history_schema
    
    def test_migration_phases_defined(self):
        """Test all migration phases are defined"""
        from core.data_migration import MigrationPhase
        
        phases = [
            MigrationPhase.BACKUP,
            MigrationPhase.SCHEMA,
            MigrationPhase.DATA,
            MigrationPhase.VERIFICATION,
            MigrationPhase.CLEANUP
        ]
        
        assert len(phases) == 5
    
    def test_data_types_defined(self):
        """Test all data types are defined"""
        from core.data_migration import DataType
        
        data_types = [
            DataType.USERS,
            DataType.TRADES,
            DataType.ORDERS,
            DataType.SESSIONS,
            DataType.CONFIG,
            DataType.PERMISSIONS
        ]
        
        assert len(data_types) >= 6
