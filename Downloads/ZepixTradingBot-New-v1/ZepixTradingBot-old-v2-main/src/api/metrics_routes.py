"""
Metrics Routes - FastAPI REST Endpoints for System Metrics

Document 08: Phase 6 - UI Dashboard (Optional)
Provides REST API endpoints for real-time metrics and dashboard data.

Endpoints:
- GET /metrics - Get system metrics
- GET /metrics/trades - Get trade metrics
- GET /metrics/plugins - Get plugin metrics
- GET /metrics/performance - Get performance metrics
- GET /dashboard - Get dashboard summary data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


class MetricsRouter:
    """
    Metrics router for system metrics endpoints.
    
    This class provides REST API endpoints for real-time metrics
    and dashboard data without requiring FastAPI as a dependency.
    
    Usage with FastAPI:
        from fastapi import APIRouter
        from api.metrics_routes import MetricsRouter
        
        metrics = MetricsRouter(trading_engine, plugin_registry)
        router = APIRouter(prefix="/metrics")
        
        @router.get("/")
        async def get_metrics():
            return metrics.get_metrics()
    """
    
    def __init__(self, trading_engine=None, plugin_registry=None):
        """
        Initialize MetricsRouter.
        
        Args:
            trading_engine: TradingEngine instance for trade data
            plugin_registry: PluginRegistry instance for plugin data
        """
        self.trading_engine = trading_engine
        self.plugin_registry = plugin_registry
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)
    
    def set_trading_engine(self, engine) -> None:
        """Set the trading engine."""
        self.trading_engine = engine
    
    def set_plugin_registry(self, registry) -> None:
        """Set the plugin registry."""
        self.plugin_registry = registry
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Returns system metrics.
        
        Endpoint: GET /metrics
        
        Returns:
            System metrics dictionary
        """
        return {
            "open_trades": self._get_open_trades_count(),
            "daily_pnl": self._get_daily_pnl(),
            "active_plugins": self._get_active_plugins_count(),
            "uptime": self._get_uptime(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_open_trades_count(self) -> int:
        """Get count of open trades."""
        if self.trading_engine:
            try:
                if hasattr(self.trading_engine, 'get_open_trades_count'):
                    return self.trading_engine.get_open_trades_count()
                elif hasattr(self.trading_engine, 'open_trades'):
                    return len(self.trading_engine.open_trades)
            except:
                pass
        return 0
    
    def _get_daily_pnl(self) -> float:
        """Get daily P&L."""
        if self.trading_engine:
            try:
                if hasattr(self.trading_engine, 'get_daily_pnl'):
                    return self.trading_engine.get_daily_pnl()
                elif hasattr(self.trading_engine, 'daily_pnl'):
                    return self.trading_engine.daily_pnl
            except:
                pass
        return 0.0
    
    def _get_active_plugins_count(self) -> int:
        """Get count of active plugins."""
        if self.plugin_registry:
            try:
                if hasattr(self.plugin_registry, 'get_active_count'):
                    return self.plugin_registry.get_active_count()
                elif hasattr(self.plugin_registry, 'get_all_plugins'):
                    plugins = self.plugin_registry.get_all_plugins()
                    return sum(1 for p in plugins if p.enabled)
            except:
                pass
        return 0
    
    def _get_uptime(self) -> str:
        """Get system uptime."""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    def get_trade_metrics(self, period: str = "today") -> Dict[str, Any]:
        """
        Get trade metrics for a period.
        
        Endpoint: GET /metrics/trades
        
        Args:
            period: Time period (today, week, month, all)
            
        Returns:
            Trade metrics dictionary
        """
        metrics = {
            "period": period,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_profit": 0.0,
            "total_pips": 0.0,
            "average_profit": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.trading_engine:
            return metrics
        
        try:
            # Get trades for period
            trades = self._get_trades_for_period(period)
            
            if trades:
                metrics["total_trades"] = len(trades)
                
                winning = [t for t in trades if t.get("profit", 0) > 0]
                losing = [t for t in trades if t.get("profit", 0) < 0]
                
                metrics["winning_trades"] = len(winning)
                metrics["losing_trades"] = len(losing)
                
                if metrics["total_trades"] > 0:
                    metrics["win_rate"] = round(
                        len(winning) / metrics["total_trades"] * 100, 2
                    )
                
                profits = [t.get("profit", 0) for t in trades]
                metrics["total_profit"] = round(sum(profits), 2)
                metrics["average_profit"] = round(
                    metrics["total_profit"] / metrics["total_trades"], 2
                ) if metrics["total_trades"] > 0 else 0
                
                if winning:
                    metrics["largest_win"] = round(max(t.get("profit", 0) for t in winning), 2)
                if losing:
                    metrics["largest_loss"] = round(min(t.get("profit", 0) for t in losing), 2)
                
                pips = [t.get("pips", 0) for t in trades]
                metrics["total_pips"] = round(sum(pips), 1)
                
        except Exception as e:
            self.logger.error(f"Error getting trade metrics: {e}")
        
        return metrics
    
    def _get_trades_for_period(self, period: str) -> List[Dict[str, Any]]:
        """Get trades for a specific period."""
        if not self.trading_engine:
            return []
        
        try:
            # Calculate date range
            today = date.today()
            
            if period == "today":
                start_date = today
            elif period == "week":
                start_date = today - timedelta(days=7)
            elif period == "month":
                start_date = today - timedelta(days=30)
            else:  # all
                start_date = None
            
            # Get trades from engine
            if hasattr(self.trading_engine, 'get_closed_trades'):
                return self.trading_engine.get_closed_trades(
                    start_date=start_date.isoformat() if start_date else None
                )
            
        except Exception as e:
            self.logger.error(f"Error getting trades for period: {e}")
        
        return []
    
    def get_plugin_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics for all plugins.
        
        Endpoint: GET /metrics/plugins
        
        Returns:
            List of plugin metrics dictionaries
        """
        metrics = []
        
        if not self.plugin_registry:
            return metrics
        
        try:
            plugins = self.plugin_registry.get_all_plugins()
            
            for plugin in plugins:
                plugin_metrics = {
                    "id": plugin.plugin_id,
                    "name": plugin.metadata.get("name", plugin.plugin_id),
                    "enabled": plugin.enabled,
                    "trades_today": 0,
                    "pnl_today": 0.0,
                    "win_rate": 0.0,
                    "status": "running" if plugin.enabled else "stopped"
                }
                
                # Get plugin-specific stats
                if hasattr(plugin, 'get_statistics'):
                    stats = plugin.get_statistics()
                    plugin_metrics.update({
                        "trades_today": stats.get("trades_today", 0),
                        "pnl_today": stats.get("pnl_today", 0.0),
                        "win_rate": stats.get("win_rate", 0.0)
                    })
                
                metrics.append(plugin_metrics)
                
        except Exception as e:
            self.logger.error(f"Error getting plugin metrics: {e}")
        
        return metrics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Endpoint: GET /metrics/performance
        
        Returns:
            Performance metrics dictionary
        """
        return {
            "uptime": self._get_uptime(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "memory_usage": self._get_memory_usage(),
            "cpu_usage": self._get_cpu_usage(),
            "active_connections": self._get_active_connections(),
            "requests_per_minute": self._get_requests_per_minute(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        try:
            import psutil
            process = psutil.Process()
            memory = process.memory_info()
            return {
                "rss_mb": round(memory.rss / 1024 / 1024, 2),
                "vms_mb": round(memory.vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2)
            }
        except ImportError:
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}
        except:
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            import psutil
            return psutil.Process().cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def _get_active_connections(self) -> int:
        """Get count of active connections."""
        # Placeholder - would need actual connection tracking
        return 0
    
    def _get_requests_per_minute(self) -> float:
        """Get requests per minute."""
        # Placeholder - would need actual request tracking
        return 0.0
    
    def get_dashboard(self) -> Dict[str, Any]:
        """
        Get dashboard summary data.
        
        Endpoint: GET /dashboard
        
        Returns:
            Dashboard summary dictionary
        """
        return {
            "metrics": self.get_metrics(),
            "trade_metrics": self.get_trade_metrics("today"),
            "plugin_metrics": self.get_plugin_metrics(),
            "performance": self.get_performance_metrics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_live_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get live trade feed.
        
        Endpoint: GET /dashboard/feed
        
        Args:
            limit: Maximum number of trades to return
            
        Returns:
            List of recent trade dictionaries
        """
        trades = []
        
        if not self.trading_engine:
            return trades
        
        try:
            if hasattr(self.trading_engine, 'get_recent_trades'):
                trades = self.trading_engine.get_recent_trades(limit)
            elif hasattr(self.trading_engine, 'trade_history'):
                trades = list(self.trading_engine.trade_history)[-limit:]
        except Exception as e:
            self.logger.error(f"Error getting live feed: {e}")
        
        return trades


# Create default router instance
router = MetricsRouter()


# FastAPI integration helper
def create_fastapi_router(trading_engine=None, plugin_registry=None):
    """
    Create FastAPI router with metrics endpoints.
    
    Usage:
        from fastapi import FastAPI
        from api.metrics_routes import create_fastapi_router
        
        app = FastAPI()
        metrics_router = create_fastapi_router(trading_engine, plugin_registry)
        app.include_router(metrics_router, prefix="/metrics")
    """
    try:
        from fastapi import APIRouter, Query
        
        metrics = MetricsRouter(trading_engine, plugin_registry)
        api_router = APIRouter()
        
        @api_router.get("/")
        async def get_metrics():
            return metrics.get_metrics()
        
        @api_router.get("/trades")
        async def get_trade_metrics(period: str = Query("today", enum=["today", "week", "month", "all"])):
            return metrics.get_trade_metrics(period)
        
        @api_router.get("/plugins")
        async def get_plugin_metrics():
            return metrics.get_plugin_metrics()
        
        @api_router.get("/performance")
        async def get_performance_metrics():
            return metrics.get_performance_metrics()
        
        @api_router.get("/dashboard")
        async def get_dashboard():
            return metrics.get_dashboard()
        
        @api_router.get("/feed")
        async def get_live_feed(limit: int = Query(10, ge=1, le=100)):
            return metrics.get_live_feed(limit)
        
        return api_router
        
    except ImportError:
        logger.warning("FastAPI not installed, cannot create FastAPI router")
        return None
