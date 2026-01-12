"""
Security Scanning Integration for V5 Hybrid Plugin Architecture.

This module provides security scanning tools:
- Bandit security scanner integration
- Secret detection
- SQL injection detection
- Plugin sandboxing verification
- Security report generation

Based on Document 13: CODE_REVIEW_GUIDELINES.md

Version: 1.0
Date: 2026-01-12
"""

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from datetime import datetime
import json


class SecuritySeverity(Enum):
    """Security issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityCategory(Enum):
    """Security issue categories."""
    HARDCODED_SECRET = "hardcoded_secret"
    SQL_INJECTION = "sql_injection"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_IMPORT = "insecure_import"
    SUBPROCESS_CALL = "subprocess_call"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    DEBUG_CODE = "debug_code"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"


@dataclass
class SecurityIssue:
    """Single security issue."""
    file_path: str
    line: int
    column: int
    code: str
    message: str
    severity: SecuritySeverity
    category: SecurityCategory
    confidence: str = "HIGH"
    cwe_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "confidence": self.confidence,
            "cwe_id": self.cwe_id
        }


@dataclass
class SecurityScanResult:
    """Result of security scan."""
    issues: List[SecurityIssue] = field(default_factory=list)
    passed: bool = True
    files_scanned: int = 0
    duration_ms: float = 0.0
    scanner: str = "custom"
    
    @property
    def critical_count(self) -> int:
        """Get number of critical issues."""
        return sum(1 for i in self.issues if i.severity == SecuritySeverity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        """Get number of high severity issues."""
        return sum(1 for i in self.issues if i.severity == SecuritySeverity.HIGH)
    
    @property
    def medium_count(self) -> int:
        """Get number of medium severity issues."""
        return sum(1 for i in self.issues if i.severity == SecuritySeverity.MEDIUM)
    
    @property
    def low_count(self) -> int:
        """Get number of low severity issues."""
        return sum(1 for i in self.issues if i.severity == SecuritySeverity.LOW)
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues."""
        return self.critical_count > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "files_scanned": self.files_scanned,
            "duration_ms": self.duration_ms,
            "scanner": self.scanner,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "total_issues": len(self.issues),
            "issues": [i.to_dict() for i in self.issues]
        }


