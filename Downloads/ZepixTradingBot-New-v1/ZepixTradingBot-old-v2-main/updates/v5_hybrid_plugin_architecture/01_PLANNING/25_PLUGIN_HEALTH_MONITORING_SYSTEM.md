# PLUGIN HEALTH MONITORING SYSTEM

**Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Production-Ready Specification  
**Priority:** 🟡 MEDIUM (Operational Excellence)

---

## 🎯 PURPOSE

Monitor the health and performance of all V3 and V6 plugins in real-time, detect anomalies, and alert operators before issues escalate.

**Health Dimensions:**
1. **Availability:** Plugin running and responsive
2. **Performance:** Execution times within SLA
3. **Accuracy:** Signal quality and trade success rates
4. **Resource Usage:** Memory, CPU, database connections
5. **Error Rate:** Exceptions, failed operations

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│          PluginHealthMonitor (Core)             │
├─────────────────────────────────────────────────┤
│  • Collect health metrics every 30s             │
│  • Detect anomalies (thresholds + ML)           │
│  • Trigger alerts (Telegram + logs)             │
│  • Store health history in zepix_bot.db         │
└─────────────────────────────────────────────────┘
           │                         │
           ▼                         ▼
┌──────────────────┐      ┌──────────────────────┐
│  V3 Combined     │      │  V6 Price Action     │
│  Plugin          │      │  Plugins (4x)        │
├──────────────────┤      ├──────────────────────┤
│ Health Checks:   │      │ Health Checks:       │
│ • is_alive()     │      │ • is_alive()         │
│ • get_metrics()  │      │ • get_metrics()      │
│ • self_test()    │      │ • self_test()        │
└──────────────────┘      └──────────────────────┘
```

---

## 📊 HEALTH METRICS

### **1. Plugin Availability Metrics**

```python
@dataclass
class PluginAvailabilityMetrics:
    plugin_id: str
    is_running: bool              # Process alive
    is_responsive: bool           # Responds to ping
    last_heartbeat: datetime      # Last activity timestamp
    uptime_seconds: int           # Time since start
    
    # Calculated
    @property
    def health_status(self) -> str:
        if not self.is_running:
            return "DEAD"
        if not self.is_responsive:
            return "HUNG"
        if (datetime.now() - self.last_heartbeat).seconds > 300:
            return "STALE"
        return "HEALTHY"
```

### **2. Plugin Performance Metrics**

```python
@dataclass
class PluginPerformanceMetrics:
    plugin_id: str
    
    # Latency metrics
    avg_execution_time_ms: float
    p95_execution_time_ms: float
    p99_execution_time_ms: float
    
    # Throughput metrics
    signals_processed_1h: int
    orders_placed_1h: int
    
    # Quality metrics
    signal_accuracy_pct: float    # Profitable signals / Total
    win_rate_pct: float           # Winning trades / Total
```

### **3. Plugin Resource Metrics**

```python
@dataclass
class PluginResourceMetrics:
    plugin_id: str
    
    # Memory
    memory_usage_mb: float
    memory_limit_mb: float
    
    # CPU
    cpu_usage_pct: float
    
    # Database
    db_connections_active: int
    db_connections_max: int
    db_query_time_avg_ms: float
    
    # File handles
    open_file_handles: int
```

### **4. Plugin Error Metrics**

```python
@dataclass
class PluginErrorMetrics:
    plugin_id: str
    
    # Error counts (last 1 hour)
    total_errors: int
    critical_errors: int
    warnings: int
    
    # Error rate
    error_rate_pct: float         # Errors / Total operations
    
    # Recent errors
    last_error_message: str
    last_error_timestamp: datetime
