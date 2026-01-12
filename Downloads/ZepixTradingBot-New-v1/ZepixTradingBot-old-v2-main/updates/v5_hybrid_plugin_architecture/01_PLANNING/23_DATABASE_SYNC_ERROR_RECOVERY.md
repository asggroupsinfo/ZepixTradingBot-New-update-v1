# DATABASE SYNC ERROR RECOVERY SYSTEM

**Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Production-Ready Implementation  
**Priority:** 🔴 HIGH (Critical for Multi-DB Architecture)

---

## 🎯 PURPOSE

Ensure **reliable synchronization** between plugin databases (V3/V6) and central database with comprehensive error handling, retry logic, and monitoring.

**Without This System:**
- Sync failures could accumulate silently
- Dashboard shows incomplete/outdated data
- No visibility into sync health

**With This System:**
- Automatic retry on transient failures
- Alerts on persistent sync issues
- Manual sync trigger for recovery
- Complete audit trail

---

## 🏗️ ENHANCED DATABASE SYNC MANAGER

### **File:** `src/core/database_sync_manager.py`

```python
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Sync operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"

@dataclass
class SyncResult:
    """Result of a sync operation"""
    plugin_id: str
    status: SyncStatus
    records_synced: int
    error_message: Optional[str]
    duration_ms: int
    timestamp: datetime
    retry_count: int = 0

class DatabaseSyncManager:
    """
    Enhanced sync manager with error recovery
    """
    
    def __init__(self, config):
        self.config = config
        
        # Database paths
        self.v3_db_path = 'data/zepix_combined.db'
        self.v6_db_path = 'data/zepix_price_action.db'
        self.central_db_path = 'data/zepix_bot.db'
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay_seconds = 5
        self.backoff_multiplier = 2
        
        # Sync tracking
        self.last_sync_time = {}  # plugin_id -> datetime
        self.sync_history = []    # List of SyncResult
        self.max_history = 1000
        
        # Error tracking
        self.consecutive_failures = {}  # plugin_id -> count
        self.alert_threshold = 3  # Alert after N consecutive failures
        
        # Control
        self._running = False
        self._sync_task = None
        self._manual_sync_event = asyncio.Event()
        
        # Statistics
        self.stats = {
            'total_syncs': 0,
            'total_success': 0,
            'total_failures': 0,
            'total_retries': 0,
            'total_records_synced': 0
        }
    
    async def start(self):
        """Start automatic sync scheduler"""
        if self._running:
            return
        
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        logger.info("✅ Database sync manager started (interval: 5 minutes)")
    
    async def stop(self):
        """Stop sync scheduler"""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Database sync manager stopped")
    
    async def _sync_loop(self):
        """Main sync loop (runs every 5 minutes)"""
        while self._running:
            try:
                # Wait for 5 minutes OR manual trigger
                try:
                    await asyncio.wait_for(
                        self._manual_sync_event.wait(),
                        timeout=300  # 5 minutes
                    )
                    # Manual sync triggered
                    self._manual_sync_event.clear()
                    logger.info("🔄 Manual sync triggered")
                except asyncio.TimeoutError:
                    # Regular scheduled sync
                    pass
                
                # Perform sync
                await self.sync_all_plugins()
                
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def sync_all_plugins(self) -> List[SyncResult]:
        """
        Sync all plugins with retry logic
        
        Returns:
            List of sync results for each plugin
        """
        results = []
        
        # V3 Combined Logic
        v3_result = await self._sync_plugin_with_retry('combined_v3', self.v3_db_path)
        results.append(v3_result)
        
        # V6 Price Action Plugins (all share same DB)
        for plugin_id in ['price_action_1m', 'price_action_5m', 'price_action_15m', 'price_action_1h']:
            v6_result = await self._sync_plugin_with_retry(plugin_id, self.v6_db_path)
            results.append(v6_result)
        
        # Check for persistent failures
        await self._check_and_alert_failures()
        
        return results
    
    async def _sync_plugin_with_retry(
        self,
        plugin_id: str,
        plugin_db_path: str
    ) -> SyncResult:
        """
        Sync single plugin with retry logic
        
        Retry Strategy:
        1. Try 1: Immediate
        2. Try 2: After 5 seconds
        3. Try 3: After 10 seconds (5 * 2^1)
        4. Try 4: After 20 seconds (5 * 2^2)
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # Attempt sync
                result = await self._sync_plugin(plugin_id, plugin_db_path)
                
                if result.status == SyncStatus.SUCCESS:
                    # Reset failure counter
                    self.consecutive_failures[plugin_id] = 0
                    return result
                else:
                    last_error = result.error_message
                    raise Exception(f"Sync failed: {last_error}")
                
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                
                if retry_count <= self.max_retries:
                    # Calculate backoff delay
                    delay = self.retry_delay_seconds * (self.backoff_multiplier ** (retry_count - 1))
                    
                    logger.warning(
                        f"⚠️ Sync failed for {plugin_id} (attempt {retry_count}/{self.max_retries}). "
                        f"Retrying in {delay}s... Error: {e}"
                    )
                    
                    self.stats['total_retries'] += 1
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
                else:
                    # Max retries exhausted
                    logger.error(
                        f"❌ Sync FAILED for {plugin_id} after {self.max_retries} retries. Error: {e}"
                    )
                    
                    # Track consecutive failures
                    self.consecutive_failures[plugin_id] = \
                        self.consecutive_failures.get(plugin_id, 0) + 1
                    
                    # Return failure result
                    return SyncResult(
                        plugin_id=plugin_id,
                        status=SyncStatus.FAILED,
                        records_synced=0,
                        error_message=last_error,
                        duration_ms=0,
                        timestamp=datetime.now(),
                        retry_count=retry_count
                    )
    
    async def _sync_plugin(
        self,
        plugin_id: str,
        plugin_db_path: str
    ) -> SyncResult:
        """
        Perform actual sync (single attempt)
        
        Returns:
            SyncResult with outcome
        """
        start_time = datetime.now()
        
        try:
            # Connect to databases
            plugin_db = sqlite3.connect(plugin_db_path)
            central_db = sqlite3.connect(self.central_db_path)
            
            plugin_db.row_factory = sqlite3.Row
            
            # Get last synced ID from central DB
            last_synced_id = self._get_last_synced_id(central_db, plugin_id)
            
            # Get new records from plugin DB
            new_records = self._fetch_new_records(
                plugin_db,
                plugin_id,
                last_synced_id
            )
            
            if len(new_records) == 0:
                # No new records
                plugin_db.close()
                central_db.close()
                
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                return SyncResult(
                    plugin_id=plugin_id,
                    status=SyncStatus.SKIPPED,
                    records_synced=0,
                    error_message=None,
                    duration_ms=int(duration),
                    timestamp=datetime.now()
                )
            
            # Insert records into central DB
            self._insert_to_central(central_db, plugin_id, new_records)
            
            # Commit
            central_db.commit()
            
            # Close connections
            plugin_db.close()
            central_db.close()
            
            # Calculate metrics
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update stats
            self.stats['total_syncs'] += 1
            self.stats['total_success'] += 1
            self.stats['total_records_synced'] += len(new_records)
            
            # Record last sync time
            self.last_sync_time[plugin_id] = datetime.now()
            
            logger.info(
                f"✅ Synced {len(new_records)} records for {plugin_id} in {int(duration)}ms"
            )
            
            result = SyncResult(
                plugin_id=plugin_id,
                status=SyncStatus.SUCCESS,
                records_synced=len(new_records),
                error_message=None,
                duration_ms=int(duration),
                timestamp=datetime.now()
            )
            
            # Add to history
            self._add_to_history(result)
            
            return result
            
        except Exception as e:
            # Ensure connections are closed
            try:
                plugin_db.close()
                central_db.close()
            except:
                pass
            
            # Update stats
            self.stats['total_syncs'] += 1
            self.stats['total_failures'] += 1
            
            raise
    
    def _get_last_synced_id(self, central_db, plugin_id: str) -> int:
        """Get the last synced record ID for this plugin"""
        cursor = central_db.execute("""
            SELECT COALESCE(MAX(id), 0) as max_id
            FROM aggregated_trades
            WHERE plugin_id = ?
        """, (plugin_id,))
        
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def _fetch_new_records(
        self,
        plugin_db,
        plugin_id: str,
        last_synced_id: int
    ) -> List[Dict]:
        """Fetch new records from plugin database"""
        
        # Determine table name based on plugin
        table_mapping = {
            'combined_v3': 'combined_v3_trades',
            'price_action_1m': 'price_action_1m_trades',
            'price_action_5m': 'price_action_5m_trades',
            'price_action_15m': 'price_action_15m_trades',
            'price_action_1h': 'price_action_1h_trades'
        }
        
        table_name = table_mapping.get(plugin_id)
        if not table_name:
            raise ValueError(f"Unknown plugin: {plugin_id}")
        
        # Query based on plugin type
        if plugin_id == 'combined_v3':
            cursor = plugin_db.execute(f"""
                SELECT 
                    id,
                    order_a_ticket as mt5_ticket,
                    symbol,
                    direction,
                    order_a_lot_size + order_b_lot_size as lot_size,
                    entry_time,
                    exit_time,
                    total_profit_dollars as profit_dollars,
                    status
                FROM {table_name}
                WHERE id > ?
                ORDER BY id
            """, (last_synced_id,))
        else:
            # V6 plugins
            cursor = plugin_db.execute(f"""
                SELECT 
                    id,
                    order_b_ticket as mt5_ticket,
                    symbol,
                    direction,
                    lot_size,
                    entry_time,
                    exit_time,
                    profit_dollars,
                    status
                FROM {table_name}
                WHERE id > ?
                ORDER BY id
            """, (last_synced_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _insert_to_central(
        self,
        central_db,
        plugin_id: str,
        records: List[Dict]
    ):
        """Insert records into central aggregated_trades table"""
        
        # Determine plugin type
        plugin_type = 'V3_COMBINED' if plugin_id == 'combined_v3' else 'V6_PRICE_ACTION'
        
        for record in records:
            central_db.execute("""
                INSERT INTO aggregated_trades
                (plugin_id, plugin_type, mt5_ticket, symbol, direction,
                 lot_size, entry_time, exit_time, profit_dollars, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_id,
                plugin_type,
                record.get('mt5_ticket'),
                record.get('symbol'),
                record.get('direction'),
                record.get('lot_size'),
                record.get('entry_time'),
                record.get('exit_time'),
                record.get('profit_dollars'),
                record.get('status')
            ))
    
    def _add_to_history(self, result: SyncResult):
        """Add result to history (keep last 1000)"""
        self.sync_history.append(result)
        
        if len(self.sync_history) > self.max_history:
            self.sync_history = self.sync_history[-self.max_history:]
    
    async def _check_and_alert_failures(self):
        """Check for persistent failures and alert"""
        for plugin_id, failure_count in self.consecutive_failures.items():
            if failure_count >= self.alert_threshold:
                # Send alert
                await self._send_sync_alert(
                    plugin_id=plugin_id,
                    failure_count=failure_count
                )
    
    async def _send_sync_alert(self, plugin_id: str, failure_count: int):
        """Send alert about sync failures"""
        from main import telegram_manager  # Avoid circular import
        
        alert_text = (
            f"🚨 <b>DATABASE SYNC ALERT</b>\n\n"
            f"Plugin: <code>{plugin_id}</code>\n"
            f"Consecutive Failures: {failure_count}\n"
            f"Status: <b>SYNC DEGRADED</b>\n\n"
            f"⚠️ Central database may have outdated data.\n"
            f"Use /sync_manual to trigger manual sync.\n"
            f"Use /sync_status to check sync health."
        )
        
        await telegram_manager.send_controller_message(
            chat_id=config['admin_chat_id'],
            text=alert_text,
            priority=MessagePriority.HIGH
        )
        
        logger.error(
            f"🚨 ALERT SENT: {plugin_id} has {failure_count} consecutive sync failures"
        )
    
    # ==========================================
    # MANUAL SYNC TRIGGER
    # ==========================================
    
    async def trigger_manual_sync(self) -> Dict:
        """
        Trigger immediate sync (bypasses 5-minute wait)
        Used via /sync_manual command
        
        Returns:
            Summary of sync results
        """
        logger.info("🔄 Manual sync triggered by admin")
        
        # Set event to trigger sync loop immediately
        self._manual_sync_event.set()
        
        # Wait a bit for sync to complete
        await asyncio.sleep(2)
        
        # Return recent results
        return {
            "triggered": True,
            "message": "Manual sync initiated. Check /sync_status in a moment.",
            "recent_results": [
                {
                    "plugin": r.plugin_id,
                    "status": r.status.value,
                    "records": r.records_synced
                }
                for r in self.sync_history[-5:]
            ]
        }
    
    # ==========================================
    # HEALTH & MONITORING
    # ==========================================
    
    def get_sync_health(self) -> Dict:
        """Get complete sync health status"""
        now = datetime.now()
        
        health = {
            "overall_status": "HEALTHY",
            "plugins": {},
            "statistics": self.stats.copy(),
            "last_run": None
        }
        
        # Check each plugin
        for plugin_id in ['combined_v3', 'price_action_1m', 'price_action_5m', 'price_action_15m', 'price_action_1h']:
            last_sync = self.last_sync_time.get(plugin_id)
            failures = self.consecutive_failures.get(plugin_id, 0)
            
            # Determine status
            if failures >= self.alert_threshold:
                status = "DEGRADED"
                health["overall_status"] = "DEGRADED"
            elif failures > 0:
                status = "WARNING"
                if health["overall_status"] == "HEALTHY":
                    health["overall_status"] = "WARNING"
            else:
                status = "HEALTHY"
            
            # Time since last sync
            if last_sync:
                minutes_since = (now - last_sync).total_seconds() / 60
                last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")
            else:
                minutes_since = 999
                last_sync_str = "Never"
            
            health["plugins"][plugin_id] = {
                "status": status,
                "last_sync": last_sync_str,
                "minutes_since_last_sync": int(minutes_since),
                "consecutive_failures": failures
            }
        
        # Overall last run
        if self.sync_history:
            health["last_run"] = self.sync_history[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return health
```

