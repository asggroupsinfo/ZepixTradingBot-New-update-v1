"""
Test Suite for Document 12: Testing Checklists

This test file verifies the implementation of the Testing Framework:
- Automated Test Runners
- Pytest Markers
- Test Data Generators
- Manual Test Guides
- Quality Gate Enforcer
- Integration Test Scenarios

Document: 12_TESTING_CHECKLISTS.md
Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import json
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestTestingPackageStructure(unittest.TestCase):
    """Test testing package structure and imports."""
    
    def test_testing_package_exists(self):
        """Test that testing package exists."""
        testing_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing'
        )
        self.assertTrue(os.path.exists(testing_path))
    
    def test_testing_init_exists(self):
        """Test that testing __init__.py exists."""
        init_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', '__init__.py'
        )
        self.assertTrue(os.path.exists(init_path))
    
    def test_test_runners_module_exists(self):
        """Test that test_runners.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', 'test_runners.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_pytest_markers_module_exists(self):
        """Test that pytest_markers.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', 'pytest_markers.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_test_data_generators_module_exists(self):
        """Test that test_data_generators.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', 'test_data_generators.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_manual_test_guides_module_exists(self):
        """Test that manual_test_guides.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', 'manual_test_guides.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_quality_gate_module_exists(self):
        """Test that quality_gate.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', 'quality_gate.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_integration_scenarios_module_exists(self):
        """Test that integration_scenarios.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'testing', 'integration_scenarios.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_package_imports(self):
        """Test that all package imports work."""
        from testing import (
            TestRunner, V3TestRunner, V6TestRunner,
            MarkerRegistry, TestSuiteRegistry,
            V3SignalGenerator, V6AlertGenerator,
            V3ManualTestGuide, V6ManualTestGuide,
            QualityGateEnforcer, PreReleaseChecker,
            ScenarioRegistry
        )
        self.assertIsNotNone(TestRunner)
        self.assertIsNotNone(V3TestRunner)
        self.assertIsNotNone(V6TestRunner)
        self.assertIsNotNone(MarkerRegistry)
        self.assertIsNotNone(TestSuiteRegistry)
        self.assertIsNotNone(V3SignalGenerator)
        self.assertIsNotNone(V6AlertGenerator)
        self.assertIsNotNone(V3ManualTestGuide)
        self.assertIsNotNone(V6ManualTestGuide)
        self.assertIsNotNone(QualityGateEnforcer)
        self.assertIsNotNone(PreReleaseChecker)
        self.assertIsNotNone(ScenarioRegistry)


class TestTestRunnerEnums(unittest.TestCase):
    """Test test runner enumerations."""
    
    def test_test_category_enum(self):
        """Test TestCategory enum values."""
        from testing.test_runners import TestCategory
        
        self.assertEqual(TestCategory.V3_SIGNAL_PROCESSING.value, "v3_signal_processing")
        self.assertEqual(TestCategory.V3_ROUTING_MATRIX.value, "v3_routing_matrix")
        self.assertEqual(TestCategory.V3_DUAL_ORDER.value, "v3_dual_order")
        self.assertEqual(TestCategory.V3_MTF_PILLAR.value, "v3_mtf_pillar")
        self.assertEqual(TestCategory.V3_POSITION_SIZING.value, "v3_position_sizing")
        self.assertEqual(TestCategory.V3_TREND_BYPASS.value, "v3_trend_bypass")
        self.assertEqual(TestCategory.V6_1M_SCALPING.value, "v6_1m_scalping")
        self.assertEqual(TestCategory.V6_5M_MOMENTUM.value, "v6_5m_momentum")
        self.assertEqual(TestCategory.V6_15M_INTRADAY.value, "v6_15m_intraday")
        self.assertEqual(TestCategory.V6_1H_SWING.value, "v6_1h_swing")
        self.assertEqual(TestCategory.V6_TREND_PULSE.value, "v6_trend_pulse")
        self.assertEqual(TestCategory.INTEGRATION.value, "integration")
        self.assertEqual(TestCategory.SHADOW_MODE.value, "shadow_mode")
        self.assertEqual(TestCategory.ALL.value, "all")
    
    def test_test_priority_enum(self):
        """Test TestPriority enum values."""
        from testing.test_runners import TestPriority
        
        self.assertEqual(TestPriority.CRITICAL.value, "critical")
        self.assertEqual(TestPriority.HIGH.value, "high")
        self.assertEqual(TestPriority.MEDIUM.value, "medium")
        self.assertEqual(TestPriority.LOW.value, "low")


class TestTestResult(unittest.TestCase):
    """Test TestResult dataclass."""
    
    def test_test_result_creation(self):
        """Test TestResult creation."""
        from testing.test_runners import TestResult, TestCategory
        
        result = TestResult(
            test_name="test_example",
            category=TestCategory.V3_SIGNAL_PROCESSING,
            passed=True,
            duration_ms=100.5
        )
        
        self.assertEqual(result.test_name, "test_example")
        self.assertEqual(result.category, TestCategory.V3_SIGNAL_PROCESSING)
        self.assertTrue(result.passed)
        self.assertEqual(result.duration_ms, 100.5)
        self.assertIsNone(result.error_message)
    
    def test_test_result_with_error(self):
        """Test TestResult with error."""
        from testing.test_runners import TestResult, TestCategory
        
        result = TestResult(
            test_name="test_failed",
            category=TestCategory.V3_ROUTING_MATRIX,
            passed=False,
            duration_ms=50.0,
            error_message="Assertion failed"
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.error_message, "Assertion failed")
    
    def test_test_result_to_dict(self):
        """Test TestResult to_dict method."""
        from testing.test_runners import TestResult, TestCategory
        
        result = TestResult(
            test_name="test_example",
            category=TestCategory.V3_DUAL_ORDER,
            passed=True,
            duration_ms=75.0
        )
        
        result_dict = result.to_dict()
        self.assertEqual(result_dict["test_name"], "test_example")
        self.assertEqual(result_dict["category"], "v3_dual_order")
        self.assertTrue(result_dict["passed"])
        self.assertEqual(result_dict["duration_ms"], 75.0)


class TestTestSuiteResult(unittest.TestCase):
    """Test TestSuiteResult dataclass."""
    
    def test_test_suite_result_creation(self):
        """Test TestSuiteResult creation."""
        from testing.test_runners import TestSuiteResult, TestCategory
        
        suite = TestSuiteResult(
            suite_name="V3 Tests",
            category=TestCategory.V3_SIGNAL_PROCESSING,
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
            skipped_tests=0,
            duration_ms=1000.0
        )
        
        self.assertEqual(suite.suite_name, "V3 Tests")
        self.assertEqual(suite.total_tests, 10)
        self.assertEqual(suite.passed_tests, 9)
        self.assertEqual(suite.failed_tests, 1)
    
    def test_test_suite_result_pass_rate(self):
        """Test TestSuiteResult pass_rate property."""
        from testing.test_runners import TestSuiteResult, TestCategory
        
        suite = TestSuiteResult(
            suite_name="Test Suite",
            category=TestCategory.V3_ROUTING_MATRIX,
            total_tests=100,
            passed_tests=90,
            failed_tests=10,
            skipped_tests=0,
            duration_ms=5000.0
        )
        
        self.assertEqual(suite.pass_rate, 90.0)
    
    def test_test_suite_result_all_passed(self):
        """Test TestSuiteResult all_passed property."""
        from testing.test_runners import TestSuiteResult, TestCategory
        
        suite_passed = TestSuiteResult(
            suite_name="All Passed",
            category=TestCategory.V3_MTF_PILLAR,
            total_tests=50,
            passed_tests=50,
            failed_tests=0,
            skipped_tests=0,
            duration_ms=2000.0
        )
        
        suite_failed = TestSuiteResult(
            suite_name="Some Failed",
            category=TestCategory.V3_POSITION_SIZING,
            total_tests=50,
            passed_tests=45,
            failed_tests=5,
            skipped_tests=0,
            duration_ms=2000.0
        )
        
        self.assertTrue(suite_passed.all_passed)
        self.assertFalse(suite_failed.all_passed)


class TestTestRunner(unittest.TestCase):
    """Test TestRunner class."""
    
    def test_test_runner_creation(self):
        """Test TestRunner creation."""
        from testing.test_runners import TestRunner
        
        runner = TestRunner()
        self.assertIsNotNone(runner)
        self.assertEqual(runner.results, [])
    
    def test_test_runner_pytest_markers(self):
        """Test TestRunner PYTEST_MARKERS mapping."""
        from testing.test_runners import TestRunner, TestCategory
        
        self.assertEqual(TestRunner.PYTEST_MARKERS[TestCategory.V3_SIGNAL_PROCESSING], "v3_signal")
        self.assertEqual(TestRunner.PYTEST_MARKERS[TestCategory.V3_ROUTING_MATRIX], "v3_routing")
        self.assertEqual(TestRunner.PYTEST_MARKERS[TestCategory.V6_1M_SCALPING], "v6_1m")
        self.assertEqual(TestRunner.PYTEST_MARKERS[TestCategory.V6_5M_MOMENTUM], "v6_5m")
        self.assertEqual(TestRunner.PYTEST_MARKERS[TestCategory.INTEGRATION], "integration")
        self.assertEqual(TestRunner.PYTEST_MARKERS[TestCategory.SHADOW_MODE], "shadow_mode")
    
    def test_test_runner_get_summary(self):
        """Test TestRunner get_summary method."""
        from testing.test_runners import TestRunner
        
        runner = TestRunner()
        summary = runner.get_summary()
        
        self.assertIn("total_suites", summary)
        self.assertIn("total_tests", summary)
        self.assertIn("total_passed", summary)
        self.assertIn("total_failed", summary)
        self.assertIn("overall_pass_rate", summary)


class TestV3TestRunner(unittest.TestCase):
    """Test V3TestRunner class."""
    
    def test_v3_test_runner_creation(self):
        """Test V3TestRunner creation."""
        from testing.test_runners import V3TestRunner
        
        runner = V3TestRunner()
        self.assertIsNotNone(runner)
    
    def test_v3_test_runner_signal_types(self):
        """Test V3TestRunner SIGNAL_TYPES list."""
        from testing.test_runners import V3TestRunner
        
        self.assertEqual(len(V3TestRunner.SIGNAL_TYPES), 12)
        self.assertIn("Institutional_Launchpad", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("Liquidity_Trap", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("Golden_Pocket", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("Screener", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("entry_v3", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("Exit_Bullish", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("Exit_Bearish", V3TestRunner.SIGNAL_TYPES)
        self.assertIn("Trend_Pulse", V3TestRunner.SIGNAL_TYPES)


class TestV6TestRunner(unittest.TestCase):
    """Test V6TestRunner class."""
    
    def test_v6_test_runner_creation(self):
        """Test V6TestRunner creation."""
        from testing.test_runners import V6TestRunner
        
        runner = V6TestRunner()
        self.assertIsNotNone(runner)
    
    def test_v6_test_runner_timeframes(self):
        """Test V6TestRunner TIMEFRAMES list."""
        from testing.test_runners import V6TestRunner
        
        self.assertEqual(V6TestRunner.TIMEFRAMES, ["1m", "5m", "15m", "1h"])
    
    def test_v6_test_runner_order_routing(self):
        """Test V6TestRunner ORDER_ROUTING mapping."""
        from testing.test_runners import V6TestRunner
        
        self.assertEqual(V6TestRunner.ORDER_ROUTING["1m"], "ORDER_B_ONLY")
        self.assertEqual(V6TestRunner.ORDER_ROUTING["5m"], "DUAL_ORDERS")
        self.assertEqual(V6TestRunner.ORDER_ROUTING["15m"], "ORDER_A_ONLY")
        self.assertEqual(V6TestRunner.ORDER_ROUTING["1h"], "ORDER_A_ONLY")
    
    def test_v6_test_runner_get_order_routing(self):
        """Test V6TestRunner get_order_routing method."""
        from testing.test_runners import V6TestRunner
        
        runner = V6TestRunner()
        self.assertEqual(runner.get_order_routing("1m"), "ORDER_B_ONLY")
        self.assertEqual(runner.get_order_routing("5m"), "DUAL_ORDERS")
        self.assertEqual(runner.get_order_routing("15m"), "ORDER_A_ONLY")
        self.assertEqual(runner.get_order_routing("1h"), "ORDER_A_ONLY")
        self.assertEqual(runner.get_order_routing("invalid"), "UNKNOWN")


class TestShadowModeTestRunner(unittest.TestCase):
    """Test ShadowModeTestRunner class."""
    
    def test_shadow_mode_test_runner_creation(self):
        """Test ShadowModeTestRunner creation."""
        from testing.test_runners import ShadowModeTestRunner
        
        runner = ShadowModeTestRunner()
        self.assertIsNotNone(runner)
    
    def test_shadow_mode_duration(self):
        """Test ShadowModeTestRunner SHADOW_DURATION_HOURS."""
        from testing.test_runners import ShadowModeTestRunner
        
        self.assertEqual(ShadowModeTestRunner.SHADOW_DURATION_HOURS, 72)
    
    def test_verify_no_real_trades(self):
        """Test verify_no_real_trades method."""
        from testing.test_runners import ShadowModeTestRunner
        
        runner = ShadowModeTestRunner()
        self.assertTrue(runner.verify_no_real_trades())
    
    def test_get_hypothetical_pnl(self):
        """Test get_hypothetical_pnl method."""
        from testing.test_runners import ShadowModeTestRunner
        
        runner = ShadowModeTestRunner()
        pnl = runner.get_hypothetical_pnl()
        
        self.assertIn("v3_combined", pnl)
        self.assertIn("v6_1m", pnl)
        self.assertIn("v6_5m", pnl)
        self.assertIn("v6_15m", pnl)
        self.assertIn("v6_1h", pnl)
        self.assertIn("total", pnl)


class TestPytestMarkers(unittest.TestCase):
    """Test pytest markers module."""
    
    def test_marker_category_enum(self):
        """Test MarkerCategory enum."""
        from testing.pytest_markers import MarkerCategory
        
        self.assertEqual(MarkerCategory.V3.value, "v3")
        self.assertEqual(MarkerCategory.V6.value, "v6")
        self.assertEqual(MarkerCategory.INTEGRATION.value, "integration")
        self.assertEqual(MarkerCategory.SHADOW_MODE.value, "shadow_mode")
        self.assertEqual(MarkerCategory.PRIORITY.value, "priority")
    
    def test_pytest_marker_creation(self):
        """Test PytestMarker creation."""
        from testing.pytest_markers import PytestMarker, MarkerCategory
        
        marker = PytestMarker(
            name="v3_signal",
            description="V3 signal processing tests",
            category=MarkerCategory.V3,
            priority="critical"
        )
        
        self.assertEqual(marker.name, "v3_signal")
        self.assertEqual(marker.description, "V3 signal processing tests")
        self.assertEqual(marker.category, MarkerCategory.V3)
        self.assertEqual(marker.priority, "critical")
    
    def test_pytest_marker_to_ini_format(self):
        """Test PytestMarker to_ini_format method."""
        from testing.pytest_markers import PytestMarker, MarkerCategory
        
        marker = PytestMarker(
            name="v3_routing",
            description="V3 routing matrix tests",
            category=MarkerCategory.V3
        )
        
        ini_format = marker.to_ini_format()
        self.assertEqual(ini_format, "v3_routing: V3 routing matrix tests")
    
    def test_pytest_marker_to_decorator(self):
        """Test PytestMarker to_decorator method."""
        from testing.pytest_markers import PytestMarker, MarkerCategory
        
        marker = PytestMarker(
            name="v6_1m",
            description="V6 1M tests",
            category=MarkerCategory.V6
        )
        
        decorator = marker.to_decorator()
        self.assertEqual(decorator, "@pytest.mark.v6_1m")


class TestMarkerRegistry(unittest.TestCase):
    """Test MarkerRegistry class."""
    
    def test_v3_markers(self):
        """Test V3 markers list."""
        from testing.pytest_markers import MarkerRegistry
        
        self.assertEqual(len(MarkerRegistry.V3_MARKERS), 6)
        marker_names = [m.name for m in MarkerRegistry.V3_MARKERS]
        self.assertIn("v3_signal", marker_names)
        self.assertIn("v3_routing", marker_names)
        self.assertIn("v3_dual_order", marker_names)
        self.assertIn("v3_mtf", marker_names)
        self.assertIn("v3_position", marker_names)
        self.assertIn("v3_trend_bypass", marker_names)
    
    def test_v6_markers(self):
        """Test V6 markers list."""
        from testing.pytest_markers import MarkerRegistry
        
        self.assertEqual(len(MarkerRegistry.V6_MARKERS), 5)
        marker_names = [m.name for m in MarkerRegistry.V6_MARKERS]
        self.assertIn("v6_1m", marker_names)
        self.assertIn("v6_5m", marker_names)
        self.assertIn("v6_15m", marker_names)
        self.assertIn("v6_1h", marker_names)
        self.assertIn("v6_trend_pulse", marker_names)
    
    def test_integration_markers(self):
        """Test integration markers list."""
        from testing.pytest_markers import MarkerRegistry
        
        self.assertEqual(len(MarkerRegistry.INTEGRATION_MARKERS), 3)
        marker_names = [m.name for m in MarkerRegistry.INTEGRATION_MARKERS]
        self.assertIn("integration", marker_names)
        self.assertIn("service_api", marker_names)
        self.assertIn("database", marker_names)
    
    def test_shadow_mode_markers(self):
        """Test shadow mode markers list."""
        from testing.pytest_markers import MarkerRegistry
        
        self.assertEqual(len(MarkerRegistry.SHADOW_MODE_MARKERS), 3)
        marker_names = [m.name for m in MarkerRegistry.SHADOW_MODE_MARKERS]
        self.assertIn("shadow_mode", marker_names)
        self.assertIn("shadow_v3", marker_names)
        self.assertIn("shadow_v6", marker_names)
    
    def test_priority_markers(self):
        """Test priority markers list."""
        from testing.pytest_markers import MarkerRegistry
        
        self.assertEqual(len(MarkerRegistry.PRIORITY_MARKERS), 4)
        marker_names = [m.name for m in MarkerRegistry.PRIORITY_MARKERS]
        self.assertIn("critical", marker_names)
        self.assertIn("high", marker_names)
        self.assertIn("medium", marker_names)
        self.assertIn("low", marker_names)
    
    def test_get_all_markers(self):
        """Test get_all_markers method."""
        from testing.pytest_markers import MarkerRegistry
        
        all_markers = MarkerRegistry.get_all_markers()
        self.assertEqual(len(all_markers), 21)
    
    def test_get_marker_by_name(self):
        """Test get_marker_by_name method."""
        from testing.pytest_markers import MarkerRegistry
        
        marker = MarkerRegistry.get_marker_by_name("v3_signal")
        self.assertIsNotNone(marker)
        self.assertEqual(marker.name, "v3_signal")
        
        unknown = MarkerRegistry.get_marker_by_name("unknown_marker")
        self.assertIsNone(unknown)
    
    def test_get_critical_markers(self):
        """Test get_critical_markers method."""
        from testing.pytest_markers import MarkerRegistry
        
        critical = MarkerRegistry.get_critical_markers()
        for marker in critical:
            self.assertEqual(marker.priority, "critical")
    
    def test_generate_pytest_ini_markers(self):
        """Test generate_pytest_ini_markers method."""
        from testing.pytest_markers import MarkerRegistry
        
        ini_content = MarkerRegistry.generate_pytest_ini_markers()
        self.assertIn("markers =", ini_content)
        self.assertIn("v3_signal:", ini_content)
        self.assertIn("v6_1m:", ini_content)


class TestTestSuiteRegistry(unittest.TestCase):
    """Test TestSuiteRegistry class."""
    
    def test_get_all_suites(self):
        """Test get_all_suites method."""
        from testing.pytest_markers import TestSuiteRegistry
        
        suites = TestSuiteRegistry.get_all_suites()
        self.assertIn("v3_full", suites)
        self.assertIn("v6_full", suites)
        self.assertIn("integration", suites)
        self.assertIn("shadow_mode", suites)
        self.assertIn("critical_only", suites)
        self.assertIn("pre_release", suites)
    
    def test_get_suite(self):
        """Test get_suite method."""
        from testing.pytest_markers import TestSuiteRegistry
        
        suite = TestSuiteRegistry.get_suite("v3_full")
        self.assertIsNotNone(suite)
        self.assertEqual(suite.name, "V3 Full Suite")
        
        unknown = TestSuiteRegistry.get_suite("unknown_suite")
        self.assertIsNone(unknown)
    
    def test_get_suite_names(self):
        """Test get_suite_names method."""
        from testing.pytest_markers import TestSuiteRegistry
        
        names = TestSuiteRegistry.get_suite_names()
        self.assertIn("v3_full", names)
        self.assertIn("v6_full", names)


class TestV3SignalData(unittest.TestCase):
    """Test V3SignalData dataclass."""
    
    def test_v3_signal_data_creation(self):
        """Test V3SignalData creation."""
        from testing.test_data_generators import V3SignalData
        
        signal = V3SignalData(
            signal_type="Institutional_Launchpad",
            tf="5",
            consensus=8,
            direction="BUY",
            mtf="1,1,1,1,1,-1"
        )
        
        self.assertEqual(signal.signal_type, "Institutional_Launchpad")
        self.assertEqual(signal.tf, "5")
        self.assertEqual(signal.consensus, 8)
        self.assertEqual(signal.direction, "BUY")
        self.assertEqual(signal.mtf, "1,1,1,1,1,-1")
    
    def test_v3_signal_data_get_expected_route(self):
        """Test V3SignalData get_expected_route method."""
        from testing.test_data_generators import V3SignalData
        
        signal_screener = V3SignalData(
            signal_type="Screener",
            tf="5",
            consensus=8,
            direction="BUY",
            mtf="1,1,1,1,1,-1"
        )
        self.assertEqual(signal_screener.get_expected_route(), "LOGIC3")
        
        signal_5m = V3SignalData(
            signal_type="Institutional_Launchpad",
            tf="5",
            consensus=8,
            direction="BUY",
            mtf="1,1,1,1,1,-1"
        )
        self.assertEqual(signal_5m.get_expected_route(), "LOGIC1")
        
        signal_15m = V3SignalData(
            signal_type="Institutional_Launchpad",
            tf="15",
            consensus=8,
            direction="BUY",
            mtf="1,1,1,1,1,-1"
        )
        self.assertEqual(signal_15m.get_expected_route(), "LOGIC2")
        
        signal_60m = V3SignalData(
            signal_type="Institutional_Launchpad",
            tf="60",
            consensus=8,
            direction="BUY",
            mtf="1,1,1,1,1,-1"
        )
        self.assertEqual(signal_60m.get_expected_route(), "LOGIC3")
    
    def test_v3_signal_data_get_mtf_pillars(self):
        """Test V3SignalData get_mtf_pillars method."""
        from testing.test_data_generators import V3SignalData
        
        signal = V3SignalData(
            signal_type="Institutional_Launchpad",
            tf="5",
            consensus=8,
            direction="BUY",
            mtf="1,1,1,1,1,-1"
        )
        
        pillars = signal.get_mtf_pillars()
        self.assertEqual(pillars["15m"], 1)
        self.assertEqual(pillars["1h"], 1)
        self.assertEqual(pillars["4h"], 1)
        self.assertEqual(pillars["1d"], -1)
    
    def test_v3_signal_data_to_dict(self):
        """Test V3SignalData to_dict method."""
        from testing.test_data_generators import V3SignalData
        
        signal = V3SignalData(
            signal_type="Liquidity_Trap",
            tf="15",
            consensus=6,
            direction="SELL",
            mtf="-1,-1,-1,-1,-1,1"
        )
        
        signal_dict = signal.to_dict()
        self.assertEqual(signal_dict["signal_type"], "Liquidity_Trap")
        self.assertEqual(signal_dict["tf"], "15")
        self.assertEqual(signal_dict["consensus"], 6)
        self.assertEqual(signal_dict["direction"], "SELL")


class TestV6AlertData(unittest.TestCase):
    """Test V6AlertData dataclass."""
    
    def test_v6_alert_data_creation(self):
        """Test V6AlertData creation."""
        from testing.test_data_generators import V6AlertData
        
        alert = V6AlertData(
            timeframe="1m",
            direction="BUY",
            adx=22.0,
            confidence_score=85,
            spread_pips=1.5
        )
        
        self.assertEqual(alert.timeframe, "1m")
        self.assertEqual(alert.direction, "BUY")
        self.assertEqual(alert.adx, 22.0)
        self.assertEqual(alert.confidence_score, 85)
        self.assertEqual(alert.spread_pips, 1.5)
    
    def test_v6_alert_data_get_expected_routing(self):
        """Test V6AlertData get_expected_routing method."""
        from testing.test_data_generators import V6AlertData
        
        alert_1m = V6AlertData(
            timeframe="1m", direction="BUY", adx=22.0,
            confidence_score=85, spread_pips=1.5
        )
        self.assertEqual(alert_1m.get_expected_routing(), "ORDER_B_ONLY")
        
        alert_5m = V6AlertData(
            timeframe="5m", direction="BUY", adx=28.0,
            confidence_score=75, spread_pips=1.5
        )
        self.assertEqual(alert_5m.get_expected_routing(), "DUAL_ORDERS")
        
        alert_15m = V6AlertData(
            timeframe="15m", direction="BUY", adx=24.0,
            confidence_score=70, spread_pips=1.5
        )
        self.assertEqual(alert_15m.get_expected_routing(), "ORDER_A_ONLY")
        
        alert_1h = V6AlertData(
            timeframe="1h", direction="BUY", adx=26.0,
            confidence_score=65, spread_pips=1.5
        )
        self.assertEqual(alert_1h.get_expected_routing(), "ORDER_A_ONLY")
    
    def test_v6_alert_data_should_allow_entry(self):
        """Test V6AlertData should_allow_entry method."""
        from testing.test_data_generators import V6AlertData
        
        alert_valid_1m = V6AlertData(
            timeframe="1m", direction="BUY", adx=22.0,
            confidence_score=85, spread_pips=1.5
        )
        self.assertTrue(alert_valid_1m.should_allow_entry())
        
        alert_low_adx = V6AlertData(
            timeframe="1m", direction="BUY", adx=18.0,
            confidence_score=85, spread_pips=1.5
        )
        self.assertFalse(alert_low_adx.should_allow_entry())
        
        alert_low_confidence = V6AlertData(
            timeframe="1m", direction="BUY", adx=22.0,
            confidence_score=75, spread_pips=1.5
        )
        self.assertFalse(alert_low_confidence.should_allow_entry())
        
        alert_high_spread = V6AlertData(
            timeframe="1m", direction="BUY", adx=22.0,
            confidence_score=85, spread_pips=2.5
        )
        self.assertFalse(alert_high_spread.should_allow_entry())


class TestV3SignalGenerator(unittest.TestCase):
    """Test V3SignalGenerator class."""
    
    def test_generate_signal(self):
        """Test generate_signal method."""
        from testing.test_data_generators import V3SignalGenerator
        
        signal = V3SignalGenerator.generate_signal(
            signal_type="Institutional_Launchpad",
            timeframe="5",
            direction="BUY",
            consensus=8
        )
        
        self.assertEqual(signal.signal_type, "Institutional_Launchpad")
        self.assertEqual(signal.tf, "5")
        self.assertEqual(signal.direction, "BUY")
        self.assertEqual(signal.consensus, 8)
    
    def test_generate_all_signal_types(self):
        """Test generate_all_signal_types method."""
        from testing.test_data_generators import V3SignalGenerator
        
        signals = V3SignalGenerator.generate_all_signal_types()
        self.assertEqual(len(signals), 12)
    
    def test_generate_routing_test_data(self):
        """Test generate_routing_test_data method."""
        from testing.test_data_generators import V3SignalGenerator
        
        test_data = V3SignalGenerator.generate_routing_test_data()
        self.assertGreater(len(test_data), 0)
        
        for signal, expected_route in test_data:
            self.assertIn(expected_route, ["LOGIC1", "LOGIC2", "LOGIC3"])
    
    def test_generate_mtf_test_data(self):
        """Test generate_mtf_test_data method."""
        from testing.test_data_generators import V3SignalGenerator
        
        test_data = V3SignalGenerator.generate_mtf_test_data()
        self.assertGreater(len(test_data), 0)
        
        for mtf_string, expected_pillars in test_data:
            self.assertIn("15m", expected_pillars)
            self.assertIn("1h", expected_pillars)
            self.assertIn("4h", expected_pillars)
            self.assertIn("1d", expected_pillars)
    
    def test_generate_consensus_test_data(self):
        """Test generate_consensus_test_data method."""
        from testing.test_data_generators import V3SignalGenerator
        
        test_data = V3SignalGenerator.generate_consensus_test_data()
        self.assertEqual(len(test_data), 10)
        
        for consensus, multiplier in test_data:
            self.assertGreaterEqual(consensus, 0)
            self.assertLessEqual(consensus, 9)
            self.assertGreaterEqual(multiplier, 0.2)
            self.assertLessEqual(multiplier, 1.0)
    
    def test_generate_trend_bypass_test_data(self):
        """Test generate_trend_bypass_test_data method."""
        from testing.test_data_generators import V3SignalGenerator
        
        test_data = V3SignalGenerator.generate_trend_bypass_test_data()
        self.assertGreater(len(test_data), 0)


class TestV6AlertGenerator(unittest.TestCase):
    """Test V6AlertGenerator class."""
    
    def test_generate_alert(self):
        """Test generate_alert method."""
        from testing.test_data_generators import V6AlertGenerator
        
        alert = V6AlertGenerator.generate_alert(
            timeframe="5m",
            direction="BUY",
            adx=28.0,
            confidence=75
        )
        
        self.assertEqual(alert.timeframe, "5m")
        self.assertEqual(alert.direction, "BUY")
        self.assertEqual(alert.adx, 28.0)
        self.assertEqual(alert.confidence_score, 75)
    
    def test_generate_1m_test_data(self):
        """Test generate_1m_test_data method."""
        from testing.test_data_generators import V6AlertGenerator
        
        test_data = V6AlertGenerator.generate_1m_test_data()
        self.assertGreater(len(test_data), 0)
        
        for alert, order_a_expected, order_b_expected in test_data:
            self.assertEqual(alert.timeframe, "1m")
    
    def test_generate_5m_test_data(self):
        """Test generate_5m_test_data method."""
        from testing.test_data_generators import V6AlertGenerator
        
        test_data = V6AlertGenerator.generate_5m_test_data()
        self.assertGreater(len(test_data), 0)
        
        for alert, order_a_expected, order_b_expected in test_data:
            self.assertEqual(alert.timeframe, "5m")
    
    def test_generate_15m_test_data(self):
        """Test generate_15m_test_data method."""
        from testing.test_data_generators import V6AlertGenerator
        
        test_data = V6AlertGenerator.generate_15m_test_data()
        self.assertGreater(len(test_data), 0)
        
        for alert, order_a_expected, order_b_expected in test_data:
            self.assertEqual(alert.timeframe, "15m")
    
    def test_generate_1h_test_data(self):
        """Test generate_1h_test_data method."""
        from testing.test_data_generators import V6AlertGenerator
        
        test_data = V6AlertGenerator.generate_1h_test_data()
        self.assertGreater(len(test_data), 0)
        
        for alert, order_a_expected, order_b_expected in test_data:
            self.assertEqual(alert.timeframe, "1h")
    
    def test_generate_all_timeframes(self):
        """Test generate_all_timeframes method."""
        from testing.test_data_generators import V6AlertGenerator
        
        alerts = V6AlertGenerator.generate_all_timeframes()
        self.assertEqual(len(alerts), 4)
        
        timeframes = [a.timeframe for a in alerts]
        self.assertIn("1m", timeframes)
        self.assertIn("5m", timeframes)
        self.assertIn("15m", timeframes)
        self.assertIn("1h", timeframes)


class TestDualOrderGenerator(unittest.TestCase):
    """Test DualOrderGenerator class."""
    
    def test_generate_v3_dual_order(self):
        """Test generate_v3_dual_order method."""
        from testing.test_data_generators import DualOrderGenerator
        
        order = DualOrderGenerator.generate_v3_dual_order(
            direction="BUY",
            total_lot=0.10
        )
        
        self.assertEqual(order.direction, "BUY")
        self.assertEqual(order.total_lot, 0.10)
        self.assertEqual(order.order_a_lot, 0.05)
        self.assertEqual(order.order_b_lot, 0.05)
    
    def test_generate_position_sizing_test_data(self):
        """Test generate_position_sizing_test_data method."""
        from testing.test_data_generators import DualOrderGenerator
        
        test_data = DualOrderGenerator.generate_position_sizing_test_data()
        self.assertGreater(len(test_data), 0)
        
        for base_lot, consensus, logic_route, expected_lot in test_data:
            self.assertIn(logic_route, ["LOGIC1", "LOGIC2", "LOGIC3"])


class TestTrendPulseGenerator(unittest.TestCase):
    """Test TrendPulseGenerator class."""
    
    def test_generate_pulse(self):
        """Test generate_pulse method."""
        from testing.test_data_generators import TrendPulseGenerator
        
        pulse = TrendPulseGenerator.generate_pulse(
            bull_count=5,
            bear_count=2
        )
        
        self.assertEqual(pulse.bull_count, 5)
        self.assertEqual(pulse.bear_count, 2)
        self.assertEqual(pulse.market_state, "TRENDING_BULLISH")
    
    def test_generate_alignment_test_data(self):
        """Test generate_alignment_test_data method."""
        from testing.test_data_generators import TrendPulseGenerator
        
        test_data = TrendPulseGenerator.generate_alignment_test_data()
        self.assertGreater(len(test_data), 0)
        
        for pulse, direction, expected_aligned in test_data:
            self.assertIn(direction, ["BUY", "SELL"])


class TestManualTestGuides(unittest.TestCase):
    """Test manual test guides module."""
    
    def test_checklist_status_enum(self):
        """Test ChecklistStatus enum."""
        from testing.manual_test_guides import ChecklistStatus
        
        self.assertEqual(ChecklistStatus.PENDING.value, "pending")
        self.assertEqual(ChecklistStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(ChecklistStatus.PASSED.value, "passed")
        self.assertEqual(ChecklistStatus.FAILED.value, "failed")
        self.assertEqual(ChecklistStatus.SKIPPED.value, "skipped")
    
    def test_checklist_item_creation(self):
        """Test ChecklistItem creation."""
        from testing.manual_test_guides import ChecklistItem, ChecklistStatus, TestPriority
        
        item = ChecklistItem(
            id="test_001",
            description="Test description",
            category="v3_signal",
            priority=TestPriority.CRITICAL
        )
        
        self.assertEqual(item.id, "test_001")
        self.assertEqual(item.description, "Test description")
        self.assertEqual(item.status, ChecklistStatus.PENDING)
    
    def test_checklist_item_mark_passed(self):
        """Test ChecklistItem mark_passed method."""
        from testing.manual_test_guides import ChecklistItem, ChecklistStatus, TestPriority
        
        item = ChecklistItem(
            id="test_002",
            description="Test item",
            category="v3_routing",
            priority=TestPriority.HIGH
        )
        
        item.mark_passed("tester", "All good")
        
        self.assertEqual(item.status, ChecklistStatus.PASSED)
        self.assertEqual(item.verified_by, "tester")
        self.assertEqual(item.notes, "All good")
        self.assertIsNotNone(item.verified_at)
    
    def test_checklist_item_mark_failed(self):
        """Test ChecklistItem mark_failed method."""
        from testing.manual_test_guides import ChecklistItem, ChecklistStatus, TestPriority
        
        item = ChecklistItem(
            id="test_003",
            description="Test item",
            category="v3_dual_order",
            priority=TestPriority.CRITICAL
        )
        
        item.mark_failed("tester", "Found issue")
        
        self.assertEqual(item.status, ChecklistStatus.FAILED)
        self.assertEqual(item.verified_by, "tester")
        self.assertEqual(item.notes, "Found issue")


class TestManualTestChecklist(unittest.TestCase):
    """Test ManualTestChecklist class."""
    
    def test_checklist_creation(self):
        """Test ManualTestChecklist creation."""
        from testing.manual_test_guides import ManualTestChecklist
        
        checklist = ManualTestChecklist(
            name="Test Checklist",
            description="Test description",
            category="v3_signal"
        )
        
        self.assertEqual(checklist.name, "Test Checklist")
        self.assertEqual(checklist.total_items, 0)
    
    def test_checklist_add_item(self):
        """Test ManualTestChecklist add_item method."""
        from testing.manual_test_guides import ManualTestChecklist, ChecklistItem, TestPriority
        
        checklist = ManualTestChecklist(
            name="Test Checklist",
            description="Test description",
            category="v3_signal"
        )
        
        item = ChecklistItem(
            id="item_001",
            description="Test item",
            category="v3_signal",
            priority=TestPriority.CRITICAL
        )
        
        checklist.add_item(item)
        self.assertEqual(checklist.total_items, 1)
    
    def test_checklist_properties(self):
        """Test ManualTestChecklist properties."""
        from testing.manual_test_guides import ManualTestChecklist, ChecklistItem, ChecklistStatus, TestPriority
        
        checklist = ManualTestChecklist(
            name="Test Checklist",
            description="Test description",
            category="v3_signal"
        )
        
        item1 = ChecklistItem(
            id="item_001", description="Item 1",
            category="v3_signal", priority=TestPriority.CRITICAL
        )
        item1.status = ChecklistStatus.PASSED
        
        item2 = ChecklistItem(
            id="item_002", description="Item 2",
            category="v3_signal", priority=TestPriority.HIGH
        )
        item2.status = ChecklistStatus.FAILED
        
        item3 = ChecklistItem(
            id="item_003", description="Item 3",
            category="v3_signal", priority=TestPriority.MEDIUM
        )
        
        checklist.add_item(item1)
        checklist.add_item(item2)
        checklist.add_item(item3)
        
        self.assertEqual(checklist.total_items, 3)
        self.assertEqual(checklist.passed_items, 1)
        self.assertEqual(checklist.failed_items, 1)
        self.assertEqual(checklist.pending_items, 1)
    
    def test_checklist_to_markdown(self):
        """Test ManualTestChecklist to_markdown method."""
        from testing.manual_test_guides import ManualTestChecklist, ChecklistItem, TestPriority
        
        checklist = ManualTestChecklist(
            name="Test Checklist",
            description="Test description",
            category="v3_signal"
        )
        
        item = ChecklistItem(
            id="item_001",
            description="Test item",
            category="v3_signal",
            priority=TestPriority.CRITICAL
        )
        checklist.add_item(item)
        
        markdown = checklist.to_markdown()
        self.assertIn("# Test Checklist", markdown)
        self.assertIn("Test description", markdown)


class TestV3ManualTestGuide(unittest.TestCase):
    """Test V3ManualTestGuide class."""
    
    def test_create_signal_processing_checklist(self):
        """Test create_signal_processing_checklist method."""
        from testing.manual_test_guides import V3ManualTestGuide
        
        checklist = V3ManualTestGuide.create_signal_processing_checklist()
        self.assertEqual(checklist.category, "v3_signal_processing")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_routing_matrix_checklist(self):
        """Test create_routing_matrix_checklist method."""
        from testing.manual_test_guides import V3ManualTestGuide
        
        checklist = V3ManualTestGuide.create_routing_matrix_checklist()
        self.assertEqual(checklist.category, "v3_routing_matrix")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_dual_order_checklist(self):
        """Test create_dual_order_checklist method."""
        from testing.manual_test_guides import V3ManualTestGuide
        
        checklist = V3ManualTestGuide.create_dual_order_checklist()
        self.assertEqual(checklist.category, "v3_dual_order")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_all_checklists(self):
        """Test create_all_checklists method."""
        from testing.manual_test_guides import V3ManualTestGuide
        
        checklists = V3ManualTestGuide.create_all_checklists()
        self.assertEqual(len(checklists), 6)


class TestV6ManualTestGuide(unittest.TestCase):
    """Test V6ManualTestGuide class."""
    
    def test_create_1m_checklist(self):
        """Test create_1m_checklist method."""
        from testing.manual_test_guides import V6ManualTestGuide
        
        checklist = V6ManualTestGuide.create_1m_checklist()
        self.assertEqual(checklist.category, "v6_1m")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_5m_checklist(self):
        """Test create_5m_checklist method."""
        from testing.manual_test_guides import V6ManualTestGuide
        
        checklist = V6ManualTestGuide.create_5m_checklist()
        self.assertEqual(checklist.category, "v6_5m")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_15m_checklist(self):
        """Test create_15m_checklist method."""
        from testing.manual_test_guides import V6ManualTestGuide
        
        checklist = V6ManualTestGuide.create_15m_checklist()
        self.assertEqual(checklist.category, "v6_15m")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_1h_checklist(self):
        """Test create_1h_checklist method."""
        from testing.manual_test_guides import V6ManualTestGuide
        
        checklist = V6ManualTestGuide.create_1h_checklist()
        self.assertEqual(checklist.category, "v6_1h")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_trend_pulse_checklist(self):
        """Test create_trend_pulse_checklist method."""
        from testing.manual_test_guides import V6ManualTestGuide
        
        checklist = V6ManualTestGuide.create_trend_pulse_checklist()
        self.assertEqual(checklist.category, "v6_trend_pulse")
        self.assertGreater(checklist.total_items, 0)
    
    def test_create_all_checklists(self):
        """Test create_all_checklists method."""
        from testing.manual_test_guides import V6ManualTestGuide
        
        checklists = V6ManualTestGuide.create_all_checklists()
        self.assertEqual(len(checklists), 5)


class TestQualityGate(unittest.TestCase):
    """Test quality gate module."""
    
    def test_gate_status_enum(self):
        """Test GateStatus enum."""
        from testing.quality_gate import GateStatus
        
        self.assertEqual(GateStatus.PASSED.value, "passed")
        self.assertEqual(GateStatus.FAILED.value, "failed")
        self.assertEqual(GateStatus.WARNING.value, "warning")
        self.assertEqual(GateStatus.SKIPPED.value, "skipped")
    
    def test_gate_category_enum(self):
        """Test GateCategory enum."""
        from testing.quality_gate import GateCategory
        
        self.assertEqual(GateCategory.TEST_COVERAGE.value, "test_coverage")
        self.assertEqual(GateCategory.CRITICAL_TESTS.value, "critical_tests")
        self.assertEqual(GateCategory.CHECKLIST_COMPLETION.value, "checklist_completion")
        self.assertEqual(GateCategory.SHADOW_MODE.value, "shadow_mode")
        self.assertEqual(GateCategory.DOCUMENTATION.value, "documentation")
    
    def test_gate_result_creation(self):
        """Test GateResult creation."""
        from testing.quality_gate import GateResult, GateStatus, GateCategory
        
        result = GateResult(
            gate_name="Test Coverage",
            category=GateCategory.TEST_COVERAGE,
            status=GateStatus.PASSED,
            message="Coverage 95% meets minimum 80%"
        )
        
        self.assertEqual(result.gate_name, "Test Coverage")
        self.assertTrue(result.passed)
    
    def test_gate_result_to_dict(self):
        """Test GateResult to_dict method."""
        from testing.quality_gate import GateResult, GateStatus, GateCategory
        
        result = GateResult(
            gate_name="Critical Tests",
            category=GateCategory.CRITICAL_TESTS,
            status=GateStatus.FAILED,
            message="5 critical tests failed"
        )
        
        result_dict = result.to_dict()
        self.assertEqual(result_dict["gate_name"], "Critical Tests")
        self.assertEqual(result_dict["status"], "failed")


class TestQualityGateReport(unittest.TestCase):
    """Test QualityGateReport class."""
    
    def test_report_creation(self):
        """Test QualityGateReport creation."""
        from testing.quality_gate import QualityGateReport
        
        report = QualityGateReport(report_name="Pre-Release")
        self.assertEqual(report.report_name, "Pre-Release")
        self.assertEqual(report.total_gates, 0)
    
    def test_report_add_gate(self):
        """Test QualityGateReport add_gate method."""
        from testing.quality_gate import QualityGateReport, GateResult, GateStatus, GateCategory
        
        report = QualityGateReport(report_name="Test Report")
        
        gate = GateResult(
            gate_name="Test Gate",
            category=GateCategory.TEST_COVERAGE,
            status=GateStatus.PASSED,
            message="Passed"
        )
        
        report.add_gate(gate)
        self.assertEqual(report.total_gates, 1)
        self.assertEqual(report.passed_gates, 1)
    
    def test_report_release_ready(self):
        """Test QualityGateReport release_ready property."""
        from testing.quality_gate import QualityGateReport, GateResult, GateStatus, GateCategory
        
        report = QualityGateReport(report_name="Test Report")
        
        gate_passed = GateResult(
            gate_name="Gate 1",
            category=GateCategory.TEST_COVERAGE,
            status=GateStatus.PASSED,
            message="Passed"
        )
        
        report.add_gate(gate_passed)
        self.assertTrue(report.release_ready)
        
        gate_failed = GateResult(
            gate_name="Gate 2",
            category=GateCategory.CRITICAL_TESTS,
            status=GateStatus.FAILED,
            message="Failed"
        )
        
        report.add_gate(gate_failed)
        self.assertFalse(report.release_ready)
    
    def test_report_to_markdown(self):
        """Test QualityGateReport to_markdown method."""
        from testing.quality_gate import QualityGateReport, GateResult, GateStatus, GateCategory
        
        report = QualityGateReport(report_name="Test Report")
        
        gate = GateResult(
            gate_name="Test Gate",
            category=GateCategory.TEST_COVERAGE,
            status=GateStatus.PASSED,
            message="All tests passed"
        )
        
        report.add_gate(gate)
        
        markdown = report.to_markdown()
        self.assertIn("Quality Gate Report", markdown)
        self.assertIn("Test Gate", markdown)


class TestQualityGateEnforcer(unittest.TestCase):
    """Test QualityGateEnforcer class."""
    
    def test_enforcer_creation(self):
        """Test QualityGateEnforcer creation."""
        from testing.quality_gate import QualityGateEnforcer
        
        enforcer = QualityGateEnforcer()
        self.assertIsNotNone(enforcer)
    
    def test_enforcer_constants(self):
        """Test QualityGateEnforcer constants."""
        from testing.quality_gate import QualityGateEnforcer
        
        self.assertEqual(QualityGateEnforcer.REQUIRED_TEST_COVERAGE, 80.0)
        self.assertEqual(QualityGateEnforcer.REQUIRED_CRITICAL_PASS_RATE, 100.0)
        self.assertEqual(QualityGateEnforcer.SHADOW_MODE_DURATION_HOURS, 72)


class TestPreReleaseChecker(unittest.TestCase):
    """Test PreReleaseChecker class."""
    
    def test_checker_creation(self):
        """Test PreReleaseChecker creation."""
        from testing.quality_gate import PreReleaseChecker
        
        checker = PreReleaseChecker()
        self.assertIsNotNone(checker)


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios module."""
    
    def test_scenario_status_enum(self):
        """Test ScenarioStatus enum."""
        from testing.integration_scenarios import ScenarioStatus
        
        self.assertEqual(ScenarioStatus.PENDING.value, "pending")
        self.assertEqual(ScenarioStatus.RUNNING.value, "running")
        self.assertEqual(ScenarioStatus.PASSED.value, "passed")
        self.assertEqual(ScenarioStatus.FAILED.value, "failed")
    
    def test_scenario_category_enum(self):
        """Test ScenarioCategory enum."""
        from testing.integration_scenarios import ScenarioCategory
        
        self.assertEqual(ScenarioCategory.V3_V6_INTEGRATION.value, "v3_v6_integration")
        self.assertEqual(ScenarioCategory.SERVICE_API.value, "service_api")
        self.assertEqual(ScenarioCategory.DATABASE.value, "database")
        self.assertEqual(ScenarioCategory.END_TO_END.value, "end_to_end")
        self.assertEqual(ScenarioCategory.SHADOW_MODE.value, "shadow_mode")
    
    def test_scenario_step_creation(self):
        """Test ScenarioStep creation."""
        from testing.integration_scenarios import ScenarioStep, ScenarioStatus
        
        step = ScenarioStep(
            step_id="step_001",
            description="Test step",
            action="Do something",
            expected_result="Something happens"
        )
        
        self.assertEqual(step.step_id, "step_001")
        self.assertEqual(step.status, ScenarioStatus.PENDING)
    
    def test_scenario_step_mark_passed(self):
        """Test ScenarioStep mark_passed method."""
        from testing.integration_scenarios import ScenarioStep, ScenarioStatus
        
        step = ScenarioStep(
            step_id="step_001",
            description="Test step",
            action="Do something",
            expected_result="Something happens"
        )
        
        step.mark_passed("Result achieved", 100.0)
        
        self.assertEqual(step.status, ScenarioStatus.PASSED)
        self.assertEqual(step.actual_result, "Result achieved")
        self.assertEqual(step.duration_ms, 100.0)