class SecretPatterns:
    """Patterns for detecting hardcoded secrets."""
    
    PATTERNS = {
        "api_key": (
            r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}["\']?',
            SecuritySeverity.CRITICAL,
            "Potential API key detected"
        ),
        "password": (
            r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']',
            SecuritySeverity.CRITICAL,
            "Potential hardcoded password detected"
        ),
        "secret_key": (
            r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{16,}["\']?',
            SecuritySeverity.CRITICAL,
            "Potential secret key detected"
        ),
        "token": (
            r'(?i)(token|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\']?[a-zA-Z0-9_\-\.]{20,}["\']?',
            SecuritySeverity.CRITICAL,
            "Potential token detected"
        ),
        "private_key": (
            r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
            SecuritySeverity.CRITICAL,
            "Private key detected"
        ),
        "aws_key": (
            r'(?i)AKIA[0-9A-Z]{16}',
            SecuritySeverity.CRITICAL,
            "AWS access key detected"
        ),
        "telegram_token": (
            r'\d{9,10}:[a-zA-Z0-9_-]{35}',
            SecuritySeverity.CRITICAL,
            "Telegram bot token detected"
        ),
        "connection_string": (
            r'(?i)(mongodb|mysql|postgres|redis)://[^\s]+',
            SecuritySeverity.HIGH,
            "Database connection string detected"
        ),
    }
    
    @classmethod
    def get_patterns(cls) -> Dict[str, tuple]:
        """Get all secret patterns."""
        return cls.PATTERNS.copy()
    
    @classmethod
    def scan_content(cls, content: str, file_path: str) -> List[SecurityIssue]:
        """Scan content for secrets."""
        issues = []
        lines = content.split('\n')
        
        for pattern_name, (pattern, severity, message) in cls.PATTERNS.items():
            for line_num, line in enumerate(lines, 1):
                if line.strip().startswith('#'):
                    continue
                
                matches = re.finditer(pattern, line)
                for match in matches:
                    issues.append(SecurityIssue(
                        file_path=file_path,
                        line=line_num,
                        column=match.start(),
                        code=pattern_name.upper(),
                        message=message,
                        severity=severity,
                        category=SecurityCategory.HARDCODED_SECRET,
                        confidence="HIGH"
                    ))
        
        return issues


class SQLInjectionDetector:
    """Detector for SQL injection vulnerabilities."""
    
    DANGEROUS_PATTERNS = [
        (r'execute\s*\(\s*["\'].*%s.*["\']', "String formatting in SQL query"),
        (r'execute\s*\(\s*f["\']', "F-string in SQL query"),
        (r'execute\s*\(\s*["\'].*\+', "String concatenation in SQL query"),
        (r'execute\s*\(\s*["\'].*\.format\(', ".format() in SQL query"),
        (r'cursor\.execute\s*\(\s*["\'].*%', "Unsafe parameter substitution"),
    ]
    
    SAFE_PATTERNS = [
        r'execute\s*\(\s*["\'][^"\']*\?\s*["\']',
        r'execute\s*\(\s*["\'][^"\']*%s["\'],\s*\(',
    ]
    
    @classmethod
    def scan_content(cls, content: str, file_path: str) -> List[SecurityIssue]:
        """Scan content for SQL injection vulnerabilities."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            for pattern, message in cls.DANGEROUS_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    is_safe = any(re.search(safe, line) for safe in cls.SAFE_PATTERNS)
                    if not is_safe:
                        issues.append(SecurityIssue(
                            file_path=file_path,
                            line=line_num,
                            column=0,
                            code="SQL_INJECTION",
                            message=message,
                            severity=SecuritySeverity.CRITICAL,
                            category=SecurityCategory.SQL_INJECTION,
                            confidence="MEDIUM",
                            cwe_id="CWE-89"
                        ))
        
        return issues


class PluginSandboxChecker:
    """Checker for plugin sandboxing violations."""
    
    FORBIDDEN_IMPORTS = {
        "os": ("Forbidden import: os module", SecuritySeverity.HIGH),
        "sys": ("Forbidden import: sys module", SecuritySeverity.HIGH),
        "subprocess": ("Forbidden import: subprocess module", SecuritySeverity.CRITICAL),
        "shutil": ("Forbidden import: shutil module", SecuritySeverity.HIGH),
        "socket": ("Forbidden import: socket module", SecuritySeverity.HIGH),
        "requests": ("Forbidden import: requests module (use ServiceAPI)", SecuritySeverity.MEDIUM),
        "urllib": ("Forbidden import: urllib module (use ServiceAPI)", SecuritySeverity.MEDIUM),
        "httpx": ("Forbidden import: httpx module (use ServiceAPI)", SecuritySeverity.MEDIUM),
        "aiohttp": ("Forbidden import: aiohttp module (use ServiceAPI)", SecuritySeverity.MEDIUM),
    }
    
    DANGEROUS_CALLS = [
        (r'os\.(system|popen|exec|spawn)', "Dangerous os call", SecuritySeverity.CRITICAL),
        (r'subprocess\.(run|call|Popen|check_output)', "Subprocess call", SecuritySeverity.CRITICAL),
        (r'eval\s*\(', "Eval call", SecuritySeverity.CRITICAL),
        (r'exec\s*\(', "Exec call", SecuritySeverity.CRITICAL),
        (r'compile\s*\(', "Compile call", SecuritySeverity.HIGH),
        (r'__import__\s*\(', "Dynamic import", SecuritySeverity.HIGH),
        (r'open\s*\([^)]*["\'][wax]', "File write operation", SecuritySeverity.MEDIUM),
        (r'pickle\.load', "Pickle deserialization", SecuritySeverity.HIGH),
    ]
    
    @classmethod
    def scan_content(cls, content: str, file_path: str, is_plugin: bool = False) -> List[SecurityIssue]:
        """Scan content for sandboxing violations."""
        issues = []
        lines = content.split('\n')
        
        if not is_plugin:
            return issues
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            import_match = re.match(r'^\s*(from\s+(\w+)|import\s+(\w+))', line)
            if import_match:
                module = import_match.group(2) or import_match.group(3)
                if module in cls.FORBIDDEN_IMPORTS:
                    message, severity = cls.FORBIDDEN_IMPORTS[module]
                    issues.append(SecurityIssue(
                        file_path=file_path,
                        line=line_num,
                        column=0,
                        code="FORBIDDEN_IMPORT",
                        message=message,
                        severity=severity,
                        category=SecurityCategory.INSECURE_IMPORT,
                        confidence="HIGH"
                    ))
            
            for pattern, message, severity in cls.DANGEROUS_CALLS:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        file_path=file_path,
                        line=line_num,
                        column=0,
                        code="DANGEROUS_CALL",
                        message=message,
                        severity=severity,
                        category=SecurityCategory.COMMAND_INJECTION,
                        confidence="HIGH"
                    ))
        
        return issues


class SensitiveDataChecker:
    """Checker for sensitive data exposure."""
    
    LOGGING_PATTERNS = [
        (r'(log|print|logger)\s*\.\s*(info|debug|warning|error)\s*\([^)]*password', "Password in log"),
        (r'(log|print|logger)\s*\.\s*(info|debug|warning|error)\s*\([^)]*token', "Token in log"),
        (r'(log|print|logger)\s*\.\s*(info|debug|warning|error)\s*\([^)]*secret', "Secret in log"),
        (r'(log|print|logger)\s*\.\s*(info|debug|warning|error)\s*\([^)]*api[_-]?key', "API key in log"),
        (r'print\s*\([^)]*password', "Password in print"),
        (r'print\s*\([^)]*token', "Token in print"),
    ]
    
    @classmethod
    def scan_content(cls, content: str, file_path: str) -> List[SecurityIssue]:
        """Scan content for sensitive data exposure."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            for pattern, message in cls.LOGGING_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        file_path=file_path,
                        line=line_num,
                        column=0,
                        code="SENSITIVE_DATA_LOG",
                        message=message,
                        severity=SecuritySeverity.HIGH,
                        category=SecurityCategory.SENSITIVE_DATA_EXPOSURE,
                        confidence="MEDIUM"
                    ))
        
        return issues


