"""
Plugin Health Monitoring System
Document 25: 25_PLUGIN_HEALTH_MONITORING_SYSTEM.md

Monitors the health and performance of all V3 and V6 plugins in real-time,
detects anomalies, and alerts operators before issues escalate.

Health Dimensions:
1. Availability: Plugin running and responsive
2. Performance: Execution times within SLA
3. Accuracy: Signal quality and trade success rates
4. Resource Usage: Memory, CPU, database connections
5. Error Rate: Exceptions, failed operations

Components:
- PluginHealthMonitor: Central health monitoring system
- HeartbeatMonitor: Track if plugins are alive and responding
- ResourceWatchdog: Monitor Memory/CPU usage per plugin
- ErrorRateTracker: Count exceptions per plugin window
- CircuitBreaker: Auto-disable plugin if it breaches error thresholds
- HealthReportGenerator: Generate status JSON for dashboard/Telegram
- DependencyChecker: Verify plugin dependencies are reachable
"""

import asyncio
import logging
import time
import os
import sqlite3
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable, Set, Deque
from enum import Enum
from pathlib import Path
from collections import deque

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class HealthStatus(Enum):
    """Plugin health status levels"""
    HEALTHY = "HEALTHY"
    STALE = "STALE"
    HUNG = "HUNG"
    DEAD = "DEAD"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Tripped, blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class DependencyType(Enum):
    """Types of plugin dependencies"""
    DATABASE = "DATABASE"
    API = "API"
    FILE = "FILE"
    SERVICE = "SERVICE"
    NETWORK = "NETWORK"


# ============================================================================
# DATA CLASSES - Health Metrics
# ============================================================================

@dataclass
class PluginAvailabilityMetrics:
    """Plugin availability metrics"""
    plugin_id: str
    is_running: bool = False
    is_responsive: bool = False
    last_heartbeat: datetime = field(default_factory=datetime.now)
    uptime_seconds: int = 0
    
    @property
    def health_status(self) -> HealthStatus:
        """Calculate health status from metrics"""
        if not self.is_running:
            return HealthStatus.DEAD
        if not self.is_responsive:
            return HealthStatus.HUNG
        if (datetime.now() - self.last_heartbeat).seconds > 300:
            return HealthStatus.STALE
        return HealthStatus.HEALTHY


@dataclass
class PluginPerformanceMetrics:
    """Plugin performance metrics"""
    plugin_id: str
    avg_execution_time_ms: float = 0.0
    p95_execution_time_ms: float = 0.0
    p99_execution_time_ms: float = 0.0
    signals_processed_1h: int = 0
    orders_placed_1h: int = 0
    signal_accuracy_pct: float = 0.0
    win_rate_pct: float = 0.0


@dataclass
class PluginResourceMetrics:
    """Plugin resource usage metrics"""
    plugin_id: str
    memory_usage_mb: float = 0.0
    memory_limit_mb: float = 1024.0
    cpu_usage_pct: float = 0.0
    db_connections_active: int = 0
    db_connections_max: int = 10
    db_query_time_avg_ms: float = 0.0
    open_file_handles: int = 0


@dataclass
class PluginErrorMetrics:
    """Plugin error metrics"""
    plugin_id: str
    total_errors: int = 0
    critical_errors: int = 0
    warnings: int = 0
    error_rate_pct: float = 0.0
    last_error_message: str = ""
    last_error_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HealthSnapshot:
    """Complete health snapshot for a plugin"""
    plugin_id: str
    timestamp: datetime
    availability: PluginAvailabilityMetrics
    performance: PluginPerformanceMetrics
    resources: PluginResourceMetrics
    errors: PluginErrorMetrics
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "plugin_id": self.plugin_id,
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status.value,
            "availability": {
                "is_running": self.availability.is_running,
                "is_responsive": self.availability.is_responsive,
                "last_heartbeat": self.availability.last_heartbeat.isoformat(),
                "uptime_seconds": self.availability.uptime_seconds,
                "health_status": self.availability.health_status.value
            },
            "performance": {
                "avg_execution_time_ms": self.performance.avg_execution_time_ms,
                "p95_execution_time_ms": self.performance.p95_execution_time_ms,
                "p99_execution_time_ms": self.performance.p99_execution_time_ms,
                "signals_processed_1h": self.performance.signals_processed_1h,
                "orders_placed_1h": self.performance.orders_placed_1h,
                "signal_accuracy_pct": self.performance.signal_accuracy_pct,
                "win_rate_pct": self.performance.win_rate_pct
            },
            "resources": {
                "memory_usage_mb": self.resources.memory_usage_mb,
                "memory_limit_mb": self.resources.memory_limit_mb,
                "cpu_usage_pct": self.resources.cpu_usage_pct,
                "db_connections_active": self.resources.db_connections_active,
                "db_connections_max": self.resources.db_connections_max,
                "db_query_time_avg_ms": self.resources.db_query_time_avg_ms,
                "open_file_handles": self.resources.open_file_handles
            },
            "errors": {
                "total_errors": self.errors.total_errors,
                "critical_errors": self.errors.critical_errors,
                "warnings": self.errors.warnings,
                "error_rate_pct": self.errors.error_rate_pct,
                "last_error_message": self.errors.last_error_message,
                "last_error_timestamp": self.errors.last_error_timestamp.isoformat()
            }
        }


