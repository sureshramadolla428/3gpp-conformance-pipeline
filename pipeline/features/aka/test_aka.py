"""
test_aka.py — TS 33.501 §6.1.3.2 conformance test (human-owned oracle).

Runs claude / llama3 / mistral against the latest TC-SEC-002 evidence folder
(aka_inputs.txt + amf.log + aka_observed.txt). Claude = REFERENCE.
"""
import pytest
from pathlib import Path

from pipeline.features.aka import impl_claude, impl_llama3, impl_mistral


def _latest_evidence() -> Path | None:
    root = Path(__file__).resolve().parents[4] / "evidence"
    folders = sorted(root.glob("TC-SEC-002_*"))
    return folders[-1] if folders else None


EVIDENCE = _latest_evidence()

IMPLS = [
    (impl_claude, "claude"),
    (impl_llama3, "llama3"),
    (impl_mistral, "mistral"),
]


@pytest.mark.parametrize("impl,name", IMPLS)
def test_no_auth_reject(impl, name):
    """MUST NOT: Authentication Reject / MAC failure."""
    if not EVIDENCE:
        pytest.skip("TC-SEC-002 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    assert result.metrics.get("auth_reject") is False, f"[{name}] {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_res_star_matches(impl, name):
    """RES* recomputed offline must match the network's HXRES*."""
    if not EVIDENCE:
        pytest.skip("TC-SEC-002 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    assert result.metrics.get("res_star_match") is True, f"[{name}] {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_overall_verdict_pass(impl, name):
    """Overall verdict must be PASS for TS 33.501 §6.1.3.2 conformance."""
    if not EVIDENCE:
        pytest.skip("TC-SEC-002 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    result.save_evidence(Path(__file__).parent / "evidence")
    assert result.verdict == "PASS", f"[{name}] Expected PASS, got {result.verdict}: {result.notes}"
