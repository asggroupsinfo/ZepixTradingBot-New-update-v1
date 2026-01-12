"""
Pre-commit Hooks Configuration for V5 Hybrid Plugin Architecture.

This module provides pre-commit hook management:
- Pre-commit configuration generator
- Git hook installation
- Hook execution and validation

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


class HookStage(Enum):
    """Git hook stages."""
    PRE_COMMIT = "pre-commit"
    PRE_PUSH = "pre-push"
    COMMIT_MSG = "commit-msg"
    PREPARE_COMMIT_MSG = "prepare-commit-msg"


class HookStatus(Enum):
    """Hook execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class HookResult:
    """Result of a single hook execution."""
    hook_id: str
    name: str
    stage: HookStage
    status: HookStatus
    duration_ms: float = 0.0
    output: str = ""
    error: str = ""
    files_modified: List[str] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if hook passed."""
        return self.status == HookStatus.PASSED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hook_id": self.hook_id,
            "name": self.name,
            "stage": self.stage.value,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "output": self.output,
            "error": self.error,
            "files_modified": self.files_modified
        }


@dataclass
class PreCommitResult:
    """Result of pre-commit run."""
    hooks: List[HookResult] = field(default_factory=list)
    passed: bool = True
    total_duration_ms: float = 0.0
    
    @property
    def passed_count(self) -> int:
        """Get number of passed hooks."""
        return sum(1 for h in self.hooks if h.passed)
    
    @property
    def failed_count(self) -> int:
        """Get number of failed hooks."""
        return sum(1 for h in self.hooks if h.status == HookStatus.FAILED)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "total_duration_ms": self.total_duration_ms,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "hooks": [h.to_dict() for h in self.hooks]
        }


@dataclass
class PreCommitHook:
    """Pre-commit hook definition."""
    id: str
    name: str
    entry: str
    language: str = "python"
    types: List[str] = field(default_factory=lambda: ["python"])
    stages: List[str] = field(default_factory=lambda: ["commit"])
    args: List[str] = field(default_factory=list)
    exclude: str = ""
    pass_filenames: bool = True
    always_run: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML."""
        result = {
            "id": self.id,
            "name": self.name,
            "entry": self.entry,
            "language": self.language,
            "types": self.types,
        }
        
        if self.stages != ["commit"]:
            result["stages"] = self.stages
        if self.args:
            result["args"] = self.args
        if self.exclude:
            result["exclude"] = self.exclude
        if not self.pass_filenames:
            result["pass_filenames"] = False
        if self.always_run:
            result["always_run"] = True
        
        return result