@dataclass
class HealthAlert:
    """Health alert record"""
    id: int = 0
    plugin_id: str = ""
    alert_level: AlertLevel = AlertLevel.INFO
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "plugin_id": self.plugin_id,
            "alert_level": self.alert_level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class DependencyStatus:
    """Status of a plugin dependency"""
    name: str
    dependency_type: DependencyType
    is_available: bool = False
    response_time_ms: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)
    error_message: str = ""


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for a plugin"""
    plugin_id: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.now)
    cooldown_until: Optional[datetime] = None


@dataclass
class HealthThresholds:
    """Configurable health thresholds"""
    max_execution_time_ms: float = 5000.0
    max_error_rate_pct: float = 5.0
    max_memory_usage_mb: float = 500.0
    max_cpu_usage_pct: float = 80.0
    min_heartbeat_interval_sec: int = 300
    circuit_breaker_threshold: int = 5
    circuit_breaker_cooldown_sec: int = 60
    stale_threshold_sec: int = 300


# ============================================================================
# HEARTBEAT MONITOR
# ============================================================================

class HeartbeatMonitor:
    """
    Tracks if plugins are alive and responding.
    Records last heartbeat time and detects stale/dead plugins.
    """
    
    def __init__(self):
        self._heartbeats: Dict[str, datetime] = {}
        self._start_times: Dict[str, datetime] = {}
        self._responsive: Dict[str, bool] = {}
        self._running: Dict[str, bool] = {}
        self._lock = asyncio.Lock()
    
    async def register_plugin(self, plugin_id: str) -> None:
        """Register a new plugin for heartbeat monitoring"""
        async with self._lock:
            now = datetime.now()
            self._heartbeats[plugin_id] = now
            self._start_times[plugin_id] = now
            self._responsive[plugin_id] = True
            self._running[plugin_id] = True
            logger.info(f"Registered plugin {plugin_id} for heartbeat monitoring")
    
    async def unregister_plugin(self, plugin_id: str) -> None:
        """Unregister a plugin from heartbeat monitoring"""
        async with self._lock:
            self._heartbeats.pop(plugin_id, None)
            self._start_times.pop(plugin_id, None)
            self._responsive.pop(plugin_id, None)
            self._running.pop(plugin_id, None)
            logger.info(f"Unregistered plugin {plugin_id} from heartbeat monitoring")
    
    async def record_heartbeat(self, plugin_id: str) -> None:
        """Record a heartbeat from a plugin"""
        async with self._lock:
            self._heartbeats[plugin_id] = datetime.now()
            self._responsive[plugin_id] = True
            self._running[plugin_id] = True
    
    async def mark_unresponsive(self, plugin_id: str) -> None:
        """Mark a plugin as unresponsive"""
        async with self._lock:
            self._responsive[plugin_id] = False
    
    async def mark_stopped(self, plugin_id: str) -> None:
        """Mark a plugin as stopped"""
        async with self._lock:
            self._running[plugin_id] = False
            self._responsive[plugin_id] = False
    
    async def get_availability_metrics(self, plugin_id: str) -> PluginAvailabilityMetrics:
        """Get availability metrics for a plugin"""
        async with self._lock:
            if plugin_id not in self._heartbeats:
                return PluginAvailabilityMetrics(
                    plugin_id=plugin_id,
                    is_running=False,
                    is_responsive=False,
                    last_heartbeat=datetime.min,
                    uptime_seconds=0
                )
            
            last_heartbeat = self._heartbeats.get(plugin_id, datetime.min)
            start_time = self._start_times.get(plugin_id, datetime.now())
            is_running = self._running.get(plugin_id, False)
            is_responsive = self._responsive.get(plugin_id, False)
            uptime = int((datetime.now() - start_time).total_seconds()) if is_running else 0
            
            return PluginAvailabilityMetrics(
                plugin_id=plugin_id,
                is_running=is_running,
                is_responsive=is_responsive,
                last_heartbeat=last_heartbeat,
                uptime_seconds=uptime
            )
    
    async def get_all_plugin_ids(self) -> List[str]:
        """Get all registered plugin IDs"""
        async with self._lock:
            return list(self._heartbeats.keys())
    
    async def check_stale_plugins(self, threshold_sec: int = 300) -> List[str]:
        """Check for plugins with stale heartbeats"""
        async with self._lock:
            stale_plugins = []
            now = datetime.now()
            for plugin_id, last_heartbeat in self._heartbeats.items():
                if (now - last_heartbeat).total_seconds() > threshold_sec:
                    stale_plugins.append(plugin_id)
            return stale_plugins


# ============================================================================
# RESOURCE WATCHDOG
# ============================================================================

class ResourceWatchdog:
    """
    Monitors Memory/CPU usage per plugin.
    Uses process-level metrics when available.
    """
    
    def __init__(self):
        self._resource_snapshots: Dict[str, PluginResourceMetrics] = {}
        self._process_ids: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        self._psutil_available = False
        
        try:
            import psutil
            self._psutil_available = True
        except ImportError:
            logger.warning("psutil not available, resource monitoring will be limited")
    
    async def register_plugin(self, plugin_id: str, process_id: Optional[int] = None) -> None:
        """Register a plugin for resource monitoring"""
        async with self._lock:
            if process_id:
                self._process_ids[plugin_id] = process_id
            self._resource_snapshots[plugin_id] = PluginResourceMetrics(plugin_id=plugin_id)
    
    async def unregister_plugin(self, plugin_id: str) -> None:
        """Unregister a plugin from resource monitoring"""
        async with self._lock:
            self._process_ids.pop(plugin_id, None)
            self._resource_snapshots.pop(plugin_id, None)
    
    async def collect_metrics(self, plugin_id: str) -> PluginResourceMetrics:
        """Collect resource metrics for a plugin"""
        async with self._lock:
            metrics = PluginResourceMetrics(plugin_id=plugin_id)
            
            if self._psutil_available and plugin_id in self._process_ids:
                try:
                    import psutil
                    process = psutil.Process(self._process_ids[plugin_id])
                    
                    memory_info = process.memory_info()
                    metrics.memory_usage_mb = memory_info.rss / (1024 * 1024)
                    metrics.cpu_usage_pct = process.cpu_percent(interval=0.1)
                    metrics.open_file_handles = len(process.open_files())
                    
                except Exception as e:
                    logger.warning(f"Failed to collect process metrics for {plugin_id}: {e}")
            
            # Use current process as fallback
            if not self._psutil_available or plugin_id not in self._process_ids:
                try:
                    import psutil
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    metrics.memory_usage_mb = memory_info.rss / (1024 * 1024)
                    metrics.cpu_usage_pct = process.cpu_percent(interval=0.1)
                except Exception:
                    pass
            
            self._resource_snapshots[plugin_id] = metrics
            return metrics
    
    async def update_db_stats(
        self,
        plugin_id: str,
        active_connections: int,
        max_connections: int,
        avg_query_time_ms: float
    ) -> None:
        """Update database connection stats for a plugin"""
        async with self._lock:
            if plugin_id in self._resource_snapshots:
                self._resource_snapshots[plugin_id].db_connections_active = active_connections
                self._resource_snapshots[plugin_id].db_connections_max = max_connections
                self._resource_snapshots[plugin_id].db_query_time_avg_ms = avg_query_time_ms
    
    async def get_metrics(self, plugin_id: str) -> PluginResourceMetrics:
        """Get cached resource metrics for a plugin"""
        async with self._lock:
            return self._resource_snapshots.get(
                plugin_id,
                PluginResourceMetrics(plugin_id=plugin_id)
            )
    
    async def check_resource_thresholds(
        self,
        plugin_id: str,
        max_memory_mb: float = 500.0,
        max_cpu_pct: float = 80.0
    ) -> List[str]:
        """Check if plugin exceeds resource thresholds"""
        violations = []
        metrics = await self.get_metrics(plugin_id)
        
        if metrics.memory_usage_mb > max_memory_mb:
            violations.append(f"Memory usage {metrics.memory_usage_mb:.1f}MB exceeds {max_memory_mb}MB")
        
        if metrics.cpu_usage_pct > max_cpu_pct:
            violations.append(f"CPU usage {metrics.cpu_usage_pct:.1f}% exceeds {max_cpu_pct}%")
        
        return violations


# ============================================================================
# ERROR RATE TRACKER
# ============================================================================

class ErrorRateTracker:
    """
    Counts exceptions per plugin within a sliding window.
    Tracks error rates and recent error messages.
    """
    
    def __init__(self, window_size_sec: int = 3600):
        self._window_size = window_size_sec
        self._errors: Dict[str, Deque[tuple]] = {}  # plugin_id -> deque of (timestamp, level, message)
        self._lock = asyncio.Lock()
    
    async def register_plugin(self, plugin_id: str) -> None:
        """Register a plugin for error tracking"""
        async with self._lock:
            self._errors[plugin_id] = deque()
    
    async def unregister_plugin(self, plugin_id: str) -> None:
        """Unregister a plugin from error tracking"""
        async with self._lock:
            self._errors.pop(plugin_id, None)
    
    async def record_error(
        self,
        plugin_id: str,
        message: str,
        is_critical: bool = False,
        is_warning: bool = False
    ) -> None:
        """Record an error for a plugin"""
        async with self._lock:
            if plugin_id not in self._errors:
                self._errors[plugin_id] = deque()
            
            level = "CRITICAL" if is_critical else ("WARNING" if is_warning else "ERROR")
            self._errors[plugin_id].append((datetime.now(), level, message))
            
            # Clean old entries
            await self._cleanup_old_entries(plugin_id)
    
    async def _cleanup_old_entries(self, plugin_id: str) -> None:
        """Remove entries older than window size"""
        if plugin_id not in self._errors:
            return
        
        cutoff = datetime.now() - timedelta(seconds=self._window_size)
        while self._errors[plugin_id] and self._errors[plugin_id][0][0] < cutoff:
            self._errors[plugin_id].popleft()
    
    async def get_error_metrics(self, plugin_id: str, total_operations: int = 100) -> PluginErrorMetrics:
        """Get error metrics for a plugin"""
        async with self._lock:
            await self._cleanup_old_entries(plugin_id)
            
            if plugin_id not in self._errors or not self._errors[plugin_id]:
                return PluginErrorMetrics(plugin_id=plugin_id)
            
            errors = self._errors[plugin_id]
            total_errors = sum(1 for _, level, _ in errors if level == "ERROR")
            critical_errors = sum(1 for _, level, _ in errors if level == "CRITICAL")
            warnings = sum(1 for _, level, _ in errors if level == "WARNING")
            
            # Get last error
            last_error = errors[-1] if errors else None
            last_error_time = last_error[0] if last_error else datetime.now()
            last_error_msg = last_error[2] if last_error else ""
            
            # Calculate error rate
            error_rate = (total_errors + critical_errors) / max(total_operations, 1) * 100
            
            return PluginErrorMetrics(
                plugin_id=plugin_id,
                total_errors=total_errors,
                critical_errors=critical_errors,
                warnings=warnings,
                error_rate_pct=error_rate,
                last_error_message=last_error_msg,
                last_error_timestamp=last_error_time
            )
    
    async def get_error_count(self, plugin_id: str, window_sec: Optional[int] = None) -> int:
        """Get error count for a plugin within a window"""
        async with self._lock:
            if plugin_id not in self._errors:
                return 0
            
            window = window_sec or self._window_size
            cutoff = datetime.now() - timedelta(seconds=window)
            
            return sum(1 for ts, level, _ in self._errors[plugin_id] 
                      if ts >= cutoff and level in ("ERROR", "CRITICAL"))
    
    async def clear_errors(self, plugin_id: str) -> None:
        """Clear all errors for a plugin"""
        async with self._lock:
            if plugin_id in self._errors:
                self._errors[plugin_id].clear()


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """
    Auto-disables a plugin if it breaches error thresholds.
    Implements the circuit breaker pattern for fault tolerance.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Tripped due to failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        cooldown_sec: int = 60
    ):
        self._failure_threshold = failure_threshold
        self._success_threshold = success_threshold
        self._cooldown_sec = cooldown_sec
        self._states: Dict[str, CircuitBreakerState] = {}
        self._lock = asyncio.Lock()
        self._on_state_change: Optional[Callable] = None
    
    def set_state_change_callback(self, callback: Callable) -> None:
        """Set callback for state changes"""
        self._on_state_change = callback
    
    async def register_plugin(self, plugin_id: str) -> None:
        """Register a plugin with the circuit breaker"""
        async with self._lock:
            self._states[plugin_id] = CircuitBreakerState(plugin_id=plugin_id)
    
    async def unregister_plugin(self, plugin_id: str) -> None:
        """Unregister a plugin from the circuit breaker"""
        async with self._lock:
            self._states.pop(plugin_id, None)
    
    async def record_success(self, plugin_id: str) -> None:
        """Record a successful operation"""
        async with self._lock:
            if plugin_id not in self._states:
                return
            
            state = self._states[plugin_id]
            state.success_count += 1
            
            if state.state == CircuitState.HALF_OPEN:
                if state.success_count >= self._success_threshold:
                    await self._transition_state(plugin_id, CircuitState.CLOSED)
    
    async def record_failure(self, plugin_id: str) -> None:
        """Record a failed operation"""
        async with self._lock:
            if plugin_id not in self._states:
                return
            
            state = self._states[plugin_id]
            state.failure_count += 1
            state.last_failure_time = datetime.now()
            
            if state.state == CircuitState.CLOSED:
                if state.failure_count >= self._failure_threshold:
                    await self._transition_state(plugin_id, CircuitState.OPEN)
            
            elif state.state == CircuitState.HALF_OPEN:
                await self._transition_state(plugin_id, CircuitState.OPEN)
    
    async def _transition_state(self, plugin_id: str, new_state: CircuitState) -> None:
        """Transition to a new state"""
        state = self._states[plugin_id]
        old_state = state.state
        state.state = new_state
        state.last_state_change = datetime.now()
        
        if new_state == CircuitState.OPEN:
            state.cooldown_until = datetime.now() + timedelta(seconds=self._cooldown_sec)
            state.success_count = 0
        elif new_state == CircuitState.CLOSED:
            state.failure_count = 0
            state.success_count = 0
            state.cooldown_until = None
        elif new_state == CircuitState.HALF_OPEN:
            state.success_count = 0
        
        logger.info(f"Circuit breaker for {plugin_id}: {old_state.value} -> {new_state.value}")
        
        if self._on_state_change:
            try:
                await self._on_state_change(plugin_id, old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    async def is_allowed(self, plugin_id: str) -> bool:
        """Check if requests are allowed for a plugin"""
        async with self._lock:
            if plugin_id not in self._states:
                return True
            
            state = self._states[plugin_id]
            
            if state.state == CircuitState.CLOSED:
                return True
            
            if state.state == CircuitState.OPEN:
                # Check if cooldown has passed
                if state.cooldown_until and datetime.now() >= state.cooldown_until:
                    await self._transition_state(plugin_id, CircuitState.HALF_OPEN)
                    return True
                return False
            
            if state.state == CircuitState.HALF_OPEN:
                return True
            
            return False
    
    async def get_state(self, plugin_id: str) -> CircuitBreakerState:
        """Get circuit breaker state for a plugin"""
        async with self._lock:
            return self._states.get(
                plugin_id,
                CircuitBreakerState(plugin_id=plugin_id)
            )
    
    async def reset(self, plugin_id: str) -> None:
        """Manually reset circuit breaker for a plugin"""
        async with self._lock:
            if plugin_id in self._states:
                await self._transition_state(plugin_id, CircuitState.CLOSED)
    
    async def trip(self, plugin_id: str) -> None:
        """Manually trip circuit breaker for a plugin"""
        async with self._lock:
            if plugin_id in self._states:
                await self._transition_state(plugin_id, CircuitState.OPEN)


# ============================================================================
# DEPENDENCY CHECKER
# ============================================================================

class DependencyChecker:
    """
    Verifies plugin dependencies (DB, API) are reachable.
    Performs health checks on external dependencies.
    """
    
    def __init__(self):
        self._dependencies: Dict[str, List[DependencyStatus]] = {}
        self._lock = asyncio.Lock()
    
    async def register_dependency(
        self,
        plugin_id: str,
        name: str,
        dependency_type: DependencyType
    ) -> None:
        """Register a dependency for a plugin"""
        async with self._lock:
            if plugin_id not in self._dependencies:
                self._dependencies[plugin_id] = []
            
            self._dependencies[plugin_id].append(DependencyStatus(
                name=name,
                dependency_type=dependency_type
            ))
    
    async def check_database(self, db_path: str) -> DependencyStatus:
        """Check if a database is accessible"""
        start_time = time.time()
        status = DependencyStatus(
            name=db_path,
            dependency_type=DependencyType.DATABASE,
            last_check=datetime.now()
        )
        
        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path, timeout=5)
                conn.execute("SELECT 1")
                conn.close()
                status.is_available = True
                status.response_time_ms = (time.time() - start_time) * 1000
            else:
                status.is_available = False
                status.error_message = "Database file not found"
        except Exception as e:
            status.is_available = False
            status.error_message = str(e)
            status.response_time_ms = (time.time() - start_time) * 1000
        
        return status
    
    async def check_file(self, file_path: str) -> DependencyStatus:
        """Check if a file is accessible"""
        status = DependencyStatus(
            name=file_path,
            dependency_type=DependencyType.FILE,
            last_check=datetime.now()
        )
        
        try:
            if os.path.exists(file_path):
                status.is_available = os.access(file_path, os.R_OK)
                if not status.is_available:
                    status.error_message = "File not readable"
            else:
                status.is_available = False
                status.error_message = "File not found"
        except Exception as e:
            status.is_available = False
            status.error_message = str(e)
        
        return status
    
    async def check_api(self, url: str, timeout: float = 5.0) -> DependencyStatus:
        """Check if an API endpoint is reachable"""
        start_time = time.time()
        status = DependencyStatus(
            name=url,
            dependency_type=DependencyType.API,
            last_check=datetime.now()
        )
        
        try:
            import urllib.request
            req = urllib.request.Request(url, method='HEAD')
            urllib.request.urlopen(req, timeout=timeout)
            status.is_available = True
            status.response_time_ms = (time.time() - start_time) * 1000
        except Exception as e:
            status.is_available = False
            status.error_message = str(e)
            status.response_time_ms = (time.time() - start_time) * 1000
        
        return status
    
    async def check_all_dependencies(self, plugin_id: str) -> List[DependencyStatus]:
        """Check all dependencies for a plugin"""
        async with self._lock:
            if plugin_id not in self._dependencies:
                return []
            
            results = []
            for dep in self._dependencies[plugin_id]:
                if dep.dependency_type == DependencyType.DATABASE:
                    result = await self.check_database(dep.name)
                elif dep.dependency_type == DependencyType.FILE:
                    result = await self.check_file(dep.name)
                elif dep.dependency_type == DependencyType.API:
                    result = await self.check_api(dep.name)
                else:
                    result = dep
                results.append(result)
            
            return results
    
    async def get_dependency_status(self, plugin_id: str) -> Dict[str, bool]:
        """Get dependency status summary for a plugin"""
        deps = await self.check_all_dependencies(plugin_id)
        return {dep.name: dep.is_available for dep in deps}


