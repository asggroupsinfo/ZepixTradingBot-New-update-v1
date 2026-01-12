"""
Manual Test Guides for V5 Hybrid Plugin Architecture.

This module provides interactive checklists and guides for manual verification:
- V3 Combined Logic manual tests
- V6 Price Action manual tests
- Integration manual tests
- Shadow Mode verification guides

Version: 1.0
Date: 2026-01-12
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import json


class ChecklistStatus(Enum):
    """Checklist item status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestPriority(Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChecklistItem:
    """Single checklist item for manual testing."""
    id: str
    description: str
    category: str
    priority: TestPriority
    status: ChecklistStatus = ChecklistStatus.PENDING
    notes: str = ""
    verified_by: str = ""
    verified_at: Optional[str] = None
    
    def mark_passed(self, verified_by: str, notes: str = "") -> None:
        """Mark item as passed."""
        self.status = ChecklistStatus.PASSED
        self.verified_by = verified_by
        self.verified_at = datetime.now().isoformat()
        self.notes = notes
    
    def mark_failed(self, verified_by: str, notes: str = "") -> None:
        """Mark item as failed."""
        self.status = ChecklistStatus.FAILED
        self.verified_by = verified_by
        self.verified_at = datetime.now().isoformat()
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "notes": self.notes,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown checkbox format."""
        checkbox = "[x]" if self.status == ChecklistStatus.PASSED else "[ ]"
        priority_badge = f"[{self.priority.value.upper()}]"
        return f"- {checkbox} {priority_badge} {self.description}"


@dataclass
class ManualTestChecklist:
    """Manual test checklist with multiple items."""
    name: str
    description: str
    category: str
    items: List[ChecklistItem] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def total_items(self) -> int:
        """Get total number of items."""
        return len(self.items)
    
    @property
    def passed_items(self) -> int:
        """Get number of passed items."""
        return sum(1 for item in self.items if item.status == ChecklistStatus.PASSED)
    
    @property
    def failed_items(self) -> int:
        """Get number of failed items."""
        return sum(1 for item in self.items if item.status == ChecklistStatus.FAILED)
    
    @property
    def pending_items(self) -> int:
        """Get number of pending items."""
        return sum(1 for item in self.items if item.status == ChecklistStatus.PENDING)
    
    @property
    def completion_rate(self) -> float:
        """Get completion rate percentage."""
        if self.total_items == 0:
            return 0.0
        completed = self.passed_items + self.failed_items
        return (completed / self.total_items) * 100
    
    @property
    def pass_rate(self) -> float:
        """Get pass rate percentage."""
        completed = self.passed_items + self.failed_items
        if completed == 0:
            return 0.0
        return (self.passed_items / completed) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if all items are verified."""
        return self.pending_items == 0
    
    @property
    def all_passed(self) -> bool:
        """Check if all items passed."""
        return self.is_complete and self.failed_items == 0
    
    def add_item(self, item: ChecklistItem) -> None:
        """Add item to checklist."""
        self.items.append(item)
    
    def get_item(self, item_id: str) -> Optional[ChecklistItem]:
        """Get item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_items_by_priority(self, priority: TestPriority) -> List[ChecklistItem]:
        """Get items by priority."""
        return [item for item in self.items if item.priority == priority]
    
    def get_critical_items(self) -> List[ChecklistItem]:
        """Get critical priority items."""
        return self.get_items_by_priority(TestPriority.CRITICAL)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "total_items": self.total_items,
            "passed_items": self.passed_items,
            "failed_items": self.failed_items,
            "pending_items": self.pending_items,
            "completion_rate": self.completion_rate,
            "pass_rate": self.pass_rate,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        lines = [
            f"# {self.name}",
            "",
            f"**Description:** {self.description}",
            f"**Category:** {self.category}",
            f"**Progress:** {self.passed_items}/{self.total_items} ({self.completion_rate:.1f}%)",
            "",
            "## Checklist Items",
            ""
        ]
        
        for priority in [TestPriority.CRITICAL, TestPriority.HIGH, TestPriority.MEDIUM, TestPriority.LOW]:
            items = self.get_items_by_priority(priority)
            if items:
                lines.append(f"### {priority.value.upper()} Priority")
                lines.append("")
                for item in items:
                    lines.append(item.to_markdown())
                lines.append("")
        
        return "\n".join(lines)
    
    def export_json(self, filepath: str) -> None:
        """Export checklist to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def export_markdown(self, filepath: str) -> None:
        """Export checklist to markdown file."""
        with open(filepath, 'w') as f:
            f.write(self.to_markdown())


class V3ManualTestGuide:
    """Manual test guide for V3 Combined Logic."""
    
    @classmethod
    def create_signal_processing_checklist(cls) -> ManualTestChecklist:
        """Create signal processing manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 Signal Processing Manual Tests",
            description="Manual verification of all 12 V3 signal types",
            category="v3_signal_processing"
        )
        
        signals = [
            ("Institutional_Launchpad", "Verify Institutional_Launchpad routes correctly"),
            ("Liquidity_Trap", "Verify Liquidity_Trap routes correctly"),
            ("Momentum_Ignition", "Verify Momentum_Ignition routes correctly"),
            ("Mitigation_Block", "Verify Mitigation_Block routes correctly"),
            ("Golden_Pocket_5m", "Verify Golden_Pocket (5m) routes to LOGIC2"),
            ("Golden_Pocket_1H", "Verify Golden_Pocket (1H) routes to LOGIC3"),
            ("Golden_Pocket_4H", "Verify Golden_Pocket (4H) routes to LOGIC3"),
            ("Screener", "Verify Screener routes to LOGIC3 (override)"),
            ("entry_v3", "Verify entry_v3 bypasses trend check"),
            ("Exit_Bullish", "Verify Exit_Bullish triggers close logic"),
            ("Exit_Bearish", "Verify Exit_Bearish triggers close logic"),
            ("Volatility_Squeeze", "Verify Volatility_Squeeze updates DB only"),
            ("Sideways_Breakout", "Verify Sideways_Breakout (Signal 12) handling"),
        ]
        
        for i, (signal_id, description) in enumerate(signals, 1):
            checklist.add_item(ChecklistItem(
                id=f"v3_signal_{i:02d}",
                description=description,
                category="v3_signal_processing",
                priority=TestPriority.CRITICAL
            ))
        
        return checklist
    
    @classmethod
    def create_routing_matrix_checklist(cls) -> ManualTestChecklist:
        """Create routing matrix manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 Routing Matrix Manual Tests",
            description="Manual verification of Priority 1 & 2 routing",
            category="v3_routing_matrix"
        )
        
        items = [
            ("Screener always routes to LOGIC3", TestPriority.CRITICAL),
            ("Golden Pocket 1H routes to LOGIC3", TestPriority.CRITICAL),
            ("Golden Pocket 4H routes to LOGIC3", TestPriority.CRITICAL),
            ("5m signal routes to LOGIC1 (1.25x multiplier)", TestPriority.CRITICAL),
            ("15m signal routes to LOGIC2 (1.0x multiplier)", TestPriority.CRITICAL),
            ("60m signal routes to LOGIC3 (0.625x multiplier)", TestPriority.CRITICAL),
            ("240m signal routes to LOGIC3 (0.625x multiplier)", TestPriority.CRITICAL),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v3_routing_{i:02d}",
                description=description,
                category="v3_routing_matrix",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_dual_order_checklist(cls) -> ManualTestChecklist:
        """Create dual order system manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 Dual Order System Manual Tests",
            description="Manual verification of Order A + Order B hybrid SL",
            category="v3_dual_order"
        )
        
        items = [
            ("Order A receives V3 Smart SL from alert", TestPriority.CRITICAL),
            ("Order B receives Fixed $10 SL (IGNORES Pine SL)", TestPriority.CRITICAL),
            ("Order A has TP2 (extended target)", TestPriority.CRITICAL),
            ("Order B has TP1 (closer target)", TestPriority.CRITICAL),
            ("50/50 lot split applied correctly", TestPriority.CRITICAL),
            ("Both orders placed simultaneously", TestPriority.HIGH),
            ("Order tagging includes plugin_id", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v3_dual_{i:02d}",
                description=description,
                category="v3_dual_order",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_mtf_pillar_checklist(cls) -> ManualTestChecklist:
        """Create MTF 4-pillar manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 MTF 4-Pillar Manual Tests",
            description="Manual verification of MTF extraction and alignment",
            category="v3_mtf_pillar"
        )
        
        items = [
            ("Pine sends 6 trends: [1m, 5m, 15m, 1H, 4H, 1D]", TestPriority.HIGH),
            ("Bot extracts indices [2:6] = [15m, 1H, 4H, 1D]", TestPriority.CRITICAL),
            ("Bot ignores indices [0:2] = [1m, 5m]", TestPriority.CRITICAL),
            ("BUY requires 3/4 bullish pillars", TestPriority.CRITICAL),
            ("SELL requires 3/4 bearish pillars", TestPriority.CRITICAL),
            ("2/4 alignment rejects entry", TestPriority.CRITICAL),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v3_mtf_{i:02d}",
                description=description,
                category="v3_mtf_pillar",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_position_sizing_checklist(cls) -> ManualTestChecklist:
        """Create position sizing manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 Position Sizing Manual Tests",
            description="Manual verification of 4-step position sizing",
            category="v3_position_sizing"
        )
        
        items = [
            ("Step 1: Base lot applied correctly", TestPriority.HIGH),
            ("Step 2: Consensus multiplier applied (0.2x to 1.0x)", TestPriority.CRITICAL),
            ("Step 3: Logic multiplier applied (LOGIC1=1.25x, LOGIC2=1.0x, LOGIC3=0.625x)", TestPriority.CRITICAL),
            ("Step 4: 50/50 split for dual orders", TestPriority.CRITICAL),
            ("Consensus 0-3 maps to 0.2x-0.5x", TestPriority.HIGH),
            ("Consensus 4-6 maps to 0.6x-0.8x", TestPriority.HIGH),
            ("Consensus 7-9 maps to 0.9x-1.0x", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v3_pos_{i:02d}",
                description=description,
                category="v3_position_sizing",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_trend_bypass_checklist(cls) -> ManualTestChecklist:
        """Create trend bypass manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 Trend Bypass Manual Tests",
            description="Manual verification of trend bypass logic",
            category="v3_trend_bypass"
        )
        
        items = [
            ("entry_v3 signal BYPASSES trend check", TestPriority.CRITICAL),
            ("Institutional_Launchpad REQUIRES trend check", TestPriority.CRITICAL),
            ("SL hunt re-entry REQUIRES trend check", TestPriority.HIGH),
            ("Bypass flag logged in database", TestPriority.MEDIUM),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v3_bypass_{i:02d}",
                description=description,
                category="v3_trend_bypass",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_all_checklists(cls) -> List[ManualTestChecklist]:
        """Create all V3 manual test checklists."""
        return [
            cls.create_signal_processing_checklist(),
            cls.create_routing_matrix_checklist(),
            cls.create_dual_order_checklist(),
            cls.create_mtf_pillar_checklist(),
            cls.create_position_sizing_checklist(),
            cls.create_trend_bypass_checklist(),
        ]


class V6ManualTestGuide:
    """Manual test guide for V6 Price Action plugins."""
    
    @classmethod
    def create_1m_checklist(cls) -> ManualTestChecklist:
        """Create V6 1M scalping manual test checklist."""
        checklist = ManualTestChecklist(
            name="V6 1M Scalping Manual Tests",
            description="Manual verification of ORDER_B_ONLY routing",
            category="v6_1m"
        )
        
        items = [
            ("ADX >= 20 allows entry", TestPriority.CRITICAL),
            ("ADX < 20 rejects entry", TestPriority.CRITICAL),
            ("Confidence >= 80 allows entry", TestPriority.CRITICAL),
            ("Confidence < 80 rejects entry", TestPriority.CRITICAL),
            ("Spread > 2.0 pips rejects entry", TestPriority.CRITICAL),
            ("ONLY Order B placed (no Order A)", TestPriority.CRITICAL),
            ("Order B uses TP1 (quick exit)", TestPriority.CRITICAL),
            ("Risk multiplier 0.5 applied", TestPriority.HIGH),
            ("Max lot 0.10 enforced", TestPriority.HIGH),
            ("Max 3 open trades enforced", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v6_1m_{i:02d}",
                description=description,
                category="v6_1m",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_5m_checklist(cls) -> ManualTestChecklist:
        """Create V6 5M momentum manual test checklist."""
        checklist = ManualTestChecklist(
            name="V6 5M Momentum Manual Tests",
            description="Manual verification of DUAL_ORDERS routing",
            category="v6_5m"
        )
        
        items = [
            ("ADX >= 25 allows entry", TestPriority.CRITICAL),
            ("15m trend alignment required", TestPriority.CRITICAL),
            ("Momentum increasing required", TestPriority.HIGH),
            ("BOTH Order A and Order B placed", TestPriority.CRITICAL),
            ("Same SL for both orders", TestPriority.CRITICAL),
            ("Order B uses TP1, Order A uses TP2", TestPriority.CRITICAL),
            ("After TP1 hit, move to breakeven", TestPriority.CRITICAL),
            ("Risk multiplier 1.0 applied", TestPriority.HIGH),
            ("Max lot 0.20 enforced", TestPriority.HIGH),
            ("Max 4 open trades enforced", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v6_5m_{i:02d}",
                description=description,
                category="v6_5m",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_15m_checklist(cls) -> ManualTestChecklist:
        """Create V6 15M intraday manual test checklist."""
        checklist = ManualTestChecklist(
            name="V6 15M Intraday Manual Tests",
            description="Manual verification of ORDER_A_ONLY routing",
            category="v6_15m"
        )
        
        items = [
            ("Market state matches signal direction", TestPriority.CRITICAL),
            ("Pulse alignment verified (bull_count > bear_count for BUY)", TestPriority.CRITICAL),
            ("ONLY Order A placed (no Order B)", TestPriority.CRITICAL),
            ("Order A uses TP2 target", TestPriority.CRITICAL),
            ("Risk multiplier 1.25 applied", TestPriority.HIGH),
            ("Max lot 0.25 enforced", TestPriority.HIGH),
            ("Max 3 open trades enforced", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v6_15m_{i:02d}",
                description=description,
                category="v6_15m",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_1h_checklist(cls) -> ManualTestChecklist:
        """Create V6 1H swing manual test checklist."""
        checklist = ManualTestChecklist(
            name="V6 1H Swing Manual Tests",
            description="Manual verification of ORDER_A_ONLY routing with extended TP",
            category="v6_1h"
        )
        
        items = [
            ("4H trend alignment required", TestPriority.CRITICAL),
            ("1D trend alignment required", TestPriority.CRITICAL),
            ("ONLY Order A placed (no Order B)", TestPriority.CRITICAL),
            ("Extended TP enabled", TestPriority.CRITICAL),
            ("Traditional TF trends used (no Trend Pulse)", TestPriority.HIGH),
            ("Risk multiplier 1.5 applied", TestPriority.HIGH),
            ("Max lot 0.30 enforced", TestPriority.HIGH),
            ("Max 2 open trades enforced", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v6_1h_{i:02d}",
                description=description,
                category="v6_1h",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_trend_pulse_checklist(cls) -> ManualTestChecklist:
        """Create Trend Pulse system manual test checklist."""
        checklist = ManualTestChecklist(
            name="V6 Trend Pulse System Manual Tests",
            description="Manual verification of Trend Pulse updates and alignment",
            category="v6_trend_pulse"
        )
        
        items = [
            ("TREND_PULSE alert updates market_trends table", TestPriority.CRITICAL),
            ("Bull count incremented correctly", TestPriority.CRITICAL),
            ("Bear count incremented correctly", TestPriority.CRITICAL),
            ("Market state updated correctly", TestPriority.CRITICAL),
            ("Changes field populated (which TFs changed)", TestPriority.HIGH),
            ("BUY requires bull > bear", TestPriority.CRITICAL),
            ("SELL requires bear > bull", TestPriority.CRITICAL),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"v6_pulse_{i:02d}",
                description=description,
                category="v6_trend_pulse",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_all_checklists(cls) -> List[ManualTestChecklist]:
        """Create all V6 manual test checklists."""
        return [
            cls.create_1m_checklist(),
            cls.create_5m_checklist(),
            cls.create_15m_checklist(),
            cls.create_1h_checklist(),
            cls.create_trend_pulse_checklist(),
        ]


class IntegrationManualTestGuide:
    """Manual test guide for integration tests."""
    
    @classmethod
    def create_v3_v6_integration_checklist(cls) -> ManualTestChecklist:
        """Create V3 + V6 integration manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 + V6 Integration Manual Tests",
            description="Manual verification of simultaneous execution",
            category="integration"
        )
        
        items = [
            ("V3 signal routes to combined_v3 plugin", TestPriority.CRITICAL),
            ("V6 1M signal routes to price_action_1m plugin", TestPriority.CRITICAL),
            ("Both execute independently", TestPriority.CRITICAL),
            ("Separate databases maintained", TestPriority.CRITICAL),
            ("No cross-contamination between plugins", TestPriority.CRITICAL),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"int_v3v6_{i:02d}",
                description=description,
                category="integration",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_service_api_checklist(cls) -> ManualTestChecklist:
        """Create ServiceAPI integration manual test checklist."""
        checklist = ManualTestChecklist(
            name="ServiceAPI Integration Manual Tests",
            description="Manual verification of ServiceAPI methods",
            category="service_api"
        )
        
        items = [
            ("place_dual_orders_v3() works correctly", TestPriority.CRITICAL),
            ("get_mtf_trends() returns 4 pillars", TestPriority.CRITICAL),
            ("validate_v3_trend_alignment() checks 3/4 correctly", TestPriority.CRITICAL),
            ("place_single_order_a() works correctly", TestPriority.CRITICAL),
            ("place_single_order_b() works correctly", TestPriority.CRITICAL),
            ("place_dual_orders_v6() works (different from V3)", TestPriority.CRITICAL),
            ("update_trend_pulse() updates market_trends table", TestPriority.CRITICAL),
            ("check_pulse_alignment() validates correctly", TestPriority.CRITICAL),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"int_api_{i:02d}",
                description=description,
                category="service_api",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_all_checklists(cls) -> List[ManualTestChecklist]:
        """Create all integration manual test checklists."""
        return [
            cls.create_v3_v6_integration_checklist(),
            cls.create_service_api_checklist(),
        ]


class ShadowModeManualTestGuide:
    """Manual test guide for shadow mode verification."""
    
    @classmethod
    def create_v3_shadow_checklist(cls) -> ManualTestChecklist:
        """Create V3 shadow mode manual test checklist."""
        checklist = ManualTestChecklist(
            name="V3 Shadow Mode Manual Tests (72-Hour)",
            description="Manual verification of V3 shadow mode operation",
            category="shadow_mode_v3"
        )
        
        items = [
            ("All 12 signals logged during shadow period", TestPriority.CRITICAL),
            ("Routing decisions logged correctly", TestPriority.CRITICAL),
            ("Hypothetical dual orders tracked", TestPriority.CRITICAL),
            ("P&L calculated without real trades", TestPriority.CRITICAL),
            ("Zero actual MT5 orders placed", TestPriority.CRITICAL),
            ("Shadow duration = 72 hours", TestPriority.HIGH),
            ("Shadow logs exportable", TestPriority.MEDIUM),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"shadow_v3_{i:02d}",
                description=description,
                category="shadow_mode_v3",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_v6_shadow_checklist(cls) -> ManualTestChecklist:
        """Create V6 shadow mode manual test checklist."""
        checklist = ManualTestChecklist(
            name="V6 Shadow Mode Manual Tests (72-Hour)",
            description="Manual verification of V6 shadow mode operation",
            category="shadow_mode_v6"
        )
        
        items = [
            ("1M: ORDER_B_ONLY simulated correctly", TestPriority.CRITICAL),
            ("5M: DUAL_ORDERS simulated correctly", TestPriority.CRITICAL),
            ("15M: ORDER_A_ONLY simulated correctly", TestPriority.CRITICAL),
            ("1H: ORDER_A_ONLY simulated correctly", TestPriority.CRITICAL),
            ("Zero actual MT5 orders placed", TestPriority.CRITICAL),
            ("Hypothetical P&L tracked per plugin", TestPriority.HIGH),
            ("Shadow duration = 72 hours per plugin", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"shadow_v6_{i:02d}",
                description=description,
                category="shadow_mode_v6",
                priority=priority
            ))
        
        return checklist
    
    @classmethod
    def create_all_checklists(cls) -> List[ManualTestChecklist]:
        """Create all shadow mode manual test checklists."""
        return [
            cls.create_v3_shadow_checklist(),
            cls.create_v6_shadow_checklist(),
        ]


class ProductionReadinessChecklist:
    """Production readiness verification checklist."""
    
    @classmethod
    def create_checklist(cls) -> ManualTestChecklist:
        """Create production readiness checklist."""
        checklist = ManualTestChecklist(
            name="Production Readiness Verification",
            description="Final verification before production deployment",
            category="production_readiness"
        )
        
        items = [
            ("All HIGH priority tests passing", TestPriority.CRITICAL),
            ("V3 plugin tested with all 12 signals", TestPriority.CRITICAL),
            ("All 4 V6 plugins tested with conditional routing", TestPriority.CRITICAL),
            ("Database schemas verified", TestPriority.CRITICAL),
            ("ServiceAPI methods verified", TestPriority.CRITICAL),
            ("Shadow mode logs reviewed", TestPriority.CRITICAL),
            ("Zero errors in 72-hour shadow period", TestPriority.CRITICAL),
            ("Documentation matches implementation", TestPriority.HIGH),
            ("Configuration templates validated", TestPriority.HIGH),
            ("Environment variables configured", TestPriority.HIGH),
        ]
        
        for i, (description, priority) in enumerate(items, 1):
            checklist.add_item(ChecklistItem(
                id=f"prod_{i:02d}",
                description=description,
                category="production_readiness",
                priority=priority
            ))
        
        return checklist


def generate_all_checklists() -> Dict[str, List[ManualTestChecklist]]:
    """Generate all manual test checklists."""
    return {
        "v3": V3ManualTestGuide.create_all_checklists(),
        "v6": V6ManualTestGuide.create_all_checklists(),
        "integration": IntegrationManualTestGuide.create_all_checklists(),
        "shadow_mode": ShadowModeManualTestGuide.create_all_checklists(),
        "production": [ProductionReadinessChecklist.create_checklist()],
    }


def export_all_checklists_markdown(output_dir: str) -> None:
    """Export all checklists to markdown files."""
    import os
    
    all_checklists = generate_all_checklists()
    
    for category, checklists in all_checklists.items():
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        for checklist in checklists:
            filename = f"{checklist.category}.md"
            filepath = os.path.join(category_dir, filename)
            checklist.export_markdown(filepath)
