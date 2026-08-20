# 3GPP LTE, 5G and 6G Pipeline

### Offline 3GPP conformance grading with a three-verifier cross-check

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Wireshark](https://img.shields.io/badge/tshark-Wireshark-1679A7?logo=wireshark&logoColor=white)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-llama3%20%C2%B7%20mistral-000000?logo=ollama&logoColor=white)
![3GPP](https://img.shields.io/badge/3GPP-TS%2033.501%20%C2%B7%2024.501%20%C2%B7%2038.331-005BAC)
> â„¹ï¸ The RAG generator and lab/RAG internals live in a **private companion repo**. This public repo is the conformance pipeline: spec contracts, three-model verifiers, compare, golden, tests, and docs.

Offline **3GPP LTE / 5G / 6G conformance verification**: run three independent graders on the same lab evidence, compare them, and freeze a golden result when they agree.

The three implementations are intentional:

| Role | Module |
|------|--------|
| **Reference** | `impl_claude.py` |
| **Offline model A** | `impl_llama3.py` |
| **Offline model B** | `impl_mistral.py` |

Claude-vs-open-source comparison is part of the design. Do not strip `claude` names or files.

---

## Flow

```mermaid
flowchart TD
    A["OAI 5G / NTN lab<br/>gNB Â· nrUE Â· CN5G"] --> B["capture evidence<br/>pcap + logs + configs"]
    B --> C["spec.md contract<br/>TS clause, must / must not"]
    C --> D1["impl_claude (reference)"]
    C --> D2["impl_llama3 (offline / RAG)"]
    C --> D3["impl_mistral (offline / RAG)"]
    D1 --> E["diff_report<br/>compare 3 verdicts"]
    D2 --> E
    D3 --> E
    E -->|disagree| F["correct offline, re-run"]
    F -.-> D2
    F -.-> D3
    E -->|all agree| G["golden + pytest / CI"]
    classDef ref fill:#dafbe1,stroke:#2da44e;
    classDef off fill:#fff8c5,stroke:#d4a72c;
    class D1,G ref;
    class D2,D3 off;
```

Diagrams: [pipeline flow](docs/pipeline_flowchart.svg) Â· [system architecture](docs/system_architecture.svg) Â· full setup story: [docs/SETUP_AND_ARCHITECTURE.md](docs/SETUP_AND_ARCHITECTURE.md)

## Results

Real runs with three-model agreement. Full write-up: [docs/RESULTS.md](docs/RESULTS.md). All five features graded; SUCI defect caught; golden frozen.

![diff_report: SUCI and Registration](docs/screenshots/01-diffreport-suci-registration.png)

Three-way `diff_report --all`: SUCI FAIL on null-scheme (IMSI in cleartext) and Registration PASS.

![diff_report: AKA and PDU session](docs/screenshots/02-diffreport-aka-pdusession.png)

Three-way `diff_report --all`: 5G-AKA PASS (RES* matches HXRES*) and PDU Session PASS.

![diff_report: SIB1, overall, and SUCI standalone](docs/screenshots/03-diffreport-sib1-overall-suci.png)

SIB1/MOCN PASS, overall agreement, plus standalone SUCI verifier FAIL with the TS 33.501 note.

![standalone: Registration and AKA](docs/screenshots/04-standalone-registration-aka.png)

Standalone Registration PASS and 5G-AKA PASS against captured evidence folders.

![standalone: PDU session and SIB1](docs/screenshots/05-standalone-pdu-sib1.png)

Standalone PDU Session PASS (GTP-U + ping) and SIB1 PASS (CU/DU PLMN order).

---


## What it checks

Each feature lives under `pipeline/features/<name>/` with the three impls, tests, and `evidence/`.

| Feature | Test ID | Clause (see runbooks) |
|---------|---------|------------------------|
| SUCI concealment | TC-SEC-001 | TS 33.501 Â§6.12 / Â§6.1.3 |
| Registration | TC-REG-001 | TS 24.501 Â§5.5.1 |
| 5G-AKA (RES*) | TC-SEC-002 | TS 33.501 Â§6.1.3.2 |
| PDU session | TC-PDU-001 | TS 24.501 Â§6.4.1 |
| SIB1 / multi-PLMN order | TC-SEC-003 | TS 38.331 Â§6.3.1 |

Verifiers read captures/logs. They do not control the live RAN. Raw pcaps for a run usually sit next to the repo under `../evidence/<TEST-ID>_<timestamp>/` (see `docs/RUN_GUIDE.md`).

---

## Layout

```
5g-conformance-pipeline/
â”œâ”€â”€ compare/diff_report.py          # three-way compare + golden freeze
â”œâ”€â”€ golden/                         # frozen Claude JSON (regression guard)
â”œâ”€â”€ pipeline/
â”‚   â”œâ”€â”€ shared/                     # VerificationResult, tshark helpers
â”‚   â””â”€â”€ features/<name>/
â”‚       â”œâ”€â”€ impl_claude.py
â”‚       â”œâ”€â”€ impl_llama3.py
â”‚       â”œâ”€â”€ impl_mistral.py
â”‚       â”œâ”€â”€ test_<name>.py
â”‚       â””â”€â”€ evidence/               # last compare artefacts (keep in git)
â””â”€â”€ docs/                           # explainer, run guide, runbooks
```

Offline verifier generation (`gen_offline_impl.py` and the local 3GPP RAG) lives in a **private companion repo**, not in this public tree.

---

## Workflow

1. Capture evidence on the OAI lab (runbooks in `docs/runbooks/`).
2. Run one reference verifier (optional):

```powershell
python -m pipeline.features.suci.impl_claude "..\evidence\TC-SEC-001_<timestamp>"
```

3. Compare all three models (main command):

```powershell
pip install -r requirements.txt
python compare\diff_report.py --all
python compare\diff_report.py --feature suci
```

When all three agree, `diff_report.py` writes `golden/<feature>_claude.json`.

4. Regression / human oracle:

```powershell
pytest -q
```

---

## Setup

- Python 3.10+
- Wireshark / `tshark` on PATH (pcap features)
- `pycryptodome` for AKA (Milenage AES)
- Optional: Ollama (`llama3.1`, `mistral`) only if you regenerate offline impls (private companion)

```powershell
cd "C:\Users\sures\OneDrive\Desktop\Setup Instructions\5g-conformance-pipeline"
pip install -r requirements.txt
```

More detail: [`docs/RUN_GUIDE.md`](docs/RUN_GUIDE.md) Â· [`docs/EXPLAINER.md`](docs/EXPLAINER.md)

---

## Honesty

- Lab / RFsim evidence, not an over-the-air certification campaign.
- `impl_claude` is the trusted reference. Offline models draft; humans correct until the three-way report agrees.
- A SUCI **FAIL** on null-scheme (IMSI in the clear) is a real lab finding, not a decoder bug.

---


---

## License / Rights

All Rights Reserved. This public repository is a showcase; see LICENSE. No permission is granted to use, copy, modify, or distribute any part of this repository without prior written consent.

## Author

Suresh Ramadolla

