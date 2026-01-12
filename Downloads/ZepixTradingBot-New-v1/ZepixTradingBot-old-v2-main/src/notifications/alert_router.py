"""
Alert Router - Route Alerts to Specific Bots/Chats

Document 19: Notification System Specification
Routes specific alert types to specific bots/chats based on configurable rules.

Features:
- Rule-based routing
- Bot-specific routing
- Chat-specific routing
- Priority-based routing
- Fallback routing
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime
import re
import logging


class AlertType(Enum):
    """Alert types for routing"""
    # Trade Alerts
    ENTRY = "entry"
    EXIT = "exit"
    TP_HIT = "tp_hit"
    SL_HIT = "sl_hit"
    PARTIAL_CLOSE = "partial_close"
    BREAKEVEN = "breakeven"
    
    # System Alerts
    SYSTEM = "system"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    
    # Analytics Alerts
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"
    PERFORMANCE = "performance"
    RISK = "risk"
    
    # Emergency Alerts
    EMERGENCY = "emergency"
    CRITICAL = "critical"


class TargetType(Enum):
    """Target types for routing"""
    BOT = "bot"           # Route to specific bot
    CHAT = "chat"         # Route to specific chat
    USER = "user"         # Route to specific user
    BROADCAST = "broadcast"  # Broadcast to all
    GROUP = "group"       # Route to user group


@dataclass
class RouteTarget:
    """Target for alert routing"""
    target_type: TargetType
    target_id: str  # Bot name, chat ID, user ID, or group name
    priority: int = 0  # Higher priority targets are tried first
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "target_type": self.target_type.value,
            "target_id": self.target_id,
            "priority": self.priority,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RouteTarget':
        """Create from dictionary"""
        return cls(
            target_type=TargetType(data["target_type"]),
            target_id=data["target_id"],
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True)
        )


@dataclass
class RoutingCondition:
    """Condition for routing rule"""
    field: str  # Field to check (e.g., "symbol", "plugin", "priority")
    operator: str  # Operator (eq, ne, gt, lt, gte, lte, in, not_in, regex)
    value: Any  # Value to compare
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate condition against data"""
        if self.field not in data:
            return False
        
        field_value = data[self.field]
        
        if self.operator == "eq":
            return field_value == self.value
        elif self.operator == "ne":
            return field_value != self.value
        elif self.operator == "gt":
            return field_value > self.value
        elif self.operator == "lt":
            return field_value < self.value
        elif self.operator == "gte":
            return field_value >= self.value
        elif self.operator == "lte":
            return field_value <= self.value
        elif self.operator == "in":
            return field_value in self.value
        elif self.operator == "not_in":
            return field_value not in self.value
        elif self.operator == "regex":
            return bool(re.match(self.value, str(field_value)))
        elif self.operator == "contains":
            return self.value in str(field_value)
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoutingCondition':
        """Create from dictionary"""
        return cls(
            field=data["field"],
            operator=data["operator"],
            value=data["value"]
        )


@dataclass
class RoutingRule:
    """Rule for alert routing"""
    rule_id: str
    name: str
    alert_types: Set[AlertType]  # Alert types this rule applies to
    targets: List[RouteTarget]  # Targets to route to
    conditions: List[RoutingCondition] = field(default_factory=list)  # Optional conditions
    priority: int = 0  # Rule priority (higher = checked first)
    enabled: bool = True
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def matches(self, alert_type: AlertType, data: Dict[str, Any]) -> bool:
        """Check if rule matches alert"""
        if not self.enabled:
            return False
        
        # Check alert type
        if alert_type not in self.alert_types:
            return False
        
        # Check all conditions
        for condition in self.conditions:
            if not condition.evaluate(data):
                return False
        
        return True
    
    def get_targets(self) -> List[RouteTarget]:
        """Get enabled targets sorted by priority"""
        enabled_targets = [t for t in self.targets if t.enabled]
        return sorted(enabled_targets, key=lambda t: -t.priority)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "alert_types": [at.value for at in self.alert_types],
            "targets": [t.to_dict() for t in self.targets],
            "conditions": [c.to_dict() for c in self.conditions],
            "priority": self.priority,
            "enabled": self.enabled,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoutingRule':
        """Create from dictionary"""
        return cls(
            rule_id=data["rule_id"],
            name=data["name"],
            alert_types={AlertType(at) for at in data["alert_types"]},
            targets=[RouteTarget.from_dict(t) for t in data["targets"]],
            conditions=[RoutingCondition.from_dict(c) for c in data.get("conditions", [])],
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True),
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )


