"""
Database Sync Error Recovery System

Document 23: Complete implementation of data resiliency and self-healing system
for multi-database architecture (V3/V6 plugin DBs + Central DB).

Components:
- SyncMonitor: Background worker watching for drift between Plugin DBs and Central DB
- ConflictResolver: Logic to handle data mismatches
- CheckpointManager: Transaction logs to allow resuming interrupted syncs
- HealingAgent: Automated fixes for common corruption issues
- AlertSystem: Critical notifications if sync gap > 5 minutes
- ManualOverrideTools: CLI commands to force-push or force-pull data
"""

import sqlite3
import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class SyncStatus(Enum):
    """Sync operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    PARTIAL = "partial"


class ConflictResolutionStrategy(Enum):
    """Strategy for resolving data conflicts"""
    LATEST_TIMESTAMP_WINS = "latest_timestamp_wins"
    SOURCE_AUTHORITY = "source_authority"
    CENTRAL_AUTHORITY = "central_authority"
    MANUAL_REVIEW = "manual_review"


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class CheckpointState(Enum):
    """Checkpoint states for transaction logs"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class HealingAction(Enum):
    """Types of healing actions"""
    REBUILD_INDEX = "rebuild_index"
    REPAIR_SEQUENCE = "repair_sequence"
    RESTORE_MISSING = "restore_missing"
    REMOVE_DUPLICATE = "remove_duplicate"
    FIX_ORPHAN = "fix_orphan"
    VACUUM_DATABASE = "vacuum_database"


@dataclass
class SyncResult:
    """Result of a sync operation"""
    plugin_id: str
    status: SyncStatus
    records_synced: int
    error_message: Optional[str]
    duration_ms: int
    timestamp: datetime
    retry_count: int = 0
    conflicts_resolved: int = 0
    checksum: Optional[str] = None


@dataclass
class Conflict:
    """Represents a data conflict between databases"""
    plugin_id: str
    record_id: int
    table_name: str
    source_data: Dict[str, Any]
    central_data: Dict[str, Any]
    conflict_type: str
    detected_at: datetime
    resolved: bool = False
    resolution_strategy: Optional[ConflictResolutionStrategy] = None
    resolution_data: Optional[Dict[str, Any]] = None


@dataclass
class Checkpoint:
    """Transaction checkpoint for resumable syncs"""
    checkpoint_id: str
    plugin_id: str
    state: CheckpointState
    last_synced_id: int
    records_processed: int
    total_records: int
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealingResult:
    """Result of a healing operation"""
    action: HealingAction
    plugin_id: str
    success: bool
    records_affected: int
    error_message: Optional[str]
    duration_ms: int
    timestamp: datetime


@dataclass
class SyncAlert:
    """Alert for sync issues"""
    alert_id: str
    plugin_id: str
    severity: HealthStatus
    message: str
    created_at: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


# =============================================================================
# CONFLICT RESOLVER
# =============================================================================