class TestIntegrationScenario(unittest.TestCase):
    """Test IntegrationScenario class."""
    
    def test_scenario_creation(self):
        """Test IntegrationScenario creation."""
        from testing.integration_scenarios import IntegrationScenario, ScenarioCategory
        
        scenario = IntegrationScenario(
            scenario_id="INT_001",
            name="Test Scenario",
            description="Test description",
            category=ScenarioCategory.V3_V6_INTEGRATION
        )
        
        self.assertEqual(scenario.scenario_id, "INT_001")
        self.assertEqual(scenario.name, "Test Scenario")
        self.assertEqual(scenario.total_steps, 0)
    
    def test_scenario_add_step(self):
        """Test IntegrationScenario add_step method."""
        from testing.integration_scenarios import IntegrationScenario, ScenarioCategory, ScenarioStep
        
        scenario = IntegrationScenario(
            scenario_id="INT_001",
            name="Test Scenario",
            description="Test description",
            category=ScenarioCategory.SERVICE_API
        )
        
        step = ScenarioStep(
            step_id="step_001",
            description="Test step",
            action="Do something",
            expected_result="Something happens"
        )
        
        scenario.add_step(step)
        self.assertEqual(scenario.total_steps, 1)
    
    def test_scenario_to_markdown(self):
        """Test IntegrationScenario to_markdown method."""
        from testing.integration_scenarios import IntegrationScenario, ScenarioCategory, ScenarioStep
        
        scenario = IntegrationScenario(
            scenario_id="INT_001",
            name="Test Scenario",
            description="Test description",
            category=ScenarioCategory.DATABASE,
            preconditions=["Precondition 1"],
            postconditions=["Postcondition 1"]
        )
        
        step = ScenarioStep(
            step_id="step_001",
            description="Test step",
            action="Do something",
            expected_result="Something happens"
        )
        scenario.add_step(step)
        
        markdown = scenario.to_markdown()
        self.assertIn("Test Scenario", markdown)
        self.assertIn("Precondition 1", markdown)


