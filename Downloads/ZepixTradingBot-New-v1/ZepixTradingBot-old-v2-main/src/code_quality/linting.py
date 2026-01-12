"""
Linting & Formatting Configuration for V5 Hybrid Plugin Architecture.

This module provides linting and formatting tools:
- Pylint configuration and runner
- Black formatting configuration
- Isort import sorting configuration
- Flake8 style checking configuration

Version: 1.0
Date: 2026-01-12
"""

import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import json


class LintSeverity(Enum):
    """Lint issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    CONVENTION = "convention"
    REFACTOR = "refactor"
    INFO = "info"


class LintTool(Enum):
    """Available linting tools."""
    PYLINT = "pylint"
    FLAKE8 = "flake8"
    BLACK = "black"
    ISORT = "isort"
    MYPY = "mypy"


@dataclass
class LintIssue:
    """Single lint issue."""
    file_path: str
    line: int
    column: int
    code: str
    message: str
    severity: LintSeverity
    tool: LintTool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "tool": self.tool.value
        }


@dataclass
class LintResult:
    """Result of linting operation."""
    tool: LintTool
    issues: List[LintIssue] = field(default_factory=list)
    passed: bool = True
    exit_code: int = 0
    duration_ms: float = 0.0
    files_checked: int = 0
    
    @property
    def error_count(self) -> int:
        """Get number of errors."""
        return sum(1 for i in self.issues if i.severity == LintSeverity.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Get number of warnings."""
        return sum(1 for i in self.issues if i.severity == LintSeverity.WARNING)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool": self.tool.value,
            "passed": self.passed,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "files_checked": self.files_checked,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [i.to_dict() for i in self.issues]
        }


