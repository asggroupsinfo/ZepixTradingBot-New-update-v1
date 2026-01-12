"""
Developer Setup Manager for V5 Hybrid Plugin Architecture.

This module provides automated developer environment setup:
- Environment setup scripts generation
- Dependency management
- VS Code configuration
- Git hooks installation
- Onboarding checklist verification

Based on Document 15: DEVELOPER_ONBOARDING.md

Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import json
import subprocess
import platform
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime


class SetupStep(Enum):
    """Setup steps for developer onboarding."""
    CLONE_REPO = "clone_repo"
    CREATE_VENV = "create_venv"
    INSTALL_DEPS = "install_deps"
    COPY_CONFIG = "copy_config"
    SETUP_MT5 = "setup_mt5"
    CREATE_BOTS = "create_bots"
    INSTALL_HOOKS = "install_hooks"
    VERIFY_SETUP = "verify_setup"


class SetupStatus(Enum):
    """Status of a setup step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SetupResult:
    """Result of a setup step."""
    step: SetupStep
    status: SetupStatus
    message: str
    duration_ms: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step": self.step.value,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "error": self.error
        }


@dataclass
class OnboardingChecklist:
    """Developer onboarding checklist."""
    items: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_item(self, name: str, description: str, completed: bool = False) -> None:
        """Add item to checklist."""
        self.items.append({
            "name": name,
            "description": description,
            "completed": completed
        })
    
    def mark_completed(self, name: str) -> None:
        """Mark item as completed."""
        for item in self.items:
            if item["name"] == name:
                item["completed"] = True
                break
    
    def get_progress(self) -> Tuple[int, int]:
        """Get progress (completed, total)."""
        completed = sum(1 for item in self.items if item["completed"])
        return completed, len(self.items)
    
    def is_complete(self) -> bool:
        """Check if all items are complete."""
        return all(item["completed"] for item in self.items)
    
    def to_markdown(self) -> str:
        """Convert to markdown checklist."""
        lines = ["## Developer Onboarding Checklist", ""]
        for item in self.items:
            checkbox = "[x]" if item["completed"] else "[ ]"
            lines.append(f"- {checkbox} **{item['name']}**: {item['description']}")
        
        completed, total = self.get_progress()
        lines.append("")
        lines.append(f"**Progress:** {completed}/{total} ({100*completed//total if total > 0 else 0}%)")
        
        return "\n".join(lines)


class SetupScriptGenerator:
    """Generator for setup scripts."""
    
    BASH_SCRIPT = '''#!/bin/bash
# Zepix Trading Bot - Developer Setup Script
# Version: 1.0
# Date: 2026-01-12

set -e

echo "=========================================="
echo "  Zepix Trading Bot - Developer Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_status "Python $PYTHON_VERSION detected"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Dependencies installed"
else
    print_warning "requirements.txt not found"
fi

# Copy config template
echo ""
echo "Setting up configuration..."
if [ ! -f "config/config.json" ]; then
    if [ -f "config/config.template.json" ]; then
        cp config/config.template.json config/config.json
        print_status "Config template copied"
    else
        print_warning "Config template not found"
    fi
else
    print_warning "config.json already exists"
fi

# Install pre-commit hooks
echo ""
echo "Installing Git hooks..."
if [ -d ".git" ]; then
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        print_status "Pre-commit hooks installed"
    else
        print_warning "pre-commit not installed, skipping hooks"
    fi
else
    print_warning "Not a Git repository, skipping hooks"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs data config
print_status "Directories created"

# Verify setup
echo ""
echo "Verifying setup..."
python3 -c "import sys; print(f'Python: {sys.version}')"
print_status "Setup verification complete"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit config/config.json with your credentials"
echo "  2. Setup MT5 demo account"
echo "  3. Create Telegram bots via @BotFather"
echo "  4. Run: python src/main.py"
echo ""
'''
    
    BATCH_SCRIPT = '''@echo off
REM Zepix Trading Bot - Developer Setup Script (Windows)
REM Version: 1.0
REM Date: 2026-01-12

echo ==========================================
echo   Zepix Trading Bot - Developer Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    exit /b 1
)
echo [OK] Python detected

REM Create virtual environment
echo.
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [WARN] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\\Scripts\\activate.bat
echo [OK] Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip > nul 2>&1
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [OK] Dependencies installed
) else (
    echo [WARN] requirements.txt not found
)

REM Copy config template
echo.
echo Setting up configuration...
if not exist "config\\config.json" (
    if exist "config\\config.template.json" (
        copy config\\config.template.json config\\config.json > nul
        echo [OK] Config template copied
    ) else (
        echo [WARN] Config template not found
    )
) else (
    echo [WARN] config.json already exists
)

REM Create necessary directories
echo.
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "config" mkdir config
echo [OK] Directories created

REM Verify setup
echo.
echo Verifying setup...
python -c "import sys; print(f'Python: {sys.version}')"
echo [OK] Setup verification complete

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo   1. Edit config\\config.json with your credentials
echo   2. Setup MT5 demo account
echo   3. Create Telegram bots via @BotFather
echo   4. Run: python src\\main.py
echo.
'''
    
    @classmethod
    def generate_bash_script(cls) -> str:
        """Generate bash setup script."""
        return cls.BASH_SCRIPT
    
    @classmethod
    def generate_batch_script(cls) -> str:
        """Generate Windows batch setup script."""
        return cls.BATCH_SCRIPT
    
    @classmethod
    def save_scripts(cls, output_dir: str) -> Dict[str, str]:
        """Save setup scripts to directory."""
        os.makedirs(output_dir, exist_ok=True)
        
        scripts = {}
        
        bash_path = os.path.join(output_dir, "setup_dev.sh")
        with open(bash_path, 'w', newline='\n') as f:
            f.write(cls.BASH_SCRIPT)
        scripts["setup_dev.sh"] = bash_path
        
        batch_path = os.path.join(output_dir, "setup_dev.bat")
        with open(batch_path, 'w', newline='\r\n') as f:
            f.write(cls.BATCH_SCRIPT)
        scripts["setup_dev.bat"] = batch_path
        
        return scripts


