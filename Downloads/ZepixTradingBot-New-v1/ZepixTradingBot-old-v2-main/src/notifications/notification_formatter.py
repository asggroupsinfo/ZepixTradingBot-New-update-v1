"""
Notification Formatter - Template-based Message Formatting

Document 19: Notification System Specification
Supports HTML/Markdown, Emojis, and Dynamic Content for all notification types.

Templates:
- Entry (V3 Dual, V6 Single A/B)
- Exit (Profit/Loss)
- TP/SL Hit
- Daily/Weekly Summary
- System Events
- Error Notifications
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import re


class FormatType(Enum):
    """Message format types"""
    PLAIN = "plain"
    HTML = "html"
    MARKDOWN = "markdown"


class TemplateType(Enum):
    """Template types for notifications"""
    # Trade Templates
    ENTRY_V3_DUAL = "entry_v3_dual"
    ENTRY_V6_SINGLE_A = "entry_v6_single_a"
    ENTRY_V6_SINGLE_B = "entry_v6_single_b"
    EXIT_PROFIT = "exit_profit"
    EXIT_LOSS = "exit_loss"
    TP_HIT = "tp_hit"
    SL_HIT = "sl_hit"
    PROFIT_PARTIAL = "profit_partial"
    SL_MODIFIED = "sl_modified"
    BREAKEVEN_MOVED = "breakeven_moved"
    
    # Summary Templates
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    PERFORMANCE_REPORT = "performance_report"
    
    # System Templates
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    EMERGENCY_STOP = "emergency_stop"
    MT5_DISCONNECT = "mt5_disconnect"
    MT5_RECONNECT = "mt5_reconnect"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_ERROR = "plugin_error"
    CONFIG_RELOAD = "config_reload"
    
    # Alert Templates
    ALERT_RECEIVED = "alert_received"
    ALERT_PROCESSED = "alert_processed"
    ALERT_ERROR = "alert_error"
    RISK_ALERT = "risk_alert"
    
    # Generic
    GENERIC = "generic"


@dataclass
class NotificationTemplate:
    """Template definition for notifications"""
    template_type: TemplateType
    template_string: str
    format_type: FormatType = FormatType.PLAIN
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    description: str = ""
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate that all required fields are present"""
        for field_name in self.required_fields:
            if field_name not in data:
                return False
        return True
    
    def get_missing_fields(self, data: Dict[str, Any]) -> List[str]:
        """Get list of missing required fields"""
        return [f for f in self.required_fields if f not in data]


class TemplateManager:
    """
    Manages notification templates
    
    Provides CRUD operations for templates and template rendering.
    """
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load all default notification templates"""
        
        # Entry V3 Dual Orders Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.ENTRY_V3_DUAL,
            template_string="""🟢 ENTRY | {plugin_name}

Symbol: {symbol}
Direction: {direction}
Entry: {entry_price}

Order A (Smart SL):
├─ Lot: {order_a_lot}
├─ SL: {order_a_sl}
└─ TP: {order_a_tp} (TP2)

Order B (Fixed $10 SL):
├─ Lot: {order_b_lot}
├─ SL: {order_b_sl}
└─ TP: {order_b_tp} (TP1)

Signal: {signal_type}
TF: {timeframe} | Logic: {logic_route}
Tickets: #{ticket_a}, #{ticket_b}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price", "signal_type"],
            optional_fields=["order_a_lot", "order_a_sl", "order_a_tp", "order_b_lot", 
                           "order_b_sl", "order_b_tp", "timeframe", "logic_route",
                           "ticket_a", "ticket_b", "timestamp"],
            description="Entry notification for V3 dual order trades"
        ))
        
        # Entry V6 Single Order A Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.ENTRY_V6_SINGLE_A,
            template_string="""🟢 ENTRY | {plugin_name} (ORDER A)

Symbol: {symbol}
Direction: {direction}
Entry: {entry_price}

Order A:
├─ Lot: {lot_size}
├─ SL: {sl_price}
└─ TP: {tp_price}

ADX: {adx} ({adx_strength})
Confidence: {confidence_score}/100 ({confidence_level})
Market State: {market_state}

Ticket: #{ticket}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price"],
            optional_fields=["lot_size", "sl_price", "tp_price", "adx", "adx_strength",
                           "confidence_score", "confidence_level", "market_state",
                           "ticket", "timestamp"],
            description="Entry notification for V6 single Order A trades"
        ))
        
        # Entry V6 Single Order B Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.ENTRY_V6_SINGLE_B,
            template_string="""🟢 ENTRY | {plugin_name} (ORDER B)

