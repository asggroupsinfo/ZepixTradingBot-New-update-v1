"""
Integration Test Scenarios for V5 Hybrid Plugin Architecture.

This module provides integration test scenario definitions and runners:
- V3 + V6 simultaneous execution scenarios
- ServiceAPI integration scenarios
- Database integration scenarios
- End-to-end workflow scenarios

Version: 1.0
Date: 2026-01-12
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import json


class ScenarioStatus(Enum):
    """Scenario execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ScenarioCategory(Enum):
    """Scenario category."""
    V3_V6_INTEGRATION = "v3_v6_integration"
    SERVICE_API = "service_api"
    DATABASE = "database"
    END_TO_END = "end_to_end"
    SHADOW_MODE = "shadow_mode"


@dataclass
class ScenarioStep:
    """Single step in an integration scenario."""
    step_id: str
    description: str
    action: str
    expected_result: str
    status: ScenarioStatus = ScenarioStatus.PENDING
    actual_result: str = ""
    error_message: str = ""
    duration_ms: float = 0.0
    
    def mark_passed(self, actual_result: str = "", duration_ms: float = 0.0) -> None:
        """Mark step as passed."""
        self.status = ScenarioStatus.PASSED
        self.actual_result = actual_result or self.expected_result
        self.duration_ms = duration_ms
    
    def mark_failed(self, error_message: str, duration_ms: float = 0.0) -> None:
        """Mark step as failed."""
        self.status = ScenarioStatus.FAILED
        self.error_message = error_message
        self.duration_ms = duration_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "action": self.action,
            "expected_result": self.expected_result,
            "status": self.status.value,
            "actual_result": self.actual_result,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms
        }


