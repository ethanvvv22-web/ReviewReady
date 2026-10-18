# ReviewReady - a Semi-Automated Contribution Assistant

Give a Python contribution an initial quality assessment **before** it reaches a
human reviewer: run deterministic SE tools, framework-specific rules, and
(optionally) AI-assisted explanations; give clear, actionable feedback; apply
safe fixes; and produce a structured **pre-review summary** separating routine
issues from the work that still needs human engineering judgment.

Reference prototype for the Ericsson validation-framework thesis (Req ID 790665).
Runs offline on the standard library; external tools are used when present.

## Pipeline

```
contribution ─► [1] deterministic tools (format/lint/type/test/static analysis)
             ─► [2] framework rules (docs, interfaces, deps, tests, structure)
             ─► [3] AI-assisted explanations (optional, where rules fall short)
             ─► [4] safe auto-fixes ─► iterate ─► [5] pre-review summary + gate
```

## JD keyword -> where it lives

| JD area | Module |
|---|---|
| formatting, linting, type checking, testing, static analysis | [reviewready/tools.py](reviewready/tools.py) (ruff/black/mypy/pytest/bandit when installed) + [reviewready/ast_checks.py](reviewready/ast_checks.py) (zero-dep fallback) |
| docs, interfaces, structure, dependencies, guideline compliance | [reviewready/rules.py](reviewready/rules.py) |
| clear, actionable feedback | [reviewready/findings.py](reviewready/findings.py) (what / where / why / fix) |
| suggest or auto-apply fixes + iterate | [reviewready/fixer.py](reviewready/fixer.py) |
| AI-assisted context-aware explanations | [reviewready/ai.py](reviewready/ai.py) (optional, offline fallback) |
| structured pre-review summary (checked / changed / needs human) | [reviewready/summary.py](reviewready/summary.py) |
| evaluate: issues, false positives, reviewer time, iterations, quality, usability | [eval/run_eval.py](eval/run_eval.py), [eval/corpus.py](eval/corpus.py) |
| practical prototype on real contributions | [reviewready/cli.py](reviewready/cli.py) - `reviewready check <path>` |

## Quick start

```bash
pip install -r requirements.txt            # only scikit-learn, for the eval

python -m reviewready.cli check samples/bad           # assess a contribution
python -m reviewready.cli check samples/bad --fix     # apply safe fixes first
python -m reviewready.cli check samples/good --json   # machine-readable summary

python -m demo.run_demo                 # clean vs messy + iterate story
python -m eval.run_eval                 # metrics vs a no-assistant baseline
python -m unittest discover -s tests    # 13 tests
```

The CLI exits non-zero when a contribution is not review-ready, so it drops
straight into a pre-commit hook or CI gate.

## Measured result (12-contribution labeled corpus)

| Metric | Value |
|---|---|
| Detection precision / recall / F1 (scikit-learn) | 1.00 / 1.00 / 1.00 |
| False positives | 0 |
| Routine issues caught before human review | 17 |
| Reviewer time shifted off the human (model) | ~43 min |
| Est. review iterations saved (model) | ~5.7 rounds |
| Safe auto-fixes applied | 13 |

> Honest framing for the thesis: detection is near-perfect **by construction** -
> the corpus is crafted with known planted issues, so deterministic rules are
> expected to catch them. The meaningful signals here are the **zero false
> positives** and the **reviewer-effort** model; the thesis step is to validate
> on **real validation-framework contributions** and measure contributor effort,
> reviewer time, iterations, and usability empirically.

## Roadmap to thesis depth

Real contribution corpus + human-labeled issues · wire real ruff/mypy/pytest/
bandit and reconcile overlaps · richer framework rules from the actual guidelines
· LLM explanations + fix suggestions with guardrails · usability study with
contributors and reviewers · measure reviewer time and iteration counts before/
after in a real review workflow.
