"""
impl_claude.py — registration verifier (implementation kept PRIVATE).

The grading logic is proprietary and not published in this public repo. This stub
preserves the public interface: run(...) -> VerificationResult. The design, the
spec.md contracts, the tests, the flowcharts and the results are all included here
and in docs/.
"""
from __future__ import annotations

from pipeline.shared.result import VerificationResult

MODEL = "claude"
FEATURE = "registration"


def run(*args, **kwargs) -> VerificationResult:
    return VerificationResult(
        verdict="ERROR", feature=FEATURE, model=MODEL,
        notes="Verifier implementation is private. See docs/ for the design and results.",
    )