```

---

## 🔍 HEALTH CHECK IMPLEMENTATION

### **PluginHealthMonitor Class**

```python
class PluginHealthMonitor:
    """
    Central health monitoring system for all plugins
    """
    
    def __init__(self, plugin_registry, telegram_manager, db_path):
        self.plugin_registry = plugin_registry
        self.telegram = telegram_manager
        self.db_path = db_path
        
        # Health thresholds
        self.thresholds = {
            'max_execution_time_ms': 5000,
            'max_error_rate_pct': 5.0,
            'max_memory_usage_mb': 500,
            'max_cpu_usage_pct': 80.0,
            'min_heartbeat_interval_sec': 300
        }
        
        # Anomaly detection
        self.historical_metrics = {}  # plugin_id -> deque of metrics
        
        # Alert throttling (prevent spam)
        self.last_alert_time = {}     # (plugin_id, alert_type) -> timestamp
        self.alert_cooldown_sec = 300  # 5 minutes
    
    async def start_monitoring(self):
        """Start background health monitoring loop"""
        logger.info("🏥 Starting plugin health monitoring...")
        
        while True:
            try:
                await self._collect_and_analyze_all_plugins()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_and_analyze_all_plugins(self):
        """Collect health metrics for all plugins and analyze"""
        plugins = self.plugin_registry.get_all_plugins()
        
        for plugin in plugins:
            try:
                # Collect all metric types
                availability = await self._collect_availability_metrics(plugin)
                performance = await self._collect_performance_metrics(plugin)
                resources = await self._collect_resource_metrics(plugin)
                errors = await self._collect_error_metrics(plugin)
                
                # Store in database
                await self._store_health_snapshot(
                    plugin.id, availability, performance, resources, errors
                )
                
                # Analyze for anomalies
                await self._analyze_health(
                    plugin.id, availability, performance, resources, errors
                )
                
            except Exception as e:
                logger.error(f"Failed to collect metrics for {plugin.id}: {e}")
    
    async def _collect_availability_metrics(
        self,
        plugin
    ) -> PluginAvailabilityMetrics:
        """Check if plugin is alive and responsive"""
        try:
            # Ping plugin
            is_responsive = await plugin.ping()
            last_heartbeat = await plugin.get_last_activity_time()
            uptime = await plugin.get_uptime_seconds()
            
            return PluginAvailabilityMetrics(
                plugin_id=plugin.id,
                is_running=True,
                is_responsive=is_responsive,
                last_heartbeat=last_heartbeat,
                uptime_seconds=uptime
            )
            
        except Exception as e:
            logger.warning(f"Plugin {plugin.id} not responding: {e}")
            return PluginAvailabilityMetrics(
                plugin_id=plugin.id,
                is_running=False,
                is_responsive=False,
                last_heartbeat=datetime.min,
                uptime_seconds=0
            )
    
    async def _collect_performance_metrics(
        self,
        plugin
    ) -> PluginPerformanceMetrics:
        """Collect performance stats from plugin"""
        stats = await plugin.get_performance_stats()
        
        return PluginPerformanceMetrics(
            plugin_id=plugin.id,
            avg_execution_time_ms=stats['avg_execution_ms'],
            p95_execution_time_ms=stats['p95_execution_ms'],
            p99_execution_time_ms=stats['p99_execution_ms'],
            signals_processed_1h=stats['signals_1h'],
            orders_placed_1h=stats['orders_1h'],
            signal_accuracy_pct=stats['signal_accuracy'],
            win_rate_pct=stats['win_rate']
        )
    
    async def _collect_resource_metrics(
        self,
        plugin
    ) -> PluginResourceMetrics:
        """Collect resource usage from plugin"""
        import psutil
        
        # Get process info
        process = psutil.Process(plugin.process_id)
        
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # Database connections
        db_stats = await plugin.get_db_connection_stats()
        
        return PluginResourceMetrics(
            plugin_id=plugin.id,
            memory_usage_mb=memory_info.rss / (1024 * 1024),
            memory_limit_mb=1024,  # From config
            cpu_usage_pct=cpu_percent,
            db_connections_active=db_stats['active'],
            db_connections_max=db_stats['max'],
            db_query_time_avg_ms=db_stats['avg_query_time_ms'],
            open_file_handles=len(process.open_files())
        )
    
    async def _collect_error_metrics(
        self,
        plugin
    ) -> PluginErrorMetrics:
        """Collect error stats from plugin"""
        error_stats = await plugin.get_error_stats()
        
        return PluginErrorMetrics(
            plugin_id=plugin.id,
            total_errors=error_stats['total_errors_1h'],
            critical_errors=error_stats['critical_errors_1h'],
            warnings=error_stats['warnings_1h'],
            error_rate_pct=error_stats['error_rate_pct'],
            last_error_message=error_stats['last_error_message'],
            last_error_timestamp=error_stats['last_error_time']
        )
    
    async def _analyze_health(
        self,
        plugin_id: str,
        availability: PluginAvailabilityMetrics,
        performance: PluginPerformanceMetrics,
        resources: PluginResourceMetrics,
        errors: PluginErrorMetrics
    ):
        """Analyze metrics and trigger alerts if needed"""
        
        # Check availability
        if availability.health_status != "HEALTHY":
            await self._trigger_alert(
                plugin_id,
                AlertLevel.CRITICAL,
                f"Plugin {plugin_id} is {availability.health_status}"
            )
        
        # Check performance
        if performance.p95_execution_time_ms > self.thresholds['max_execution_time_ms']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} slow: P95={performance.p95_execution_time_ms}ms"
            )
        
        # Check resources
        if resources.memory_usage_mb > self.thresholds['max_memory_usage_mb']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} high memory: {resources.memory_usage_mb:.1f}MB"
            )
        
        if resources.cpu_usage_pct > self.thresholds['max_cpu_usage_pct']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} high CPU: {resources.cpu_usage_pct:.1f}%"
            )
        
        # Check errors
        if errors.error_rate_pct > self.thresholds['max_error_rate_pct']:
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
    ):
        """Send alert if not throttled"""
        alert_key = (plugin_id, message)
        
        # Check if recently alerted
        if alert_key in self.last_alert_time:
            elapsed = (datetime.now() - self.last_alert_time[alert_key]).seconds
            if elapsed < self.alert_cooldown_sec:
                return  # Throttled
        
        # Send alert
        emoji = {
            AlertLevel.CRITICAL: "🚨",
            AlertLevel.HIGH: "⚠️",
            AlertLevel.WARNING: "⚠️"
        }[level]
        
        await self.telegram.send_notification(
            chat_id=config['telegram_chat_id'],
            text=f"{emoji} <b>Health Alert</b>\n{message}",
            priority=MessagePriority.CRITICAL if level == AlertLevel.CRITICAL else MessagePriority.HIGH
        )
        
        # Update throttle timestamp
        self.last_alert_time[alert_key] = datetime.now()
        
        logger.warning(f"Health alert triggered: {message}")