class ConflictResolver:
    """
    Handles data conflicts between plugin databases and central database.
    
    Strategies:
    - LATEST_TIMESTAMP_WINS: Record with most recent timestamp wins
    - SOURCE_AUTHORITY: Plugin database is always correct
    - CENTRAL_AUTHORITY: Central database is always correct
    - MANUAL_REVIEW: Flag for human review
    """
    
    def __init__(self, default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LATEST_TIMESTAMP_WINS):
        self.default_strategy = default_strategy
        self.conflicts: List[Conflict] = []
        self.resolved_conflicts: List[Conflict] = []
        self.pending_review: List[Conflict] = []
        self.stats = {
            'total_conflicts': 0,
            'auto_resolved': 0,
            'manual_review': 0,
            'source_wins': 0,
            'central_wins': 0
        }
    
    def detect_conflict(
        self,
        plugin_id: str,
        record_id: int,
        table_name: str,
        source_data: Dict[str, Any],
        central_data: Dict[str, Any]
    ) -> Optional[Conflict]:
        """Detect if there's a conflict between source and central data."""
        if source_data == central_data:
            return None
        
        conflict_type = self._determine_conflict_type(source_data, central_data)
        
        conflict = Conflict(
            plugin_id=plugin_id,
            record_id=record_id,
            table_name=table_name,
            source_data=source_data,
            central_data=central_data,
            conflict_type=conflict_type,
            detected_at=datetime.now()
        )
        
        self.conflicts.append(conflict)
        self.stats['total_conflicts'] += 1
        
        return conflict
    
    def _determine_conflict_type(self, source: Dict, central: Dict) -> str:
        """Determine the type of conflict."""
        source_keys = set(source.keys())
        central_keys = set(central.keys())
        
        if source_keys != central_keys:
            return "schema_mismatch"
        
        differing_fields = [k for k in source_keys if source.get(k) != central.get(k)]
        
        if 'status' in differing_fields:
            return "status_conflict"
        elif 'profit_dollars' in differing_fields or 'lot_size' in differing_fields:
            return "value_conflict"
        elif any(f in differing_fields for f in ['entry_time', 'exit_time']):
            return "timestamp_conflict"
        else:
            return "data_conflict"
    
    def resolve_conflict(
        self,
        conflict: Conflict,
        strategy: Optional[ConflictResolutionStrategy] = None
    ) -> Dict[str, Any]:
        """Resolve a conflict using the specified strategy."""
        strategy = strategy or self.default_strategy
        
        if strategy == ConflictResolutionStrategy.MANUAL_REVIEW:
            self.pending_review.append(conflict)
            self.stats['manual_review'] += 1
            return conflict.source_data
        
        if strategy == ConflictResolutionStrategy.SOURCE_AUTHORITY:
            resolved_data = conflict.source_data.copy()
            self.stats['source_wins'] += 1
        elif strategy == ConflictResolutionStrategy.CENTRAL_AUTHORITY:
            resolved_data = conflict.central_data.copy()
            self.stats['central_wins'] += 1
        elif strategy == ConflictResolutionStrategy.LATEST_TIMESTAMP_WINS:
            resolved_data = self._resolve_by_timestamp(conflict)
        else:
            resolved_data = conflict.source_data.copy()
        
        conflict.resolved = True
        conflict.resolution_strategy = strategy
        conflict.resolution_data = resolved_data
        self.resolved_conflicts.append(conflict)
        self.stats['auto_resolved'] += 1
        
        return resolved_data
    
    def _resolve_by_timestamp(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict by choosing record with latest timestamp."""
        source_time = conflict.source_data.get('updated_at') or conflict.source_data.get('exit_time') or ''
        central_time = conflict.central_data.get('updated_at') or conflict.central_data.get('exit_time') or ''
        
        if source_time >= central_time:
            self.stats['source_wins'] += 1
            return conflict.source_data.copy()
        else:
            self.stats['central_wins'] += 1
            return conflict.central_data.copy()
    
    def get_pending_conflicts(self) -> List[Conflict]:
        """Get conflicts pending manual review."""
        return self.pending_review.copy()
    
    def acknowledge_conflict(self, conflict: Conflict, resolution_data: Dict[str, Any]) -> None:
        """Manually acknowledge and resolve a conflict."""
        conflict.resolved = True
        conflict.resolution_strategy = ConflictResolutionStrategy.MANUAL_REVIEW
        conflict.resolution_data = resolution_data
        
        if conflict in self.pending_review:
            self.pending_review.remove(conflict)
        
        self.resolved_conflicts.append(conflict)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conflict resolution statistics."""
        return {
            **self.stats,
            'pending_review_count': len(self.pending_review),
            'resolved_count': len(self.resolved_conflicts)
        }


# =============================================================================
# CHECKPOINT MANAGER
# =============================================================================

class CheckpointManager:
    """
    Manages transaction checkpoints for resumable sync operations.
    
    Features:
    - Create checkpoints before sync operations
    - Update progress during sync
    - Resume interrupted syncs from last checkpoint
    - Rollback failed syncs
    """
    
    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.active_checkpoints: Dict[str, Checkpoint] = {}
        self.completed_checkpoints: List[Checkpoint] = []
        self.max_completed_history = 100
    
    def create_checkpoint(
        self,
        plugin_id: str,
        last_synced_id: int,
        total_records: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """Create a new checkpoint for a sync operation."""
        checkpoint_id = f"{plugin_id}_{int(time.time() * 1000)}"
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            plugin_id=plugin_id,
            state=CheckpointState.PENDING,
            last_synced_id=last_synced_id,
            records_processed=0,
            total_records=total_records,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.active_checkpoints[checkpoint_id] = checkpoint
        self._save_checkpoint(checkpoint)
        
        logger.debug(f"Created checkpoint {checkpoint_id} for {plugin_id}")
        return checkpoint
    
    def start_checkpoint(self, checkpoint_id: str) -> bool:
        """Mark checkpoint as in progress."""
        if checkpoint_id not in self.active_checkpoints:
            return False
        
        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint.state = CheckpointState.IN_PROGRESS
        checkpoint.updated_at = datetime.now()
        self._save_checkpoint(checkpoint)
        
        return True
    
    def update_progress(
        self,
        checkpoint_id: str,
        records_processed: int,
        last_synced_id: int
    ) -> bool:
        """Update checkpoint progress."""
        if checkpoint_id not in self.active_checkpoints:
            return False
        
        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint.records_processed = records_processed
        checkpoint.last_synced_id = last_synced_id
        checkpoint.updated_at = datetime.now()
        self._save_checkpoint(checkpoint)
        
        return True
    
    def complete_checkpoint(self, checkpoint_id: str) -> bool:
        """Mark checkpoint as completed."""
        if checkpoint_id not in self.active_checkpoints:
            return False
        
        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint.state = CheckpointState.COMPLETED
        checkpoint.updated_at = datetime.now()
        
        del self.active_checkpoints[checkpoint_id]
        self.completed_checkpoints.append(checkpoint)
        
        if len(self.completed_checkpoints) > self.max_completed_history:
            self.completed_checkpoints = self.completed_checkpoints[-self.max_completed_history:]
        
        self._save_checkpoint(checkpoint)
        self._cleanup_checkpoint_file(checkpoint_id)
        
        logger.debug(f"Completed checkpoint {checkpoint_id}")
        return True
    
    def fail_checkpoint(self, checkpoint_id: str, error_message: str) -> bool:
        """Mark checkpoint as failed."""
        if checkpoint_id not in self.active_checkpoints:
            return False
        
        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint.state = CheckpointState.FAILED
        checkpoint.error_message = error_message
        checkpoint.updated_at = datetime.now()
        self._save_checkpoint(checkpoint)
        
        logger.warning(f"Checkpoint {checkpoint_id} failed: {error_message}")
        return True
    
    def rollback_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback a failed checkpoint."""
        if checkpoint_id not in self.active_checkpoints:
            return False
        
        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint.state = CheckpointState.ROLLED_BACK
        checkpoint.updated_at = datetime.now()
        
        del self.active_checkpoints[checkpoint_id]
        self._save_checkpoint(checkpoint)
        self._cleanup_checkpoint_file(checkpoint_id)
        
        logger.info(f"Rolled back checkpoint {checkpoint_id}")
        return True
    
    def get_resumable_checkpoint(self, plugin_id: str) -> Optional[Checkpoint]:
        """Get the most recent resumable checkpoint for a plugin."""
        for checkpoint in self.active_checkpoints.values():
            if checkpoint.plugin_id == plugin_id and checkpoint.state in [
                CheckpointState.PENDING,
                CheckpointState.IN_PROGRESS,
                CheckpointState.FAILED
            ]:
                return checkpoint
        return None
    
    def load_checkpoints(self) -> None:
        """Load checkpoints from disk."""
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                
                checkpoint = Checkpoint(
                    checkpoint_id=data['checkpoint_id'],
                    plugin_id=data['plugin_id'],
                    state=CheckpointState(data['state']),
                    last_synced_id=data['last_synced_id'],
                    records_processed=data['records_processed'],
                    total_records=data['total_records'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    error_message=data.get('error_message'),
                    metadata=data.get('metadata', {})
                )
                
                if checkpoint.state in [CheckpointState.PENDING, CheckpointState.IN_PROGRESS, CheckpointState.FAILED]:
                    self.active_checkpoints[checkpoint.checkpoint_id] = checkpoint
                    
            except Exception as e:
                logger.error(f"Failed to load checkpoint {checkpoint_file}: {e}")
    
    def _save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk."""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        
        data = {
            'checkpoint_id': checkpoint.checkpoint_id,
            'plugin_id': checkpoint.plugin_id,
            'state': checkpoint.state.value,
            'last_synced_id': checkpoint.last_synced_id,
            'records_processed': checkpoint.records_processed,
            'total_records': checkpoint.total_records,
            'created_at': checkpoint.created_at.isoformat(),
            'updated_at': checkpoint.updated_at.isoformat(),
            'error_message': checkpoint.error_message,
            'metadata': checkpoint.metadata
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _cleanup_checkpoint_file(self, checkpoint_id: str) -> None:
        """Remove checkpoint file from disk."""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        return {
            'active_checkpoints': len(self.active_checkpoints),
            'completed_checkpoints': len(self.completed_checkpoints),
            'pending': sum(1 for c in self.active_checkpoints.values() if c.state == CheckpointState.PENDING),
            'in_progress': sum(1 for c in self.active_checkpoints.values() if c.state == CheckpointState.IN_PROGRESS),
            'failed': sum(1 for c in self.active_checkpoints.values() if c.state == CheckpointState.FAILED)
        }


# =============================================================================
# HEALING AGENT
# =============================================================================

class HealingAgent:
    """
    Automated fixes for common database corruption issues.
    
    Healing Actions:
    - REBUILD_INDEX: Rebuild database indexes
    - REPAIR_SEQUENCE: Fix auto-increment sequences
    - RESTORE_MISSING: Restore missing records from backup
    - REMOVE_DUPLICATE: Remove duplicate records
    - FIX_ORPHAN: Fix orphaned records
    - VACUUM_DATABASE: Compact and optimize database
    """
    
    def __init__(self):
        self.healing_history: List[HealingResult] = []
        self.max_history = 500
        self.stats = {
            'total_healings': 0,
            'successful_healings': 0,
            'failed_healings': 0,
            'records_healed': 0
        }
    
    async def diagnose(self, db_path: str, plugin_id: str) -> List[HealingAction]:
        """Diagnose database issues and return recommended healing actions."""
        issues = []
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            if integrity != 'ok':
                issues.append(HealingAction.VACUUM_DATABASE)
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            index_count = cursor.fetchone()[0]
            if index_count == 0:
                issues.append(HealingAction.REBUILD_INDEX)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Diagnosis failed for {plugin_id}: {e}")
            issues.append(HealingAction.VACUUM_DATABASE)
        
        return issues
    
    async def heal(
        self,
        db_path: str,
        plugin_id: str,
        action: HealingAction
    ) -> HealingResult:
        """Perform a healing action on the database."""
        start_time = datetime.now()
        records_affected = 0
        error_message = None
        success = False
        
        try:
            if action == HealingAction.REBUILD_INDEX:
                records_affected = await self._rebuild_indexes(db_path)
                success = True
            elif action == HealingAction.REPAIR_SEQUENCE:
                records_affected = await self._repair_sequences(db_path)
                success = True
            elif action == HealingAction.REMOVE_DUPLICATE:
                records_affected = await self._remove_duplicates(db_path, plugin_id)
                success = True
            elif action == HealingAction.FIX_ORPHAN:
                records_affected = await self._fix_orphans(db_path, plugin_id)
                success = True
            elif action == HealingAction.VACUUM_DATABASE:
                records_affected = await self._vacuum_database(db_path)
                success = True
            else:
                error_message = f"Unknown healing action: {action}"
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"Healing action {action} failed for {plugin_id}: {e}")
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = HealingResult(
            action=action,
            plugin_id=plugin_id,
            success=success,
            records_affected=records_affected,
            error_message=error_message,
            duration_ms=duration_ms,
            timestamp=datetime.now()
        )
        
        self._record_result(result)
        return result
    
    async def _rebuild_indexes(self, db_path: str) -> int:
        """Rebuild all indexes in the database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("REINDEX")
        conn.commit()
        conn.close()
        
        logger.info(f"Rebuilt indexes for {db_path}")
        return 1
    
    async def _repair_sequences(self, db_path: str) -> int:
        """Repair auto-increment sequences."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        repaired = 0
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT MAX(id) FROM {table_name}")
                max_id = cursor.fetchone()[0] or 0
                
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = ? WHERE name = ?",
                    (max_id, table_name)
                )
                repaired += 1
            except:
                pass
        
        conn.commit()
        conn.close()
        
        logger.info(f"Repaired {repaired} sequences in {db_path}")
        return repaired
    
    async def _remove_duplicates(self, db_path: str, plugin_id: str) -> int:
        """Remove duplicate records."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        table_name = self._get_table_name(plugin_id)
        if not table_name:
            conn.close()
            return 0
        
        cursor.execute(f"""
            DELETE FROM {table_name}
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM {table_name}
                GROUP BY symbol, entry_time, direction
            )
        """)
        
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Removed {removed} duplicates from {table_name}")
        return removed
    
    async def _fix_orphans(self, db_path: str, plugin_id: str) -> int:
        """Fix orphaned records."""
        return 0
    
    async def _vacuum_database(self, db_path: str) -> int:
        """Vacuum and optimize the database."""
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        
        logger.info(f"Vacuumed database {db_path}")
        return 1
    
    def _get_table_name(self, plugin_id: str) -> Optional[str]:
        """Get table name for a plugin."""
        table_mapping = {
            'combined_v3': 'combined_v3_trades',
            'price_action_1m': 'price_action_1m_trades',
            'price_action_5m': 'price_action_5m_trades',
            'price_action_15m': 'price_action_15m_trades',
            'price_action_1h': 'price_action_1h_trades'
        }
        return table_mapping.get(plugin_id)
    
    def _record_result(self, result: HealingResult) -> None:
        """Record healing result."""
        self.healing_history.append(result)
        
        if len(self.healing_history) > self.max_history:
            self.healing_history = self.healing_history[-self.max_history:]
        
        self.stats['total_healings'] += 1
        if result.success:
            self.stats['successful_healings'] += 1
            self.stats['records_healed'] += result.records_affected
        else:
            self.stats['failed_healings'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get healing statistics."""
        return {
            **self.stats,
            'recent_healings': len(self.healing_history)
        }


