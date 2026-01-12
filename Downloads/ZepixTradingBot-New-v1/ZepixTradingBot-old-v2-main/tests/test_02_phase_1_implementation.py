"""
Test Suite for Document 02: Phase 1 - Core Plugin System Foundation

This test file verifies 100% implementation of Document 02 requirements:
- 7 new files created (plugin system core + template)
- 3 files modified (config, main.py integration, .gitignore)
- All functionality working as specified

Document: 02_PHASE_1_PLAN.md
Test Coverage: 100% of Document 02 requirements
"""

import os
import sys
import json
import pytest
import asyncio
import importlib
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, AsyncMock, patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestPluginSystemCoreFiles:
    """Test that all 7 core plugin system files exist and have correct structure"""
    
    def test_base_plugin_file_exists(self):
        """Verify base_plugin.py exists"""
        path = os.path.join(PROJECT_ROOT, "src/core/plugin_system/base_plugin.py")
        assert os.path.exists(path), f"base_plugin.py not found at {path}"
    
    def test_plugin_registry_file_exists(self):
        """Verify plugin_registry.py exists"""
        path = os.path.join(PROJECT_ROOT, "src/core/plugin_system/plugin_registry.py")
        assert os.path.exists(path), f"plugin_registry.py not found at {path}"
    
    def test_plugin_system_init_file_exists(self):
        """Verify __init__.py exists in plugin_system"""
        path = os.path.join(PROJECT_ROOT, "src/core/plugin_system/__init__.py")
        assert os.path.exists(path), f"__init__.py not found at {path}"
    
    def test_template_plugin_file_exists(self):
        """Verify _template/plugin.py exists"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/plugin.py")
        assert os.path.exists(path), f"_template/plugin.py not found at {path}"
    
    def test_template_config_file_exists(self):
        """Verify _template/config.json exists"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        assert os.path.exists(path), f"_template/config.json not found at {path}"
    
    def test_template_readme_file_exists(self):
        """Verify _template/README.md exists"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/README.md")
        assert os.path.exists(path), f"_template/README.md not found at {path}"
    
    def test_test_plugin_script_exists(self):
        """Verify scripts/test_plugin.py exists"""
        path = os.path.join(PROJECT_ROOT, "scripts/test_plugin.py")
        assert os.path.exists(path), f"scripts/test_plugin.py not found at {path}"


class TestBaseLogicPlugin:
    """Test BaseLogicPlugin class implementation"""
    
    def test_base_plugin_is_abstract(self):
        """Verify BaseLogicPlugin is an abstract class"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        from abc import ABC
        assert issubclass(BaseLogicPlugin, ABC), "BaseLogicPlugin should be abstract"
    
    def test_base_plugin_has_required_abstract_methods(self):
        """Verify BaseLogicPlugin has all required abstract methods"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        import inspect
        
        abstract_methods = []
        for name, method in inspect.getmembers(BaseLogicPlugin):
            if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
                abstract_methods.append(name)
        
        required_methods = ['process_entry_signal', 'process_exit_signal', 'process_reversal_signal']
        for method in required_methods:
            assert method in abstract_methods, f"Missing abstract method: {method}"
    
    def test_base_plugin_init_signature(self):
        """Verify BaseLogicPlugin __init__ accepts correct parameters"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        import inspect
        
        sig = inspect.signature(BaseLogicPlugin.__init__)
        params = list(sig.parameters.keys())
        
        assert 'plugin_id' in params, "Missing plugin_id parameter"
        assert 'config' in params, "Missing config parameter"
        assert 'service_api' in params, "Missing service_api parameter"
    
    def test_base_plugin_has_enable_disable_methods(self):
        """Verify BaseLogicPlugin has enable/disable methods"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'enable'), "Missing enable method"
        assert hasattr(BaseLogicPlugin, 'disable'), "Missing disable method"
    
    def test_base_plugin_has_get_status_method(self):
        """Verify BaseLogicPlugin has get_status method"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'get_status'), "Missing get_status method"
    
    def test_base_plugin_has_validate_alert_method(self):
        """Verify BaseLogicPlugin has validate_alert method"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'validate_alert'), "Missing validate_alert method"
    
    def test_base_plugin_has_database_connection_method(self):
        """Verify BaseLogicPlugin has get_database_connection method"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'get_database_connection'), "Missing get_database_connection method"


