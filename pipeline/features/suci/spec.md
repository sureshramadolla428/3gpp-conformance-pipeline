# spec.md — SUCI + NAS Security Mode Conformance

**TS reference:** TS 33.501 §6.1.3, §6.12 + Annex C (SUCI / ECIES protection schemes)  
**Feature:** suci  
**Written by:** Basha (YOU — the contract; AI cannot change this)

**Change log:**
- 2026-08-05: null-scheme prohibition added to MUST NOT (see below), applied by AI
  **under explicit written authorization from the owner (Basha)**, who directed the exact change.
  This strengthens the oracle; it does not weaken any existing criterion.

---

## What the spec says

TS 33.501 §6.1.3 (5G-AKA and EAP-AKA' authentication):

> The UE SHALL send a Subscription Concealed Identifier (SUCI) in the
> Registration Request message. The UE SHALL NOT send a cleartext SUPI
> (IMSI) over the radio interface before NAS security is established.

The NAS Security Mode Command / Complete exchange (TS 24.501 §5.4.2)
establishes integrity + ciphering. After that, SUPI may be revealed
to the network internally, but never on the air in cleartext.

---

## Inputs

- A PCAP file captured on the N2 interface (SCTP/NGAP) during UE registration.
- Captured with `tcpdump` on the Docker bridge during `pathc-bringup-du0.sh`.

---

## MUST (test will assert these)

1. NAS-5GS frames present on N2 interface (ngap dissection visible).
2. NAS Security Mode Command (message type 0x5d) present.
3. NAS Security Mode Complete (message type 0x5e) present.
4. SUCI IE (`nas-5gs.mm.suci.*`) present in at least one Registration Request.

## MUST NOT

- Cleartext IMSI (`e212.imsi` field) visible in any frame BEFORE Security Mode Complete.
- **SUCI protection scheme ID == 0 (null scheme) in any Registration Request.**
  A null-scheme SUCI carries the SUPI (IMSI) in cleartext inside the SUCI, so it does NOT
  provide identifier privacy even though the identity type decodes as "SUCI". A capture that
  uses the null scheme MUST fail this conformance test until real concealment (a provisioned
  home-network public key / ECIES profile A or B) is used.
  Ref: TS 33.501 §6.12 + Annex C (protection scheme 0 = null).
  Metric asserted by the test: `null_scheme_frames == 0`.

---

## Done when

`pytest pipeline/features/suci/test_suci.py` passes for ALL THREE models
AND evidence reports saved to `pipeline/features/suci/evidence/`.

---

## Lab evidence file

`pipeline/features/suci/evidence/AMF.pcapng`  
(copy from: `3GPP_Spec_Test/Input/AMF.pcapng`)
