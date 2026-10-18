"""Command-line entry point.

  python -m reviewready.cli check <path> [--fix] [--json]

Runs the pre-review assessment on a Python file or package and prints the
structured summary; --fix applies safe auto-fixes first, --json emits JSON.
"""
from __future__ import annotations
import argparse
import json
import sys

from .assistant import assess
from .summary import build, to_markdown


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="reviewready")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="assess a contribution")
    c.add_argument("path")
    c.add_argument("--fix", action="store_true", help="apply safe auto-fixes first")
    c.add_argument("--json", action="store_true", help="emit JSON")
    args = p.parse_args(argv)

    a = assess(args.path, autofix=args.fix)
    if args.json:
        print(json.dumps(build(a), indent=2))
    else:
        print(to_markdown(a))
    # exit non-zero if not review-ready (useful as a pre-commit / CI gate)
    return 0 if a.ready else 1


if __name__ == "__main__":
    sys.exit(main())
