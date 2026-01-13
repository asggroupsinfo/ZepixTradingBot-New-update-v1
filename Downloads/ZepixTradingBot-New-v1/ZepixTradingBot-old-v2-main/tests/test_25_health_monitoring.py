"""
Test Suite for Document 25: Plugin Health Monitoring System
Tests all health monitoring components including simulating crashing plugins.

Components Tested:
1. PluginHealthMonitor - Central health monitoring system
2. HeartbeatMonitor - Track if plugins are alive and responding
3. ResourceWatchdog - Monitor Memory/CPU usage per plugin
4. ErrorRateTracker - Count exceptions per plugin window
5. CircuitBreaker - Auto-disable plugin if it breaches error thresholds
6. HealthReportGenerator - Generate status JSON for dashboard/Telegram
7. DependencyChecker - Verify plugin dependencies are reachable
"""

import sys
import os
import asyncio
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# MODULE STRUCTURE TESTS
# ============================================================================

class TestHealthMonitorModuleStructure:
    """Test that all required classes and enums exist in health_monitor module"""
    
    def test_module_imports(self):
        """Test that health_monitor module can be imported"""
        from core import health_monitor
        assert health_monitor is not None
    
    def test_health_status_enum_exists(self):
        """Test HealthStatus enum exists"""
        from core.health_monitor import HealthStatus
        assert HealthStatus is not None
    
    def test_alert_level_enum_exists(self):
        """Test AlertLevel enum exists"""
        from core.health_monitor import AlertLevel
        assert AlertLevel is not None
    
    def test_circuit_state_enum_exists(self):
        """Test CircuitState enum exists"""
        from core.health_monitor import CircuitState
        assert CircuitState is not None
    
    def test_dependency_type_enum_exists(self):
        """Test DependencyType enum exists"""
        from core.health_monitor import DependencyType
        assert DependencyType is not None
    
    def test_plugin_availability_metrics_exists(self):
        """Test PluginAvailabilityMetrics dataclass exists"""
        from core.health_monitor import PluginAvailabilityMetrics
        assert PluginAvailabilityMetrics is not None
    
    def test_plugin_performance_metrics_exists(self):
        """Test PluginPerformanceMetrics dataclass exists"""
        from core.health_monitor import PluginPerformanceMetrics
        assert PluginPerformanceMetrics is not None
    
    def test_plugin_resource_metrics_exists(self):
        """Test PluginResourceMetrics dataclass exists"""
        from core.health_monitor import PluginResourceMetrics
        assert PluginResourceMetrics is not None
    
    def test_plugin_error_metrics_exists(self):
        """Test PluginErrorMetrics dataclass exists"""
        from core.health_monitor import PluginErrorMetrics
        assert PluginErrorMetrics is not None
    
    def test_health_snapshot_exists(self):
        """Test HealthSnapshot dataclass exists"""
        from core.health_monitor import HealthSnapshot
        assert HealthSnapshot is not None
    
    def test_health_alert_exists(self):
        """Test HealthAlert dataclass exists"""
        from core.health_monitor import HealthAlert
        assert HealthAlert is not None
    
    def test_health_thresholds_exists(self):
        """Test HealthThresholds dataclass exists"""
        from core.health_monitor import HealthThresholds
        assert HealthThresholds is not None
    
    def test_heartbeat_monitor_exists(self):
        """Test HeartbeatMonitor class exists"""
        from core.health_monitor import HeartbeatMonitor
        assert HeartbeatMonitor is not None
    
    def test_resource_watchdog_exists(self):
        """Test ResourceWatchdog class exists"""
        from core.health_monitor import ResourceWatchdog
        assert ResourceWatchdog is not None
    
    def test_error_rate_tracker_exists(self):
        """Test ErrorRateTracker class exists"""
        from core.health_monitor import ErrorRateTracker
        assert ErrorRateTracker is not None
    
    def test_circuit_breaker_exists(self):
        """Test CircuitBreaker class exists"""
        from core.health_monitor import CircuitBreaker
        assert CircuitBreaker is not None
    
    def test_dependency_checker_exists(self):
        """Test DependencyChecker class exists"""
        from core.health_monitor import DependencyChecker
        assert DependencyChecker is not None
    
    def test_health_report_generator_exists(self):
        """Test HealthReportGenerator class exists"""
        from core.health_monitor import HealthReportGenerator
        assert HealthReportGenerator is not None
    
    def test_plugin_health_monitor_exists(self):
        """Test PluginHealthMonitor class exists"""
        from core.health_monitor import PluginHealthMonitor
        assert PluginHealthMonitor is not None


# ============================================================================
# ENUM TESTS
# ============================================================================

class TestHealthStatusEnum:
    """Test HealthStatus enum values"""
    
    def test_health_status_values(self):
        """Test all HealthStatus values exist"""
        from core.health_monitor import HealthStatus
        
        assert HealthStatus.HEALTHY.value == "HEALTHY"
        assert HealthStatus.STALE.value == "STALE"
        assert HealthStatus.HUNG.value == "HUNG"
        assert HealthStatus.DEAD.value == "DEAD"
        assert HealthStatus.DEGRADED.value == "DEGRADED"
        assert HealthStatus.UNKNOWN.value == "UNKNOWN"


class TestAlertLevelEnum:
    """Test AlertLevel enum values"""
    
    def test_alert_level_values(self):
        """Test all AlertLevel values exist"""
        from core.health_monitor import AlertLevel
        
        assert AlertLevel.INFO.value == "INFO"
        assert AlertLevel.WARNING.value == "WARNING"
        assert AlertLevel.HIGH.value == "HIGH"
        assert AlertLevel.CRITICAL.value == "CRITICAL"


class TestCircuitStateEnum:
    """Test CircuitState enum values"""
    
    def test_circuit_state_values(self):
        """Test all CircuitState values exist"""
        from core.health_monitor import CircuitState
        
        assert CircuitState.CLOSED.value == "CLOSED"
        assert CircuitState.OPEN.value == "OPEN"
        assert CircuitState.HALF_OPEN.value == "HALF_OPEN"