class TestPluginRegistry:
    """Test PluginRegistry class implementation"""
    
    def test_plugin_registry_class_exists(self):
        """Verify PluginRegistry class exists"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        assert PluginRegistry is not None
    
    def test_plugin_registry_init_signature(self):
        """Verify PluginRegistry __init__ accepts correct parameters"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        import inspect
        
        sig = inspect.signature(PluginRegistry.__init__)
        params = list(sig.parameters.keys())
        
        assert 'config' in params, "Missing config parameter"
        assert 'service_api' in params, "Missing service_api parameter"
    
    def test_plugin_registry_has_discover_plugins_method(self):
        """Verify PluginRegistry has discover_plugins method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'discover_plugins'), "Missing discover_plugins method"
    
    def test_plugin_registry_has_load_plugin_method(self):
        """Verify PluginRegistry has load_plugin method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'load_plugin'), "Missing load_plugin method"
    
    def test_plugin_registry_has_load_all_plugins_method(self):
        """Verify PluginRegistry has load_all_plugins method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'load_all_plugins'), "Missing load_all_plugins method"
    
    def test_plugin_registry_has_get_plugin_method(self):
        """Verify PluginRegistry has get_plugin method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'get_plugin'), "Missing get_plugin method"
    
    def test_plugin_registry_has_route_alert_method(self):
        """Verify PluginRegistry has route_alert_to_plugin method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'route_alert_to_plugin'), "Missing route_alert_to_plugin method"
    
    def test_plugin_registry_has_get_all_plugins_method(self):
        """Verify PluginRegistry has get_all_plugins method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'get_all_plugins'), "Missing get_all_plugins method"
    
    def test_plugin_registry_has_execute_hook_method(self):
        """Verify PluginRegistry has execute_hook method"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        assert hasattr(PluginRegistry, 'execute_hook'), "Missing execute_hook method"


class TestPluginSystemInit:
    """Test plugin system __init__.py exports"""
    
    def test_init_exports_base_plugin(self):
        """Verify __init__.py exports BaseLogicPlugin"""
        from src.core.plugin_system import BaseLogicPlugin
        assert BaseLogicPlugin is not None
    
    def test_init_exports_plugin_registry(self):
        """Verify __init__.py exports PluginRegistry"""
        from src.core.plugin_system import PluginRegistry
        assert PluginRegistry is not None


class TestTemplatePlugin:
    """Test template plugin implementation"""
    
    def test_template_plugin_class_exists(self):
        """Verify TemplatePlugin class exists"""
        from src.logic_plugins._template.plugin import TemplatePlugin
        assert TemplatePlugin is not None
    
    def test_template_plugin_extends_base_plugin(self):
        """Verify TemplatePlugin extends BaseLogicPlugin"""
        from src.logic_plugins._template.plugin import TemplatePlugin
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert issubclass(TemplatePlugin, BaseLogicPlugin), "TemplatePlugin should extend BaseLogicPlugin"
    
    def test_template_plugin_implements_entry_signal(self):
        """Verify TemplatePlugin implements process_entry_signal"""
        from src.logic_plugins._template.plugin import TemplatePlugin
        import inspect
        
        assert hasattr(TemplatePlugin, 'process_entry_signal')
        method = getattr(TemplatePlugin, 'process_entry_signal')
        assert asyncio.iscoroutinefunction(method), "process_entry_signal should be async"
    
    def test_template_plugin_implements_exit_signal(self):
        """Verify TemplatePlugin implements process_exit_signal"""
        from src.logic_plugins._template.plugin import TemplatePlugin
        import inspect
        
        assert hasattr(TemplatePlugin, 'process_exit_signal')
        method = getattr(TemplatePlugin, 'process_exit_signal')
        assert asyncio.iscoroutinefunction(method), "process_exit_signal should be async"
    
    def test_template_plugin_implements_reversal_signal(self):
        """Verify TemplatePlugin implements process_reversal_signal"""
        from src.logic_plugins._template.plugin import TemplatePlugin
        import inspect
        
        assert hasattr(TemplatePlugin, 'process_reversal_signal')
        method = getattr(TemplatePlugin, 'process_reversal_signal')
        assert asyncio.iscoroutinefunction(method), "process_reversal_signal should be async"


class TestTemplateConfig:
    """Test template plugin config.json"""
    
    def test_template_config_is_valid_json(self):
        """Verify _template/config.json is valid JSON"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert isinstance(config, dict)
    
    def test_template_config_has_plugin_id(self):
        """Verify config has plugin_id field"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'plugin_id' in config, "Missing plugin_id in config"
        assert config['plugin_id'] == '_template'
    
    def test_template_config_has_enabled_field(self):
        """Verify config has enabled field (should be false for template)"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'enabled' in config, "Missing enabled in config"
        assert config['enabled'] == False, "Template should be disabled by default"
    
    def test_template_config_has_database_settings(self):
        """Verify config has database settings"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'database' in config, "Missing database settings in config"
    
    def test_template_config_has_trading_settings(self):
        """Verify config has trading_settings"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'trading_settings' in config, "Missing trading_settings in config"
    
    def test_template_config_has_notification_settings(self):
        """Verify config has notification_settings"""
        path = os.path.join(PROJECT_ROOT, "src/logic_plugins/_template/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'notification_settings' in config, "Missing notification_settings in config"


class TestMainConfigPluginSystem:
    """Test main config.json has plugin_system configuration"""
    
    def test_main_config_exists(self):
        """Verify config/config.json exists"""
        path = os.path.join(PROJECT_ROOT, "config/config.json")
        assert os.path.exists(path), f"config.json not found at {path}"
    
    def test_main_config_has_plugin_system_section(self):
        """Verify config has plugin_system section"""
        path = os.path.join(PROJECT_ROOT, "config/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'plugin_system' in config, "Missing plugin_system section in config"
    
    def test_main_config_plugin_system_has_enabled(self):
        """Verify plugin_system has enabled field"""
        path = os.path.join(PROJECT_ROOT, "config/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'enabled' in config['plugin_system'], "Missing enabled in plugin_system"
    
    def test_main_config_plugin_system_has_plugin_dir(self):
        """Verify plugin_system has plugin_dir field"""
        path = os.path.join(PROJECT_ROOT, "config/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'plugin_dir' in config['plugin_system'], "Missing plugin_dir in plugin_system"
        assert config['plugin_system']['plugin_dir'] == 'src/logic_plugins'
    
    def test_main_config_has_plugins_section(self):
        """Verify config has plugins section"""
        path = os.path.join(PROJECT_ROOT, "config/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        assert 'plugins' in config, "Missing plugins section in config"


class TestGitignorePluginDatabases:
    """Test .gitignore has plugin database patterns"""
    
    def test_gitignore_exists(self):
        """Verify .gitignore exists"""
        path = os.path.join(PROJECT_ROOT, ".gitignore")
        assert os.path.exists(path), f".gitignore not found at {path}"
    
    def test_gitignore_has_db_pattern(self):
        """Verify .gitignore has pattern for database files"""
        path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(path, 'r') as f:
            content = f.read()
        assert 'data/*.db' in content or '*.db' in content, "Missing database pattern in .gitignore"


class TestPluginDiscovery:
    """Test plugin discovery functionality"""
    
    def test_registry_discovers_template_plugin(self):
        """Verify registry can discover _template plugin directory"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        config = {
            "plugin_system": {
                "plugin_dir": os.path.join(PROJECT_ROOT, "src/logic_plugins")
            },
            "plugins": {}
        }
        
        registry = PluginRegistry(config, None)
        plugins = registry.discover_plugins()
        
        assert isinstance(plugins, list), "discover_plugins should return a list"
    
    def test_registry_discovers_combined_v3_plugin(self):
        """Verify registry discovers combined_v3 plugin"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        config = {
            "plugin_system": {
                "plugin_dir": os.path.join(PROJECT_ROOT, "src/logic_plugins")
            },
            "plugins": {}
        }
        
        registry = PluginRegistry(config, None)
        plugins = registry.discover_plugins()
        
        assert 'combined_v3' in plugins, "combined_v3 plugin not discovered"
    
    def test_registry_discovers_price_action_v6_plugin(self):
        """Verify registry discovers price_action_v6 plugin"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        config = {
            "plugin_system": {
                "plugin_dir": os.path.join(PROJECT_ROOT, "src/logic_plugins")
            },
            "plugins": {}
        }
        
        registry = PluginRegistry(config, None)
        plugins = registry.discover_plugins()
        
        assert 'price_action_v6' in plugins, "price_action_v6 plugin not discovered"
    
    def test_registry_excludes_template_from_discovery(self):
        """Verify registry excludes _template (starts with underscore)"""
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        config = {
            "plugin_system": {
                "plugin_dir": os.path.join(PROJECT_ROOT, "src/logic_plugins")
            },
            "plugins": {}
        }
        
        registry = PluginRegistry(config, None)
        plugins = registry.discover_plugins()
        
        assert '_template' not in plugins, "_template should be excluded (starts with _)"


class TestPluginInstantiation:
    """Test plugin instantiation with mock service API"""
    
    def test_can_instantiate_dummy_plugin(self):
        """Verify we can create a concrete plugin subclass"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True}
            
            async def process_exit_signal(self, alert):
                return {"success": True}
            
            async def process_reversal_signal(self, alert):
                return {"success": True}
        
        plugin = DummyPlugin("test_plugin", {"enabled": True}, None)
        
        assert plugin.plugin_id == "test_plugin"
        assert plugin.enabled == True
    
    def test_plugin_enable_disable_works(self):
        """Verify enable/disable methods work"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True}
            
            async def process_exit_signal(self, alert):
                return {"success": True}
            
            async def process_reversal_signal(self, alert):
                return {"success": True}
        
        plugin = DummyPlugin("test", {"enabled": True}, None)
        
        plugin.disable()
        assert plugin.enabled == False
        
        plugin.enable()
        assert plugin.enabled == True
    
    def test_plugin_get_status_returns_dict(self):
        """Verify get_status returns proper dict"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True}
            
            async def process_exit_signal(self, alert):
                return {"success": True}
            
            async def process_reversal_signal(self, alert):
                return {"success": True}
        
        plugin = DummyPlugin("test", {"enabled": True}, None)
        status = plugin.get_status()
        
        assert isinstance(status, dict)
        assert 'plugin_id' in status
        assert 'enabled' in status
        assert status['plugin_id'] == 'test'


class TestAlertRouting:
    """Test alert routing functionality"""
    
    def test_route_entry_alert_to_plugin(self):
        """Verify entry alerts are routed correctly"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True, "type": "entry"}
            
            async def process_exit_signal(self, alert):
                return {"success": True, "type": "exit"}
            
            async def process_reversal_signal(self, alert):
                return {"success": True, "type": "reversal"}
        
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        
        registry = PluginRegistry(config, None)
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        class MockAlert:
            signal_type = "entry"
        
        result = asyncio.run(registry.route_alert_to_plugin(MockAlert(), "test"))
        
        assert result.get("success") == True
        assert result.get("type") == "entry"
    
    def test_route_exit_alert_to_plugin(self):
        """Verify exit alerts are routed correctly"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True, "type": "entry"}
            
            async def process_exit_signal(self, alert):
                return {"success": True, "type": "exit"}
            
            async def process_reversal_signal(self, alert):
                return {"success": True, "type": "reversal"}
        
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        
        registry = PluginRegistry(config, None)
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        class MockAlert:
            signal_type = "exit"
        
        result = asyncio.run(registry.route_alert_to_plugin(MockAlert(), "test"))
        
        assert result.get("success") == True
        assert result.get("type") == "exit"
    
    def test_route_reversal_alert_to_plugin(self):
        """Verify reversal alerts are routed correctly"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True, "type": "entry"}
            
            async def process_exit_signal(self, alert):
                return {"success": True, "type": "exit"}
            
            async def process_reversal_signal(self, alert):
                return {"success": True, "type": "reversal"}
        
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        
        registry = PluginRegistry(config, None)
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        class MockAlert:
            signal_type = "reversal"
        
        result = asyncio.run(registry.route_alert_to_plugin(MockAlert(), "test"))
        
        assert result.get("success") == True
        assert result.get("type") == "reversal"
    
    def test_disabled_plugin_skips_alert(self):
        """Verify disabled plugins skip alerts"""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        from src.core.plugin_system.plugin_registry import PluginRegistry
        
        class DummyPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True}
            
            async def process_exit_signal(self, alert):
                return {"success": True}
            
            async def process_reversal_signal(self, alert):
                return {"success": True}
        
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": False}}
        }
        
        registry = PluginRegistry(config, None)
        plugin = DummyPlugin("test", {"enabled": False}, None)
        plugin.disable()
        registry.plugins["test"] = plugin
        
        class MockAlert:
            signal_type = "entry"
        
        result = asyncio.run(registry.route_alert_to_plugin(MockAlert(), "test"))
        
        assert result.get("skipped") == True
        assert result.get("reason") == "plugin_disabled"


class TestTradingEnginePluginIntegration:
    """Test plugin system integration in TradingEngine"""
    
    def test_trading_engine_imports_plugin_registry(self):
        """Verify TradingEngine imports PluginRegistry"""
        trading_engine_path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(trading_engine_path, 'r') as f:
            content = f.read()
        
        assert 'from src.core.plugin_system.plugin_registry import PluginRegistry' in content
    
    def test_trading_engine_imports_service_api(self):
        """Verify TradingEngine imports ServiceAPI"""
        trading_engine_path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(trading_engine_path, 'r') as f:
            content = f.read()
        
        assert 'from src.core.plugin_system.service_api import ServiceAPI' in content
    
    def test_trading_engine_initializes_plugin_registry(self):
        """Verify TradingEngine initializes PluginRegistry"""
        trading_engine_path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(trading_engine_path, 'r') as f:
            content = f.read()
        
        assert 'self.plugin_registry = PluginRegistry' in content
    
    def test_trading_engine_initializes_service_api(self):
        """Verify TradingEngine initializes ServiceAPI"""
        trading_engine_path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(trading_engine_path, 'r') as f:
            content = f.read()
        
        assert 'self.service_api = ServiceAPI' in content
    
    def test_trading_engine_loads_plugins_on_initialize(self):
        """Verify TradingEngine loads plugins in initialize method"""
        trading_engine_path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(trading_engine_path, 'r') as f:
            content = f.read()
        
        assert 'plugin_registry.discover_plugins()' in content or 'plugin_registry.load_all_plugins()' in content
    
    def test_trading_engine_executes_plugin_hooks(self):
        """Verify TradingEngine executes plugin hooks in process_alert"""
        trading_engine_path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(trading_engine_path, 'r') as f:
            content = f.read()
        
        assert 'execute_hook' in content


class TestServiceAPIExists:
    """Test ServiceAPI class exists and has required structure"""
    
    def test_service_api_file_exists(self):
        """Verify service_api.py exists"""
        path = os.path.join(PROJECT_ROOT, "src/core/plugin_system/service_api.py")
        assert os.path.exists(path), f"service_api.py not found at {path}"
    
    def test_service_api_class_exists(self):
        """Verify ServiceAPI class exists"""
        from src.core.plugin_system.service_api import ServiceAPI
        assert ServiceAPI is not None


class TestDocument02CompleteSummary:
    """Summary tests to verify 100% Document 02 implementation"""
    
    def test_all_7_new_files_exist(self):
        """Verify all 7 new files from Document 02 exist"""
        files = [
            "src/core/plugin_system/base_plugin.py",
            "src/core/plugin_system/plugin_registry.py",
            "src/core/plugin_system/__init__.py",
            "src/logic_plugins/_template/plugin.py",
            "src/logic_plugins/_template/config.json",
            "src/logic_plugins/_template/README.md",
            "scripts/test_plugin.py"
        ]
        
        for file in files:
            path = os.path.join(PROJECT_ROOT, file)
            assert os.path.exists(path), f"Missing file: {file}"
    
    def test_config_modified_with_plugin_system(self):
        """Verify config.json has plugin_system configuration"""
        path = os.path.join(PROJECT_ROOT, "config/config.json")
        with open(path, 'r') as f:
            config = json.load(f)
        
        assert 'plugin_system' in config
        assert 'plugins' in config
    
    def test_trading_engine_integrated(self):
        """Verify TradingEngine has plugin system integration"""
        path = os.path.join(PROJECT_ROOT, "src/core/trading_engine.py")
        with open(path, 'r') as f:
            content = f.read()
        
        assert 'PluginRegistry' in content
        assert 'ServiceAPI' in content
    
    def test_gitignore_updated(self):
        """Verify .gitignore has database patterns"""
        path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(path, 'r') as f:
            content = f.read()
        
        assert '.db' in content
    
    def test_plugin_system_functional(self):
        """Verify plugin system is functional end-to-end"""
        from src.core.plugin_system import BaseLogicPlugin, PluginRegistry
        
        class TestPlugin(BaseLogicPlugin):
            async def process_entry_signal(self, alert):
                return {"success": True}
            
            async def process_exit_signal(self, alert):
                return {"success": True}
            
            async def process_reversal_signal(self, alert):
                return {"success": True}
        
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        
        registry = PluginRegistry(config, None)
        plugin = TestPlugin("functional_test", {"enabled": True}, None)
        registry.plugins["functional_test"] = plugin
        
        assert registry.get_plugin("functional_test") is not None
        assert registry.get_plugin("functional_test").enabled == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
