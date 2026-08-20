# START HERE — 5G/NTN conformance evidence capture (for Cursor)

This folder contains 5 standalone runbooks. Run them **one at a time**, in the order below.
Each produces its own evidence folder under `~/leo-evidence/`.

## Order
1. TC-SEC-001_suci.md            — SUCI privacy (N2 capture)
2. TC-REG-001_registration.md    — registration success (N2 capture)
3. TC-SEC-002_aka.md             — 5G-AKA RES* == XRES* (logs + offline recompute)
4. TC-PDU-001_pdu_session.md     — PDU session + user plane (N2 + N3 + ping)
5. TC-SEC-003_sib1.md            — multi-PLMN SIB1 / MOCN order (config + F1)

## Rules that apply to EVERY runbook (do not break)
1. Do NOT modify, rename, or delete any existing file. Create NEW files ONLY under
   `~/leo-evidence/<TEST-ID>_<UTC-timestamp>/`.
2. If a config change is required, COPY the conf into the evidence folder, edit the copy, and launch
   from the copy. Never edit an original.
3. Start packet captures BEFORE the UE attaches, or the Registration Request / SUCI is lost.
4. REPORT the counts you observe. Do NOT declare PASS or FAIL — the pipeline verifier decides that.
5. Before running anything, print the exact commands you intend to run and WAIT for my confirmation.
6. Placeholders like <BR>, <N3>, <start gNB NTN> must be resolved by discovery (Step 1 of each
   runbook), not guessed.

## Per-test workflow
For each runbook, in order: open the file → do its discovery step and report findings → wait for my
go-ahead → run capture+scenario → collect logs → run the self-check → print the evidence folder path
and the counts → STOP and wait for me to say "next" before starting the following test.

## Caveats to respect (do not silently assume)
- tshark field names and message-type hex are ILLUSTRATIVE until confirmed on this Wireshark version.
  If a filter returns 0, try the 3.x underscore vs 4.x hyphen field-name variant before concluding absence.
- TC-SEC-002 (AKA): RAND, K, OPc and the SNN must all come from the SAME run or RES* will not match.
- TC-SEC-003 (SIB1): in RFsim there is no over-the-air SIB1 pcap — compare CU vs DU config PLMN order,
  optionally confirmed via F1AP on loopback.
