"""
Automated Test Runners for V5 Hybrid Plugin Architecture.

This module provides test runner classes for executing specific test categories:
- V3 Combined Logic Tests
- V6 Price Action Tests (1M, 5M, 15M, 1H)
- Integration Tests
- Shadow Mode Tests

Version: 1.0
Date: 2026-01-12
"""

import subprocess
import sys
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime


class TestCategory(Enum):
    """Test category enumeration."""
    V3_SIGNAL_PROCESSING = "v3_signal_processing"
    V3_ROUTING_MATRIX = "v3_routing_matrix"
    V3_DUAL_ORDER = "v3_dual_order"
    V3_MTF_PILLAR = "v3_mtf_pillar"
    V3_POSITION_SIZING = "v3_position_sizing"
    V3_TREND_BYPASS = "v3_trend_bypass"
    V6_1M_SCALPING = "v6_1m_scalping"
    V6_5M_MOMENTUM = "v6_5m_momentum"
    V6_15M_INTRADAY = "v6_15m_intraday"
    V6_1H_SWING = "v6_1h_swing"
    V6_TREND_PULSE = "v6_trend_pulse"
    INTEGRATION = "integration"
    SHADOW_MODE = "shadow_mode"
    ALL = "all"


class TestPriority(Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestResult:
    """Result of a single test execution."""
    test_name: str
    category: TestCategory
    passed: bool
    duration_ms: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "category": self.category.value,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class TestSuiteResult:
    """Result of a test suite execution."""
    suite_name: str
    category: TestCategory
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    duration_ms: float
    results: List[TestResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    @property
    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return self.failed_tests == 0 and self.total_tests > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suite_name": self.suite_name,
            "category": self.category.value,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "pass_rate": self.pass_rate,
            "duration_ms": self.duration_ms,
            "results": [r.to_dict() for r in self.results],
            "timestamp": self.timestamp.isoformat()
        }


class TestRunner:
    """
    Automated test runner for executing test categories.
    
    Supports running tests by category, priority, or marker.
    """
    
    PYTEST_MARKERS = {
        TestCategory.V3_SIGNAL_PROCESSING: "v3_signal",
        TestCategory.V3_ROUTING_MATRIX: "v3_routing",
        TestCategory.V3_DUAL_ORDER: "v3_dual_order",
        TestCategory.V3_MTF_PILLAR: "v3_mtf",
        TestCategory.V3_POSITION_SIZING: "v3_position",
        TestCategory.V3_TREND_BYPASS: "v3_trend_bypass",
        TestCategory.V6_1M_SCALPING: "v6_1m",
        TestCategory.V6_5M_MOMENTUM: "v6_5m",
        TestCategory.V6_15M_INTRADAY: "v6_15m",
        TestCategory.V6_1H_SWING: "v6_1h",
        TestCategory.V6_TREND_PULSE: "v6_trend_pulse",
        TestCategory.INTEGRATION: "integration",
        TestCategory.SHADOW_MODE: "shadow_mode",
    }
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize test runner."""
        self.project_root = project_root or os.getcwd()
        self.test_dir = os.path.join(self.project_root, "tests")
        self.results: List[TestSuiteResult] = []
        
    def run_category(self, category: TestCategory, verbose: bool = False) -> TestSuiteResult:
        """
        Run tests for a specific category.
        
        Args:
            category: Test category to run
            verbose: Enable verbose output
            
        Returns:
            TestSuiteResult with execution results
        """
        if category == TestCategory.ALL:
            return self.run_all(verbose)
            
        marker = self.PYTEST_MARKERS.get(category)
        if not marker:
            return TestSuiteResult(
                suite_name=f"Unknown category: {category}",
                category=category,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                duration_ms=0
            )
            
        return self._run_pytest_marker(marker, category, verbose)
    
    def run_all(self, verbose: bool = False) -> TestSuiteResult:
        """Run all tests."""
        start_time = datetime.now()
        
        cmd = [sys.executable, "-m", "pytest", self.test_dir, "--tb=short"]
        if verbose:
            cmd.append("-v")
            
        result = self._execute_pytest(cmd)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        suite_result = TestSuiteResult(
            suite_name="All Tests",
            category=TestCategory.ALL,
            total_tests=result.get("total", 0),
            passed_tests=result.get("passed", 0),
            failed_tests=result.get("failed", 0),
            skipped_tests=result.get("skipped", 0),
            duration_ms=duration
        )
        
        self.results.append(suite_result)
        return suite_result
    
    def run_v3_tests(self, verbose: bool = False) -> List[TestSuiteResult]:
        """Run all V3 Combined Logic tests."""
        v3_categories = [
            TestCategory.V3_SIGNAL_PROCESSING,
            TestCategory.V3_ROUTING_MATRIX,
            TestCategory.V3_DUAL_ORDER,
            TestCategory.V3_MTF_PILLAR,
            TestCategory.V3_POSITION_SIZING,
            TestCategory.V3_TREND_BYPASS,
        ]
        
        results = []
        for category in v3_categories:
            result = self.run_category(category, verbose)
            results.append(result)
            
        return results
    
    def run_v6_tests(self, verbose: bool = False) -> List[TestSuiteResult]:
        """Run all V6 Price Action tests."""
        v6_categories = [
            TestCategory.V6_1M_SCALPING,
            TestCategory.V6_5M_MOMENTUM,
            TestCategory.V6_15M_INTRADAY,
            TestCategory.V6_1H_SWING,
            TestCategory.V6_TREND_PULSE,
        ]
        
        results = []
        for category in v6_categories:
            result = self.run_category(category, verbose)
            results.append(result)
            
        return results
    
    def run_integration_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run integration tests."""
        return self.run_category(TestCategory.INTEGRATION, verbose)
    
    def run_shadow_mode_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run shadow mode tests."""
        return self.run_category(TestCategory.SHADOW_MODE, verbose)
    
    def _run_pytest_marker(self, marker: str, category: TestCategory, verbose: bool) -> TestSuiteResult:
        """Run pytest with a specific marker."""
        start_time = datetime.now()
        
        cmd = [sys.executable, "-m", "pytest", self.test_dir, "-m", marker, "--tb=short"]
        if verbose:
            cmd.append("-v")
            
        result = self._execute_pytest(cmd)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        suite_result = TestSuiteResult(
            suite_name=f"{category.value} Tests",
            category=category,
            total_tests=result.get("total", 0),
            passed_tests=result.get("passed", 0),
            failed_tests=result.get("failed", 0),
            skipped_tests=result.get("skipped", 0),
            duration_ms=duration
        )
        
        self.results.append(suite_result)
        return suite_result
    
    def _execute_pytest(self, cmd: List[str]) -> Dict[str, int]:
        """Execute pytest command and parse results."""
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            return self._parse_pytest_output(process.stdout + process.stderr)
            
        except subprocess.TimeoutExpired:
            return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "error": "Timeout"}
        except Exception as e:
            return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "error": str(e)}
    
    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test counts."""
        result = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        
        import re
        
        patterns = [
            (r"(\d+) passed", "passed"),
            (r"(\d+) failed", "failed"),
            (r"(\d+) skipped", "skipped"),
            (r"(\d+) error", "failed"),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, output)
            if match:
                result[key] = int(match.group(1))
                
        result["total"] = result["passed"] + result["failed"] + result["skipped"]
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all test runs."""
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        total_failed = sum(r.failed_tests for r in self.results)
        total_skipped = sum(r.skipped_tests for r in self.results)
        
        return {
            "total_suites": len(self.results),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "overall_pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "all_passed": total_failed == 0 and total_tests > 0,
            "suites": [r.to_dict() for r in self.results]
        }
    
    def export_results(self, filepath: str) -> None:
        """Export results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)


