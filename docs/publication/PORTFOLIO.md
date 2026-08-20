# Portfolio Guide — 5G 3GPP Conformance Pipeline + NTN Lab

Two projects, one narrative: you built a **spec-to-evidence conformance factory** on top of a
**fully verified 5G NTN lab** — then added a three-model LLM calibration loop so offline AI
(Ollama) stays anchored to spec-correct Claude output.

---

## Positioning note — this is a SENIOR portfolio (15+ years)

At 15 years in wireless, no reviewer doubts you can bring up a 5G stack — they assume it. So this
project must **not** read as "I set up a lab." It has to read as: *deep protocol debugging + modern
test automation*, the combination that is genuinely hard to hire for.

Lead everywhere with the two **root-cause investigations**, not the setup:

1. **5G-AKA Gate-2** — PLMN-order divergence between CU and DU SIB1 → wrong Serving Network Name →
   RES\* ≠ XRES\* → Authentication Reject. (Control-plane / security.)
2. **NTN F1 handover post-HO user-plane loss** — CU switches F1-U GTP to the target DU and marks HO
   "complete" via *source release*, but the UE never acquires the target PCI radio; tunnel stays up
   over a dead radio → 100% post-HO ping loss. Correctly distinguished a **degraded** "marking HO as
   complete" from a **true** "handover complete!" — and refused to overclaim. (RAN / mobility.)

Then the **automation** (spec → test → evidence → CI) and the **offline LLM calibration** show you
pair that depth with current software-engineering discipline. That pairing is the differentiator.
The "I brought up OAI" part is table stakes — keep it in the background.

**Where this lands best:** conformance / test-automation / protocol-validation roles at test vendors
(Keysight, Rohde & Schwarz), silicon/modem test teams (Qualcomm, MediaTek), or RAN/core vendors
(Nokia, Ericsson, Samsung). It lands weakest for pure RF-planning or radio-optimization roles —
lean on the protocol-depth angle there and downplay the tooling.

---

## 1. Resume

### Project title (pick one)

> **5G SA 3GPP Conformance Verification Pipeline — OpenAirInterface + LLM Calibration Loop**

> **5G Non-Terrestrial Network (LEO) Conformance Lab — OAI + Automated 3GPP Evidence Factory**

### Bullet points

Paste these under a single project entry. Trim to 4–5 for a tight resume; keep all for a CV.

---

- Built a **spec-to-evidence conformance pipeline** against 3GPP TS 33.501 and TS 38.331 on a live
  OpenAirInterface 5G SA stack: each feature maps a TS clause → `spec.md` contract → a cited Python
  verifier → `pytest` gate → JSON + Markdown evidence report — covering **SUCI privacy
  (TS 33.501 §6.1.3)**, **5G-AKA / Milenage RES\* derivation (TS 33.501 §6.1.3.2)**, and
  **Multi-PLMN SIB1 / MOCN ordering (TS 38.331 §6.3.1)**.

- Root-caused a **5G-AKA Gate-2 authentication failure** to a PLMN order inversion (CU had
  20893 first, DU SIB1 had 001/01 first → UE derived wrong Serving Network Name → RES\* ≠ XRES\*)
  and hardened it as an automated regression guard using `pycryptodome` Milenage and tshark pcap
  parsing — failure reproducible in < 30 s, guard runs on every commit via GitHub Actions CI.

- Root-caused an **NTN F1 handover post-HO user-plane blackhole** through a controlled 6-hypothesis
  investigation: on the SAT_LEO dual-DU RFsim topology the CU correctly switches the F1-U GTP tunnel
  to the target DU (`127.0.0.5:2153`) and the UE applies the HO reconfiguration, but the UE never
  acquires the target-cell radio (`synch Failed` storm, target PCI never reached), so the CU marks
  HO "complete" only via **source release** while `oaitun_ue1` stays up over a dead radio → 100%
  post-HO ping loss. Isolated the cause to an **RFsim multi-client limitation** (proven-LEO uses a
  DU-as-server topology, proven-HO uses a UE-as-server topology) — refuting F1-U routing, GTP port
  collision, and CU tunnel-update hypotheses with packet/log evidence — and distinguished a
  **degraded** "marking HO as complete" from a **true** "handover complete!" to prevent a false PASS.