class SecurityScanner:
    """Main security scanner."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize scanner."""
        self.project_root = project_root or os.getcwd()
    
    def scan_file(self, file_path: str, is_plugin: bool = False) -> List[SecurityIssue]:
        """Scan a single file for security issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues.extend(SecretPatterns.scan_content(content, file_path))
            issues.extend(SQLInjectionDetector.scan_content(content, file_path))
            issues.extend(PluginSandboxChecker.scan_content(content, file_path, is_plugin))
            issues.extend(SensitiveDataChecker.scan_content(content, file_path))
            
        except Exception:
            pass
        
        return issues
    
    def scan_directory(
        self, 
        directory: str, 
        exclude_patterns: Optional[List[str]] = None,
        plugin_dirs: Optional[List[str]] = None
    ) -> SecurityScanResult:
        """Scan directory for security issues."""
        exclude_patterns = exclude_patterns or ["__pycache__", ".venv", "venv", "migrations"]
        plugin_dirs = plugin_dirs or ["logic_plugins"]
        
        start_time = datetime.now()
        result = SecurityScanResult(scanner="custom")
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            is_plugin_dir = any(pd in root for pd in plugin_dirs)
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    issues = self.scan_file(file_path, is_plugin=is_plugin_dir)
                    result.issues.extend(issues)
                    result.files_scanned += 1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        result.passed = not result.has_critical_issues
        
        return result
    
    def scan_project(self) -> SecurityScanResult:
        """Scan entire project for security issues."""
        src_dir = os.path.join(self.project_root, "src")
        if os.path.exists(src_dir):
            return self.scan_directory(src_dir)
        return self.scan_directory(self.project_root)
    
    def quick_scan(self, file_paths: List[str]) -> SecurityScanResult:
        """Quick scan of specific files."""
        start_time = datetime.now()
        result = SecurityScanResult(scanner="custom_quick")
        
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path.endswith('.py'):
                is_plugin = "logic_plugins" in file_path
                issues = self.scan_file(file_path, is_plugin=is_plugin)
                result.issues.extend(issues)
                result.files_scanned += 1
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        result.passed = not result.has_critical_issues
        
        return result


class BanditRunner:
    """Runner for Bandit security scanner."""
    
    DEFAULT_CONFIG = {
        "skips": ["B101"],
        "exclude_dirs": [".venv", "venv", "tests", "__pycache__"],
        "severity": "low",
        "confidence": "low",
    }
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize Bandit runner."""
        self.project_root = project_root or os.getcwd()
    
    def run(self, paths: Optional[List[str]] = None, severity: str = "low") -> SecurityScanResult:
        """Run Bandit security scanner."""
        paths = paths or [os.path.join(self.project_root, "src")]
        start_time = datetime.now()
        result = SecurityScanResult(scanner="bandit")
        
        try:
            cmd = [
                sys.executable, "-m", "bandit",
                "-r", "-f", "json",
                f"--severity-level={severity}",
            ]
            cmd.extend(paths)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if proc.stdout:
                data = json.loads(proc.stdout)
                result.issues = self._parse_bandit_output(data)
                result.files_scanned = data.get("metrics", {}).get("_totals", {}).get("loc", 0)
            
            result.passed = proc.returncode == 0
            
        except subprocess.TimeoutExpired:
            result.passed = False
        except Exception:
            result.passed = False
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def _parse_bandit_output(self, data: Dict[str, Any]) -> List[SecurityIssue]:
        """Parse Bandit JSON output into security issues."""
        issues = []
        
        severity_map = {
            "HIGH": SecuritySeverity.HIGH,
            "MEDIUM": SecuritySeverity.MEDIUM,
            "LOW": SecuritySeverity.LOW,
        }
        
        for result in data.get("results", []):
            severity = severity_map.get(result.get("issue_severity", "LOW"), SecuritySeverity.LOW)
            
            issues.append(SecurityIssue(
                file_path=result.get("filename", ""),
                line=result.get("line_number", 0),
                column=result.get("col_offset", 0),
                code=result.get("test_id", ""),
                message=result.get("issue_text", ""),
                severity=severity,
                category=SecurityCategory.INSECURE_IMPORT,
                confidence=result.get("issue_confidence", "MEDIUM"),
                cwe_id=result.get("cwe", {}).get("id")
            ))
        
        return issues
    
    @classmethod
    def generate_config(cls) -> str:
        """Generate Bandit configuration for pyproject.toml."""
        lines = [
            "[tool.bandit]",
            f'skips = {json.dumps(cls.DEFAULT_CONFIG["skips"])}',
            f'exclude_dirs = {json.dumps(cls.DEFAULT_CONFIG["exclude_dirs"])}',
        ]
        return "\n".join(lines)


