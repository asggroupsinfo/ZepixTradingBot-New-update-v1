"""
CI/CD Integration Scripts for V5 Hybrid Plugin Architecture.

This module provides CI/CD integration tools:
- GitHub Actions workflow generator
- Quality suite runner
- CI pipeline configuration
- Quality gate enforcement

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


class CIProvider(Enum):
    """CI/CD providers."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"


class QualityCheckType(Enum):
    """Quality check types."""
    LINT = "lint"
    TYPE_CHECK = "type_check"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    TESTS = "tests"
    COVERAGE = "coverage"
    FORMAT = "format"


class CheckStatus(Enum):
    """Check execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class QualityCheckResult:
    """Result of a quality check."""
    check_type: QualityCheckType
    status: CheckStatus
    duration_ms: float = 0.0
    exit_code: int = 0
    output: str = ""
    error: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        """Check if quality check passed."""
        return self.status == CheckStatus.PASSED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_type": self.check_type.value,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "exit_code": self.exit_code,
            "output": self.output[:1000] if self.output else "",
            "error": self.error[:500] if self.error else "",
            "metrics": self.metrics,
            "passed": self.passed
        }


@dataclass
class QualitySuiteResult:
    """Result of full quality suite run."""
    checks: List[QualityCheckResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    @property
    def total_checks(self) -> int:
        """Get total number of checks."""
        return len(self.checks)
    
    @property
    def passed_checks(self) -> int:
        """Get number of passed checks."""
        return sum(1 for c in self.checks if c.passed)
    
    @property
    def failed_checks(self) -> int:
        """Get number of failed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
    
    @property
    def all_passed(self) -> bool:
        """Check if all checks passed."""
        return all(c.passed for c in self.checks)
    
    @property
    def total_duration_ms(self) -> float:
        """Get total duration."""
        return sum(c.duration_ms for c in self.checks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "all_passed": self.all_passed,
            "total_duration_ms": self.total_duration_ms,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "checks": [c.to_dict() for c in self.checks]
        }


