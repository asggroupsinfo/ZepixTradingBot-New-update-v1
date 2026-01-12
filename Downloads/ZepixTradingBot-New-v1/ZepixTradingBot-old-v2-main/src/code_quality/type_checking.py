"""
Type Checking Configuration for V5 Hybrid Plugin Architecture.

This module provides type checking tools:
- Mypy configuration and runner
- Type stub management
- Type coverage analysis

Version: 1.0
Date: 2026-01-12
"""

import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import json
import re


class TypeCheckSeverity(Enum):
    """Type check issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"


@dataclass
class TypeCheckIssue:
    """Single type check issue."""
    file_path: str
    line: int
    column: int
    code: str
    message: str
    severity: TypeCheckSeverity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value
        }


@dataclass
class TypeCheckResult:
    """Result of type checking operation."""
    issues: List[TypeCheckIssue] = field(default_factory=list)
    passed: bool = True
    exit_code: int = 0
    duration_ms: float = 0.0
    files_checked: int = 0
    lines_checked: int = 0
    
    @property
    def error_count(self) -> int:
        """Get number of errors."""
        return sum(1 for i in self.issues if i.severity == TypeCheckSeverity.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Get number of warnings."""
        return sum(1 for i in self.issues if i.severity == TypeCheckSeverity.WARNING)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "files_checked": self.files_checked,
            "lines_checked": self.lines_checked,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [i.to_dict() for i in self.issues]
        }