@dataclass
class RoutingResult:
    """Result of alert routing"""
    alert_type: AlertType
    matched_rules: List[str]  # Rule IDs that matched
    targets: List[RouteTarget]  # Final targets
    routed: bool = False
    fallback_used: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_type": self.alert_type.value,
            "matched_rules": self.matched_rules,
            "targets": [t.to_dict() for t in self.targets],
            "routed": self.routed,
            "fallback_used": self.fallback_used,
            "timestamp": self.timestamp.isoformat()
        }


class AlertRouter:
    """
    Alert Router
    
    Routes alerts to appropriate bots/chats based on configurable rules.
    """
    
    def __init__(self):
        self.rules: Dict[str, RoutingRule] = {}
        self.fallback_targets: List[RouteTarget] = []
        self.logger = logging.getLogger(__name__)
        self._rule_counter = 0
        
        # Default routing by alert type
        self.default_routing: Dict[AlertType, str] = {
            AlertType.ENTRY: "notification",
            AlertType.EXIT: "notification",
            AlertType.TP_HIT: "notification",
            AlertType.SL_HIT: "notification",
            AlertType.PARTIAL_CLOSE: "notification",
            AlertType.BREAKEVEN: "notification",
            AlertType.SYSTEM: "controller",
            AlertType.ERROR: "notification",
            AlertType.WARNING: "notification",
            AlertType.INFO: "controller",
            AlertType.DAILY_REPORT: "analytics",
            AlertType.WEEKLY_REPORT: "analytics",
            AlertType.PERFORMANCE: "analytics",
            AlertType.RISK: "notification",
            AlertType.EMERGENCY: "broadcast",
            AlertType.CRITICAL: "broadcast",
        }
        
        self._load_default_rules()
    
    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        self._rule_counter += 1
        return f"RULE-{self._rule_counter:04d}"
    
    def _load_default_rules(self) -> None:
        """Load default routing rules"""
        # Emergency alerts to all bots
        self.add_rule(RoutingRule(
            rule_id="DEFAULT-EMERGENCY",
            name="Emergency Broadcast",
            alert_types={AlertType.EMERGENCY, AlertType.CRITICAL},
            targets=[
                RouteTarget(TargetType.BROADCAST, "all", priority=100)
            ],
            priority=100,
            description="Broadcast emergency alerts to all bots"
        ))
        
        # Trade alerts to notification bot
        self.add_rule(RoutingRule(
            rule_id="DEFAULT-TRADES",
            name="Trade Notifications",
            alert_types={
                AlertType.ENTRY, AlertType.EXIT, AlertType.TP_HIT,
                AlertType.SL_HIT, AlertType.PARTIAL_CLOSE, AlertType.BREAKEVEN
            },
            targets=[
                RouteTarget(TargetType.BOT, "notification", priority=50)
            ],
            priority=50,
            description="Route trade alerts to notification bot"
        ))
        
        # Analytics to analytics bot
        self.add_rule(RoutingRule(
            rule_id="DEFAULT-ANALYTICS",
            name="Analytics Reports",
            alert_types={
                AlertType.DAILY_REPORT, AlertType.WEEKLY_REPORT,
                AlertType.PERFORMANCE
            },
            targets=[
                RouteTarget(TargetType.BOT, "analytics", priority=30)
            ],
            priority=30,
            description="Route analytics to analytics bot"
        ))
        
        # System info to controller
        self.add_rule(RoutingRule(
            rule_id="DEFAULT-SYSTEM",
            name="System Information",
            alert_types={AlertType.SYSTEM, AlertType.INFO},
            targets=[
                RouteTarget(TargetType.BOT, "controller", priority=20)
            ],
            priority=20,
            description="Route system info to controller bot"
        ))
        
        # Errors and warnings to notification
        self.add_rule(RoutingRule(
            rule_id="DEFAULT-ERRORS",
            name="Errors and Warnings",
            alert_types={AlertType.ERROR, AlertType.WARNING, AlertType.RISK},
            targets=[
                RouteTarget(TargetType.BOT, "notification", priority=40)
            ],
            priority=40,
            description="Route errors and warnings to notification bot"
        ))
        
        # Set fallback
        self.fallback_targets = [
            RouteTarget(TargetType.BOT, "notification", priority=0)
        ]
    
    def add_rule(self, rule: RoutingRule) -> str:
        """Add routing rule"""
        if not rule.rule_id:
            rule.rule_id = self._generate_rule_id()
        self.rules[rule.rule_id] = rule
        return rule.rule_id
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove routing rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[RoutingRule]:
        """Get rule by ID"""
        return self.rules.get(rule_id)
    
    def update_rule(self, rule: RoutingRule) -> bool:
        """Update existing rule"""
        if rule.rule_id in self.rules:
            self.rules[rule.rule_id] = rule
            return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False
    
    def route(self, alert_type: AlertType, data: Dict[str, Any]) -> RoutingResult:
        """
        Route alert to appropriate targets
        
        Args:
            alert_type: Type of alert
            data: Alert data
            
        Returns:
            RoutingResult with matched rules and targets
        """
        matched_rules = []
        all_targets = []
        
        # Sort rules by priority
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: -r.priority
        )
        
        # Find matching rules
        for rule in sorted_rules:
            if rule.matches(alert_type, data):
                matched_rules.append(rule.rule_id)
                all_targets.extend(rule.get_targets())
        
        # Use fallback if no matches
        fallback_used = False
        if not all_targets:
            all_targets = self.fallback_targets
            fallback_used = True
        
        # Deduplicate targets
        seen = set()
        unique_targets = []
        for target in all_targets:
            key = (target.target_type, target.target_id)
            if key not in seen:
                seen.add(key)
                unique_targets.append(target)
        
        return RoutingResult(
            alert_type=alert_type,
            matched_rules=matched_rules,
            targets=unique_targets,
            routed=len(unique_targets) > 0,
            fallback_used=fallback_used
        )
    
    def get_default_bot(self, alert_type: AlertType) -> str:
        """Get default bot for alert type"""
        return self.default_routing.get(alert_type, "notification")
    
    def set_fallback_targets(self, targets: List[RouteTarget]) -> None:
        """Set fallback targets"""
        self.fallback_targets = targets
    
    def create_symbol_rule(
        self,
        symbol: str,
        target_bot: str,
        alert_types: Optional[Set[AlertType]] = None
    ) -> str:
        """Create rule for specific symbol"""
        if alert_types is None:
            alert_types = {AlertType.ENTRY, AlertType.EXIT, AlertType.TP_HIT, AlertType.SL_HIT}
        
        rule = RoutingRule(
            rule_id=self._generate_rule_id(),
            name=f"Symbol: {symbol}",
            alert_types=alert_types,
            targets=[RouteTarget(TargetType.BOT, target_bot)],
            conditions=[
                RoutingCondition("symbol", "eq", symbol)
            ],
            priority=60,
            description=f"Route {symbol} alerts to {target_bot}"
        )
        return self.add_rule(rule)
    
    def create_plugin_rule(
        self,
        plugin_name: str,
        target_bot: str,
        alert_types: Optional[Set[AlertType]] = None
    ) -> str:
        """Create rule for specific plugin"""
        if alert_types is None:
            alert_types = {AlertType.ENTRY, AlertType.EXIT, AlertType.TP_HIT, AlertType.SL_HIT}
        
        rule = RoutingRule(
            rule_id=self._generate_rule_id(),
            name=f"Plugin: {plugin_name}",
            alert_types=alert_types,
            targets=[RouteTarget(TargetType.BOT, target_bot)],
            conditions=[
                RoutingCondition("plugin", "eq", plugin_name)
            ],
            priority=55,
            description=f"Route {plugin_name} alerts to {target_bot}"
        )
        return self.add_rule(rule)
    
    def create_profit_threshold_rule(
        self,
        min_profit: float,
        target_bot: str
    ) -> str:
        """Create rule for high-profit trades"""
        rule = RoutingRule(
            rule_id=self._generate_rule_id(),
            name=f"High Profit (>= ${min_profit})",
            alert_types={AlertType.EXIT, AlertType.TP_HIT},
            targets=[RouteTarget(TargetType.BOT, target_bot)],
            conditions=[
                RoutingCondition("profit", "gte", min_profit)
            ],
            priority=70,
            description=f"Route high-profit trades (>= ${min_profit}) to {target_bot}"
        )
        return self.add_rule(rule)
    
    def list_rules(self) -> List[RoutingRule]:
        """List all rules sorted by priority"""
        return sorted(self.rules.values(), key=lambda r: -r.priority)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        total_rules = len(self.rules)
        enabled_rules = sum(1 for r in self.rules.values() if r.enabled)
        
        by_alert_type: Dict[str, int] = {}
        for rule in self.rules.values():
            for at in rule.alert_types:
                by_alert_type[at.value] = by_alert_type.get(at.value, 0) + 1
        
        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "disabled_rules": total_rules - enabled_rules,
            "rules_by_alert_type": by_alert_type,
            "fallback_targets": len(self.fallback_targets)
        }
    
    def export_rules(self) -> List[Dict[str, Any]]:
        """Export all rules as dictionaries"""
        return [rule.to_dict() for rule in self.rules.values()]
    
    def import_rules(self, rules_data: List[Dict[str, Any]], replace: bool = False) -> int:
        """Import rules from dictionaries"""
        if replace:
            self.rules.clear()
        
        count = 0
        for data in rules_data:
            rule = RoutingRule.from_dict(data)
            self.add_rule(rule)
            count += 1
        
        return count