Symbol: {symbol}
Direction: {direction}
Entry: {entry_price}

Order B:
├─ Lot: {lot_size}
├─ SL: {sl_price}
└─ TP: {tp_price}

Signal: {signal_type}
Timeframe: {timeframe}

Ticket: #{ticket}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price"],
            optional_fields=["lot_size", "sl_price", "tp_price", "signal_type",
                           "timeframe", "ticket", "timestamp"],
            description="Entry notification for V6 single Order B trades"
        ))
        
        # Exit Profit Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.EXIT_PROFIT,
            template_string="""🔴 EXIT | {plugin_name}

Symbol: {symbol}
Direction: {direction} → CLOSED

Entry: {entry_price} → Exit: {exit_price}
Hold Time: {hold_duration}

✅ P&L: +{profit:.2f} USD
Commission: -{commission:.2f} USD
Net: {net_profit:.2f} USD

Reason: {close_reason}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price", 
                           "exit_price", "profit"],
            optional_fields=["hold_duration", "commission", "net_profit", 
                           "close_reason", "timestamp"],
            description="Exit notification for profitable trades"
        ))
        
        # Exit Loss Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.EXIT_LOSS,
            template_string="""🔴 EXIT | {plugin_name}

Symbol: {symbol}
Direction: {direction} → CLOSED

Entry: {entry_price} → Exit: {exit_price}
Hold Time: {hold_duration}

❌ P&L: {profit:.2f} USD
Commission: -{commission:.2f} USD
Net: {net_profit:.2f} USD

Reason: {close_reason}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price",
                           "exit_price", "profit"],
            optional_fields=["hold_duration", "commission", "net_profit",
                           "close_reason", "timestamp"],
            description="Exit notification for losing trades"
        ))
        
        # TP Hit Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.TP_HIT,
            template_string="""🎯 TP{tp_level} HIT | {plugin_name}

Symbol: {symbol}
Direction: {direction}

Entry: {entry_price} → TP: {tp_price}
Profit: +{profit:.2f} USD

Remaining Position: {remaining_lots} lots
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["tp_level", "plugin_name", "symbol", "direction",
                           "entry_price", "tp_price", "profit"],
            optional_fields=["remaining_lots", "timestamp"],
            description="Take profit hit notification"
        ))
        
        # SL Hit Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.SL_HIT,
            template_string="""🛑 SL HIT | {plugin_name}

Symbol: {symbol}
Direction: {direction}

Entry: {entry_price} → SL: {sl_price}
Loss: {profit:.2f} USD

Reason: {reason}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price",
                           "sl_price", "profit"],
            optional_fields=["reason", "timestamp"],
            description="Stop loss hit notification"
        ))
        
        # Partial Profit Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.PROFIT_PARTIAL,
            template_string="""💰 PARTIAL PROFIT | {plugin_name}

Symbol: {symbol}
Direction: {direction}

Closed: {closed_lots} lots at {close_price}
Profit: +{profit:.2f} USD

Remaining: {remaining_lots} lots
New SL: {new_sl}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "closed_lots",
                           "close_price", "profit"],
            optional_fields=["remaining_lots", "new_sl", "timestamp"],
            description="Partial profit booking notification"
        ))
        
        # SL Modified Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.SL_MODIFIED,
            template_string="""📝 SL MODIFIED | {plugin_name}

Symbol: {symbol}
Direction: {direction}

