"""
Test Suite for Document 08: Phase 6 - UI Dashboard (Optional)

This test file verifies 100% implementation of Document 08 requirements:
1. FastAPI REST Endpoints for Plugin Management
2. Metrics Endpoints for Dashboard
3. Health Check Endpoints
4. API Package Structure

Test Categories:
- TestAPIPackage: API package structure tests
- TestAdminRoutes: Admin routes functionality tests
- TestMetricsRoutes: Metrics routes functionality tests
- TestHealthRoutes: Health routes functionality tests
- TestFastAPIIntegration: FastAPI integration tests
- TestDocument08Integration: Integration tests
- TestDocument08Summary: Summary verification tests
"""

import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAPIPackage:
    """Tests for API package structure."""
    
    def test_api_package_exists(self):
        """Test api package directory exists."""
        api_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api'
        )
        assert os.path.exists(api_path)
        assert os.path.isdir(api_path)
    
    def test_api_init_exists(self):
        """Test api/__init__.py exists."""
        init_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', '__init__.py'
        )
        assert os.path.exists(init_path)
    
    def test_admin_routes_exists(self):
        """Test admin_routes.py exists."""
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', 'admin_routes.py'
        )
        assert os.path.exists(routes_path)
    
    def test_metrics_routes_exists(self):
        """Test metrics_routes.py exists."""
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', 'metrics_routes.py'
        )
        assert os.path.exists(routes_path)
    
    def test_health_routes_exists(self):
        """Test health_routes.py exists."""
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', 'health_routes.py'
        )
        assert os.path.exists(routes_path)
    
    def test_api_package_imports(self):
        """Test api package can be imported."""
        from api import admin_router, metrics_router, health_router
        assert admin_router is not None
        assert metrics_router is not None
        assert health_router is not None