@dataclass
class IntegrationScenario:
    """Integration test scenario with multiple steps."""
    scenario_id: str
    name: str
    description: str
    category: ScenarioCategory
    steps: List[ScenarioStep] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    status: ScenarioStatus = ScenarioStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    
    @property
    def total_steps(self) -> int:
        """Get total number of steps."""
        return len(self.steps)
    
    @property
    def passed_steps(self) -> int:
        """Get number of passed steps."""
        return sum(1 for s in self.steps if s.status == ScenarioStatus.PASSED)
    
    @property
    def failed_steps(self) -> int:
        """Get number of failed steps."""
        return sum(1 for s in self.steps if s.status == ScenarioStatus.FAILED)
    
    @property
    def all_passed(self) -> bool:
        """Check if all steps passed."""
        return self.failed_steps == 0 and self.total_steps > 0
    
    @property
    def total_duration_ms(self) -> float:
        """Get total duration in milliseconds."""
        return sum(s.duration_ms for s in self.steps)
    
    def add_step(self, step: ScenarioStep) -> None:
        """Add step to scenario."""
        self.steps.append(step)
    
    def get_step(self, step_id: str) -> Optional[ScenarioStep]:
        """Get step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "all_passed": self.all_passed,
            "total_duration_ms": self.total_duration_ms,
            "steps": [s.to_dict() for s in self.steps],
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        status_mark = "[PASS]" if self.all_passed else "[FAIL]" if self.failed_steps > 0 else "[PENDING]"
        
        lines = [
            f"# {status_mark} {self.name}",
            "",
            f"**ID:** {self.scenario_id}",
            f"**Category:** {self.category.value}",
            f"**Description:** {self.description}",
            "",
            "## Preconditions",
            ""
        ]
        
        for pre in self.preconditions:
            lines.append(f"- {pre}")
        
        lines.extend(["", "## Steps", ""])
        
        for i, step in enumerate(self.steps, 1):
            step_mark = "[PASS]" if step.status == ScenarioStatus.PASSED else "[FAIL]" if step.status == ScenarioStatus.FAILED else "[ ]"
            lines.append(f"### Step {i}: {step_mark} {step.description}")
            lines.append(f"**Action:** {step.action}")
            lines.append(f"**Expected:** {step.expected_result}")
            if step.actual_result:
                lines.append(f"**Actual:** {step.actual_result}")
            if step.error_message:
                lines.append(f"**Error:** {step.error_message}")
            lines.append("")
        
        lines.extend(["## Postconditions", ""])
        for post in self.postconditions:
            lines.append(f"- {post}")
        
        return "\n".join(lines)


class V3V6IntegrationScenarios:
    """V3 + V6 integration test scenarios."""
    
    @classmethod
    def create_simultaneous_execution_scenario(cls) -> IntegrationScenario:
        """Create V3 + V6 simultaneous execution scenario."""
        scenario = IntegrationScenario(
            scenario_id="INT_001",
            name="V3 + V6 Simultaneous Execution",
            description="Verify V3 and V6 plugins can execute simultaneously without interference",
            category=ScenarioCategory.V3_V6_INTEGRATION,
            preconditions=[
                "Both V3 and V6 plugins are enabled",
                "ServiceAPI is initialized",
                "Databases are ready"
            ],
            postconditions=[
                "Both plugins executed independently",
                "Separate database entries created",
                "No cross-contamination"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="INT_001_01",
            description="Send V3 signal to combined_v3 plugin",
            action="Process Institutional_Launchpad signal with tf=5",
            expected_result="Signal routes to LOGIC1, dual orders prepared"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="INT_001_02",
            description="Send V6 1M alert to price_action_1m plugin",
            action="Process V6 1M alert with ADX=22, confidence=85",
            expected_result="Alert routes to ORDER_B_ONLY, single order prepared"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="INT_001_03",
            description="Verify V3 database entry",
            action="Query zepix_combined.db for V3 trade",
            expected_result="V3 trade entry found with correct plugin_id"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="INT_001_04",
            description="Verify V6 database entry",
            action="Query zepix_v6_1m.db for V6 trade",
            expected_result="V6 trade entry found with correct plugin_id"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="INT_001_05",
            description="Verify no cross-contamination",
            action="Check V3 DB has no V6 entries and vice versa",
            expected_result="Databases are isolated, no cross-contamination"
        ))
        
        return scenario
    
    @classmethod
    def create_plugin_isolation_scenario(cls) -> IntegrationScenario:
        """Create plugin isolation verification scenario."""
        scenario = IntegrationScenario(
            scenario_id="INT_002",
            name="Plugin Isolation Verification",
            description="Verify plugins are properly isolated from each other",
            category=ScenarioCategory.V3_V6_INTEGRATION,
            preconditions=[
                "All plugins are loaded",
                "Plugin registry is initialized"
            ],
            postconditions=[
                "Each plugin has its own database",
                "Each plugin has its own configuration",
                "No shared state between plugins"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="INT_002_01",
            description="Verify V3 plugin has isolated database",
            action="Check combined_v3 plugin database path",
            expected_result="Database path is zepix_combined.db"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="INT_002_02",
            description="Verify V6 1M plugin has isolated database",
            action="Check price_action_1m plugin database path",
            expected_result="Database path is zepix_v6_1m.db"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="INT_002_03",
            description="Verify plugin configurations are separate",
            action="Load configs for V3 and V6 plugins",
            expected_result="Each plugin has its own config.json"
        ))
        
        return scenario
    
    @classmethod
    def create_all_scenarios(cls) -> List[IntegrationScenario]:
        """Create all V3 + V6 integration scenarios."""
        return [
            cls.create_simultaneous_execution_scenario(),
            cls.create_plugin_isolation_scenario(),
        ]


class ServiceAPIIntegrationScenarios:
    """ServiceAPI integration test scenarios."""
    
    @classmethod
    def create_order_execution_scenario(cls) -> IntegrationScenario:
        """Create order execution ServiceAPI scenario."""
        scenario = IntegrationScenario(
            scenario_id="API_001",
            name="ServiceAPI Order Execution",
            description="Verify ServiceAPI order execution methods work correctly",
            category=ScenarioCategory.SERVICE_API,
            preconditions=[
                "ServiceAPI is initialized",
                "OrderExecutionService is available",
                "MT5 connection is mocked"
            ],
            postconditions=[
                "Orders are placed correctly",
                "Order IDs are returned",
                "Database entries created"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="API_001_01",
            description="Test place_dual_orders_v3()",
            action="Call place_dual_orders_v3 with V3 signal data",
            expected_result="Two orders placed (Order A + Order B)"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_001_02",
            description="Test place_single_order_a()",
            action="Call place_single_order_a with V6 15M alert",
            expected_result="Single Order A placed"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_001_03",
            description="Test place_single_order_b()",
            action="Call place_single_order_b with V6 1M alert",
            expected_result="Single Order B placed"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_001_04",
            description="Test place_dual_orders_v6()",
            action="Call place_dual_orders_v6 with V6 5M alert",
            expected_result="Two orders placed with V6 routing"
        ))
        
        return scenario
    
    @classmethod
    def create_risk_management_scenario(cls) -> IntegrationScenario:
        """Create risk management ServiceAPI scenario."""
        scenario = IntegrationScenario(
            scenario_id="API_002",
            name="ServiceAPI Risk Management",
            description="Verify ServiceAPI risk management methods work correctly",
            category=ScenarioCategory.SERVICE_API,
            preconditions=[
                "ServiceAPI is initialized",
                "RiskManagementService is available"
            ],
            postconditions=[
                "Lot sizes calculated correctly",
                "Daily limits enforced"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="API_002_01",
            description="Test calculate_lot_size()",
            action="Call calculate_lot_size with balance=10000, risk=1%",
            expected_result="Lot size calculated based on risk parameters"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_002_02",
            description="Test check_daily_limit()",
            action="Call check_daily_limit for combined_v3 plugin",
            expected_result="Daily limit status returned"
        ))
        
        return scenario
    
    @classmethod
    def create_trend_monitor_scenario(cls) -> IntegrationScenario:
        """Create trend monitor ServiceAPI scenario."""
        scenario = IntegrationScenario(
            scenario_id="API_003",
            name="ServiceAPI Trend Monitor",
            description="Verify ServiceAPI trend monitoring methods work correctly",
            category=ScenarioCategory.SERVICE_API,
            preconditions=[
                "ServiceAPI is initialized",
                "TrendMonitorService is available"
            ],
            postconditions=[
                "MTF trends retrieved correctly",
                "Trend alignment validated"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="API_003_01",
            description="Test get_mtf_trends()",
            action="Call get_mtf_trends for XAUUSD",
            expected_result="4-pillar MTF trends returned (15m, 1h, 4h, 1d)"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_003_02",
            description="Test validate_v3_trend_alignment()",
            action="Call validate_v3_trend_alignment with BUY direction",
            expected_result="Alignment status returned (3/4 required)"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_003_03",
            description="Test update_trend_pulse()",
            action="Call update_trend_pulse with pulse data",
            expected_result="market_trends table updated"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="API_003_04",
            description="Test check_pulse_alignment()",
            action="Call check_pulse_alignment for BUY direction",
            expected_result="Pulse alignment status returned"
        ))
        
        return scenario
    
    @classmethod
    def create_all_scenarios(cls) -> List[IntegrationScenario]:
        """Create all ServiceAPI integration scenarios."""
        return [
            cls.create_order_execution_scenario(),
            cls.create_risk_management_scenario(),
            cls.create_trend_monitor_scenario(),
        ]


class DatabaseIntegrationScenarios:
    """Database integration test scenarios."""
    
    @classmethod
    def create_v3_database_scenario(cls) -> IntegrationScenario:
        """Create V3 database integration scenario."""
        scenario = IntegrationScenario(
            scenario_id="DB_001",
            name="V3 Database Integration",
            description="Verify V3 database operations work correctly",
            category=ScenarioCategory.DATABASE,
            preconditions=[
                "V3 database is initialized",
                "Schema is created"
            ],
            postconditions=[
                "Trades can be inserted and queried",
                "Signals are logged",
                "Daily stats are aggregated"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="DB_001_01",
            description="Insert V3 trade",
            action="Insert trade into combined_v3_trades table",
            expected_result="Trade inserted with auto-generated ID"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_001_02",
            description="Query V3 trade",
            action="Query trade by ID",
            expected_result="Trade data retrieved correctly"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_001_03",
            description="Log V3 signal",
            action="Insert signal into v3_signals_log table",
            expected_result="Signal logged with timestamp"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_001_04",
            description="Update daily stats",
            action="Update v3_daily_stats table",
            expected_result="Daily stats aggregated correctly"
        ))
        
        return scenario
    
    @classmethod
    def create_v6_database_scenario(cls) -> IntegrationScenario:
        """Create V6 database integration scenario."""
        scenario = IntegrationScenario(
            scenario_id="DB_002",
            name="V6 Database Integration",
            description="Verify V6 database operations work correctly",
            category=ScenarioCategory.DATABASE,
            preconditions=[
                "V6 databases are initialized",
                "Schemas are created for all 4 timeframes"
            ],
            postconditions=[
                "Trades can be inserted and queried per timeframe",
                "Trend pulse data is stored",
                "Market trends are updated"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="DB_002_01",
            description="Insert V6 1M trade",
            action="Insert trade into v6_1m_trades table",
            expected_result="Trade inserted with ORDER_B_ONLY routing"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_002_02",
            description="Insert V6 5M trade",
            action="Insert trade into v6_5m_trades table",
            expected_result="Trade inserted with DUAL_ORDERS routing"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_002_03",
            description="Update market trends",
            action="Update market_trends table with pulse data",
            expected_result="Market trends updated with bull/bear counts"
        ))
        
        return scenario
    
    @classmethod
    def create_database_sync_scenario(cls) -> IntegrationScenario:
        """Create database sync integration scenario."""
        scenario = IntegrationScenario(
            scenario_id="DB_003",
            name="Database Sync Integration",
            description="Verify database sync between plugin DBs and central DB",
            category=ScenarioCategory.DATABASE,
            preconditions=[
                "All plugin databases are initialized",
                "Central database is initialized",
                "Sync manager is running"
            ],
            postconditions=[
                "Data synced to central database",
                "No data loss during sync",
                "Sync interval = 5 minutes"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="DB_003_01",
            description="Trigger sync from V3 to central",
            action="Run sync_v3_to_central()",
            expected_result="V3 trades synced to central database"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_003_02",
            description="Trigger sync from V6 to central",
            action="Run sync_v6_to_central()",
            expected_result="V6 trades synced to central database"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="DB_003_03",
            description="Verify central database aggregation",
            action="Query central database for all trades",
            expected_result="All trades from V3 and V6 present"
        ))
        
        return scenario
    
    @classmethod
    def create_all_scenarios(cls) -> List[IntegrationScenario]:
        """Create all database integration scenarios."""
        return [
            cls.create_v3_database_scenario(),
            cls.create_v6_database_scenario(),
            cls.create_database_sync_scenario(),
        ]


class EndToEndScenarios:
    """End-to-end workflow test scenarios."""
    
    @classmethod
    def create_v3_full_workflow_scenario(cls) -> IntegrationScenario:
        """Create V3 full workflow scenario."""
        scenario = IntegrationScenario(
            scenario_id="E2E_001",
            name="V3 Full Workflow",
            description="End-to-end V3 signal processing workflow",
            category=ScenarioCategory.END_TO_END,
            preconditions=[
                "V3 plugin is enabled",
                "All services are running",
                "Database is ready"
            ],
            postconditions=[
                "Signal processed completely",
                "Orders placed (or simulated)",
                "Database updated",
                "Notifications sent"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_01",
            description="Receive V3 signal from TradingView",
            action="Webhook receives Institutional_Launchpad signal",
            expected_result="Signal parsed and validated"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_02",
            description="Route signal to logic",
            action="Routing matrix determines LOGIC1",
            expected_result="Signal routed to LOGIC1 (1.25x multiplier)"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_03",
            description="Extract MTF pillars",
            action="Extract 4 pillars from MTF string",
            expected_result="Pillars extracted: 15m, 1h, 4h, 1d"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_04",
            description="Validate trend alignment",
            action="Check 3/4 pillar alignment",
            expected_result="Trend alignment validated"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_05",
            description="Calculate position size",
            action="Apply 4-step position sizing",
            expected_result="Lot size calculated with consensus and logic multipliers"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_06",
            description="Place dual orders",
            action="Place Order A (V3 SL) and Order B (Fixed $10 SL)",
            expected_result="Both orders placed with 50/50 split"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_07",
            description="Update database",
            action="Insert trade into combined_v3_trades",
            expected_result="Trade recorded with all metadata"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_001_08",
            description="Send notification",
            action="Send entry notification via Telegram",
            expected_result="Notification sent to notification bot"
        ))
        
        return scenario
    
    @classmethod
    def create_v6_full_workflow_scenario(cls) -> IntegrationScenario:
        """Create V6 full workflow scenario."""
        scenario = IntegrationScenario(
            scenario_id="E2E_002",
            name="V6 Full Workflow",
            description="End-to-end V6 alert processing workflow",
            category=ScenarioCategory.END_TO_END,
            preconditions=[
                "V6 plugins are enabled",
                "All services are running",
                "Database is ready"
            ],
            postconditions=[
                "Alert processed completely",
                "Orders placed based on timeframe routing",
                "Database updated",
                "Notifications sent"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_002_01",
            description="Receive V6 5M alert",
            action="Webhook receives V6 5M momentum alert",
            expected_result="Alert parsed and validated"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_002_02",
            description="Check entry conditions",
            action="Verify ADX >= 25, confidence >= 70, 15m aligned",
            expected_result="Entry conditions met"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_002_03",
            description="Determine order routing",
            action="5M timeframe routes to DUAL_ORDERS",
            expected_result="DUAL_ORDERS routing selected"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_002_04",
            description="Place dual orders",
            action="Place Order A (TP2) and Order B (TP1)",
            expected_result="Both orders placed with same SL"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_002_05",
            description="Update database",
            action="Insert trade into v6_5m_trades",
            expected_result="Trade recorded with DUAL_ORDERS routing"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="E2E_002_06",
            description="Send notification",
            action="Send entry notification via Telegram",
            expected_result="Notification sent with V6 5M details"
        ))
        
        return scenario
    
    @classmethod
    def create_all_scenarios(cls) -> List[IntegrationScenario]:
        """Create all end-to-end scenarios."""
        return [
            cls.create_v3_full_workflow_scenario(),
            cls.create_v6_full_workflow_scenario(),
        ]


class ShadowModeScenarios:
    """Shadow mode test scenarios."""
    
    @classmethod
    def create_v3_shadow_scenario(cls) -> IntegrationScenario:
        """Create V3 shadow mode scenario."""
        scenario = IntegrationScenario(
            scenario_id="SHADOW_001",
            name="V3 Shadow Mode (72-Hour)",
            description="Verify V3 shadow mode operation for 72 hours",
            category=ScenarioCategory.SHADOW_MODE,
            preconditions=[
                "Shadow mode is enabled for V3",
                "All 12 signal types are configured",
                "Logging is enabled"
            ],
            postconditions=[
                "All signals logged",
                "Hypothetical P&L calculated",
                "Zero real MT5 orders placed"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_001_01",
            description="Enable shadow mode",
            action="Set shadow_mode=true in V3 config",
            expected_result="Shadow mode enabled"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_001_02",
            description="Process signals in shadow mode",
            action="Process all 12 signal types",
            expected_result="All signals logged without real orders"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_001_03",
            description="Verify no real orders",
            action="Check MT5 for orders from shadow period",
            expected_result="Zero real orders placed"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_001_04",
            description="Calculate hypothetical P&L",
            action="Calculate P&L based on logged signals",
            expected_result="Hypothetical P&L calculated"
        ))
        
        return scenario
    
    @classmethod
    def create_v6_shadow_scenario(cls) -> IntegrationScenario:
        """Create V6 shadow mode scenario."""
        scenario = IntegrationScenario(
            scenario_id="SHADOW_002",
            name="V6 Shadow Mode (72-Hour)",
            description="Verify V6 shadow mode operation for all 4 timeframes",
            category=ScenarioCategory.SHADOW_MODE,
            preconditions=[
                "Shadow mode is enabled for all V6 plugins",
                "All timeframes are configured",
                "Logging is enabled"
            ],
            postconditions=[
                "All alerts logged per timeframe",
                "Order routing simulated correctly",
                "Zero real MT5 orders placed"
            ]
        )
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_002_01",
            description="Enable shadow mode for all V6 plugins",
            action="Set shadow_mode=true in all V6 configs",
            expected_result="Shadow mode enabled for 1M, 5M, 15M, 1H"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_002_02",
            description="Verify 1M ORDER_B_ONLY simulation",
            action="Process 1M alerts in shadow mode",
            expected_result="ORDER_B_ONLY simulated correctly"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_002_03",
            description="Verify 5M DUAL_ORDERS simulation",
            action="Process 5M alerts in shadow mode",
            expected_result="DUAL_ORDERS simulated correctly"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_002_04",
            description="Verify 15M ORDER_A_ONLY simulation",
            action="Process 15M alerts in shadow mode",
            expected_result="ORDER_A_ONLY simulated correctly"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_002_05",
            description="Verify 1H ORDER_A_ONLY simulation",
            action="Process 1H alerts in shadow mode",
            expected_result="ORDER_A_ONLY simulated correctly"
        ))
        
        scenario.add_step(ScenarioStep(
            step_id="SHADOW_002_06",
            description="Verify no real orders",
            action="Check MT5 for orders from shadow period",
            expected_result="Zero real orders placed"
        ))
        
        return scenario
    
    @classmethod
    def create_all_scenarios(cls) -> List[IntegrationScenario]:
        """Create all shadow mode scenarios."""
        return [
            cls.create_v3_shadow_scenario(),
            cls.create_v6_shadow_scenario(),
        ]


class ScenarioRegistry:
    """Registry of all integration test scenarios."""
    
    @classmethod
    def get_all_scenarios(cls) -> Dict[str, List[IntegrationScenario]]:
        """Get all scenarios organized by category."""
        return {
            "v3_v6_integration": V3V6IntegrationScenarios.create_all_scenarios(),
            "service_api": ServiceAPIIntegrationScenarios.create_all_scenarios(),
            "database": DatabaseIntegrationScenarios.create_all_scenarios(),
            "end_to_end": EndToEndScenarios.create_all_scenarios(),
            "shadow_mode": ShadowModeScenarios.create_all_scenarios(),
        }
    
    @classmethod
    def get_scenario_by_id(cls, scenario_id: str) -> Optional[IntegrationScenario]:
        """Get scenario by ID."""
        for scenarios in cls.get_all_scenarios().values():
            for scenario in scenarios:
                if scenario.scenario_id == scenario_id:
                    return scenario
        return None
    
    @classmethod
    def get_scenarios_by_category(cls, category: ScenarioCategory) -> List[IntegrationScenario]:
        """Get scenarios by category."""
        category_map = {
            ScenarioCategory.V3_V6_INTEGRATION: "v3_v6_integration",
            ScenarioCategory.SERVICE_API: "service_api",
            ScenarioCategory.DATABASE: "database",
            ScenarioCategory.END_TO_END: "end_to_end",
            ScenarioCategory.SHADOW_MODE: "shadow_mode",
        }
        key = category_map.get(category)
        if key:
            return cls.get_all_scenarios().get(key, [])
        return []
    
    @classmethod
    def get_total_scenario_count(cls) -> int:
        """Get total number of scenarios."""
        return sum(len(scenarios) for scenarios in cls.get_all_scenarios().values())
    
    @classmethod
    def get_total_step_count(cls) -> int:
        """Get total number of steps across all scenarios."""
        total = 0
        for scenarios in cls.get_all_scenarios().values():
            for scenario in scenarios:
                total += scenario.total_steps
        return total


def export_all_scenarios_markdown(output_dir: str) -> None:
    """Export all scenarios to markdown files."""
    import os
    
    all_scenarios = ScenarioRegistry.get_all_scenarios()
    
    for category, scenarios in all_scenarios.items():
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        for scenario in scenarios:
            filename = f"{scenario.scenario_id}.md"
            filepath = os.path.join(category_dir, filename)
            with open(filepath, 'w') as f:
                f.write(scenario.to_markdown())
