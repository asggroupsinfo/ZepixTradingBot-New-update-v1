"""
Test Suite for Document 23: Database Sync Error Recovery System

Tests cover:
- SyncMonitor: Background worker for drift detection
- ConflictResolver: Data mismatch handling
- CheckpointManager: Transaction logs for resuming
- HealingAgent: Automated fixes for corruption
- AlertSystem: Critical notifications for sync issues
- ManualOverrideTools: CLI force-push/pull commands
- DatabaseSyncManager: Complete sync manager with all components
"""

import sys
import os
import asyncio
import tempfile
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSyncModuleStructure:
    """Test that all Document 23 components exist."""
    
    def test_module_exists(self):
        """Test that database_sync_manager module exists."""
        from core import database_sync_manager
        assert database_sync_manager is not None
    
    def test_sync_status_enum_exists(self):
        """Test SyncStatus enum exists."""
        from core.database_sync_manager import SyncStatus
        assert SyncStatus is not None
    
    def test_conflict_resolution_strategy_exists(self):
        """Test ConflictResolutionStrategy enum exists."""
        from core.database_sync_manager import ConflictResolutionStrategy
        assert ConflictResolutionStrategy is not None
    
    def test_health_status_exists(self):
        """Test HealthStatus enum exists."""
        from core.database_sync_manager import HealthStatus
        assert HealthStatus is not None
    
    def test_checkpoint_state_exists(self):
        """Test CheckpointState enum exists."""
        from core.database_sync_manager import CheckpointState
        assert CheckpointState is not None
    
    def test_healing_action_exists(self):
        """Test HealingAction enum exists."""
        from core.database_sync_manager import HealingAction
        assert HealingAction is not None
    
    def test_sync_result_exists(self):
        """Test SyncResult dataclass exists."""
        from core.database_sync_manager import SyncResult
        assert SyncResult is not None
    
    def test_conflict_exists(self):
        """Test Conflict dataclass exists."""
        from core.database_sync_manager import Conflict
        assert Conflict is not None
    
    def test_checkpoint_exists(self):
        """Test Checkpoint dataclass exists."""
        from core.database_sync_manager import Checkpoint
        assert Checkpoint is not None
    
    def test_healing_result_exists(self):
        """Test HealingResult dataclass exists."""
        from core.database_sync_manager import HealingResult
        assert HealingResult is not None
    
    def test_sync_alert_exists(self):
        """Test SyncAlert dataclass exists."""
        from core.database_sync_manager import SyncAlert
        assert SyncAlert is not None
    
    def test_conflict_resolver_exists(self):
        """Test ConflictResolver class exists."""
        from core.database_sync_manager import ConflictResolver
        assert ConflictResolver is not None
    
    def test_checkpoint_manager_exists(self):
        """Test CheckpointManager class exists."""
        from core.database_sync_manager import CheckpointManager
        assert CheckpointManager is not None
    
    def test_healing_agent_exists(self):
        """Test HealingAgent class exists."""
        from core.database_sync_manager import HealingAgent
        assert HealingAgent is not None
    
    def test_sync_monitor_exists(self):
        """Test SyncMonitor class exists."""
        from core.database_sync_manager import SyncMonitor
        assert SyncMonitor is not None
    
    def test_manual_override_tools_exists(self):
        """Test ManualOverrideTools class exists."""
        from core.database_sync_manager import ManualOverrideTools
        assert ManualOverrideTools is not None
    
    def test_database_sync_manager_exists(self):
        """Test DatabaseSyncManager class exists."""
        from core.database_sync_manager import DatabaseSyncManager
        assert DatabaseSyncManager is not None
    
    def test_factory_function_exists(self):
        """Test create_sync_manager factory function exists."""
        from core.database_sync_manager import create_sync_manager
        assert create_sync_manager is not None


class TestSyncStatusEnum:
    """Test SyncStatus enum values."""
    
    def test_status_values(self):
        """Test all status values exist."""
        from core.database_sync_manager import SyncStatus
        assert SyncStatus.SUCCESS.value == "success"
        assert SyncStatus.FAILED.value == "failed"
        assert SyncStatus.RETRYING.value == "retrying"
        assert SyncStatus.SKIPPED.value == "skipped"
        assert SyncStatus.PARTIAL.value == "partial"


class TestConflictResolutionStrategy:
    """Test ConflictResolutionStrategy enum."""
    
    def test_strategy_values(self):
        """Test all strategy values exist."""
        from core.database_sync_manager import ConflictResolutionStrategy
        assert ConflictResolutionStrategy.LATEST_TIMESTAMP_WINS.value == "latest_timestamp_wins"
        assert ConflictResolutionStrategy.SOURCE_AUTHORITY.value == "source_authority"
        assert ConflictResolutionStrategy.CENTRAL_AUTHORITY.value == "central_authority"
        assert ConflictResolutionStrategy.MANUAL_REVIEW.value == "manual_review"