```

---

## 📦 DATABASE SCHEMA

```sql
-- Plugin health snapshots
CREATE TABLE plugin_health_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Availability
    is_running BOOLEAN,
    is_responsive BOOLEAN,
    health_status TEXT,
    uptime_seconds INTEGER,
    
    -- Performance
    avg_execution_time_ms REAL,
    p95_execution_time_ms REAL,
    signals_processed_1h INTEGER,
    win_rate_pct REAL,
    
    -- Resources
    memory_usage_mb REAL,
    cpu_usage_pct REAL,
    db_connections_active INTEGER,
    
    -- Errors
    total_errors INTEGER,
    error_rate_pct REAL,
    
    INDEX idx_plugin_time (plugin_id, timestamp)
);

-- Health alerts history
CREATE TABLE health_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    alert_level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    
    INDEX idx_plugin_alerts (plugin_id, timestamp)
);
```

---

## 📊 TELEGRAM HEALTH STATUS COMMAND

```python
@telegram_handler('/health')
async def show_health_status(update, context):
    """Show comprehensive health status for all plugins"""
    
    # Get latest health snapshots
    snapshots = await health_monitor.get_latest_snapshots()
    
    text = "🏥 <b>Plugin Health Dashboard</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for snapshot in snapshots:
        status_emoji = {
            "HEALTHY": "🟢",
            "STALE": "🟡",
            "HUNG": "🟠",
            "DEAD": "🔴"
        }[snapshot.health_status]
        
        text += f"{status_emoji} <b>{snapshot.plugin_id}</b>\n"
        text += f"├ Status: {snapshot.health_status}\n"
        text += f"├ Uptime: {format_uptime(snapshot.uptime_seconds)}\n"
        text += f"├ Exec Time: {snapshot.p95_execution_time_ms:.0f}ms (P95)\n"
        text += f"├ Memory: {snapshot.memory_usage_mb:.1f}MB\n"
        text += f"├ CPU: {snapshot.cpu_usage_pct:.1f}%\n"
        text += f"└ Error Rate: {snapshot.error_rate_pct:.2f}%\n\n"
    
    # Recent alerts
    recent_alerts = await health_monitor.get_recent_alerts(limit=5)
    if recent_alerts:
        text += "⚠️ <b>Recent Alerts (last 5):</b>\n"
        for alert in recent_alerts:
            age = format_time_ago(alert.timestamp)
            text += f"• [{age}] {alert.message}\n"
    
    await update.message.reply_text(text, parse_mode='HTML')
```

---

## ✅ COMPLETION CHECKLIST

- [x] Health metrics dataclasses defined
- [x] `PluginHealthMonitor` implementation
- [x] Availability, performance, resource, error collection
- [x] Anomaly detection and alerting
- [x] Alert throttling (prevent spam)
- [x] Database schema for health snapshots
- [x] Telegram `/health` command
- [x] Integration with plugin registry

**Status:** ✅ READY FOR IMPLEMENTATION