# ============================================================================
# HEALTH REPORT GENERATOR
# ============================================================================

class HealthReportGenerator:
    """
    Generates status JSON for dashboard/Telegram header.
    Creates comprehensive health reports for all plugins.
    """
    
    def __init__(self):
        self._snapshots: Dict[str, HealthSnapshot] = {}
        self._alerts: List[HealthAlert] = []
        self._lock = asyncio.Lock()
    
    async def store_snapshot(self, snapshot: HealthSnapshot) -> None:
        """Store a health snapshot"""
        async with self._lock:
            self._snapshots[snapshot.plugin_id] = snapshot
    
    async def store_alert(self, alert: HealthAlert) -> None:
        """Store a health alert"""
        async with self._lock:
            self._alerts.append(alert)
            # Keep only last 100 alerts
            if len(self._alerts) > 100:
                self._alerts = self._alerts[-100:]
    
    async def get_latest_snapshots(self) -> List[HealthSnapshot]:
        """Get latest health snapshots for all plugins"""
        async with self._lock:
            return list(self._snapshots.values())
    
    async def get_snapshot(self, plugin_id: str) -> Optional[HealthSnapshot]:
        """Get latest snapshot for a specific plugin"""
        async with self._lock:
            return self._snapshots.get(plugin_id)
    
    async def get_recent_alerts(self, limit: int = 5) -> List[HealthAlert]:
        """Get recent health alerts"""
        async with self._lock:
            return self._alerts[-limit:]
    
    async def get_unresolved_alerts(self) -> List[HealthAlert]:
        """Get unresolved health alerts"""
        async with self._lock:
            return [a for a in self._alerts if not a.resolved]
    
    async def resolve_alert(self, alert_id: int) -> bool:
        """Resolve a health alert"""
        async with self._lock:
            for alert in self._alerts:
                if alert.id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    return True
            return False
    
    async def generate_json_report(self) -> Dict[str, Any]:
        """Generate comprehensive JSON health report"""
        async with self._lock:
            snapshots = list(self._snapshots.values())
            alerts = self._alerts[-10:]
            
            # Calculate overall system health
            healthy_count = sum(1 for s in snapshots if s.overall_status == HealthStatus.HEALTHY)
            total_count = len(snapshots)
            system_health = "HEALTHY" if healthy_count == total_count else (
                "DEGRADED" if healthy_count > 0 else "CRITICAL"
            )
            
            return {
                "generated_at": datetime.now().isoformat(),
                "system_health": system_health,
                "plugins": {
                    "total": total_count,
                    "healthy": healthy_count,
                    "degraded": total_count - healthy_count
                },
                "snapshots": [s.to_dict() for s in snapshots],
                "recent_alerts": [a.to_dict() for a in alerts],
                "unresolved_alerts": len([a for a in self._alerts if not a.resolved])
            }
    
    async def generate_telegram_report(self) -> str:
        """Generate health report formatted for Telegram"""
        async with self._lock:
            snapshots = list(self._snapshots.values())
            
            text = "<b>Plugin Health Dashboard</b>\n"
            text += "=" * 30 + "\n\n"
            
            for snapshot in snapshots:
                status_emoji = {
                    HealthStatus.HEALTHY: "GREEN",
                    HealthStatus.STALE: "YELLOW",
                    HealthStatus.HUNG: "ORANGE",
                    HealthStatus.DEAD: "RED",
                    HealthStatus.DEGRADED: "YELLOW",
                    HealthStatus.UNKNOWN: "GRAY"
                }.get(snapshot.overall_status, "GRAY")
                
                text += f"[{status_emoji}] <b>{snapshot.plugin_id}</b>\n"
                text += f"  Status: {snapshot.overall_status.value}\n"
                text += f"  Uptime: {self._format_uptime(snapshot.availability.uptime_seconds)}\n"
                text += f"  Exec Time: {snapshot.performance.p95_execution_time_ms:.0f}ms (P95)\n"
                text += f"  Memory: {snapshot.resources.memory_usage_mb:.1f}MB\n"
                text += f"  CPU: {snapshot.resources.cpu_usage_pct:.1f}%\n"
                text += f"  Error Rate: {snapshot.errors.error_rate_pct:.2f}%\n\n"
            
            # Recent alerts
            recent_alerts = self._alerts[-5:]
            if recent_alerts:
                text += "<b>Recent Alerts (last 5):</b>\n"
                for alert in recent_alerts:
                    age = self._format_time_ago(alert.timestamp)
                    text += f"  [{age}] {alert.message}\n"
            
            return text
    
    def _format_uptime(self, seconds: int) -> str:
        """Format uptime in human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format time ago in human-readable format"""
        delta = datetime.now() - timestamp
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"


