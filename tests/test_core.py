"""Unit + integration tests (stdlib unittest).

Run:  python -m unittest discover -s tests
"""
import ast
import unittest
from pathlib import Path

from reviewready import ast_checks
from reviewready.rules import run_rules
from reviewready.fixer import apply_safe_fixes
from reviewready.assistant import assess
from reviewready.summary import build

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def cats(findings):
    return {f.category for f in findings}


class TestAstChecks(unittest.TestCase):
    def test_detects_many(self):
        src = ('import os\nfrom math import *\n\n'
               'def BadName(x, items=[]):\n'
               '    try:\n        print(x)\n    except:\n        pass\n')
        c = cats(ast_checks.analyze(src))
        for expected in ["missing-module-docstring", "unused-import", "star-import",
                         "naming-convention", "mutable-default", "bare-except",
                         "print-statement", "missing-func-docstring",
                         "missing-type-hints"]:
            self.assertIn(expected, c, expected)

    def test_clean_has_no_findings(self):
        src = '"""Doc."""\n\n\ndef add(a: int, b: int) -> int:\n    """Add."""\n    return a + b\n'
        self.assertEqual(ast_checks.analyze(src), [])

    def test_syntax_error_is_error(self):
        c = cats(ast_checks.analyze("def f(:\n"))
        self.assertTrue(c)


class TestRules(unittest.TestCase):
    def test_non_approved_dependency(self):
        c = cats(run_rules(ast.parse("import tensorflow\n"), True))
        self.assertIn("non-approved-dependency", c)

    def test_approved_and_stdlib_ok(self):
        c = cats(run_rules(ast.parse("import os\nimport numpy\n"), True))
        self.assertNotIn("non-approved-dependency", c)

    def test_interface_missing_method(self):
        src = "class FooDriver:\n    def read(self):\n        return 1\n"
        c = cats(run_rules(ast.parse(src), True))
        self.assertIn("interface-missing-method", c)

    def test_missing_tests(self):
        self.assertIn("missing-tests", cats(run_rules(ast.parse("x = 1\n"), False)))
        self.assertNotIn("missing-tests", cats(run_rules(ast.parse("x = 1\n"), True)))


class TestFixer(unittest.TestCase):
    def test_adds_docstring_without_todo(self):
        out, applied = apply_safe_fixes("x = 1")
        self.assertIn("added module docstring stub", applied)
        self.assertNotIn("TODO", out)
        ast.parse(out)  # still valid

    def test_strips_trailing_and_newline(self):
        out, applied = apply_safe_fixes('"""D."""\nx = 1   ')
        self.assertIn("removed trailing whitespace", applied)
        self.assertTrue(out.endswith("\n"))

    def test_never_breaks_broken_code(self):
        out, _ = apply_safe_fixes("def f(:\n")  # unparseable
        self.assertIsInstance(out, str)


class TestAssistant(unittest.TestCase):
    def test_good_is_ready(self):
        a = assess(str(SAMPLES / "good"))
        self.assertTrue(a.ready)
        self.assertEqual(a.readiness, 100)

    def test_bad_is_not_ready(self):
        a = assess(str(SAMPLES / "bad"))
        self.assertFalse(a.ready)
        self.assertTrue(any(f.severity == "error" for f in a.findings))

    def test_summary_shape(self):
        s = build(assess(str(SAMPLES / "bad")))
        for key in ["readiness_score", "gate", "checked", "auto_changed",
                    "needs_human_judgment", "all_findings"]:
            self.assertIn(key, s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
