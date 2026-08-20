"""
test_pdu_session.py — TS 24.501 §6.4.1 conformance test (human-owned oracle).

Runs claude / llama3 / mistral against the latest TC-PDU-001 evidence folder
(core.pcap + n3.pcap + run.log). Claude = REFERENCE.
"""
import pytest
from pathlib import Path

from pipeline.features.pdu_session import impl_claude, impl_llama3, impl_mistral


def _latest_evidence() -> Path | None:
    root = Path(__file__).resolve().parents[4] / "evidence"
    folders = sorted(root.glob("TC-PDU-001_*"))
    return folders[-1] if folders else None


EVIDENCE = _latest_evidence()

IMPLS = [
    (impl_claude, "claude"),
    (impl_llama3, "llama3"),
    (impl_mistral, "mistral"),
]


@pytest.mark.parametrize("impl,name", IMPLS)
def test_no_pdu_reject(impl, name):
    """MUST NOT: PDU Session Establishment Reject (0xc3)."""
    if not EVIDENCE:
        pytest.skip("TC-PDU-001 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    assert result.metrics.get("pdu_reject") is False, f"[{name}] {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_user_plane_reachable(impl, name):
    """User plane: GTP-U present on N3 and ping 0% loss."""
    if not EVIDENCE:
        pytest.skip("TC-PDU-001 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    assert result.metrics.get("gtpu_frames", 0) > 0, f"[{name}] no GTP-U: {result.notes}"
    assert result.metrics.get("ping_ok") is True, f"[{name}] ping not clean: {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_overall_verdict_pass(impl, name):
    """Overall verdict must be PASS for TS 24.501 §6.4.1 conformance."""
    if not EVIDENCE:
        pytest.skip("TC-PDU-001 evidence not found under evidence/")
    result = impl.run(EVIDENCE)
    result.save_evidence(Path(__file__).parent / "evidence")
    assert result.verdict == "PASS", f"[{name}] Expected PASS, got {result.verdict}: {result.notes}"
