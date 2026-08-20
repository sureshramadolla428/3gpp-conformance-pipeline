# Feature: registration  —  Initial 5GMM registration success   [TC-REG-001]

feature:      registration
ts_clause:    TS 24.501 §5.5.1 (registration procedure); TS 24.501 §9.7 (NAS message types)
interface:    N2 / NGAP (NAS-5GS)
capture:      pcap on N2 during initial UE registration
verdict_of:   PASS | FAIL | INCONCLUSIVE | ERROR

## Purpose
Verify that the UE completes the initial registration procedure end to end and reaches 5GMM-REGISTERED.

## Preconditions  (if unmet → INCONCLUSIVE, never FAIL)
- P1  NGAP frames present     metric: ngap_frames > 0
- P2  NAS-5GS frames present   metric: nas_frames > 0
# Rule: no signalling captured → INCONCLUSIVE.

## MUST be present  (ALL required for PASS)
- M1  Registration Request observed        check: 5GMM message type == 0x41                                        metric: reg_request        expect: true
- M2  Authentication Request and Response   check: Authentication Request (0x56) and Response (0x57) both present    metric: auth_present       expect: true
- M3  Security Mode Command and Complete    check: SMC (0x5d) followed by SMP (0x5e)                                 metric: security_complete  expect: true
- M4  Registration Accept observed          check: 5GMM message type == 0x42                                        metric: reg_accept         expect: true

## MUST NOT be present  (ANY hit → FAIL)
- N1  Registration Reject observed          check: 5GMM message type == 0x44                                        metric: reg_reject         expect: false

## Verdict logic  (evaluation order matters)
  if not (P1 and P2):              INCONCLUSIVE
  elif N1 violated:                FAIL
  elif M1 and M2 and M3 and M4:    PASS
  else:                            FAIL

## Metrics the verifier MUST emit  (exact keys)
  ngap_frames        int
  nas_frames         int
  reg_request        bool
  auth_present       bool
  security_complete  bool
  reg_accept         bool
  reg_reject         bool
  verdict            str

## Notes / caveats
- 0x41 = Registration Request, 0x42 = Registration Accept, 0x44 = Registration Reject,
  0x56/0x57 = Authentication messages, 0x5d/0x5e = Security Mode messages.
- This feature intentionally overlaps suci and aka.
- This test does not cover PDU session / user plane.