class PylintConfig:
    """Pylint configuration generator."""
    
    DEFAULT_CONFIG = {
        "MASTER": {
            "ignore": ["migrations", "tests", "__pycache__"],
            "ignore-patterns": ["test_*.py"],
            "jobs": 4,
            "persistent": "yes",
            "suggestion-mode": "yes",
        },
        "MESSAGES CONTROL": {
            "disable": [
                "C0114",  # missing-module-docstring
                "C0115",  # missing-class-docstring (we use our own)
                "C0116",  # missing-function-docstring (we use our own)
                "R0903",  # too-few-public-methods
                "R0913",  # too-many-arguments
                "W0511",  # fixme
            ],
            "enable": [
                "W0611",  # unused-import
                "W0612",  # unused-variable
                "E1101",  # no-member
            ],
        },
        "FORMAT": {
            "max-line-length": 120,
            "max-module-lines": 1000,
            "indent-string": "    ",
        },
        "BASIC": {
            "good-names": ["i", "j", "k", "ex", "db", "id", "tf", "sl", "tp"],
            "bad-names": ["foo", "bar", "baz"],
            "function-rgx": "[a-z_][a-z0-9_]{2,50}$",
            "variable-rgx": "[a-z_][a-z0-9_]{1,30}$",
            "const-rgx": "(([A-Z_][A-Z0-9_]*)|(__.*__))$",
        },
        "DESIGN": {
            "max-args": 10,
            "max-locals": 20,
            "max-returns": 6,
            "max-branches": 15,
            "max-statements": 60,
            "max-parents": 7,
            "max-attributes": 15,
            "min-public-methods": 1,
            "max-public-methods": 25,
        },
        "IMPORTS": {
            "known-third-party": ["MetaTrader5", "telegram", "fastapi", "pydantic"],
        },
        "EXCEPTIONS": {
            "overgeneral-exceptions": ["Exception", "BaseException"],
        },
    }
    
    @classmethod
    def generate_pylintrc(cls) -> str:
        """Generate .pylintrc content."""
        lines = ["# Pylint configuration for V5 Hybrid Plugin Architecture", ""]
        
        for section, options in cls.DEFAULT_CONFIG.items():
            lines.append(f"[{section}]")
            for key, value in options.items():
                if isinstance(value, list):
                    lines.append(f"{key}={','.join(str(v) for v in value)}")
                else:
                    lines.append(f"{key}={value}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return cls.DEFAULT_CONFIG.copy()


class BlackConfig:
    """Black formatter configuration generator."""
    
    DEFAULT_CONFIG = {
        "line-length": 120,
        "target-version": ["py310", "py311", "py312"],
        "include": r"\.pyi?$",
        "exclude": r"/(\.git|\.hg|\.mypy_cache|\.tox|\.venv|_build|buck-out|build|dist|migrations)/",
        "skip-string-normalization": False,
        "skip-magic-trailing-comma": False,
    }
    
    @classmethod
    def generate_pyproject_section(cls) -> str:
        """Generate [tool.black] section for pyproject.toml."""
        lines = ["[tool.black]"]
        
        for key, value in cls.DEFAULT_CONFIG.items():
            if isinstance(value, list):
                lines.append(f'{key} = {json.dumps(value)}')
            elif isinstance(value, bool):
                lines.append(f'{key} = {"true" if value else "false"}')
            elif isinstance(value, int):
                lines.append(f'{key} = {value}')
            else:
                lines.append(f'{key} = "{value}"')
        
        return "\n".join(lines)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return cls.DEFAULT_CONFIG.copy()


class IsortConfig:
    """Isort import sorting configuration generator."""
    
    DEFAULT_CONFIG = {
        "profile": "black",
        "line_length": 120,
        "multi_line_output": 3,
        "include_trailing_comma": True,
        "force_grid_wrap": 0,
        "use_parentheses": True,
        "ensure_newline_before_comments": True,
        "skip": [".git", "__pycache__", "migrations", ".venv", "venv"],
        "skip_glob": ["**/migrations/*"],
        "known_first_party": ["src", "core", "services", "telegram", "logic_plugins"],
        "known_third_party": ["MetaTrader5", "telegram", "fastapi", "pydantic", "pytest"],
        "sections": ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"],
    }
    
    @classmethod
    def generate_pyproject_section(cls) -> str:
        """Generate [tool.isort] section for pyproject.toml."""
        lines = ["[tool.isort]"]
        
        for key, value in cls.DEFAULT_CONFIG.items():
            if isinstance(value, list):
                lines.append(f'{key} = {json.dumps(value)}')
            elif isinstance(value, bool):
                lines.append(f'{key} = {"true" if value else "false"}')
            elif isinstance(value, int):
                lines.append(f'{key} = {value}')
            else:
                lines.append(f'{key} = "{value}"')
        
        return "\n".join(lines)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return cls.DEFAULT_CONFIG.copy()


class Flake8Config:
    """Flake8 style checking configuration generator."""
    
    DEFAULT_CONFIG = {
        "max-line-length": 120,
        "max-complexity": 15,
        "select": ["E", "F", "W", "C90"],
        "ignore": [
            "E501",  # line too long (handled by black)
            "W503",  # line break before binary operator
            "E203",  # whitespace before ':' (black conflict)
        ],
        "exclude": [
            ".git",
            "__pycache__",
            "migrations",
            ".venv",
            "venv",
            "build",
            "dist",
        ],
        "per-file-ignores": {
            "__init__.py": ["F401"],  # imported but unused
            "tests/*": ["S101"],  # use of assert
        },
    }
    
    @classmethod
    def generate_setup_cfg_section(cls) -> str:
        """Generate [flake8] section for setup.cfg."""
        lines = ["[flake8]"]
        
        for key, value in cls.DEFAULT_CONFIG.items():
            if key == "per-file-ignores":
                pfi_lines = []
                for file_pattern, ignores in value.items():
                    pfi_lines.append(f"    {file_pattern}: {','.join(ignores)}")
                lines.append(f"per-file-ignores =")
                lines.extend(pfi_lines)
            elif isinstance(value, list):
                lines.append(f"{key} = {','.join(str(v) for v in value)}")
            else:
                lines.append(f"{key} = {value}")
        
        return "\n".join(lines)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return cls.DEFAULT_CONFIG.copy()


class LintRunner:
    """Runner for linting tools."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize lint runner."""
        self.project_root = project_root or os.getcwd()
        self.results: List[LintResult] = []
    
    def run_pylint(self, paths: Optional[List[str]] = None) -> LintResult:
        """Run pylint on specified paths."""
        paths = paths or [os.path.join(self.project_root, "src")]
        start_time = datetime.now()
        
        result = LintResult(tool=LintTool.PYLINT)
        
        try:
            cmd = [sys.executable, "-m", "pylint", "--output-format=json"] + paths
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = proc.returncode
            result.passed = proc.returncode == 0
            
            if proc.stdout:
                try:
                    issues_data = json.loads(proc.stdout)
                    for issue in issues_data:
                        severity = self._map_pylint_severity(issue.get("type", ""))
                        result.issues.append(LintIssue(
                            file_path=issue.get("path", ""),
                            line=issue.get("line", 0),
                            column=issue.get("column", 0),
                            code=issue.get("message-id", ""),
                            message=issue.get("message", ""),
                            severity=severity,
                            tool=LintTool.PYLINT
                        ))
                except json.JSONDecodeError:
                    pass
                    
        except subprocess.TimeoutExpired:
            result.passed = False
            result.exit_code = -1
        except Exception:
            result.passed = False
            result.exit_code = -1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.results.append(result)
        return result
    
    def run_flake8(self, paths: Optional[List[str]] = None) -> LintResult:
        """Run flake8 on specified paths."""
        paths = paths or [os.path.join(self.project_root, "src")]
        start_time = datetime.now()
        
        result = LintResult(tool=LintTool.FLAKE8)
        
        try:
            cmd = [sys.executable, "-m", "flake8", "--format=json"] + paths
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = proc.returncode
            result.passed = proc.returncode == 0
            
        except subprocess.TimeoutExpired:
            result.passed = False
            result.exit_code = -1
        except Exception:
            result.passed = False
            result.exit_code = -1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.results.append(result)
        return result
    
    def run_black_check(self, paths: Optional[List[str]] = None) -> LintResult:
        """Run black in check mode."""
        paths = paths or [os.path.join(self.project_root, "src")]
        start_time = datetime.now()
        
        result = LintResult(tool=LintTool.BLACK)
        
        try:
            cmd = [sys.executable, "-m", "black", "--check", "--diff"] + paths
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = proc.returncode
            result.passed = proc.returncode == 0
            
        except subprocess.TimeoutExpired:
            result.passed = False
            result.exit_code = -1
        except Exception:
            result.passed = False
            result.exit_code = -1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.results.append(result)
        return result
    
    def run_isort_check(self, paths: Optional[List[str]] = None) -> LintResult:
        """Run isort in check mode."""
        paths = paths or [os.path.join(self.project_root, "src")]
        start_time = datetime.now()
        
        result = LintResult(tool=LintTool.ISORT)
        
        try:
            cmd = [sys.executable, "-m", "isort", "--check-only", "--diff"] + paths
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = proc.returncode
            result.passed = proc.returncode == 0
            
        except subprocess.TimeoutExpired:
            result.passed = False
            result.exit_code = -1
        except Exception:
            result.passed = False
            result.exit_code = -1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.results.append(result)
        return result
    
    def run_all(self, paths: Optional[List[str]] = None) -> List[LintResult]:
        """Run all linting tools."""
        self.run_pylint(paths)
        self.run_flake8(paths)
        self.run_black_check(paths)
        self.run_isort_check(paths)
        return self.results
    
    def _map_pylint_severity(self, pylint_type: str) -> LintSeverity:
        """Map pylint message type to severity."""
        mapping = {
            "error": LintSeverity.ERROR,
            "warning": LintSeverity.WARNING,
            "convention": LintSeverity.CONVENTION,
            "refactor": LintSeverity.REFACTOR,
            "info": LintSeverity.INFO,
        }
        return mapping.get(pylint_type.lower(), LintSeverity.INFO)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all lint results."""
        total_errors = sum(r.error_count for r in self.results)
        total_warnings = sum(r.warning_count for r in self.results)
        all_passed = all(r.passed for r in self.results)
        
        return {
            "total_tools": len(self.results),
            "all_passed": all_passed,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "results": [r.to_dict() for r in self.results]
        }


def generate_all_configs(output_dir: str) -> Dict[str, str]:
    """Generate all linting configuration files."""
    configs = {}
    
    pylintrc = PylintConfig.generate_pylintrc()
    configs[".pylintrc"] = pylintrc
    
    black_config = BlackConfig.generate_pyproject_section()
    isort_config = IsortConfig.generate_pyproject_section()
    configs["pyproject_lint_section.toml"] = f"{black_config}\n\n{isort_config}"
    
    flake8_config = Flake8Config.generate_setup_cfg_section()
    configs["setup_flake8_section.cfg"] = flake8_config
    
    return configs