Old SL: {old_sl} → New SL: {new_sl}
Reason: {reason}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "old_sl", "new_sl"],
            optional_fields=["reason", "timestamp"],
            description="Stop loss modification notification"
        ))
        
        # Breakeven Moved Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.BREAKEVEN_MOVED,
            template_string="""⚖️ BREAKEVEN | {plugin_name}

Symbol: {symbol}
Direction: {direction}

Entry: {entry_price}
SL moved to breakeven: {breakeven_price}
Secured: {secured_profit:.2f} USD

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "symbol", "direction", "entry_price",
                           "breakeven_price"],
            optional_fields=["secured_profit", "timestamp"],
            description="Breakeven move notification"
        ))
        
        # Daily Summary Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.DAILY_SUMMARY,
            template_string="""📊 DAILY SUMMARY | {date}

Performance:
├─ Total Trades: {total_trades}
├─ Winners: {winners} ({win_rate:.1f}%)
├─ Losers: {losers}
└─ Breakeven: {breakeven}

P&L:
├─ Gross Profit: +${gross_profit:.2f}
├─ Gross Loss: -${gross_loss:.2f}
├─ Commission: -${commission:.2f}
└─ Net P&L: {net_pnl_sign}${net_pnl:.2f}

By Plugin:
{plugin_breakdown}

Risk Metrics:
├─ Max Drawdown: {max_drawdown:.1f}%
├─ Risk/Reward: {risk_reward:.2f}
└─ Sharpe Ratio: {sharpe:.2f}""",
            format_type=FormatType.PLAIN,
            required_fields=["date", "total_trades", "winners", "losers", "win_rate",
                           "gross_profit", "gross_loss", "net_pnl"],
            optional_fields=["breakeven", "commission", "net_pnl_sign", "plugin_breakdown",
                           "max_drawdown", "risk_reward", "sharpe"],
            description="Daily trading summary notification"
        ))
        
        # Weekly Summary Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.WEEKLY_SUMMARY,
            template_string="""📈 WEEKLY SUMMARY | {week_start} - {week_end}

Performance:
├─ Total Trades: {total_trades}
├─ Win Rate: {win_rate:.1f}%
├─ Best Day: {best_day} (+${best_day_pnl:.2f})
└─ Worst Day: {worst_day} (-${worst_day_pnl:.2f})

P&L:
├─ Gross Profit: +${gross_profit:.2f}
├─ Gross Loss: -${gross_loss:.2f}
└─ Net P&L: {net_pnl_sign}${net_pnl:.2f}

By Plugin:
{plugin_breakdown}

Risk Metrics:
├─ Max Drawdown: {max_drawdown:.1f}%
├─ Avg Trade Duration: {avg_duration}
└─ Profit Factor: {profit_factor:.2f}""",
            format_type=FormatType.PLAIN,
            required_fields=["week_start", "week_end", "total_trades", "win_rate",
                           "gross_profit", "gross_loss", "net_pnl"],
            optional_fields=["best_day", "best_day_pnl", "worst_day", "worst_day_pnl",
                           "net_pnl_sign", "plugin_breakdown", "max_drawdown",
                           "avg_duration", "profit_factor"],
            description="Weekly trading summary notification"
        ))
        
        # Bot Started Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.BOT_STARTED,
            template_string="""🟢 BOT STARTED

Bot: {bot_name}
Version: {version}
Mode: {mode}

Plugins Loaded: {plugins_count}
Active Symbols: {symbols_count}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["bot_name"],
            optional_fields=["version", "mode", "plugins_count", "symbols_count", "timestamp"],
            description="Bot startup notification"
        ))
        
        # Bot Stopped Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.BOT_STOPPED,
            template_string="""🔴 BOT STOPPED

Bot: {bot_name}
Reason: {reason}

Open Positions: {open_positions}
Session Duration: {session_duration}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["bot_name", "reason"],
            optional_fields=["open_positions", "session_duration", "timestamp"],
            description="Bot shutdown notification"
        ))
        
        # Emergency Stop Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.EMERGENCY_STOP,
            template_string="""🚨 EMERGENCY STOP 🚨

