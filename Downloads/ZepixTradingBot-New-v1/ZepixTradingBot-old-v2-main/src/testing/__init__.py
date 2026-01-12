"""
Testing Framework for V5 Hybrid Plugin Architecture.

This package provides comprehensive testing tools:
- Automated test runners for V3/V6 tests
- Pytest markers for test categorization
- Test data generators for all scenarios
- Manual test guides and checklists
- Quality gate enforcer for release verification
- Integration test scenarios

Version: 1.0
Date: 2026-01-12
"""

from .test_runners import (
    TestCategory,
    TestPriority,
    TestResult,
    TestSuiteResult,
    TestRunner,
    V3TestRunner,
    V6TestRunner,
    IntegrationTestRunner,
    ShadowModeTestRunner,
)

from .pytest_markers import (
    MarkerCategory,
    PytestMarker,
    MarkerRegistry,
    TestSuite,
    TestSuiteRegistry,
    generate_conftest_markers,
    generate_pytest_ini,
)

from .test_data_generators import (
    SignalType,
    Direction,
    LogicRoute,
    OrderRouting,
    ADXStrength,
    V3SignalData,
    V6AlertData,
    DualOrderData,
    TrendPulseData,
    V3SignalGenerator,
    V6AlertGenerator,
    DualOrderGenerator,
    TrendPulseGenerator,
    ShadowModeDataGenerator,
    IntegrationTestDataGenerator,
)

from .manual_test_guides import (
    ChecklistStatus,
    ChecklistItem,
    ManualTestChecklist,
    V3ManualTestGuide,
    V6ManualTestGuide,
    IntegrationManualTestGuide,
    ShadowModeManualTestGuide,
    ProductionReadinessChecklist,
    generate_all_checklists,
    export_all_checklists_markdown,
)

from .quality_gate import (
    GateStatus,
    GateCategory,
    GateResult,
    QualityGateReport,
    QualityGateEnforcer,
    PreReleaseChecker,
    ChecklistGateChecker,
    run_quality_gates,
    check_release_readiness,
)

from .integration_scenarios import (
    ScenarioStatus,
    ScenarioCategory,
    ScenarioStep,
    IntegrationScenario,
    V3V6IntegrationScenarios,
    ServiceAPIIntegrationScenarios,
    DatabaseIntegrationScenarios,
    EndToEndScenarios,
    ShadowModeScenarios,
    ScenarioRegistry,
    export_all_scenarios_markdown,
)

__all__ = [
    # Test Runners
    "TestCategory",
    "TestPriority",
    "TestResult",
    "TestSuiteResult",
    "TestRunner",
    "V3TestRunner",
    "V6TestRunner",
    "IntegrationTestRunner",
    "ShadowModeTestRunner",
    
    # Pytest Markers
    "MarkerCategory",
    "PytestMarker",
    "MarkerRegistry",
    "TestSuite",
    "TestSuiteRegistry",
    "generate_conftest_markers",
    "generate_pytest_ini",
    
    # Test Data Generators
    "SignalType",
    "Direction",
    "LogicRoute",
    "OrderRouting",
    "ADXStrength",
    "V3SignalData",
    "V6AlertData",
    "DualOrderData",
    "TrendPulseData",
    "V3SignalGenerator",
    "V6AlertGenerator",
    "DualOrderGenerator",
    "TrendPulseGenerator",
    "ShadowModeDataGenerator",
    "IntegrationTestDataGenerator",
    
    # Manual Test Guides
    "ChecklistStatus",
    "ChecklistItem",
    "ManualTestChecklist",
    "V3ManualTestGuide",
    "V6ManualTestGuide",
    "IntegrationManualTestGuide",
    "ShadowModeManualTestGuide",
    "ProductionReadinessChecklist",
    "generate_all_checklists",
    "export_all_checklists_markdown",
    
    # Quality Gate
    "GateStatus",
    "GateCategory",
    "GateResult",
    "QualityGateReport",
    "QualityGateEnforcer",
    "PreReleaseChecker",
    "ChecklistGateChecker",
    "run_quality_gates",
    "check_release_readiness",
    
    # Integration Scenarios
    "ScenarioStatus",
    "ScenarioCategory",
    "ScenarioStep",
    "IntegrationScenario",
    "V3V6IntegrationScenarios",
    "ServiceAPIIntegrationScenarios",
    "DatabaseIntegrationScenarios",
    "EndToEndScenarios",
    "ShadowModeScenarios",
    "ScenarioRegistry",
    "export_all_scenarios_markdown",
]

__version__ = "1.0.0"