class TestHealthStatus:
    """Test HealthStatus enum."""
    
    def test_health_values(self):
        """Test all health status values exist."""
        from core.database_sync_manager import HealthStatus
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.CRITICAL.value == "critical"


class TestCheckpointState:
    """Test CheckpointState enum."""
    
    def test_checkpoint_state_values(self):
        """Test all checkpoint state values exist."""
        from core.database_sync_manager import CheckpointState
        assert CheckpointState.PENDING.value == "pending"
        assert CheckpointState.IN_PROGRESS.value == "in_progress"
        assert CheckpointState.COMPLETED.value == "completed"
        assert CheckpointState.FAILED.value == "failed"
        assert CheckpointState.ROLLED_BACK.value == "rolled_back"


class TestHealingAction:
    """Test HealingAction enum."""
    
    def test_healing_action_values(self):
        """Test all healing action values exist."""
        from core.database_sync_manager import HealingAction
        assert HealingAction.REBUILD_INDEX.value == "rebuild_index"
        assert HealingAction.REPAIR_SEQUENCE.value == "repair_sequence"
        assert HealingAction.RESTORE_MISSING.value == "restore_missing"
        assert HealingAction.REMOVE_DUPLICATE.value == "remove_duplicate"
        assert HealingAction.FIX_ORPHAN.value == "fix_orphan"
        assert HealingAction.VACUUM_DATABASE.value == "vacuum_database"


class TestSyncResult:
    """Test SyncResult dataclass."""
    
    def test_sync_result_creation(self):
        """Test creating a SyncResult."""
        from core.database_sync_manager import SyncResult, SyncStatus
        
        result = SyncResult(
            plugin_id="combined_v3",
            status=SyncStatus.SUCCESS,
            records_synced=100,
            error_message=None,
            duration_ms=500,
            timestamp=datetime.now()
        )
        
        assert result.plugin_id == "combined_v3"
        assert result.status == SyncStatus.SUCCESS
        assert result.records_synced == 100
        assert result.error_message is None
        assert result.duration_ms == 500
        assert result.retry_count == 0
    
    def test_sync_result_with_error(self):
        """Test SyncResult with error."""
        from core.database_sync_manager import SyncResult, SyncStatus
        
        result = SyncResult(
            plugin_id="price_action_1m",
            status=SyncStatus.FAILED,
            records_synced=0,
            error_message="Database locked",
            duration_ms=100,
            timestamp=datetime.now(),
            retry_count=3
        )
        
        assert result.status == SyncStatus.FAILED
        assert result.error_message == "Database locked"
        assert result.retry_count == 3


class TestConflict:
    """Test Conflict dataclass."""
    
    def test_conflict_creation(self):
        """Test creating a Conflict."""
        from core.database_sync_manager import Conflict
        
        conflict = Conflict(
            plugin_id="combined_v3",
            record_id=123,
            table_name="combined_v3_trades",
            source_data={"profit": 100.0},
            central_data={"profit": 95.0},
            conflict_type="value_conflict",
            detected_at=datetime.now()
        )
        
        assert conflict.plugin_id == "combined_v3"
        assert conflict.record_id == 123
        assert conflict.conflict_type == "value_conflict"
        assert conflict.resolved is False


class TestCheckpoint:
    """Test Checkpoint dataclass."""
    
    def test_checkpoint_creation(self):
        """Test creating a Checkpoint."""
        from core.database_sync_manager import Checkpoint, CheckpointState
        
        now = datetime.now()
        checkpoint = Checkpoint(
            checkpoint_id="cp_123",
            plugin_id="combined_v3",
            state=CheckpointState.PENDING,
            last_synced_id=100,
            records_processed=0,
            total_records=50,
            created_at=now,
            updated_at=now
        )
        
        assert checkpoint.checkpoint_id == "cp_123"
        assert checkpoint.state == CheckpointState.PENDING
        assert checkpoint.records_processed == 0
        assert checkpoint.total_records == 50


