# Feature: sib1  —  Multi-PLMN SIB1 / MOCN order consistency   [TC-SEC-003]

feature:      sib1
ts_clause:    TS 38.331 §6.3.1 (SIB1, plmn-IdentityInfoList); TS 23.003 (PLMN/SNN mapping context)
interface:    Uu broadcast SIB1 (or F1AP / gNB-DU config carrying served PLMNs)
capture:      pcap containing SIB1 (or f1.pcap) + CU and DU config files
verdict_of:   PASS | FAIL | INCONCLUSIVE | ERROR

## Purpose
Verify that the PLMN order broadcast in the DU's SIB1 matches the CU's configured order, so the UE
derives the intended serving network path.

## Preconditions  (if unmet → INCONCLUSIVE, never FAIL)
- P1  At least one comparison source available   metric: sib1_frames > 0 OR configs_present == true
- P2  PLMN list available for comparison          metric: plmn_count >= 1
# Rule: if neither SIB1 nor usable config data is available, the result is INCONCLUSIVE.

## MUST be present  (ALL required for PASS)
- M1  DU and CU first PLMN match      check: index-0 of SIB1 PLMN list == index-0 of CU PLMN list   metric: plmn_order_match      expect: true
- M2  Target PLMN present in the list  check: target PLMN appears in the broadcast/configured list    metric: target_plmn_present   expect: true

## MUST NOT be present  (ANY hit → FAIL)
- N1  First-PLMN mismatch              check: index-0 mismatch between DU SIB1 and CU config          metric: plmn_order_mismatch   expect: true

## Verdict logic  (evaluation order matters)
  if not (P1 and P2):     INCONCLUSIVE
  elif N1:                FAIL
  elif M1 and M2:         PASS
  else:                   FAIL

## Metrics the verifier MUST emit  (exact keys)
  sib1_frames          int
  configs_present      bool
  plmn_count           int
  cu_first_plmn        str
  du_first_plmn        str
  plmn_order_match     bool
  target_plmn_present  bool
  plmn_order_mismatch  bool
  verdict              str

## Notes / caveats
- Normalize PLMN format before comparison (MCC-MNC, with 2- or 3-digit MNC handled consistently).
- Wireshark field paths vary by version; support both plmn-IdentityInfoList and related decoded field names.
- If the scenario is not multi-PLMN, the order check may be INCONCLUSIVE rather than FAIL.
- This checks order consistency only, not whether authentication succeeds.