---

## 🎮 TELEGRAM COMMANDS

### **File:** `src/telegram/controller_bot.py` (Add these handlers)

```python
@controller_bot.command("sync_status")
async def sync_status_command(update, context):
    """Show database sync health"""
    health = database_sync_manager.get_sync_health()
    
    # Format message
    status_emoji = "✅" if health["overall_status"] == "HEALTHY" else "⚠️"
    
    message = f"{status_emoji} <b>DATABASE SYNC STATUS</b>\n\n"
    message += f"Overall: <b>{health['overall_status']}</b>\n"
    message += f"Last Run: {health['last_run']}\n\n"
    
    for plugin_id, plugin_health in health["plugins"].items():
        emoji = "✅" if plugin_health["status"] == "HEALTHY" else "⚠️"
        message += f"{emoji} <code>{plugin_id}</code>\n"
        message += f"   Last Sync: {plugin_health['last_sync']}\n"
        message += f"   Failures: {plugin_health['consecutive_failures']}\n\n"
    
    message += f"📊 <b>Statistics:</b>\n"
    message += f"Total Syncs: {health['statistics']['total_syncs']}\n"
    message += f"Success Rate: {health['statistics']['total_success']}/{health['statistics']['total_syncs']}\n"
    message += f"Records Synced: {health['statistics']['total_records_synced']}\n"
    
    await update.message.reply_text(message, parse_mode='HTML')

@controller_bot.command("sync_manual")
async def sync_manual_command(update, context):
    """Trigger manual sync"""
    result = await database_sync_manager.trigger_manual_sync()
    
    message = "🔄 <b>MANUAL SYNC TRIGGERED</b>\n\n"
    message += f"{result['message']}\n\n"
    message += "Use /sync_status to check results."
    
    await update.message.reply_text(message, parse_mode='HTML')
```

---

## ✅ COMPLETION CHECKLIST

- [x] Retry logic (3 attempts with exponential backoff)
- [x] Failure tracking per plugin
- [x] Alert on persistent failures (3+ consecutive)
- [x] Manual sync trigger command
- [x] Sync health monitoring
- [x] Statistics tracking
- [x] Error logging
- [x] Telegram commands (/sync_status, /sync_manual)

**Status:** ✅ READY FOR IMPLEMENTATION
