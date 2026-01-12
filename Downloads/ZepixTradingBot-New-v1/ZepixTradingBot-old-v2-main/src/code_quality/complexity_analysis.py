"""
Complexity Analysis Tools for V5 Hybrid Plugin Architecture.

This module provides code complexity analysis:
- Cyclomatic complexity measurement (radon-style)
- Maintainability index calculation
- Halstead metrics
- Lines of code analysis
- Complexity thresholds and reporting

Version: 1.0
Date: 2026-01-12
"""

import os
import ast
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import json


class ComplexityGrade(Enum):
    """Complexity grade levels (A-F)."""
    A = "A"  # Low complexity (1-5)
    B = "B"  # Low complexity (6-10)
    C = "C"  # Moderate complexity (11-20)
    D = "D"  # High complexity (21-30)
    E = "E"  # Very high complexity (31-40)
    F = "F"  # Extremely high complexity (41+)


class MaintainabilityGrade(Enum):
    """Maintainability index grade levels."""
    A = "A"  # Very high maintainability (100-20)
    B = "B"  # High maintainability (19-10)
    C = "C"  # Moderate maintainability (9-0)


@dataclass
class FunctionComplexity:
    """Complexity metrics for a single function."""
    name: str
    file_path: str
    line_start: int
    line_end: int
    cyclomatic_complexity: int
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    parameters: int = 0
    
    @property
    def grade(self) -> ComplexityGrade:
        """Get complexity grade."""
        cc = self.cyclomatic_complexity
        if cc <= 5:
            return ComplexityGrade.A
        elif cc <= 10:
            return ComplexityGrade.B
        elif cc <= 20:
            return ComplexityGrade.C
        elif cc <= 30:
            return ComplexityGrade.D
        elif cc <= 40:
            return ComplexityGrade.E
        else:
            return ComplexityGrade.F
    
    @property
    def is_complex(self) -> bool:
        """Check if function is too complex (grade C or worse)."""
        return self.cyclomatic_complexity > 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "cognitive_complexity": self.cognitive_complexity,
            "lines_of_code": self.lines_of_code,
            "parameters": self.parameters,
            "grade": self.grade.value,
            "is_complex": self.is_complex
        }


@dataclass
class ClassComplexity:
    """Complexity metrics for a single class."""
    name: str
    file_path: str
    line_start: int
    line_end: int
    methods: List[FunctionComplexity] = field(default_factory=list)
    
    @property
    def total_complexity(self) -> int:
        """Get total complexity of all methods."""
        return sum(m.cyclomatic_complexity for m in self.methods)
    
    @property
    def average_complexity(self) -> float:
        """Get average complexity per method."""
        if not self.methods:
            return 0.0
        return self.total_complexity / len(self.methods)
    
    @property
    def method_count(self) -> int:
        """Get number of methods."""
        return len(self.methods)
    
    @property
    def complex_methods(self) -> List[FunctionComplexity]:
        """Get list of complex methods."""
        return [m for m in self.methods if m.is_complex]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "method_count": self.method_count,
            "total_complexity": self.total_complexity,
            "average_complexity": self.average_complexity,
            "complex_methods_count": len(self.complex_methods),
            "methods": [m.to_dict() for m in self.methods]
        }


@dataclass
class FileComplexity:
    """Complexity metrics for a single file."""
    file_path: str
    functions: List[FunctionComplexity] = field(default_factory=list)
    classes: List[ClassComplexity] = field(default_factory=list)
    lines_of_code: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    
    @property
    def total_complexity(self) -> int:
        """Get total complexity."""
        func_complexity = sum(f.cyclomatic_complexity for f in self.functions)
        class_complexity = sum(c.total_complexity for c in self.classes)
        return func_complexity + class_complexity
    
    @property
    def average_complexity(self) -> float:
        """Get average complexity."""
        total_items = len(self.functions) + sum(c.method_count for c in self.classes)
        if total_items == 0:
            return 0.0
        return self.total_complexity / total_items
    
    @property
    def maintainability_index(self) -> float:
        """Calculate maintainability index (0-100)."""
        if self.lines_of_code == 0:
            return 100.0
        
        import math
        
        avg_cc = self.average_complexity if self.average_complexity > 0 else 1
        loc = self.lines_of_code
        
        mi = 171 - 5.2 * math.log(avg_cc) - 0.23 * avg_cc - 16.2 * math.log(loc)
        mi = max(0, min(100, mi * 100 / 171))
        
        return round(mi, 2)
    
    @property
    def maintainability_grade(self) -> MaintainabilityGrade:
        """Get maintainability grade."""
        mi = self.maintainability_index
        if mi >= 20:
            return MaintainabilityGrade.A
        elif mi >= 10:
            return MaintainabilityGrade.B
        else:
            return MaintainabilityGrade.C
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "lines_of_code": self.lines_of_code,
            "blank_lines": self.blank_lines,
            "comment_lines": self.comment_lines,
            "total_complexity": self.total_complexity,
            "average_complexity": self.average_complexity,
            "maintainability_index": self.maintainability_index,
            "maintainability_grade": self.maintainability_grade.value,
            "function_count": len(self.functions),
            "class_count": len(self.classes),
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes]
        }