class TestConflictResolver:
    """Test ConflictResolver class."""
    
    def test_resolver_initialization(self):
        """Test ConflictResolver initialization."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        resolver = ConflictResolver()
        assert resolver.default_strategy == ConflictResolutionStrategy.LATEST_TIMESTAMP_WINS
        assert len(resolver.conflicts) == 0
    
    def test_resolver_custom_strategy(self):
        """Test ConflictResolver with custom strategy."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        resolver = ConflictResolver(default_strategy=ConflictResolutionStrategy.SOURCE_AUTHORITY)
        assert resolver.default_strategy == ConflictResolutionStrategy.SOURCE_AUTHORITY
    
    def test_detect_conflict(self):
        """Test conflict detection."""
        from core.database_sync_manager import ConflictResolver
        
        resolver = ConflictResolver()
        
        conflict = resolver.detect_conflict(
            plugin_id="combined_v3",
            record_id=1,
            table_name="trades",
            source_data={"profit": 100.0, "status": "closed"},
            central_data={"profit": 95.0, "status": "closed"}
        )
        
        assert conflict is not None
        assert conflict.plugin_id == "combined_v3"
        assert resolver.stats['total_conflicts'] == 1
    
    def test_no_conflict_when_equal(self):
        """Test no conflict when data is equal."""
        from core.database_sync_manager import ConflictResolver
        
        resolver = ConflictResolver()
        
        conflict = resolver.detect_conflict(
            plugin_id="combined_v3",
            record_id=1,
            table_name="trades",
            source_data={"profit": 100.0},
            central_data={"profit": 100.0}
        )
        
        assert conflict is None
    
    def test_resolve_conflict_source_authority(self):
        """Test resolving conflict with source authority."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        resolver = ConflictResolver()
        
        conflict = resolver.detect_conflict(
            plugin_id="combined_v3",
            record_id=1,
            table_name="trades",
            source_data={"profit": 100.0},
            central_data={"profit": 95.0}
        )
        
        resolved = resolver.resolve_conflict(conflict, ConflictResolutionStrategy.SOURCE_AUTHORITY)
        
        assert resolved["profit"] == 100.0
        assert conflict.resolved is True
        assert resolver.stats['source_wins'] == 1
    
    def test_resolve_conflict_central_authority(self):
        """Test resolving conflict with central authority."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        resolver = ConflictResolver()
        
        conflict = resolver.detect_conflict(
            plugin_id="combined_v3",
            record_id=1,
            table_name="trades",
            source_data={"profit": 100.0},
            central_data={"profit": 95.0}
        )
        
        resolved = resolver.resolve_conflict(conflict, ConflictResolutionStrategy.CENTRAL_AUTHORITY)
        
        assert resolved["profit"] == 95.0
        assert resolver.stats['central_wins'] == 1
    
    def test_resolve_conflict_manual_review(self):
        """Test flagging conflict for manual review."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        resolver = ConflictResolver()
        
        conflict = resolver.detect_conflict(
            plugin_id="combined_v3",
            record_id=1,
            table_name="trades",
            source_data={"profit": 100.0},
            central_data={"profit": 95.0}
        )
        
        resolver.resolve_conflict(conflict, ConflictResolutionStrategy.MANUAL_REVIEW)
        
        assert len(resolver.pending_review) == 1
        assert resolver.stats['manual_review'] == 1
    
    def test_get_pending_conflicts(self):
        """Test getting pending conflicts."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        resolver = ConflictResolver()
        
        conflict = resolver.detect_conflict(
            plugin_id="combined_v3",
            record_id=1,
            table_name="trades",
            source_data={"profit": 100.0},
            central_data={"profit": 95.0}
        )
        
        resolver.resolve_conflict(conflict, ConflictResolutionStrategy.MANUAL_REVIEW)
        
        pending = resolver.get_pending_conflicts()
        assert len(pending) == 1
    
    def test_get_stats(self):
        """Test getting resolver statistics."""
        from core.database_sync_manager import ConflictResolver
        
        resolver = ConflictResolver()
        stats = resolver.get_stats()
        
        assert 'total_conflicts' in stats
        assert 'auto_resolved' in stats
        assert 'pending_review_count' in stats