@dataclass
class PreCommitRepo:
    """Pre-commit repository definition."""
    repo: str
    rev: str
    hooks: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML."""
        return {
            "repo": self.repo,
            "rev": self.rev,
            "hooks": self.hooks
        }


class PreCommitConfig:
    """Pre-commit configuration generator."""
    
    DEFAULT_REPOS = [
        PreCommitRepo(
            repo="https://github.com/pre-commit/pre-commit-hooks",
            rev="v4.5.0",
            hooks=[
                {"id": "trailing-whitespace"},
                {"id": "end-of-file-fixer"},
                {"id": "check-yaml"},
                {"id": "check-json"},
                {"id": "check-added-large-files", "args": ["--maxkb=1000"]},
                {"id": "check-merge-conflict"},
                {"id": "check-case-conflict"},
                {"id": "detect-private-key"},
                {"id": "debug-statements"},
                {"id": "check-docstring-first"},
            ]
        ),
        PreCommitRepo(
            repo="https://github.com/psf/black",
            rev="24.1.0",
            hooks=[
                {"id": "black", "args": ["--line-length=120"]}
            ]
        ),
        PreCommitRepo(
            repo="https://github.com/pycqa/isort",
            rev="5.13.2",
            hooks=[
                {"id": "isort", "args": ["--profile=black", "--line-length=120"]}
            ]
        ),
        PreCommitRepo(
            repo="https://github.com/pycqa/flake8",
            rev="7.0.0",
            hooks=[
                {"id": "flake8", "args": ["--max-line-length=120", "--ignore=E501,W503,E203"]}
            ]
        ),
        PreCommitRepo(
            repo="https://github.com/pre-commit/mirrors-mypy",
            rev="v1.8.0",
            hooks=[
                {"id": "mypy", "args": ["--ignore-missing-imports"], "additional_dependencies": []}
            ]
        ),
        PreCommitRepo(
            repo="https://github.com/PyCQA/bandit",
            rev="1.7.7",
            hooks=[
                {"id": "bandit", "args": ["-c", "pyproject.toml"], "additional_dependencies": ["bandit[toml]"]}
            ]
        ),
    ]
    
    LOCAL_HOOKS = [
        PreCommitHook(
            id="check-plugin-structure",
            name="Check Plugin Structure",
            entry="python -m src.code_quality.plugin_validator",
            language="system",
            types=["python"],
            pass_filenames=False,
            always_run=True
        ),
        PreCommitHook(
            id="check-no-hardcoded-secrets",
            name="Check No Hardcoded Secrets",
            entry="python -m src.code_quality.security_scanner --quick",
            language="system",
            types=["python"],
            pass_filenames=True
        ),
    ]
    
    @classmethod
    def generate_pre_commit_config(cls, include_local: bool = True) -> str:
        """Generate .pre-commit-config.yaml content."""
        lines = [
            "# Pre-commit configuration for V5 Hybrid Plugin Architecture",
            "# See https://pre-commit.com for more information",
            "",
            "default_stages: [commit]",
            "default_language_version:",
            "  python: python3.10",
            "",
            "repos:",
        ]
        
        for repo in cls.DEFAULT_REPOS:
            lines.append(f"  - repo: {repo.repo}")
            lines.append(f"    rev: {repo.rev}")
            lines.append("    hooks:")
            for hook in repo.hooks:
                lines.append(f"      - id: {hook['id']}")
                for key, value in hook.items():
                    if key == "id":
                        continue
                    if isinstance(value, list):
                        lines.append(f"        {key}:")
                        for item in value:
                            lines.append(f"          - {item}")
                    else:
                        lines.append(f"        {key}: {value}")
            lines.append("")
        
        if include_local and cls.LOCAL_HOOKS:
            lines.append("  - repo: local")
            lines.append("    hooks:")
            for hook in cls.LOCAL_HOOKS:
                lines.append(f"      - id: {hook.id}")
                lines.append(f"        name: {hook.name}")
                lines.append(f"        entry: {hook.entry}")
                lines.append(f"        language: {hook.language}")
                if hook.types:
                    lines.append(f"        types: [{', '.join(hook.types)}]")
                if not hook.pass_filenames:
                    lines.append("        pass_filenames: false")
                if hook.always_run:
                    lines.append("        always_run: true")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def get_repos(cls) -> List[PreCommitRepo]:
        """Get list of pre-commit repos."""
        return cls.DEFAULT_REPOS.copy()
    
    @classmethod
    def get_local_hooks(cls) -> List[PreCommitHook]:
        """Get list of local hooks."""
        return cls.LOCAL_HOOKS.copy()


class GitHookInstaller:
    """Installer for Git hooks."""
    
    PRE_COMMIT_HOOK = '''#!/bin/sh
# Pre-commit hook for V5 Hybrid Plugin Architecture
# This hook runs pre-commit framework

# Check if pre-commit is installed
if command -v pre-commit &> /dev/null; then
    pre-commit run --hook-stage commit
    exit $?
else
    echo "Warning: pre-commit not installed. Run: pip install pre-commit"
    exit 0
fi
'''
    
    PRE_PUSH_HOOK = '''#!/bin/sh
# Pre-push hook for V5 Hybrid Plugin Architecture
# This hook runs tests before push

# Run tests
python -m pytest tests/ -x -q
exit $?
'''
    
    COMMIT_MSG_HOOK = '''#!/bin/sh
# Commit message hook for V5 Hybrid Plugin Architecture
# This hook validates commit message format

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check commit message format
# Format: <type>: <description>
# Types: feat, fix, docs, style, refactor, test, chore

pattern="^(feat|fix|docs|style|refactor|test|chore|Document [0-9]+): .+"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "Error: Invalid commit message format"
    echo "Expected: <type>: <description>"
    echo "Types: feat, fix, docs, style, refactor, test, chore, Document N"
    exit 1
fi

exit 0
'''
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize Git hook installer."""
        self.project_root = project_root or os.getcwd()
        self.hooks_dir = os.path.join(self.project_root, ".git", "hooks")
    
    def install_pre_commit_hook(self) -> bool:
        """Install pre-commit hook."""
        return self._install_hook("pre-commit", self.PRE_COMMIT_HOOK)
    
    def install_pre_push_hook(self) -> bool:
        """Install pre-push hook."""
        return self._install_hook("pre-push", self.PRE_PUSH_HOOK)
    
    def install_commit_msg_hook(self) -> bool:
        """Install commit-msg hook."""
        return self._install_hook("commit-msg", self.COMMIT_MSG_HOOK)
    
    def install_all_hooks(self) -> Dict[str, bool]:
        """Install all Git hooks."""
        return {
            "pre-commit": self.install_pre_commit_hook(),
            "pre-push": self.install_pre_push_hook(),
            "commit-msg": self.install_commit_msg_hook(),
        }
    
    def _install_hook(self, hook_name: str, content: str) -> bool:
        """Install a single Git hook."""
        try:
            if not os.path.exists(self.hooks_dir):
                os.makedirs(self.hooks_dir)
            
            hook_path = os.path.join(self.hooks_dir, hook_name)
            with open(hook_path, 'w') as f:
                f.write(content)
            
            os.chmod(hook_path, 0o755)
            return True
            
        except Exception:
            return False
    
    def is_hook_installed(self, hook_name: str) -> bool:
        """Check if a hook is installed."""
        hook_path = os.path.join(self.hooks_dir, hook_name)
        return os.path.exists(hook_path) and os.access(hook_path, os.X_OK)
    
    def get_installed_hooks(self) -> List[str]:
        """Get list of installed hooks."""
        installed = []
        for hook in ["pre-commit", "pre-push", "commit-msg", "prepare-commit-msg"]:
            if self.is_hook_installed(hook):
                installed.append(hook)
        return installed