class MypyConfig:
    """Mypy type checking configuration generator."""
    
    DEFAULT_CONFIG = {
        "mypy": {
            "python_version": "3.10",
            "warn_return_any": True,
            "warn_unused_configs": True,
            "warn_redundant_casts": True,
            "warn_unused_ignores": True,
            "warn_no_return": True,
            "warn_unreachable": True,
            "strict_equality": True,
            "strict_concatenate": True,
            "check_untyped_defs": True,
            "disallow_untyped_defs": False,
            "disallow_incomplete_defs": True,
            "disallow_untyped_decorators": False,
            "no_implicit_optional": True,
            "show_error_codes": True,
            "show_column_numbers": True,
            "pretty": True,
            "ignore_missing_imports": True,
            "follow_imports": "silent",
            "exclude": [
                "migrations/",
                "tests/",
                "venv/",
                ".venv/",
            ],
        },
        "mypy-src.*": {
            "disallow_untyped_defs": True,
        },
        "mypy-tests.*": {
            "disallow_untyped_defs": False,
            "ignore_errors": True,
        },
    }
    
    STRICT_CONFIG = {
        "mypy": {
            "python_version": "3.10",
            "strict": True,
            "warn_return_any": True,
            "warn_unused_configs": True,
            "disallow_untyped_defs": True,
            "disallow_incomplete_defs": True,
            "disallow_untyped_decorators": True,
            "no_implicit_optional": True,
            "warn_redundant_casts": True,
            "warn_unused_ignores": True,
            "warn_no_return": True,
            "warn_unreachable": True,
            "strict_equality": True,
            "show_error_codes": True,
            "show_column_numbers": True,
            "pretty": True,
        },
    }
    
    @classmethod
    def generate_mypy_ini(cls, strict: bool = False) -> str:
        """Generate mypy.ini content."""
        config = cls.STRICT_CONFIG if strict else cls.DEFAULT_CONFIG
        lines = ["# Mypy configuration for V5 Hybrid Plugin Architecture", ""]
        
        for section, options in config.items():
            lines.append(f"[{section}]")
            for key, value in options.items():
                if isinstance(value, bool):
                    lines.append(f"{key} = {'True' if value else 'False'}")
                elif isinstance(value, list):
                    for item in value:
                        lines.append(f"{key} = {item}")
                else:
                    lines.append(f"{key} = {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def generate_pyproject_section(cls, strict: bool = False) -> str:
        """Generate [tool.mypy] section for pyproject.toml."""
        config = cls.STRICT_CONFIG if strict else cls.DEFAULT_CONFIG
        lines = ["[tool.mypy]"]
        
        mypy_config = config.get("mypy", {})
        for key, value in mypy_config.items():
            if isinstance(value, bool):
                lines.append(f'{key} = {"true" if value else "false"}')
            elif isinstance(value, list):
                lines.append(f'{key} = {json.dumps(value)}')
            else:
                lines.append(f'{key} = "{value}"')
        
        return "\n".join(lines)
    
    @classmethod
    def get_config_dict(cls, strict: bool = False) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return cls.STRICT_CONFIG.copy() if strict else cls.DEFAULT_CONFIG.copy()


class TypeCheckRunner:
    """Runner for type checking tools."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize type check runner."""
        self.project_root = project_root or os.getcwd()
        self.results: List[TypeCheckResult] = []
    
    def run_mypy(self, paths: Optional[List[str]] = None, strict: bool = False) -> TypeCheckResult:
        """Run mypy on specified paths."""
        paths = paths or [os.path.join(self.project_root, "src")]
        start_time = datetime.now()
        
        result = TypeCheckResult()
        
        try:
            cmd = [sys.executable, "-m", "mypy"]
            if strict:
                cmd.append("--strict")
            cmd.extend(["--show-error-codes", "--show-column-numbers"])
            cmd.extend(paths)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )
            
            result.exit_code = proc.returncode
            result.passed = proc.returncode == 0
            
            if proc.stdout:
                result.issues = self._parse_mypy_output(proc.stdout)
            
        except subprocess.TimeoutExpired:
            result.passed = False
            result.exit_code = -1
        except Exception:
            result.passed = False
            result.exit_code = -1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.results.append(result)
        return result
    
    def _parse_mypy_output(self, output: str) -> List[TypeCheckIssue]:
        """Parse mypy output into issues."""
        issues = []
        pattern = r"^(.+):(\d+):(\d+): (error|warning|note): (.+?)(?:\s+\[([^\]]+)\])?$"
        
        for line in output.split("\n"):
            match = re.match(pattern, line)
            if match:
                file_path, line_num, col, severity_str, message, code = match.groups()
                
                severity_map = {
                    "error": TypeCheckSeverity.ERROR,
                    "warning": TypeCheckSeverity.WARNING,
                    "note": TypeCheckSeverity.NOTE,
                }
                
                issues.append(TypeCheckIssue(
                    file_path=file_path,
                    line=int(line_num),
                    column=int(col),
                    code=code or "",
                    message=message,
                    severity=severity_map.get(severity_str, TypeCheckSeverity.NOTE)
                ))
        
        return issues
    
    def get_type_coverage(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get type coverage statistics."""
        paths = paths or [os.path.join(self.project_root, "src")]
        
        try:
            cmd = [sys.executable, "-m", "mypy", "--txt-report", "-", "--any-exprs-report", "-"]
            cmd.extend(paths)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )
            
            return {
                "coverage_available": True,
                "output": proc.stdout,
            }
            
        except Exception:
            return {
                "coverage_available": False,
                "output": "",
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all type check results."""
        if not self.results:
            return {
                "total_runs": 0,
                "all_passed": True,
                "total_errors": 0,
                "total_warnings": 0,
            }
        
        total_errors = sum(r.error_count for r in self.results)
        total_warnings = sum(r.warning_count for r in self.results)
        all_passed = all(r.passed for r in self.results)
        
        return {
            "total_runs": len(self.results),
            "all_passed": all_passed,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "results": [r.to_dict() for r in self.results]
        }


class TypeStubManager:
    """Manager for type stubs."""
    
    COMMON_STUBS = [
        "types-requests",
        "types-python-dateutil",
        "types-PyYAML",
        "types-setuptools",
    ]
    
    PROJECT_STUBS = {
        "MetaTrader5": "# Type stubs for MetaTrader5\nfrom typing import Any, Dict, List, Optional, Tuple\n\ndef initialize() -> bool: ...\ndef shutdown() -> None: ...\ndef login(login: int, password: str, server: str) -> bool: ...\ndef account_info() -> Any: ...\ndef symbol_info(symbol: str) -> Any: ...\ndef symbol_info_tick(symbol: str) -> Any: ...\ndef order_send(request: Dict[str, Any]) -> Any: ...\ndef positions_get(symbol: Optional[str] = None) -> Tuple[Any, ...]: ...\ndef orders_get(symbol: Optional[str] = None) -> Tuple[Any, ...]: ...\n",
    }
    
    @classmethod
    def get_stub_packages(cls) -> List[str]:
        """Get list of stub packages to install."""
        return cls.COMMON_STUBS.copy()
    
    @classmethod
    def generate_custom_stub(cls, module_name: str) -> Optional[str]:
        """Generate custom stub for a module."""
        return cls.PROJECT_STUBS.get(module_name)
    
    @classmethod
    def get_all_custom_stubs(cls) -> Dict[str, str]:
        """Get all custom stubs."""
        return cls.PROJECT_STUBS.copy()


def generate_type_config(output_dir: str, strict: bool = False) -> Dict[str, str]:
    """Generate type checking configuration files."""
    configs = {}
    
    mypy_ini = MypyConfig.generate_mypy_ini(strict)
    configs["mypy.ini"] = mypy_ini
    
    pyproject_section = MypyConfig.generate_pyproject_section(strict)
    configs["pyproject_mypy_section.toml"] = pyproject_section
    
    return configs
