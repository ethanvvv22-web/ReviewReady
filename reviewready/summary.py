"""Structured pre-review summary: what was checked, what changed, and what
still needs human engineering judgment."""
from __future__ import annotations
from collections import Counter

from .assistant import Assessment


def build(assessment: Assessment) -> dict:
    a = assessment
    by_cat = Counter(f.category for f in a.findings)
    by_sev = Counter(f.severity for f in a.findings)
    needs_human = [f for f in a.findings if f.needs_human
                   or f.severity == "error"]
    return {
        "readiness_score": a.readiness,
        "gate": "REVIEW-READY" if a.ready else "NOT READY",
        "counts_by_severity": dict(by_sev),
        "counts_by_category": dict(by_cat),
        "checked": _checked(a),
        "auto_changed": a.applied_fixes,
        "needs_human_judgment": [f.as_dict() for f in needs_human],
        "all_findings": [f.as_dict() for f in a.findings],
    }


def _checked(a: Assessment) -> dict:
    checked = {"built-in ast checks": "ran", "framework rules": "ran"}
    checked.update(a.tool_status)
    return checked


def to_markdown(assessment: Assessment) -> str:
    s = build(assessment)
    L = [f"# Pre-Review Summary",
         f"**Gate:** {s['gate']}  |  **Readiness:** {s['readiness_score']}/100  "
         f"|  severity {s['counts_by_severity']}", ""]
    L.append("## What was checked")
    for k, v in s["checked"].items():
        L.append(f"- {k}: {v}")
    L.append("\n## What was auto-changed")
    L += [f"- {x}" for x in s["auto_changed"]] or ["- (nothing auto-applied)"]
    L.append("\n## Needs human engineering judgment")
    if s["needs_human_judgment"]:
        for f in s["needs_human_judgment"]:
            L.append(f"- [{f['severity']}] {f['file']}:{f['line']} "
                     f"{f['message']} -> {f['suggestion']}")
    else:
        L.append("- (none - routine issues only)")
    L.append("\n## Contributor action list (top items)")
    for f in s["all_findings"][:10]:
        tag = "auto-fixable" if f["auto_fixable"] else "manual"
        L.append(f"- [{f['severity']}/{tag}] {f['file']}:{f['line']} "
                 f"{f['message']} -> {f['suggestion']}")
    return "\n".join(L)
