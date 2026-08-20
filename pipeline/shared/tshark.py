"""
pipeline/shared/tshark.py
Shared tshark (Wireshark CLI) helpers used by every reference verifier.

Keeping these in one place means all five features dissect pcaps identically,
so a difference in a verdict can never be caused by a difference in how the
capture was read. Install tshark:
    Windows : winget install WiresharkFoundation.Wireshark
    Ubuntu  : sudo apt install -y tshark
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def find_tshark() -> str | None:
    """Locate tshark on PATH or in common Windows/Linux install locations."""
    found = shutil.which("tshark")
    if found:
        return found
    for candidate in (
        Path(r"C:\Program Files\Wireshark\tshark.exe"),
        Path(r"C:\Program Files (x86)\Wireshark\tshark.exe"),
        Path("/usr/bin/tshark"),
        Path("/usr/local/bin/tshark"),
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def run_tshark(tshark: str, pcap: Path, extra: list[str], null_decipher: bool = True) -> str:
    """Run tshark and return stdout.

    null_decipher=True asks Wireshark to dissect NAS-5GS assuming the null
    cipher, so cleartext initial messages (Registration Request, SUCI, etc.)
    decode even before security is established.
    """
    cmd = [tshark, "-r", str(pcap)]
    if null_decipher:
        cmd += ["-o", "nas-5gs.null_decipher:TRUE"]
    cmd += extra
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return proc.stdout or ""


def count(tshark: str, pcap: Path, display_filter: str, null_decipher: bool = True) -> int:
    """Count frames matching a tshark display filter."""
    out = run_tshark(
        tshark, pcap,
        ["-Y", display_filter, "-T", "fields", "-e", "frame.number"],
        null_decipher,
    )
    return len([ln for ln in out.splitlines() if ln.strip()])


def field_values(
    tshark: str, pcap: Path, display_filter: str, field: str, null_decipher: bool = True
) -> list[str]:
    """Return every value of `field` across frames matching `display_filter`."""
    out = run_tshark(
        tshark, pcap,
        ["-Y", display_filter, "-T", "fields", "-e", field],
        null_decipher,
    )
    values: list[str] = []
    for ln in out.splitlines():
        for v in ln.split(","):
            if v.strip():
                values.append(v.strip())
    return values


def count_msg_type(tshark: str, pcap: Path, base_filter: str, field: str, hexval: str) -> int:
    """Count frames of a given NAS message type, trying Wireshark 4.x (hyphen)
    and 3.x (underscore) field-name variants so the verifier is version-robust.
    """
    n = count(tshark, pcap, f"{field} == {hexval}")
    if n == 0 and "-" in field:
        n = count(tshark, pcap, f"{field.replace('-', '_')} == {hexval}")
    return n
