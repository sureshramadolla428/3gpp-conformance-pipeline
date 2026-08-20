# Screenshot shot list — for Medium & GitHub

Run these in order and snap each one (**Win + Shift + S**). Before each: type `cls`, Enter,
run the command, then snap the output. G = good for GitHub, M = good for Medium.

---

## Prep (run once)
```powershell
cd "C:\Users\sures\OneDrive\Desktop\Setup Instructions\5g-conformance-pipeline"
function prompt { "PS> " }
```
This short prompt keeps the long OneDrive path out of your screenshots.

> Note on evidence paths: the `-m` verifier commands below use fixed timestamped folders.
> If yours differ, tab-complete after typing `..\evidence\TC-...`, or use the auto-latest form:
> `$e=(gci "..\evidence\TC-SEC-001_*"|sort Name|select -last 1).FullName; python -m pipeline.features.suci.impl_claude $e`

---

## PART A — Results (the proof)   ★ the essential four

### 1. All three models agree  ·  G M  ★ headline
```powershell
cls; python compare\diff_report.py --all
```
Snap the top (SUCI table) and the bottom `OVERALL: All features agree ✅`.
*Caption: "Three independent verifiers — a trusted reference + two offline models — agree on every metric across five 3GPP checks."*

### 2. The defect: SUCI FAIL (IMSI exposed)  ·  G M
```powershell
cls; python compare\diff_report.py --feature suci
```
*Caption: "The pipeline flags a null-scheme SUCI (null_scheme_frames=2) — the IMSI in cleartext — that a naive 'is a SUCI present?' check passes."*

### 3. The crypto proof: AKA RES* == HXRES*  ·  G M
```powershell
cls; python compare\diff_report.py --feature aka
```
*Caption: "RES* recomputed offline (98ffc4…) matches the network's HXRES* (671faf…) — authentication verified, not assumed."*

### 4. Tests green  ·  G M
```powershell
cls; python -m pytest -q
```
*Caption: "33 conformance assertions pass; the human-owned oracle guards against regressions."*

---

## PART B — One script, one verdict (the JSON)

### 5. Run the SUCI verifier directly → FAIL  ·  M
```powershell
cls; python -m pipeline.features.suci.impl_claude "..\evidence\TC-SEC-001_20260805T211732Z"
```
*Caption: "A single verifier reads the capture and returns FAIL with evidence and the TS clause."*

### 6. Run the AKA verifier directly → PASS  ·  M
```powershell
cls; python -m pipeline.features.aka.impl_claude "..\evidence\TC-SEC-002_20260805T220324Z"
```
*Caption: "The AKA verifier recomputes Milenage offline and confirms the match — one command, full evidence."*

---

## PART C — The source code (open in VS Code, then snap)

These look best in an editor (syntax colors). `type <file>` in PowerShell also works but is plain.

### 7. The reference AKA verifier (Milenage/KDF)  ·  G M  ★ most impressive code
```powershell
code pipeline\features\aka\impl_claude.py
```
*Caption: "The reference verifier — real Milenage + TS 33.501 Annex A.4/A.5 KDF, cited inline."*

### 8. The SUCI null-scheme detection  ·  M
```powershell
code pipeline\features\suci\impl_claude.py
```

### 9. The human-authored contract  ·  G M
```powershell
code pipeline\features\suci\spec.md
```
*Caption: "The spec.md contract — MUST / MUST NOT distilled from the TS clause; the checkable version of the standard."*

---

## PART D — The AI-calibration angle

### 10. Raw offline draft (before calibration)  ·  M
```powershell
code pipeline\features\aka\impl_llama3.generated.py
```
*Caption: "What the offline model produced from the spec — before a human calibrated it to the reference (see CALIBRATION_LOG.md)."*

### 11. The RAG generator running  ·  M
```powershell
cls; python tools\gen_offline_impl.py --feature suci --model llama3   # private companion repo
```
*Caption: "The offline generator: retrieves the relevant 3GPP clauses from the local RAG, then a local model drafts the verifier."*

---

## PART E — Structure & artifacts

### 12. The 3-model file pattern per feature  ·  G
```powershell
cls; tree /F pipeline\features\suci
```
*Caption: "Each feature = one spec contract + three implementations (reference + two offline) + a test."*

### 13. A frozen golden result  ·  G
```powershell
cls; type golden\aka_claude.json
```
*Caption: "When all three agree, the result freezes as a golden file — the offline oracle."*

### 14. The flowchart (not PowerShell)
Open `docs\pipeline_flowchart.svg` in a browser and snap it, or use the Mermaid diagram in
`README.md` (GitHub renders it automatically). *Put this near the top of both posts.*

---

## Recommended order in the posts
- **GitHub README:** flowchart (14) → results (1) → defect (2) → structure (12) → code (7).
- **Medium article:** flowchart (14) → the hook/code (7) → run one script (5,6) → the RAG draft (10) → the calibration diff (1) → the defect (2) → tests green (4).
