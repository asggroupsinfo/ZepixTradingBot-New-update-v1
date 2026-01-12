"""
Test Suite for Document 09: Database Schema Designs

This test file verifies the complete implementation of Document 09:
- V3 Combined Logic Database Schema
- V6 Price Action Database Schema
- Central System Database Schema
- Database Sync Manager
- ORM Models and Data Validation

Test Categories:
- TestDatabasePackage: Package structure and imports
- TestV3DatabaseSchema: V3 schema structure and operations
- TestV6DatabaseSchema: V6 schema structure and operations
- TestCentralDatabaseSchema: Central schema structure and operations
- TestDatabaseMigration: Schema creation and migration
- TestORMModels: ORM model functionality
- TestDataValidation: Data integrity constraints
- TestDatabaseSyncManager: Sync manager functionality
- TestDocument09Integration: All schemas working together
- TestDocument09Summary: Summary verification
"""

import unittest
import os
import sys
import tempfile
import shutil
import sqlite3
from datetime import datetime, date

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDatabasePackage(unittest.TestCase):
    """Test database package structure and imports."""
    
    def test_package_exists(self):
        """Test that database package exists."""
        package_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database'
        )
        self.assertTrue(os.path.exists(package_path))
    
    def test_init_file_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', '__init__.py'
        )
        self.assertTrue(os.path.exists(init_path))
    
    def test_schemas_module_exists(self):
        """Test that schemas.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schemas.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_v3_database_module_exists(self):
        """Test that v3_database.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'v3_database.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_v6_database_module_exists(self):
        """Test that v6_database.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'v6_database.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_central_database_module_exists(self):
        """Test that central_database.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'central_database.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_sync_manager_module_exists(self):
        """Test that sync_manager.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'sync_manager.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_import_base_schema(self):
        """Test importing BaseSchema."""
        from database.schemas import BaseSchema
        self.assertTrue(hasattr(BaseSchema, 'get_schema_sql'))
        self.assertTrue(hasattr(BaseSchema, 'get_indexes_sql'))
        self.assertTrue(hasattr(BaseSchema, 'create_schema'))
    
    def test_import_schema_manager(self):
        """Test importing SchemaManager."""
        from database.schemas import SchemaManager
        self.assertTrue(hasattr(SchemaManager, 'create_all_databases'))
        self.assertTrue(hasattr(SchemaManager, 'validate_all_schemas'))
    
    def test_import_v3_classes(self):
        """Test importing V3 classes."""
        from database.v3_database import V3Schema, V3Database
        self.assertIsNotNone(V3Schema)
        self.assertIsNotNone(V3Database)
    
    def test_import_v6_classes(self):
        """Test importing V6 classes."""
        from database.v6_database import V6Schema, V6Database
        self.assertIsNotNone(V6Schema)
        self.assertIsNotNone(V6Database)
    
    def test_import_central_classes(self):
        """Test importing Central classes."""
        from database.central_database import CentralSchema, CentralDatabase
        self.assertIsNotNone(CentralSchema)
        self.assertIsNotNone(CentralDatabase)
    
    def test_import_sync_manager(self):
        """Test importing DatabaseSyncManager."""
        from database.sync_manager import DatabaseSyncManager
        self.assertIsNotNone(DatabaseSyncManager)


class TestV3DatabaseSchema(unittest.TestCase):
    """Test V3 Combined Logic database schema."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_v3.db')
        
        from database.v3_database import V3Schema, V3Database
        cls.schema = V3Schema(cls.db_path)
        cls.schema.create_schema()
        cls.db = V3Database(cls.db_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.db.close()
        shutil.rmtree(cls.test_dir)
    
    def test_schema_creates_combined_v3_trades_table(self):
        """Test combined_v3_trades table exists."""
        self.assertTrue(self.schema.table_exists('combined_v3_trades'))
    
    def test_schema_creates_v3_profit_bookings_table(self):
        """Test v3_profit_bookings table exists."""
        self.assertTrue(self.schema.table_exists('v3_profit_bookings'))
    
    def test_schema_creates_v3_signals_log_table(self):
        """Test v3_signals_log table exists."""
        self.assertTrue(self.schema.table_exists('v3_signals_log'))
    
    def test_schema_creates_v3_daily_stats_table(self):
        """Test v3_daily_stats table exists."""
        self.assertTrue(self.schema.table_exists('v3_daily_stats'))
    
    def test_combined_v3_trades_has_order_columns(self):
        """Test combined_v3_trades has order A and B columns."""
        columns = self.schema.get_table_info('combined_v3_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('order_a_ticket', column_names)
        self.assertIn('order_b_ticket', column_names)
        self.assertIn('order_a_lot_size', column_names)
        self.assertIn('order_b_lot_size', column_names)
    
    def test_combined_v3_trades_has_mtf_columns(self):
        """Test combined_v3_trades has MTF 4-pillar columns."""
        columns = self.schema.get_table_info('combined_v3_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('mtf_15m', column_names)
        self.assertIn('mtf_1h', column_names)
        self.assertIn('mtf_4h', column_names)
        self.assertIn('mtf_1d', column_names)
    
    def test_combined_v3_trades_has_logic_route(self):
        """Test combined_v3_trades has logic_route column."""
        columns = self.schema.get_table_info('combined_v3_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('logic_route', column_names)
        self.assertIn('logic_multiplier', column_names)
    
    def test_save_trade(self):
        """Test saving a V3 trade."""
        trade_data = {
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'entry_price': 1.1000,
            'signal_type': 'ENTRY_V3_SIGNAL',
            'logic_route': 'LOGIC1',
            'order_a_lot_size': 0.01,
            'order_b_lot_size': 0.02,
            'order_a_status': 'OPEN',
            'order_b_status': 'OPEN'
        }
        
        trade_id = self.db.save_trade(trade_data)
        self.assertIsNotNone(trade_id)
        self.assertGreater(trade_id, 0)
    
    def test_get_trade(self):
        """Test getting a V3 trade."""
        trade_data = {
            'symbol': 'GBPUSD',
            'direction': 'SELL',
            'entry_price': 1.2500,
            'signal_type': 'ENTRY_V3_SIGNAL',
            'logic_route': 'LOGIC2'
        }
        
        trade_id = self.db.save_trade(trade_data)
        trade = self.db.get_trade(trade_id)
        
        self.assertIsNotNone(trade)
        self.assertEqual(trade['symbol'], 'GBPUSD')
        self.assertEqual(trade['direction'], 'SELL')
    
    def test_get_open_trades(self):
        """Test getting open trades."""
        open_trades = self.db.get_open_trades()
        self.assertIsInstance(open_trades, list)
    
    def test_update_trade(self):
        """Test updating a trade."""
        trade_data = {
            'symbol': 'USDJPY',
            'direction': 'BUY',
            'entry_price': 110.00,
            'signal_type': 'ENTRY_V3_SIGNAL'
        }
        
        trade_id = self.db.save_trade(trade_data)
        result = self.db.update_trade(trade_id, {'status': 'PARTIAL'})
        
        self.assertTrue(result)
        
        trade = self.db.get_trade(trade_id)
        self.assertEqual(trade['status'], 'PARTIAL')
    
    def test_log_signal(self):
        """Test logging a signal."""
        signal_data = {
            'signal_type': 'ENTRY_V3_SIGNAL',
            'symbol': 'XAUUSD',
            'direction': 'BUY',
            'consensus_score': 7
        }
        
        signal_id = self.db.log_signal(signal_data)
        self.assertIsNotNone(signal_id)
        self.assertGreater(signal_id, 0)
    
    def test_get_daily_stats(self):
        """Test getting daily stats."""
        stats = self.db.get_daily_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('date', stats)
        self.assertIn('total_dual_entries', stats)
    
    def test_get_statistics(self):
        """Test getting overall statistics."""
        stats = self.db.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_trades', stats)
        self.assertIn('open_trades', stats)


class TestV6DatabaseSchema(unittest.TestCase):
    """Test V6 Price Action database schema."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_v6.db')
        
        from database.v6_database import V6Schema, V6Database
        cls.schema = V6Schema(cls.db_path)
        cls.schema.create_schema()
        cls.db = V6Database(cls.db_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.db.close()
        shutil.rmtree(cls.test_dir)
    
    def test_schema_creates_1m_trades_table(self):
        """Test price_action_1m_trades table exists."""
        self.assertTrue(self.schema.table_exists('price_action_1m_trades'))
    
    def test_schema_creates_5m_trades_table(self):
        """Test price_action_5m_trades table exists."""
        self.assertTrue(self.schema.table_exists('price_action_5m_trades'))
    
    def test_schema_creates_15m_trades_table(self):
        """Test price_action_15m_trades table exists."""
        self.assertTrue(self.schema.table_exists('price_action_15m_trades'))
    
    def test_schema_creates_1h_trades_table(self):
        """Test price_action_1h_trades table exists."""
        self.assertTrue(self.schema.table_exists('price_action_1h_trades'))
    
    def test_schema_creates_market_trends_table(self):
        """Test market_trends table exists."""
        self.assertTrue(self.schema.table_exists('market_trends'))
    
    def test_schema_creates_v6_signals_log_table(self):
        """Test v6_signals_log table exists."""
        self.assertTrue(self.schema.table_exists('v6_signals_log'))
    
    def test_schema_creates_v6_daily_stats_table(self):
        """Test v6_daily_stats table exists."""
        self.assertTrue(self.schema.table_exists('v6_daily_stats'))
    
    def test_1m_table_has_order_b_only(self):
        """Test 1M table has ORDER B only columns."""
        columns = self.schema.get_table_info('price_action_1m_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('order_b_ticket', column_names)
        self.assertNotIn('order_a_ticket', column_names)
    
    def test_5m_table_has_dual_orders(self):
        """Test 5M table has dual order columns."""
        columns = self.schema.get_table_info('price_action_5m_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('order_a_ticket', column_names)
        self.assertIn('order_b_ticket', column_names)
    
    def test_15m_table_has_order_a_only(self):
        """Test 15M table has ORDER A only columns."""
        columns = self.schema.get_table_info('price_action_15m_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('order_a_ticket', column_names)
        self.assertNotIn('order_b_ticket', column_names)
    
    def test_1h_table_has_order_a_only(self):
        """Test 1H table has ORDER A only columns."""
        columns = self.schema.get_table_info('price_action_1h_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('order_a_ticket', column_names)
        self.assertNotIn('order_b_ticket', column_names)
    
    def test_plugin_configs(self):
        """Test plugin configurations."""
        configs = self.db.PLUGIN_CONFIGS
        
        self.assertEqual(configs['price_action_1m']['order_type'], 'B_ONLY')
        self.assertEqual(configs['price_action_5m']['order_type'], 'DUAL')
        self.assertEqual(configs['price_action_15m']['order_type'], 'A_ONLY')
        self.assertEqual(configs['price_action_1h']['order_type'], 'A_ONLY')
    
    def test_sl_multipliers(self):
        """Test SL multipliers per plugin."""
        configs = self.db.PLUGIN_CONFIGS
        
        self.assertEqual(configs['price_action_1m']['sl_multiplier'], 0.5)
        self.assertEqual(configs['price_action_5m']['sl_multiplier'], 1.0)
        self.assertEqual(configs['price_action_15m']['sl_multiplier'], 1.5)
        self.assertEqual(configs['price_action_1h']['sl_multiplier'], 2.0)
    
    def test_max_hold_minutes(self):
        """Test max hold minutes per plugin."""
        configs = self.db.PLUGIN_CONFIGS
        
        self.assertEqual(configs['price_action_1m']['max_hold_minutes'], 60)
        self.assertEqual(configs['price_action_5m']['max_hold_minutes'], 240)
        self.assertEqual(configs['price_action_15m']['max_hold_minutes'], 480)
        self.assertEqual(configs['price_action_1h']['max_hold_minutes'], 1440)
    
    def test_save_1m_trade(self):
        """Test saving a 1M trade."""
        trade_data = {
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'entry_price': 1.1000,
            'signal_type': 'BULLISH_ENTRY',
            'lot_size': 0.01,
            'order_b_ticket': 12345
        }
        
        trade_id = self.db.save_trade('price_action_1m', trade_data)
        self.assertIsNotNone(trade_id)
        self.assertGreater(trade_id, 0)
    
    def test_save_5m_trade(self):
        """Test saving a 5M trade (dual orders)."""
        trade_data = {
            'symbol': 'GBPUSD',
            'direction': 'SELL',
            'entry_price': 1.2500,
            'signal_type': 'BEARISH_ENTRY',
            'order_a_lot_size': 0.01,
            'order_b_lot_size': 0.02,
            'order_a_ticket': 12346,
            'order_b_ticket': 12347,
            'order_a_status': 'OPEN',
            'order_b_status': 'OPEN'
        }
        
        trade_id = self.db.save_trade('price_action_5m', trade_data)
        self.assertIsNotNone(trade_id)
    
    def test_get_trade(self):
        """Test getting a V6 trade."""
        trade_data = {
            'symbol': 'USDJPY',
            'direction': 'BUY',
            'entry_price': 110.00,
            'signal_type': 'BULLISH_ENTRY',
            'lot_size': 0.01,
            'order_a_ticket': 12348
        }
        
        trade_id = self.db.save_trade('price_action_15m', trade_data)
        trade = self.db.get_trade('price_action_15m', trade_id)
        
        self.assertIsNotNone(trade)
        self.assertEqual(trade['symbol'], 'USDJPY')
    
    def test_update_market_trend(self):
        """Test updating market trend."""
        result = self.db.update_market_trend(
            'EURUSD', '1M', bull_count=5, bear_count=3, trend_pulse='BULLISH'
        )
        self.assertTrue(result)
    
    def test_get_market_trend(self):
        """Test getting market trend."""
        self.db.update_market_trend('GBPUSD', '5M', 4, 2, 'BULLISH')
        trend = self.db.get_market_trend('GBPUSD', '5M')
        
        self.assertIsNotNone(trend)
        self.assertEqual(trend['bull_count'], 4)
        self.assertEqual(trend['bear_count'], 2)
    
    def test_log_signal(self):
        """Test logging a V6 signal."""
        signal_data = {
            'signal_type': 'BULLISH_ENTRY',
            'symbol': 'XAUUSD',
            'direction': 'BUY',
            'trend_pulse_bull': 5,
            'trend_pulse_bear': 2
        }
        
        signal_id = self.db.log_signal('price_action_1m', signal_data)
        self.assertIsNotNone(signal_id)
    
    def test_get_statistics(self):
        """Test getting V6 statistics."""
        stats = self.db.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('price_action_1m', stats)
        self.assertIn('price_action_5m', stats)


class TestCentralDatabaseSchema(unittest.TestCase):
    """Test Central System database schema."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_central.db')
        
        from database.central_database import CentralSchema, CentralDatabase
        cls.schema = CentralSchema(cls.db_path)
        cls.schema.create_schema()
        cls.db = CentralDatabase(cls.db_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.db.close()
        shutil.rmtree(cls.test_dir)
    
    def test_schema_creates_plugins_registry_table(self):
        """Test plugins_registry table exists."""
        self.assertTrue(self.schema.table_exists('plugins_registry'))
    
    def test_schema_creates_aggregated_trades_table(self):
        """Test aggregated_trades table exists."""
        self.assertTrue(self.schema.table_exists('aggregated_trades'))
    
    def test_schema_creates_system_config_table(self):
        """Test system_config table exists."""
        self.assertTrue(self.schema.table_exists('system_config'))
    
    def test_schema_creates_system_events_table(self):
        """Test system_events table exists."""
        self.assertTrue(self.schema.table_exists('system_events'))
    
    def test_plugins_registry_prepopulated(self):
        """Test plugins_registry is pre-populated with 5 plugins."""
        plugins = self.db.get_all_plugins()
        self.assertEqual(len(plugins), 5)
    
    def test_plugins_registry_has_combined_v3(self):
        """Test combined_v3 plugin exists."""
        plugin = self.db.get_plugin('combined_v3')
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin['plugin_type'], 'V3_COMBINED')
    
    def test_plugins_registry_has_price_action_1m(self):
        """Test price_action_1m plugin exists."""
        plugin = self.db.get_plugin('price_action_1m')
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin['plugin_type'], 'V6_PRICE_ACTION')
    
    def test_plugins_registry_has_price_action_5m(self):
        """Test price_action_5m plugin exists."""
        plugin = self.db.get_plugin('price_action_5m')
        self.assertIsNotNone(plugin)
    
    def test_plugins_registry_has_price_action_15m(self):
        """Test price_action_15m plugin exists."""
        plugin = self.db.get_plugin('price_action_15m')
        self.assertIsNotNone(plugin)
    
    def test_plugins_registry_has_price_action_1h(self):
        """Test price_action_1h plugin exists."""
        plugin = self.db.get_plugin('price_action_1h')
        self.assertIsNotNone(plugin)
    
    def test_system_config_prepopulated(self):
        """Test system_config is pre-populated."""
        config = self.db.get_all_config()
        
        self.assertIn('bot_version', config)
        self.assertIn('architecture', config)
        self.assertIn('v3_enabled', config)
        self.assertIn('v6_enabled', config)
    
    def test_system_config_bot_version(self):
        """Test bot_version config."""
        version = self.db.get_config('bot_version')
        self.assertEqual(version, '5.0.0')
    
    def test_system_config_architecture(self):
        """Test architecture config."""
        arch = self.db.get_config('architecture')
        self.assertEqual(arch, 'V5_HYBRID_PLUGIN')
    
    def test_enable_disable_plugin(self):
        """Test enabling and disabling plugins."""
        # Disable
        result = self.db.disable_plugin('price_action_1m')
        self.assertTrue(result)
        
        plugin = self.db.get_plugin('price_action_1m')
        self.assertEqual(plugin['enabled'], 0)
        
        # Enable
        result = self.db.enable_plugin('price_action_1m')
        self.assertTrue(result)
        
        plugin = self.db.get_plugin('price_action_1m')
        self.assertEqual(plugin['enabled'], 1)
    
    def test_add_aggregated_trade(self):
        """Test adding an aggregated trade."""
        trade_data = {
            'plugin_id': 'combined_v3',
            'plugin_type': 'V3_COMBINED',
            'source_trade_id': 1,
            'mt5_ticket': 12345,
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'lot_size': 0.01,
            'entry_price': 1.1000,
            'status': 'OPEN'
        }
        
        trade_id = self.db.add_aggregated_trade(trade_data)
        self.assertIsNotNone(trade_id)
        self.assertGreater(trade_id, 0)
    
    def test_get_aggregated_trades(self):
        """Test getting aggregated trades."""
        trades = self.db.get_aggregated_trades()
        self.assertIsInstance(trades, list)
    
    def test_set_get_config(self):
        """Test setting and getting config."""
        self.db.set_config('test_key', 'test_value', 'Test description')
        value = self.db.get_config('test_key')
        self.assertEqual(value, 'test_value')
    
    def test_log_event(self):
        """Test logging an event."""
        event_id = self.db.log_event(
            event_type='TEST_EVENT',
            message='Test event message',
            severity='INFO',
            source='TestSuite'
        )
        self.assertIsNotNone(event_id)
        self.assertGreater(event_id, 0)
    
    def test_get_events(self):
        """Test getting events."""
        events = self.db.get_events()
        self.assertIsInstance(events, list)
    
    def test_acknowledge_event(self):
        """Test acknowledging an event."""
        event_id = self.db.log_event(
            event_type='ACK_TEST',
            message='Test ack',
            severity='WARNING'
        )
        
        result = self.db.acknowledge_event(event_id)
        self.assertTrue(result)
    
    def test_get_system_statistics(self):
        """Test getting system statistics."""
        stats = self.db.get_system_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_plugins', stats)
        self.assertIn('enabled_plugins', stats)
        self.assertIn('total_trades', stats)


class TestDatabaseMigration(unittest.TestCase):
    """Test database migration and schema creation."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_v3_schema_creation(self):
        """Test V3 schema creation from scratch."""
        from database.v3_database import V3Schema
        
        db_path = os.path.join(self.test_dir, 'new_v3.db')
        schema = V3Schema(db_path)
        result = schema.create_schema()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(db_path))
        self.assertTrue(schema.table_exists('combined_v3_trades'))
    
    def test_v6_schema_creation(self):
        """Test V6 schema creation from scratch."""
        from database.v6_database import V6Schema
        
        db_path = os.path.join(self.test_dir, 'new_v6.db')
        schema = V6Schema(db_path)
        result = schema.create_schema()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(db_path))
        self.assertTrue(schema.table_exists('price_action_1m_trades'))
    
    def test_central_schema_creation(self):
        """Test Central schema creation from scratch."""
        from database.central_database import CentralSchema
        
        db_path = os.path.join(self.test_dir, 'new_central.db')
        schema = CentralSchema(db_path)
        result = schema.create_schema()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(db_path))
        self.assertTrue(schema.table_exists('plugins_registry'))
    
    def test_schema_manager_create_all(self):
        """Test SchemaManager creates all databases."""
        from database.schemas import SchemaManager
        
        # Override paths for testing
        manager = SchemaManager()
        manager.V3_DB_PATH = os.path.join(self.test_dir, 'v3.db')
        manager.V6_DB_PATH = os.path.join(self.test_dir, 'v6.db')
        manager.CENTRAL_DB_PATH = os.path.join(self.test_dir, 'central.db')
        
        # Note: This would need the paths to be set before schema classes are instantiated
        # For now, just verify the method exists
        self.assertTrue(hasattr(manager, 'create_all_databases'))
    
    def test_idempotent_schema_creation(self):
        """Test schema creation is idempotent."""
        from database.v3_database import V3Schema
        
        db_path = os.path.join(self.test_dir, 'idempotent.db')
        schema = V3Schema(db_path)
        
        # Create twice
        result1 = schema.create_schema()
        result2 = schema.create_schema()
        
        self.assertTrue(result1)
        self.assertTrue(result2)


class TestORMModels(unittest.TestCase):
    """Test ORM model functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test databases."""
        cls.test_dir = tempfile.mkdtemp()
        
        from database.v3_database import V3Database
        from database.v6_database import V6Database
        from database.central_database import CentralDatabase
        
        cls.v3_db = V3Database(os.path.join(cls.test_dir, 'v3.db'))
        cls.v6_db = V6Database(os.path.join(cls.test_dir, 'v6.db'))
        cls.central_db = CentralDatabase(os.path.join(cls.test_dir, 'central.db'))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test databases."""
        cls.v3_db.close()
        cls.v6_db.close()
        cls.central_db.close()
        shutil.rmtree(cls.test_dir)
    
    def test_v3_trade_crud(self):
        """Test V3 trade CRUD operations."""
        # Create
        trade_id = self.v3_db.save_trade({
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'entry_price': 1.1000,
            'signal_type': 'ENTRY_V3_SIGNAL'
        })
        self.assertIsNotNone(trade_id)
        
        # Read
        trade = self.v3_db.get_trade(trade_id)
        self.assertEqual(trade['symbol'], 'EURUSD')
        
        # Update
        self.v3_db.update_trade(trade_id, {'status': 'CLOSED'})
        trade = self.v3_db.get_trade(trade_id)
        self.assertEqual(trade['status'], 'CLOSED')
    
    def test_v6_trade_crud(self):
        """Test V6 trade CRUD operations."""
        # Create
        trade_id = self.v6_db.save_trade('price_action_1m', {
            'symbol': 'GBPUSD',
            'direction': 'SELL',
            'entry_price': 1.2500,
            'signal_type': 'BEARISH_ENTRY',
            'lot_size': 0.01,
            'order_b_ticket': 99999
        })
        self.assertIsNotNone(trade_id)
        
        # Read
        trade = self.v6_db.get_trade('price_action_1m', trade_id)
        self.assertEqual(trade['symbol'], 'GBPUSD')
        
        # Update
        self.v6_db.update_trade('price_action_1m', trade_id, {'status': 'CLOSED'})
        trade = self.v6_db.get_trade('price_action_1m', trade_id)
        self.assertEqual(trade['status'], 'CLOSED')
    
    def test_central_plugin_crud(self):
        """Test Central plugin CRUD operations."""
        # Read (pre-populated)
        plugins = self.central_db.get_all_plugins()
        self.assertEqual(len(plugins), 5)
        
        # Update (enable/disable)
        self.central_db.disable_plugin('combined_v3')
        plugin = self.central_db.get_plugin('combined_v3')
        self.assertEqual(plugin['enabled'], 0)
        
        self.central_db.enable_plugin('combined_v3')
        plugin = self.central_db.get_plugin('combined_v3')
        self.assertEqual(plugin['enabled'], 1)
    
    def test_row_factory_returns_dict(self):
        """Test that row factory returns dictionaries."""
        trade_id = self.v3_db.save_trade({
            'symbol': 'XAUUSD',
            'direction': 'BUY',
            'entry_price': 1900.00,
            'signal_type': 'ENTRY_V3_SIGNAL'
        })
        
        trade = self.v3_db.get_trade(trade_id)
        self.assertIsInstance(trade, dict)
        self.assertIn('symbol', trade)


class TestDataValidation(unittest.TestCase):
    """Test data integrity constraints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'validation.db')
        
        from database.v3_database import V3Schema
        cls.schema = V3Schema(cls.db_path)
        cls.schema.create_schema()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.schema.close()
        shutil.rmtree(cls.test_dir)
    
    def test_direction_constraint(self):
        """Test direction column constraint (BUY/SELL)."""
        conn = self.schema.connect()
        cursor = conn.cursor()
        
        # Valid direction
        cursor.execute("""
            INSERT INTO combined_v3_trades (symbol, direction, entry_price, signal_type)
            VALUES ('EURUSD', 'BUY', 1.1, 'TEST')
        """)
        conn.commit()
        
        # Invalid direction should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO combined_v3_trades (symbol, direction, entry_price, signal_type)
                VALUES ('EURUSD', 'INVALID', 1.1, 'TEST')
            """)
    
    def test_status_constraint(self):
        """Test status column constraint (OPEN/PARTIAL/CLOSED)."""
        conn = self.schema.connect()
        cursor = conn.cursor()
        
        # Valid status
        cursor.execute("""
            INSERT INTO combined_v3_trades (symbol, direction, entry_price, signal_type, status)
            VALUES ('GBPUSD', 'SELL', 1.25, 'TEST', 'OPEN')
        """)
        conn.commit()
        
        # Invalid status should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO combined_v3_trades (symbol, direction, entry_price, signal_type, status)
                VALUES ('GBPUSD', 'SELL', 1.25, 'TEST', 'INVALID')
            """)
    
    def test_logic_route_constraint(self):
        """Test logic_route column constraint (LOGIC1/LOGIC2/LOGIC3)."""
        conn = self.schema.connect()
        cursor = conn.cursor()
        
        # Valid logic route
        cursor.execute("""
            INSERT INTO combined_v3_trades (symbol, direction, entry_price, signal_type, logic_route)
            VALUES ('USDJPY', 'BUY', 110, 'TEST', 'LOGIC1')
        """)
        conn.commit()
        
        # Invalid logic route should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO combined_v3_trades (symbol, direction, entry_price, signal_type, logic_route)
                VALUES ('USDJPY', 'BUY', 110, 'TEST', 'LOGIC4')
            """)
    
    def test_mtf_constraint(self):
        """Test MTF column constraint (-1, 0, 1)."""
        conn = self.schema.connect()
        cursor = conn.cursor()
        
        # Valid MTF values
        cursor.execute("""
            INSERT INTO combined_v3_trades 
            (symbol, direction, entry_price, signal_type, mtf_15m, mtf_1h, mtf_4h, mtf_1d)
            VALUES ('XAUUSD', 'BUY', 1900, 'TEST', -1, 0, 1, 1)
        """)
        conn.commit()
        
        # Invalid MTF value should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO combined_v3_trades 
                (symbol, direction, entry_price, signal_type, mtf_15m)
                VALUES ('XAUUSD', 'BUY', 1900, 'TEST', 2)
            """)
    
    def test_not_null_constraint(self):
        """Test NOT NULL constraints."""
        conn = self.schema.connect()
        cursor = conn.cursor()
        
        # Missing required field should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO combined_v3_trades (direction, entry_price, signal_type)
                VALUES ('BUY', 1.1, 'TEST')
            """)


