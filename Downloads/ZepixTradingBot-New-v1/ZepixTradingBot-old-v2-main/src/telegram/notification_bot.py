"""
Notification Bot - V5 Hybrid Plugin Architecture

The Notification Bot handles all trade alerts and system notifications.
This bot is dedicated to sending real-time trading information.

Part of Document 01: Project Overview - Multi-Telegram System
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels."""
    CRITICAL = 1  # Stop loss hit, errors
    HIGH = 2      # Trade entries/exits
    MEDIUM = 3    # Profit booking, re-entries
    LOW = 4       # Daily summaries
    INFO = 5      # General information


class NotificationBot:
    """
    Notification Bot for trade alerts and system notifications.
    
    Responsibilities:
    - Send trade entry notifications
    - Send trade exit notifications
    - Send profit booking alerts
    - Send re-entry notifications
    - Send system alerts (errors, warnings)
    - Priority-based message queuing
    
    Notification Types:
    - ENTRY: New trade opened
    - EXIT: Trade closed
    - PROFIT: Profit booked
    - REENTRY: Re-entry triggered
    - SL_HIT: Stop loss triggered
    - ERROR: System error
    - WARNING: System warning
    
    Benefits:
    - Dedicated channel for trade alerts
    - No clutter from commands
    - Priority-based delivery
    - Clear notification formatting
    
    Usage:
        bot = NotificationBot(token, config)
        await bot.send_entry_notification(trade_data)
    """
    
    def __init__(self, token: str, config: Dict[str, Any]):
        """
        Initialize Notification Bot.
        
        Args:
            token: Telegram bot token
            config: Bot configuration
        """
        self.token = token
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.NotificationBot")
        
        # Chat ID for notifications
        self.chat_id = config.get("telegram_chat_id")
        
        # Bot state
        self.is_running = False
        self.started_at: Optional[datetime] = None
        
        # Notification statistics
        self.stats = {
            "total_sent": 0,
            "entries": 0,
            "exits": 0,
            "errors": 0
        }
        
        self.logger.info("NotificationBot initialized")
    
    async def start(self):
        """Start the notification bot."""
        self.is_running = True
        self.started_at = datetime.now()
        self.logger.info("NotificationBot started")
        
        # TODO: Initialize telegram bot
        # This is a skeleton - full implementation in Phase 2
    
    async def stop(self):
        """Stop the notification bot."""
        self.is_running = False
        self.logger.info("NotificationBot stopped")
        
        # TODO: Stop telegram bot
        # This is a skeleton - full implementation in Phase 2
    
    async def send_message(
        self,
        text: str,
        chat_id: Optional[int] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Send a notification message.
        
        Args:
            text: Message text
            chat_id: Target chat (None = default)
            priority: Message priority
            parse_mode: Message parse mode
            
        Returns:
            bool: True if sent successfully
        """
        target_chat = chat_id or self.chat_id
        
        self.logger.debug(
            f"Sending notification [{priority.name}] to {target_chat}: {text[:50]}..."
        )
        
        # TODO: Implement actual message sending with priority queue
        # This is a skeleton - full implementation in Phase 2
        
        self.stats["total_sent"] += 1
        return True
    
    async def send_entry_notification(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float,
        sl_price: float,
        tp_price: float,
        plugin_id: str,
        logic_type: str = "",
        order_type: str = ""
    ):
        """
        Send trade entry notification.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            entry_price: Entry price
            sl_price: Stop loss price
            tp_price: Take profit price
            plugin_id: Plugin that placed the trade
            logic_type: Logic type (e.g., LOGIC1, LOGIC2)
            order_type: Order type (e.g., ORDER_A, ORDER_B)
        """
        emoji = "🟢" if direction == "BUY" else "🔴"
        
        message = (
            f"{emoji} *NEW ENTRY*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Direction:* {direction}\n"
            f"*Lot Size:* {lot_size}\n"
            f"*Entry:* {entry_price}\n"
            f"*SL:* {sl_price}\n"
            f"*TP:* {tp_price}\n"
            f"*Plugin:* {plugin_id}\n"
        )
        
        if logic_type:
            message += f"*Logic:* {logic_type}\n"
        if order_type:
            message += f"*Order:* {order_type}\n"
        
        await self.send_message(message, priority=NotificationPriority.HIGH)
        self.stats["entries"] += 1
    
    async def send_exit_notification(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float,
        exit_price: float,
        pnl: float,
        exit_reason: str,
        plugin_id: str
    ):
        """
        Send trade exit notification.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/Loss amount
            exit_reason: Reason for exit
            plugin_id: Plugin that managed the trade
        """
        emoji = "💰" if pnl >= 0 else "💸"
        pnl_text = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
        
        message = (
            f"{emoji} *TRADE CLOSED*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Direction:* {direction}\n"
            f"*Lot Size:* {lot_size}\n"
            f"*Entry:* {entry_price}\n"
            f"*Exit:* {exit_price}\n"
            f"*P/L:* {pnl_text}\n"
            f"*Reason:* {exit_reason}\n"
            f"*Plugin:* {plugin_id}\n"
        )
        
        priority = NotificationPriority.CRITICAL if pnl < 0 else NotificationPriority.HIGH
        await self.send_message(message, priority=priority)
        self.stats["exits"] += 1
    
    async def send_profit_booking_notification(
        self,
        symbol: str,
        level: int,
        profit_booked: float,
        orders_closed: int,
        orders_placed: int,
        plugin_id: str
    ):
        """
        Send profit booking notification.
        
        Args:
            symbol: Trading symbol
            level: Profit booking level
            profit_booked: Amount of profit booked
            orders_closed: Number of orders closed
            orders_placed: Number of new orders placed
            plugin_id: Plugin managing the chain
        """
        message = (
            f"📈 *PROFIT BOOKED*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Level:* {level}\n"
            f"*Profit:* +${profit_booked:.2f}\n"
            f"*Closed:* {orders_closed} orders\n"
            f"*Placed:* {orders_placed} new orders\n"
            f"*Plugin:* {plugin_id}\n"
        )
        
        await self.send_message(message, priority=NotificationPriority.MEDIUM)
    
    async def send_reentry_notification(
        self,
        symbol: str,
        direction: str,
        reentry_type: str,
        level: int,
        plugin_id: str
    ):
        """
        Send re-entry notification.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            reentry_type: Type of re-entry (SL_HUNT, TP_CONT, EXIT_CONT)
            level: Re-entry level
            plugin_id: Plugin managing the re-entry
        """
        message = (
            f"🔄 *RE-ENTRY*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Direction:* {direction}\n"
            f"*Type:* {reentry_type}\n"
            f"*Level:* {level}\n"
            f"*Plugin:* {plugin_id}\n"
        )
        
        await self.send_message(message, priority=NotificationPriority.MEDIUM)
    
    async def send_error_notification(
        self,
        error_type: str,
        message: str,
        plugin_id: str = "",
        details: str = ""
    ):
        """
        Send error notification.
        
        Args:
            error_type: Type of error
            message: Error message
            plugin_id: Plugin that encountered the error
            details: Additional details
        """
        error_message = (
            f"🚨 *ERROR*\n\n"
            f"*Type:* {error_type}\n"
            f"*Message:* {message}\n"
        )
        
        if plugin_id:
            error_message += f"*Plugin:* {plugin_id}\n"
        if details:
            error_message += f"*Details:* {details}\n"
        
        await self.send_message(error_message, priority=NotificationPriority.CRITICAL)
        self.stats["errors"] += 1
    
    async def send_warning_notification(
        self,
        warning_type: str,
        message: str,
        plugin_id: str = ""
    ):
        """
        Send warning notification.
        
        Args:
            warning_type: Type of warning
            message: Warning message
            plugin_id: Related plugin
        """
        warning_message = (
            f"⚠️ *WARNING*\n\n"
            f"*Type:* {warning_type}\n"
            f"*Message:* {message}\n"
        )
        
        if plugin_id:
            warning_message += f"*Plugin:* {plugin_id}\n"
        
        await self.send_message(warning_message, priority=NotificationPriority.HIGH)
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status."""
        return {
            "type": "notification",
            "is_running": self.is_running,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stats": self.stats.copy()
        }
