"""
test_registration.py — TS 24.501 §5.5.1 conformance test (human-owned oracle).

Runs claude / llama3 / mistral against the latest TC-REG-001 capture and
asserts the initial registration completed. Claude = REFERENCE.
"""
import pytest
from pathlib import Path

from pipeline.features.registration import impl_claude, impl_llama3, impl_mistral


def _latest_pcap() -> Path | None:
    """Newest TC-REG-001 evidence capture under <repo-parent>/evidence/."""
    root = Path(__file__).resolve().parents[4] / "evidence"
    folders = sorted(root.glob("TC-REG-001_*"))
    return (folders[-1] / "core.pcap") if folders else None


PCAP = _latest_pcap()

IMPLS = [
    (impl_claude, "claude"),
    (impl_llama3, "llama3"),
    (impl_mistral, "mistral"),
]


@pytest.mark.parametrize("impl,name", IMPLS)
def test_signalling_present(impl, name):
    """N2 must carry NGAP + NAS-5GS frames."""
    if not PCAP or not PCAP.exists():
        pytest.skip("TC-REG-001 core.pcap not found under evidence/")
    result = impl.run(PCAP)
    assert result.verdict != "ERROR", f"[{name}] {result.notes}"
    assert result.verdict != "INCONCLUSIVE", f"[{name}] {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_no_registration_reject(impl, name):
    """MUST NOT: Registration Reject (0x44)."""
    if not PCAP or not PCAP.exists():
        pytest.skip("TC-REG-001 core.pcap not found under evidence/")
    result = impl.run(PCAP)
    assert result.metrics.get("reg_reject") is False, f"[{name}] {result.notes}"


@pytest.mark.parametrize("impl,name", IMPLS)
def test_overall_verdict_pass(impl, name):
    """Overall verdict must be PASS for TS 24.501 §5.5.1 conformance."""
    if not PCAP or not PCAP.exists():
        pytest.skip("TC-REG-001 core.pcap not found under evidence/")
    result = impl.run(PCAP)
    result.save_evidence(Path(__file__).parent / "evidence")
    assert result.verdict == "PASS", f"[{name}] Expected PASS, got {result.verdict}: {result.notes}"
