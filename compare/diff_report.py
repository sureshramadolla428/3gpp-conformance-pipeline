"""
compare/diff_report.py
Three-way comparison: Claude (REFERENCE) vs llama3 vs mistral.

Claude is always the gold standard.
Ollama deviations are flagged as [NEEDS CORRECTION].
Correct the Ollama impl file, re-run, repeat until all agree.

Usage:
  python compare/diff_report.py --feature suci
  python compare/diff_report.py --feature aka
  python compare/diff_report.py --all
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

# Ensure the repo root is importable when run as `python compare/diff_report.py`
# (otherwise only the compare/ folder is on sys.path and `import pipeline` fails).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Registered features — each maps to the latest matching evidence folder under
# <repo-parent>/evidence/. Add new ones here as you build them.
FEATURES = {
    "suci":         {"glob": "TC-SEC-001_*",       "ts_clause": "TS 33.501 §6.12"},
    "registration": {"glob": "TC-REG-001_*",       "ts_clause": "TS 24.501 §5.5.1"},
    "aka":          {"glob": "TC-SEC-002_*",       "ts_clause": "TS 33.501 §6.1.3.2"},
    "pdu_session":  {"glob": "TC-PDU-001_*",       "ts_clause": "TS 24.501 §6.4.1"},
    "sib1":         {"glob": "TC-SEC-003_*2PLMN*", "ts_clause": "TS 38.331 §6.3.1"},
}

EVIDENCE_ROOT = Path(__file__).resolve().parents[2] / "evidence"


def _resolve_evidence(glob_pat: str) -> Path | None:
    """Newest evidence folder matching the feature's glob under EVIDENCE_ROOT."""
    folders = sorted(EVIDENCE_ROOT.glob(glob_pat))
    if not folders and "2PLMN" in glob_pat:  # fall back to any TC-SEC-003 run
        folders = sorted(EVIDENCE_ROOT.glob("TC-SEC-003_*"))
    return folders[-1] if folders else None

MODELS = ["claude", "llama3", "mistral"]
WIDTH = 72


def _banner(text: str) -> None:
    print("═" * WIDTH)
    print(f"  {text}")
    print("═" * WIDTH)


def _load_impl(feature: str, model: str):
    """Dynamically import impl_<model>.py for a feature."""
    module_path = f"pipeline.features.{feature}.impl_{model}"
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None


def _run_impl(feature: str, model: str, evidence: Path | None):
    """Run one impl against its evidence folder; return the VerificationResult."""
    impl = _load_impl(feature, model)
    if impl is None:
        return None
    try:
        if evidence is None:
            return impl.run()
        return impl.run(evidence)
    except Exception as exc:
        from pipeline.shared.result import VerificationResult
        return VerificationResult(
            verdict="ERROR",
            feature=feature,
            model=model,
            notes=str(exc),
        )


