"""
pipeline/shared/result.py
Common VerificationResult returned by every impl_*.py.
Claude's output is the REFERENCE. Ollama outputs are compared against it.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass
class VerificationResult:
    # Core verdict — what the test asserts on
    verdict: str          # "PASS" | "FAIL" | "INCONCLUSIVE" | "ERROR"
    feature: str          # e.g. "suci", "aka", "sib1"
    model: str            # "claude" | "llama3" | "mistral"

    # Feature-specific metrics (populated by each impl)
    metrics: dict = field(default_factory=dict)

    # Human-readable notes and TS citation
    ts_clause: str = ""   # e.g. "TS 33.501 §6.1.3"
    notes: str = ""       # explanation of verdict

    # Auto-set at runtime
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def passed(self) -> bool:
        return self.verdict == "PASS"

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    def save_evidence(self, out_dir: Path) -> Path:
        """Write a Markdown evidence report alongside the JSON."""
        out_dir.mkdir(parents=True, exist_ok=True)

        # JSON for machine comparison
        json_path = out_dir / f"{self.model}_result.json"
        json_path.write_text(self.to_json())

        # Markdown for human reading
        md_path = out_dir / f"{self.model}_report.md"
        lines = [
            f"# {self.feature.upper()} — {self.model.capitalize()} Evidence Report",
            f"",
            f"**Clause:** {self.ts_clause}  ",
            f"**Verdict:** {self.verdict}  ",
            f"**Timestamp:** {self.timestamp}  ",
            f"",
            f"## Metrics",
            f"",
        ]
        for k, v in self.metrics.items():
            lines.append(f"- **{k}**: {v}")
        lines += ["", "## Notes", "", self.notes or "_(none)_"]
        md_path.write_text("\n".join(lines))

        return md_path
