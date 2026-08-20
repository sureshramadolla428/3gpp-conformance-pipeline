"""
test_suci.py — TS 33.501 §6.1.3 conformance test
YOU wrote this. AI modifies ONLY under your explicit written authorization.

Runs all three implementations against the same pcap.
Claude = REFERENCE. Ollama outputs compared against it.

Change log:
  2026-08-05: added test_suci_not_null_scheme (null-scheme prohibition), applied by AI
              under explicit written authorization from the owner (Basha). Strengthens
              the oracle — TC-SEC-001 evidence will correctly FAIL while a null-scheme
              SUCI (IMSI exposed) is in use, until real concealment is provisioned.
"""
import pytest
from pathlib import Path
from pipeline.features.suci import impl_claude, impl_llama3, impl_mistral

# Real lab pcap — copy from 3GPP_Spec_Test/Input/AMF.pcapng
PCAP = Path(__file__).parent / "evidence" / "AMF.pcapng"

IMPLS = [
    (impl_claude,  "claude"),
    (impl_llama3,  "llama3"),
    (impl_mistral, "mistral"),
]


@pytest.mark.parametrize("impl,name", IMPLS)
def test_nas_control_plane_present(impl, name):
    """N2 interface must carry NAS-5GS / NGAP frames. TS 33.501 §6.1.3."""
    if not PCAP.exists():
        pytest.skip(f"pcap not found — copy AMF.pcapng to {PCAP}")
    result = impl.run(pcap=PCAP)
    assert result.verdict != "ERROR", f"[{name}] impl errored: {result.notes}"
    assert result.verdict != "INCONCLUSIVE", (
        f"[{name}] No NAS frames found — re-capture during UE attach. "
        f"Notes: {result.notes}"
    )


@pytest.mark.parametrize("impl,name", IMPLS)
def test_security_mode_command_present(impl, name):
    """NAS Security Mode Command (0x5d) must be present. TS 24.501 §5.4.2."""
    if not PCAP.exists():
        pytest.skip(f"pcap not found — copy AMF.pcapng to {PCAP}")
    result = impl.run(pcap=PCAP)
    assert result.metrics.get("security_mode_command") is True, (
        f"[{name}] Security Mode Command not found. Notes: {result.notes}"
    )


@pytest.mark.parametrize("impl,name", IMPLS)
def test_security_mode_complete_present(impl, name):
    """NAS Security Mode Complete (0x5e) must be present. TS 24.501 §5.4.2."""
    if not PCAP.exists():
        pytest.skip(f"pcap not found — copy AMF.pcapng to {PCAP}")
    result = impl.run(pcap=PCAP)
    assert result.metrics.get("security_mode_complete") is True, (
        f"[{name}] Security Mode Complete not found. Notes: {result.notes}"
    )


@pytest.mark.parametrize("impl,name", IMPLS)
def test_suci_present_in_registration(impl, name):
    """UE must use SUCI (not clear IMSI) on Registration. TS 33.501 §6.1.3."""
    if not PCAP.exists():
        pytest.skip(f"pcap not found — copy AMF.pcapng to {PCAP}")
    result = impl.run(pcap=PCAP)
    assert result.metrics.get("suci_frames", 0) > 0, (
        f"[{name}] No SUCI IE found. UE may be sending clear IMSI. "
        f"Notes: {result.notes}"
    )


@pytest.mark.parametrize("impl,name", IMPLS)
def test_suci_not_null_scheme(impl, name):
    """SUCI MUST NOT use the null protection scheme (scheme id 0).

    A null-scheme SUCI carries the SUPI (IMSI) in cleartext inside the SUCI, so it
    provides no identifier privacy even though the identity type decodes as SUCI.
    TS 33.501 §6.12 + Annex C.  Added 2026-08-05 under owner authorization.
    """
    if not PCAP.exists():
        pytest.skip(f"pcap not found — copy AMF.pcapng to {PCAP}")
    result = impl.run(pcap=PCAP)
    assert result.metrics.get("null_scheme_frames", 0) == 0, (
        f"[{name}] SUCI uses NULL protection scheme — IMSI exposed in cleartext. "
        f"null_scheme_frames={result.metrics.get('null_scheme_frames')}. "
        f"Provision a home-network key (ECIES profile A/B) so a real scheme is used. "
        f"Notes: {result.notes}"
    )


@pytest.mark.parametrize("impl,name", IMPLS)
def test_overall_verdict_pass(impl, name):
    """Overall verdict must be PASS for TS 33.501 §6.1.3 conformance."""
    if not PCAP.exists():
        pytest.skip(f"pcap not found — copy AMF.pcapng to {PCAP}")
    result = impl.run(pcap=PCAP)
    # Save evidence report every run
    evidence_dir = Path(__file__).parent / "evidence"
    result.save_evidence(evidence_dir)
    assert result.verdict == "PASS", (
        f"[{name}] Expected PASS, got {result.verdict}. Notes: {result.notes}"
    )
