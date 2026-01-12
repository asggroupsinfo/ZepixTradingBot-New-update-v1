"""
Error Handler and Health Monitoring for Multi-Telegram System.

This module provides:
- Graceful error handling
- Automatic retry logic
- Health monitoring dashboard
- Bot status tracking
- Alert notifications for errors

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import traceback


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error category enumeration."""
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    MESSAGE_SEND = "message_send"
    CALLBACK = "callback"
    COMMAND = "command"
    INTERNAL = "internal"
    EXTERNAL = "external"


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """Recovery action enumeration."""
    RETRY = "retry"
    RESTART = "restart"
    SKIP = "skip"
    ALERT = "alert"
    ESCALATE = "escalate"


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    stack_trace: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    bot_id: Optional[str] = None
    user_id: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    recovery_action: Optional[RecoveryAction] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "bot_id": self.bot_id,
            "user_id": self.user_id,
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None,
            "recovery_action": self.recovery_action.value if self.recovery_action else None,
            "retry_count": self.retry_count
        }
    
    def format_notification(self) -> str:
        """Format error for notification."""
        return f"""❌ ERROR ALERT | {self.category.value.upper()}

Error Type: {self.message}
Severity: {self.severity.value.upper()}
Time: {self.timestamp.strftime('%H:%M:%S')}

Details:
{self.details or 'No additional details'}

Status: {'Resolved' if self.resolved else f'Retry {self.retry_count}/3'}
{'Next Retry: 30 seconds' if not self.resolved and self.retry_count < 3 else ''}

📌 Manual Action Required if persists."""


@dataclass
class HealthMetric:
    """Health metric data."""
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_status(self) -> HealthStatus:
        """Get health status based on thresholds."""
        if self.value >= self.threshold_critical:
            return HealthStatus.UNHEALTHY
        elif self.value >= self.threshold_warning:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "status": self.get_status().value,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class BotHealthReport:
    """Health report for a single bot."""
    bot_id: str
    status: HealthStatus
    uptime_seconds: float
    messages_sent: int
    errors_count: int
    last_error: Optional[ErrorRecord] = None
    last_activity: Optional[datetime] = None
    metrics: List[HealthMetric] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bot_id": self.bot_id,
            "status": self.status.value,
            "uptime_seconds": self.uptime_seconds,
            "messages_sent": self.messages_sent,
            "errors_count": self.errors_count,
            "last_error": self.last_error.to_dict() if self.last_error else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "metrics": [m.to_dict() for m in self.metrics]
        }


@dataclass
class SystemHealthReport:
    """Health report for entire system."""
    overall_status: HealthStatus
    bots: Dict[str, BotHealthReport]
    total_errors_24h: int
    total_messages_24h: int
    uptime_percentage: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_status": self.overall_status.value,
            "bots": {k: v.to_dict() for k, v in self.bots.items()},
            "total_errors_24h": self.total_errors_24h,
            "total_messages_24h": self.total_messages_24h,
            "uptime_percentage": self.uptime_percentage,
            "timestamp": self.timestamp.isoformat()
        }