class TestDependencyTypeEnum:
    """Test DependencyType enum values"""
    
    def test_dependency_type_values(self):
        """Test all DependencyType values exist"""
        from core.health_monitor import DependencyType
        
        assert DependencyType.DATABASE.value == "DATABASE"
        assert DependencyType.API.value == "API"
        assert DependencyType.FILE.value == "FILE"
        assert DependencyType.SERVICE.value == "SERVICE"
        assert DependencyType.NETWORK.value == "NETWORK"


# ============================================================================
# DATACLASS TESTS
# ============================================================================

class TestPluginAvailabilityMetrics:
    """Test PluginAvailabilityMetrics dataclass"""
    
    def test_creation(self):
        """Test creating PluginAvailabilityMetrics"""
        from core.health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=True,
            uptime_seconds=3600
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.is_running is True
        assert metrics.is_responsive is True
        assert metrics.uptime_seconds == 3600
    
    def test_health_status_healthy(self):
        """Test health_status property returns HEALTHY"""
        from core.health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=True,
            last_heartbeat=datetime.now()
        )
        
        assert metrics.health_status == HealthStatus.HEALTHY
    
    def test_health_status_dead(self):
        """Test health_status property returns DEAD when not running"""
        from core.health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=False,
            is_responsive=False
        )
        
        assert metrics.health_status == HealthStatus.DEAD
    
    def test_health_status_hung(self):
        """Test health_status property returns HUNG when not responsive"""
        from core.health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=False,
            last_heartbeat=datetime.now()
        )
        
        assert metrics.health_status == HealthStatus.HUNG