Reason: {reason}
Triggered By: {triggered_by}

Actions Taken:
{actions_taken}

Open Positions: {open_positions}
Pending Orders: {pending_orders}

⚠️ MANUAL INTERVENTION REQUIRED

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["reason"],
            optional_fields=["triggered_by", "actions_taken", "open_positions",
                           "pending_orders", "timestamp"],
            description="Emergency stop notification"
        ))
        
        # MT5 Disconnect Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.MT5_DISCONNECT,
            template_string="""⚠️ MT5 DISCONNECTED

Server: {server}
Account: {account}
Error: {error}

Last Connected: {last_connected}
Retry Attempt: {retry_attempt}/{max_retries}

⚠️ Trading paused until reconnection

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["server", "account"],
            optional_fields=["error", "last_connected", "retry_attempt", 
                           "max_retries", "timestamp"],
            description="MT5 disconnection notification"
        ))
        
        # MT5 Reconnect Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.MT5_RECONNECT,
            template_string="""✅ MT5 RECONNECTED

Server: {server}
Account: {account}

Downtime: {downtime}
Trading resumed

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["server", "account"],
            optional_fields=["downtime", "timestamp"],
            description="MT5 reconnection notification"
        ))
        
        # Plugin Loaded Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.PLUGIN_LOADED,
            template_string="""🔌 PLUGIN LOADED

Plugin: {plugin_name}
Version: {version}
Type: {plugin_type}

Symbols: {symbols}
Mode: {mode}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name"],
            optional_fields=["version", "plugin_type", "symbols", "mode", "timestamp"],
            description="Plugin loaded notification"
        ))
        
        # Plugin Error Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.PLUGIN_ERROR,
            template_string="""❌ PLUGIN ERROR

Plugin: {plugin_name}
Error: {error}

Details: {details}
Stack Trace: {stack_trace}

Action: {action}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["plugin_name", "error"],
            optional_fields=["details", "stack_trace", "action", "timestamp"],
            description="Plugin error notification"
        ))
        
        # Config Reload Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.CONFIG_RELOAD,
            template_string="""🔄 CONFIG RELOADED

Changes:
{changes}

Affected Plugins: {affected_plugins}
Reloaded By: {reloaded_by}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["changes"],
            optional_fields=["affected_plugins", "reloaded_by", "timestamp"],
            description="Configuration reload notification"
        ))
        
        # Alert Received Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.ALERT_RECEIVED,
            template_string="""📥 ALERT RECEIVED

Source: {source}
Symbol: {symbol}
Signal: {signal_type}

Raw Data:
{raw_data}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["source", "symbol", "signal_type"],
            optional_fields=["raw_data", "timestamp"],
            description="Alert received notification"
        ))
        
        # Alert Processed Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.ALERT_PROCESSED,
            template_string="""✅ ALERT PROCESSED

Source: {source}
Symbol: {symbol}
Signal: {signal_type}

Action: {action}
Result: {result}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["source", "symbol", "signal_type", "action"],
            optional_fields=["result", "timestamp"],
            description="Alert processed notification"
        ))
        
        # Alert Error Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.ALERT_ERROR,
            template_string="""❌ ALERT ERROR

Source: {source}
Symbol: {symbol}
Error: {error}

Raw Data:
{raw_data}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["source", "error"],
            optional_fields=["symbol", "raw_data", "timestamp"],
            description="Alert error notification"
        ))
        
        # Risk Alert Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.RISK_ALERT,
            template_string="""⚠️ RISK ALERT

Type: {risk_type}
Level: {risk_level}
Message: {message}

Current Value: {current_value}
Threshold: {threshold}

Recommended Action: {recommended_action}
Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["risk_type", "message"],
            optional_fields=["risk_level", "current_value", "threshold",
                           "recommended_action", "timestamp"],
            description="Risk alert notification"
        ))
        
        # Generic Template
        self.register_template(NotificationTemplate(
            template_type=TemplateType.GENERIC,
            template_string="""📢 {title}

{message}

