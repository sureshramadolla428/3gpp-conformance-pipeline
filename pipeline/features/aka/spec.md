# Feature: aka  —  5G-AKA RES* equals XRES* (Gate-2 regression guard)   [TC-SEC-002]

feature:      aka
ts_clause:    TS 33.501 §6.1.3.2 (5G AKA); TS 33.501 Annex A.4 (RES/XRES derivation); TS 23.003 §28.x (Serving Network Name)
interface:    AMF / gNB logs (+ optional N2 pcap) + offline Milenage recompute
capture:      run.log / AMF log during registration; known K, OPc, RAND, XRES*, PLMN from config
verdict_of:   PASS | FAIL | INCONCLUSIVE | ERROR

## Purpose
Verify that the UE-derived RES* matches the network XRES* so authentication succeeds, and that the
Serving Network Name is well formed.

## Preconditions  (if unmet → INCONCLUSIVE, never FAIL)
- P1  Authentication procedure present     metric: auth_request == true
- P2  Recompute inputs available            metric: inputs_available == true
# Rule: without the auth exchange or crypto inputs, the result is INCONCLUSIVE.

## MUST be present  (ALL required for PASS)
- M1  Authentication Request observed          check: 5GMM Authentication Request message present         metric: auth_request_seen    expect: true
- M2  Authentication Response / RES* available  check: UE response present and RES* recomputable          metric: auth_response_seen   expect: true
- M3  Recomputed RES* matches network XRES*     check: Milenage f2 + KDF over RAND + SNN                   metric: res_star_match       expect: true
- M4  Serving Network Name is well formed        check: SNN matches 5G format                              metric: snn_correct          expect: true

## MUST NOT be present  (ANY hit → FAIL)
- N1  Authentication Reject / MAC failure        check: Authentication Reject seen in log or pcap          metric: auth_reject          expect: false

## Verdict logic  (evaluation order matters)
  if not (P1 and P2):              INCONCLUSIVE
  elif N1 violated:                FAIL
  elif M1 and M2 and M3 and M4:    PASS
  else:                            FAIL

## Metrics the verifier MUST emit  (exact keys)
  auth_request         bool
  auth_request_seen    bool
  auth_response_seen   bool
  inputs_available     bool
  res_star_match       bool
  snn_correct          bool
  auth_reject          bool
  verdict              str

## Notes / caveats
- Verify the RES/XRES derivation reference (TS 33.501 Annex A.4) and the SNN construction used in the lab.
- 0x42 = Registration Accept, 0x58 = Authentication Reject.
- Milenage constants and operator configuration must match the deployment.
- This test is about crypto correctness; SUCI privacy is separate.