class VSCodeConfigGenerator:
    """Generator for VS Code configuration files."""
    
    SETTINGS = {
        "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
        "python.formatting.provider": "black",
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.linting.flake8Enabled": True,
        "python.linting.mypyEnabled": True,
        "python.testing.pytestEnabled": True,
        "python.testing.pytestArgs": ["tests"],
        "editor.formatOnSave": True,
        "editor.rulers": [88, 120],
        "files.trimTrailingWhitespace": True,
        "files.insertFinalNewline": True,
        "[python]": {
            "editor.tabSize": 4,
            "editor.insertSpaces": True
        }
    }
    
    LAUNCH = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Run Bot",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/src/main.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            },
            {
                "name": "Run Tests",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "-v"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            },
            {
                "name": "Debug Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal"
            }
        ]
    }
    
    EXTENSIONS = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.black-formatter",
            "ms-python.isort",
            "ms-python.flake8",
            "ms-python.mypy-type-checker",
            "charliermarsh.ruff",
            "eamodio.gitlens",
            "usernamehw.errorlens",
            "gruntfuggly.todo-tree",
            "streetsidesoftware.code-spell-checker"
        ]
    }
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """Get VS Code settings."""
        return cls.SETTINGS.copy()
    
    @classmethod
    def get_launch_config(cls) -> Dict[str, Any]:
        """Get VS Code launch configuration."""
        return cls.LAUNCH.copy()
    
    @classmethod
    def get_extensions(cls) -> Dict[str, Any]:
        """Get VS Code extensions recommendations."""
        return cls.EXTENSIONS.copy()
    
    @classmethod
    def save_configs(cls, vscode_dir: str) -> Dict[str, str]:
        """Save VS Code configuration files."""
        os.makedirs(vscode_dir, exist_ok=True)
        
        configs = {}
        
        settings_path = os.path.join(vscode_dir, "settings.json")
        with open(settings_path, 'w') as f:
            json.dump(cls.SETTINGS, f, indent=4)
        configs["settings.json"] = settings_path
        
        launch_path = os.path.join(vscode_dir, "launch.json")
        with open(launch_path, 'w') as f:
            json.dump(cls.LAUNCH, f, indent=4)
        configs["launch.json"] = launch_path
        
        extensions_path = os.path.join(vscode_dir, "extensions.json")
        with open(extensions_path, 'w') as f:
            json.dump(cls.EXTENSIONS, f, indent=4)
        configs["extensions.json"] = extensions_path
        
        return configs