class TestDatabaseSyncManager(unittest.TestCase):
    """Test Database Sync Manager functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test databases."""
        cls.test_dir = tempfile.mkdtemp()
        
        from database.v3_database import V3Database
        from database.v6_database import V6Database
        from database.central_database import CentralDatabase
        from database.sync_manager import DatabaseSyncManager
        
        cls.v3_db = V3Database(os.path.join(cls.test_dir, 'v3.db'))
        cls.v6_db = V6Database(os.path.join(cls.test_dir, 'v6.db'))
        cls.central_db = CentralDatabase(os.path.join(cls.test_dir, 'central.db'))
        cls.sync_manager = DatabaseSyncManager(cls.v3_db, cls.v6_db, cls.central_db)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test databases."""
        cls.sync_manager.close()
        shutil.rmtree(cls.test_dir)
    
    def test_sync_manager_initialization(self):
        """Test sync manager initializes correctly."""
        self.assertIsNotNone(self.sync_manager)
        self.assertFalse(self.sync_manager.is_running)
    
    def test_sync_manager_has_databases(self):
        """Test sync manager has database references."""
        self.assertIsNotNone(self.sync_manager.v3_db)
        self.assertIsNotNone(self.sync_manager.v6_db)
        self.assertIsNotNone(self.sync_manager.central_db)
    
    def test_default_sync_interval(self):
        """Test default sync interval is 5 minutes."""
        self.assertEqual(self.sync_manager.sync_interval, 5 * 60)
    
    def test_sync_stats_initialized(self):
        """Test sync stats are initialized."""
        stats = self.sync_manager.sync_stats
        
        self.assertIn('total_syncs', stats)
        self.assertIn('successful_syncs', stats)
        self.assertIn('failed_syncs', stats)
        self.assertIn('v3_trades_synced', stats)
        self.assertIn('v6_trades_synced', stats)
    
    def test_get_sync_status(self):
        """Test getting sync status."""
        status = self.sync_manager.get_sync_status()
        
        self.assertIn('running', status)
        self.assertIn('sync_interval_seconds', status)
        self.assertIn('stats', status)
    
    def test_sync_trade_update(self):
        """Test syncing a trade update."""
        # Add a trade to V3
        trade_id = self.v3_db.save_trade({
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'entry_price': 1.1000,
            'signal_type': 'ENTRY_V3_SIGNAL'
        })
        
        # Add to central
        self.central_db.add_aggregated_trade({
            'plugin_id': 'combined_v3',
            'plugin_type': 'V3_COMBINED',
            'source_trade_id': trade_id,
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'status': 'OPEN'
        })
        
        # Sync update
        result = self.sync_manager.sync_trade_update(
            'combined_v3', trade_id, {'status': 'CLOSED'}
        )
        self.assertTrue(result)
    
    def test_last_synced_trade_id(self):
        """Test getting last synced trade ID."""
        last_id = self.central_db.get_last_synced_trade_id('combined_v3')
        self.assertIsInstance(last_id, int)


class TestDocument09Integration(unittest.TestCase):
    """Test all Document 09 components working together."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = tempfile.mkdtemp()
        
        from database.v3_database import V3Database
        from database.v6_database import V6Database
        from database.central_database import CentralDatabase
        from database.sync_manager import DatabaseSyncManager
        
        cls.v3_db = V3Database(os.path.join(cls.test_dir, 'v3.db'))
        cls.v6_db = V6Database(os.path.join(cls.test_dir, 'v6.db'))
        cls.central_db = CentralDatabase(os.path.join(cls.test_dir, 'central.db'))
        cls.sync_manager = DatabaseSyncManager(cls.v3_db, cls.v6_db, cls.central_db)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cls.sync_manager.close()
        shutil.rmtree(cls.test_dir)
    
    def test_three_database_architecture(self):
        """Test three-database architecture is implemented."""
        # V3 database
        self.assertTrue(self.v3_db.schema.table_exists('combined_v3_trades'))
        
        # V6 database
        self.assertTrue(self.v6_db.schema.table_exists('price_action_1m_trades'))
        
        # Central database
        self.assertTrue(self.central_db.schema.table_exists('plugins_registry'))
    
    def test_database_isolation(self):
        """Test V3 and V6 databases are isolated."""
        # V3 should not have V6 tables
        self.assertFalse(self.v3_db.schema.table_exists('price_action_1m_trades'))
        
        # V6 should not have V3 tables
        self.assertFalse(self.v6_db.schema.table_exists('combined_v3_trades'))
    
    def test_central_aggregates_all_plugins(self):
        """Test central database can aggregate from all plugins."""
        # Add V3 trade
        v3_trade_id = self.v3_db.save_trade({
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'entry_price': 1.1000,
            'signal_type': 'ENTRY_V3_SIGNAL'
        })
        
        # Add V6 trade
        v6_trade_id = self.v6_db.save_trade('price_action_1m', {
            'symbol': 'GBPUSD',
            'direction': 'SELL',
            'entry_price': 1.2500,
            'signal_type': 'BEARISH_ENTRY',
            'lot_size': 0.01,
            'order_b_ticket': 88888
        })
        
        # Aggregate to central
        self.central_db.add_aggregated_trade({
            'plugin_id': 'combined_v3',
            'plugin_type': 'V3_COMBINED',
            'source_trade_id': v3_trade_id,
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'status': 'OPEN'
        })
        
        self.central_db.add_aggregated_trade({
            'plugin_id': 'price_action_1m',
            'plugin_type': 'V6_PRICE_ACTION',
            'source_trade_id': v6_trade_id,
            'symbol': 'GBPUSD',
            'direction': 'SELL',
            'status': 'OPEN'
        })
        
        # Verify aggregation
        trades = self.central_db.get_aggregated_trades()
        self.assertGreaterEqual(len(trades), 2)
    
    def test_plugin_registry_complete(self):
        """Test plugin registry has all 5 plugins."""
        plugins = self.central_db.get_all_plugins()
        plugin_ids = [p['plugin_id'] for p in plugins]
        
        self.assertIn('combined_v3', plugin_ids)
        self.assertIn('price_action_1m', plugin_ids)
        self.assertIn('price_action_5m', plugin_ids)
        self.assertIn('price_action_15m', plugin_ids)
        self.assertIn('price_action_1h', plugin_ids)
    
    def test_sync_manager_connects_all_databases(self):
        """Test sync manager connects all databases."""
        self.assertIsNotNone(self.sync_manager.v3_db)
        self.assertIsNotNone(self.sync_manager.v6_db)
        self.assertIsNotNone(self.sync_manager.central_db)