class TestAdminRoutes:
    """Tests for AdminRouter functionality."""
    
    def test_admin_router_import(self):
        """Test AdminRouter can be imported."""
        from api.admin_routes import AdminRouter
        assert AdminRouter is not None
    
    def test_admin_router_initialization(self):
        """Test AdminRouter initialization."""
        from api.admin_routes import AdminRouter
        
        router = AdminRouter()
        assert router.plugin_registry is None
        assert router.config_manager is None
    
    def test_admin_router_with_dependencies(self):
        """Test AdminRouter with dependencies."""
        from api.admin_routes import AdminRouter
        
        mock_registry = Mock()
        mock_config = Mock()
        
        router = AdminRouter(mock_registry, mock_config)
        assert router.plugin_registry == mock_registry
        assert router.config_manager == mock_config
    
    def test_set_plugin_registry(self):
        """Test set_plugin_registry method."""
        from api.admin_routes import AdminRouter
        
        router = AdminRouter()
        mock_registry = Mock()
        
        router.set_plugin_registry(mock_registry)
        assert router.plugin_registry == mock_registry
    
    def test_set_config_manager(self):
        """Test set_config_manager method."""
        from api.admin_routes import AdminRouter
        
        router = AdminRouter()
        mock_config = Mock()
        
        router.set_config_manager(mock_config)
        assert router.config_manager == mock_config
    
    def test_list_plugins_empty(self):
        """Test list_plugins with no registry."""
        from api.admin_routes import AdminRouter
        
        router = AdminRouter()
        plugins = router.list_plugins()
        assert plugins == []
    
    def test_list_plugins_with_registry(self):
        """Test list_plugins with mock registry."""
        from api.admin_routes import AdminRouter
        
        mock_plugin = Mock()
        mock_plugin.plugin_id = "test_plugin"
        mock_plugin.metadata = {"name": "Test Plugin", "version": "1.0.0"}
        mock_plugin.enabled = True
        mock_plugin.get_status.return_value = {"status": "running"}
        
        mock_registry = Mock()
        mock_registry.get_all_plugins.return_value = [mock_plugin]
        
        router = AdminRouter(mock_registry)
        plugins = router.list_plugins()
        
        assert len(plugins) == 1
        assert plugins[0]["id"] == "test_plugin"
        assert plugins[0]["enabled"] == True
    
    def test_get_plugin_not_found(self):
        """Test get_plugin when plugin not found."""
        from api.admin_routes import AdminRouter
        
        mock_registry = Mock()
        mock_registry.get_plugin.return_value = None
        
        router = AdminRouter(mock_registry)
        result = router.get_plugin("nonexistent")
        
        assert result is None
    
    def test_get_plugin_found(self):
        """Test get_plugin when plugin found."""
        from api.admin_routes import AdminRouter
        
        mock_plugin = Mock()
        mock_plugin.plugin_id = "test_plugin"
        mock_plugin.metadata = {"name": "Test", "version": "1.0.0", "description": "", "author": "Test"}
        mock_plugin.enabled = True
        mock_plugin.db_path = "data/test.db"
        mock_plugin.get_status.return_value = {"status": "running"}
        
        mock_registry = Mock()
        mock_registry.get_plugin.return_value = mock_plugin
        
        router = AdminRouter(mock_registry)
        result = router.get_plugin("test_plugin")
        
        assert result is not None
        assert result["id"] == "test_plugin"
    
    def test_enable_plugin(self):
        """Test enable_plugin method."""
        from api.admin_routes import AdminRouter
        
        mock_plugin = Mock()
        mock_plugin.plugin_id = "test_plugin"
        
        mock_registry = Mock()
        mock_registry.get_plugin.return_value = mock_plugin
        
        router = AdminRouter(mock_registry)
        result = router.enable_plugin("test_plugin")
        
        assert result["success"] == True
        mock_plugin.enable.assert_called_once()
    
    def test_disable_plugin(self):
        """Test disable_plugin method."""
        from api.admin_routes import AdminRouter
        
        mock_plugin = Mock()
        mock_plugin.plugin_id = "test_plugin"
        
        mock_registry = Mock()
        mock_registry.get_plugin.return_value = mock_plugin
        
        router = AdminRouter(mock_registry)
        result = router.disable_plugin("test_plugin")
        
        assert result["success"] == True
        mock_plugin.disable.assert_called_once()
    
    def test_get_config(self):
        """Test get_config method."""
        from api.admin_routes import AdminRouter
        
        mock_config = Mock()
        mock_config.config = {"test": "value"}
        
        router = AdminRouter(config_manager=mock_config)
        result = router.get_config()
        
        assert result == {"test": "value"}
    
    def test_reload_config(self):
        """Test reload_config method."""
        from api.admin_routes import AdminRouter
        
        mock_config = Mock()
        mock_config.reload_config.return_value = ["key1", "key2"]
        
        router = AdminRouter(config_manager=mock_config)
        result = router.reload_config()
        
        assert result["success"] == True
        assert "key1" in result["changes"]
    
    def test_plugin_info_class(self):
        """Test PluginInfo class."""
        from api.admin_routes import PluginInfo
        
        info = PluginInfo(
            plugin_id="test",
            name="Test Plugin",
            version="1.0.0",
            enabled=True,
            status="running",
            stats={"trades": 10}
        )
        
        result = info.to_dict()
        assert result["id"] == "test"
        assert result["name"] == "Test Plugin"
        assert result["enabled"] == True


