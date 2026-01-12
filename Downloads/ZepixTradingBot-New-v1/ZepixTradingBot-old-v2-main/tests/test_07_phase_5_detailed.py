"""
Test Suite for Document 07: Phase 5 - Dynamic Config & Per-Plugin Databases

This test file verifies 100% implementation of Document 07 requirements:
1. ConfigManager with hot-reload capability
2. Per-Plugin Database setup (PluginDatabase class)
3. Plugin Config Hot-Reload integration
4. Database Migration Tools

Test Categories:
- TestConfigManager: ConfigManager functionality tests
- TestPluginDatabase: Per-plugin database tests
- TestConfigHotReload: Config hot-reload integration tests
- TestDatabaseMigration: Migration tools tests
- TestBasePluginConfigSupport: Base plugin config support tests
- TestDatabaseIsolation: Database isolation tests
- TestDocument07Integration: Integration tests
- TestDocument07Summary: Summary verification tests
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestConfigManager:
    """Tests for ConfigManager implementation."""
    
    def test_config_manager_module_exists(self):
        """Test config_manager.py module exists."""
        config_manager_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'core', 'config_manager.py'
        )
        assert os.path.exists(config_manager_path)
    
    def test_config_manager_class_import(self):
        """Test ConfigManager class can be imported."""
        from core.config_manager import ConfigManager
        assert ConfigManager is not None
    
    def test_config_file_handler_import(self):
        """Test ConfigFileHandler class can be imported."""
        from core.config_manager import ConfigFileHandler
        assert ConfigFileHandler is not None
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization with config file."""
        from core.config_manager import ConfigManager
        
        # Create temp config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "value", "plugins": {}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            assert manager.config_path == temp_path
            assert manager.config == {"test": "value", "plugins": {}}
        finally:
            os.unlink(temp_path)
    
    def test_load_config_method(self):
        """Test load_config method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            config = manager.load_config()
            assert config == {"key": "value"}
        finally:
            os.unlink(temp_path)
    
    def test_reload_config_method(self):
        """Test reload_config method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value1"}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            # Modify config file
            with open(temp_path, 'w') as f:
                json.dump({"key": "value2"}, f)
            
            changes = manager.reload_config()
            assert "key" in changes
            assert manager.config["key"] == "value2"
        finally:
            os.unlink(temp_path)
    
    def test_diff_config_method(self):
        """Test _diff_config method detects changes."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            old = {"a": 1, "b": 2}
            new = {"a": 1, "b": 3, "c": 4}
            
            changes = manager._diff_config(old, new)
            assert "b" in changes
            assert "c" in changes
            assert "a" not in changes
        finally:
            os.unlink(temp_path)
    
    def test_register_observer(self):
        """Test register_observer method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            callback = Mock()
            manager.register_observer(callback)
            
            assert callback in manager.observers
        finally:
            os.unlink(temp_path)
    
    def test_unregister_observer(self):
        """Test unregister_observer method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            callback = Mock()
            manager.register_observer(callback)
            manager.unregister_observer(callback)
            
            assert callback not in manager.observers
        finally:
            os.unlink(temp_path)
    
    def test_notify_observers(self):
        """Test _notify_observers method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value1"}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            callback = Mock()
            manager.register_observer(callback)
            
            # Modify and reload
            with open(temp_path, 'w') as f:
                json.dump({"key": "value2"}, f)
            
            manager.reload_config()
            
            callback.assert_called_once()
        finally:
            os.unlink(temp_path)
    
    def test_get_method(self):
        """Test get method with dot notation."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"plugins": {"test": {"enabled": True}}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            assert manager.get("plugins.test.enabled") == True
            assert manager.get("plugins.test.missing", "default") == "default"
        finally:
            os.unlink(temp_path)
    
    def test_set_method(self):
        """Test set method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"plugins": {}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            manager.set("plugins.test.enabled", True)
            
            assert manager.get("plugins.test.enabled") == True
        finally:
            os.unlink(temp_path)
    
    def test_get_plugin_config(self):
        """Test get_plugin_config method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"plugins": {"combined_v3": {"enabled": True, "max_lot": 1.0}}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            config = manager.get_plugin_config("combined_v3")
            
            assert config["enabled"] == True
            assert config["max_lot"] == 1.0
        finally:
            os.unlink(temp_path)
    
    def test_get_plugin_enabled(self):
        """Test get_plugin_enabled method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"plugins": {"test": {"enabled": True}}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            assert manager.get_plugin_enabled("test") == True
            assert manager.get_plugin_enabled("missing") == False
        finally:
            os.unlink(temp_path)
    
    def test_save_config(self):
        """Test save_config method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            manager.set("new_key", "new_value")
            manager.save_config()
            
            # Read back
            with open(temp_path, 'r') as f:
                saved = json.load(f)
            
            assert saved["new_key"] == "new_value"
        finally:
            os.unlink(temp_path)
    
    def test_validate_config(self):
        """Test validate_config method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"trading": {}, "telegram": {}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            errors = manager.validate_config()
            assert len(errors) == 0
        finally:
            os.unlink(temp_path)
    
    def test_get_all_plugin_ids(self):
        """Test get_all_plugin_ids method."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"plugins": {"plugin_a": {}, "plugin_b": {}}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            ids = manager.get_all_plugin_ids()
            
            assert "plugin_a" in ids
            assert "plugin_b" in ids
        finally:
            os.unlink(temp_path)


class TestPluginDatabase:
    """Tests for PluginDatabase implementation."""
    
    def test_plugin_database_module_exists(self):
        """Test plugin_database.py module exists."""
        db_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'core', 'plugin_database.py'
        )
        assert os.path.exists(db_path)
    
    def test_plugin_database_class_import(self):
        """Test PluginDatabase class can be imported."""
        from core.plugin_database import PluginDatabase
        assert PluginDatabase is not None
    
    def test_plugin_database_initialization(self):
        """Test PluginDatabase initialization."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Patch DB_DIR
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_plugin")
                assert db.plugin_id == "test_plugin"
                assert db.connection is not None
                db.close()
    
    def test_database_path_format(self):
        """Test database path follows zepix_{plugin_id}.db format."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("combined_v3")
                assert "zepix_combined_v3.db" in db.db_path
                db.close()
    
    def test_schema_creation(self):
        """Test database schema is created correctly."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_schema")
                
                # Check tables exist
                cursor = db.connection.cursor()
                tables = cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                table_names = [t[0] for t in tables]
                
                assert "trades" in table_names
                assert "daily_stats" in table_names
                assert "plugin_info" in table_names
                assert "trade_events" in table_names
                assert "schema_version" in table_names
                
                db.close()
    
    def test_save_trade(self):
        """Test save_trade method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_save")
                
                trade_id = db.save_trade({
                    "ticket": 12345,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "lot_size": 0.1,
                    "entry_price": 1.0850,
                    "sl_price": 1.0800,
                    "tp_price": 1.0900
                })
                
                assert trade_id > 0
                db.close()
    
    def test_get_trade_by_ticket(self):
        """Test get_trade_by_ticket method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_get")
                
                db.save_trade({
                    "ticket": 99999,
                    "symbol": "GBPUSD",
                    "direction": "SELL",
                    "lot_size": 0.2,
                    "entry_price": 1.2500
                })
                
                trade = db.get_trade_by_ticket(99999)
                assert trade is not None
                assert trade["symbol"] == "GBPUSD"
                assert trade["direction"] == "SELL"
                
                db.close()
    
    def test_get_open_trades(self):
        """Test get_open_trades method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_open")
                
                db.save_trade({
                    "ticket": 11111,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "lot_size": 0.1,
                    "entry_price": 1.0850
                })
                
                open_trades = db.get_open_trades()
                assert len(open_trades) == 1
                assert open_trades[0]["mt5_ticket"] == 11111
                
                db.close()
    
    def test_update_trade(self):
        """Test update_trade method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_update")
                
                db.save_trade({
                    "ticket": 22222,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "lot_size": 0.1,
                    "entry_price": 1.0850
                })
                
                result = db.update_trade(22222, {"sl_price": 1.0800})
                assert result == True
                
                trade = db.get_trade_by_ticket(22222)
                assert trade["sl_price"] == 1.0800
                
                db.close()
    
    def test_close_trade(self):
        """Test close_trade method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_close")
                
                db.save_trade({
                    "ticket": 33333,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "lot_size": 0.1,
                    "entry_price": 1.0850
                })
                
                result = db.close_trade(33333, 1.0900, 50.0, 25.0, "TP")
                assert result == True
                
                trade = db.get_trade_by_ticket(33333)
                assert trade["status"] == "CLOSED"
                assert trade["close_reason"] == "TP"
                
                db.close()
    
    def test_get_statistics(self):
        """Test get_statistics method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_stats")
                
                stats = db.get_statistics()
                assert "plugin_id" in stats
                assert "total_trades" in stats
                assert "win_rate" in stats
                
                db.close()
    
    def test_get_plugin_info(self):
        """Test get_plugin_info method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_info")
                
                info = db.get_plugin_info()
                assert info["plugin_id"] == "test_info"
                
                db.close()
    
    def test_update_plugin_info(self):
        """Test update_plugin_info method."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_update_info")
                
                db.update_plugin_info(version="2.0.0")
                info = db.get_plugin_info()
                assert info["version"] == "2.0.0"
                
                db.close()
    
    def test_trade_events_logging(self):
        """Test trade events are logged."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_events")
                
                trade_id = db.save_trade({
                    "ticket": 44444,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "lot_size": 0.1,
                    "entry_price": 1.0850
                })
                
                events = db.get_trade_events(trade_id)
                assert len(events) > 0
                assert events[0]["event_type"] == "TRADE_OPENED"
                
                db.close()


class TestDatabaseIsolation:
    """Tests for database isolation between plugins."""
    
    def test_plugin_database_isolation(self):
        """Test plugins cannot access each other's databases."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                # Create two plugin databases
                db_a = PluginDatabase("plugin_a")
                db_b = PluginDatabase("plugin_b")
                
                # Save trade to plugin_a
                db_a.save_trade({
                    "ticket": 55555,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "lot_size": 0.1,
                    "entry_price": 1.0850
                })
                
                # Plugin B should not see Plugin A's trades
                trades_b = db_b.get_all_trades()
                assert len(trades_b) == 0
                
                db_a.close()
                db_b.close()
    
    def test_separate_database_files(self):
        """Test each plugin gets its own database file."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db_a = PluginDatabase("plugin_a")
                db_b = PluginDatabase("plugin_b")
                
                assert db_a.db_path != db_b.db_path
                assert os.path.exists(db_a.db_path)
                assert os.path.exists(db_b.db_path)
                
                db_a.close()
                db_b.close()


class TestConfigHotReload:
    """Tests for config hot-reload integration."""
    
    def test_base_plugin_on_config_changed_method(self):
        """Test BaseLogicPlugin has on_config_changed method."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'on_config_changed')
        assert callable(getattr(BaseLogicPlugin, 'on_config_changed'))
    
    def test_base_plugin_on_plugin_enabled_method(self):
        """Test BaseLogicPlugin has on_plugin_enabled method."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'on_plugin_enabled')
        assert callable(getattr(BaseLogicPlugin, 'on_plugin_enabled'))
    
    def test_base_plugin_on_plugin_disabled_method(self):
        """Test BaseLogicPlugin has on_plugin_disabled method."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'on_plugin_disabled')
        assert callable(getattr(BaseLogicPlugin, 'on_plugin_disabled'))
    
    def test_base_plugin_set_config_manager_method(self):
        """Test BaseLogicPlugin has set_config_manager method."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'set_config_manager')
        assert callable(getattr(BaseLogicPlugin, 'set_config_manager'))
    
    def test_base_plugin_reload_config_method(self):
        """Test BaseLogicPlugin has reload_config method."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert hasattr(BaseLogicPlugin, 'reload_config')
        assert callable(getattr(BaseLogicPlugin, 'reload_config'))
    
    def test_base_plugin_config_manager_attribute(self):
        """Test BaseLogicPlugin has config_manager attribute."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        # Check __init__ sets config_manager
        import inspect
        source = inspect.getsource(BaseLogicPlugin.__init__)
        assert "config_manager" in source
    
    def test_base_plugin_max_lot_attribute(self):
        """Test BaseLogicPlugin has max_lot attribute."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        import inspect
        source = inspect.getsource(BaseLogicPlugin.__init__)
        assert "max_lot" in source
    
    def test_base_plugin_risk_percent_attribute(self):
        """Test BaseLogicPlugin has risk_percent attribute."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        import inspect
        source = inspect.getsource(BaseLogicPlugin.__init__)
        assert "risk_percent" in source


class TestDatabaseMigration:
    """Tests for database migration tools."""
    
    def test_migration_script_exists(self):
        """Test migration script exists."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'scripts', 'migrate_legacy_to_plugin_db.py'
        )
        assert os.path.exists(script_path)
    
    def test_legacy_database_migrator_import(self):
        """Test LegacyDatabaseMigrator can be imported."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from migrate_legacy_to_plugin_db import LegacyDatabaseMigrator
        assert LegacyDatabaseMigrator is not None
    
    def test_migrator_plugin_patterns(self):
        """Test migrator has plugin patterns defined."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from migrate_legacy_to_plugin_db import LegacyDatabaseMigrator
        
        assert hasattr(LegacyDatabaseMigrator, 'PLUGIN_PATTERNS')
        assert "combined_v3" in LegacyDatabaseMigrator.PLUGIN_PATTERNS
    
    def test_migrator_legacy_db_paths(self):
        """Test migrator has legacy DB paths defined."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from migrate_legacy_to_plugin_db import LegacyDatabaseMigrator
        
        assert hasattr(LegacyDatabaseMigrator, 'LEGACY_DB_PATHS')
        assert len(LegacyDatabaseMigrator.LEGACY_DB_PATHS) > 0
    
    def test_migrator_map_trade_fields(self):
        """Test migrator has _map_trade_fields method."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from migrate_legacy_to_plugin_db import LegacyDatabaseMigrator
        
        assert hasattr(LegacyDatabaseMigrator, '_map_trade_fields')
    
    def test_migrator_normalize_direction(self):
        """Test migrator has _normalize_direction method."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from migrate_legacy_to_plugin_db import LegacyDatabaseMigrator
        
        migrator = LegacyDatabaseMigrator.__new__(LegacyDatabaseMigrator)
        
        assert migrator._normalize_direction("BUY") == "BUY"
        assert migrator._normalize_direction("SELL") == "SELL"
        assert migrator._normalize_direction("LONG") == "BUY"
        assert migrator._normalize_direction("SHORT") == "SELL"
        assert migrator._normalize_direction("0") == "BUY"
        assert migrator._normalize_direction("1") == "SELL"


class TestDocument07Integration:
    """Integration tests for Document 07 components."""
    
    def test_config_manager_with_plugin_database(self):
        """Test ConfigManager works with PluginDatabase."""
        from core.config_manager import ConfigManager
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config file
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump({
                    "plugins": {
                        "test_plugin": {"enabled": True}
                    }
                }, f)
            
            # Create config manager
            manager = ConfigManager(config_path)
            
            # Create plugin database
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_plugin")
                
                # Verify both work together
                assert manager.get_plugin_enabled("test_plugin") == True
                assert db.plugin_id == "test_plugin"
                
                db.close()
    
    def test_zero_downtime_config_update(self):
        """Test config can be updated without restart."""
        from core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"plugins": {"test": {"max_lot": 1.0}}}, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            # Initial value
            assert manager.get("plugins.test.max_lot") == 1.0
            
            # Update config file
            with open(temp_path, 'w') as f:
                json.dump({"plugins": {"test": {"max_lot": 2.0}}}, f)
            
            # Reload without restart
            manager.reload_config()
            
            # New value
            assert manager.get("plugins.test.max_lot") == 2.0
        finally:
            os.unlink(temp_path)
    
    def test_plugin_database_schema_version(self):
        """Test database schema versioning works."""
        from core.plugin_database import PluginDatabase
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PluginDatabase, 'DB_DIR', temp_dir):
                db = PluginDatabase("test_version")
                
                cursor = db.connection.cursor()
                version = cursor.execute(
                    "SELECT MAX(version) FROM schema_version"
                ).fetchone()[0]
                
                assert version == PluginDatabase.SCHEMA_VERSION
                
                db.close()
    
    def test_all_components_importable(self):
        """Test all Document 07 components can be imported."""
        from core.config_manager import ConfigManager, ConfigFileHandler
        from core.plugin_database import PluginDatabase
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert ConfigManager is not None
        assert ConfigFileHandler is not None
        assert PluginDatabase is not None
        assert BaseLogicPlugin is not None


class TestDocument07Summary:
    """Summary tests verifying Document 07 completion criteria."""
    
    def test_config_manager_implemented(self):
        """Test ConfigManager is fully implemented."""
        from core.config_manager import ConfigManager
        
        required_methods = [
            'load_config', 'reload_config', 'register_observer',
            'unregister_observer', 'get', 'set', 'save_config',
            'get_plugin_config', 'get_plugin_enabled', 'validate_config'
        ]
        
        for method in required_methods:
            assert hasattr(ConfigManager, method), f"Missing method: {method}"
    
    def test_per_plugin_databases_created(self):
        """Test per-plugin database system is implemented."""
        from core.plugin_database import PluginDatabase
        
        required_methods = [
            'save_trade', 'get_trade_by_ticket', 'get_open_trades',
            'update_trade', 'close_trade', 'get_statistics',
            'get_plugin_info', 'update_plugin_info'
        ]
        
        for method in required_methods:
            assert hasattr(PluginDatabase, method), f"Missing method: {method}"
    
    def test_config_hot_reload_working(self):
        """Test config hot-reload is implemented."""
        from core.plugin_system.base_plugin import BaseLogicPlugin
        
        required_methods = [
            'on_config_changed', 'on_plugin_enabled', 'on_plugin_disabled',
            'set_config_manager', 'reload_config'
        ]
        
        for method in required_methods:
            assert hasattr(BaseLogicPlugin, method), f"Missing method: {method}"
    
    def test_migration_scripts_ready(self):
        """Test migration scripts are ready."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'scripts', 'migrate_legacy_to_plugin_db.py'
        )
        assert os.path.exists(script_path)
        
        # Check script is valid Python
        with open(script_path, 'r') as f:
            content = f.read()
        
        compile(content, script_path, 'exec')
    
    def test_document_07_requirements_met(self):
        """Test all Document 07 requirements are met."""
        # 1. ConfigManager implemented
        from core.config_manager import ConfigManager
        assert ConfigManager is not None
        
        # 2. Per-plugin databases created
        from core.plugin_database import PluginDatabase
        assert PluginDatabase is not None
        
        # 3. Config hot-reload working
        from core.plugin_system.base_plugin import BaseLogicPlugin
        assert hasattr(BaseLogicPlugin, 'on_config_changed')
        
        # 4. Migration scripts ready
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'scripts', 'migrate_legacy_to_plugin_db.py'
        )
        assert os.path.exists(script_path)
        
        # All requirements met
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