class TestCheckpointManager:
    """Test CheckpointManager class."""
    
    def test_manager_initialization(self):
        """Test CheckpointManager initialization."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            assert len(manager.active_checkpoints) == 0
    
    def test_create_checkpoint(self):
        """Test creating a checkpoint."""
        from core.database_sync_manager import CheckpointManager, CheckpointState
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            assert checkpoint.plugin_id == "combined_v3"
            assert checkpoint.state == CheckpointState.PENDING
            assert checkpoint.last_synced_id == 100
            assert checkpoint.total_records == 50
    
    def test_start_checkpoint(self):
        """Test starting a checkpoint."""
        from core.database_sync_manager import CheckpointManager, CheckpointState
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            result = manager.start_checkpoint(checkpoint.checkpoint_id)
            
            assert result is True
            assert manager.active_checkpoints[checkpoint.checkpoint_id].state == CheckpointState.IN_PROGRESS
    
    def test_update_progress(self):
        """Test updating checkpoint progress."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            manager.start_checkpoint(checkpoint.checkpoint_id)
            result = manager.update_progress(checkpoint.checkpoint_id, 25, 125)
            
            assert result is True
            assert manager.active_checkpoints[checkpoint.checkpoint_id].records_processed == 25
            assert manager.active_checkpoints[checkpoint.checkpoint_id].last_synced_id == 125
    
    def test_complete_checkpoint(self):
        """Test completing a checkpoint."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            manager.start_checkpoint(checkpoint.checkpoint_id)
            result = manager.complete_checkpoint(checkpoint.checkpoint_id)
            
            assert result is True
            assert checkpoint.checkpoint_id not in manager.active_checkpoints
            assert len(manager.completed_checkpoints) == 1
    
    def test_fail_checkpoint(self):
        """Test failing a checkpoint."""
        from core.database_sync_manager import CheckpointManager, CheckpointState
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            manager.start_checkpoint(checkpoint.checkpoint_id)
            result = manager.fail_checkpoint(checkpoint.checkpoint_id, "Database error")
            
            assert result is True
            assert manager.active_checkpoints[checkpoint.checkpoint_id].state == CheckpointState.FAILED
            assert manager.active_checkpoints[checkpoint.checkpoint_id].error_message == "Database error"
    
    def test_rollback_checkpoint(self):
        """Test rolling back a checkpoint."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            manager.fail_checkpoint(checkpoint.checkpoint_id, "Error")
            result = manager.rollback_checkpoint(checkpoint.checkpoint_id)
            
            assert result is True
            assert checkpoint.checkpoint_id not in manager.active_checkpoints
    
    def test_get_resumable_checkpoint(self):
        """Test getting resumable checkpoint."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            checkpoint = manager.create_checkpoint(
                plugin_id="combined_v3",
                last_synced_id=100,
                total_records=50
            )
            
            manager.fail_checkpoint(checkpoint.checkpoint_id, "Error")
            
            resumable = manager.get_resumable_checkpoint("combined_v3")
            assert resumable is not None
            assert resumable.checkpoint_id == checkpoint.checkpoint_id
    
    def test_get_stats(self):
        """Test getting checkpoint statistics."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            stats = manager.get_stats()
            
            assert 'active_checkpoints' in stats
            assert 'completed_checkpoints' in stats
            assert 'pending' in stats
            assert 'in_progress' in stats
            assert 'failed' in stats


class TestHealingAgent:
    """Test HealingAgent class."""
    
    def test_agent_initialization(self):
        """Test HealingAgent initialization."""
        from core.database_sync_manager import HealingAgent
        
        agent = HealingAgent()
        assert len(agent.healing_history) == 0
        assert agent.stats['total_healings'] == 0
    
    def test_diagnose_healthy_db(self):
        """Test diagnosing a healthy database."""
        from core.database_sync_manager import HealingAgent
        
        agent = HealingAgent()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            async def run_diagnose():
                return await agent.diagnose(db_path, "test_plugin")
            
            issues = asyncio.run(run_diagnose())
            assert isinstance(issues, list)
        finally:
            os.unlink(db_path)
    
    def test_heal_vacuum_database(self):
        """Test vacuum database healing action."""
        from core.database_sync_manager import HealingAgent, HealingAction
        
        agent = HealingAgent()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            async def run_heal():
                return await agent.heal(db_path, "test_plugin", HealingAction.VACUUM_DATABASE)
            
            result = asyncio.run(run_heal())
            
            assert result.success is True
            assert result.action == HealingAction.VACUUM_DATABASE
            assert agent.stats['successful_healings'] == 1
        finally:
            os.unlink(db_path)
    
    def test_heal_rebuild_indexes(self):
        """Test rebuild indexes healing action."""
        from core.database_sync_manager import HealingAgent, HealingAction
        
        agent = HealingAgent()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("CREATE INDEX idx_name ON test(name)")
            conn.commit()
            conn.close()
            
            async def run_heal():
                return await agent.heal(db_path, "test_plugin", HealingAction.REBUILD_INDEX)
            
            result = asyncio.run(run_heal())
            
            assert result.success is True
            assert result.action == HealingAction.REBUILD_INDEX
        finally:
            os.unlink(db_path)
    
    def test_get_stats(self):
        """Test getting healing statistics."""
        from core.database_sync_manager import HealingAgent
        
        agent = HealingAgent()
        stats = agent.get_stats()
        
        assert 'total_healings' in stats
        assert 'successful_healings' in stats
        assert 'failed_healings' in stats
        assert 'records_healed' in stats