class TestPluginPerformanceMetrics:
    """Test PluginPerformanceMetrics dataclass"""
    
    def test_creation(self):
        """Test creating PluginPerformanceMetrics"""
        from core.health_monitor import PluginPerformanceMetrics
        
        metrics = PluginPerformanceMetrics(
            plugin_id="test_plugin",
            avg_execution_time_ms=100.0,
            p95_execution_time_ms=200.0,
            p99_execution_time_ms=500.0,
            signals_processed_1h=50,
            orders_placed_1h=10,
            signal_accuracy_pct=75.0,
            win_rate_pct=60.0
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.avg_execution_time_ms == 100.0
        assert metrics.p95_execution_time_ms == 200.0
        assert metrics.win_rate_pct == 60.0
    
    def test_defaults(self):
        """Test default values"""
        from core.health_monitor import PluginPerformanceMetrics
        
        metrics = PluginPerformanceMetrics(plugin_id="test_plugin")
        
        assert metrics.avg_execution_time_ms == 0.0
        assert metrics.signals_processed_1h == 0


class TestPluginResourceMetrics:
    """Test PluginResourceMetrics dataclass"""
    
    def test_creation(self):
        """Test creating PluginResourceMetrics"""
        from core.health_monitor import PluginResourceMetrics
        
        metrics = PluginResourceMetrics(
            plugin_id="test_plugin",
            memory_usage_mb=256.0,
            memory_limit_mb=512.0,
            cpu_usage_pct=25.0,
            db_connections_active=3,
            db_connections_max=10
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.memory_usage_mb == 256.0
        assert metrics.cpu_usage_pct == 25.0
    
    def test_defaults(self):
        """Test default values"""
        from core.health_monitor import PluginResourceMetrics
        
        metrics = PluginResourceMetrics(plugin_id="test_plugin")
        
        assert metrics.memory_usage_mb == 0.0
        assert metrics.memory_limit_mb == 1024.0


class TestPluginErrorMetrics:
    """Test PluginErrorMetrics dataclass"""
    
    def test_creation(self):
        """Test creating PluginErrorMetrics"""
        from core.health_monitor import PluginErrorMetrics
        
        metrics = PluginErrorMetrics(
            plugin_id="test_plugin",
            total_errors=5,
            critical_errors=1,
            warnings=10,
            error_rate_pct=2.5,
            last_error_message="Test error"
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.total_errors == 5
        assert metrics.critical_errors == 1
        assert metrics.error_rate_pct == 2.5


class TestHealthSnapshot:
    """Test HealthSnapshot dataclass"""
    
    def test_creation(self):
        """Test creating HealthSnapshot"""
        from core.health_monitor import (
            HealthSnapshot, HealthStatus,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics
        )
        
        snapshot = HealthSnapshot(
            plugin_id="test_plugin",
            timestamp=datetime.now(),
            availability=PluginAvailabilityMetrics(plugin_id="test_plugin"),
            performance=PluginPerformanceMetrics(plugin_id="test_plugin"),
            resources=PluginResourceMetrics(plugin_id="test_plugin"),
            errors=PluginErrorMetrics(plugin_id="test_plugin"),
            overall_status=HealthStatus.HEALTHY
        )
        
        assert snapshot.plugin_id == "test_plugin"
        assert snapshot.overall_status == HealthStatus.HEALTHY
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.health_monitor import (
            HealthSnapshot, HealthStatus,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics
        )
        
        snapshot = HealthSnapshot(
            plugin_id="test_plugin",
            timestamp=datetime.now(),
            availability=PluginAvailabilityMetrics(plugin_id="test_plugin"),
            performance=PluginPerformanceMetrics(plugin_id="test_plugin"),
            resources=PluginResourceMetrics(plugin_id="test_plugin"),
            errors=PluginErrorMetrics(plugin_id="test_plugin"),
            overall_status=HealthStatus.HEALTHY
        )
        
        data = snapshot.to_dict()
        
        assert "plugin_id" in data
        assert "timestamp" in data
        assert "overall_status" in data
        assert "availability" in data
        assert "performance" in data
        assert "resources" in data
        assert "errors" in data


class TestHealthAlert:
    """Test HealthAlert dataclass"""
    
    def test_creation(self):
        """Test creating HealthAlert"""
        from core.health_monitor import HealthAlert, AlertLevel
        
        alert = HealthAlert(
            id=1,
            plugin_id="test_plugin",
            alert_level=AlertLevel.WARNING,
            message="Test alert message"
        )
        
        assert alert.id == 1
        assert alert.plugin_id == "test_plugin"
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.message == "Test alert message"
        assert alert.resolved is False
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.health_monitor import HealthAlert, AlertLevel
        
        alert = HealthAlert(
            id=1,
            plugin_id="test_plugin",
            alert_level=AlertLevel.CRITICAL,
            message="Critical error"
        )
        
        data = alert.to_dict()
        
        assert data["id"] == 1
        assert data["plugin_id"] == "test_plugin"
        assert data["alert_level"] == "CRITICAL"


class TestHealthThresholds:
    """Test HealthThresholds dataclass"""
    
    def test_creation(self):
        """Test creating HealthThresholds"""
        from core.health_monitor import HealthThresholds
        
        thresholds = HealthThresholds(
            max_execution_time_ms=3000.0,
            max_error_rate_pct=3.0,
            max_memory_usage_mb=400.0,
            max_cpu_usage_pct=70.0
        )
        
        assert thresholds.max_execution_time_ms == 3000.0
        assert thresholds.max_error_rate_pct == 3.0
    
    def test_defaults(self):
        """Test default values"""
        from core.health_monitor import HealthThresholds
        
        thresholds = HealthThresholds()
        
        assert thresholds.max_execution_time_ms == 5000.0
        assert thresholds.max_error_rate_pct == 5.0
        assert thresholds.max_memory_usage_mb == 500.0
        assert thresholds.max_cpu_usage_pct == 80.0
        assert thresholds.min_heartbeat_interval_sec == 300
        assert thresholds.circuit_breaker_threshold == 5


# ============================================================================
# HEARTBEAT MONITOR TESTS
# ============================================================================

class TestHeartbeatMonitor:
    """Test HeartbeatMonitor class"""
    
    def test_register_plugin(self):
        """Test registering a plugin"""
        from core.health_monitor import HeartbeatMonitor
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            plugin_ids = await monitor.get_all_plugin_ids()
            assert "test_plugin" in plugin_ids
        
        asyncio.run(run_test())
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin"""
        from core.health_monitor import HeartbeatMonitor
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.unregister_plugin("test_plugin")
            plugin_ids = await monitor.get_all_plugin_ids()
            assert "test_plugin" not in plugin_ids
        
        asyncio.run(run_test())
    
    def test_record_heartbeat(self):
        """Test recording a heartbeat"""
        from core.health_monitor import HeartbeatMonitor
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.record_heartbeat("test_plugin")
            metrics = await monitor.get_availability_metrics("test_plugin")
            assert metrics.is_running is True
            assert metrics.is_responsive is True
        
        asyncio.run(run_test())
    
    def test_mark_unresponsive(self):
        """Test marking a plugin as unresponsive"""
        from core.health_monitor import HeartbeatMonitor, HealthStatus
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.mark_unresponsive("test_plugin")
            metrics = await monitor.get_availability_metrics("test_plugin")
            assert metrics.is_responsive is False
            assert metrics.health_status == HealthStatus.HUNG
        
        asyncio.run(run_test())
    
    def test_mark_stopped(self):
        """Test marking a plugin as stopped"""
        from core.health_monitor import HeartbeatMonitor, HealthStatus
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.mark_stopped("test_plugin")
            metrics = await monitor.get_availability_metrics("test_plugin")
            assert metrics.is_running is False
            assert metrics.health_status == HealthStatus.DEAD
        
        asyncio.run(run_test())
    
    def test_check_stale_plugins(self):
        """Test checking for stale plugins"""
        from core.health_monitor import HeartbeatMonitor
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            stale = await monitor.check_stale_plugins(threshold_sec=0)
            assert "test_plugin" in stale
        
        asyncio.run(run_test())
    
    def test_uptime_calculation(self):
        """Test uptime calculation"""
        from core.health_monitor import HeartbeatMonitor
        
        async def run_test():
            monitor = HeartbeatMonitor()
            await monitor.register_plugin("test_plugin")
            await asyncio.sleep(0.1)
            metrics = await monitor.get_availability_metrics("test_plugin")
            assert metrics.uptime_seconds >= 0
        
        asyncio.run(run_test())


# ============================================================================
# RESOURCE WATCHDOG TESTS
# ============================================================================

class TestResourceWatchdog:
    """Test ResourceWatchdog class"""
    
    def test_register_plugin(self):
        """Test registering a plugin"""
        from core.health_monitor import ResourceWatchdog
        
        async def run_test():
            watchdog = ResourceWatchdog()
            await watchdog.register_plugin("test_plugin")
            metrics = await watchdog.get_metrics("test_plugin")
            assert metrics.plugin_id == "test_plugin"
        
        asyncio.run(run_test())
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin"""
        from core.health_monitor import ResourceWatchdog
        
        async def run_test():
            watchdog = ResourceWatchdog()
            await watchdog.register_plugin("test_plugin")
            await watchdog.unregister_plugin("test_plugin")
            metrics = await watchdog.get_metrics("test_plugin")
            assert metrics.plugin_id == "test_plugin"
        
        asyncio.run(run_test())
    
    def test_collect_metrics(self):
        """Test collecting resource metrics"""
        from core.health_monitor import ResourceWatchdog
        
        async def run_test():
            watchdog = ResourceWatchdog()
            await watchdog.register_plugin("test_plugin")
            metrics = await watchdog.collect_metrics("test_plugin")
            assert metrics.plugin_id == "test_plugin"
            assert isinstance(metrics.memory_usage_mb, float)
            assert isinstance(metrics.cpu_usage_pct, float)
        
        asyncio.run(run_test())
    
    def test_update_db_stats(self):
        """Test updating database stats"""
        from core.health_monitor import ResourceWatchdog
        
        async def run_test():
            watchdog = ResourceWatchdog()
            await watchdog.register_plugin("test_plugin")
            await watchdog.update_db_stats("test_plugin", 5, 10, 15.5)
            metrics = await watchdog.get_metrics("test_plugin")
            assert metrics.db_connections_active == 5
            assert metrics.db_connections_max == 10
            assert metrics.db_query_time_avg_ms == 15.5
        
        asyncio.run(run_test())
    
    def test_check_resource_thresholds(self):
        """Test checking resource thresholds"""
        from core.health_monitor import ResourceWatchdog
        
        async def run_test():
            watchdog = ResourceWatchdog()
            await watchdog.register_plugin("test_plugin")
            await watchdog.collect_metrics("test_plugin")
            violations = await watchdog.check_resource_thresholds(
                "test_plugin",
                max_memory_mb=0.001,
                max_cpu_pct=0.001
            )
            assert isinstance(violations, list)
        
        asyncio.run(run_test())


# ============================================================================
# ERROR RATE TRACKER TESTS
# ============================================================================

class TestErrorRateTracker:
    """Test ErrorRateTracker class"""
    
    def test_register_plugin(self):
        """Test registering a plugin"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            metrics = await tracker.get_error_metrics("test_plugin")
            assert metrics.plugin_id == "test_plugin"
            assert metrics.total_errors == 0
        
        asyncio.run(run_test())
    
    def test_record_error(self):
        """Test recording an error"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            await tracker.record_error("test_plugin", "Test error message")
            metrics = await tracker.get_error_metrics("test_plugin")
            assert metrics.total_errors == 1
            assert metrics.last_error_message == "Test error message"
        
        asyncio.run(run_test())
    
    def test_record_critical_error(self):
        """Test recording a critical error"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            await tracker.record_error("test_plugin", "Critical error", is_critical=True)
            metrics = await tracker.get_error_metrics("test_plugin")
            assert metrics.critical_errors == 1
        
        asyncio.run(run_test())
    
    def test_record_warning(self):
        """Test recording a warning"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            await tracker.record_error("test_plugin", "Warning message", is_warning=True)
            metrics = await tracker.get_error_metrics("test_plugin")
            assert metrics.warnings == 1
        
        asyncio.run(run_test())
    
    def test_get_error_count(self):
        """Test getting error count"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            for i in range(5):
                await tracker.record_error("test_plugin", f"Error {i}")
            count = await tracker.get_error_count("test_plugin")
            assert count == 5
        
        asyncio.run(run_test())
    
    def test_clear_errors(self):
        """Test clearing errors"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            await tracker.record_error("test_plugin", "Test error")
            await tracker.clear_errors("test_plugin")
            count = await tracker.get_error_count("test_plugin")
            assert count == 0
        
        asyncio.run(run_test())
    
    def test_error_rate_calculation(self):
        """Test error rate calculation"""
        from core.health_monitor import ErrorRateTracker
        
        async def run_test():
            tracker = ErrorRateTracker()
            await tracker.register_plugin("test_plugin")
            for i in range(10):
                await tracker.record_error("test_plugin", f"Error {i}")
            metrics = await tracker.get_error_metrics("test_plugin", total_operations=100)
            assert metrics.error_rate_pct == 10.0
        
        asyncio.run(run_test())


# ============================================================================
# CIRCUIT BREAKER TESTS
# ============================================================================

class TestCircuitBreaker:
    """Test CircuitBreaker class"""
    
    def test_register_plugin(self):
        """Test registering a plugin"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        async def run_test():
            breaker = CircuitBreaker()
            await breaker.register_plugin("test_plugin")
            state = await breaker.get_state("test_plugin")
            assert state.state == CircuitState.CLOSED
        
        asyncio.run(run_test())
    
    def test_initial_state_closed(self):
        """Test initial state is CLOSED"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        async def run_test():
            breaker = CircuitBreaker()
            await breaker.register_plugin("test_plugin")
            is_allowed = await breaker.is_allowed("test_plugin")
            assert is_allowed is True
        
        asyncio.run(run_test())
    
    def test_record_success(self):
        """Test recording success"""
        from core.health_monitor import CircuitBreaker
        
        async def run_test():
            breaker = CircuitBreaker()
            await breaker.register_plugin("test_plugin")
            await breaker.record_success("test_plugin")
            state = await breaker.get_state("test_plugin")
            assert state.success_count == 1
        
        asyncio.run(run_test())
    
    def test_record_failure(self):
        """Test recording failure"""
        from core.health_monitor import CircuitBreaker
        
        async def run_test():
            breaker = CircuitBreaker()
            await breaker.register_plugin("test_plugin")
            await breaker.record_failure("test_plugin")
            state = await breaker.get_state("test_plugin")
            assert state.failure_count == 1
        
        asyncio.run(run_test())
    
    def test_circuit_trips_on_threshold(self):
        """Test circuit trips when failure threshold is reached"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        async def run_test():
            breaker = CircuitBreaker(failure_threshold=3)
            await breaker.register_plugin("test_plugin")
            for _ in range(3):
                await breaker.record_failure("test_plugin")
            state = await breaker.get_state("test_plugin")
            assert state.state == CircuitState.OPEN
        
        asyncio.run(run_test())
    
    def test_circuit_blocks_when_open(self):
        """Test circuit blocks requests when OPEN"""
        from core.health_monitor import CircuitBreaker
        
        async def run_test():
            breaker = CircuitBreaker(failure_threshold=3, cooldown_sec=60)
            await breaker.register_plugin("test_plugin")
            for _ in range(3):
                await breaker.record_failure("test_plugin")
            is_allowed = await breaker.is_allowed("test_plugin")
            assert is_allowed is False
        
        asyncio.run(run_test())
    
    def test_manual_reset(self):
        """Test manual circuit reset"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        async def run_test():
            breaker = CircuitBreaker(failure_threshold=3)
            await breaker.register_plugin("test_plugin")
            for _ in range(3):
                await breaker.record_failure("test_plugin")
            await breaker.reset("test_plugin")
            state = await breaker.get_state("test_plugin")
            assert state.state == CircuitState.CLOSED
        
        asyncio.run(run_test())
    
    def test_manual_trip(self):
        """Test manual circuit trip"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        async def run_test():
            breaker = CircuitBreaker()
            await breaker.register_plugin("test_plugin")
            await breaker.trip("test_plugin")
            state = await breaker.get_state("test_plugin")
            assert state.state == CircuitState.OPEN
        
        asyncio.run(run_test())
    
    def test_state_change_callback(self):
        """Test state change callback is called"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        async def run_test():
            callback_called = []
            
            async def callback(plugin_id, old_state, new_state):
                callback_called.append((plugin_id, old_state, new_state))
            
            breaker = CircuitBreaker(failure_threshold=3)
            breaker.set_state_change_callback(callback)
            await breaker.register_plugin("test_plugin")
            for _ in range(3):
                await breaker.record_failure("test_plugin")
            
            assert len(callback_called) == 1
            assert callback_called[0][0] == "test_plugin"
            assert callback_called[0][2] == CircuitState.OPEN
        
        asyncio.run(run_test())


# ============================================================================
# DEPENDENCY CHECKER TESTS
# ============================================================================

class TestDependencyChecker:
    """Test DependencyChecker class"""
    
    def test_register_dependency(self):
        """Test registering a dependency"""
        from core.health_monitor import DependencyChecker, DependencyType
        
        async def run_test():
            checker = DependencyChecker()
            await checker.register_dependency(
                "test_plugin",
                "test.db",
                DependencyType.DATABASE
            )
            status = await checker.get_dependency_status("test_plugin")
            assert "test.db" in status
        
        asyncio.run(run_test())
    
    def test_check_database_exists(self):
        """Test checking existing database"""
        from core.health_monitor import DependencyChecker
        
        async def run_test():
            checker = DependencyChecker()
            
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
                db_path = f.name
            
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.close()
                
                status = await checker.check_database(db_path)
                assert status.is_available is True
            finally:
                os.unlink(db_path)
        
        asyncio.run(run_test())
    
    def test_check_database_not_exists(self):
        """Test checking non-existent database"""
        from core.health_monitor import DependencyChecker
        
        async def run_test():
            checker = DependencyChecker()
            status = await checker.check_database("/nonexistent/path/test.db")
            assert status.is_available is False
            assert "not found" in status.error_message.lower()
        
        asyncio.run(run_test())
    
    def test_check_file_exists(self):
        """Test checking existing file"""
        from core.health_monitor import DependencyChecker
        
        async def run_test():
            checker = DependencyChecker()
            
            with tempfile.NamedTemporaryFile(delete=False) as f:
                file_path = f.name
            
            try:
                status = await checker.check_file(file_path)
                assert status.is_available is True
            finally:
                os.unlink(file_path)
        
        asyncio.run(run_test())
    
    def test_check_file_not_exists(self):
        """Test checking non-existent file"""
        from core.health_monitor import DependencyChecker
        
        async def run_test():
            checker = DependencyChecker()
            status = await checker.check_file("/nonexistent/path/test.txt")
            assert status.is_available is False
        
        asyncio.run(run_test())


# ============================================================================
# HEALTH REPORT GENERATOR TESTS
# ============================================================================

class TestHealthReportGenerator:
    """Test HealthReportGenerator class"""
    
    def test_store_snapshot(self):
        """Test storing a health snapshot"""
        from core.health_monitor import (
            HealthReportGenerator, HealthSnapshot, HealthStatus,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics
        )
        
        async def run_test():
            generator = HealthReportGenerator()
            
            snapshot = HealthSnapshot(
                plugin_id="test_plugin",
                timestamp=datetime.now(),
                availability=PluginAvailabilityMetrics(plugin_id="test_plugin"),
                performance=PluginPerformanceMetrics(plugin_id="test_plugin"),
                resources=PluginResourceMetrics(plugin_id="test_plugin"),
                errors=PluginErrorMetrics(plugin_id="test_plugin"),
                overall_status=HealthStatus.HEALTHY
            )
            
            await generator.store_snapshot(snapshot)
            snapshots = await generator.get_latest_snapshots()
            assert len(snapshots) == 1
            assert snapshots[0].plugin_id == "test_plugin"
        
        asyncio.run(run_test())
    
    def test_store_alert(self):
        """Test storing a health alert"""
        from core.health_monitor import HealthReportGenerator, HealthAlert, AlertLevel
        
        async def run_test():
            generator = HealthReportGenerator()
            
            alert = HealthAlert(
                id=1,
                plugin_id="test_plugin",
                alert_level=AlertLevel.WARNING,
                message="Test alert"
            )
            
            await generator.store_alert(alert)
            alerts = await generator.get_recent_alerts()
            assert len(alerts) == 1
            assert alerts[0].message == "Test alert"
        
        asyncio.run(run_test())
    
    def test_get_unresolved_alerts(self):
        """Test getting unresolved alerts"""
        from core.health_monitor import HealthReportGenerator, HealthAlert, AlertLevel
        
        async def run_test():
            generator = HealthReportGenerator()
            
            alert1 = HealthAlert(id=1, plugin_id="p1", alert_level=AlertLevel.WARNING, message="Alert 1")
            alert2 = HealthAlert(id=2, plugin_id="p2", alert_level=AlertLevel.WARNING, message="Alert 2", resolved=True)
            
            await generator.store_alert(alert1)
            await generator.store_alert(alert2)
            
            unresolved = await generator.get_unresolved_alerts()
            assert len(unresolved) == 1
            assert unresolved[0].id == 1
        
        asyncio.run(run_test())
    
    def test_resolve_alert(self):
        """Test resolving an alert"""
        from core.health_monitor import HealthReportGenerator, HealthAlert, AlertLevel
        
        async def run_test():
            generator = HealthReportGenerator()
            
            alert = HealthAlert(id=1, plugin_id="test_plugin", alert_level=AlertLevel.WARNING, message="Test")
            await generator.store_alert(alert)
            
            result = await generator.resolve_alert(1)
            assert result is True
            
            unresolved = await generator.get_unresolved_alerts()
            assert len(unresolved) == 0
        
        asyncio.run(run_test())
    
    def test_generate_json_report(self):
        """Test generating JSON report"""
        from core.health_monitor import (
            HealthReportGenerator, HealthSnapshot, HealthStatus,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics
        )
        
        async def run_test():
            generator = HealthReportGenerator()
            
            snapshot = HealthSnapshot(
                plugin_id="test_plugin",
                timestamp=datetime.now(),
                availability=PluginAvailabilityMetrics(plugin_id="test_plugin"),
                performance=PluginPerformanceMetrics(plugin_id="test_plugin"),
                resources=PluginResourceMetrics(plugin_id="test_plugin"),
                errors=PluginErrorMetrics(plugin_id="test_plugin"),
                overall_status=HealthStatus.HEALTHY
            )
            await generator.store_snapshot(snapshot)
            
            report = await generator.generate_json_report()
            
            assert "generated_at" in report
            assert "system_health" in report
            assert "plugins" in report
            assert "snapshots" in report
        
        asyncio.run(run_test())
    
    def test_generate_telegram_report(self):
        """Test generating Telegram report"""
        from core.health_monitor import (
            HealthReportGenerator, HealthSnapshot, HealthStatus,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics
        )
        
        async def run_test():
            generator = HealthReportGenerator()
            
            snapshot = HealthSnapshot(
                plugin_id="test_plugin",
                timestamp=datetime.now(),
                availability=PluginAvailabilityMetrics(plugin_id="test_plugin"),
                performance=PluginPerformanceMetrics(plugin_id="test_plugin"),
                resources=PluginResourceMetrics(plugin_id="test_plugin"),
                errors=PluginErrorMetrics(plugin_id="test_plugin"),
                overall_status=HealthStatus.HEALTHY
            )
            await generator.store_snapshot(snapshot)
            
            report = await generator.generate_telegram_report()
            
            assert "Plugin Health Dashboard" in report
            assert "test_plugin" in report
        
        asyncio.run(run_test())


# ============================================================================
# PLUGIN HEALTH MONITOR TESTS
# ============================================================================

class TestPluginHealthMonitor:
    """Test PluginHealthMonitor main class"""
    
    def test_creation(self):
        """Test creating PluginHealthMonitor"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        assert monitor is not None
        assert monitor.heartbeat_monitor is not None
        assert monitor.resource_watchdog is not None
        assert monitor.error_tracker is not None
        assert monitor.circuit_breaker is not None
        assert monitor.dependency_checker is not None
        assert monitor.report_generator is not None
    
    def test_register_plugin(self):
        """Test registering a plugin"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            plugin_ids = await monitor.heartbeat_monitor.get_all_plugin_ids()
            assert "test_plugin" in plugin_ids
        
        asyncio.run(run_test())
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.unregister_plugin("test_plugin")
            plugin_ids = await monitor.heartbeat_monitor.get_all_plugin_ids()
            assert "test_plugin" not in plugin_ids
        
        asyncio.run(run_test())
    
    def test_record_heartbeat(self):
        """Test recording heartbeat"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.record_heartbeat("test_plugin")
            metrics = await monitor.heartbeat_monitor.get_availability_metrics("test_plugin")
            assert metrics.is_responsive is True
        
        asyncio.run(run_test())
    
    def test_record_error(self):
        """Test recording error"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.record_error("test_plugin", "Test error")
            metrics = await monitor.error_tracker.get_error_metrics("test_plugin")
            assert metrics.total_errors == 1
        
        asyncio.run(run_test())
    
    def test_record_success(self):
        """Test recording success"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            await monitor.record_success("test_plugin")
            state = await monitor.circuit_breaker.get_state("test_plugin")
            assert state.success_count == 1
        
        asyncio.run(run_test())
    
    def test_is_plugin_allowed(self):
        """Test checking if plugin is allowed"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            is_allowed = await monitor.is_plugin_allowed("test_plugin")
            assert is_allowed is True
        
        asyncio.run(run_test())
    
    def test_get_health_report(self):
        """Test getting health report"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("test_plugin")
            report = await monitor.get_health_report()
            assert "generated_at" in report
            assert "system_health" in report
        
        asyncio.run(run_test())
    
    def test_get_stats(self):
        """Test getting monitoring stats"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        stats = monitor.get_stats()
        
        assert "checks_performed" in stats
        assert "alerts_triggered" in stats
        assert "circuit_breaker_trips" in stats


class TestPluginHealthMonitorStartStop:
    """Test PluginHealthMonitor start/stop functionality"""
    
    def test_start_monitoring(self):
        """Test starting monitoring"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.start_monitoring()
            assert monitor._running is True
            await monitor.stop_monitoring()
        
        asyncio.run(run_test())
    
    def test_stop_monitoring(self):
        """Test stopping monitoring"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.start_monitoring()
            await monitor.stop_monitoring()
            assert monitor._running is False
        
        asyncio.run(run_test())
    
    def test_double_start(self):
        """Test double start is handled"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.start_monitoring()
            await monitor.start_monitoring()
            assert monitor._running is True
            await monitor.stop_monitoring()
        
        asyncio.run(run_test())


# ============================================================================
# SIMULATING CRASHING PLUGINS TESTS
# ============================================================================

class TestCrashingPluginSimulation:
    """Test simulating crashing plugins"""
    
    def test_plugin_crash_detection(self):
        """Test detecting a crashed plugin"""
        from core.health_monitor import PluginHealthMonitor, HealthStatus
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("crashing_plugin")
            await monitor.heartbeat_monitor.mark_stopped("crashing_plugin")
            metrics = await monitor.heartbeat_monitor.get_availability_metrics("crashing_plugin")
            assert metrics.health_status == HealthStatus.DEAD
        
        asyncio.run(run_test())
    
    def test_plugin_hung_detection(self):
        """Test detecting a hung plugin"""
        from core.health_monitor import PluginHealthMonitor, HealthStatus
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("hung_plugin")
            await monitor.heartbeat_monitor.mark_unresponsive("hung_plugin")
            metrics = await monitor.heartbeat_monitor.get_availability_metrics("hung_plugin")
            assert metrics.health_status == HealthStatus.HUNG
        
        asyncio.run(run_test())
    
    def test_circuit_breaker_trips_on_errors(self):
        """Test circuit breaker trips after multiple errors"""
        from core.health_monitor import PluginHealthMonitor, CircuitState
        
        async def run_test():
            monitor = PluginHealthMonitor()
            monitor.circuit_breaker._failure_threshold = 3
            await monitor.register_plugin("error_prone_plugin")
            for i in range(3):
                await monitor.record_error("error_prone_plugin", f"Error {i}")
            state = await monitor.circuit_breaker.get_state("error_prone_plugin")
            assert state.state == CircuitState.OPEN
        
        asyncio.run(run_test())
    
    def test_plugin_disabled_after_circuit_trip(self):
        """Test plugin is disabled after circuit breaker trips"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            monitor.circuit_breaker._failure_threshold = 3
            monitor.circuit_breaker._cooldown_sec = 60
            await monitor.register_plugin("disabled_plugin")
            for i in range(3):
                await monitor.record_error("disabled_plugin", f"Error {i}")
            is_allowed = await monitor.is_plugin_allowed("disabled_plugin")
            assert is_allowed is False
        
        asyncio.run(run_test())
    
    def test_plugin_recovery_after_reset(self):
        """Test plugin recovers after circuit breaker reset"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            monitor.circuit_breaker._failure_threshold = 3
            await monitor.register_plugin("recovering_plugin")
            for i in range(3):
                await monitor.record_error("recovering_plugin", f"Error {i}")
            await monitor.reset_circuit_breaker("recovering_plugin")
            is_allowed = await monitor.is_plugin_allowed("recovering_plugin")
            assert is_allowed is True
        
        asyncio.run(run_test())
    
    def test_high_error_rate_detection(self):
        """Test detecting high error rate"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            monitor = PluginHealthMonitor()
            await monitor.register_plugin("high_error_plugin")
            for i in range(20):
                await monitor.record_error("high_error_plugin", f"Error {i}")
            metrics = await monitor.error_tracker.get_error_metrics("high_error_plugin", total_operations=100)
            assert metrics.error_rate_pct == 20.0
        
        asyncio.run(run_test())


# ============================================================================
# FACTORY FUNCTION TESTS
# ============================================================================

class TestFactoryFunctions:
    """Test factory functions"""
    
    def test_create_health_monitor(self):
        """Test create_health_monitor factory"""
        from core.health_monitor import create_health_monitor
        
        monitor = create_health_monitor()
        assert monitor is not None
    
    def test_create_health_monitor_with_db_path(self):
        """Test create_health_monitor with custom db path"""
        from core.health_monitor import create_health_monitor
        
        monitor = create_health_monitor(db_path="/tmp/test_health.db")
        assert monitor.db_path == "/tmp/test_health.db"
    
    def test_create_default_thresholds(self):
        """Test create_default_thresholds factory"""
        from core.health_monitor import create_default_thresholds
        
        thresholds = create_default_thresholds()
        assert thresholds.max_execution_time_ms == 5000.0
        assert thresholds.max_error_rate_pct == 5.0
    
    def test_create_strict_thresholds(self):
        """Test create_strict_thresholds factory"""
        from core.health_monitor import create_strict_thresholds
        
        thresholds = create_strict_thresholds()
        assert thresholds.max_execution_time_ms == 2000.0
        assert thresholds.max_error_rate_pct == 2.0
        assert thresholds.circuit_breaker_threshold == 3
    
    def test_create_relaxed_thresholds(self):
        """Test create_relaxed_thresholds factory"""
        from core.health_monitor import create_relaxed_thresholds
        
        thresholds = create_relaxed_thresholds()
        assert thresholds.max_execution_time_ms == 10000.0
        assert thresholds.max_error_rate_pct == 20.0
        assert thresholds.circuit_breaker_threshold == 10


# ============================================================================
# DATABASE PERSISTENCE TESTS
# ============================================================================

class TestDatabasePersistence:
    """Test database persistence functionality"""
    
    def test_store_health_snapshot_creates_table(self):
        """Test storing snapshot creates database table"""
        from core.health_monitor import (
            PluginHealthMonitor, HealthSnapshot, HealthStatus,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics
        )
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test_health.db")
                monitor = PluginHealthMonitor(db_path=db_path)
                
                snapshot = HealthSnapshot(
                    plugin_id="test_plugin",
                    timestamp=datetime.now(),
                    availability=PluginAvailabilityMetrics(plugin_id="test_plugin"),
                    performance=PluginPerformanceMetrics(plugin_id="test_plugin"),
                    resources=PluginResourceMetrics(plugin_id="test_plugin"),
                    errors=PluginErrorMetrics(plugin_id="test_plugin"),
                    overall_status=HealthStatus.HEALTHY
                )
                
                await monitor._store_health_snapshot(snapshot)
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='plugin_health_snapshots'")
                result = cursor.fetchone()
                conn.close()
                
                assert result is not None
        
        asyncio.run(run_test())
    
    def test_store_health_alert_creates_table(self):
        """Test storing alert creates database table"""
        from core.health_monitor import PluginHealthMonitor, HealthAlert, AlertLevel
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test_health.db")
                monitor = PluginHealthMonitor(db_path=db_path)
                
                alert = HealthAlert(
                    id=1,
                    plugin_id="test_plugin",
                    alert_level=AlertLevel.WARNING,
                    message="Test alert"
                )
                
                await monitor._store_health_alert(alert)
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='health_alerts'")
                result = cursor.fetchone()
                conn.close()
                
                assert result is not None
        
        asyncio.run(run_test())


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for health monitoring system"""
    
    def test_full_monitoring_cycle(self):
        """Test full monitoring cycle"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = os.path.join(tmpdir, "test_health.db")
                monitor = PluginHealthMonitor(db_path=db_path)
                
                await monitor.register_plugin("plugin_a")
                await monitor.register_plugin("plugin_b")
                await monitor.record_heartbeat("plugin_a")
                await monitor.record_heartbeat("plugin_b")
                await monitor.record_error("plugin_a", "Minor error")
                await monitor.record_success("plugin_b")
                
                report = await monitor.get_health_report()
                
                assert report is not None
                assert "system_health" in report
        
        asyncio.run(run_test())
    
    def test_alert_callback_integration(self):
        """Test alert callback is called on health issues"""
        from core.health_monitor import PluginHealthMonitor
        
        async def run_test():
            alerts_received = []
            
            async def alert_callback(alert):
                alerts_received.append(alert)
            
            monitor = PluginHealthMonitor()
            monitor.set_alert_callback(alert_callback)
            monitor._alert_cooldown_sec = 0
            
            await monitor.register_plugin("test_plugin")
            await monitor.heartbeat_monitor.mark_stopped("test_plugin")
            
            availability = await monitor.heartbeat_monitor.get_availability_metrics("test_plugin")
            performance = await monitor._collect_performance_metrics("test_plugin")
            resources = await monitor.resource_watchdog.get_metrics("test_plugin")
            errors = await monitor.error_tracker.get_error_metrics("test_plugin")
            
            await monitor._analyze_health("test_plugin", availability, performance, resources, errors)
            
            assert len(alerts_received) >= 1
        
        asyncio.run(run_test())


# ============================================================================
# DOCUMENT 25 REQUIREMENTS TESTS
# ============================================================================

class TestDocument25Requirements:
    """Test Document 25 specific requirements"""
    
    def test_heartbeat_monitor_implemented(self):
        """Test Heartbeat Monitor is implemented"""
        from core.health_monitor import HeartbeatMonitor
        
        monitor = HeartbeatMonitor()
        assert hasattr(monitor, 'register_plugin')
        assert hasattr(monitor, 'record_heartbeat')
        assert hasattr(monitor, 'get_availability_metrics')
    
    def test_resource_watchdog_implemented(self):
        """Test Resource Watchdog is implemented"""
        from core.health_monitor import ResourceWatchdog
        
        watchdog = ResourceWatchdog()
        assert hasattr(watchdog, 'collect_metrics')
        assert hasattr(watchdog, 'check_resource_thresholds')
    
    def test_error_rate_tracker_implemented(self):
        """Test Error Rate Tracker is implemented"""
        from core.health_monitor import ErrorRateTracker
        
        tracker = ErrorRateTracker()
        assert hasattr(tracker, 'record_error')
        assert hasattr(tracker, 'get_error_metrics')
        assert hasattr(tracker, 'get_error_count')
    
    def test_circuit_breaker_implemented(self):
        """Test Circuit Breaker is implemented"""
        from core.health_monitor import CircuitBreaker, CircuitState
        
        breaker = CircuitBreaker()
        assert hasattr(breaker, 'record_failure')
        assert hasattr(breaker, 'record_success')
        assert hasattr(breaker, 'is_allowed')
        assert hasattr(breaker, 'trip')
        assert hasattr(breaker, 'reset')
    
    def test_health_report_implemented(self):
        """Test Health Report Generator is implemented"""
        from core.health_monitor import HealthReportGenerator
        
        generator = HealthReportGenerator()
        assert hasattr(generator, 'generate_json_report')
        assert hasattr(generator, 'generate_telegram_report')
    
    def test_dependency_checker_implemented(self):
        """Test Dependency Checker is implemented"""
        from core.health_monitor import DependencyChecker
        
        checker = DependencyChecker()
        assert hasattr(checker, 'check_database')
        assert hasattr(checker, 'check_file')
        assert hasattr(checker, 'check_api')
    
    def test_health_thresholds_configurable(self):
        """Test health thresholds are configurable"""
        from core.health_monitor import HealthThresholds, PluginHealthMonitor
        
        custom_thresholds = HealthThresholds(
            max_execution_time_ms=1000.0,
            max_error_rate_pct=1.0
        )
        
        monitor = PluginHealthMonitor(thresholds=custom_thresholds)
        assert monitor.thresholds.max_execution_time_ms == 1000.0
        assert monitor.thresholds.max_error_rate_pct == 1.0
    
    def test_alert_throttling_implemented(self):
        """Test alert throttling is implemented"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        assert hasattr(monitor, '_alert_cooldown_sec')
        assert hasattr(monitor, '_last_alert_time')


class TestDocument25Summary:
    """Summary tests for Document 25 implementation"""
    
    def test_all_components_importable(self):
        """Test all components can be imported"""
        from core.health_monitor import (
            HealthStatus,
            AlertLevel,
            CircuitState,
            DependencyType,
            PluginAvailabilityMetrics,
            PluginPerformanceMetrics,
            PluginResourceMetrics,
            PluginErrorMetrics,
            HealthSnapshot,
            HealthAlert,
            HealthThresholds,
            HeartbeatMonitor,
            ResourceWatchdog,
            ErrorRateTracker,
            CircuitBreaker,
            DependencyChecker,
            HealthReportGenerator,
            PluginHealthMonitor,
            create_health_monitor,
            create_default_thresholds,
            create_strict_thresholds,
            create_relaxed_thresholds
        )
        
        assert all([
            HealthStatus, AlertLevel, CircuitState, DependencyType,
            PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics,
            HealthSnapshot, HealthAlert, HealthThresholds,
            HeartbeatMonitor, ResourceWatchdog, ErrorRateTracker,
            CircuitBreaker, DependencyChecker, HealthReportGenerator,
            PluginHealthMonitor, create_health_monitor,
            create_default_thresholds, create_strict_thresholds,
            create_relaxed_thresholds
        ])
    
    def test_health_monitor_has_all_components(self):
        """Test PluginHealthMonitor has all required components"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        
        assert monitor.heartbeat_monitor is not None
        assert monitor.resource_watchdog is not None
        assert monitor.error_tracker is not None
        assert monitor.circuit_breaker is not None
        assert monitor.dependency_checker is not None
        assert monitor.report_generator is not None
    
    def test_monitoring_can_start_and_stop(self):
        """Test monitoring can be started and stopped"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        
        assert hasattr(monitor, 'start_monitoring')
        assert hasattr(monitor, 'stop_monitoring')
        assert callable(monitor.start_monitoring)
        assert callable(monitor.stop_monitoring)
    
    def test_database_schema_implemented(self):
        """Test database schema is implemented"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        
        assert hasattr(monitor, '_store_health_snapshot')
        assert hasattr(monitor, '_store_health_alert')
    
    def test_telegram_health_command_support(self):
        """Test Telegram health command support"""
        from core.health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor()
        
        assert hasattr(monitor, 'get_telegram_report')
        assert hasattr(monitor, 'get_latest_snapshots')
        assert hasattr(monitor, 'get_recent_alerts')
