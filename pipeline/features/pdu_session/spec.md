# Feature: pdu_session  —  PDU session establishment + user plane   [TC-PDU-001]

feature:      pdu_session
ts_clause:    TS 24.501 §6.4.1 (PDU session establishment); TS 23.502 §4.3.2 (procedure); TS 24.501 §9.7 (NAS message types)
interface:    N2 / NGAP (5GSM NAS) + N3 (GTP-U) + UE tunnel (ping)
capture:      core pcap (N2 + N3) + run.log containing ping result
verdict_of:   PASS | FAIL | INCONCLUSIVE | ERROR

## Purpose
Verify that the UE establishes a PDU session and that user-plane traffic flows successfully over N3.

## Preconditions  (if unmet → INCONCLUSIVE, never FAIL)
- P1  UE registered first             metric: registered == true
- P2  NAS-5GS frames present           metric: nas_frames > 0
- P3  PDU session procedure visible     metric: pdu_session_frames > 0
# Rule: without registration, NAS visibility, and PDU session signalling, the result is INCONCLUSIVE.

## MUST be present  (ALL required for PASS)
- M1  PDU Session Establishment Request   check: 5GSM message type == 0xc1                       metric: pdu_req       expect: true
- M2  PDU Session Establishment Accept     check: 5GSM message type == 0xc2                       metric: pdu_accept    expect: true
- M3  GTP-U user plane on N3               check: GTP-U frames present on the N3 interface         metric: gtpu_frames   expect: > 0
- M4  Data-plane reachability              check: ping loss == 0% in run.log                       metric: ping_ok       expect: true

## MUST NOT be present  (ANY hit → FAIL)
- N1  PDU Session Establishment Reject     check: 5GSM message type == 0xc3                        metric: pdu_reject    expect: false

## Verdict logic  (evaluation order matters)
  if not (P1 and P2 and P3):        INCONCLUSIVE
  elif N1 violated:                 FAIL
  elif M1 and M2 and M3 and M4:     PASS
  else:                             FAIL

## Metrics the verifier MUST emit  (exact keys)
  registered           bool
  nas_frames           int
  pdu_session_frames   int
  pdu_req              bool
  pdu_accept           bool
  gtpu_frames          int
  ping_ok              bool
  pdu_reject           bool
  verdict              str

## Notes / caveats
- 0xc1 = PDU Session Establishment Request, 0xc2 = Accept, 0xc3 = Reject.
- Ping evidence comes from run.log, not the pcap.
- GTP-U filter is gtp on the N3-bearing interface; ensure the capture file really contains N3.
- Long RTT over NTN is acceptable; the pass criterion here is connectivity, not latency.