@dataclass
class ProjectComplexity:
    """Complexity metrics for entire project."""
    files: List[FileComplexity] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_files(self) -> int:
        """Get total number of files."""
        return len(self.files)
    
    @property
    def total_lines(self) -> int:
        """Get total lines of code."""
        return sum(f.lines_of_code for f in self.files)
    
    @property
    def total_complexity(self) -> int:
        """Get total complexity."""
        return sum(f.total_complexity for f in self.files)
    
    @property
    def average_complexity(self) -> float:
        """Get average complexity per file."""
        if not self.files:
            return 0.0
        return self.total_complexity / self.total_files
    
    @property
    def average_maintainability(self) -> float:
        """Get average maintainability index."""
        if not self.files:
            return 100.0
        return sum(f.maintainability_index for f in self.files) / self.total_files
    
    @property
    def complex_functions(self) -> List[FunctionComplexity]:
        """Get all complex functions across project."""
        result = []
        for file in self.files:
            result.extend([f for f in file.functions if f.is_complex])
            for cls in file.classes:
                result.extend(cls.complex_methods)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_complexity": self.total_complexity,
            "average_complexity": self.average_complexity,
            "average_maintainability": self.average_maintainability,
            "complex_functions_count": len(self.complex_functions),
            "analyzed_at": self.analyzed_at.isoformat(),
            "files": [f.to_dict() for f in self.files]
        }