Time: {timestamp}""",
            format_type=FormatType.PLAIN,
            required_fields=["title", "message"],
            optional_fields=["timestamp"],
            description="Generic notification template"
        ))
    
    def register_template(self, template: NotificationTemplate) -> None:
        """Register a notification template"""
        self.templates[template.template_type.value] = template
    
    def get_template(self, template_type: str) -> Optional[NotificationTemplate]:
        """Get template by type"""
        return self.templates.get(template_type)
    
    def update_template(self, template_type: str, template_string: str) -> bool:
        """Update existing template string"""
        if template_type in self.templates:
            self.templates[template_type].template_string = template_string
            return True
        return False
    
    def delete_template(self, template_type: str) -> bool:
        """Delete a template"""
        if template_type in self.templates:
            del self.templates[template_type]
            return True
        return False
    
    def list_templates(self) -> List[str]:
        """List all registered template types"""
        return list(self.templates.keys())
    
    def get_all_templates(self) -> Dict[str, NotificationTemplate]:
        """Get all templates"""
        return self.templates.copy()


class NotificationFormatter:
    """
    Notification Formatter
    
    Formats notifications using templates with support for
    HTML, Markdown, and plain text formats.
    """
    
    def __init__(self, template_manager: Optional[TemplateManager] = None):
        self.template_manager = template_manager or TemplateManager()
        self.custom_formatters: Dict[str, Callable] = {}
        self.default_format = FormatType.PLAIN
    
    def register_custom_formatter(self, notification_type: str, formatter: Callable) -> None:
        """Register custom formatter for notification type"""
        self.custom_formatters[notification_type] = formatter
    
    def format(
        self,
        notification_type: str,
        data: Dict[str, Any],
        format_type: Optional[FormatType] = None
    ) -> str:
        """
        Format notification using template
        
        Args:
            notification_type: Type of notification
            data: Data to fill template
            format_type: Override format type
            
        Returns:
            Formatted notification string
        """
        # Check for custom formatter first
        if notification_type in self.custom_formatters:
            return self.custom_formatters[notification_type](data)
        
        # Get template
        template = self.template_manager.get_template(notification_type)
        if not template:
            # Use generic template
            template = self.template_manager.get_template("generic")
            if not template:
                return f"{notification_type.upper()}: {data}"
            data = {
                "title": notification_type.upper().replace("_", " "),
                "message": str(data),
                "timestamp": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
        
        # Add default timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add default values for optional fields
        data = self._add_defaults(data, template)
        
        # Format template
        try:
            formatted = template.template_string.format(**data)
        except KeyError as e:
            # Handle missing keys gracefully
            formatted = self._safe_format(template.template_string, data)
        
        # Convert format if needed
        target_format = format_type or template.format_type or self.default_format
        if target_format == FormatType.HTML:
            formatted = self._to_html(formatted)
        elif target_format == FormatType.MARKDOWN:
            formatted = self._to_markdown(formatted)
        
        return formatted
    
    def _add_defaults(self, data: Dict[str, Any], template: NotificationTemplate) -> Dict[str, Any]:
        """Add default values for missing optional fields"""
        result = data.copy()
        
        # Default values for common fields
        defaults = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "commission": 0.0,
            "net_profit": data.get("profit", 0.0),
            "net_pnl_sign": "+" if data.get("net_pnl", 0) >= 0 else "",
            "hold_duration": "N/A",
            "close_reason": "Manual",
            "remaining_lots": 0.0,
            "reason": "N/A",
            "breakeven": 0,
            "plugin_breakdown": "N/A",
            "max_drawdown": 0.0,
            "risk_reward": 0.0,
            "sharpe": 0.0,
            "version": "1.0.0",
            "mode": "Live",
            "plugins_count": 0,
            "symbols_count": 0,
            "open_positions": 0,
            "pending_orders": 0,
            "session_duration": "N/A",
            "triggered_by": "System",
            "actions_taken": "N/A",
            "error": "Unknown",
            "last_connected": "N/A",
            "retry_attempt": 1,
            "max_retries": 5,
            "downtime": "N/A",
            "plugin_type": "Unknown",
            "symbols": "N/A",
            "details": "N/A",
            "stack_trace": "N/A",
            "action": "N/A",
            "changes": "N/A",
            "affected_plugins": "N/A",
            "reloaded_by": "System",
            "raw_data": "N/A",
            "result": "N/A",
            "risk_type": "Unknown",
            "risk_level": "Medium",
            "current_value": "N/A",
            "threshold": "N/A",
            "recommended_action": "Review",
            "secured_profit": 0.0,
            "new_sl": "N/A",
            "old_sl": "N/A",
            "tp_level": 1,
            "tp_price": 0.0,
            "sl_price": 0.0,
            "lot_size": 0.0,
            "adx": 0.0,
            "adx_strength": "N/A",
            "confidence_score": 0,
            "confidence_level": "N/A",
            "market_state": "N/A",
            "ticket": 0,
            "ticket_a": 0,
            "ticket_b": 0,
            "order_a_lot": 0.0,
            "order_a_sl": 0.0,
            "order_a_tp": 0.0,
            "order_b_lot": 0.0,
            "order_b_sl": 0.0,
            "order_b_tp": 0.0,
            "timeframe": "N/A",
            "logic_route": "N/A",
            "closed_lots": 0.0,
            "close_price": 0.0,
            "breakeven_price": 0.0,
            "week_start": "N/A",
            "week_end": "N/A",
            "best_day": "N/A",
            "best_day_pnl": 0.0,
            "worst_day": "N/A",
            "worst_day_pnl": 0.0,
            "avg_duration": "N/A",
            "profit_factor": 0.0,
            "server": "N/A",
            "account": "N/A",
            "source": "N/A",
            "signal_type": "N/A",
        }
        
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value
        
        return result
    
    def _safe_format(self, template_string: str, data: Dict[str, Any]) -> str:
        """Safely format template, replacing missing keys with placeholders"""
        result = template_string
        
        # Find all placeholders
        placeholders = re.findall(r'\{(\w+)(?::[^}]*)?\}', template_string)
        
        for placeholder in placeholders:
            if placeholder not in data:
                data[placeholder] = f"[{placeholder}]"
        
        try:
            result = template_string.format(**data)
        except Exception:
            result = template_string
        
        return result
    
    def _to_html(self, text: str) -> str:
        """Convert plain text to HTML format"""
        # Escape HTML characters
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        
        # Convert newlines to <br>
        text = text.replace("\n", "<br>")
        
        # Bold headers (lines ending with :)
        lines = text.split("<br>")
        for i, line in enumerate(lines):
            if line.strip().endswith(":") and not line.strip().startswith("├") and not line.strip().startswith("└"):
                lines[i] = f"<b>{line}</b>"
        
        return "<br>".join(lines)
    
    def _to_markdown(self, text: str) -> str:
        """Convert plain text to Markdown format"""
        # Bold headers (lines ending with :)
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().endswith(":") and not line.strip().startswith("├") and not line.strip().startswith("└"):
                lines[i] = f"**{line}**"
        
        return "\n".join(lines)
    
    def format_entry_v3_dual(self, data: Dict[str, Any]) -> str:
        """Format V3 dual order entry notification"""
        return self.format("entry_v3_dual", data)
    
    def format_entry_v6_single(self, data: Dict[str, Any], order_type: str = "A") -> str:
        """Format V6 single order entry notification"""
        template_type = f"entry_v6_single_{order_type.lower()}"
        return self.format(template_type, data)
    
    def format_exit(self, data: Dict[str, Any]) -> str:
        """Format exit notification"""
        template_type = "exit_profit" if data.get("profit", 0) > 0 else "exit_loss"
        return self.format(template_type, data)
    
    def format_daily_summary(self, data: Dict[str, Any]) -> str:
        """Format daily summary notification"""
        return self.format("daily_summary", data)
    
    def format_emergency(self, data: Dict[str, Any]) -> str:
        """Format emergency notification"""
        return self.format("emergency_stop", data)
