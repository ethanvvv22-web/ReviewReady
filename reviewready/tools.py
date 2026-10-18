"""Deterministic external tool layer.

Runs industry tools when installed (formatting, linting, type-checking,
testing, security static analysis) and records which ran vs were skipped, so
the pre-review summary is honest about coverage. When a tool is missing the
built-in ast_checks layer still covers the basics.
"""
from __future__ import annotations
import json
import shutil
import subprocess

from .findings import Finding

# tool name -> (command builder, category, severity)
_TOOLS = {
    "ruff":   (lambda p: ["ruff", "check", "--output-format", "json", p], "lint", "warning"),
    "black":  (lambda p: ["black", "--check", "-q", p], "formatting", "info"),
    "mypy":   (lambda p: ["mypy", "--no-error-summary", p], "missing-type-hints", "warning"),
    "pytest": (lambda p: ["pytest", "-q", p], "missing-tests", "error"),
    "bandit": (lambda p: ["bandit", "-q", "-f", "json", "-r", p], "security", "error"),
}


def available() -> dict[str, bool]:
    return {name: shutil.which(name) is not None for name in _TOOLS}


def run_external_tools(path: str) -> tuple[list[Finding], dict[str, str]]:
    findings: list[Finding] = []
    status: dict[str, str] = {}
    for name, (build, category, severity) in _TOOLS.items():
        if shutil.which(name) is None:
            status[name] = "skipped (not installed)"
            continue
        try:
            r = subprocess.run(build(path), capture_output=True, text=True, timeout=120)
        except Exception as e:  # tool present but failed to run
            status[name] = f"error: {e}"
            continue
        n = _parse(name, r)
        status[name] = "clean" if n == 0 else f"{n} issue(s)"
        if n:
            findings.append(Finding(category, severity,
                                    f"{name} reported {n} issue(s)",
                                    f"run '{name}' locally and address its findings",
                                    0, "tool"))
    return findings, status


def _parse(name: str, r: subprocess.CompletedProcess) -> int:
    if name == "ruff":
        try:
            return len(json.loads(r.stdout or "[]"))
        except Exception:
            return 0 if r.returncode == 0 else 1
    if name == "bandit":
        try:
            return len(json.loads(r.stdout or "{}").get("results", []))
        except Exception:
            return 0 if r.returncode == 0 else 1
    # black/mypy/pytest: non-zero return code => issues
    return 0 if r.returncode == 0 else 1
