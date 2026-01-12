"""
Notification Stats - Statistics and Analytics

Document 19: Notification System Specification
Tracks notification metrics and provides analytics.

Features:
- Total notifications sent
- By type breakdown
- By priority breakdown
- By bot breakdown
- Voice alerts tracking
- Failed notifications tracking
- Time-based analytics
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class NotificationMetric:
    """Single notification metric"""
    notification_type: str
    priority: str
    target_bot: str
    success: bool
    voice_sent: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    delivery_time_ms: float = 0.0
    user_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "notification_type": self.notification_type,
            "priority": self.priority,
            "target_bot": self.target_bot,
            "success": self.success,
            "voice_sent": self.voice_sent,
            "timestamp": self.timestamp.isoformat(),
            "delivery_time_ms": self.delivery_time_ms,
            "user_id": self.user_id
        }


@dataclass
class HourlyStats:
    """Hourly statistics"""
    hour: int
    total: int = 0
    successful: int = 0
    failed: int = 0
    voice_alerts: int = 0
    avg_delivery_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "hour": self.hour,
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "voice_alerts": self.voice_alerts,
            "avg_delivery_time_ms": self.avg_delivery_time_ms
        }


@dataclass
class DailyStats:
    """Daily statistics"""
    date: str
    total: int = 0
    successful: int = 0
    failed: int = 0
    voice_alerts: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_priority: Dict[str, int] = field(default_factory=dict)
    by_bot: Dict[str, int] = field(default_factory=dict)
    avg_delivery_time_ms: float = 0.0
    peak_hour: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "date": self.date,
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "voice_alerts": self.voice_alerts,
            "by_type": self.by_type,
            "by_priority": self.by_priority,
            "by_bot": self.by_bot,
            "avg_delivery_time_ms": self.avg_delivery_time_ms,
            "peak_hour": self.peak_hour
        }


class NotificationStats:
    """
    Notification Statistics Tracker
    
    Tracks all notification metrics for analytics and monitoring.
    """
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        
        # Core counters
        self.total_sent = 0
        self.total_successful = 0
        self.total_failed = 0
        self.voice_alerts_sent = 0
        
        # Breakdown counters
        self.by_type: Dict[str, int] = defaultdict(int)
        self.by_priority: Dict[str, int] = defaultdict(int)
        self.by_bot: Dict[str, int] = defaultdict(int)
        
        # Detailed history
        self.history: List[NotificationMetric] = []
        
        # Time-based tracking
        self.hourly_stats: Dict[int, HourlyStats] = {}
        self.daily_stats: Dict[str, DailyStats] = {}
        
        # Delivery time tracking
        self._delivery_times: List[float] = []
        self._max_delivery_times = 1000
        
        # Session tracking
        self.session_start = datetime.now()
    
    def record(
        self,
        notification_type: str,
        priority: Any,
        target_bot: str,
        success: bool,
        voice_sent: bool = False,
        delivery_time_ms: float = 0.0,
        user_id: Optional[int] = None
    ) -> None:
        """
        Record a notification metric
        
        Args:
            notification_type: Type of notification
            priority: Priority level (enum or string)
            target_bot: Target bot name
            success: Whether delivery was successful
            voice_sent: Whether voice alert was sent
            delivery_time_ms: Delivery time in milliseconds
            user_id: Optional user ID
        """
        # Convert priority to string if enum
        priority_str = priority.name if hasattr(priority, 'name') else str(priority)
        
        # Update counters
        self.total_sent += 1
        if success:
            self.total_successful += 1
        else:
            self.total_failed += 1
        
        if voice_sent:
            self.voice_alerts_sent += 1
        
        # Update breakdowns
        self.by_type[notification_type] += 1
        self.by_priority[priority_str] += 1
        self.by_bot[target_bot] += 1
        
        # Track delivery time
        if delivery_time_ms > 0:
            self._delivery_times.append(delivery_time_ms)
            if len(self._delivery_times) > self._max_delivery_times:
                self._delivery_times = self._delivery_times[-self._max_delivery_times:]
        
        # Create metric
        metric = NotificationMetric(
            notification_type=notification_type,
            priority=priority_str,
            target_bot=target_bot,
            success=success,
            voice_sent=voice_sent,
            delivery_time_ms=delivery_time_ms,
            user_id=user_id
        )
        
        # Add to history
        self.history.append(metric)
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
        
        # Update time-based stats
        self._update_hourly_stats(metric)
        self._update_daily_stats(metric)
    
    def _update_hourly_stats(self, metric: NotificationMetric) -> None:
        """Update hourly statistics"""
        hour = metric.timestamp.hour
        
        if hour not in self.hourly_stats:
            self.hourly_stats[hour] = HourlyStats(hour=hour)
        
        stats = self.hourly_stats[hour]
        stats.total += 1
        if metric.success:
            stats.successful += 1
        else:
            stats.failed += 1
        if metric.voice_sent:
            stats.voice_alerts += 1
        
        # Update average delivery time
        if metric.delivery_time_ms > 0:
            current_total = stats.avg_delivery_time_ms * (stats.total - 1)
            stats.avg_delivery_time_ms = (current_total + metric.delivery_time_ms) / stats.total
    
    def _update_daily_stats(self, metric: NotificationMetric) -> None:
        """Update daily statistics"""
        date_str = metric.timestamp.strftime("%Y-%m-%d")
        
        if date_str not in self.daily_stats:
            self.daily_stats[date_str] = DailyStats(date=date_str)
        
        stats = self.daily_stats[date_str]
        stats.total += 1
        if metric.success:
            stats.successful += 1
        else:
            stats.failed += 1
        if metric.voice_sent:
            stats.voice_alerts += 1
        
        # Update breakdowns
        stats.by_type[metric.notification_type] = stats.by_type.get(metric.notification_type, 0) + 1
        stats.by_priority[metric.priority] = stats.by_priority.get(metric.priority, 0) + 1
        stats.by_bot[metric.target_bot] = stats.by_bot.get(metric.target_bot, 0) + 1
        
        # Update average delivery time
        if metric.delivery_time_ms > 0:
            current_total = stats.avg_delivery_time_ms * (stats.total - 1)
            stats.avg_delivery_time_ms = (current_total + metric.delivery_time_ms) / stats.total
    
    def get_summary(self) -> Dict[str, Any]:
        """Get statistics summary"""
        success_rate = 0.0
        if self.total_sent > 0:
            success_rate = (self.total_successful / self.total_sent) * 100
        
        avg_delivery_time = 0.0
        if self._delivery_times:
            avg_delivery_time = sum(self._delivery_times) / len(self._delivery_times)
        
        return {
            "total_sent": self.total_sent,
            "successful": self.total_successful,
            "failed": self.total_failed,
            "success_rate": success_rate,
            "voice_alerts_sent": self.voice_alerts_sent,
            "by_type": dict(self.by_type),
            "by_priority": dict(self.by_priority),
            "by_bot": dict(self.by_bot),
            "avg_delivery_time_ms": avg_delivery_time,
            "session_duration_seconds": (datetime.now() - self.session_start).total_seconds()
        }
    
    def get_hourly_breakdown(self) -> List[Dict[str, Any]]:
        """Get hourly statistics breakdown"""
        return [
            self.hourly_stats[hour].to_dict()
            for hour in sorted(self.hourly_stats.keys())
        ]
    
    def get_daily_breakdown(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily statistics for last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        
        return [
            stats.to_dict()
            for date_str, stats in sorted(self.daily_stats.items())
            if date_str >= cutoff_str
        ]
    
    def get_top_notification_types(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top notification types by count"""
        sorted_types = sorted(
            self.by_type.items(),
            key=lambda x: -x[1]
        )[:limit]
        
        return [
            {"type": t, "count": c, "percentage": (c / self.total_sent * 100) if self.total_sent > 0 else 0}
            for t, c in sorted_types
        ]
    
    def get_recent_failures(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent failed notifications"""
        failures = [m for m in self.history if not m.success]
        return [f.to_dict() for f in failures[-limit:]]
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        return [m.to_dict() for m in self.history[-limit:]]
    
    def reset(self) -> None:
        """Reset all statistics"""
        self.total_sent = 0
        self.total_successful = 0
        self.total_failed = 0
        self.voice_alerts_sent = 0
        self.by_type.clear()
        self.by_priority.clear()
        self.by_bot.clear()
        self.history.clear()
        self.hourly_stats.clear()
        self.daily_stats.clear()
        self._delivery_times.clear()
        self.session_start = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export all statistics as dictionary"""
        return {
            "summary": self.get_summary(),
            "hourly": self.get_hourly_breakdown(),
            "daily": self.get_daily_breakdown(),
            "top_types": self.get_top_notification_types(),
            "recent_failures": self.get_recent_failures()
        }


class StatsAggregator:
    """
    Statistics Aggregator
    
    Aggregates statistics from multiple sources and provides unified reporting.
    """
    
    def __init__(self):
        self.notification_stats = NotificationStats()
        self.custom_metrics: Dict[str, Any] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.max_alerts = 100
    
    def record_notification(
        self,
        notification_type: str,
        priority: Any,
        target_bot: str,
        success: bool,
        **kwargs
    ) -> None:
        """Record notification metric"""
        self.notification_stats.record(
            notification_type=notification_type,
            priority=priority,
            target_bot=target_bot,
            success=success,
            **kwargs
        )
    
    def record_custom_metric(self, name: str, value: Any) -> None:
        """Record custom metric"""
        self.custom_metrics[name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_alert(self, alert_type: str, message: str, severity: str = "info") -> None:
        """Add monitoring alert"""
        self.alerts.append({
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
    
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check for threshold violations"""
        violations = []
        summary = self.notification_stats.get_summary()
        
        # Check failure rate
        if summary["total_sent"] > 100:
            failure_rate = 100 - summary["success_rate"]
            if failure_rate > 10:
                violations.append({
                    "metric": "failure_rate",
                    "value": failure_rate,
                    "threshold": 10,
                    "severity": "high" if failure_rate > 20 else "medium"
                })
        
        # Check delivery time
        if summary["avg_delivery_time_ms"] > 5000:
            violations.append({
                "metric": "avg_delivery_time",
                "value": summary["avg_delivery_time_ms"],
                "threshold": 5000,
                "severity": "medium"
            })
        
        return violations
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        summary = self.notification_stats.get_summary()
        
        return {
            "summary": summary,
            "hourly_chart": self.notification_stats.get_hourly_breakdown(),
            "daily_chart": self.notification_stats.get_daily_breakdown(),
            "top_types": self.notification_stats.get_top_notification_types(5),
            "recent_failures": self.notification_stats.get_recent_failures(10),
            "custom_metrics": self.custom_metrics,
            "alerts": self.alerts[-10:],
            "threshold_violations": self.check_thresholds(),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_report(self, period: str = "daily") -> Dict[str, Any]:
        """Generate statistics report"""
        summary = self.notification_stats.get_summary()
        
        report = {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "highlights": []
        }
        
        # Add highlights
        if summary["total_sent"] > 0:
            report["highlights"].append(
                f"Total notifications: {summary['total_sent']}"
            )
            report["highlights"].append(
                f"Success rate: {summary['success_rate']:.1f}%"
            )
            
            if summary["voice_alerts_sent"] > 0:
                report["highlights"].append(
                    f"Voice alerts: {summary['voice_alerts_sent']}"
                )
            
            # Top notification type
            top_types = self.notification_stats.get_top_notification_types(1)
            if top_types:
                report["highlights"].append(
                    f"Most common: {top_types[0]['type']} ({top_types[0]['count']})"
                )
        
        # Add breakdown
        if period == "daily":
            report["breakdown"] = self.notification_stats.get_daily_breakdown(1)
        elif period == "weekly":
            report["breakdown"] = self.notification_stats.get_daily_breakdown(7)
        elif period == "hourly":
            report["breakdown"] = self.notification_stats.get_hourly_breakdown()
        
        return report
    
    def reset_all(self) -> None:
        """Reset all statistics"""
        self.notification_stats.reset()
        self.custom_metrics.clear()
        self.alerts.clear()