def compare_feature(feature: str) -> bool:
    """Run all three models for a feature and print the diff report. Returns True if all agree."""
    cfg = FEATURES.get(feature)
    if cfg is None:
        print(f"Unknown feature: {feature}. Add it to FEATURES dict in diff_report.py.")
        return False

    _banner(f"FEATURE: {feature.upper()}  —  {cfg['ts_clause']}")

    evidence = _resolve_evidence(cfg["glob"])
    if evidence is None:
        print(f"  [WARN] No evidence folder matching '{cfg['glob']}' under {EVIDENCE_ROOT}")

    results = {}
    for model in MODELS:
        results[model] = _run_impl(feature, model, evidence)

    # Reference is Claude
    ref = results.get("claude")
    if ref is None:
        print("  [ERROR] Could not load impl_claude.py — fix it first.")
        return False

    print(f"\n  {'METRIC':<30} {'CLAUDE':>12} {'LLAMA3':>12} {'MISTRAL':>12}  STATUS")
    print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*12}  {'------'}")

    # Collect all metric keys across all models
    all_keys = set(ref.metrics.keys())
    for m in ["llama3", "mistral"]:
        r = results.get(m)
        if r:
            all_keys.update(r.metrics.keys())

    all_agree = True

    # Verdict row first
    verdicts = {m: (results[m].verdict if results[m] else "NOT LOADED") for m in MODELS}
    _print_row("verdict", verdicts, ref.verdict)
    if not all(v == ref.verdict for v in verdicts.values()):
        all_agree = False

    # Metric rows
    for key in sorted(all_keys):
        vals = {}
        for m in MODELS:
            r = results.get(m)
            vals[m] = str(r.metrics.get(key, "—")) if r else "NOT LOADED"
        ref_val = str(ref.metrics.get(key, "—"))
        _print_row(key, vals, ref_val)
        if not all(v == ref_val for v in vals.values()):
            all_agree = False

    print()

    # Correction notes
    for model in ["llama3", "mistral"]:
        r = results.get(model)
        if r is None:
            print(f"  ⚠  [{model.upper()}] impl not loaded — run Ollama and paste output into impl_{model}.py")
            all_agree = False
            continue
        if r.verdict == "ERROR" and "NOT IMPLEMENTED" in r.notes:
            print(f"  ⚠  [{model.upper()}] NOT YET WRITTEN")
            print(f"     → Open pipeline/features/{feature}/impl_{model}.py")
            print(f"     → Follow the instructions in the file header")
            print(f"     → Paste the Ollama output, then re-run this script")
            all_agree = False
        elif r.verdict != ref.verdict:
            print(f"  ✗  [{model.upper()}] NEEDS CORRECTION — verdict {r.verdict} ≠ REFERENCE {ref.verdict}")
            print(f"     Notes: {r.notes}")
            all_agree = False

    if all_agree:
        print(f"  ✓  All three models agree — Claude output saved as golden.")
        _save_golden(feature, ref)
    else:
        print(f"\n  RESULT: Disagreement detected. Correct Ollama impls and re-run.")

    print()
    return all_agree


def _print_row(key: str, vals: dict[str, str], ref_val: str) -> None:
    claude_v = vals.get("claude", "—")
    llama_v  = vals.get("llama3", "—")
    mistr_v  = vals.get("mistral", "—")

    agree_llama   = llama_v == ref_val
    agree_mistral = mistr_v == ref_val
    all_ok = agree_llama and agree_mistral

    status = "✅ agree" if all_ok else "⚠  DISAGREE"
    print(f"  {key:<30} {claude_v:>12} {llama_v:>12} {mistr_v:>12}  {status}")

    if not agree_llama:
        print(f"  {'':30} {'':>12} {'↑ fix':>12} {'':>12}  [NEEDS CORRECTION]")
    if not agree_mistral:
        print(f"  {'':30} {'':>12} {'':>12} {'↑ fix':>12}  [NEEDS CORRECTION]")


def _save_golden(feature: str, result) -> None:
    """Freeze Claude's output as the golden file."""
    golden_dir = Path("golden")
    golden_dir.mkdir(exist_ok=True)
    golden_path = golden_dir / f"{feature}_claude.json"
    golden_path.write_text(result.to_json())
    print(f"  → Golden saved: {golden_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Claude vs Ollama diff report")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--feature", choices=list(FEATURES.keys()), help="Single feature to compare")
    group.add_argument("--all", action="store_true", help="Compare all registered features")
    args = ap.parse_args()

    features = list(FEATURES.keys()) if args.all else [args.feature]
    results = [compare_feature(f) for f in features]

    print("═" * WIDTH)
    if all(results):
        print("  OVERALL: All features agree ✅")
    else:
        failed = [f for f, ok in zip(features, results) if not ok]
        print(f"  OVERALL: {len(failed)} feature(s) need correction: {', '.join(failed)}")
    print("═" * WIDTH)


if __name__ == "__main__":
    main()
