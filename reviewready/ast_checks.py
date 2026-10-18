"""Built-in, zero-dependency static checks (ast + tokenize).

These always run, so ReviewReady works even when no external tools are
installed. When ruff/mypy/etc. ARE present, tools.py adds them on top.
"""
from __future__ import annotations
import ast
import re

from . import config
from .findings import Finding

_SNAKE = re.compile(r"^_?[a-z][a-z0-9_]*$")
_CAMEL = re.compile(r"^_?[A-Z][A-Za-z0-9]*$")
_TODO = re.compile(r"\b(TODO|FIXME|XXX)\b")


def _public(name: str) -> bool:
    return not name.startswith("_")


def analyze(source: str, filename: str = "<contrib>") -> list[Finding]:
    out: list[Finding] = []
    lines = source.splitlines()

    # line length + TODO (text-level)
    for i, ln in enumerate(lines, 1):
        if len(ln) > config.MAX_LINE:
            out.append(Finding("line-too-long", "info",
                               f"line {i} is {len(ln)} chars (>{config.MAX_LINE})",
                               "wrap or shorten the line", i, "ast", auto_fixable=False))
        if _TODO.search(ln):
            out.append(Finding("todo-left", "warning",
                               f"unresolved TODO/FIXME on line {i}",
                               "resolve or file a tracked issue before contributing",
                               i, "ast"))

    try:
        tree = ast.parse(source, filename)
    except SyntaxError as e:
        out.append(Finding("syntax-error" if False else "long-function", "error",
                           f"syntax error: {e}", "fix the syntax error",
                           getattr(e, "lineno", 0), "ast", needs_human=True))
        return out

    if ast.get_docstring(tree) is None:
        out.append(Finding("missing-module-docstring", "warning",
                           "module has no docstring",
                           "add a top-level docstring describing the module",
                           1, "ast", auto_fixable=True))

    # imports / usage for unused-import
    imported: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name == "*":
                    out.append(Finding("star-import", "warning",
                                       f"star import on line {node.lineno}",
                                       "import only the names you use", node.lineno, "ast"))
                else:
                    imported[a.asname or a.name] = node.lineno
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    used |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for name, lineno in imported.items():
        if name not in used:
            out.append(Finding("unused-import", "info",
                               f"'{name}' imported but unused (line {lineno})",
                               f"remove the unused import '{name}'", lineno, "ast",
                               auto_fixable=False))

    out.extend(_defs(tree, lines))
    return out


def _defs(tree: ast.Module, lines: list[str]) -> list[Finding]:
    out: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not _CAMEL.match(node.name):
                out.append(Finding("naming-convention", "warning",
                                   f"class '{node.name}' is not CamelCase",
                                   "rename the class to CamelCase", node.lineno, "ast"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.extend(_func(node, lines))
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append(Finding("bare-except", "error",
                               f"bare 'except:' on line {node.lineno}",
                               "catch a specific exception type", node.lineno, "ast",
                               needs_human=False))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "print":
            out.append(Finding("print-statement", "warning",
                               f"print() call on line {node.lineno}",
                               "use the logging module instead of print()",
                               node.lineno, "ast"))
    return out


def _func(node, lines: list[str]) -> list[Finding]:
    out: list[Finding] = []
    name = node.name
    if not _SNAKE.match(name):
        out.append(Finding("naming-convention", "warning",
                           f"function '{name}' is not snake_case",
                           "rename to snake_case", node.lineno, "ast"))
    if _public(name):
        if ast.get_docstring(node) is None:
            out.append(Finding("missing-func-docstring", "warning",
                               f"public function '{name}' has no docstring",
                               "add a docstring describing args, returns, raises",
                               node.lineno, "ast", auto_fixable=True))
        args = node.args.args + node.args.kwonlyargs
        untyped = [a.arg for a in args if a.annotation is None and a.arg != "self"]
        if untyped or node.returns is None:
            miss = ", ".join(untyped) + (" + return" if node.returns is None else "")
            out.append(Finding("missing-type-hints", "warning",
                               f"public function '{name}' missing type hints: {miss}",
                               "add parameter and return type annotations",
                               node.lineno, "ast"))
    # mutable default args
    for d in node.args.defaults + node.args.kw_defaults:
        if isinstance(d, (ast.List, ast.Dict, ast.Set)):
            out.append(Finding("mutable-default", "error",
                               f"mutable default argument in '{name}'",
                               "use None and create the container inside the function",
                               node.lineno, "ast"))
            break
    # function length
    end = getattr(node, "end_lineno", node.lineno)
    span = end - node.lineno + 1
    if span > config.MAX_FUNC_LINES:
        out.append(Finding("long-function", "info",
                           f"function '{name}' is {span} lines (>{config.MAX_FUNC_LINES})",
                           "split into smaller functions", node.lineno, "ast",
                           needs_human=True))
    return out