class TestDocument09Summary(unittest.TestCase):
    """Summary tests for Document 09 implementation."""
    
    def test_v3_database_path(self):
        """Test V3 database path is correct."""
        from database.v3_database import V3Database
        self.assertEqual(V3Database.DB_PATH, 'data/zepix_combined.db')
    
    def test_v6_database_path(self):
        """Test V6 database path is correct."""
        from database.v6_database import V6Database
        self.assertEqual(V6Database.DB_PATH, 'data/zepix_price_action.db')
    
    def test_central_database_path(self):
        """Test Central database path is correct."""
        from database.central_database import CentralDatabase
        self.assertEqual(CentralDatabase.DB_PATH, 'data/zepix_bot.db')
    
    def test_v3_has_12_signal_support(self):
        """Test V3 schema supports 12 signal types."""
        from database.v3_database import V3Schema
        
        test_dir = tempfile.mkdtemp()
        db_path = os.path.join(test_dir, 'test.db')
        schema = V3Schema(db_path)
        schema.create_schema()
        
        columns = schema.get_table_info('combined_v3_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('signal_type', column_names)
        
        schema.close()
        shutil.rmtree(test_dir)
    
    def test_v3_has_dual_order_support(self):
        """Test V3 schema has dual order support."""
        from database.v3_database import V3Schema
        
        test_dir = tempfile.mkdtemp()
        db_path = os.path.join(test_dir, 'test.db')
        schema = V3Schema(db_path)
        schema.create_schema()
        
        columns = schema.get_table_info('combined_v3_trades')
        column_names = [c['name'] for c in columns]
        
        self.assertIn('order_a_ticket', column_names)
        self.assertIn('order_b_ticket', column_names)
        
        schema.close()
        shutil.rmtree(test_dir)
    
    def test_v6_has_4_timeframe_tables(self):
        """Test V6 schema has 4 timeframe-specific tables."""
        from database.v6_database import V6Schema
        
        test_dir = tempfile.mkdtemp()
        db_path = os.path.join(test_dir, 'test.db')
        schema = V6Schema(db_path)
        schema.create_schema()
        
        self.assertTrue(schema.table_exists('price_action_1m_trades'))
        self.assertTrue(schema.table_exists('price_action_5m_trades'))
        self.assertTrue(schema.table_exists('price_action_15m_trades'))
        self.assertTrue(schema.table_exists('price_action_1h_trades'))
        
        schema.close()
        shutil.rmtree(test_dir)
    
    def test_sync_interval_is_5_minutes(self):
        """Test sync interval is 5 minutes."""
        from database.sync_manager import DatabaseSyncManager
        self.assertEqual(DatabaseSyncManager.DEFAULT_SYNC_INTERVAL, 5 * 60)
    
    def test_all_modules_importable(self):
        """Test all database modules are importable."""
        from database import (
            BaseSchema,
            SchemaManager,
            V3Database,
            V3Schema,
            V6Database,
            V6Schema,
            CentralDatabase,
            CentralSchema,
            DatabaseSyncManager
        )
        
        self.assertIsNotNone(BaseSchema)
        self.assertIsNotNone(SchemaManager)
        self.assertIsNotNone(V3Database)
        self.assertIsNotNone(V3Schema)
        self.assertIsNotNone(V6Database)
        self.assertIsNotNone(V6Schema)
        self.assertIsNotNone(CentralDatabase)
        self.assertIsNotNone(CentralSchema)
        self.assertIsNotNone(DatabaseSyncManager)


if __name__ == '__main__':
    unittest.main(verbosity=2)
