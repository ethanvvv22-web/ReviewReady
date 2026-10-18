"""Safe auto-fixer.

Applies only low-risk, behaviour-preserving fixes so contributors can iterate
without surprises: trailing whitespace, final newline, and a module docstring
stub. Everything riskier is left as a suggestion for the contributor.
"""
from __future__ import annotations
import ast


def apply_safe_fixes(source: str) -> tuple[str, list[str]]:
    applied: list[str] = []
    lines = source.splitlines()

    # 1. strip trailing whitespace
    stripped = [ln.rstrip() for ln in lines]
    if stripped != lines:
        applied.append("removed trailing whitespace")
        lines = stripped

    text = "\n".join(lines)

    # 2. module docstring stub if missing
    try:
        tree = ast.parse(text)
        if ast.get_docstring(tree) is None:
            insert_at = _module_doc_insert_line(lines)
            stub = '"""Module docstring stub (auto-added) - please complete."""'
            lines.insert(insert_at, stub)
            applied.append("added module docstring stub")
            text = "\n".join(lines)
    except SyntaxError:
        pass  # never auto-edit code that does not parse

    # 3. ensure single trailing newline
    if not text.endswith("\n"):
        text += "\n"
        applied.append("added final newline")

    return text, applied


def _module_doc_insert_line(lines: list[str]) -> int:
    """Insert after shebang / encoding / __future__ imports, else at top."""
    i = 0
    while i < len(lines) and (lines[i].startswith("#!")
                              or "coding" in lines[i]
                              or lines[i].startswith("from __future__")):
        i += 1
    return i
