"""
Legacy Database to Plugin Database Migration Script

Document 07: Phase 5 - Dynamic Config & Per-Plugin Databases
Migrates trades from main database (zepix_bot.db) to plugin-specific databases.

Features:
- Migrate trades based on plugin_id/comment patterns
- Preserve all trade data and relationships
- Support date range filtering
- Dry-run mode for validation
- Progress tracking and logging

Usage:
    python scripts/migrate_legacy_to_plugin_db.py --plugin combined_v3 --start-date 2024-01-01
    python scripts/migrate_legacy_to_plugin_db.py --plugin combined_v3 --dry-run
    python scripts/migrate_legacy_to_plugin_db.py --all-plugins
"""

import sqlite3
import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.plugin_database import PluginDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegacyDatabaseMigrator:
    """
    Migrates trades from legacy main database to plugin-specific databases.
    
    The legacy database (data/zepix_bot.db or data/trading_bot.db) contains
    all trades from all plugins. This migrator separates them into
    plugin-specific databases for isolation.
    """
    
    # Possible legacy database paths
    LEGACY_DB_PATHS = [
        "data/zepix_bot.db",
        "data/trading_bot.db",
        "trading_bot.db"
    ]
    
    # Plugin identification patterns in trade comments
    PLUGIN_PATTERNS = {
        "combined_v3": ["V3", "Combined", "LOGIC1", "LOGIC2", "LOGIC3"],
        "price_action_v6_1m": ["V6_1M", "PA_1M", "1M_"],
        "price_action_v6_5m": ["V6_5M", "PA_5M", "5M_"],
        "price_action_v6_15m": ["V6_15M", "PA_15M", "15M_"],
        "price_action_v6_1h": ["V6_1H", "PA_1H", "1H_"]
    }
    
    def __init__(self, legacy_db_path: Optional[str] = None):
        """
        Initialize migrator.
        
        Args:
            legacy_db_path: Path to legacy database (auto-detected if None)
        """
        self.legacy_db_path = legacy_db_path or self._find_legacy_db()
        self.legacy_connection: Optional[sqlite3.Connection] = None
        self.stats = {
            'total_found': 0,
            'migrated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def _find_legacy_db(self) -> str:
        """Find the legacy database file."""
        for path in self.LEGACY_DB_PATHS:
            if os.path.exists(path):
                logger.info(f"Found legacy database: {path}")
                return path
        
        raise FileNotFoundError(
            f"Legacy database not found. Checked: {self.LEGACY_DB_PATHS}"
        )
    
    def connect(self) -> None:
        """Connect to legacy database."""
        if not os.path.exists(self.legacy_db_path):
            raise FileNotFoundError(f"Legacy database not found: {self.legacy_db_path}")
        
        self.legacy_connection = sqlite3.connect(self.legacy_db_path)
        self.legacy_connection.row_factory = sqlite3.Row
        logger.info(f"Connected to legacy database: {self.legacy_db_path}")
    
    def disconnect(self) -> None:
        """Disconnect from legacy database."""
        if self.legacy_connection:
            self.legacy_connection.close()
            self.legacy_connection = None
    
    def get_legacy_trades(self, plugin_id: str, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query legacy trades for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            List of trade dictionaries
        """
        if not self.legacy_connection:
            self.connect()
        
        cursor = self.legacy_connection.cursor()
        
        # Build query with plugin pattern matching
        patterns = self.PLUGIN_PATTERNS.get(plugin_id, [plugin_id])
        
        # Try to find trades table
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        
        # Determine trade table name
        trade_table = None
        for name in ['trades', 'trade_history', 'orders']:
            if name in table_names:
                trade_table = name
                break
        
        if not trade_table:
            logger.warning(f"No trade table found in legacy database. Tables: {table_names}")
            return []
        
        # Build WHERE clause for pattern matching
        pattern_conditions = " OR ".join([f"comment LIKE '%{p}%'" for p in patterns])
        
        query = f"""
            SELECT * FROM {trade_table}
            WHERE ({pattern_conditions})
        """
        params = []
        
        if start_date:
            query += " AND entry_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND entry_time <= ?"
            params.append(end_date + " 23:59:59")
        
        query += " ORDER BY entry_time"
        
        try:
            trades = cursor.execute(query, params).fetchall()
            return [dict(row) for row in trades]
        except sqlite3.OperationalError as e:
            logger.error(f"Query error: {e}")
            return []
    
    def migrate_trades_to_plugin_db(self, plugin_id: str, start_date: Optional[str] = None,
                                     end_date: Optional[str] = None, dry_run: bool = False) -> Dict[str, int]:
        """
        Migrates trades from main DB to plugin DB.
        
        Args:
            plugin_id: Plugin identifier
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            dry_run: If True, don't actually migrate, just report
            
        Returns:
            Migration statistics
        """
        logger.info(f"Starting migration for {plugin_id}...")
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Get legacy trades
        trades = self.get_legacy_trades(plugin_id, start_date, end_date)
        self.stats['total_found'] = len(trades)
        
        logger.info(f"Found {len(trades)} trades for {plugin_id}")
        
        if not trades:
            logger.info("No trades to migrate")
            return self.stats
        
        if dry_run:
            # Just report what would be migrated
            for trade in trades[:5]:  # Show first 5
                logger.info(f"  Would migrate: {trade.get('mt5_ticket', 'N/A')} - {trade.get('symbol', 'N/A')}")
            if len(trades) > 5:
                logger.info(f"  ... and {len(trades) - 5} more trades")
            return self.stats
        
        # Create plugin database
        plugin_db = PluginDatabase(plugin_id)
        
        # Migrate each trade
        for trade in trades:
            try:
                # Map legacy fields to new schema
                trade_data = self._map_trade_fields(trade)
                
                # Check if already migrated (by ticket)
                existing = plugin_db.get_trade_by_ticket(trade_data.get('ticket'))
                if existing:
                    logger.debug(f"Trade {trade_data.get('ticket')} already exists, skipping")
                    self.stats['skipped'] += 1
                    continue
                
                # Save to plugin database
                plugin_db.save_trade(trade_data)
                self.stats['migrated'] += 1
                
                if self.stats['migrated'] % 100 == 0:
                    logger.info(f"Migrated {self.stats['migrated']} trades...")
                    
            except Exception as e:
                logger.error(f"Error migrating trade {trade.get('mt5_ticket', 'N/A')}: {e}")
                self.stats['errors'] += 1
        
        plugin_db.close()
        
        logger.info(f"Migration complete for {plugin_id}")
        logger.info(f"  Total found: {self.stats['total_found']}")
        logger.info(f"  Migrated: {self.stats['migrated']}")
        logger.info(f"  Skipped: {self.stats['skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        
        return self.stats
    
    def _map_trade_fields(self, legacy_trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map legacy trade fields to new plugin database schema.
        
        Args:
            legacy_trade: Trade from legacy database
            
        Returns:
            Trade data for plugin database
        """
        # Field mapping (legacy -> new)
        field_map = {
            'mt5_ticket': 'ticket',
            'ticket': 'ticket',
            'order_ticket': 'ticket',
            'symbol': 'symbol',
            'pair': 'symbol',
            'direction': 'direction',
            'type': 'direction',
            'order_type': 'direction',
            'lot_size': 'lot_size',
            'lots': 'lot_size',
            'volume': 'lot_size',
            'entry_price': 'entry_price',
            'open_price': 'entry_price',
            'price': 'entry_price',
            'sl_price': 'sl_price',
            'stop_loss': 'sl_price',
            'sl': 'sl_price',
            'tp_price': 'tp_price',
            'take_profit': 'tp_price',
            'tp': 'tp_price',
            'exit_price': 'exit_price',
            'close_price': 'exit_price',
            'profit_pips': 'profit_pips',
            'pips': 'profit_pips',
            'profit_dollars': 'profit_dollars',
            'profit': 'profit_dollars',
            'pnl': 'profit_dollars',
            'commission': 'commission',
            'swap': 'swap',
            'comment': 'signal_data'
        }
        
        trade_data = {}
        
        for legacy_field, new_field in field_map.items():
            if legacy_field in legacy_trade and legacy_trade[legacy_field] is not None:
                value = legacy_trade[legacy_field]
                
                # Handle direction normalization
                if new_field == 'direction':
                    value = self._normalize_direction(value)
                
                # Handle signal_data (store comment as JSON)
                if new_field == 'signal_data':
                    value = {'comment': value, 'migrated': True}
                
                trade_data[new_field] = value
        
        return trade_data
    
    def _normalize_direction(self, direction: Any) -> str:
        """Normalize direction to BUY or SELL."""
        if direction is None:
            return 'BUY'
        
        direction_str = str(direction).upper()
        
        if direction_str in ['BUY', 'LONG', '0', 'ORDER_TYPE_BUY']:
            return 'BUY'
        elif direction_str in ['SELL', 'SHORT', '1', 'ORDER_TYPE_SELL']:
            return 'SELL'
        
        return 'BUY'  # Default
    
    def migrate_all_plugins(self, start_date: Optional[str] = None,
                            dry_run: bool = False) -> Dict[str, Dict[str, int]]:
        """
        Migrate trades for all known plugins.
        
        Args:
            start_date: Start date filter
            dry_run: If True, don't actually migrate
            
        Returns:
            Dictionary of plugin_id -> migration stats
        """
        results = {}
        
        for plugin_id in self.PLUGIN_PATTERNS.keys():
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing plugin: {plugin_id}")
            logger.info(f"{'='*50}")
            
            self.stats = {
                'total_found': 0,
                'migrated': 0,
                'skipped': 0,
                'errors': 0
            }
            
            results[plugin_id] = self.migrate_trades_to_plugin_db(
                plugin_id, start_date, dry_run=dry_run
            )
        
        return results
    
    def get_legacy_db_info(self) -> Dict[str, Any]:
        """Get information about the legacy database."""
        if not self.legacy_connection:
            self.connect()
        
        cursor = self.legacy_connection.cursor()
        
        # Get tables
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        
        info = {
            'path': self.legacy_db_path,
            'tables': [t[0] for t in tables],
            'trade_counts': {}
        }
        
        # Count trades per table
        for table in info['tables']:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                info['trade_counts'][table] = count
            except:
                pass
        
        return info


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate trades from legacy database to plugin databases'
    )
    
    parser.add_argument(
        '--plugin', '-p',
        help='Plugin ID to migrate (e.g., combined_v3)'
    )
    
    parser.add_argument(
        '--all-plugins', '-a',
        action='store_true',
        help='Migrate all known plugins'
    )
    
    parser.add_argument(
        '--start-date', '-s',
        help='Start date filter (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date', '-e',
        help='End date filter (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Dry run mode - show what would be migrated without making changes'
    )
    
    parser.add_argument(
        '--legacy-db', '-l',
        help='Path to legacy database (auto-detected if not specified)'
    )
    
    parser.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show legacy database info and exit'
    )
    
    args = parser.parse_args()
    
    try:
        migrator = LegacyDatabaseMigrator(args.legacy_db)
        
        if args.info:
            info = migrator.get_legacy_db_info()
            print(f"\nLegacy Database Info:")
            print(f"  Path: {info['path']}")
            print(f"  Tables: {', '.join(info['tables'])}")
            print(f"  Record counts:")
            for table, count in info['trade_counts'].items():
                print(f"    {table}: {count}")
            return
        
        if args.all_plugins:
            results = migrator.migrate_all_plugins(
                start_date=args.start_date,
                dry_run=args.dry_run
            )
            
            print("\n" + "="*50)
            print("MIGRATION SUMMARY")
            print("="*50)
            
            total_migrated = 0
            for plugin_id, stats in results.items():
                print(f"\n{plugin_id}:")
                print(f"  Found: {stats['total_found']}")
                print(f"  Migrated: {stats['migrated']}")
                print(f"  Skipped: {stats['skipped']}")
                print(f"  Errors: {stats['errors']}")
                total_migrated += stats['migrated']
            
            print(f"\nTotal trades migrated: {total_migrated}")
            
        elif args.plugin:
            stats = migrator.migrate_trades_to_plugin_db(
                args.plugin,
                start_date=args.start_date,
                end_date=args.end_date,
                dry_run=args.dry_run
            )
            
            print(f"\nMigration complete for {args.plugin}")
            print(f"  Migrated: {stats['migrated']} trades")
            
        else:
            parser.print_help()
            print("\nError: Please specify --plugin or --all-plugins")
            sys.exit(1)
            
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        if 'migrator' in locals():
            migrator.disconnect()


if __name__ == "__main__":
    main()