- Designed a **three-model LLM calibration loop**: Claude Code writes `impl_claude.py` as the
  3GPP-cited reference implementation; Ollama (llama3 + mistral) generates offline counterparts;
  `diff_report.py` flags per-metric deviations as `[NEEDS CORRECTION]` and freezes `golden/*.json`
  only when all three agree — progressively calibrating offline RAG to spec-correct output without
  internet dependency.

- Built and verified a fully **software-only 5G LEO Non-Terrestrial Network** (OAI gNB + nrUE +
  RFsimulator `SAT_LEO_TRANS` + OAI CN5G): full call flow — RACH → RRC → 5G-AKA → Registration →
  PDU session → GTP-U → **ping at 0% loss, ~32 ms RTT** over a 600 km moving LEO satellite with
  time-varying delay and ~37 kHz Doppler; 3GPP Rel-17 NTN mechanisms end-to-end (SIB19, ta-Common,
  Koffset, Doppler pre-compensation).

- Authored **6 new NTN conformance test cases** (TC-NTN-001 to TC-NTN-006) covering SIB19 encoding
  verification, 5G-AKA Gate-2 regression guard, SUCI during NTN attach, F1 handover in AWGN, and
  dynamic NTN timing hot-reload — with automated evidence capture (pcap + logs) synced to Windows
  via VMware shared folder, organized by test case ID and timestamp.

- Upgraded orbit tooling to **real SGP4** over the **live Starlink constellation (~10,700 TLEs)**;
  implemented **3GPP-style satellite handover** (hysteresis + time-to-trigger) reducing churn from
  ~68 to ~10 handovers over 20 min at identical coverage; built NTN-aware AIOps (access-regime
  classifier, anomaly detector, handover-time predictor, sync-loss detector).

---

### Skills line

```
5G SA · NTN (3GPP Rel-17/18) · 3GPP conformance testing · protocol root-cause analysis
· F1 handover / mobility · OpenAirInterface (gNB / nrUE / CN5G) · TS 33.501 · TS 38.331 · TS 38.401
· 5G-AKA / Milenage · SUCI · PLMN / MOCN · SIB1 / SIB19 · F1-U / GTP-U · tshark / Wireshark
· Python (pytest, pycryptodome) · CI/CD (GitHub Actions) · Ollama (llama3, mistral) · LLM calibration
· SGP4 · satellite handover · Docker · Prometheus / Grafana / Loki · pcap evidence
```

---

## 2. GitHub

### Two repos (or one monorepo)

**Option A — Monorepo** (recommended if both projects are in the same folder):
```
5g-oai-lab/
├── 5g-ntn-emulation-lab/    ← NTN + AIOps + orbit tooling
└── 5g-conformance-pipeline/ ← spec-to-evidence + LLM calibration
```

**Option B — Two separate repos**:
- `5g-ntn-emulation-lab` (already named)
- `5g-conformance-pipeline`

---

### README for `5g-conformance-pipeline`

Copy this as your `README.md`:

---

