"""
API Package - FastAPI REST Endpoints for Bot Management

Document 08: Phase 6 - UI Dashboard (Optional)
Provides REST API endpoints for plugin management, metrics, and configuration.

Modules:
- admin_routes: Plugin management endpoints (/admin/plugins, /admin/config)
- metrics_routes: System metrics endpoints (/metrics, /dashboard)
- health_routes: Health check endpoints (/health, /status)
"""

from .admin_routes import router as admin_router
from .metrics_routes import router as metrics_router
from .health_routes import router as health_router

__all__ = [
    'admin_router',
    'metrics_router', 
    'health_router'
]