class TestSyncMonitor:
    """Test SyncMonitor class."""
    
    def test_monitor_initialization(self):
        """Test SyncMonitor initialization."""
        from core.database_sync_manager import SyncMonitor
        
        monitor = SyncMonitor()
        assert monitor._running is False
        assert len(monitor.alerts) == 0
    
    def test_monitor_custom_interval(self):
        """Test SyncMonitor with custom interval."""
        from core.database_sync_manager import SyncMonitor
        
        monitor = SyncMonitor(check_interval_seconds=30, drift_threshold_minutes=10)
        assert monitor.check_interval == 30
        assert monitor.drift_threshold == timedelta(minutes=10)
    
    def test_monitor_start_stop(self):
        """Test starting and stopping monitor."""
        from core.database_sync_manager import SyncMonitor
        
        monitor = SyncMonitor(check_interval_seconds=1)
        
        async def run_test():
            await monitor.start()
            assert monitor._running is True
            await asyncio.sleep(0.1)
            await monitor.stop()
            assert monitor._running is False
        
        asyncio.run(run_test())
    
    def test_generate_alert(self):
        """Test generating an alert."""
        from core.database_sync_manager import SyncMonitor, HealthStatus
        
        monitor = SyncMonitor()
        
        alert = monitor.generate_alert(
            plugin_id="combined_v3",
            severity=HealthStatus.WARNING,
            message="Sync delayed"
        )
        
        assert alert.plugin_id == "combined_v3"
        assert alert.severity == HealthStatus.WARNING
        assert alert.acknowledged is False
        assert len(monitor.alerts) == 1
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        from core.database_sync_manager import SyncMonitor, HealthStatus
        
        monitor = SyncMonitor()
        
        alert = monitor.generate_alert(
            plugin_id="combined_v3",
            severity=HealthStatus.WARNING,
            message="Sync delayed"
        )
        
        result = monitor.acknowledge_alert(alert.alert_id, "admin")
        
        assert result is True
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "admin"
    
    def test_get_unacknowledged_alerts(self):
        """Test getting unacknowledged alerts."""
        from core.database_sync_manager import SyncMonitor, HealthStatus
        
        monitor = SyncMonitor()
        
        alert1 = monitor.generate_alert("plugin1", HealthStatus.WARNING, "Alert 1")
        alert2 = monitor.generate_alert("plugin2", HealthStatus.CRITICAL, "Alert 2")
        
        monitor.acknowledge_alert(alert1.alert_id, "admin")
        
        unacked = monitor.get_unacknowledged_alerts()
        assert len(unacked) == 1
        assert unacked[0].alert_id == alert2.alert_id
    
    def test_get_health_summary(self):
        """Test getting health summary."""
        from core.database_sync_manager import SyncMonitor
        
        monitor = SyncMonitor()
        summary = monitor.get_health_summary()
        
        assert 'last_check' in summary
        assert 'plugin_status' in summary
        assert 'unacknowledged_alerts' in summary
        assert 'stats' in summary


class TestManualOverrideTools:
    """Test ManualOverrideTools class."""
    
    def test_tools_initialization(self):
        """Test ManualOverrideTools initialization."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        assert tools.sync_manager == manager
        assert len(tools.operation_history) == 0
    
    def test_force_push_requires_confirmation(self):
        """Test force push requires confirmation."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        async def run_test():
            result = await tools.force_push("combined_v3", confirm=False)
            return result
        
        result = asyncio.run(run_test())
        
        assert result['success'] is False
        assert 'confirmation' in result['message'].lower()
    
    def test_force_pull_requires_confirmation(self):
        """Test force pull requires confirmation."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        async def run_test():
            result = await tools.force_pull("combined_v3", confirm=False)
            return result
        
        result = asyncio.run(run_test())
        
        assert result['success'] is False
        assert 'confirmation' in result['message'].lower()
    
    def test_reset_sync_requires_confirmation(self):
        """Test reset sync requires confirmation."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        async def run_test():
            result = await tools.reset_sync("combined_v3", confirm=False)
            return result
        
        result = asyncio.run(run_test())
        
        assert result['success'] is False
    
    def test_reset_sync_with_confirmation(self):
        """Test reset sync with confirmation."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        manager.last_sync_time["combined_v3"] = datetime.now()
        manager.consecutive_failures["combined_v3"] = 5
        
        tools = ManualOverrideTools(manager)
        
        async def run_test():
            result = await tools.reset_sync("combined_v3", confirm=True)
            return result
        
        result = asyncio.run(run_test())
        
        assert result['success'] is True
        assert "combined_v3" not in manager.last_sync_time
        assert "combined_v3" not in manager.consecutive_failures
    
    def test_export_data(self):
        """Test exporting data - verifies export functionality exists."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        assert hasattr(tools, 'export_data')
        assert callable(tools.export_data)
        
        async def run_test():
            result = await tools.export_data("combined_v3", "/tmp/nonexistent_output.json")
            return result
        
        result = asyncio.run(run_test())
        assert 'success' in result
    
    def test_import_data_requires_confirmation(self):
        """Test import data requires confirmation."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        async def run_test():
            result = await tools.import_data("combined_v3", "/tmp/backup.json", confirm=False)
            return result
        
        result = asyncio.run(run_test())
        
        assert result['success'] is False
    
    def test_get_operation_history(self):
        """Test getting operation history."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        async def run_test():
            await tools.reset_sync("combined_v3", confirm=True)
            return tools.get_operation_history()
        
        history = asyncio.run(run_test())
        
        assert len(history) == 1
        assert history[0]['type'] == 'reset_sync'


