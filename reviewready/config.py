"""Framework guidelines the assistant enforces (what a real validation
framework would put in its contribution guide)."""

MAX_LINE = 100
MAX_FUNC_LINES = 40          # complexity proxy
MIN_DOCSTRING_WORDS = 3

# Dependency allow-list: stdlib is always fine; third-party must be approved.
APPROVED_THIRD_PARTY = {"numpy", "pandas", "requests", "pydantic", "pyyaml"}

# Interface rule: classes whose name ends with 'Driver' must implement these.
DRIVER_REQUIRED_METHODS = {"open", "close", "read"}

# Reviewer-time model (minutes a reviewer spends per issue if it reaches them).
TIME_PER_SEVERITY = {"error": 5.0, "warning": 2.0, "info": 0.5}
ISSUES_PER_REVIEW_ROUND = 3   # used to estimate review iterations saved
