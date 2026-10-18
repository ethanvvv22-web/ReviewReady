"""Framework-specific rules: dependencies, interface compliance, tests.

These encode a validation framework's contribution guidelines - the kind of
conventions a human reviewer repeatedly checks by hand today.
"""
from __future__ import annotations
import ast
import sys

from . import config
from .findings import Finding

_STDLIB = set(getattr(sys, "stdlib_module_names", set()))


def check_dependencies(tree: ast.Module) -> list[Finding]:
    out = []
    seen = set()
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods = [node.module.split(".")[0]]
        for m in mods:
            if m in seen or m in _STDLIB or m in config.APPROVED_THIRD_PARTY:
                continue
            if m == "reviewready":
                continue
            seen.add(m)
            out.append(Finding("non-approved-dependency", "error",
                               f"dependency '{m}' is not on the framework allow-list",
                               f"use an approved dependency or request approval for '{m}'",
                               getattr(node, "lineno", 0), "framework", needs_human=True))
    return out


def check_interfaces(tree: ast.Module) -> list[Finding]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("Driver"):
            methods = {n.name for n in node.body
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            missing = config.DRIVER_REQUIRED_METHODS - methods
            if missing:
                out.append(Finding("interface-missing-method", "error",
                                   f"Driver class '{node.name}' missing methods: "
                                   f"{', '.join(sorted(missing))}",
                                   "implement the required Driver interface methods",
                                   node.lineno, "framework"))
    return out


def check_tests(has_tests: bool) -> list[Finding]:
    if has_tests:
        return []
    return [Finding("missing-tests", "error",
                    "no accompanying tests found for this contribution",
                    "add a test module (e.g. test_<name>.py) covering the public API",
                    0, "framework", needs_human=False)]


def run_rules(tree: ast.Module, has_tests: bool) -> list[Finding]:
    return (check_dependencies(tree) + check_interfaces(tree)
            + check_tests(has_tests))
