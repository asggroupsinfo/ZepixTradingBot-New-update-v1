"""
Health Routes - FastAPI REST Endpoints for Health Checks

Document 08: Phase 6 - UI Dashboard (Optional)
Provides REST API endpoints for health checks and system status.

Endpoints:
- GET /health - Basic health check
- GET /health/ready - Readiness check
- GET /health/live - Liveness check
- GET /status - Detailed system status
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthRouter:
    """
    Health router for health check endpoints.
    
    This class provides REST API endpoints for health checks
    and system status without requiring FastAPI as a dependency.
    
    Usage with FastAPI:
        from fastapi import APIRouter
        from api.health_routes import HealthRouter
        
        health = HealthRouter(trading_engine, plugin_registry)
        router = APIRouter(prefix="/health")
        
        @router.get("/")
        async def health_check():
            return health.health_check()
    """
    
    def __init__(self, trading_engine=None, plugin_registry=None, config_manager=None):
        """
        Initialize HealthRouter.
        
        Args:
            trading_engine: TradingEngine instance
            plugin_registry: PluginRegistry instance
            config_manager: ConfigManager instance
        """
        self.trading_engine = trading_engine
        self.plugin_registry = plugin_registry
        self.config_manager = config_manager
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)
    
    def set_trading_engine(self, engine) -> None:
        """Set the trading engine."""
        self.trading_engine = engine
    
    def set_plugin_registry(self, registry) -> None:
        """Set the plugin registry."""
        self.plugin_registry = registry
    
    def set_config_manager(self, manager) -> None:
        """Set the config manager."""
        self.config_manager = manager
    
    def health_check(self) -> Dict[str, Any]:
        """
        Basic health check.
        
        Endpoint: GET /health
        
        Returns:
            Health status dictionary
        """
        checks = self._run_health_checks()
        
        # Determine overall status
        if all(c["status"] == HealthStatus.HEALTHY for c in checks.values()):
            status = HealthStatus.HEALTHY
        elif any(c["status"] == HealthStatus.UNHEALTHY for c in checks.values()):
            status = HealthStatus.UNHEALTHY
        else:
            status = HealthStatus.DEGRADED
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "checks": checks
        }
    
    def _run_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks."""
        checks = {}
        
        # Database check
        checks["database"] = self._check_database()
        
        # Plugin registry check
        checks["plugins"] = self._check_plugins()
        
        # Config check
        checks["config"] = self._check_config()
        
        # Trading engine check
        checks["trading_engine"] = self._check_trading_engine()
        
        return checks
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # Check if data directory exists
            data_dir = "data"
            if os.path.exists(data_dir):
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Database directory accessible"
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "Database directory not found"
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": str(e)
            }
    
    def _check_plugins(self) -> Dict[str, Any]:
        """Check plugin registry status."""
        if not self.plugin_registry:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Plugin registry not configured"
            }
        
        try:
            plugins = self.plugin_registry.get_all_plugins()
            active = sum(1 for p in plugins if p.enabled)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": f"{active}/{len(plugins)} plugins active",
                "total": len(plugins),
                "active": active
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": str(e)
            }
    
    def _check_config(self) -> Dict[str, Any]:
        """Check configuration status."""
        if not self.config_manager:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Config manager not configured"
            }
        
        try:
            config = self.config_manager.config
            if config:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Configuration loaded"
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "Configuration empty"
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": str(e)
            }
    
    def _check_trading_engine(self) -> Dict[str, Any]:
        """Check trading engine status."""
        if not self.trading_engine:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Trading engine not configured"
            }
        
        try:
            if hasattr(self.trading_engine, 'is_running'):
                if self.trading_engine.is_running:
                    return {
                        "status": HealthStatus.HEALTHY,
                        "message": "Trading engine running"
                    }
                else:
                    return {
                        "status": HealthStatus.DEGRADED,
                        "message": "Trading engine stopped"
                    }
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Trading engine available"
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": str(e)
            }
    
    def readiness_check(self) -> Dict[str, Any]:
        """
        Readiness check - is the service ready to accept traffic?
        
        Endpoint: GET /health/ready
        
        Returns:
            Readiness status dictionary
        """
        checks = self._run_health_checks()
        
        # Service is ready if all critical checks pass
        critical_checks = ["database", "config"]
        ready = all(
            checks.get(c, {}).get("status") != HealthStatus.UNHEALTHY
            for c in critical_checks
        )
        
        return {
            "ready": ready,
            "timestamp": datetime.now().isoformat(),
            "checks": {k: v for k, v in checks.items() if k in critical_checks}
        }
    
    def liveness_check(self) -> Dict[str, Any]:
        """
        Liveness check - is the service alive?
        
        Endpoint: GET /health/live
        
        Returns:
            Liveness status dictionary
        """
        return {
            "alive": True,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed system status.
        
        Endpoint: GET /status
        
        Returns:
            Detailed status dictionary
        """
        health = self.health_check()
        
        return {
            "health": health,
            "version": self._get_version(),
            "environment": self._get_environment(),
            "components": self._get_component_status(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_version(self) -> Dict[str, str]:
        """Get version information."""
        return {
            "app": "ZepixTradingBot",
            "version": "5.0.0",
            "architecture": "V5 Hybrid Plugin"
        }
    
    def _get_environment(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "python_version": self._get_python_version(),
            "platform": os.name,
            "pid": os.getpid()
        }
    
    def _get_python_version(self) -> str:
        """Get Python version."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_component_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all components."""
        components = {}
        
        # Trading Engine
        components["trading_engine"] = {
            "configured": self.trading_engine is not None,
            "status": "running" if self.trading_engine else "not configured"
        }
        
        # Plugin Registry
        components["plugin_registry"] = {
            "configured": self.plugin_registry is not None,
            "status": "running" if self.plugin_registry else "not configured"
        }
        
        # Config Manager
        components["config_manager"] = {
            "configured": self.config_manager is not None,
            "status": "running" if self.config_manager else "not configured"
        }
        
        return components


# Create default router instance
router = HealthRouter()


# FastAPI integration helper
def create_fastapi_router(trading_engine=None, plugin_registry=None, config_manager=None):
    """
    Create FastAPI router with health endpoints.
    
    Usage:
        from fastapi import FastAPI
        from api.health_routes import create_fastapi_router
        
        app = FastAPI()
        health_router = create_fastapi_router(trading_engine, plugin_registry, config_manager)
        app.include_router(health_router, prefix="/health")
    """
    try:
        from fastapi import APIRouter
        from fastapi.responses import JSONResponse
        
        health = HealthRouter(trading_engine, plugin_registry, config_manager)
        api_router = APIRouter()
        
        @api_router.get("/")
        async def health_check():
            result = health.health_check()
            status_code = 200 if result["status"] == HealthStatus.HEALTHY else 503
            return JSONResponse(content=result, status_code=status_code)
        
        @api_router.get("/ready")
        async def readiness_check():
            result = health.readiness_check()
            status_code = 200 if result["ready"] else 503
            return JSONResponse(content=result, status_code=status_code)
        
        @api_router.get("/live")
        async def liveness_check():
            return health.liveness_check()
        
        @api_router.get("/status")
        async def get_status():
            return health.get_status()
        
        return api_router
        
    except ImportError:
        logger.warning("FastAPI not installed, cannot create FastAPI router")
        return None