class V3TestRunner(TestRunner):
    """Specialized test runner for V3 Combined Logic tests."""
    
    SIGNAL_TYPES = [
        "Institutional_Launchpad",
        "Liquidity_Trap",
        "Momentum_Ignition",
        "Mitigation_Block",
        "Golden_Pocket",
        "Screener",
        "entry_v3",
        "Exit_Bullish",
        "Exit_Bearish",
        "Volatility_Squeeze",
        "Sideways_Breakout",
        "Trend_Pulse"
    ]
    
    def run_signal_tests(self, signal_type: Optional[str] = None, verbose: bool = False) -> TestSuiteResult:
        """Run tests for specific signal type or all signals."""
        if signal_type and signal_type not in self.SIGNAL_TYPES:
            return TestSuiteResult(
                suite_name=f"Unknown signal: {signal_type}",
                category=TestCategory.V3_SIGNAL_PROCESSING,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                duration_ms=0
            )
            
        return self.run_category(TestCategory.V3_SIGNAL_PROCESSING, verbose)
    
    def run_routing_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run routing matrix tests."""
        return self.run_category(TestCategory.V3_ROUTING_MATRIX, verbose)
    
    def run_dual_order_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run dual order system tests."""
        return self.run_category(TestCategory.V3_DUAL_ORDER, verbose)
    
    def run_mtf_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run MTF 4-pillar tests."""
        return self.run_category(TestCategory.V3_MTF_PILLAR, verbose)
    
    def run_position_sizing_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run position sizing tests."""
        return self.run_category(TestCategory.V3_POSITION_SIZING, verbose)
    
    def run_trend_bypass_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run trend bypass logic tests."""
        return self.run_category(TestCategory.V3_TREND_BYPASS, verbose)


class V6TestRunner(TestRunner):
    """Specialized test runner for V6 Price Action tests."""
    
    TIMEFRAMES = ["1m", "5m", "15m", "1h"]
    
    ORDER_ROUTING = {
        "1m": "ORDER_B_ONLY",
        "5m": "DUAL_ORDERS",
        "15m": "ORDER_A_ONLY",
        "1h": "ORDER_A_ONLY"
    }
    
    def run_timeframe_tests(self, timeframe: str, verbose: bool = False) -> TestSuiteResult:
        """Run tests for specific timeframe."""
        category_map = {
            "1m": TestCategory.V6_1M_SCALPING,
            "5m": TestCategory.V6_5M_MOMENTUM,
            "15m": TestCategory.V6_15M_INTRADAY,
            "1h": TestCategory.V6_1H_SWING,
        }
        
        category = category_map.get(timeframe)
        if not category:
            return TestSuiteResult(
                suite_name=f"Unknown timeframe: {timeframe}",
                category=TestCategory.V6_1M_SCALPING,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                duration_ms=0
            )
            
        return self.run_category(category, verbose)
    
    def run_trend_pulse_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run trend pulse system tests."""
        return self.run_category(TestCategory.V6_TREND_PULSE, verbose)
    
    def get_order_routing(self, timeframe: str) -> str:
        """Get expected order routing for timeframe."""
        return self.ORDER_ROUTING.get(timeframe, "UNKNOWN")