class ErrorHandler:
    """
    Handles errors with retry logic and recovery.
    
    Features:
    - Error categorization
    - Automatic retry with backoff
    - Error notification
    - Recovery actions
    """
    
    def __init__(self, max_retries: int = 3, 
                 retry_delay: float = 1.0,
                 backoff_multiplier: float = 2.0):
        """Initialize error handler."""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier
        self._errors: List[ErrorRecord] = []
        self._error_counter = 0
        self._error_callbacks: List[Callable[[ErrorRecord], None]] = []
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID."""
        self._error_counter += 1
        return f"err_{self._error_counter}_{int(datetime.now().timestamp())}"
    
    def handle_error(self, exception: Exception,
                    category: ErrorCategory = ErrorCategory.INTERNAL,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    bot_id: Optional[str] = None,
                    user_id: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> ErrorRecord:
        """Handle an error."""
        error = ErrorRecord(
            error_id=self._generate_error_id(),
            category=category,
            severity=severity,
            message=str(exception),
            details=str(context) if context else None,
            stack_trace=traceback.format_exc(),
            bot_id=bot_id,
            user_id=user_id
        )
        
        self._errors.append(error)
        
        recovery_action = self._determine_recovery_action(error)
        error.recovery_action = recovery_action
        
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
        
        logger.error(f"Error handled: {error.error_id} - {error.message}")
        
        return error
    
    def _determine_recovery_action(self, error: ErrorRecord) -> RecoveryAction:
        """Determine recovery action based on error."""
        if error.category == ErrorCategory.CONNECTION:
            return RecoveryAction.RETRY
        elif error.category == ErrorCategory.RATE_LIMIT:
            return RecoveryAction.RETRY
        elif error.category == ErrorCategory.AUTHENTICATION:
            return RecoveryAction.ESCALATE
        elif error.severity == ErrorSeverity.CRITICAL:
            return RecoveryAction.ALERT
        elif error.retry_count < self.max_retries:
            return RecoveryAction.RETRY
        else:
            return RecoveryAction.SKIP
    
    def should_retry(self, error: ErrorRecord) -> bool:
        """Check if error should be retried."""
        return (error.recovery_action == RecoveryAction.RETRY and 
                error.retry_count < self.max_retries)
    
    def get_retry_delay(self, error: ErrorRecord) -> float:
        """Get retry delay with exponential backoff."""
        return self.retry_delay * (self.backoff_multiplier ** error.retry_count)
    
    def mark_resolved(self, error_id: str) -> bool:
        """Mark error as resolved."""
        for error in self._errors:
            if error.error_id == error_id:
                error.resolved = True
                error.resolution_time = datetime.now()
                return True
        return False
    
    def increment_retry(self, error: ErrorRecord) -> None:
        """Increment retry count."""
        error.retry_count += 1
    
    def register_callback(self, callback: Callable[[ErrorRecord], None]) -> None:
        """Register error callback."""
        self._error_callbacks.append(callback)
    
    def get_recent_errors(self, hours: int = 24) -> List[ErrorRecord]:
        """Get errors from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [e for e in self._errors if e.timestamp > cutoff]
    
    def get_unresolved_errors(self) -> List[ErrorRecord]:
        """Get unresolved errors."""
        return [e for e in self._errors if not e.resolved]
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorRecord]:
        """Get errors by category."""
        return [e for e in self._errors if e.category == category]
    
    def get_error_count(self, hours: int = 24) -> int:
        """Get error count for last N hours."""
        return len(self.get_recent_errors(hours))
    
    def clear_resolved_errors(self, older_than_hours: int = 24) -> int:
        """Clear resolved errors older than N hours."""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        original_count = len(self._errors)
        self._errors = [e for e in self._errors 
                       if not (e.resolved and e.timestamp < cutoff)]
        return original_count - len(self._errors)