def scan_security(project_root: Optional[str] = None) -> SecurityScanResult:
    """Scan project for security issues."""
    scanner = SecurityScanner(project_root)
    return scanner.scan_project()


def generate_security_report(result: SecurityScanResult) -> str:
    """Generate security report in markdown format."""
    lines = [
        "# Security Scan Report",
        "",
        f"**Scanner:** {result.scanner}",
        f"**Files Scanned:** {result.files_scanned}",
        f"**Duration:** {result.duration_ms:.2f}ms",
        f"**Status:** {'PASSED' if result.passed else 'FAILED'}",
        "",
        "## Summary",
        "",
        f"- **Critical:** {result.critical_count}",
        f"- **High:** {result.high_count}",
        f"- **Medium:** {result.medium_count}",
        f"- **Low:** {result.low_count}",
        f"- **Total:** {len(result.issues)}",
        "",
    ]
    
    if result.issues:
        lines.append("## Issues")
        lines.append("")
        
        for severity in [SecuritySeverity.CRITICAL, SecuritySeverity.HIGH, SecuritySeverity.MEDIUM, SecuritySeverity.LOW]:
            severity_issues = [i for i in result.issues if i.severity == severity]
            if severity_issues:
                lines.append(f"### {severity.value.upper()}")
                lines.append("")
                for issue in severity_issues:
                    lines.append(f"- **{issue.code}**: {issue.message}")
                    lines.append(f"  - File: {issue.file_path}:{issue.line}")
                    lines.append(f"  - Category: {issue.category.value}")
                lines.append("")
    
    return "\n".join(lines)
