"""
Pytest Markers Configuration for V5 Hybrid Plugin Architecture.

This module defines pytest markers for categorizing tests:
- V3 Combined Logic markers
- V6 Price Action markers (per timeframe)
- Integration markers
- Shadow Mode markers
- Priority markers

Version: 1.0
Date: 2026-01-12
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MarkerCategory(Enum):
    """Marker category enumeration."""
    V3 = "v3"
    V6 = "v6"
    INTEGRATION = "integration"
    SHADOW_MODE = "shadow_mode"
    PRIORITY = "priority"


@dataclass
class PytestMarker:
    """Pytest marker definition."""
    name: str
    description: str
    category: MarkerCategory
    priority: str = "medium"
    
    def to_ini_format(self) -> str:
        """Convert to pytest.ini format."""
        return f"{self.name}: {self.description}"
    
    def to_decorator(self) -> str:
        """Get decorator string."""
        return f"@pytest.mark.{self.name}"


class MarkerRegistry:
    """
    Registry of all pytest markers for the testing framework.
    
    Provides marker definitions and utilities for test categorization.
    """
    
    V3_MARKERS = [
        PytestMarker(
            name="v3_signal",
            description="V3 signal processing tests (12 signal types)",
            category=MarkerCategory.V3,
            priority="critical"
        ),
        PytestMarker(
            name="v3_routing",
            description="V3 routing matrix tests (Priority 1 & 2)",
            category=MarkerCategory.V3,
            priority="critical"
        ),
        PytestMarker(
            name="v3_dual_order",
            description="V3 dual order system tests (Order A + Order B)",
            category=MarkerCategory.V3,
            priority="critical"
        ),
        PytestMarker(
            name="v3_mtf",
            description="V3 MTF 4-pillar extraction tests",
            category=MarkerCategory.V3,
            priority="high"
        ),
        PytestMarker(
            name="v3_position",
            description="V3 position sizing 4-step tests",
            category=MarkerCategory.V3,
            priority="high"
        ),
        PytestMarker(
            name="v3_trend_bypass",
            description="V3 trend bypass logic tests",
            category=MarkerCategory.V3,
            priority="high"
        ),
    ]
    
    V6_MARKERS = [
        PytestMarker(
            name="v6_1m",
            description="V6 1M scalping tests (ORDER_B_ONLY)",
            category=MarkerCategory.V6,
            priority="high"
        ),
        PytestMarker(
            name="v6_5m",
            description="V6 5M momentum tests (DUAL_ORDERS)",
            category=MarkerCategory.V6,
            priority="high"
        ),
        PytestMarker(
            name="v6_15m",
            description="V6 15M intraday tests (ORDER_A_ONLY)",
            category=MarkerCategory.V6,
            priority="high"
        ),
        PytestMarker(
            name="v6_1h",
            description="V6 1H swing tests (ORDER_A_ONLY)",
            category=MarkerCategory.V6,
            priority="high"
        ),
        PytestMarker(
            name="v6_trend_pulse",
            description="V6 Trend Pulse system tests",
            category=MarkerCategory.V6,
            priority="high"
        ),
    ]
    
    INTEGRATION_MARKERS = [
        PytestMarker(
            name="integration",
            description="Integration tests (V3 + V6 simultaneous)",
            category=MarkerCategory.INTEGRATION,
            priority="critical"
        ),
        PytestMarker(
            name="service_api",
            description="ServiceAPI integration tests",
            category=MarkerCategory.INTEGRATION,
            priority="critical"
        ),
        PytestMarker(
            name="database",
            description="Database integration tests",
            category=MarkerCategory.INTEGRATION,
            priority="high"
        ),
    ]
    
    SHADOW_MODE_MARKERS = [
        PytestMarker(
            name="shadow_mode",
            description="Shadow mode tests (72-hour simulation)",
            category=MarkerCategory.SHADOW_MODE,
            priority="critical"
        ),
        PytestMarker(
            name="shadow_v3",
            description="V3 shadow mode tests",
            category=MarkerCategory.SHADOW_MODE,
            priority="high"
        ),
        PytestMarker(
            name="shadow_v6",
            description="V6 shadow mode tests",
            category=MarkerCategory.SHADOW_MODE,
            priority="high"
        ),
    ]
    
    PRIORITY_MARKERS = [
        PytestMarker(
            name="critical",
            description="Critical priority tests (must pass for release)",
            category=MarkerCategory.PRIORITY,
            priority="critical"
        ),
        PytestMarker(
            name="high",
            description="High priority tests",
            category=MarkerCategory.PRIORITY,
            priority="high"
        ),
        PytestMarker(
            name="medium",
            description="Medium priority tests",
            category=MarkerCategory.PRIORITY,
            priority="medium"
        ),
        PytestMarker(
            name="low",
            description="Low priority tests",
            category=MarkerCategory.PRIORITY,
            priority="low"
        ),
    ]
    
    @classmethod
    def get_all_markers(cls) -> List[PytestMarker]:
        """Get all registered markers."""
        return (
            cls.V3_MARKERS +
            cls.V6_MARKERS +
            cls.INTEGRATION_MARKERS +
            cls.SHADOW_MODE_MARKERS +
            cls.PRIORITY_MARKERS
        )
    
    @classmethod
    def get_markers_by_category(cls, category: MarkerCategory) -> List[PytestMarker]:
        """Get markers for a specific category."""
        category_map = {
            MarkerCategory.V3: cls.V3_MARKERS,
            MarkerCategory.V6: cls.V6_MARKERS,
            MarkerCategory.INTEGRATION: cls.INTEGRATION_MARKERS,
            MarkerCategory.SHADOW_MODE: cls.SHADOW_MODE_MARKERS,
            MarkerCategory.PRIORITY: cls.PRIORITY_MARKERS,
        }
        return category_map.get(category, [])
    
    @classmethod
    def get_marker_by_name(cls, name: str) -> Optional[PytestMarker]:
        """Get marker by name."""
        for marker in cls.get_all_markers():
            if marker.name == name:
                return marker
        return None
    
    @classmethod
    def generate_pytest_ini_markers(cls) -> str:
        """Generate markers section for pytest.ini."""
        lines = ["markers ="]
        for marker in cls.get_all_markers():
            lines.append(f"    {marker.to_ini_format()}")
        return "\n".join(lines)
    
    @classmethod
    def get_critical_markers(cls) -> List[PytestMarker]:
        """Get all critical priority markers."""
        return [m for m in cls.get_all_markers() if m.priority == "critical"]
    
    @classmethod
    def get_v3_marker_names(cls) -> List[str]:
        """Get V3 marker names."""
        return [m.name for m in cls.V3_MARKERS]
    
    @classmethod
    def get_v6_marker_names(cls) -> List[str]:
        """Get V6 marker names."""
        return [m.name for m in cls.V6_MARKERS]


@dataclass
class TestSuite:
    """Test suite definition with markers."""
    name: str
    description: str
    markers: List[str]
    test_files: List[str] = field(default_factory=list)
    priority: str = "medium"
    
    def get_pytest_command(self) -> str:
        """Get pytest command to run this suite."""
        marker_expr = " or ".join(self.markers)
        return f"pytest -m '{marker_expr}'"


class TestSuiteRegistry:
    """Registry of predefined test suites."""
    
    SUITES = {
        "v3_full": TestSuite(
            name="V3 Full Suite",
            description="All V3 Combined Logic tests",
            markers=MarkerRegistry.get_v3_marker_names(),
            priority="critical"
        ),
        "v6_full": TestSuite(
            name="V6 Full Suite",
            description="All V6 Price Action tests",
            markers=MarkerRegistry.get_v6_marker_names(),
            priority="critical"
        ),
        "v6_1m_only": TestSuite(
            name="V6 1M Scalping Suite",
            description="V6 1M scalping tests only",
            markers=["v6_1m"],
            priority="high"
        ),
        "v6_5m_only": TestSuite(
            name="V6 5M Momentum Suite",
            description="V6 5M momentum tests only",
            markers=["v6_5m"],
            priority="high"
        ),
        "v6_15m_only": TestSuite(
            name="V6 15M Intraday Suite",
            description="V6 15M intraday tests only",
            markers=["v6_15m"],
            priority="high"
        ),
        "v6_1h_only": TestSuite(
            name="V6 1H Swing Suite",
            description="V6 1H swing tests only",
            markers=["v6_1h"],
            priority="high"
        ),
        "integration": TestSuite(
            name="Integration Suite",
            description="All integration tests",
            markers=["integration", "service_api", "database"],
            priority="critical"
        ),
        "shadow_mode": TestSuite(
            name="Shadow Mode Suite",
            description="All shadow mode tests",
            markers=["shadow_mode", "shadow_v3", "shadow_v6"],
            priority="critical"
        ),
        "critical_only": TestSuite(
            name="Critical Tests Only",
            description="Only critical priority tests",
            markers=["critical"],
            priority="critical"
        ),
        "pre_release": TestSuite(
            name="Pre-Release Suite",
            description="All tests required before release",
            markers=["critical", "high"],
            priority="critical"
        ),
    }
    
    @classmethod
    def get_suite(cls, name: str) -> Optional[TestSuite]:
        """Get suite by name."""
        return cls.SUITES.get(name)
    
    @classmethod
    def get_all_suites(cls) -> Dict[str, TestSuite]:
        """Get all registered suites."""
        return cls.SUITES
    
    @classmethod
    def get_suite_names(cls) -> List[str]:
        """Get all suite names."""
        return list(cls.SUITES.keys())


def generate_conftest_markers() -> str:
    """Generate conftest.py marker registration code."""
    code = '''"""
Pytest configuration with marker registration.
Auto-generated by testing framework.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
'''
    
    for marker in MarkerRegistry.get_all_markers():
        code += f'    config.addinivalue_line("markers", "{marker.to_ini_format()}")\n'
    
    return code


def generate_pytest_ini() -> str:
    """Generate pytest.ini content."""
    content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short

"""
    content += MarkerRegistry.generate_pytest_ini_markers()
    return content