class TestScenarioRegistry(unittest.TestCase):
    """Test ScenarioRegistry class."""
    
    def test_get_all_scenarios(self):
        """Test get_all_scenarios method."""
        from testing.integration_scenarios import ScenarioRegistry
        
        scenarios = ScenarioRegistry.get_all_scenarios()
        self.assertIn("v3_v6_integration", scenarios)
        self.assertIn("service_api", scenarios)
        self.assertIn("database", scenarios)
        self.assertIn("end_to_end", scenarios)
        self.assertIn("shadow_mode", scenarios)
    
    def test_get_scenario_by_id(self):
        """Test get_scenario_by_id method."""
        from testing.integration_scenarios import ScenarioRegistry
        
        scenario = ScenarioRegistry.get_scenario_by_id("INT_001")
        self.assertIsNotNone(scenario)
        self.assertEqual(scenario.scenario_id, "INT_001")
    
    def test_get_total_scenario_count(self):
        """Test get_total_scenario_count method."""
        from testing.integration_scenarios import ScenarioRegistry
        
        count = ScenarioRegistry.get_total_scenario_count()
        self.assertGreater(count, 0)
    
    def test_get_total_step_count(self):
        """Test get_total_step_count method."""
        from testing.integration_scenarios import ScenarioRegistry
        
        count = ScenarioRegistry.get_total_step_count()
        self.assertGreater(count, 0)