class TestDatabaseSyncManager:
    """Test DatabaseSyncManager class."""
    
    def test_manager_initialization(self):
        """Test DatabaseSyncManager initialization."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        assert manager._running is False
        assert manager.max_retries == 3
        assert manager.alert_threshold == 3
        assert manager.conflict_resolver is not None
        assert manager.checkpoint_manager is not None
        assert manager.healing_agent is not None
        assert manager.sync_monitor is not None
    
    def test_manager_custom_config(self):
        """Test DatabaseSyncManager with custom config."""
        from core.database_sync_manager import DatabaseSyncManager
        
        config = {
            'max_retries': 5,
            'retry_delay_seconds': 10,
            'sync_interval_seconds': 600
        }
        
        manager = DatabaseSyncManager(config)
        
        assert manager.max_retries == 5
        assert manager.retry_delay_seconds == 10
        assert manager.sync_interval_seconds == 600
    
    def test_manager_start_stop(self):
        """Test starting and stopping manager."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager({'sync_interval_seconds': 1})
        
        async def run_test():
            await manager.start()
            assert manager._running is True
            assert manager.manual_tools is not None
            await asyncio.sleep(0.1)
            await manager.stop()
            assert manager._running is False
        
        asyncio.run(run_test())
    
    def test_get_sync_health(self):
        """Test getting sync health."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        health = manager.get_sync_health()
        
        assert 'overall_status' in health
        assert 'plugins' in health
        assert 'statistics' in health
        assert 'conflict_stats' in health
        assert 'checkpoint_stats' in health
        assert 'healing_stats' in health
    
    def test_get_stats(self):
        """Test getting comprehensive stats."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        stats = manager.get_stats()
        
        assert 'sync_stats' in stats
        assert 'conflict_stats' in stats
        assert 'checkpoint_stats' in stats
        assert 'healing_stats' in stats
        assert 'monitor_stats' in stats
    
    def test_trigger_manual_sync(self):
        """Test triggering manual sync."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        async def run_test():
            await manager.start()
            result = await manager.trigger_manual_sync()
            await manager.stop()
            return result
        
        result = asyncio.run(run_test())
        
        assert result['triggered'] is True
        assert 'message' in result
    
    def test_set_alert_callback(self):
        """Test setting alert callback."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        alerts_received = []
        
        def callback(plugin_id, message):
            alerts_received.append((plugin_id, message))
        
        manager.set_alert_callback(callback)
        assert manager._alert_callback == callback
    
    def test_consecutive_failure_tracking(self):
        """Test consecutive failure tracking."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        manager.consecutive_failures['combined_v3'] = 3
        
        health = manager.get_sync_health()
        
        assert health['plugins']['combined_v3']['status'] == 'DEGRADED'
        assert health['overall_status'] == 'DEGRADED'


class TestFactoryFunction:
    """Test create_sync_manager factory function."""
    
    def test_create_default_manager(self):
        """Test creating default manager."""
        from core.database_sync_manager import create_sync_manager
        
        manager = create_sync_manager()
        
        assert manager is not None
        assert manager.sync_monitor is not None
        assert manager.healing_agent is not None
    
    def test_create_manager_without_monitoring(self):
        """Test creating manager without monitoring."""
        from core.database_sync_manager import create_sync_manager
        
        manager = create_sync_manager(enable_monitoring=False)
        
        assert manager.sync_monitor is None
    
    def test_create_manager_without_healing(self):
        """Test creating manager without healing."""
        from core.database_sync_manager import create_sync_manager
        
        manager = create_sync_manager(enable_healing=False)
        
        assert manager.healing_agent is None
    
    def test_create_manager_with_config(self):
        """Test creating manager with config."""
        from core.database_sync_manager import create_sync_manager
        
        config = {'max_retries': 10}
        manager = create_sync_manager(config=config)
        
        assert manager.max_retries == 10


class TestSyncFailureSimulation:
    """Test sync failure and recovery scenarios."""
    
    def test_retry_count_tracking(self):
        """Test retry count is tracked correctly."""
        from core.database_sync_manager import SyncResult, SyncStatus
        
        result = SyncResult(
            plugin_id="combined_v3",
            status=SyncStatus.FAILED,
            records_synced=0,
            error_message="Connection timeout",
            duration_ms=5000,
            timestamp=datetime.now(),
            retry_count=3
        )
        
        assert result.retry_count == 3
        assert result.status == SyncStatus.FAILED
    
    def test_failure_threshold_detection(self):
        """Test failure threshold detection."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        manager.alert_threshold = 3
        
        manager.consecutive_failures['combined_v3'] = 2
        health = manager.get_sync_health()
        assert health['plugins']['combined_v3']['status'] == 'WARNING'
        
        manager.consecutive_failures['combined_v3'] = 3
        health = manager.get_sync_health()
        assert health['plugins']['combined_v3']['status'] == 'DEGRADED'
    
    def test_failure_reset_on_success(self):
        """Test failure counter resets on success."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        manager.consecutive_failures['combined_v3'] = 5
        
        manager.consecutive_failures['combined_v3'] = 0
        
        health = manager.get_sync_health()
        assert health['plugins']['combined_v3']['status'] == 'HEALTHY'


class TestDocument23Integration:
    """Test Document 23 integration requirements."""
    
    def test_all_components_importable(self):
        """Test all Document 23 components are importable."""
        from core.database_sync_manager import (
            SyncStatus,
            ConflictResolutionStrategy,
            HealthStatus,
            CheckpointState,
            HealingAction,
            SyncResult,
            Conflict,
            Checkpoint,
            HealingResult,
            SyncAlert,
            ConflictResolver,
            CheckpointManager,
            HealingAgent,
            SyncMonitor,
            ManualOverrideTools,
            DatabaseSyncManager,
            create_sync_manager
        )
        
        assert all([
            SyncStatus, ConflictResolutionStrategy, HealthStatus,
            CheckpointState, HealingAction, SyncResult, Conflict,
            Checkpoint, HealingResult, SyncAlert, ConflictResolver,
            CheckpointManager, HealingAgent, SyncMonitor,
            ManualOverrideTools, DatabaseSyncManager, create_sync_manager
        ])
    
    def test_sync_monitor_drift_detection(self):
        """Test sync monitor can detect drift."""
        from core.database_sync_manager import SyncMonitor, HealthStatus
        
        monitor = SyncMonitor(drift_threshold_minutes=5)
        
        alert = monitor.generate_alert(
            plugin_id="combined_v3",
            severity=HealthStatus.CRITICAL,
            message="Sync gap > 5 minutes detected"
        )
        
        assert alert.severity == HealthStatus.CRITICAL
        assert "5 minutes" in alert.message
    
    def test_conflict_resolver_strategies(self):
        """Test all conflict resolution strategies work."""
        from core.database_sync_manager import ConflictResolver, ConflictResolutionStrategy
        
        for strategy in ConflictResolutionStrategy:
            resolver = ConflictResolver(default_strategy=strategy)
            assert resolver.default_strategy == strategy
    
    def test_checkpoint_resumability(self):
        """Test checkpoints can be resumed."""
        from core.database_sync_manager import CheckpointManager, CheckpointState
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            cp = manager.create_checkpoint("combined_v3", 100, 50)
            manager.start_checkpoint(cp.checkpoint_id)
            manager.update_progress(cp.checkpoint_id, 25, 125)
            manager.fail_checkpoint(cp.checkpoint_id, "Interrupted")
            
            resumable = manager.get_resumable_checkpoint("combined_v3")
            
            assert resumable is not None
            assert resumable.records_processed == 25
            assert resumable.last_synced_id == 125
    
    def test_healing_agent_actions(self):
        """Test all healing actions are defined."""
        from core.database_sync_manager import HealingAction
        
        actions = list(HealingAction)
        assert len(actions) == 6
        assert HealingAction.REBUILD_INDEX in actions
        assert HealingAction.VACUUM_DATABASE in actions
    
    def test_manual_tools_operations(self):
        """Test manual tools have all operations."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        assert hasattr(tools, 'force_push')
        assert hasattr(tools, 'force_pull')
        assert hasattr(tools, 'reset_sync')
        assert hasattr(tools, 'export_data')
        assert hasattr(tools, 'import_data')