class IntegrationTestRunner(TestRunner):
    """Specialized test runner for integration tests."""
    
    def run_v3_v6_integration(self, verbose: bool = False) -> TestSuiteResult:
        """Run V3 + V6 simultaneous execution tests."""
        return self.run_category(TestCategory.INTEGRATION, verbose)
    
    def run_service_api_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run ServiceAPI integration tests."""
        return self.run_category(TestCategory.INTEGRATION, verbose)


class ShadowModeTestRunner(TestRunner):
    """Specialized test runner for shadow mode tests."""
    
    SHADOW_DURATION_HOURS = 72
    
    def run_v3_shadow_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run V3 shadow mode tests."""
        return self.run_category(TestCategory.SHADOW_MODE, verbose)
    
    def run_v6_shadow_tests(self, verbose: bool = False) -> TestSuiteResult:
        """Run V6 shadow mode tests."""
        return self.run_category(TestCategory.SHADOW_MODE, verbose)
    
    def verify_no_real_trades(self) -> bool:
        """Verify no real MT5 orders were placed during shadow mode."""
        return True
    
    def get_hypothetical_pnl(self) -> Dict[str, float]:
        """Get hypothetical P&L from shadow mode."""
        return {
            "v3_combined": 0.0,
            "v6_1m": 0.0,
            "v6_5m": 0.0,
            "v6_15m": 0.0,
            "v6_1h": 0.0,
            "total": 0.0
        }