class TestV3V6IntegrationScenarios(unittest.TestCase):
    """Test V3V6IntegrationScenarios class."""
    
    def test_create_simultaneous_execution_scenario(self):
        """Test create_simultaneous_execution_scenario method."""
        from testing.integration_scenarios import V3V6IntegrationScenarios
        
        scenario = V3V6IntegrationScenarios.create_simultaneous_execution_scenario()
        self.assertEqual(scenario.scenario_id, "INT_001")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_plugin_isolation_scenario(self):
        """Test create_plugin_isolation_scenario method."""
        from testing.integration_scenarios import V3V6IntegrationScenarios
        
        scenario = V3V6IntegrationScenarios.create_plugin_isolation_scenario()
        self.assertEqual(scenario.scenario_id, "INT_002")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_all_scenarios(self):
        """Test create_all_scenarios method."""
        from testing.integration_scenarios import V3V6IntegrationScenarios
        
        scenarios = V3V6IntegrationScenarios.create_all_scenarios()
        self.assertEqual(len(scenarios), 2)


class TestServiceAPIIntegrationScenarios(unittest.TestCase):
    """Test ServiceAPIIntegrationScenarios class."""
    
    def test_create_order_execution_scenario(self):
        """Test create_order_execution_scenario method."""
        from testing.integration_scenarios import ServiceAPIIntegrationScenarios
        
        scenario = ServiceAPIIntegrationScenarios.create_order_execution_scenario()
        self.assertEqual(scenario.scenario_id, "API_001")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_risk_management_scenario(self):
        """Test create_risk_management_scenario method."""
        from testing.integration_scenarios import ServiceAPIIntegrationScenarios
        
        scenario = ServiceAPIIntegrationScenarios.create_risk_management_scenario()
        self.assertEqual(scenario.scenario_id, "API_002")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_trend_monitor_scenario(self):
        """Test create_trend_monitor_scenario method."""
        from testing.integration_scenarios import ServiceAPIIntegrationScenarios
        
        scenario = ServiceAPIIntegrationScenarios.create_trend_monitor_scenario()
        self.assertEqual(scenario.scenario_id, "API_003")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_all_scenarios(self):
        """Test create_all_scenarios method."""
        from testing.integration_scenarios import ServiceAPIIntegrationScenarios
        
        scenarios = ServiceAPIIntegrationScenarios.create_all_scenarios()
        self.assertEqual(len(scenarios), 3)