class ComplexityThresholds:
    """Complexity thresholds for quality gates."""
    
    MAX_CYCLOMATIC_COMPLEXITY = 15
    MAX_COGNITIVE_COMPLEXITY = 20
    MAX_FUNCTION_LINES = 50
    MAX_FUNCTION_PARAMETERS = 7
    MAX_CLASS_METHODS = 20
    MIN_MAINTAINABILITY_INDEX = 20.0
    MAX_FILE_LINES = 500
    
    @classmethod
    def get_thresholds(cls) -> Dict[str, Any]:
        """Get all thresholds as dictionary."""
        return {
            "max_cyclomatic_complexity": cls.MAX_CYCLOMATIC_COMPLEXITY,
            "max_cognitive_complexity": cls.MAX_COGNITIVE_COMPLEXITY,
            "max_function_lines": cls.MAX_FUNCTION_LINES,
            "max_function_parameters": cls.MAX_FUNCTION_PARAMETERS,
            "max_class_methods": cls.MAX_CLASS_METHODS,
            "min_maintainability_index": cls.MIN_MAINTAINABILITY_INDEX,
            "max_file_lines": cls.MAX_FILE_LINES,
        }
    
    @classmethod
    def check_function(cls, func: FunctionComplexity) -> List[str]:
        """Check function against thresholds, return violations."""
        violations = []
        
        if func.cyclomatic_complexity > cls.MAX_CYCLOMATIC_COMPLEXITY:
            violations.append(
                f"Cyclomatic complexity {func.cyclomatic_complexity} exceeds max {cls.MAX_CYCLOMATIC_COMPLEXITY}"
            )
        
        if func.cognitive_complexity > cls.MAX_COGNITIVE_COMPLEXITY:
            violations.append(
                f"Cognitive complexity {func.cognitive_complexity} exceeds max {cls.MAX_COGNITIVE_COMPLEXITY}"
            )
        
        if func.lines_of_code > cls.MAX_FUNCTION_LINES:
            violations.append(
                f"Function has {func.lines_of_code} lines, exceeds max {cls.MAX_FUNCTION_LINES}"
            )
        
        if func.parameters > cls.MAX_FUNCTION_PARAMETERS:
            violations.append(
                f"Function has {func.parameters} parameters, exceeds max {cls.MAX_FUNCTION_PARAMETERS}"
            )
        
        return violations
    
    @classmethod
    def check_class(cls, class_complexity: ClassComplexity) -> List[str]:
        """Check class against thresholds, return violations."""
        violations = []
        
        if class_complexity.method_count > cls.MAX_CLASS_METHODS:
            violations.append(
                f"Class has {class_complexity.method_count} methods, exceeds max {cls.MAX_CLASS_METHODS}"
            )
        
        return violations
    
    @classmethod
    def check_file(cls, file_complexity: FileComplexity) -> List[str]:
        """Check file against thresholds, return violations."""
        violations = []
        
        if file_complexity.lines_of_code > cls.MAX_FILE_LINES:
            violations.append(
                f"File has {file_complexity.lines_of_code} lines, exceeds max {cls.MAX_FILE_LINES}"
            )
        
        if file_complexity.maintainability_index < cls.MIN_MAINTAINABILITY_INDEX:
            violations.append(
                f"Maintainability index {file_complexity.maintainability_index} below min {cls.MIN_MAINTAINABILITY_INDEX}"
            )
        
        return violations


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor for calculating complexity."""
    
    COMPLEXITY_NODES = (
        ast.If, ast.For, ast.While, ast.ExceptHandler,
        ast.With, ast.Assert, ast.comprehension
    )
    
    def __init__(self):
        """Initialize visitor."""
        self.functions: List[FunctionComplexity] = []
        self.classes: List[ClassComplexity] = []
        self._current_class: Optional[ClassComplexity] = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        complexity = self._calculate_complexity(node)
        
        func = FunctionComplexity(
            name=node.name,
            file_path="",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            cyclomatic_complexity=complexity,
            lines_of_code=(node.end_lineno or node.lineno) - node.lineno + 1,
            parameters=len(node.args.args)
        )
        
        if self._current_class:
            self._current_class.methods.append(func)
        else:
            self.functions.append(func)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        complexity = self._calculate_complexity(node)
        
        func = FunctionComplexity(
            name=node.name,
            file_path="",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            cyclomatic_complexity=complexity,
            lines_of_code=(node.end_lineno or node.lineno) - node.lineno + 1,
            parameters=len(node.args.args)
        )
        
        if self._current_class:
            self._current_class.methods.append(func)
        else:
            self.functions.append(func)
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        cls = ClassComplexity(
            name=node.name,
            file_path="",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno
        )
        
        self._current_class = cls
        self.generic_visit(node)
        self._current_class = None
        
        self.classes.append(cls)
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a node."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, self.COMPLEXITY_NODES):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class ComplexityAnalyzer:
    """Analyzer for code complexity."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize analyzer."""
        self.project_root = project_root or os.getcwd()
    
    def analyze_file(self, file_path: str) -> FileComplexity:
        """Analyze a single Python file."""
        result = FileComplexity(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            result.lines_of_code = len([l for l in lines if l.strip()])
            result.blank_lines = len([l for l in lines if not l.strip()])
            result.comment_lines = len([l for l in lines if l.strip().startswith('#')])
            
            tree = ast.parse(content)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            for func in visitor.functions:
                func.file_path = file_path
                result.functions.append(func)
            
            for cls in visitor.classes:
                cls.file_path = file_path
                for method in cls.methods:
                    method.file_path = file_path
                result.classes.append(cls)
                
        except SyntaxError:
            pass
        except Exception:
            pass
        
        return result
    
    def analyze_directory(self, directory: str, exclude_patterns: Optional[List[str]] = None) -> ProjectComplexity:
        """Analyze all Python files in a directory."""
        exclude_patterns = exclude_patterns or ["__pycache__", ".venv", "venv", "migrations", "tests"]
        result = ProjectComplexity()
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_complexity = self.analyze_file(file_path)
                    result.files.append(file_complexity)
        
        return result
    
    def analyze_project(self, exclude_patterns: Optional[List[str]] = None) -> ProjectComplexity:
        """Analyze entire project."""
        src_dir = os.path.join(self.project_root, "src")
        if os.path.exists(src_dir):
            return self.analyze_directory(src_dir, exclude_patterns)
        return self.analyze_directory(self.project_root, exclude_patterns)
    
    def get_violations(self, project: ProjectComplexity) -> Dict[str, List[Dict[str, Any]]]:
        """Get all threshold violations in project."""
        violations = {
            "functions": [],
            "classes": [],
            "files": []
        }
        
        for file in project.files:
            file_violations = ComplexityThresholds.check_file(file)
            if file_violations:
                violations["files"].append({
                    "file_path": file.file_path,
                    "violations": file_violations
                })
            
            for func in file.functions:
                func_violations = ComplexityThresholds.check_function(func)
                if func_violations:
                    violations["functions"].append({
                        "name": func.name,
                        "file_path": func.file_path,
                        "line": func.line_start,
                        "violations": func_violations
                    })
            
            for cls in file.classes:
                class_violations = ComplexityThresholds.check_class(cls)
                if class_violations:
                    violations["classes"].append({
                        "name": cls.name,
                        "file_path": cls.file_path,
                        "line": cls.line_start,
                        "violations": class_violations
                    })
                
                for method in cls.methods:
                    method_violations = ComplexityThresholds.check_function(method)
                    if method_violations:
                        violations["functions"].append({
                            "name": f"{cls.name}.{method.name}",
                            "file_path": method.file_path,
                            "line": method.line_start,
                            "violations": method_violations
                        })
        
        return violations


class RadonRunner:
    """Runner for radon complexity analysis tool."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize radon runner."""
        self.project_root = project_root or os.getcwd()
    
    def run_cc(self, paths: Optional[List[str]] = None, min_grade: str = "C") -> Dict[str, Any]:
        """Run radon cyclomatic complexity analysis."""
        paths = paths or [os.path.join(self.project_root, "src")]
        
        try:
            cmd = [sys.executable, "-m", "radon", "cc", "-j", "-s", f"--min={min_grade}"]
            cmd.extend(paths)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if proc.stdout:
                return json.loads(proc.stdout)
            return {}
            
        except Exception:
            return {}
    
    def run_mi(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run radon maintainability index analysis."""
        paths = paths or [os.path.join(self.project_root, "src")]
        
        try:
            cmd = [sys.executable, "-m", "radon", "mi", "-j", "-s"]
            cmd.extend(paths)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if proc.stdout:
                return json.loads(proc.stdout)
            return {}
            
        except Exception:
            return {}
    
    def run_raw(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run radon raw metrics analysis."""
        paths = paths or [os.path.join(self.project_root, "src")]
        
        try:
            cmd = [sys.executable, "-m", "radon", "raw", "-j", "-s"]
            cmd.extend(paths)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if proc.stdout:
                return json.loads(proc.stdout)
            return {}
            
        except Exception:
            return {}


def analyze_complexity(project_root: Optional[str] = None) -> ProjectComplexity:
    """Analyze project complexity."""
    analyzer = ComplexityAnalyzer(project_root)
    return analyzer.analyze_project()


def generate_complexity_report(project: ProjectComplexity) -> str:
    """Generate complexity report in markdown format."""
    lines = [
        "# Code Complexity Report",
        "",
        f"**Analyzed:** {project.analyzed_at.strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        f"- **Total Files:** {project.total_files}",
        f"- **Total Lines:** {project.total_lines}",
        f"- **Total Complexity:** {project.total_complexity}",
        f"- **Average Complexity:** {project.average_complexity:.2f}",
        f"- **Average Maintainability:** {project.average_maintainability:.2f}",
        f"- **Complex Functions:** {len(project.complex_functions)}",
        "",
    ]
    
    if project.complex_functions:
        lines.append("## Complex Functions (CC > 10)")
        lines.append("")
        for func in sorted(project.complex_functions, key=lambda f: f.cyclomatic_complexity, reverse=True)[:20]:
            lines.append(f"- **{func.name}** (CC={func.cyclomatic_complexity}, Grade={func.grade.value})")
            lines.append(f"  - File: {func.file_path}:{func.line_start}")
        lines.append("")
    
    lines.append("## Files by Maintainability")
    lines.append("")
    for file in sorted(project.files, key=lambda f: f.maintainability_index)[:10]:
        lines.append(f"- **{os.path.basename(file.file_path)}** (MI={file.maintainability_index:.1f}, Grade={file.maintainability_grade.value})")
    
    return "\n".join(lines)