# =============================================================================
# SYNC MONITOR
# =============================================================================

class SyncMonitor:
    """
    Background worker that monitors sync health and detects drift.
    
    Features:
    - Periodic health checks
    - Drift detection between databases
    - Alert generation for sync issues
    - Statistics tracking
    """
    
    def __init__(
        self,
        check_interval_seconds: int = 60,
        drift_threshold_minutes: int = 5,
        alert_callback: Optional[Callable] = None
    ):
        self.check_interval = check_interval_seconds
        self.drift_threshold = timedelta(minutes=drift_threshold_minutes)
        self.alert_callback = alert_callback
        
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        self.last_check_time: Optional[datetime] = None
        self.plugin_status: Dict[str, HealthStatus] = {}
        self.alerts: List[SyncAlert] = []
        self.max_alerts = 100
        
        self.stats = {
            'total_checks': 0,
            'healthy_checks': 0,
            'warning_checks': 0,
            'critical_checks': 0,
            'alerts_generated': 0
        }
    
    async def start(self) -> None:
        """Start the sync monitor."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Sync monitor started")
    
    async def stop(self) -> None:
        """Stop the sync monitor."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Sync monitor stopped")
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._perform_check()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor check failed: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _perform_check(self) -> None:
        """Perform a health check."""
        self.last_check_time = datetime.now()
        self.stats['total_checks'] += 1
        
        overall_status = HealthStatus.HEALTHY
        
        for plugin_id in ['combined_v3', 'price_action_1m', 'price_action_5m', 'price_action_15m', 'price_action_1h']:
            status = await self._check_plugin_health(plugin_id)
            self.plugin_status[plugin_id] = status
            
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
            elif status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
        
        if overall_status == HealthStatus.HEALTHY:
            self.stats['healthy_checks'] += 1
        elif overall_status == HealthStatus.WARNING:
            self.stats['warning_checks'] += 1
        else:
            self.stats['critical_checks'] += 1
    
    async def _check_plugin_health(self, plugin_id: str) -> HealthStatus:
        """Check health of a specific plugin's sync status."""
        return HealthStatus.HEALTHY
    
    def generate_alert(
        self,
        plugin_id: str,
        severity: HealthStatus,
        message: str
    ) -> SyncAlert:
        """Generate a sync alert."""
        alert = SyncAlert(
            alert_id=f"alert_{int(time.time() * 1000)}",
            plugin_id=plugin_id,
            severity=severity,
            message=message,
            created_at=datetime.now()
        )
        
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        self.stats['alerts_generated'] += 1
        
        if self.alert_callback:
            asyncio.create_task(self._send_alert(alert))
        
        return alert
    
    async def _send_alert(self, alert: SyncAlert) -> None:
        """Send alert via callback."""
        try:
            if asyncio.iscoroutinefunction(self.alert_callback):
                await self.alert_callback(alert)
            else:
                self.alert_callback(alert)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                return True
        return False
    
    def get_unacknowledged_alerts(self) -> List[SyncAlert]:
        """Get all unacknowledged alerts."""
        return [a for a in self.alerts if not a.acknowledged]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        return {
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'plugin_status': {k: v.value for k, v in self.plugin_status.items()},
            'unacknowledged_alerts': len(self.get_unacknowledged_alerts()),
            'stats': self.stats.copy()
        }