class TestShadowModeScenarios(unittest.TestCase):
    """Test ShadowModeScenarios class."""
    
    def test_create_v3_shadow_scenario(self):
        """Test create_v3_shadow_scenario method."""
        from testing.integration_scenarios import ShadowModeScenarios
        
        scenario = ShadowModeScenarios.create_v3_shadow_scenario()
        self.assertEqual(scenario.scenario_id, "SHADOW_001")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_v6_shadow_scenario(self):
        """Test create_v6_shadow_scenario method."""
        from testing.integration_scenarios import ShadowModeScenarios
        
        scenario = ShadowModeScenarios.create_v6_shadow_scenario()
        self.assertEqual(scenario.scenario_id, "SHADOW_002")
        self.assertGreater(scenario.total_steps, 0)
    
    def test_create_all_scenarios(self):
        """Test create_all_scenarios method."""
        from testing.integration_scenarios import ShadowModeScenarios
        
        scenarios = ShadowModeScenarios.create_all_scenarios()
        self.assertEqual(len(scenarios), 2)


class TestGenerateAllChecklists(unittest.TestCase):
    """Test generate_all_checklists function."""
    
    def test_generate_all_checklists(self):
        """Test generate_all_checklists function."""
        from testing.manual_test_guides import generate_all_checklists
        
        checklists = generate_all_checklists()
        self.assertIn("v3", checklists)
        self.assertIn("v6", checklists)
        self.assertIn("integration", checklists)
        self.assertIn("shadow_mode", checklists)
        self.assertIn("production", checklists)