class PreCommitRunner:
    """Runner for pre-commit hooks."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize pre-commit runner."""
        self.project_root = project_root or os.getcwd()
    
    def run_all_hooks(self, files: Optional[List[str]] = None) -> PreCommitResult:
        """Run all pre-commit hooks."""
        start_time = datetime.now()
        result = PreCommitResult()
        
        try:
            cmd = [sys.executable, "-m", "pre_commit", "run", "--all-files"]
            if files:
                cmd = [sys.executable, "-m", "pre_commit", "run", "--files"] + files
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )
            
            result.passed = proc.returncode == 0
            result.hooks = self._parse_output(proc.stdout)
            
        except subprocess.TimeoutExpired:
            result.passed = False
        except Exception:
            result.passed = False
        
        result.total_duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_hook(self, hook_id: str, files: Optional[List[str]] = None) -> HookResult:
        """Run a specific hook."""
        start_time = datetime.now()
        
        try:
            cmd = [sys.executable, "-m", "pre_commit", "run", hook_id]
            if files:
                cmd.extend(["--files"] + files)
            else:
                cmd.append("--all-files")
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            status = HookStatus.PASSED if proc.returncode == 0 else HookStatus.FAILED
            
            return HookResult(
                hook_id=hook_id,
                name=hook_id,
                stage=HookStage.PRE_COMMIT,
                status=status,
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                output=proc.stdout,
                error=proc.stderr
            )
            
        except Exception as e:
            return HookResult(
                hook_id=hook_id,
                name=hook_id,
                stage=HookStage.PRE_COMMIT,
                status=HookStatus.ERROR,
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e)
            )
    
    def _parse_output(self, output: str) -> List[HookResult]:
        """Parse pre-commit output into hook results."""
        hooks = []
        
        for line in output.split("\n"):
            if "..." in line:
                parts = line.split("...")
                if len(parts) >= 2:
                    hook_name = parts[0].strip()
                    status_str = parts[-1].strip().lower()
                    
                    if "passed" in status_str:
                        status = HookStatus.PASSED
                    elif "failed" in status_str:
                        status = HookStatus.FAILED
                    elif "skipped" in status_str:
                        status = HookStatus.SKIPPED
                    else:
                        status = HookStatus.ERROR
                    
                    hooks.append(HookResult(
                        hook_id=hook_name.lower().replace(" ", "-"),
                        name=hook_name,
                        stage=HookStage.PRE_COMMIT,
                        status=status
                    ))
        
        return hooks
    
    def install_pre_commit(self) -> bool:
        """Install pre-commit hooks."""
        try:
            cmd = [sys.executable, "-m", "pre_commit", "install"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60
            )
            return proc.returncode == 0
        except Exception:
            return False
    
    def autoupdate(self) -> bool:
        """Update pre-commit hooks to latest versions."""
        try:
            cmd = [sys.executable, "-m", "pre_commit", "autoupdate"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )
            return proc.returncode == 0
        except Exception:
            return False


def generate_pre_commit_config(output_path: str, include_local: bool = True) -> str:
    """Generate pre-commit configuration file."""
    config = PreCommitConfig.generate_pre_commit_config(include_local)
    
    with open(output_path, 'w') as f:
        f.write(config)
    
    return config
