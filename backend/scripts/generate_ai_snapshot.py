#!/usr/bin/env python3
"""
AI Project Snapshot Generator

Scans backend Python files and generates a token-efficient PROJECT_SNAPSHOT.md
(target: 800-1000 tokens) that gives AI agents a complete understanding of the project.

Usage:
    python scripts/generate_ai_snapshot.py

This script is designed to be run:
- Manually when needed
- Automatically via pre-commit hook
- As part of CI/CD pipeline
"""

import ast
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    is_async: bool = False
    is_endpoint: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class FileInfo:
    """Information about a Python file."""
    path: str
    relative_path: str
    purpose: str
    key_classes: List[str] = field(default_factory=list)
    key_functions: List[FunctionInfo] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    endpoints: List[str] = field(default_factory=list)
    line_count: int = 0


class ProjectAnalyzer:
    """Analyzes Python project structure and generates token-efficient documentation."""

    def __init__(self, backend_dir: Path):
        """
        Initialize the project analyzer.

        Args:
            backend_dir: Path to the backend directory
        """
        self.backend_dir = backend_dir
        self.files: List[FileInfo] = []
        self.all_dependencies: Set[str] = set()

    def scan_files(self) -> None:
        """Scan all Python files in the backend directory."""
        for py_file in self.backend_dir.glob("*.py"):
            # Skip __pycache__, venv, and other non-source files
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue

            file_info = self._analyze_file(py_file)
            if file_info:
                self.files.append(file_info)
                self.all_dependencies.update(file_info.dependencies)

    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """
        Analyze a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            FileInfo object or None if analysis fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract module docstring (purpose)
            purpose = ast.get_docstring(tree) or "No description"
            # Truncate long docstrings to first sentence
            purpose = purpose.split('\n')[0][:120]

            # Extract classes
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # Extract functions with metadata
            functions = []
            endpoints = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip nested functions and private methods
                    if node.name.startswith("_") and node.name not in ["__init__", "__repr__"]:
                        continue

                    decorators = [self._get_decorator_name(d) for d in node.decorator_list]
                    is_endpoint = any(d in ["get", "post", "put", "delete", "patch"] for d in decorators)

                    func_info = FunctionInfo(
                        name=node.name,
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                        is_endpoint=is_endpoint,
                        decorators=decorators
                    )

                    functions.append(func_info)

                    # Extract endpoint paths
                    if is_endpoint:
                        endpoint_path = self._extract_endpoint_path(node)
                        if endpoint_path:
                            endpoints.append(endpoint_path)

            # Extract dependencies (imports)
            dependencies = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Only include project-local and key external deps
                        if self._is_relevant_dependency(alias.name):
                            dependencies.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and self._is_relevant_dependency(node.module):
                        dependencies.add(node.module)

            # Count lines
            line_count = len(content.split('\n'))

            return FileInfo(
                path=str(file_path),
                relative_path=file_path.name,
                purpose=purpose,
                key_classes=classes[:10],  # Limit to 10 most important
                key_functions=functions[:15],  # Limit to 15 most important
                dependencies=dependencies,
                endpoints=endpoints,
                line_count=line_count
            )

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")
            return None

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
            elif isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return ""

    def _extract_endpoint_path(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract the path from an endpoint decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Check if decorator is app.get("/path"), etc.
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value
                    if isinstance(path, str) and path.startswith("/"):
                        # Get HTTP method
                        method = self._get_decorator_name(decorator)
                        return f"{method.upper()} {path}"
        return None

    def _is_relevant_dependency(self, module_name: str) -> bool:
        """Determine if a dependency is relevant for the snapshot."""
        # Include local modules
        if module_name in ["database", "hardware_detector", "conversation_manager", "logger"]:
            return True

        # Include key external dependencies
        key_external = ["fastapi", "sqlalchemy", "httpx", "pydantic", "uvicorn"]
        return any(module_name.startswith(dep) for dep in key_external)

    def generate_snapshot(self) -> str:
        """
        Generate a token-efficient PROJECT_SNAPSHOT.md.

        Returns:
            Markdown content as string
        """
        lines = []

        # Header
        lines.append("# AI Assistant - Project Snapshot")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Quick Overview
        lines.append("## Overview")
        lines.append("Local-first AI assistant with FastAPI backend, Ollama LLM integration, "
                    "hardware detection, and conversation management. MVP focuses on chat with local LLM; "
                    "future phases add MCP tool integration (Gmail, Calendar, Salesforce), workflow automation, "
                    "and OAuth authentication.")
        lines.append("")

        # Architecture Summary
        lines.append("## Architecture")
        lines.append("**Stack**: FastAPI + SQLAlchemy + Ollama + httpx")
        lines.append("**Database**: SQLite with 5 tables (users, conversations, tool_connections, workflows, workflow_executions)")
        lines.append("**LLM**: Local Ollama models with automatic hardware-optimized selection")
        lines.append("**Frontend**: Vanilla JS with fetch API (simple SPA at /frontend)")
        lines.append("")

        # Core Files (token-optimized)
        lines.append("## Core Files")
        lines.append("")

        for file_info in sorted(self.files, key=lambda f: f.relative_path):
            if file_info.relative_path == "__init__.py":
                continue

            lines.append(f"### {file_info.relative_path}")
            lines.append(f"**Purpose**: {file_info.purpose}")
            lines.append(f"**Lines**: {file_info.line_count}")

            # Classes
            if file_info.key_classes:
                classes_str = ", ".join(file_info.key_classes[:5])
                lines.append(f"**Classes**: {classes_str}")

            # Key functions (condensed)
            if file_info.key_functions:
                # Prioritize endpoints and async functions
                priority_funcs = [f for f in file_info.key_functions if f.is_endpoint or f.is_async]
                other_funcs = [f for f in file_info.key_functions if not (f.is_endpoint or f.is_async)]

                funcs_to_show = (priority_funcs[:5] + other_funcs[:3])[:8]

                func_names = []
                for func in funcs_to_show:
                    prefix = "async " if func.is_async else ""
                    suffix = " [endpoint]" if func.is_endpoint else ""
                    func_names.append(f"{prefix}{func.name}{suffix}")

                lines.append(f"**Functions**: {', '.join(func_names)}")

            # Dependencies (only show local deps)
            local_deps = [d for d in file_info.dependencies
                         if d in ["database", "hardware_detector", "conversation_manager", "logger"]]
            if local_deps:
                lines.append(f"**Imports**: {', '.join(sorted(local_deps))}")

            lines.append("")

        # API Endpoints Summary
        all_endpoints = []
        for file_info in self.files:
            all_endpoints.extend(file_info.endpoints)

        if all_endpoints:
            lines.append("## API Endpoints")
            for endpoint in sorted(all_endpoints):
                lines.append(f"- `{endpoint}`")
            lines.append("")

        # Database Models
        lines.append("## Database Models")
        lines.append("- **User**: email, created_at")
        lines.append("- **Conversation**: user_id, conversation_id, messages (JSON), timestamps")
        lines.append("- **ToolConnection**: user_id, service_name, auth_data, is_connected")
        lines.append("- **Workflow**: user_id, name, trigger (JSON), actions (JSON), is_active")
        lines.append("- **WorkflowExecution**: workflow_id, status, results (JSON), tokens_used")
        lines.append("")

        # Key Dependencies
        lines.append("## Key Dependencies")
        external_deps = [d for d in self.all_dependencies
                        if any(d.startswith(key) for key in ["fastapi", "sqlalchemy", "httpx", "pydantic"])]
        if external_deps:
            lines.append(f"{', '.join(sorted(set(external_deps)))}")
        lines.append("")

        # Development Notes
        lines.append("## Dev Notes")
        lines.append("- **Startup**: `python main.py` (runs on :8000, auto-reload in debug mode)")
        lines.append("- **Config**: Environment vars via .env (ollama_base_url=http://localhost:11434, database_url, host, port)")
        lines.append("- **Hardware Detection**: Detects Apple Silicon/Intel, RAM, cores → recommends optimal model from catalog")
        lines.append("  - Model catalog: llama3.2 (1B/3B/11B), phi3:mini, mistral:7b, llama3.1:8b, gemma2:9b, codellama:13b")
        lines.append("  - Returns ALL compatible models with performance ratings (excellent/good/acceptable/slow)")
        lines.append("- **Chat Flow**: User msg → conversation_manager → sanitize context → ollama_chat (full ctx) → fallback to last msg → fallback to generate → store response")
        lines.append("- **Robust Fallbacks**: 3-tier strategy ensures responses even when context issues occur")
        lines.append("- **Context Sanitization**: Strictly validates messages for Ollama (role+content only, handles list/dict content)")
        lines.append("")

        # Stats
        total_lines = sum(f.line_count for f in self.files)
        lines.append("## Stats")
        lines.append(f"**Files**: {len(self.files)} | **Total Lines**: {total_lines}")
        lines.append("")

        return "\n".join(lines)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 characters).

        Args:
            text: Text to estimate

        Returns:
            Approximate token count
        """
        return len(text) // 4


def main():
    """Main entry point for the snapshot generator."""
    # Determine backend directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent

    print(f"Scanning backend directory: {backend_dir}")

    # Initialize analyzer
    analyzer = ProjectAnalyzer(backend_dir)

    # Scan files
    print("Analyzing Python files...")
    analyzer.scan_files()

    print(f"Found {len(analyzer.files)} Python files")

    # Generate snapshot
    print("Generating PROJECT_SNAPSHOT.md...")
    snapshot_content = analyzer.generate_snapshot()

    # Estimate tokens
    token_count = analyzer.estimate_tokens(snapshot_content)
    print(f"Estimated tokens: {token_count}")

    # Write to file
    output_path = backend_dir / "PROJECT_SNAPSHOT.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(snapshot_content)

    print(f"✓ Generated {output_path}")

    # Token budget check
    if token_count < 800:
        print("⚠ Warning: Snapshot is under 800 tokens, consider adding more detail")
    elif token_count > 1200:
        print("⚠ Warning: Snapshot exceeds 1200 tokens, consider condensing")
    else:
        print("✓ Token count within target range (800-1000)")

    return 0


if __name__ == "__main__":
    exit(main())