class TestProductionReadinessChecklist(unittest.TestCase):
    """Test ProductionReadinessChecklist class."""
    
    def test_create_checklist(self):
        """Test create_checklist method."""
        from testing.manual_test_guides import ProductionReadinessChecklist
        
        checklist = ProductionReadinessChecklist.create_checklist()
        self.assertEqual(checklist.category, "production_readiness")
        self.assertGreater(checklist.total_items, 0)


class TestDocument12Integration(unittest.TestCase):
    """Test Document 12 integration scenarios."""
    
    def test_v3_signal_processing_coverage(self):
        """Test V3 signal processing test coverage."""
        from testing.test_data_generators import V3SignalGenerator
        
        signals = V3SignalGenerator.generate_all_signal_types()
        self.assertEqual(len(signals), 12)
        
        signal_types = [s.signal_type for s in signals]
        self.assertIn("Institutional_Launchpad", signal_types)
        self.assertIn("Liquidity_Trap", signal_types)
        self.assertIn("Screener", signal_types)
        self.assertIn("entry_v3", signal_types)
        self.assertIn("Exit_Bullish", signal_types)
        self.assertIn("Exit_Bearish", signal_types)
    
    def test_v6_timeframe_coverage(self):
        """Test V6 timeframe test coverage."""
        from testing.test_data_generators import V6AlertGenerator
        
        alerts = V6AlertGenerator.generate_all_timeframes()
        self.assertEqual(len(alerts), 4)
        
        timeframes = [a.timeframe for a in alerts]
        self.assertIn("1m", timeframes)
        self.assertIn("5m", timeframes)
        self.assertIn("15m", timeframes)
        self.assertIn("1h", timeframes)
    
    def test_order_routing_coverage(self):
        """Test order routing coverage."""
        from testing.test_runners import V6TestRunner
        
        runner = V6TestRunner()
        
        self.assertEqual(runner.get_order_routing("1m"), "ORDER_B_ONLY")
        self.assertEqual(runner.get_order_routing("5m"), "DUAL_ORDERS")
        self.assertEqual(runner.get_order_routing("15m"), "ORDER_A_ONLY")
        self.assertEqual(runner.get_order_routing("1h"), "ORDER_A_ONLY")
    
    def test_shadow_mode_duration(self):
        """Test shadow mode duration is 72 hours."""
        from testing.test_runners import ShadowModeTestRunner
        from testing.quality_gate import QualityGateEnforcer
        
        self.assertEqual(ShadowModeTestRunner.SHADOW_DURATION_HOURS, 72)
        self.assertEqual(QualityGateEnforcer.SHADOW_MODE_DURATION_HOURS, 72)