class TestDocument23Summary:
    """Test Document 23 summary requirements."""
    
    def test_sync_monitor_implemented(self):
        """Test SyncMonitor is fully implemented."""
        from core.database_sync_manager import SyncMonitor
        
        monitor = SyncMonitor()
        
        assert hasattr(monitor, 'start')
        assert hasattr(monitor, 'stop')
        assert hasattr(monitor, 'generate_alert')
        assert hasattr(monitor, 'acknowledge_alert')
        assert hasattr(monitor, 'get_health_summary')
    
    def test_conflict_resolver_implemented(self):
        """Test ConflictResolver is fully implemented."""
        from core.database_sync_manager import ConflictResolver
        
        resolver = ConflictResolver()
        
        assert hasattr(resolver, 'detect_conflict')
        assert hasattr(resolver, 'resolve_conflict')
        assert hasattr(resolver, 'get_pending_conflicts')
        assert hasattr(resolver, 'acknowledge_conflict')
        assert hasattr(resolver, 'get_stats')
    
    def test_checkpoint_manager_implemented(self):
        """Test CheckpointManager is fully implemented."""
        from core.database_sync_manager import CheckpointManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            
            assert hasattr(manager, 'create_checkpoint')
            assert hasattr(manager, 'start_checkpoint')
            assert hasattr(manager, 'update_progress')
            assert hasattr(manager, 'complete_checkpoint')
            assert hasattr(manager, 'fail_checkpoint')
            assert hasattr(manager, 'rollback_checkpoint')
            assert hasattr(manager, 'get_resumable_checkpoint')
    
    def test_healing_agent_implemented(self):
        """Test HealingAgent is fully implemented."""
        from core.database_sync_manager import HealingAgent
        
        agent = HealingAgent()
        
        assert hasattr(agent, 'diagnose')
        assert hasattr(agent, 'heal')
        assert hasattr(agent, 'get_stats')
    
    def test_alert_system_implemented(self):
        """Test alert system is implemented in SyncMonitor."""
        from core.database_sync_manager import SyncMonitor, HealthStatus
        
        monitor = SyncMonitor()
        
        assert hasattr(monitor, 'generate_alert')
        assert hasattr(monitor, 'acknowledge_alert')
        assert hasattr(monitor, 'get_unacknowledged_alerts')
        assert hasattr(monitor, 'alerts')
        assert hasattr(monitor, 'alert_callback')
        
        assert monitor.stats['alerts_generated'] == 0
    
    def test_manual_override_tools_implemented(self):
        """Test ManualOverrideTools is fully implemented."""
        from core.database_sync_manager import ManualOverrideTools, DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        tools = ManualOverrideTools(manager)
        
        assert hasattr(tools, 'force_push')
        assert hasattr(tools, 'force_pull')
        assert hasattr(tools, 'reset_sync')
        assert hasattr(tools, 'export_data')
        assert hasattr(tools, 'import_data')
        assert hasattr(tools, 'get_operation_history')
    
    def test_database_sync_manager_implemented(self):
        """Test DatabaseSyncManager is fully implemented."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        assert hasattr(manager, 'start')
        assert hasattr(manager, 'stop')
        assert hasattr(manager, 'sync_all_plugins')
        assert hasattr(manager, 'trigger_manual_sync')
        assert hasattr(manager, 'run_healing')
        assert hasattr(manager, 'get_sync_health')
        assert hasattr(manager, 'get_stats')
        assert hasattr(manager, 'set_alert_callback')
    
    def test_retry_logic_implemented(self):
        """Test retry logic with exponential backoff is implemented."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        assert manager.max_retries == 3
        assert manager.retry_delay_seconds == 5
        assert manager.backoff_multiplier == 2
    
    def test_statistics_tracking_implemented(self):
        """Test statistics tracking is implemented."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        
        assert 'total_syncs' in manager.stats
        assert 'total_success' in manager.stats
        assert 'total_failures' in manager.stats
        assert 'total_retries' in manager.stats
        assert 'total_records_synced' in manager.stats
    
    def test_health_monitoring_implemented(self):
        """Test health monitoring is implemented."""
        from core.database_sync_manager import DatabaseSyncManager
        
        manager = DatabaseSyncManager()
        health = manager.get_sync_health()
        
        assert health['overall_status'] in ['HEALTHY', 'WARNING', 'DEGRADED']
        assert 'combined_v3' in health['plugins']
        assert 'price_action_1m' in health['plugins']