class GitHooksManager:
    """Manager for Git hooks."""
    
    PRE_COMMIT_HOOK = '''#!/bin/bash
# Pre-commit hook for Zepix Trading Bot
# Runs linting and type checking before commit

echo "Running pre-commit checks..."

# Run black check
echo "Checking code formatting with Black..."
black --check src/ tests/ 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Code formatting issues found. Run 'black src/ tests/' to fix."
    exit 1
fi

# Run isort check
echo "Checking import sorting with isort..."
isort --check-only src/ tests/ 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Import sorting issues found. Run 'isort src/ tests/' to fix."
    exit 1
fi

# Run flake8
echo "Running flake8 linting..."
flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Flake8 found some issues."
fi

# Run mypy (optional, don't fail on errors)
echo "Running mypy type checking..."
mypy src/ --ignore-missing-imports 2>/dev/null || true

echo "Pre-commit checks passed!"
exit 0
'''
    
    PRE_PUSH_HOOK = '''#!/bin/bash
# Pre-push hook for Zepix Trading Bot
# Runs tests before push

echo "Running pre-push checks..."

# Run tests
echo "Running pytest..."
pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
    echo "ERROR: Tests failed. Fix tests before pushing."
    exit 1
fi

echo "Pre-push checks passed!"
exit 0
'''
    
    COMMIT_MSG_HOOK = '''#!/bin/bash
# Commit message hook for Zepix Trading Bot
# Validates commit message format

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check minimum length
if [ ${#COMMIT_MSG} -lt 10 ]; then
    echo "ERROR: Commit message too short (min 10 characters)"
    exit 1
fi

# Check for conventional commit format (optional)
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .+"; then
    echo "WARNING: Consider using conventional commit format:"
    echo "  feat: add new feature"
    echo "  fix: fix a bug"
    echo "  docs: documentation changes"
    echo "  test: add or modify tests"
fi

exit 0
'''
    
    PRE_COMMIT_CONFIG = '''# Pre-commit configuration for Zepix Trading Bot
# See https://pre-commit.com for more information

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=120", "--ignore=E501,W503"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: []
        args: ["--ignore-missing-imports"]
'''
    
    @classmethod
    def get_pre_commit_hook(cls) -> str:
        """Get pre-commit hook script."""
        return cls.PRE_COMMIT_HOOK
    
    @classmethod
    def get_pre_push_hook(cls) -> str:
        """Get pre-push hook script."""
        return cls.PRE_PUSH_HOOK
    
    @classmethod
    def get_commit_msg_hook(cls) -> str:
        """Get commit-msg hook script."""
        return cls.COMMIT_MSG_HOOK
    
    @classmethod
    def get_pre_commit_config(cls) -> str:
        """Get pre-commit configuration."""
        return cls.PRE_COMMIT_CONFIG
    
    @classmethod
    def save_hooks(cls, project_root: str) -> Dict[str, str]:
        """Save Git hooks to project."""
        hooks = {}
        
        pre_commit_config_path = os.path.join(project_root, ".pre-commit-config.yaml")
        with open(pre_commit_config_path, 'w') as f:
            f.write(cls.PRE_COMMIT_CONFIG)
        hooks[".pre-commit-config.yaml"] = pre_commit_config_path
        
        return hooks


class DevContainerGenerator:
    """Generator for DevContainer configuration."""
    
    DEVCONTAINER_JSON = {
        "name": "Zepix Trading Bot Dev",
        "image": "mcr.microsoft.com/devcontainers/python:3.11",
        "features": {
            "ghcr.io/devcontainers/features/git:1": {}
        },
        "customizations": {
            "vscode": {
                "extensions": [
                    "ms-python.python",
                    "ms-python.vscode-pylance",
                    "ms-python.black-formatter",
                    "ms-python.isort",
                    "ms-python.flake8",
                    "ms-python.mypy-type-checker",
                    "eamodio.gitlens"
                ],
                "settings": {
                    "python.defaultInterpreterPath": "/usr/local/bin/python",
                    "python.formatting.provider": "black",
                    "python.linting.enabled": True
                }
            }
        },
        "postCreateCommand": "pip install -r requirements.txt",
        "forwardPorts": [8000],
        "remoteUser": "vscode"
    }
    
    DOCKERFILE = '''# Zepix Trading Bot Development Container
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install development tools
RUN pip install --no-cache-dir \\
    black \\
    isort \\
    flake8 \\
    mypy \\
    pytest \\
    pre-commit

# Set environment variables
ENV PYTHONPATH=/workspace/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
'''
    
    @classmethod
    def get_devcontainer_json(cls) -> Dict[str, Any]:
        """Get devcontainer.json configuration."""
        return cls.DEVCONTAINER_JSON.copy()
    
    @classmethod
    def get_dockerfile(cls) -> str:
        """Get Dockerfile content."""
        return cls.DOCKERFILE
    
    @classmethod
    def save_configs(cls, devcontainer_dir: str) -> Dict[str, str]:
        """Save DevContainer configuration files."""
        os.makedirs(devcontainer_dir, exist_ok=True)
        
        configs = {}
        
        json_path = os.path.join(devcontainer_dir, "devcontainer.json")
        with open(json_path, 'w') as f:
            json.dump(cls.DEVCONTAINER_JSON, f, indent=4)
        configs["devcontainer.json"] = json_path
        
        dockerfile_path = os.path.join(devcontainer_dir, "Dockerfile")
        with open(dockerfile_path, 'w') as f:
            f.write(cls.DOCKERFILE)
        configs["Dockerfile"] = dockerfile_path
        
        return configs