class QualitySuiteRunner:
    """Runner for full quality suite."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize quality suite runner."""
        self.project_root = project_root or os.getcwd()
    
    def run_lint(self) -> QualityCheckResult:
        """Run linting checks."""
        start_time = datetime.now()
        result = QualityCheckResult(check_type=QualityCheckType.LINT, status=CheckStatus.RUNNING)
        
        try:
            cmd = [sys.executable, "-m", "flake8", "src/", "--max-line-length=120", "--ignore=E501,W503,E203"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = proc.returncode
            result.output = proc.stdout
            result.error = proc.stderr
            result.status = CheckStatus.PASSED if proc.returncode == 0 else CheckStatus.FAILED
            
        except subprocess.TimeoutExpired:
            result.status = CheckStatus.ERROR
            result.error = "Timeout expired"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error = str(e)
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_type_check(self) -> QualityCheckResult:
        """Run type checking."""
        start_time = datetime.now()
        result = QualityCheckResult(check_type=QualityCheckType.TYPE_CHECK, status=CheckStatus.RUNNING)
        
        try:
            cmd = [sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )
            
            result.exit_code = proc.returncode
            result.output = proc.stdout
            result.error = proc.stderr
            result.status = CheckStatus.PASSED if proc.returncode == 0 else CheckStatus.FAILED
            
        except subprocess.TimeoutExpired:
            result.status = CheckStatus.ERROR
            result.error = "Timeout expired"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error = str(e)
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_security(self) -> QualityCheckResult:
        """Run security scanning."""
        start_time = datetime.now()
        result = QualityCheckResult(check_type=QualityCheckType.SECURITY, status=CheckStatus.RUNNING)
        
        try:
            cmd = [sys.executable, "-m", "bandit", "-r", "src/", "-f", "json"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = proc.returncode
            result.output = proc.stdout
            result.error = proc.stderr
            
            if proc.stdout:
                try:
                    data = json.loads(proc.stdout)
                    high_issues = len([r for r in data.get("results", []) if r.get("issue_severity") == "HIGH"])
                    result.metrics = {"high_severity_issues": high_issues}
                    result.status = CheckStatus.PASSED if high_issues == 0 else CheckStatus.FAILED
                except json.JSONDecodeError:
                    result.status = CheckStatus.PASSED if proc.returncode == 0 else CheckStatus.FAILED
            else:
                result.status = CheckStatus.PASSED if proc.returncode == 0 else CheckStatus.FAILED
            
        except subprocess.TimeoutExpired:
            result.status = CheckStatus.ERROR
            result.error = "Timeout expired"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error = str(e)
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_tests(self, coverage: bool = True) -> QualityCheckResult:
        """Run tests with optional coverage."""
        start_time = datetime.now()
        result = QualityCheckResult(check_type=QualityCheckType.TESTS, status=CheckStatus.RUNNING)
        
        try:
            cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
            if coverage:
                cmd.extend(["--cov=src", "--cov-report=json"])
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )
            
            result.exit_code = proc.returncode
            result.output = proc.stdout
            result.error = proc.stderr
            result.status = CheckStatus.PASSED if proc.returncode == 0 else CheckStatus.FAILED
            
            if coverage:
                cov_file = os.path.join(self.project_root, "coverage.json")
                if os.path.exists(cov_file):
                    with open(cov_file, 'r') as f:
                        cov_data = json.load(f)
                        result.metrics["coverage_percent"] = cov_data.get("totals", {}).get("percent_covered", 0)
            
        except subprocess.TimeoutExpired:
            result.status = CheckStatus.ERROR
            result.error = "Timeout expired"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error = str(e)
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_format_check(self) -> QualityCheckResult:
        """Run format checking (black, isort)."""
        start_time = datetime.now()
        result = QualityCheckResult(check_type=QualityCheckType.FORMAT, status=CheckStatus.RUNNING)
        
        try:
            black_cmd = [sys.executable, "-m", "black", "--check", "--diff", "src/"]
            black_proc = subprocess.run(
                black_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            isort_cmd = [sys.executable, "-m", "isort", "--check-only", "--diff", "src/"]
            isort_proc = subprocess.run(
                isort_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            result.exit_code = max(black_proc.returncode, isort_proc.returncode)
            result.output = f"Black:\n{black_proc.stdout}\n\nIsort:\n{isort_proc.stdout}"
            result.error = f"Black:\n{black_proc.stderr}\n\nIsort:\n{isort_proc.stderr}"
            result.status = CheckStatus.PASSED if result.exit_code == 0 else CheckStatus.FAILED
            result.metrics = {
                "black_passed": black_proc.returncode == 0,
                "isort_passed": isort_proc.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            result.status = CheckStatus.ERROR
            result.error = "Timeout expired"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error = str(e)
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_all(self, include_tests: bool = True) -> QualitySuiteResult:
        """Run all quality checks."""
        result = QualitySuiteResult()
        
        result.checks.append(self.run_format_check())
        result.checks.append(self.run_lint())
        result.checks.append(self.run_type_check())
        result.checks.append(self.run_security())
        
        if include_tests:
            result.checks.append(self.run_tests())
        
        result.completed_at = datetime.now()
        return result


class GitHubActionsGenerator:
    """Generator for GitHub Actions workflows."""
    
    QUALITY_WORKFLOW = '''name: Code Quality

on:
  push:
    branches: [ main, develop, 'feature/*', 'devin/*' ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort mypy bandit pytest pytest-cov
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Check formatting with Black
      run: black --check --diff src/

    - name: Check imports with isort
      run: isort --check-only --diff src/

    - name: Lint with flake8
      run: flake8 src/ --max-line-length=120 --ignore=E501,W503,E203

    - name: Type check with mypy
      run: mypy src/ --ignore-missing-imports
      continue-on-error: true

    - name: Security scan with Bandit
      run: bandit -r src/ -ll
      continue-on-error: true

    - name: Run tests
      run: pytest tests/ -v --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
'''
    
    PRE_COMMIT_WORKFLOW = '''name: Pre-commit

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    - uses: pre-commit/action@v3.0.0
'''
    
    TEST_WORKFLOW = '''name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov pytest-asyncio
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run tests
      run: pytest tests/ -v --cov=src --cov-report=xml --cov-report=html

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
'''
    
    @classmethod
    def generate_quality_workflow(cls) -> str:
        """Generate quality workflow."""
        return cls.QUALITY_WORKFLOW
    
    @classmethod
    def generate_pre_commit_workflow(cls) -> str:
        """Generate pre-commit workflow."""
        return cls.PRE_COMMIT_WORKFLOW
    
    @classmethod
    def generate_test_workflow(cls) -> str:
        """Generate test workflow."""
        return cls.TEST_WORKFLOW
    
    @classmethod
    def generate_all_workflows(cls) -> Dict[str, str]:
        """Generate all workflows."""
        return {
            "quality.yml": cls.QUALITY_WORKFLOW,
            "pre-commit.yml": cls.PRE_COMMIT_WORKFLOW,
            "tests.yml": cls.TEST_WORKFLOW,
        }


class QualityGateEnforcer:
    """Enforcer for quality gates in CI/CD."""
    
    DEFAULT_GATES = {
        "lint_passed": True,
        "type_check_passed": False,
        "security_no_high": True,
        "tests_passed": True,
        "coverage_min": 70.0,
        "format_passed": True,
    }
    
    def __init__(self, gates: Optional[Dict[str, Any]] = None):
        """Initialize quality gate enforcer."""
        self.gates = gates or self.DEFAULT_GATES.copy()
    
    def check_gates(self, suite_result: QualitySuiteResult) -> Dict[str, Any]:
        """Check if quality gates are met."""
        results = {
            "passed": True,
            "gates": {}
        }
        
        for check in suite_result.checks:
            if check.check_type == QualityCheckType.LINT:
                gate_passed = check.passed
                if self.gates.get("lint_passed") and not gate_passed:
                    results["passed"] = False
                results["gates"]["lint"] = {"required": self.gates.get("lint_passed"), "passed": gate_passed}
            
            elif check.check_type == QualityCheckType.TYPE_CHECK:
                gate_passed = check.passed
                if self.gates.get("type_check_passed") and not gate_passed:
                    results["passed"] = False
                results["gates"]["type_check"] = {"required": self.gates.get("type_check_passed"), "passed": gate_passed}
            
            elif check.check_type == QualityCheckType.SECURITY:
                high_issues = check.metrics.get("high_severity_issues", 0)
                gate_passed = high_issues == 0
                if self.gates.get("security_no_high") and not gate_passed:
                    results["passed"] = False
                results["gates"]["security"] = {"required": self.gates.get("security_no_high"), "passed": gate_passed, "high_issues": high_issues}
            
            elif check.check_type == QualityCheckType.TESTS:
                gate_passed = check.passed
                if self.gates.get("tests_passed") and not gate_passed:
                    results["passed"] = False
                results["gates"]["tests"] = {"required": self.gates.get("tests_passed"), "passed": gate_passed}
                
                coverage = check.metrics.get("coverage_percent", 0)
                min_coverage = self.gates.get("coverage_min", 0)
                coverage_passed = coverage >= min_coverage
                if min_coverage > 0 and not coverage_passed:
                    results["passed"] = False
                results["gates"]["coverage"] = {"required": min_coverage, "actual": coverage, "passed": coverage_passed}
            
            elif check.check_type == QualityCheckType.FORMAT:
                gate_passed = check.passed
                if self.gates.get("format_passed") and not gate_passed:
                    results["passed"] = False
                results["gates"]["format"] = {"required": self.gates.get("format_passed"), "passed": gate_passed}
        
        return results
    
    @classmethod
    def get_default_gates(cls) -> Dict[str, Any]:
        """Get default quality gates."""
        return cls.DEFAULT_GATES.copy()


class CIConfigGenerator:
    """Generator for CI configuration files."""
    
    @staticmethod
    def generate_github_actions(output_dir: str) -> Dict[str, str]:
        """Generate GitHub Actions workflow files."""
        workflows = GitHubActionsGenerator.generate_all_workflows()
        
        workflows_dir = os.path.join(output_dir, ".github", "workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        
        for filename, content in workflows.items():
            filepath = os.path.join(workflows_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        return workflows
    
    @staticmethod
    def generate_gitlab_ci() -> str:
        """Generate GitLab CI configuration."""
        return '''stages:
  - quality
  - test
  - security

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

quality:
  stage: quality
  image: python:3.10
  script:
    - pip install flake8 black isort mypy
    - black --check src/
    - isort --check-only src/
    - flake8 src/ --max-line-length=120

test:
  stage: test
  image: python:3.10
  script:
    - pip install pytest pytest-cov
    - pip install -r requirements.txt
    - pytest tests/ -v --cov=src
  coverage: '/TOTAL.*\\s+(\\d+%)/'

security:
  stage: security
  image: python:3.10
  script:
    - pip install bandit
    - bandit -r src/ -ll
  allow_failure: true
'''
    
    @staticmethod
    def generate_azure_pipelines() -> str:
        """Generate Azure Pipelines configuration."""
        return '''trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

strategy:
  matrix:
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(python.version)'

- script: |
    python -m pip install --upgrade pip
    pip install flake8 black isort mypy bandit pytest pytest-cov
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    black --check src/
    isort --check-only src/
    flake8 src/ --max-line-length=120
  displayName: 'Code quality checks'

- script: |
    pytest tests/ -v --cov=src --cov-report=xml
  displayName: 'Run tests'

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: Cobertura
    summaryFileLocation: '$(System.DefaultWorkingDirectory)/coverage.xml'
'''


def run_quality_suite(project_root: Optional[str] = None) -> QualitySuiteResult:
    """Run full quality suite."""
    runner = QualitySuiteRunner(project_root)
    return runner.run_all()


def generate_ci_config(provider: CIProvider, output_dir: str) -> str:
    """Generate CI configuration for specified provider."""
    if provider == CIProvider.GITHUB_ACTIONS:
        CIConfigGenerator.generate_github_actions(output_dir)
        return "GitHub Actions workflows generated"
    elif provider == CIProvider.GITLAB_CI:
        content = CIConfigGenerator.generate_gitlab_ci()
        filepath = os.path.join(output_dir, ".gitlab-ci.yml")
        with open(filepath, 'w') as f:
            f.write(content)
        return content
    elif provider == CIProvider.AZURE_DEVOPS:
        content = CIConfigGenerator.generate_azure_pipelines()
        filepath = os.path.join(output_dir, "azure-pipelines.yml")
        with open(filepath, 'w') as f:
            f.write(content)
        return content
    else:
        return ""


def generate_quality_report(result: QualitySuiteResult) -> str:
    """Generate quality suite report in markdown format."""
    lines = [
        "# Quality Suite Report",
        "",
        f"**Started:** {result.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Completed:** {result.completed_at.strftime('%Y-%m-%d %H:%M:%S') if result.completed_at else 'N/A'}",
        f"**Duration:** {result.total_duration_ms:.2f}ms",
        "",
        "## Summary",
        "",
        f"- **Total Checks:** {result.total_checks}",
        f"- **Passed:** {result.passed_checks}",
        f"- **Failed:** {result.failed_checks}",
        f"- **Status:** {'PASSED' if result.all_passed else 'FAILED'}",
        "",
        "## Check Results",
        "",
    ]
    
    for check in result.checks:
        status_icon = "PASS" if check.passed else "FAIL"
        lines.append(f"### {check.check_type.value.upper()} - {status_icon}")
        lines.append("")
        lines.append(f"- **Duration:** {check.duration_ms:.2f}ms")
        lines.append(f"- **Exit Code:** {check.exit_code}")
        if check.metrics:
            lines.append(f"- **Metrics:** {json.dumps(check.metrics)}")
        lines.append("")
    
    return "\n".join(lines)
