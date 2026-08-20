# Results — three-model conformance run

These are real runs of the pipeline against captured lab evidence (OpenAirInterface NTN
lab + UERANSIM/Open5GS). Each feature is graded by three independent verifiers — the
**Claude reference** and two **offline models** (llama3, mistral) — and the run only
freezes a `golden/` result when **all three agree**.

Command used for the comparison shots:

```powershell
python compare\diff_report.py --all
```

---

## 1. SUCI + Registration — `diff_report --all`

![diff_report: SUCI and Registration](screenshots/01-diffreport-suci-registration.png)

**SUCI (TS 33.501 §6.12) → FAIL, and that is correct.** All three models independently
return `verdict=FAIL` with `null_scheme_frames=2`: the UE sends a **null-scheme SUCI**
(protection scheme 0), so the IMSI travels in cleartext and identifier privacy is not
provided. This is a genuine lab-config defect the pipeline caught — not a tooling error.
`security_mode_command` / `security_mode_complete` are present, `clear_imsi_frames=0`.

**Registration (TS 24.501 §5.5.1) → PASS.** Full procedure confirmed:
`reg_request → auth_present → security_complete → reg_accept`, `reg_reject=False`. The UE
reached 5GMM-REGISTERED. All three models agree, so Claude's output is frozen as golden.

---

## 2. 5G-AKA + PDU Session — `diff_report --all`

![diff_report: AKA and PDU session](screenshots/02-diffreport-aka-pdusession.png)

**5G-AKA (TS 33.501 §6.1.3.2) → PASS.** The strongest evidence of correctness: the
recomputed **RES\*** (`98ffc4…`) and **HXRES\*** (`671faf…`) match byte-for-byte across all
three models, the RAND and SNN (`5G:mnc001.mcc001.3gppnetwork.org`) agree, and
`res_star_match=True`. The crypto (Milenage f2 + the KDF from Annex A.4/A.5) is reproduced
independently — not just a message-count check.

**PDU Session (TS 24.501 §6.4.1) → PASS.** `pdu_req → pdu_accept`, `pdu_reject=False`,
`gtpu_frames=42` on N3, and `ping_ok=True` (0% loss). The user plane is genuinely up.

---

## 3. SIB1 / MOCN + overall, and the SUCI verifier standalone

![diff_report: SIB1 and overall + SUCI standalone](screenshots/03-diffreport-sib1-overall-suci.png)

**SIB1 / MOCN (TS 38.331 §6.3.1) → PASS.** CU and DU agree on PLMN order
(`cu_first_plmn = du_first_plmn = 208-93`), 2 PLMNs, 7 F1AP frames confirm — no
`plmn_order_mismatch`. **OVERALL: All features agree ✅.**

The lower half runs a single verifier on its own:

```powershell
python -m pipeline.features.suci.impl_claude "..\evidence\TC-SEC-001_20260805T211732Z"
```

It prints `FAIL` and the full JSON: `null_scheme_frames=2`, and the note
*"Null-scheme SUCI: protection scheme 0 on 2 frame(s) — the IMSI is carried in cleartext …
TS 33.501 §6.12 violated."* This is the same defect from panel 1, shown close up.

---

## 4. Registration + 5G-AKA standalone verifiers

![standalone: registration and AKA](screenshots/04-standalone-registration-aka.png)

Each verifier run directly against its evidence folder:

```powershell
python -m pipeline.features.registration.impl_claude "..\evidence\TC-REG-001_20260805T213520Z"
python -m pipeline.features.aka.impl_claude          "..\evidence\TC-SEC-002_20260805T220324Z"
```

Registration → PASS (full attach chain). AKA → PASS, with the note confirming
*"Recomputed RES\* matches network HXRES\* (SHA-256 msb half); … AMF reported
success=True. TS 33.501 §6.1.3.2 satisfied."*

---

## 5. PDU Session + SIB1 standalone verifiers

![standalone: PDU session and SIB1](screenshots/05-standalone-pdu-sib1.png)

```powershell
python -m pipeline.features.pdu_session.impl_claude "..\evidence\TC-PDU-001_20260805T224736Z"
python -m pipeline.features.sib1.impl_claude         "..\evidence\TC-SEC-003_20260805T232636Z_2PLMN"
```

PDU Session → PASS (GTP-U 42 frames, ping 0% loss). SIB1 → PASS (CU/DU PLMN order
consistent at `208-93`).

---

### How to read these

| Verdict | Meaning |
|---|---|
| **PASS** | Evidence satisfies the spec contract; all three graders agree. |
| **FAIL** | A real 3GPP requirement is violated (here: null-scheme SUCI). The tool is doing its job. |
| **agree** | Claude reference and both offline models produced the same value — result frozen as golden. |

No AI runs at grading time: the verifiers are pure Python + tshark + Milenage. The offline
models were used once, at build time, to draft the offline verifiers, which were then
calibrated to the reference (see [CALIBRATION_LOG.md](CALIBRATION_LOG.md)).