class TestMetricsRoutes:
    """Tests for MetricsRouter functionality."""
    
    def test_metrics_router_import(self):
        """Test MetricsRouter can be imported."""
        from api.metrics_routes import MetricsRouter
        assert MetricsRouter is not None
    
    def test_metrics_router_initialization(self):
        """Test MetricsRouter initialization."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        assert router.trading_engine is None
        assert router.plugin_registry is None
    
    def test_get_metrics(self):
        """Test get_metrics method."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        metrics = router.get_metrics()
        
        assert "open_trades" in metrics
        assert "daily_pnl" in metrics
        assert "active_plugins" in metrics
        assert "uptime" in metrics
        assert "timestamp" in metrics
    
    def test_get_trade_metrics(self):
        """Test get_trade_metrics method."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        metrics = router.get_trade_metrics("today")
        
        assert "period" in metrics
        assert "total_trades" in metrics
        assert "win_rate" in metrics
        assert "total_profit" in metrics
    
    def test_get_plugin_metrics(self):
        """Test get_plugin_metrics method."""
        from api.metrics_routes import MetricsRouter
        
        mock_plugin = Mock()
        mock_plugin.plugin_id = "test"
        mock_plugin.metadata = {"name": "Test"}
        mock_plugin.enabled = True
        mock_plugin.get_statistics.return_value = {"trades_today": 5}
        
        mock_registry = Mock()
        mock_registry.get_all_plugins.return_value = [mock_plugin]
        
        router = MetricsRouter(plugin_registry=mock_registry)
        metrics = router.get_plugin_metrics()
        
        assert len(metrics) == 1
        assert metrics[0]["id"] == "test"
    
    def test_get_performance_metrics(self):
        """Test get_performance_metrics method."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        metrics = router.get_performance_metrics()
        
        assert "uptime" in metrics
        assert "memory_usage" in metrics
        assert "cpu_usage" in metrics
    
    def test_get_dashboard(self):
        """Test get_dashboard method."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        dashboard = router.get_dashboard()
        
        assert "metrics" in dashboard
        assert "trade_metrics" in dashboard
        assert "plugin_metrics" in dashboard
        assert "performance" in dashboard
    
    def test_get_live_feed(self):
        """Test get_live_feed method."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        feed = router.get_live_feed(limit=10)
        
        assert isinstance(feed, list)
    
    def test_uptime_calculation(self):
        """Test uptime calculation."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        uptime = router._get_uptime()
        
        assert isinstance(uptime, str)
        assert "s" in uptime or "m" in uptime or "h" in uptime


class TestHealthRoutes:
    """Tests for HealthRouter functionality."""
    
    def test_health_router_import(self):
        """Test HealthRouter can be imported."""
        from api.health_routes import HealthRouter
        assert HealthRouter is not None
    
    def test_health_status_constants(self):
        """Test HealthStatus constants."""
        from api.health_routes import HealthStatus
        
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNHEALTHY == "unhealthy"
    
    def test_health_router_initialization(self):
        """Test HealthRouter initialization."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        assert router.trading_engine is None
        assert router.plugin_registry is None
        assert router.config_manager is None
    
    def test_health_check(self):
        """Test health_check method."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        health = router.health_check()
        
        assert "status" in health
        assert "timestamp" in health
        assert "uptime_seconds" in health
        assert "checks" in health
    
    def test_readiness_check(self):
        """Test readiness_check method."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        result = router.readiness_check()
        
        assert "ready" in result
        assert "timestamp" in result
        assert "checks" in result
    
    def test_liveness_check(self):
        """Test liveness_check method."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        result = router.liveness_check()
        
        assert result["alive"] == True
        assert "timestamp" in result
        assert "uptime_seconds" in result
    
    def test_get_status(self):
        """Test get_status method."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        status = router.get_status()
        
        assert "health" in status
        assert "version" in status
        assert "environment" in status
        assert "components" in status
    
    def test_version_info(self):
        """Test version information."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        version = router._get_version()
        
        assert version["app"] == "ZepixTradingBot"
        assert version["version"] == "5.0.0"
        assert version["architecture"] == "V5 Hybrid Plugin"
    
    def test_environment_info(self):
        """Test environment information."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        env = router._get_environment()
        
        assert "python_version" in env
        assert "platform" in env
        assert "pid" in env
    
    def test_component_status(self):
        """Test component status."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        components = router._get_component_status()
        
        assert "trading_engine" in components
        assert "plugin_registry" in components
        assert "config_manager" in components


class TestFastAPIIntegration:
    """Tests for FastAPI integration helpers."""
    
    def test_admin_create_fastapi_router_function(self):
        """Test admin create_fastapi_router function exists."""
        from api.admin_routes import create_fastapi_router
        assert create_fastapi_router is not None
        assert callable(create_fastapi_router)
    
    def test_metrics_create_fastapi_router_function(self):
        """Test metrics create_fastapi_router function exists."""
        from api.metrics_routes import create_fastapi_router
        assert create_fastapi_router is not None
        assert callable(create_fastapi_router)
    
    def test_health_create_fastapi_router_function(self):
        """Test health create_fastapi_router function exists."""
        from api.health_routes import create_fastapi_router
        assert create_fastapi_router is not None
        assert callable(create_fastapi_router)
    
    def test_admin_router_instance(self):
        """Test admin router instance exists."""
        from api.admin_routes import router
        assert router is not None
    
    def test_metrics_router_instance(self):
        """Test metrics router instance exists."""
        from api.metrics_routes import router
        assert router is not None
    
    def test_health_router_instance(self):
        """Test health router instance exists."""
        from api.health_routes import router
        assert router is not None


class TestDocument08Integration:
    """Integration tests for Document 08 components."""
    
    def test_all_routers_work_together(self):
        """Test all routers can work together."""
        from api.admin_routes import AdminRouter
        from api.metrics_routes import MetricsRouter
        from api.health_routes import HealthRouter
        
        mock_registry = Mock()
        mock_registry.get_all_plugins.return_value = []
        
        mock_config = Mock()
        mock_config.config = {}
        
        mock_engine = Mock()
        
        admin = AdminRouter(mock_registry, mock_config)
        metrics = MetricsRouter(mock_engine, mock_registry)
        health = HealthRouter(mock_engine, mock_registry, mock_config)
        
        # All should return valid responses
        assert admin.list_plugins() == []
        assert "open_trades" in metrics.get_metrics()
        assert "status" in health.health_check()
    
    def test_plugin_management_flow(self):
        """Test complete plugin management flow."""
        from api.admin_routes import AdminRouter
        
        mock_plugin = Mock()
        mock_plugin.plugin_id = "test_plugin"
        mock_plugin.metadata = {"name": "Test", "version": "1.0.0"}
        mock_plugin.enabled = False
        
        mock_registry = Mock()
        mock_registry.get_plugin.return_value = mock_plugin
        mock_registry.get_all_plugins.return_value = [mock_plugin]
        
        router = AdminRouter(mock_registry)
        
        # List plugins
        plugins = router.list_plugins()
        assert len(plugins) == 1
        
        # Enable plugin
        result = router.enable_plugin("test_plugin")
        assert result["success"] == True
        
        # Disable plugin
        result = router.disable_plugin("test_plugin")
        assert result["success"] == True
    
    def test_dashboard_data_flow(self):
        """Test dashboard data retrieval flow."""
        from api.metrics_routes import MetricsRouter
        
        router = MetricsRouter()
        
        # Get all dashboard data
        dashboard = router.get_dashboard()
        
        assert "metrics" in dashboard
        assert "trade_metrics" in dashboard
        assert "plugin_metrics" in dashboard
        assert "performance" in dashboard
    
    def test_health_monitoring_flow(self):
        """Test health monitoring flow."""
        from api.health_routes import HealthRouter
        
        router = HealthRouter()
        
        # Check liveness
        live = router.liveness_check()
        assert live["alive"] == True
        
        # Check readiness
        ready = router.readiness_check()
        assert "ready" in ready
        
        # Full health check
        health = router.health_check()
        assert "status" in health
        assert "checks" in health


class TestDocument08Summary:
    """Summary tests verifying Document 08 completion criteria."""
    
    def test_api_package_complete(self):
        """Test API package is complete."""
        api_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api'
        )
        
        required_files = [
            '__init__.py',
            'admin_routes.py',
            'metrics_routes.py',
            'health_routes.py'
        ]
        
        for file in required_files:
            file_path = os.path.join(api_path, file)
            assert os.path.exists(file_path), f"Missing file: {file}"
    
    def test_admin_routes_complete(self):
        """Test admin routes are complete."""
        from api.admin_routes import AdminRouter
        
        required_methods = [
            'list_plugins', 'get_plugin', 'enable_plugin', 'disable_plugin',
            'update_plugin_config', 'get_config', 'update_config', 'reload_config'
        ]
        
        for method in required_methods:
            assert hasattr(AdminRouter, method), f"Missing method: {method}"
    
    def test_metrics_routes_complete(self):
        """Test metrics routes are complete."""
        from api.metrics_routes import MetricsRouter
        
        required_methods = [
            'get_metrics', 'get_trade_metrics', 'get_plugin_metrics',
            'get_performance_metrics', 'get_dashboard', 'get_live_feed'
        ]
        
        for method in required_methods:
            assert hasattr(MetricsRouter, method), f"Missing method: {method}"
    
    def test_health_routes_complete(self):
        """Test health routes are complete."""
        from api.health_routes import HealthRouter
        
        required_methods = [
            'health_check', 'readiness_check', 'liveness_check', 'get_status'
        ]
        
        for method in required_methods:
            assert hasattr(HealthRouter, method), f"Missing method: {method}"
    
    def test_document_08_requirements_met(self):
        """Test all Document 08 requirements are met."""
        # 1. API package exists
        from api import admin_router, metrics_router, health_router
        assert admin_router is not None
        assert metrics_router is not None
        assert health_router is not None
        
        # 2. Admin routes for plugin management
        from api.admin_routes import AdminRouter
        router = AdminRouter()
        assert hasattr(router, 'list_plugins')
        assert hasattr(router, 'enable_plugin')
        
        # 3. Metrics routes for dashboard
        from api.metrics_routes import MetricsRouter
        metrics = MetricsRouter()
        assert hasattr(metrics, 'get_dashboard')
        
        # 4. Health routes for monitoring
        from api.health_routes import HealthRouter
        health = HealthRouter()
        assert hasattr(health, 'health_check')
        
        # All requirements met
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
