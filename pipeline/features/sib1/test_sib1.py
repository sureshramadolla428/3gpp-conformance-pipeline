"""
test_sib1.py — TS 38.331 §6.3.1 conformance test (human-owned oracle).

Runs claude / llama3 / mistral against the latest 2-PLMN TC-SEC-003 evidence
(cu.conf + du.conf + f1.pcap). Claude = REFERENCE.
"""
import pytest
from pathlib import Path

from pipeline.features.sib1 import impl_claude, impl_llama3, impl_mistral


def _latest_evidence() -> Path | None:
    root = Path(__file__).resolve().parents[4] / "evidence"
    # prefer the multi-PLMN run; fall back to any TC-SEC-003 folder
    folders = sorted(root.glob("TC-SEC-003_*2PLMN*")) or sorted(root.glob("TC-SEC-003_*"))
    return folders[-1] if folders else None


EVIDENCE = _latest_evidence()

IMPLS = [
    (impl_claude, "claude"),
    (impl_llama3, "llama3"),
    (impl_mistral, "mistral"),
]


@pytest.mark.parametrize("impl,name", IMPLS)
def test_no_order_mismatch(impl, name):
    """MUST NOT: CU/DU first-PLMN mismatch (the Gate-2 fault)."""
    if not EVIDENCE:
        pytest.skip("TC-SEC-003 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    assert result.metrics.get("plmn_order_mismatch") is False, f"[{name}] {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_overall_verdict_pass(impl, name):
    """Overall verdict must be PASS for TS 38.331 §6.3.1 conformance."""
    if not EVIDENCE:
        pytest.skip("TC-SEC-003 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    result.save_evidence(Path(__file__).parent / "evidence")
    assert result.verdict == "PASS", f"[{name}] Expected PASS, got {result.verdict}: {result.notes}"