class OnboardingChecklistGenerator:
    """Generator for onboarding checklists."""
    
    DEFAULT_ITEMS = [
        ("dev_environment", "Development environment setup", False),
        ("bot_runs", "Bot runs successfully", False),
        ("understand_architecture", "Understand plugin architecture", False),
        ("created_plugin", "Created first plugin", False),
        ("wrote_tests", "Wrote unit tests", False),
        ("read_guidelines", "Read code review guidelines", False),
        ("joined_community", "Joined developer community", False),
    ]
    
    @classmethod
    def create_default_checklist(cls) -> OnboardingChecklist:
        """Create default onboarding checklist."""
        checklist = OnboardingChecklist()
        for name, description, completed in cls.DEFAULT_ITEMS:
            checklist.add_item(name, description, completed)
        return checklist
    
    @classmethod
    def get_checklist_items(cls) -> List[Tuple[str, str, bool]]:
        """Get default checklist items."""
        return cls.DEFAULT_ITEMS.copy()


class EnvironmentVerifier:
    """Verifier for development environment."""
    
    @staticmethod
    def check_python_version() -> Tuple[bool, str]:
        """Check Python version."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        return False, f"Python 3.9+ required, found {version.major}.{version.minor}"
    
    @staticmethod
    def check_venv() -> Tuple[bool, str]:
        """Check if running in virtual environment."""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            return True, "Virtual environment active"
        return False, "Not in virtual environment"
    
    @staticmethod
    def check_git() -> Tuple[bool, str]:
        """Check if Git is available."""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, "Git not found"
        except FileNotFoundError:
            return False, "Git not installed"
    
    @staticmethod
    def check_directory_structure(project_root: str) -> Tuple[bool, str]:
        """Check if directory structure is correct."""
        required_dirs = ['src', 'config', 'tests']
        missing = []
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(project_root, dir_name)):
                missing.append(dir_name)
        
        if missing:
            return False, f"Missing directories: {', '.join(missing)}"
        return True, "Directory structure OK"
    
    @classmethod
    def run_all_checks(cls, project_root: Optional[str] = None) -> List[Dict[str, Any]]:
        """Run all environment checks."""
        project_root = project_root or os.getcwd()
        
        checks = []
        
        passed, message = cls.check_python_version()
        checks.append({"name": "Python Version", "passed": passed, "message": message})
        
        passed, message = cls.check_venv()
        checks.append({"name": "Virtual Environment", "passed": passed, "message": message})
        
        passed, message = cls.check_git()
        checks.append({"name": "Git", "passed": passed, "message": message})
        
        passed, message = cls.check_directory_structure(project_root)
        checks.append({"name": "Directory Structure", "passed": passed, "message": message})
        
        return checks


class DeveloperSetupManager:
    """Main manager for developer setup."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize setup manager."""
        self.project_root = project_root or os.getcwd()
    
    def generate_all_configs(self) -> Dict[str, Dict[str, str]]:
        """Generate all configuration files."""
        generated = {}
        
        scripts_dir = os.path.join(self.project_root, "scripts")
        generated["scripts"] = SetupScriptGenerator.save_scripts(scripts_dir)
        
        vscode_dir = os.path.join(self.project_root, ".vscode")
        generated["vscode"] = VSCodeConfigGenerator.save_configs(vscode_dir)
        
        generated["hooks"] = GitHooksManager.save_hooks(self.project_root)
        
        devcontainer_dir = os.path.join(self.project_root, ".devcontainer")
        generated["devcontainer"] = DevContainerGenerator.save_configs(devcontainer_dir)
        
        return generated
    
    def verify_environment(self) -> List[Dict[str, Any]]:
        """Verify development environment."""
        return EnvironmentVerifier.run_all_checks(self.project_root)
    
    def create_onboarding_checklist(self) -> OnboardingChecklist:
        """Create onboarding checklist."""
        return OnboardingChecklistGenerator.create_default_checklist()


def setup_developer_environment(project_root: Optional[str] = None) -> Dict[str, Any]:
    """Setup developer environment."""
    manager = DeveloperSetupManager(project_root)
    
    result = {
        "generated": manager.generate_all_configs(),
        "checks": manager.verify_environment(),
        "checklist": manager.create_onboarding_checklist().to_markdown()
    }
    
    return result
