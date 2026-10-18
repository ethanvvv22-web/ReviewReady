"""A single finding and the category taxonomy.

Each finding carries everything a contributor needs to act: what, where, why,
how to fix, and whether a human reviewer still has to judge it.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# Categories map to the JD's areas of exploration.
CATEGORIES = [
    "missing-module-docstring", "missing-func-docstring", "missing-type-hints",
    "bare-except", "print-statement", "mutable-default", "unused-import",
    "line-too-long", "todo-left", "star-import", "naming-convention",
    "long-function", "non-approved-dependency", "interface-missing-method",
    "missing-tests",
]

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass
class Finding:
    category: str
    severity: str            # error | warning | info
    message: str             # what is wrong
    suggestion: str          # how to fix it (actionable)
    line: int = 0
    layer: str = "framework" # tool | ast | framework | ai
    auto_fixable: bool = False
    needs_human: bool = False
    fixed: bool = False
    file: str = ""

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("category", "severity", "message", "suggestion", "line",
                 "layer", "auto_fixable", "needs_human", "fixed", "file")}