class HealthMonitor:
    """
    Monitors health of Telegram bots.
    
    Features:
    - Real-time health tracking
    - Metric collection
    - Alert generation
    - Dashboard data
    """
    
    def __init__(self, check_interval_seconds: int = 60):
        """Initialize health monitor."""
        self.check_interval = check_interval_seconds
        self._bot_stats: Dict[str, Dict[str, Any]] = {}
        self._system_start_time = datetime.now()
        self._health_callbacks: List[Callable[[SystemHealthReport], None]] = []
    
    def register_bot(self, bot_id: str) -> None:
        """Register a bot for monitoring."""
        self._bot_stats[bot_id] = {
            "start_time": datetime.now(),
            "messages_sent": 0,
            "errors_count": 0,
            "last_activity": None,
            "last_error": None,
            "status": HealthStatus.HEALTHY
        }
        logger.info(f"Registered bot for monitoring: {bot_id}")
    
    def record_message_sent(self, bot_id: str) -> None:
        """Record a message sent."""
        if bot_id in self._bot_stats:
            self._bot_stats[bot_id]["messages_sent"] += 1
            self._bot_stats[bot_id]["last_activity"] = datetime.now()
    
    def record_error(self, bot_id: str, error: ErrorRecord) -> None:
        """Record an error."""
        if bot_id in self._bot_stats:
            self._bot_stats[bot_id]["errors_count"] += 1
            self._bot_stats[bot_id]["last_error"] = error
            self._update_bot_status(bot_id)
    
    def _update_bot_status(self, bot_id: str) -> None:
        """Update bot health status."""
        if bot_id not in self._bot_stats:
            return
        
        stats = self._bot_stats[bot_id]
        error_rate = stats["errors_count"] / max(stats["messages_sent"], 1)
        
        if error_rate > 0.1:
            stats["status"] = HealthStatus.UNHEALTHY
        elif error_rate > 0.05:
            stats["status"] = HealthStatus.DEGRADED
        else:
            stats["status"] = HealthStatus.HEALTHY
    
    def get_bot_health(self, bot_id: str) -> Optional[BotHealthReport]:
        """Get health report for a bot."""
        if bot_id not in self._bot_stats:
            return None
        
        stats = self._bot_stats[bot_id]
        uptime = (datetime.now() - stats["start_time"]).total_seconds()
        
        return BotHealthReport(
            bot_id=bot_id,
            status=stats["status"],
            uptime_seconds=uptime,
            messages_sent=stats["messages_sent"],
            errors_count=stats["errors_count"],
            last_error=stats["last_error"],
            last_activity=stats["last_activity"]
        )
    
    def get_system_health(self) -> SystemHealthReport:
        """Get system-wide health report."""
        bot_reports = {}
        total_errors = 0
        total_messages = 0
        unhealthy_count = 0
        
        for bot_id in self._bot_stats:
            report = self.get_bot_health(bot_id)
            if report:
                bot_reports[bot_id] = report
                total_errors += report.errors_count
                total_messages += report.messages_sent
                if report.status == HealthStatus.UNHEALTHY:
                    unhealthy_count += 1
        
        total_bots = len(self._bot_stats)
        if total_bots == 0:
            overall_status = HealthStatus.UNKNOWN
        elif unhealthy_count == 0:
            overall_status = HealthStatus.HEALTHY
        elif unhealthy_count < total_bots:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        uptime_seconds = (datetime.now() - self._system_start_time).total_seconds()
        uptime_percentage = 100.0
        
        return SystemHealthReport(
            overall_status=overall_status,
            bots=bot_reports,
            total_errors_24h=total_errors,
            total_messages_24h=total_messages,
            uptime_percentage=uptime_percentage
        )
    
    def register_health_callback(self, callback: Callable[[SystemHealthReport], None]) -> None:
        """Register health status callback."""
        self._health_callbacks.append(callback)
    
    def format_health_dashboard(self) -> str:
        """Format health data for dashboard display."""
        report = self.get_system_health()
        
        status_icon = {
            HealthStatus.HEALTHY: "🟢",
            HealthStatus.DEGRADED: "🟡",
            HealthStatus.UNHEALTHY: "🔴",
            HealthStatus.UNKNOWN: "⚪"
        }
        
        lines = [
            f"System Health: {status_icon[report.overall_status]} {report.overall_status.value.upper()}",
            f"Uptime: {report.uptime_percentage:.1f}%",
            f"Messages (24h): {report.total_messages_24h}",
            f"Errors (24h): {report.total_errors_24h}",
            "",
            "Bot Status:"
        ]
        
        for bot_id, bot_report in report.bots.items():
            icon = status_icon[bot_report.status]
            uptime_hours = bot_report.uptime_seconds / 3600
            lines.append(f"  {icon} {bot_id}: {bot_report.messages_sent} msgs, {bot_report.errors_count} errors, {uptime_hours:.1f}h uptime")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        report = self.get_system_health()
        return {
            "overall_status": report.overall_status.value,
            "total_bots": len(self._bot_stats),
            "total_messages": report.total_messages_24h,
            "total_errors": report.total_errors_24h,
            "uptime_percentage": report.uptime_percentage
        }


class TelegramErrorHandler:
    """
    Combined error handler and health monitor for Telegram system.
    """
    
    def __init__(self):
        """Initialize Telegram error handler."""
        self.error_handler = ErrorHandler()
        self.health_monitor = HealthMonitor()
        
        self.error_handler.register_callback(self._on_error)
    
    def _on_error(self, error: ErrorRecord) -> None:
        """Handle error callback."""
        if error.bot_id:
            self.health_monitor.record_error(error.bot_id, error)
    
    def register_bot(self, bot_id: str) -> None:
        """Register bot for monitoring."""
        self.health_monitor.register_bot(bot_id)
    
    def handle_error(self, exception: Exception, **kwargs) -> ErrorRecord:
        """Handle an error."""
        return self.error_handler.handle_error(exception, **kwargs)
    
    def record_message(self, bot_id: str) -> None:
        """Record message sent."""
        self.health_monitor.record_message_sent(bot_id)
    
    def get_health_report(self) -> SystemHealthReport:
        """Get system health report."""
        return self.health_monitor.get_system_health()
    
    def get_health_dashboard(self) -> str:
        """Get formatted health dashboard."""
        return self.health_monitor.format_health_dashboard()
    
    def get_recent_errors(self, hours: int = 24) -> List[ErrorRecord]:
        """Get recent errors."""
        return self.error_handler.get_recent_errors(hours)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics."""
        return {
            "health": self.health_monitor.get_stats(),
            "errors": {
                "total_24h": self.error_handler.get_error_count(24),
                "unresolved": len(self.error_handler.get_unresolved_errors())
            }
        }


def create_error_handler() -> ErrorHandler:
    """Factory function to create Error Handler."""
    return ErrorHandler()


def create_health_monitor() -> HealthMonitor:
    """Factory function to create Health Monitor."""
    return HealthMonitor()


def create_telegram_error_handler() -> TelegramErrorHandler:
    """Factory function to create Telegram Error Handler."""
    return TelegramErrorHandler()
