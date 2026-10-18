"""Orchestrator: run every layer over a contribution and score readiness."""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
from pathlib import Path

from . import ast_checks, tools, config
from .rules import run_rules
from .fixer import apply_safe_fixes
from .findings import Finding, SEVERITY_ORDER


@dataclass
class Assessment:
    findings: list[Finding] = field(default_factory=list)
    tool_status: dict = field(default_factory=dict)
    applied_fixes: list[str] = field(default_factory=list)
    readiness: int = 100
    ready: bool = False

    def by_severity(self, sev: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == sev]


def _has_tests(path: Path) -> bool:
    root = path if path.is_dir() else path.parent
    if (root / "tests").is_dir():
        return True
    if any(root.glob("test_*.py")) or any(root.glob("*_test.py")):
        return True
    if path.is_file():
        return (root / f"test_{path.stem}.py").exists()
    return False


def _py_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return [p for p in path.rglob("*.py") if "test" not in p.name
            and p.name != "__init__.py"]


def _analyze_source(src: str, name: str, has_tests: bool) -> list[Finding]:
    found = ast_checks.analyze(src, name)
    try:
        tree = ast.parse(src, name)
        found += run_rules(tree, has_tests)
    except SyntaxError:
        pass
    for f in found:
        f.file = name
    return found


def assess(target: str, autofix: bool = False) -> Assessment:
    path = Path(target)
    has_tests = _has_tests(path)
    files = _py_files(path)

    all_findings: list[Finding] = []
    applied: list[str] = []
    for fp in files:
        src = fp.read_text(encoding="utf-8")
        if autofix:
            new_src, fixes = apply_safe_fixes(src)
            if fixes:
                fp.write_text(new_src, encoding="utf-8")
                applied += [f"{fp.name}: {x}" for x in fixes]
                src = new_src
        all_findings += _analyze_source(src, fp.name, has_tests)

    tool_findings, status = tools.run_external_tools(str(path))
    all_findings += tool_findings

    all_findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.file, f.line))
    score = _readiness(all_findings)
    ready = not any(f.severity == "error" for f in all_findings)
    return Assessment(all_findings, status, applied, score, ready)


def _readiness(findings: list[Finding]) -> int:
    weight = {"error": 15, "warning": 5, "info": 1}
    score = 100 - sum(weight.get(f.severity, 0) for f in findings)
    return max(0, score)
