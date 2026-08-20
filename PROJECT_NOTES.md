# PROJECT_NOTES.md

Guidance for Claude Code when working in this repository.

## What this project is

A 3GPP conformance verification pipeline. Each feature takes a real 3GPP TS requirement,
implements an independent reference verifier, runs it against lab evidence (pcaps / OAI logs),
and produces a cited PASS/FAIL report.

**Three-model workflow:**
- `impl_claude.py`  — written by Claude Code. This is the REFERENCE implementation.
- `impl_llama3.py`  — written by Ollama llama3 (offline). Compared against Claude.
- `impl_mistral.py` — written by Ollama mistral (offline). Compared against Claude.

`compare/diff_report.py` runs all three, flags where Ollama deviates from Claude,
and generates correction notes so Ollama can be improved over time.

## Lab setup

- OAI UE + gNB + Core (rfsim) running on Ubuntu VM
- UERANSIM + Open5GS as secondary testbed
- PCaps captured via tcpdump on Docker bridge (N2/N3/SBI interfaces)
- Offline 3GPP RAG: Ollama (llama3 + mistral) + FastAPI, no internet required

## Stack

Python 3.11. All tools run fully offline after first install.

```sh
pip install -e ".[dev]"   # install deps
pytest                    # run all feature tests
python compare/diff_report.py --feature suci   # compare Claude vs Ollama
```

## Structure

```
pipeline/
  shared/result.py          Common VerificationResult dataclass
  features/<name>/
    spec.md                 TS clause + MUST/MUST-NOT contract (YOU write)
    test_<name>.py          pytest — runs all 3 impls (YOU write, AI cannot change)
    impl_claude.py          Claude Code reference implementation
    impl_llama3.py          Ollama llama3 implementation
    impl_mistral.py         Ollama mistral implementation
    evidence/               pcaps, logs, generated reports
compare/
  diff_report.py            Claude vs Ollama diff + correction notes
golden/                     Frozen Claude outputs (regression guard)
# rag/ and labs/ are local / private, not in this public repo
# tools/gen_offline_impl.py lives in the private companion repo
```

## Key TS references

| Spec | Clause | Feature |
|------|--------|---------|
| TS 33.501 | §6.1.3 | SUCI — UE identity concealment |
| TS 33.501 | §6.1.3.2 + TS 23.003 §28.7 | 5G-AKA RES* derivation |
| TS 38.331 | §6.3.1 | SIB1 plmn-IdentityList (MOCN) |

## DO NOT MODIFY THIS SECTION WITHOUT ASKING ME

### Coding guidelines

- `impl_claude.py` is the REFERENCE. Write it to be correct, cited, and readable.
- Every impl must return a `VerificationResult` from `pipeline.shared.result`.
- Never mock pcap input in tests — always use real lab evidence files.
- Why-comments citing the TS clause on every non-obvious computation.
- All verifiers: exit 0=PASS, 1=FAIL, 2=error, 3=inconclusive (consistent with existing scripts).

### Conventions

- pcap parsing: `subprocess` + `tshark` (already installed in lab VM).
- Crypto (AKA feature): `pycryptodome` for AES-ECB Milenage.
- Tests: `pytest.mark.parametrize` over all three impls in one test function.
- Evidence reports: Markdown, saved to `pipeline/features/<name>/evidence/`.
- Golden files: saved to `golden/<feature>_claude.json` after first PASS.