# ============================================================================
# PLUGIN HEALTH MONITOR - MAIN CLASS
# ============================================================================

class PluginHealthMonitor:
    """
    Central health monitoring system for all plugins.
    Integrates all health monitoring components.
    """
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        thresholds: Optional[HealthThresholds] = None
    ):
        self.db_path = db_path or "data/zepix_bot.db"
        self.thresholds = thresholds or HealthThresholds()
        
        # Components
        self.heartbeat_monitor = HeartbeatMonitor()
        self.resource_watchdog = ResourceWatchdog()
        self.error_tracker = ErrorRateTracker()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.thresholds.circuit_breaker_threshold,
            cooldown_sec=self.thresholds.circuit_breaker_cooldown_sec
        )
        self.dependency_checker = DependencyChecker()
        self.report_generator = HealthReportGenerator()
        
        # Alert management
        self._last_alert_time: Dict[tuple, datetime] = {}
        self._alert_cooldown_sec = 300
        self._alert_id_counter = 0
        
        # Monitoring state
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._check_interval_sec = 30
        
        # Callbacks
        self._alert_callback: Optional[Callable] = None
        self._plugin_registry: Optional[Any] = None
        
        # Statistics
        self._stats = {
            "checks_performed": 0,
            "alerts_triggered": 0,
            "circuit_breaker_trips": 0,
            "last_check_time": None
        }
        
        # Set up circuit breaker callback
        self.circuit_breaker.set_state_change_callback(self._on_circuit_state_change)
        
        logger.info("PluginHealthMonitor initialized")
    
    def set_alert_callback(self, callback: Callable) -> None:
        """Set callback for health alerts"""
        self._alert_callback = callback
    
    def set_plugin_registry(self, registry: Any) -> None:
        """Set plugin registry for automatic plugin discovery"""
        self._plugin_registry = registry
    
    async def register_plugin(
        self,
        plugin_id: str,
        process_id: Optional[int] = None,
        dependencies: Optional[List[tuple]] = None
    ) -> None:
        """Register a plugin for health monitoring"""
        await self.heartbeat_monitor.register_plugin(plugin_id)
        await self.resource_watchdog.register_plugin(plugin_id, process_id)
        await self.error_tracker.register_plugin(plugin_id)
        await self.circuit_breaker.register_plugin(plugin_id)
        
        if dependencies:
            for name, dep_type in dependencies:
                await self.dependency_checker.register_dependency(plugin_id, name, dep_type)
        
        logger.info(f"Registered plugin {plugin_id} for health monitoring")
    
    async def unregister_plugin(self, plugin_id: str) -> None:
        """Unregister a plugin from health monitoring"""
        await self.heartbeat_monitor.unregister_plugin(plugin_id)
        await self.resource_watchdog.unregister_plugin(plugin_id)
        await self.error_tracker.unregister_plugin(plugin_id)
        await self.circuit_breaker.unregister_plugin(plugin_id)
        
        logger.info(f"Unregistered plugin {plugin_id} from health monitoring")
    
    async def record_heartbeat(self, plugin_id: str) -> None:
        """Record a heartbeat from a plugin"""
        await self.heartbeat_monitor.record_heartbeat(plugin_id)
    
    async def record_error(
        self,
        plugin_id: str,
        message: str,
        is_critical: bool = False
    ) -> None:
        """Record an error from a plugin"""
        await self.error_tracker.record_error(plugin_id, message, is_critical)
        await self.circuit_breaker.record_failure(plugin_id)
    
    async def record_success(self, plugin_id: str) -> None:
        """Record a successful operation from a plugin"""
        await self.circuit_breaker.record_success(plugin_id)
    
    async def is_plugin_allowed(self, plugin_id: str) -> bool:
        """Check if a plugin is allowed to operate (circuit breaker)"""
        return await self.circuit_breaker.is_allowed(plugin_id)
    
    async def start_monitoring(self) -> None:
        """Start background health monitoring loop"""
        if self._running:
            logger.warning("Health monitoring already running")
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started plugin health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop background health monitoring loop"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped plugin health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        logger.info("Health monitoring loop started")
        
        while self._running:
            try:
                await self._collect_and_analyze_all_plugins()
                self._stats["checks_performed"] += 1
                self._stats["last_check_time"] = datetime.now()
                await asyncio.sleep(self._check_interval_sec)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_and_analyze_all_plugins(self) -> None:
        """Collect health metrics for all plugins and analyze"""
        plugin_ids = await self.heartbeat_monitor.get_all_plugin_ids()
        
        for plugin_id in plugin_ids:
            try:
                # Collect all metric types
                availability = await self.heartbeat_monitor.get_availability_metrics(plugin_id)
                performance = await self._collect_performance_metrics(plugin_id)
                resources = await self.resource_watchdog.collect_metrics(plugin_id)
                errors = await self.error_tracker.get_error_metrics(plugin_id)
                
                # Determine overall status
                overall_status = self._determine_overall_status(
                    availability, performance, resources, errors
                )
                
                # Create snapshot
                snapshot = HealthSnapshot(
                    plugin_id=plugin_id,
                    timestamp=datetime.now(),
                    availability=availability,
                    performance=performance,
                    resources=resources,
                    errors=errors,
                    overall_status=overall_status
                )
                
                # Store snapshot
                await self.report_generator.store_snapshot(snapshot)
                
                # Store in database
                await self._store_health_snapshot(snapshot)
                
                # Analyze for anomalies
                await self._analyze_health(plugin_id, availability, performance, resources, errors)
                
            except Exception as e:
                logger.error(f"Failed to collect metrics for {plugin_id}: {e}")
    
    async def _collect_performance_metrics(self, plugin_id: str) -> PluginPerformanceMetrics:
        """Collect performance metrics for a plugin"""
        # Default metrics - would be populated from actual plugin stats
        return PluginPerformanceMetrics(plugin_id=plugin_id)
    
    def _determine_overall_status(
        self,
        availability: PluginAvailabilityMetrics,
        performance: PluginPerformanceMetrics,
        resources: PluginResourceMetrics,
        errors: PluginErrorMetrics
    ) -> HealthStatus:
        """Determine overall health status from all metrics"""
        # Check availability first
        if availability.health_status != HealthStatus.HEALTHY:
            return availability.health_status
        
        # Check for degraded conditions
        degraded = False
        
        if performance.p95_execution_time_ms > self.thresholds.max_execution_time_ms:
            degraded = True
        
        if resources.memory_usage_mb > self.thresholds.max_memory_usage_mb:
            degraded = True
        
        if resources.cpu_usage_pct > self.thresholds.max_cpu_usage_pct:
            degraded = True
        
        if errors.error_rate_pct > self.thresholds.max_error_rate_pct:
            degraded = True
        
        return HealthStatus.DEGRADED if degraded else HealthStatus.HEALTHY
    
    async def _analyze_health(
        self,
        plugin_id: str,
        availability: PluginAvailabilityMetrics,
        performance: PluginPerformanceMetrics,
        resources: PluginResourceMetrics,
        errors: PluginErrorMetrics
    ) -> None:
        """Analyze metrics and trigger alerts if needed"""
        
        # Check availability
        if availability.health_status != HealthStatus.HEALTHY:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.CRITICAL,
                f"Plugin {plugin_id} is {availability.health_status.value}"
            )
        
        # Check performance
        if performance.p95_execution_time_ms > self.thresholds.max_execution_time_ms:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} slow: P95={performance.p95_execution_time_ms:.0f}ms"
            )
        
        # Check resources
        if resources.memory_usage_mb > self.thresholds.max_memory_usage_mb:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} high memory: {resources.memory_usage_mb:.1f}MB"
            )
        
        if resources.cpu_usage_pct > self.thresholds.max_cpu_usage_pct:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} high CPU: {resources.cpu_usage_pct:.1f}%"
            )
        
        # Check errors
        if errors.error_rate_pct > self.thresholds.max_error_rate_pct:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.HIGH,
                f"Plugin {plugin_id} high error rate: {errors.error_rate_pct:.1f}%"
            )
    
    async def _trigger_alert(
        self,
        plugin_id: str,
        level: AlertLevel,
        message: str
    ) -> None:
        """Send alert if not throttled"""
        alert_key = (plugin_id, message)
        
        # Check if recently alerted
        if alert_key in self._last_alert_time:
            elapsed = (datetime.now() - self._last_alert_time[alert_key]).total_seconds()
            if elapsed < self._alert_cooldown_sec:
                return  # Throttled
        
        # Create alert
        self._alert_id_counter += 1
        alert = HealthAlert(
            id=self._alert_id_counter,
            plugin_id=plugin_id,
            alert_level=level,
            message=message,
            timestamp=datetime.now()
        )
        
        # Store alert
        await self.report_generator.store_alert(alert)
        await self._store_health_alert(alert)
        
        # Update throttle timestamp
        self._last_alert_time[alert_key] = datetime.now()
        self._stats["alerts_triggered"] += 1
        
        logger.warning(f"Health alert triggered: {message}")
        
        # Call alert callback if set
        if self._alert_callback:
            try:
                await self._alert_callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    async def _on_circuit_state_change(
        self,
        plugin_id: str,
        old_state: CircuitState,
        new_state: CircuitState
    ) -> None:
        """Handle circuit breaker state changes"""
        if new_state == CircuitState.OPEN:
            self._stats["circuit_breaker_trips"] += 1
            await self._trigger_alert(
                plugin_id,
                AlertLevel.CRITICAL,
                f"Circuit breaker TRIPPED for {plugin_id} - plugin disabled"
            )
        elif new_state == CircuitState.CLOSED and old_state == CircuitState.OPEN:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.INFO,
                f"Circuit breaker RESET for {plugin_id} - plugin re-enabled"
            )
    
    async def _store_health_snapshot(self, snapshot: HealthSnapshot) -> None:
        """Store health snapshot in database"""
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugin_health_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_running BOOLEAN,
                    is_responsive BOOLEAN,
                    health_status TEXT,
                    uptime_seconds INTEGER,
                    avg_execution_time_ms REAL,
                    p95_execution_time_ms REAL,
                    signals_processed_1h INTEGER,
                    win_rate_pct REAL,
                    memory_usage_mb REAL,
                    cpu_usage_pct REAL,
                    db_connections_active INTEGER,
                    total_errors INTEGER,
                    error_rate_pct REAL
                )
            """)
            
            # Create index if not exists
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_plugin_time 
                ON plugin_health_snapshots (plugin_id, timestamp)
            """)
            
            # Insert snapshot
            cursor.execute("""
                INSERT INTO plugin_health_snapshots (
                    plugin_id, timestamp, is_running, is_responsive, health_status,
                    uptime_seconds, avg_execution_time_ms, p95_execution_time_ms,
                    signals_processed_1h, win_rate_pct, memory_usage_mb, cpu_usage_pct,
                    db_connections_active, total_errors, error_rate_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.plugin_id,
                snapshot.timestamp.isoformat(),
                snapshot.availability.is_running,
                snapshot.availability.is_responsive,
                snapshot.overall_status.value,
                snapshot.availability.uptime_seconds,
                snapshot.performance.avg_execution_time_ms,
                snapshot.performance.p95_execution_time_ms,
                snapshot.performance.signals_processed_1h,
                snapshot.performance.win_rate_pct,
                snapshot.resources.memory_usage_mb,
                snapshot.resources.cpu_usage_pct,
                snapshot.resources.db_connections_active,
                snapshot.errors.total_errors,
                snapshot.errors.error_rate_pct
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store health snapshot: {e}")
    
    async def _store_health_alert(self, alert: HealthAlert) -> None:
        """Store health alert in database"""
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME
                )
            """)
            
            # Create index if not exists
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_plugin_alerts 
                ON health_alerts (plugin_id, timestamp)
            """)
            
            # Insert alert
            cursor.execute("""
                INSERT INTO health_alerts (
                    plugin_id, alert_level, message, timestamp, resolved
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                alert.plugin_id,
                alert.alert_level.value,
                alert.message,
                alert.timestamp.isoformat(),
                alert.resolved
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store health alert: {e}")
    
    async def get_latest_snapshots(self) -> List[HealthSnapshot]:
        """Get latest health snapshots for all plugins"""
        return await self.report_generator.get_latest_snapshots()
    
    async def get_recent_alerts(self, limit: int = 5) -> List[HealthAlert]:
        """Get recent health alerts"""
        return await self.report_generator.get_recent_alerts(limit)
    
    async def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report as JSON"""
        return await self.report_generator.generate_json_report()
    
    async def get_telegram_report(self) -> str:
        """Get health report formatted for Telegram"""
        return await self.report_generator.generate_telegram_report()
    
    async def get_plugin_health(self, plugin_id: str) -> Optional[HealthSnapshot]:
        """Get health snapshot for a specific plugin"""
        return await self.report_generator.get_snapshot(plugin_id)
    
    async def check_dependencies(self, plugin_id: str) -> Dict[str, bool]:
        """Check all dependencies for a plugin"""
        return await self.dependency_checker.get_dependency_status(plugin_id)
    
    async def reset_circuit_breaker(self, plugin_id: str) -> None:
        """Manually reset circuit breaker for a plugin"""
        await self.circuit_breaker.reset(plugin_id)
    
    async def trip_circuit_breaker(self, plugin_id: str) -> None:
        """Manually trip circuit breaker for a plugin"""
        await self.circuit_breaker.trip(plugin_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return self._stats.copy()


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_health_monitor(
    db_path: Optional[str] = None,
    thresholds: Optional[HealthThresholds] = None
) -> PluginHealthMonitor:
    """Create a new PluginHealthMonitor instance"""
    return PluginHealthMonitor(db_path=db_path, thresholds=thresholds)


def create_default_thresholds() -> HealthThresholds:
    """Create default health thresholds"""
    return HealthThresholds()


def create_strict_thresholds() -> HealthThresholds:
    """Create strict health thresholds for production"""
    return HealthThresholds(
        max_execution_time_ms=2000.0,
        max_error_rate_pct=2.0,
        max_memory_usage_mb=300.0,
        max_cpu_usage_pct=60.0,
        min_heartbeat_interval_sec=120,
        circuit_breaker_threshold=3,
        circuit_breaker_cooldown_sec=120
    )


def create_relaxed_thresholds() -> HealthThresholds:
    """Create relaxed health thresholds for development"""
    return HealthThresholds(
        max_execution_time_ms=10000.0,
        max_error_rate_pct=20.0,
        max_memory_usage_mb=1024.0,
        max_cpu_usage_pct=95.0,
        min_heartbeat_interval_sec=600,
        circuit_breaker_threshold=10,
        circuit_breaker_cooldown_sec=30
    )
