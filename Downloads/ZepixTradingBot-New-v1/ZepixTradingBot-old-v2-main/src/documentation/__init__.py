"""
Documentation Package for V5 Hybrid Plugin Architecture.

This package provides documentation generation tools:
- Automated doc generator
- API reference generator
- User guide generation
- Admin guide generation
- Plugin developer guide generation
- Troubleshooting guide generation

Based on Document 14: USER_DOCUMENTATION.md

Version: 1.0
Date: 2026-01-12
"""

from src.documentation.doc_generator import (
    DocType,
    DocFormat,
    DocSection,
    DocPage,
    FunctionDoc,
    ClassDoc,
    ModuleDoc,
    DocstringParser,
    CodeAnalyzer,
    DocumentationGenerator,
    generate_documentation,
)

from src.documentation.api_reference import (
    APICategory,
    APIEndpoint,
    APISection,
    ServiceAPIReference,
    TelegramAPIReference,
    APIReferenceGenerator,
    generate_api_reference,
)

__version__ = "1.0.0"

__all__ = [
    # Doc Generator
    "DocType",
    "DocFormat",
    "DocSection",
    "DocPage",
    "FunctionDoc",
    "ClassDoc",
    "ModuleDoc",
    "DocstringParser",
    "CodeAnalyzer",
    "DocumentationGenerator",
    "generate_documentation",
    
    # API Reference
    "APICategory",
    "APIEndpoint",
    "APISection",
    "ServiceAPIReference",
    "TelegramAPIReference",
    "APIReferenceGenerator",
    "generate_api_reference",
]
