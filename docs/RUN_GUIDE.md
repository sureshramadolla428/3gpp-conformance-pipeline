# RUN GUIDE — from scratch, step by step

Everything needed to go from an empty machine to a green `diff_report --all`, in order.
Commands are Windows PowerShell. The project root is:

```
C:\Users\sures\OneDrive\Desktop\Setup Instructions\5g-conformance-pipeline
```

Legend: **[once]** = one-time setup · **[each run]** = every time you verify a capture.

---

## Part 0 — Prerequisites  [once]

| Tool | Why | Install (PowerShell) |
|---|---|---|
| Python 3.10+ | runs the pipeline | `winget install Python.Python.3.12` |
| Wireshark / tshark | dissects pcaps (verifiers call it) | `winget install WiresharkFoundation.Wireshark` |
| OAI 5G lab (on a VM) | produces the captures | (your existing OpenAirInterface setup) |
| Ollama + models | offline AI (only for the calibration half) | `winget install Ollama.Ollama` then `ollama pull llama3.1:8b` and `ollama pull mistral` |

Verify:
```powershell
python --version
tshark -v | Select-Object -First 1
ollama list        # only needed for the offline-model step
```

---

## Part 1 — Get into the project + install deps  [once]

```powershell
cd "C:\Users\sures\OneDrive\Desktop\Setup Instructions\5g-conformance-pipeline"
pip install -r requirements.txt        # pytest, pycryptodome, etc.
```

Sanity check the code imports and compiles:
```powershell
python -c "import pipeline, compare"
```

---

## Part 2 — Capture evidence on the OAI lab  [each new test]

The verifiers only analyse captures; they never touch the live network. On the Ubuntu VM,
run the test and capture pcaps + logs (see `docs/runbooks/` for the exact per-test commands).
Each test's evidence goes into its own timestamped folder, synced to:

```
C:\Users\sures\OneDrive\Desktop\Setup Instructions\evidence\<TEST-ID>_<timestamp>\
```

The verifiers auto-pick the **newest** folder matching each test ID (`TC-SEC-001_*`, `TC-REG-001_*`,
`TC-SEC-002_*`, `TC-PDU-001_*`, `TC-SEC-003_*2PLMN*`). So once new evidence lands, the steps below
use it automatically — no path editing.

---

## Part 3 — Run ONE reference verifier (optional, to eyeball a single feature)

`impl_claude.py` is the trusted reference verifier for each feature. Run one directly:

```powershell
# suci  -> expect FAIL (null-scheme SUCI, IMSI exposed)
python -m pipeline.features.suci.impl_claude        "..\evidence\TC-SEC-001_<timestamp>"
# registration -> PASS
python -m pipeline.features.registration.impl_claude "..\evidence\TC-REG-001_<timestamp>"
# pdu_session -> PASS
python -m pipeline.features.pdu_session.impl_claude  "..\evidence\TC-PDU-001_<timestamp>"
# sib1 -> PASS   (no tshark needed; parses cu/du configs)
python -m pipeline.features.sib1.impl_claude         "..\evidence\TC-SEC-003_<timestamp>_2PLMN"
# aka -> PASS    (recomputes RES* with Milenage; no tshark needed)
python -m pipeline.features.aka.impl_claude          "..\evidence\TC-SEC-002_<timestamp>"
```
Each prints the verdict + the full metrics JSON.

---

## Part 4 — Run the THREE-model comparison + freeze golden  [each run]  ★ main command

This is the one you run most. `diff_report.py` runs all three verifiers (claude / llama3 / mistral)
for every feature against the latest evidence, prints a side-by-side table, and — when all three
agree — freezes the Claude result as `golden\<feature>_claude.json`.

```powershell
python compare\diff_report.py --all           # all five features
# or one feature:
python compare\diff_report.py --feature suci
```
Expected: **OVERALL: All features agree ✅** and five golden files written.

---

## Part 5 — Run the human-owned test oracle  [each run]

```powershell
pytest -q
```
The tests assert the conformance criteria independently of the verifiers. Green = the evidence still
conforms (or, for suci, correctly fails on the known null-scheme defect).

---

## Part 6 — (Offline AI) generate + calibrate the offline verifiers  [when adding/refreshing]

This is the RAG half. It uses your local Ollama + the 3GPP-spec/failure-log RAG to *draft* the
offline verifiers, which you then calibrate against the reference. Requires Ollama running.

```powershell
# 1) generate a draft for one feature/model (writes impl_<model>.generated.py, does NOT overwrite the real file)
# The generator lives in a private companion repo (not in this public tree).
python tools\gen_offline_impl.py --feature suci --model llama3
# or all features:
python tools\gen_offline_impl.py --all --model llama3
python tools\gen_offline_impl.py --all --model mistral --ollama-model "mistral:latest"

# 2) review each pipeline\features\<f>\impl_<model>.generated.py, paste its run() into impl_<model>.py
# 3) compare + correct until they agree:
python compare\diff_report.py --all
```
See `docs/OLLAMA_CALIBRATION.md` for the loop and `docs/CALIBRATION_LOG.md` for what the models
typically get wrong.

---

## Part 7 — Add a NEW test case  [to extend]

1. `mkdir pipeline\features\<newfeature>` and add `__init__.py` + an `evidence\` folder.
2. Write `spec.md` (the human contract: MUST / MUST NOT + metric keys + verdict logic).
3. Write `impl_claude.py` (reference) + `test_<newfeature>.py`; add `impl_llama3.py` / `impl_mistral.py`
   (start from stubs, or generate with `tools\gen_offline_impl.py` from the private companion repo).
4. Register it in `compare\diff_report.py` (add to the `FEATURES` dict with its evidence glob + TS clause).
5. Capture evidence, then run Parts 4–5.

---

## Command cheat-sheet

| Goal | Command |
|---|---|
| install deps | `pip install -r requirements.txt` |
| one feature, reference only | `python -m pipeline.features.<f>.impl_claude "<evidence folder>"` |
| **all features, 3-way compare, freeze golden** | `python compare\diff_report.py --all` |
| run the test oracle | `pytest -q` |
| generate offline drafts | `python tools\gen_offline_impl.py --all --model llama3` (private companion repo) |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: pipeline` | run from the repo root; `diff_report.py` already fixes its own path |
| `pytest` not found | `pip install pytest` then `python -m pytest -q` |
| verifier says `tshark not found` | install Wireshark; ensure `tshark` is on PATH |
| aka: `pip install pycryptodome` | `pip install pycryptodome` |
| a filter reads 0 unexpectedly | Wireshark field-name version diff — the verifiers try hyphen + underscore; confirm the field with `tshark -G fields \| findstr <name>` |
| offline model 404 | `ollama list` for the exact tag, pass `--ollama-model "<tag>"` or `ollama pull <model>` |