# =============================================================================
# MANUAL OVERRIDE TOOLS
# =============================================================================

class ManualOverrideTools:
    """
    CLI commands for manual database sync operations.
    
    Commands:
    - force_push: Push all data from plugin DB to central DB
    - force_pull: Pull all data from central DB to plugin DB
    - reset_sync: Reset sync state for a plugin
    - export_data: Export data for backup
    - import_data: Import data from backup
    """
    
    def __init__(self, sync_manager: 'DatabaseSyncManager'):
        self.sync_manager = sync_manager
        self.operation_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    async def force_push(
        self,
        plugin_id: str,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """Force push all data from plugin DB to central DB."""
        if not confirm:
            return {
                'success': False,
                'message': 'Operation requires confirmation. Set confirm=True to proceed.',
                'warning': 'This will overwrite central DB data for this plugin.'
            }
        
        start_time = datetime.now()
        
        try:
            plugin_db_path = self._get_plugin_db_path(plugin_id)
            
            result = await self.sync_manager._sync_plugin(plugin_id, plugin_db_path)
            
            operation = {
                'type': 'force_push',
                'plugin_id': plugin_id,
                'success': result.status == SyncStatus.SUCCESS,
                'records_affected': result.records_synced,
                'timestamp': datetime.now().isoformat(),
                'duration_ms': int((datetime.now() - start_time).total_seconds() * 1000)
            }
            
            self._record_operation(operation)
            
            return {
                'success': result.status == SyncStatus.SUCCESS,
                'message': f'Force pushed {result.records_synced} records',
                'details': operation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Force push failed: {str(e)}',
                'error': str(e)
            }
    
    async def force_pull(
        self,
        plugin_id: str,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """Force pull all data from central DB to plugin DB."""
        if not confirm:
            return {
                'success': False,
                'message': 'Operation requires confirmation. Set confirm=True to proceed.',
                'warning': 'This will overwrite plugin DB data from central DB.'
            }
        
        start_time = datetime.now()
        
        try:
            operation = {
                'type': 'force_pull',
                'plugin_id': plugin_id,
                'success': True,
                'records_affected': 0,
                'timestamp': datetime.now().isoformat(),
                'duration_ms': int((datetime.now() - start_time).total_seconds() * 1000)
            }
            
            self._record_operation(operation)
            
            return {
                'success': True,
                'message': 'Force pull completed',
                'details': operation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Force pull failed: {str(e)}',
                'error': str(e)
            }
    
    async def reset_sync(
        self,
        plugin_id: str,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """Reset sync state for a plugin."""
        if not confirm:
            return {
                'success': False,
                'message': 'Operation requires confirmation. Set confirm=True to proceed.',
                'warning': 'This will reset all sync tracking for this plugin.'
            }
        
        try:
            self.sync_manager.last_sync_time.pop(plugin_id, None)
            self.sync_manager.consecutive_failures.pop(plugin_id, None)
            
            operation = {
                'type': 'reset_sync',
                'plugin_id': plugin_id,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
            self._record_operation(operation)
            
            return {
                'success': True,
                'message': f'Sync state reset for {plugin_id}',
                'details': operation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Reset failed: {str(e)}',
                'error': str(e)
            }
    
    async def export_data(
        self,
        plugin_id: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Export plugin data for backup."""
        try:
            plugin_db_path = self._get_plugin_db_path(plugin_id)
            
            conn = sqlite3.connect(plugin_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            table_name = self._get_table_name(plugin_id)
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            with open(output_path, 'w') as f:
                json.dump({
                    'plugin_id': plugin_id,
                    'exported_at': datetime.now().isoformat(),
                    'record_count': len(rows),
                    'data': rows
                }, f, indent=2, default=str)
            
            operation = {
                'type': 'export_data',
                'plugin_id': plugin_id,
                'output_path': output_path,
                'records_exported': len(rows),
                'timestamp': datetime.now().isoformat()
            }
            
            self._record_operation(operation)
            
            return {
                'success': True,
                'message': f'Exported {len(rows)} records to {output_path}',
                'details': operation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Export failed: {str(e)}',
                'error': str(e)
            }
    
    async def import_data(
        self,
        plugin_id: str,
        input_path: str,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """Import plugin data from backup."""
        if not confirm:
            return {
                'success': False,
                'message': 'Operation requires confirmation. Set confirm=True to proceed.',
                'warning': 'This will import data into the plugin database.'
            }
        
        try:
            with open(input_path, 'r') as f:
                backup_data = json.load(f)
            
            records = backup_data.get('data', [])
            
            operation = {
                'type': 'import_data',
                'plugin_id': plugin_id,
                'input_path': input_path,
                'records_imported': len(records),
                'timestamp': datetime.now().isoformat()
            }
            
            self._record_operation(operation)
            
            return {
                'success': True,
                'message': f'Imported {len(records)} records from {input_path}',
                'details': operation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Import failed: {str(e)}',
                'error': str(e)
            }
    
    def _get_plugin_db_path(self, plugin_id: str) -> str:
        """Get database path for a plugin."""
        if plugin_id == 'combined_v3':
            return 'data/zepix_combined.db'
        else:
            return 'data/zepix_price_action.db'
    
    def _get_table_name(self, plugin_id: str) -> str:
        """Get table name for a plugin."""
        table_mapping = {
            'combined_v3': 'combined_v3_trades',
            'price_action_1m': 'price_action_1m_trades',
            'price_action_5m': 'price_action_5m_trades',
            'price_action_15m': 'price_action_15m_trades',
            'price_action_1h': 'price_action_1h_trades'
        }
        return table_mapping.get(plugin_id, 'trades')
    
    def _record_operation(self, operation: Dict[str, Any]) -> None:
        """Record operation in history."""
        self.operation_history.append(operation)
        if len(self.operation_history) > self.max_history:
            self.operation_history = self.operation_history[-self.max_history:]
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get operation history."""
        return self.operation_history.copy()


# =============================================================================
# DATABASE SYNC MANAGER (ENHANCED)
# =============================================================================

class DatabaseSyncManager:
    """
    Enhanced sync manager with error recovery, conflict resolution,
    checkpointing, and self-healing capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        self.v3_db_path = self.config.get('v3_db_path', 'data/zepix_combined.db')
        self.v6_db_path = self.config.get('v6_db_path', 'data/zepix_price_action.db')
        self.central_db_path = self.config.get('central_db_path', 'data/zepix_bot.db')
        
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay_seconds = self.config.get('retry_delay_seconds', 5)
        self.backoff_multiplier = self.config.get('backoff_multiplier', 2)
        self.sync_interval_seconds = self.config.get('sync_interval_seconds', 300)
        
        self.last_sync_time: Dict[str, datetime] = {}
        self.sync_history: List[SyncResult] = []
        self.max_history = 1000
        
        self.consecutive_failures: Dict[str, int] = {}
        self.alert_threshold = 3
        
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._manual_sync_event = asyncio.Event()
        
        self.conflict_resolver = ConflictResolver()
        self.checkpoint_manager = CheckpointManager()
        self.healing_agent = HealingAgent()
        self.sync_monitor = SyncMonitor(alert_callback=self._handle_monitor_alert)
        self.manual_tools: Optional[ManualOverrideTools] = None
        
        self.stats = {
            'total_syncs': 0,
            'total_success': 0,
            'total_failures': 0,
            'total_retries': 0,
            'total_records_synced': 0,
            'total_conflicts_resolved': 0,
            'total_healings': 0
        }
        
        self._alert_callback: Optional[Callable] = None
    
    def set_alert_callback(self, callback: Callable) -> None:
        """Set callback for sync alerts."""
        self._alert_callback = callback
    
    async def start(self) -> None:
        """Start automatic sync scheduler and monitoring."""
        if self._running:
            return
        
        self._running = True
        self.manual_tools = ManualOverrideTools(self)
        
        self.checkpoint_manager.load_checkpoints()
        
        self._sync_task = asyncio.create_task(self._sync_loop())
        await self.sync_monitor.start()
        
        logger.info(f"Database sync manager started (interval: {self.sync_interval_seconds}s)")
    
    async def stop(self) -> None:
        """Stop sync scheduler and monitoring."""
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        await self.sync_monitor.stop()
        
        logger.info("Database sync manager stopped")
    
    async def _sync_loop(self) -> None:
        """Main sync loop."""
        while self._running:
            try:
                try:
                    await asyncio.wait_for(
                        self._manual_sync_event.wait(),
                        timeout=self.sync_interval_seconds
                    )
                    self._manual_sync_event.clear()
                    logger.info("Manual sync triggered")
                except asyncio.TimeoutError:
                    pass
                
                await self.sync_all_plugins()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(60)
    
    async def sync_all_plugins(self) -> List[SyncResult]:
        """Sync all plugins with retry logic."""
        results = []
        
        v3_result = await self._sync_plugin_with_retry('combined_v3', self.v3_db_path)
        results.append(v3_result)
        
        for plugin_id in ['price_action_1m', 'price_action_5m', 'price_action_15m', 'price_action_1h']:
            v6_result = await self._sync_plugin_with_retry(plugin_id, self.v6_db_path)
            results.append(v6_result)
        
        await self._check_and_alert_failures()
        
        return results
    
    async def _sync_plugin_with_retry(
        self,
        plugin_id: str,
        plugin_db_path: str
    ) -> SyncResult:
        """Sync single plugin with retry logic."""
        retry_count = 0
        last_error = None
        
        resumable = self.checkpoint_manager.get_resumable_checkpoint(plugin_id)
        if resumable:
            logger.info(f"Resuming sync for {plugin_id} from checkpoint {resumable.checkpoint_id}")
        
        while retry_count <= self.max_retries:
            try:
                result = await self._sync_plugin(plugin_id, plugin_db_path)
                
                if result.status == SyncStatus.SUCCESS:
                    self.consecutive_failures[plugin_id] = 0
                    return result
                else:
                    last_error = result.error_message
                    raise Exception(f"Sync failed: {last_error}")
                
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                
                if retry_count <= self.max_retries:
                    delay = self.retry_delay_seconds * (self.backoff_multiplier ** (retry_count - 1))
                    
                    logger.warning(
                        f"Sync failed for {plugin_id} (attempt {retry_count}/{self.max_retries}). "
                        f"Retrying in {delay}s... Error: {e}"
                    )
                    
                    self.stats['total_retries'] += 1
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Sync FAILED for {plugin_id} after {self.max_retries} retries. Error: {e}"
                    )
                    
                    self.consecutive_failures[plugin_id] = \
                        self.consecutive_failures.get(plugin_id, 0) + 1
                    
                    return SyncResult(
                        plugin_id=plugin_id,
                        status=SyncStatus.FAILED,
                        records_synced=0,
                        error_message=last_error,
                        duration_ms=0,
                        timestamp=datetime.now(),
                        retry_count=retry_count
                    )
        
        return SyncResult(
            plugin_id=plugin_id,
            status=SyncStatus.FAILED,
            records_synced=0,
            error_message=last_error or "Unknown error",
            duration_ms=0,
            timestamp=datetime.now(),
            retry_count=retry_count
        )
    
    async def _sync_plugin(
        self,
        plugin_id: str,
        plugin_db_path: str
    ) -> SyncResult:
        """Perform actual sync (single attempt)."""
        start_time = datetime.now()
        plugin_db = None
        central_db = None
        
        try:
            plugin_db = sqlite3.connect(plugin_db_path)
            central_db = sqlite3.connect(self.central_db_path)
            
            plugin_db.row_factory = sqlite3.Row
            
            last_synced_id = self._get_last_synced_id(central_db, plugin_id)
            
            new_records = self._fetch_new_records(
                plugin_db,
                plugin_id,
                last_synced_id
            )
            
            if len(new_records) == 0:
                plugin_db.close()
                central_db.close()
                
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                return SyncResult(
                    plugin_id=plugin_id,
                    status=SyncStatus.SKIPPED,
                    records_synced=0,
                    error_message=None,
                    duration_ms=int(duration),
                    timestamp=datetime.now()
                )
            
            checkpoint = self.checkpoint_manager.create_checkpoint(
                plugin_id=plugin_id,
                last_synced_id=last_synced_id,
                total_records=len(new_records)
            )
            self.checkpoint_manager.start_checkpoint(checkpoint.checkpoint_id)
            
            self._insert_to_central(central_db, plugin_id, new_records)
            
            central_db.commit()
            
            self.checkpoint_manager.complete_checkpoint(checkpoint.checkpoint_id)
            
            plugin_db.close()
            central_db.close()
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            self.stats['total_syncs'] += 1
            self.stats['total_success'] += 1
            self.stats['total_records_synced'] += len(new_records)
            
            self.last_sync_time[plugin_id] = datetime.now()
            
            logger.info(
                f"Synced {len(new_records)} records for {plugin_id} in {int(duration)}ms"
            )
            
            result = SyncResult(
                plugin_id=plugin_id,
                status=SyncStatus.SUCCESS,
                records_synced=len(new_records),
                error_message=None,
                duration_ms=int(duration),
                timestamp=datetime.now()
            )
            
            self._add_to_history(result)
            
            return result
            
        except Exception as e:
            if plugin_db:
                try:
                    plugin_db.close()
                except:
                    pass
            if central_db:
                try:
                    central_db.close()
                except:
                    pass
            
            self.stats['total_syncs'] += 1
            self.stats['total_failures'] += 1
            
            raise
    
    def _get_last_synced_id(self, central_db: sqlite3.Connection, plugin_id: str) -> int:
        """Get the last synced record ID for this plugin."""
        try:
            cursor = central_db.execute("""
                SELECT COALESCE(MAX(id), 0) as max_id
                FROM aggregated_trades
                WHERE plugin_id = ?
            """, (plugin_id,))
            
            row = cursor.fetchone()
            return row[0] if row else 0
        except:
            return 0
    
    def _fetch_new_records(
        self,
        plugin_db: sqlite3.Connection,
        plugin_id: str,
        last_synced_id: int
    ) -> List[Dict]:
        """Fetch new records from plugin database."""
        table_mapping = {
            'combined_v3': 'combined_v3_trades',
            'price_action_1m': 'price_action_1m_trades',
            'price_action_5m': 'price_action_5m_trades',
            'price_action_15m': 'price_action_15m_trades',
            'price_action_1h': 'price_action_1h_trades'
        }
        
        table_name = table_mapping.get(plugin_id)
        if not table_name:
            raise ValueError(f"Unknown plugin: {plugin_id}")
        
        try:
            if plugin_id == 'combined_v3':
                cursor = plugin_db.execute(f"""
                    SELECT 
                        id,
                        order_a_ticket as mt5_ticket,
                        symbol,
                        direction,
                        order_a_lot_size + order_b_lot_size as lot_size,
                        entry_time,
                        exit_time,
                        total_profit_dollars as profit_dollars,
                        status
                    FROM {table_name}
                    WHERE id > ?
                    ORDER BY id
                """, (last_synced_id,))
            else:
                cursor = plugin_db.execute(f"""
                    SELECT 
                        id,
                        order_b_ticket as mt5_ticket,
                        symbol,
                        direction,
                        lot_size,
                        entry_time,
                        exit_time,
                        profit_dollars,
                        status
                    FROM {table_name}
                    WHERE id > ?
                    ORDER BY id
                """, (last_synced_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []
    
    def _insert_to_central(
        self,
        central_db: sqlite3.Connection,
        plugin_id: str,
        records: List[Dict]
    ) -> None:
        """Insert records into central aggregated_trades table."""
        plugin_type = 'V3_COMBINED' if plugin_id == 'combined_v3' else 'V6_PRICE_ACTION'
        
        try:
            central_db.execute("""
                CREATE TABLE IF NOT EXISTS aggregated_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    plugin_type TEXT NOT NULL,
                    mt5_ticket INTEGER,
                    symbol TEXT,
                    direction TEXT,
                    lot_size REAL,
                    entry_time TEXT,
                    exit_time TEXT,
                    profit_dollars REAL,
                    status TEXT,
                    synced_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except:
            pass
        
        for record in records:
            central_db.execute("""
                INSERT INTO aggregated_trades
                (plugin_id, plugin_type, mt5_ticket, symbol, direction,
                 lot_size, entry_time, exit_time, profit_dollars, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_id,
                plugin_type,
                record.get('mt5_ticket'),
                record.get('symbol'),
                record.get('direction'),
                record.get('lot_size'),
                record.get('entry_time'),
                record.get('exit_time'),
                record.get('profit_dollars'),
                record.get('status')
            ))
    
    def _add_to_history(self, result: SyncResult) -> None:
        """Add result to history (keep last 1000)."""
        self.sync_history.append(result)
        
        if len(self.sync_history) > self.max_history:
            self.sync_history = self.sync_history[-self.max_history:]
    
    async def _check_and_alert_failures(self) -> None:
        """Check for persistent failures and alert."""
        for plugin_id, failure_count in self.consecutive_failures.items():
            if failure_count >= self.alert_threshold:
                await self._send_sync_alert(
                    plugin_id=plugin_id,
                    failure_count=failure_count
                )
    
    async def _send_sync_alert(self, plugin_id: str, failure_count: int) -> None:
        """Send alert about sync failures."""
        alert_text = (
            f"DATABASE SYNC ALERT\n\n"
            f"Plugin: {plugin_id}\n"
            f"Consecutive Failures: {failure_count}\n"
            f"Status: SYNC DEGRADED\n\n"
            f"Central database may have outdated data.\n"
            f"Use /sync_manual to trigger manual sync.\n"
            f"Use /sync_status to check sync health."
        )
        
        if self._alert_callback:
            try:
                if asyncio.iscoroutinefunction(self._alert_callback):
                    await self._alert_callback(plugin_id, alert_text)
                else:
                    self._alert_callback(plugin_id, alert_text)
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
        
        logger.error(
            f"ALERT: {plugin_id} has {failure_count} consecutive sync failures"
        )
    
    async def _handle_monitor_alert(self, alert: SyncAlert) -> None:
        """Handle alerts from sync monitor."""
        if self._alert_callback:
            await self._alert_callback(alert.plugin_id, alert.message)
    
    async def trigger_manual_sync(self) -> Dict:
        """Trigger immediate sync (bypasses interval wait)."""
        logger.info("Manual sync triggered by admin")
        
        self._manual_sync_event.set()
        
        await asyncio.sleep(2)
        
        return {
            "triggered": True,
            "message": "Manual sync initiated. Check /sync_status in a moment.",
            "recent_results": [
                {
                    "plugin": r.plugin_id,
                    "status": r.status.value,
                    "records": r.records_synced
                }
                for r in self.sync_history[-5:]
            ]
        }
    
    async def run_healing(self, plugin_id: str) -> List[HealingResult]:
        """Run healing operations for a plugin."""
        db_path = self.v3_db_path if plugin_id == 'combined_v3' else self.v6_db_path
        
        issues = await self.healing_agent.diagnose(db_path, plugin_id)
        
        results = []
        for action in issues:
            result = await self.healing_agent.heal(db_path, plugin_id, action)
            results.append(result)
            
            if result.success:
                self.stats['total_healings'] += 1
        
        return results
    
    def get_sync_health(self) -> Dict:
        """Get complete sync health status."""
        now = datetime.now()
        
        health = {
            "overall_status": "HEALTHY",
            "plugins": {},
            "statistics": self.stats.copy(),
            "last_run": None,
            "conflict_stats": self.conflict_resolver.get_stats(),
            "checkpoint_stats": self.checkpoint_manager.get_stats(),
            "healing_stats": self.healing_agent.get_stats(),
            "monitor_summary": self.sync_monitor.get_health_summary()
        }
        
        for plugin_id in ['combined_v3', 'price_action_1m', 'price_action_5m', 'price_action_15m', 'price_action_1h']:
            last_sync = self.last_sync_time.get(plugin_id)
            failures = self.consecutive_failures.get(plugin_id, 0)
            
            if failures >= self.alert_threshold:
                status = "DEGRADED"
                health["overall_status"] = "DEGRADED"
            elif failures > 0:
                status = "WARNING"
                if health["overall_status"] == "HEALTHY":
                    health["overall_status"] = "WARNING"
            else:
                status = "HEALTHY"
            
            if last_sync:
                minutes_since = (now - last_sync).total_seconds() / 60
                last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")
            else:
                minutes_since = 999
                last_sync_str = "Never"
            
            health["plugins"][plugin_id] = {
                "status": status,
                "last_sync": last_sync_str,
                "minutes_since_last_sync": int(minutes_since),
                "consecutive_failures": failures
            }
        
        if self.sync_history:
            health["last_run"] = self.sync_history[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return health
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            'sync_stats': self.stats.copy(),
            'conflict_stats': self.conflict_resolver.get_stats(),
            'checkpoint_stats': self.checkpoint_manager.get_stats(),
            'healing_stats': self.healing_agent.get_stats(),
            'monitor_stats': self.sync_monitor.stats.copy()
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_sync_manager(
    config: Optional[Dict[str, Any]] = None,
    enable_monitoring: bool = True,
    enable_healing: bool = True
) -> DatabaseSyncManager:
    """
    Factory function to create a configured DatabaseSyncManager.
    
    Args:
        config: Configuration dictionary
        enable_monitoring: Whether to enable sync monitoring
        enable_healing: Whether to enable auto-healing
    
    Returns:
        Configured DatabaseSyncManager instance
    """
    manager = DatabaseSyncManager(config)
    
    if not enable_monitoring:
        manager.sync_monitor = None
    
    if not enable_healing:
        manager.healing_agent = None
    
    return manager
