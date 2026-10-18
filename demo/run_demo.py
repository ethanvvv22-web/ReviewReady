"""End-to-end demo of the contribution assistant (offline, no external tools).

Run:  python -m demo.run_demo
"""
import shutil
import tempfile
from pathlib import Path

from reviewready.assistant import assess
from reviewready.summary import to_markdown, build

HERE = Path(__file__).resolve().parent.parent


def hr(t):
    print("\n" + "#" * 72 + f"\n# {t}\n" + "#" * 72)


def main():
    hr("1. A clean contribution -> REVIEW-READY")
    print(to_markdown(assess(str(HERE / "samples" / "good"))))

    hr("2. A messy contribution -> NOT READY, with actionable feedback")
    a = assess(str(HERE / "samples" / "bad"))
    print(to_markdown(a))

    hr("3. Contributor iterates: apply safe auto-fixes, then re-check")
    # a contribution whose only issues are auto-fixable (no docstring + trailing ws)
    tmp = Path(tempfile.mkdtemp())
    (tmp / "tests").mkdir()
    (tmp / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n")
    (tmp / "util.py").write_text(
        "import logging\n\n\n"
        "logger = logging.getLogger(__name__)\n\n\n"
        "def ping() -> int:\n"
        '    """Return a heartbeat value."""\n'
        "    return 1   \n", encoding="utf-8")
    before = build(assess(str(tmp)))
    after = build(assess(str(tmp), autofix=True))
    print(f"readiness before auto-fix : {before['readiness_score']}/100  "
          f"({before['gate']})")
    print(f"auto-applied fixes        : {after['auto_changed']}")
    print(f"readiness after auto-fix  : {after['readiness_score']}/100  "
          f"({after['gate']})")
    print("\nFor the messy contribution above, the remaining items are errors "
          "(missing tests, bad interface, unsafe deps) -- exactly the "
          "engineering-judgment work the assistant deliberately leaves to humans.")


if __name__ == "__main__":
    main()