```markdown
# 5G 3GPP Conformance Verification Pipeline

Automated spec-to-evidence conformance checks on a live OpenAirInterface 5G SA stack,
with a three-model LLM calibration loop (Claude → Ollama llama3/mistral).

[![CI](https://github.com/<your-handle>/5g-conformance-pipeline/actions/workflows/ci.yml/badge.svg)](...)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](...)
[![3GPP TS 33.501](https://img.shields.io/badge/3GPP-TS%2033.501-green)](...)

## What this does

```
TS clause → spec.md → impl_claude.py (REFERENCE) → pytest → evidence JSON + Markdown
                              ↓
              diff_report.py compares Claude vs llama3 vs mistral
                              ↓
              golden/*.json frozen when all three agree
```

## Features

| Feature | Spec | Status |
|---------|------|--------|
| SUCI privacy verification | TS 33.501 §6.1.3 | ✅ impl + tests |
| 5G-AKA RES\* / Milenage | TS 33.501 §6.1.3.2 | 🔧 in progress |
| Multi-PLMN SIB1 / MOCN | TS 38.331 §6.3.1 | 🔧 in progress |
| NTN SIB19 encoding | TS 38.331 §6.3.1 | 📋 TC-NTN-002 |

## Quick start

```bash
pip install -r requirements.txt
# Copy your AMF.pcapng to pipeline/features/suci/evidence/
pytest pipeline/features/suci/ -k claude -v
```

## Three-model calibration loop

Claude writes `impl_claude.py` first — spec-cited, tested, correct.
Ollama (offline) writes `impl_llama3.py` and `impl_mistral.py`.
`diff_report.py` shows exactly where they diverge:

```
python compare/diff_report.py --feature suci
```

Output:
```
  METRIC                         CLAUDE       LLAMA3      MISTRAL   STATUS
  verdict                          PASS         FAIL         PASS   ⚠ DISAGREE
  suci_frames                         3            0            3   ⚠ DISAGREE
                                            ↑ fix               [NEEDS CORRECTION]
```

Correct `impl_llama3.py`, re-run, repeat → offline RAG becomes calibrated to
spec-correct output.

## Root causes documented

Two full RCA write-ups — the deep-debugging core of this project:

- **5G-AKA Gate-2** — PLMN order CU≠DU → wrong SNN → RES\*≠XRES\* → Authentication Reject.
  See `docs/GATE2_AKA_RCA.md`. Automated regression guard in `pipeline/features/aka/`.
- **NTN F1 handover post-HO user-plane loss** — CU switches F1-U to target DU and marks HO
  "complete" via source release, but UE never acquires target PCI radio → 100% post-HO ping loss.
  6-hypothesis investigation, cause isolated to RFsim multi-client topology.
  See `docs/D3C_POST_HO_UP_LOSS_RCA.md`. Honesty note in the doc: live SAT_LEO dual-DU HO is **not**
  claimed to pass — proven HO remains AWGN + UE-as-server.

## Lab setup

OpenAirInterface gNB + nrUE + OAI CN5G · RFsimulator · VMware Ubuntu VM
Evidence captures: `oai-config/validation/capture-l2l3.sh`
NTN test cases: `NTN_TEST_CASES.md`
```

---

### Topics to add to both repos

```
5g  5g-sa  3gpp  conformance-testing  ntn  non-terrestrial-networks  satellite  leo
openairinterface  oai  sib19  5g-aka  milenage  suci  plmn  mocn  tshark  pytest
pycryptodome  llm-calibration  ollama  rag  python  ci-cd  github-actions  sgp4
doppler  satellite-handover  prometheus  grafana  wireshark
```

---

### Pinned repos strategy

Pin these two + your offline RAG repo. The three together tell a single story:
**NTN lab → conformance pipeline → offline AI calibration**.

---

## 3. Medium Article

### Title options (pick one)

1. **"I Root-Caused a 5G Authentication Failure in My Home Lab — Then Automated the Regression Guard"**
2. **"Spec-First 5G: How I Built a 3GPP Conformance Factory on OpenAirInterface with Claude + Ollama"**
3. **"Building a 5G Satellite Network on a Laptop — Then Making an AI Verify It Against the Spec"**

Title #1 is the strongest hook — it leads with a real debugging story.

---

### Article outline (Title #1)

**Hook (200 words)**
> I was running a 5G authentication test. The UE was attaching — RACH, RRC, everything green — and then: `Authentication Reject`. No obvious reason. I had the pcap. I had the logs. What I didn't have was 30 seconds to wait before it failed again.

**Section 1: What the spec says (300 words)**
- TS 33.501 §6.1.3.2: UE derives RES\* using Milenage f2, then KDF over RAND + SNN
- SNN = "5G:mnc{MNC}.mcc{MCC}.3gppnetwork.org" — PLMN-locked
- Network computes XRES\* from the same inputs; they MUST match
- Code snippet: the Milenage derivation in `impl_claude.py`

**Section 2: The actual root cause (400 words)**
- CU SIB1 had PLMN 20893 first; DU SIB1 had 001/01 first
- UE read DU SIB1 → derived SNN = "5G:mnc001.mcc001..." 
- AMF computed XRES\* with SNN = "5G:mnc093.mcc208..."
- RES\* ≠ XRES\* → Authentication Reject
- One config line fix: reorder `plmn_list` in DU gnb conf

**Section 3: Turning a one-off fix into a regression guard (400 words)**
- Problem: fixing it manually means it can silently regress
- Solution: `pipeline/features/aka/impl_claude.py` — Milenage in Python, tshark for pcap
- `test_aka.py` — pytest parametrized, runs on every commit
- GitHub Actions CI badge: the fix is now permanent evidence

**Section 4: The LLM calibration angle (300 words)**
- Claude writes the spec-cited reference implementation
- Ollama (offline) writes its version without internet
- `diff_report.py` shows exact metric-level divergence
- Use case: lab without internet, but you still want AI help that's spec-correct
- "Correct the offline model, re-run, repeat" loop

**Section 5: NTN and why it matters (200 words)**
- Same verification approach applied to NTN: TC-NTN-001 to TC-NTN-006
- SIB19 encoding, LEO attach, F1 handover — all now have spec-to-evidence tests
- The lab runs completely offline — VMware + OAI + Ollama

**Closing (100 words)**
- Link to GitHub repos
- "The spec is the test. The test is the guard. The guard is the trust."

---

### Companion article — the handover story (strong second piece)

**Title:** *"'Handover Complete' Was Lying to Me — Debugging a 5G NTN Post-Handover Blackhole"*

This is arguably a *better* senior-signal piece than the AKA one, because the whole story is about
**not trusting a log line**. Outline:

- **Hook:** The log said `marking HO as complete`. The ping said 100% loss. Both were true.
- **The trap:** OAI emits `marking HO as complete` when the CU releases the *source* cell — that is
  not the same as `handover for UE … complete!`, which means the UE actually acquired the *target*.
  Reading the first as success is an easy, costly mistake.
- **The method:** 6 hypotheses (F1-U not switched? port collision? host routing? UE locked to source
  PCI? DU1 timing mismatch? RFsim multi-client limit?), each refuted or supported with pcap/log
  evidence — a clean worked example of disciplined RCA.
- **The finding:** proven-LEO runs a DU-as-RFsim-server topology; proven-HO runs a UE-as-server
  topology. Stitching HO onto the LEO topology puts two clients on one RFsim server and the target
  radio never comes up — the UE never reaches target PCI, tunnel stays up over a dead radio.
- **The integrity beat:** I did *not* claim live SAT_LEO dual-DU HO works. Naming the limit is the
  result. (This is the part that reads as staff-level.)

### Medium tags

`5G` · `Telecommunications` · `3GPP` · `OpenAirInterface` · `AI` · `Machine Learning` · `Python` · `Satellite` · `NTN` · `Software Engineering`

---

### Publication targets

- **Towards Data Science** — angle on the LLM calibration loop
- **Better Programming** — angle on the spec-first TDD approach
- **Your own Medium** — post all three articles (NTN lab, conformance pipeline, LLM loop) as a series

---

## 4. LinkedIn

### Post (copy-paste ready)

Post this as a text post (LinkedIn boosts text-heavy posts over link posts):

---

```
I root-caused a 5G authentication failure last week.

The UE was attaching. RACH ✅ RRC ✅ Authentication... ❌ Reject.

The cause: a 3-character config difference between the CU and DU SIB1 PLMN list order.

CU said: PLMN 208/93 first.
DU said: PLMN 001/01 first.

The UE reads the DU's SIB1, derives its Serving Network Name from PLMN 001/01, and computes RES* against it.

The AMF computed XRES* against PLMN 208/93.

They don't match → Authentication Reject.

One line fix. But the real question: how do you make sure it never silently regresses?

My answer: turn it into an automated regression guard.

→ spec.md documents the TS 33.501 §6.1.3.2 contract
→ impl_claude.py implements Milenage RES* derivation with the TS citation inline
→ test_aka.py runs pytest against the real pcap
→ GitHub Actions CI runs it on every push

Then I added the twist: the same test runs against llama3 and mistral (offline, via Ollama). A diff report shows exactly where the offline models deviate from the spec-correct Claude output — and flags them as [NEEDS CORRECTION].

The goal: calibrate offline AI to spec-correct output without needing internet.

Project stack:
• OpenAirInterface gNB + nrUE + OAI CN5G (VMware)
• 5G LEO satellite (SAT_LEO_TRANS, moving satellite, ~37 kHz Doppler)
• TS 33.501 + TS 38.331 conformance
• Python / pytest / pycryptodome / tshark
• Ollama (llama3 + mistral) + Claude

Happy to share more — repos in bio.

#5G #3GPP #OpenAirInterface #NTN #Satellite #Python #AI #Telecommunications #SpecFirst
```

---

### Alternate post — the handover story

```
The log said "marking HO as complete."
The ping said 100% packet loss.
Both were true. That's what made it interesting.

I was testing F1 handover in a 5G NTN lab (OpenAirInterface, LEO satellite). The CU triggered the
handover, switched the F1-U GTP tunnel to the target DU, and printed "marking HO as complete."

But every ping after that dropped.

Here's the trap: "marking HO as complete" is NOT the same as "handover for UE complete!"

The first one fires when the CU releases the SOURCE cell.
The second one means the UE actually acquired the TARGET cell radio.

My UE was doing the first and never the second — it left the source PCI, hit a synch-Failed storm,
and never locked onto the target. The data tunnel stayed up over a dead radio. A blackhole that
looks like success if you only read the top-level log.

I ran it as a proper root cause — 6 hypotheses, each refuted or confirmed against pcap + logs:
• F1-U not switched to target? Refuted — GTP tunnel moved correctly.
• Port collision (2152 vs 2153)? Refuted.
• Host routing after HO? Refuted.
• Cause: an RFsim multi-client limitation. My proven-LEO setup uses a DU-as-server topology; my
  proven-HO setup uses UE-as-server. Stitching HO onto the LEO topology puts two clients on one
  RFsim server and the target radio never comes up.

The honest conclusion: live SAT_LEO dual-DU handover does NOT complete on this topology. I'm not
going to claim it does. Naming the limit precisely IS the result.

15 years in wireless has taught me one thing above all: don't trust the log line. Trust the packet.

#5G #NTN #OpenAirInterface #Handover #RootCauseAnalysis #Wireless #Satellite
```

### LinkedIn About section (add this paragraph)

```
I build and verify 5G networks in software — OpenAirInterface RAN and core, 3GPP conformance testing,
and Non-Terrestrial Networks (LEO satellite). My current project: a spec-to-evidence conformance
pipeline that takes a TS clause, runs three AI models against a real pcap, and flags deviations
from the 3GPP spec automatically. The lab runs fully offline on VMware. Evidence: pcap + logs,
organized by test case, synced to desktop.
```

### LinkedIn Skills to add (if not already listed)

- 5G NR
- 3GPP Standards
- Network Protocol Testing
- Non-Terrestrial Networks (NTN)
- OpenAirInterface
- Python
- Wireshark / tshark
- CI/CD (GitHub Actions)
- LLM / Generative AI

---

## Quick Reference — What Goes Where

| Platform | Lead with | Tone |
|---|---|---|
| Resume | the two root-cause bullets, then metrics + TS clauses | formal, quantified |
| GitHub | README architecture + "Root causes documented" section | technical, scannable |
| Medium | the handover "the log was lying" story (Gate-2 as companion) | narrative, show your thinking |
| LinkedIn | either root-cause post — both end on "trust the packet" | conversational, specific |

**At 15 years, the differentiator is depth + rigor, not breadth.** Two clean root-cause
investigations that end in an honestly-stated limit beat ten features that all say PASS.

**The single thread across all four:** You didn't just configure a 5G stack — you debugged it to the
spec level, automated the proof, and built a system that teaches offline AI to be spec-correct.
That's the story. Lead with it everywhere.