class TestDocument12Summary(unittest.TestCase):
    """Test Document 12 summary verification."""
    
    def test_testing_package_complete(self):
        """Test testing package is complete."""
        from testing import (
            TestRunner, V3TestRunner, V6TestRunner,
            IntegrationTestRunner, ShadowModeTestRunner,
            MarkerRegistry, TestSuiteRegistry,
            V3SignalGenerator, V6AlertGenerator,
            DualOrderGenerator, TrendPulseGenerator,
            V3ManualTestGuide, V6ManualTestGuide,
            IntegrationManualTestGuide, ShadowModeManualTestGuide,
            QualityGateEnforcer, PreReleaseChecker,
            ScenarioRegistry
        )
        
        self.assertIsNotNone(TestRunner)
        self.assertIsNotNone(V3TestRunner)
        self.assertIsNotNone(V6TestRunner)
        self.assertIsNotNone(IntegrationTestRunner)
        self.assertIsNotNone(ShadowModeTestRunner)
        self.assertIsNotNone(MarkerRegistry)
        self.assertIsNotNone(TestSuiteRegistry)
        self.assertIsNotNone(V3SignalGenerator)
        self.assertIsNotNone(V6AlertGenerator)
        self.assertIsNotNone(DualOrderGenerator)
        self.assertIsNotNone(TrendPulseGenerator)
        self.assertIsNotNone(V3ManualTestGuide)
        self.assertIsNotNone(V6ManualTestGuide)
        self.assertIsNotNone(IntegrationManualTestGuide)
        self.assertIsNotNone(ShadowModeManualTestGuide)
        self.assertIsNotNone(QualityGateEnforcer)
        self.assertIsNotNone(PreReleaseChecker)
        self.assertIsNotNone(ScenarioRegistry)
    
    def test_v3_test_categories_complete(self):
        """Test V3 test categories are complete."""
        from testing.pytest_markers import MarkerRegistry
        
        v3_markers = MarkerRegistry.get_v3_marker_names()
        self.assertIn("v3_signal", v3_markers)
        self.assertIn("v3_routing", v3_markers)
        self.assertIn("v3_dual_order", v3_markers)
        self.assertIn("v3_mtf", v3_markers)
        self.assertIn("v3_position", v3_markers)
        self.assertIn("v3_trend_bypass", v3_markers)
    
    def test_v6_test_categories_complete(self):
        """Test V6 test categories are complete."""
        from testing.pytest_markers import MarkerRegistry
        
        v6_markers = MarkerRegistry.get_v6_marker_names()
        self.assertIn("v6_1m", v6_markers)
        self.assertIn("v6_5m", v6_markers)
        self.assertIn("v6_15m", v6_markers)
        self.assertIn("v6_1h", v6_markers)
        self.assertIn("v6_trend_pulse", v6_markers)
    
    def test_integration_scenarios_complete(self):
        """Test integration scenarios are complete."""
        from testing.integration_scenarios import ScenarioRegistry
        
        scenarios = ScenarioRegistry.get_all_scenarios()
        self.assertIn("v3_v6_integration", scenarios)
        self.assertIn("service_api", scenarios)
        self.assertIn("database", scenarios)
        self.assertIn("end_to_end", scenarios)
        self.assertIn("shadow_mode", scenarios)
    
    def test_quality_gates_complete(self):
        """Test quality gates are complete."""
        from testing.quality_gate import GateCategory
        
        self.assertEqual(GateCategory.TEST_COVERAGE.value, "test_coverage")
        self.assertEqual(GateCategory.CRITICAL_TESTS.value, "critical_tests")
        self.assertEqual(GateCategory.CHECKLIST_COMPLETION.value, "checklist_completion")
        self.assertEqual(GateCategory.SHADOW_MODE.value, "shadow_mode")
        self.assertEqual(GateCategory.DOCUMENTATION.value, "documentation")
        self.assertEqual(GateCategory.CODE_QUALITY.value, "code_quality")
    
    def test_manual_checklists_complete(self):
        """Test manual checklists are complete."""
        from testing.manual_test_guides import generate_all_checklists
        
        checklists = generate_all_checklists()
        
        self.assertEqual(len(checklists["v3"]), 6)
        self.assertEqual(len(checklists["v6"]), 5)
        self.assertEqual(len(checklists["integration"]), 2)
        self.assertEqual(len(checklists["shadow_mode"]), 2)
        self.assertEqual(len(checklists["production"]), 1)
    
    def test_test_data_generators_complete(self):
        """Test test data generators are complete."""
        from testing.test_data_generators import (
            V3SignalGenerator, V6AlertGenerator,
            DualOrderGenerator, TrendPulseGenerator,
            ShadowModeDataGenerator, IntegrationTestDataGenerator
        )
        
        v3_signals = V3SignalGenerator.generate_all_signal_types()
        self.assertEqual(len(v3_signals), 12)
        
        v6_alerts = V6AlertGenerator.generate_all_timeframes()
        self.assertEqual(len(v6_alerts), 4)
        
        dual_order = DualOrderGenerator.generate_v3_dual_order()
        self.assertIsNotNone(dual_order)
        
        pulse = TrendPulseGenerator.generate_pulse()
        self.assertIsNotNone(pulse)
        
        shadow_session = ShadowModeDataGenerator.generate_shadow_session()
        self.assertIsNotNone(shadow_session)
        
        integration_data = IntegrationTestDataGenerator.generate_v3_v6_simultaneous_data()
        self.assertIsNotNone(integration_data)
    
    def test_document_12_requirements_met(self):
        """Test all Document 12 requirements are met."""
        from testing import (
            TestRunner, MarkerRegistry, V3SignalGenerator,
            V3ManualTestGuide, QualityGateEnforcer, ScenarioRegistry
        )
        
        self.assertIsNotNone(TestRunner)
        
        markers = MarkerRegistry.get_all_markers()
        self.assertEqual(len(markers), 21)
        
        signals = V3SignalGenerator.generate_all_signal_types()
        self.assertEqual(len(signals), 12)
        
        checklists = V3ManualTestGuide.create_all_checklists()
        self.assertEqual(len(checklists), 6)
        
        self.assertIsNotNone(QualityGateEnforcer)
        
        scenarios = ScenarioRegistry.get_all_scenarios()
        self.assertGreater(len(scenarios), 0)


if __name__ == '__main__':
    unittest.main()
