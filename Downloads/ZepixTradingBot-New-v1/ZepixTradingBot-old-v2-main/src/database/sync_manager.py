"""
Database Synchronization Manager

Document 09: Database Schema Designs
Implements the DatabaseSyncManager for syncing V3 and V6 plugin data
to the central database every 5 minutes.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .v3_database import V3Database
from .v6_database import V6Database
from .central_database import CentralDatabase

logger = logging.getLogger(__name__)


class DatabaseSyncManager:
    """
    Database Synchronization Manager.
    
    Syncs trade data from V3 and V6 plugin databases to the central
    aggregated_trades table every 5 minutes.
    
    Features:
    - Incremental sync (only new trades since last sync)
    - Async operation for non-blocking sync
    - Error handling and retry logic
    - Sync status tracking
    """
    
    DEFAULT_SYNC_INTERVAL = 5 * 60  # 5 minutes in seconds
    
    def __init__(self, v3_db: Optional[V3Database] = None,
                 v6_db: Optional[V6Database] = None,
                 central_db: Optional[CentralDatabase] = None,
                 sync_interval: int = DEFAULT_SYNC_INTERVAL):
        """
        Initialize sync manager.
        
        Args:
            v3_db: V3 database instance (optional, will create if not provided)
            v6_db: V6 database instance (optional, will create if not provided)
            central_db: Central database instance (optional, will create if not provided)
            sync_interval: Sync interval in seconds (default: 5 minutes)
        """
        self.v3_db = v3_db or V3Database()
        self.v6_db = v6_db or V6Database()
        self.central_db = central_db or CentralDatabase()
        self.sync_interval = sync_interval
        
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._last_sync_time: Optional[datetime] = None
        self._sync_stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "v3_trades_synced": 0,
            "v6_trades_synced": 0,
            "last_error": None
        }
    
    @property
    def is_running(self) -> bool:
        """Check if sync manager is running."""
        return self._running
    
    @property
    def last_sync_time(self) -> Optional[datetime]:
        """Get last sync time."""
        return self._last_sync_time
    
    @property
    def sync_stats(self) -> Dict[str, Any]:
        """Get sync statistics."""
        return self._sync_stats.copy()
    
    async def start(self) -> None:
        """Start the sync manager background task."""
        if self._running:
            self.logger.warning("Sync manager already running")
            return
        
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        self.logger.info(f"Sync manager started (interval: {self.sync_interval}s)")
        
        # Log event
        self.central_db.log_event(
            event_type="SYNC_MANAGER_STARTED",
            message=f"Database sync manager started with {self.sync_interval}s interval",
            severity="INFO",
            source="DatabaseSyncManager"
        )
    
    async def stop(self) -> None:
        """Stop the sync manager background task."""
        if not self._running:
            return
        
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
            self._sync_task = None
        
        self.logger.info("Sync manager stopped")
        
        # Log event
        self.central_db.log_event(
            event_type="SYNC_MANAGER_STOPPED",
            message="Database sync manager stopped",
            severity="INFO",
            source="DatabaseSyncManager"
        )
    
    async def _sync_loop(self) -> None:
        """Background sync loop."""
        while self._running:
            try:
                await self.sync_all_plugins()
            except Exception as e:
                self.logger.error(f"Sync error: {e}")
                self._sync_stats["last_error"] = str(e)
            
            # Wait for next sync interval
            await asyncio.sleep(self.sync_interval)
    
    async def sync_all_plugins(self) -> Dict[str, Any]:
        """
        Sync all plugin databases to central database.
        
        Returns:
            Sync results dictionary
        """
        self._sync_stats["total_syncs"] += 1
        results = {
            "v3_synced": 0,
            "v6_synced": 0,
            "errors": []
        }
        
        try:
            # Sync V3 trades
            v3_count = await self.sync_v3_trades()
            results["v3_synced"] = v3_count
            self._sync_stats["v3_trades_synced"] += v3_count
            
            # Sync V6 trades (all 4 timeframes)
            v6_count = await self.sync_v6_trades()
            results["v6_synced"] = v6_count
            self._sync_stats["v6_trades_synced"] += v6_count
            
            # Update last sync time
            self._last_sync_time = datetime.now()
            self.central_db.set_config("last_sync_time", self._last_sync_time.isoformat())
            
            self._sync_stats["successful_syncs"] += 1
            
            self.logger.info(f"Sync complete: V3={v3_count}, V6={v6_count}")
            
        except Exception as e:
            self._sync_stats["failed_syncs"] += 1
            self._sync_stats["last_error"] = str(e)
            results["errors"].append(str(e))
            
            # Log error event
            self.central_db.log_event(
                event_type="SYNC_ERROR",
                message=f"Database sync failed: {e}",
                severity="ERROR",
                source="DatabaseSyncManager",
                details=str(e)
            )
        
        return results
    
    async def sync_v3_trades(self) -> int:
        """
        Sync V3 trades to central database.
        
        Returns:
            Number of trades synced
        """
        # Get last synced trade ID
        last_id = self.central_db.get_last_synced_trade_id("combined_v3")
        
        # Get new trades from V3 database
        conn = self.v3_db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, order_a_ticket, symbol, direction, 
                   order_a_lot_size, entry_price, entry_time, exit_time,
                   total_profit_pips, total_profit_dollars, status
            FROM combined_v3_trades
            WHERE id > ?
            ORDER BY id ASC
        """, (last_id,))
        
        new_trades = cursor.fetchall()
        synced_count = 0
        
        for trade in new_trades:
            try:
                self.central_db.add_aggregated_trade({
                    "plugin_id": "combined_v3",
                    "plugin_type": "V3_COMBINED",
                    "source_trade_id": trade["id"],
                    "mt5_ticket": trade["order_a_ticket"],
                    "symbol": trade["symbol"],
                    "direction": trade["direction"],
                    "lot_size": trade["order_a_lot_size"],
                    "entry_price": trade["entry_price"],
                    "entry_time": trade["entry_time"],
                    "exit_time": trade["exit_time"],
                    "profit_pips": trade["total_profit_pips"],
                    "profit_dollars": trade["total_profit_dollars"],
                    "status": trade["status"]
                })
                synced_count += 1
            except Exception as e:
                self.logger.error(f"Error syncing V3 trade {trade['id']}: {e}")
        
        return synced_count
    
    async def sync_v6_trades(self) -> int:
        """
        Sync all V6 plugin trades to central database.
        
        Returns:
            Total number of trades synced
        """
        total_synced = 0
        
        # Sync each V6 plugin
        for plugin_id in ["price_action_1m", "price_action_5m", "price_action_15m", "price_action_1h"]:
            count = await self._sync_v6_plugin(plugin_id)
            total_synced += count
        
        return total_synced
    
    async def _sync_v6_plugin(self, plugin_id: str) -> int:
        """
        Sync a specific V6 plugin's trades.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Number of trades synced
        """
        # Get last synced trade ID
        last_id = self.central_db.get_last_synced_trade_id(plugin_id)
        
        # Get table and config for this plugin
        table = self.v6_db.get_table_for_plugin(plugin_id)
        config = self.v6_db.PLUGIN_CONFIGS.get(plugin_id, {})
        
        # Build query based on order type
        if config.get("order_type") == "DUAL":
            select_cols = """
                id, order_a_ticket as mt5_ticket, symbol, direction,
                order_a_lot_size as lot_size, entry_price, entry_time, exit_time,
                total_profit_pips as profit_pips, total_profit_dollars as profit_dollars, status
            """
        elif config.get("order_type") == "B_ONLY":
            select_cols = """
                id, order_b_ticket as mt5_ticket, symbol, direction,
                lot_size, entry_price, entry_time, exit_time,
                profit_pips, profit_dollars, status
            """
        else:  # A_ONLY
            select_cols = """
                id, order_a_ticket as mt5_ticket, symbol, direction,
                lot_size, entry_price, entry_time, exit_time,
                profit_pips, profit_dollars, status
            """
        
        conn = self.v6_db.connect()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT {select_cols}
            FROM {table}
            WHERE id > ?
            ORDER BY id ASC
        """, (last_id,))
        
        new_trades = cursor.fetchall()
        synced_count = 0
        
        for trade in new_trades:
            try:
                self.central_db.add_aggregated_trade({
                    "plugin_id": plugin_id,
                    "plugin_type": "V6_PRICE_ACTION",
                    "source_trade_id": trade["id"],
                    "mt5_ticket": trade["mt5_ticket"],
                    "symbol": trade["symbol"],
                    "direction": trade["direction"],
                    "lot_size": trade["lot_size"],
                    "entry_price": trade["entry_price"],
                    "entry_time": trade["entry_time"],
                    "exit_time": trade["exit_time"],
                    "profit_pips": trade["profit_pips"],
                    "profit_dollars": trade["profit_dollars"],
                    "status": trade["status"]
                })
                synced_count += 1
            except Exception as e:
                self.logger.error(f"Error syncing {plugin_id} trade {trade['id']}: {e}")
        
        return synced_count
    
    def sync_trade_update(self, plugin_id: str, source_trade_id: int,
                          updates: Dict[str, Any]) -> bool:
        """
        Sync a trade update to central database.
        
        This is called when a trade is updated (e.g., closed) to
        immediately sync the update without waiting for the next
        scheduled sync.
        
        Args:
            plugin_id: Plugin identifier
            source_trade_id: Source trade ID in plugin database
            updates: Fields to update
            
        Returns:
            True if synced successfully
        """
        conn = self.central_db.connect()
        cursor = conn.cursor()
        
        # Find the aggregated trade
        cursor.execute(
            "SELECT id FROM aggregated_trades WHERE plugin_id = ? AND source_trade_id = ?",
            (plugin_id, source_trade_id)
        )
        row = cursor.fetchone()
        
        if row:
            return self.central_db.update_aggregated_trade(row["id"], updates)
        
        return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current sync status.
        
        Returns:
            Status dictionary
        """
        return {
            "running": self._running,
            "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None,
            "sync_interval_seconds": self.sync_interval,
            "stats": self._sync_stats.copy()
        }
    
    def force_sync(self) -> Dict[str, Any]:
        """
        Force an immediate sync (synchronous version).
        
        Returns:
            Sync results
        """
        import asyncio
        
        # Run sync in event loop
        loop = asyncio.new_event_loop()
        try:
            results = loop.run_until_complete(self.sync_all_plugins())
        finally:
            loop.close()
        
        return results
    
    def close(self) -> None:
        """Close all database connections."""
        self.v3_db.close()
        self.v6_db.close()
        self.central_db.close()


# Convenience function for creating sync manager
def create_sync_manager(sync_interval: int = DatabaseSyncManager.DEFAULT_SYNC_INTERVAL) -> DatabaseSyncManager:
    """
    Create a new DatabaseSyncManager instance.
    
    Args:
        sync_interval: Sync interval in seconds
        
    Returns:
        DatabaseSyncManager instance
    """
    return DatabaseSyncManager(sync_interval=sync_interval)
