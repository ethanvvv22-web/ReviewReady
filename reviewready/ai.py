"""Optional AI-assisted layer.

Where deterministic rules can flag an issue but not explain the *why* in
context, an LLM can produce a context-aware explanation or a fix suggestion.
It is OPTIONAL: used only if `anthropic` is installed and ANTHROPIC_API_KEY is
set; otherwise a deterministic template explanation is returned, so the
assistant always runs offline.
"""
from __future__ import annotations
import os

from .findings import Finding

MODEL = "claude-opus-4-8"


class Explainer:
    def __init__(self) -> None:
        self.client = None
        try:
            import anthropic  # noqa
            if os.environ.get("ANTHROPIC_API_KEY"):
                self.client = anthropic.Anthropic()
        except Exception:
            self.client = None

    @property
    def available(self) -> bool:
        return self.client is not None

    def explain(self, finding: Finding, code_context: str = "") -> str:
        if not self.client:
            # Deterministic fallback explanation.
            return (f"{finding.message}. {finding.suggestion}. "
                    f"(Category: {finding.category}; severity: {finding.severity}.)")
        msg = self.client.messages.create(
            model=MODEL, max_tokens=256,
            messages=[{"role": "user", "content":
                       f"Explain briefly, for a contributor, why this is an issue "
                       f"and how to fix it.\nIssue: {finding.message}\n"
                       f"Code:\n{code_context}"}],
        )
        return "".join(b.text for b in msg.content if b.type == "text").strip()
