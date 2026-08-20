# MASTER Spec Index — End-to-End: UE → RAN → Transport → Core → Satellite (LTE · 5G · NTN · V2X)

The umbrella reference. Covers the whole chain and the cross-cutting domains: **conformance/test &
failure specs, hardware/RF, transport/fronthaul, V2X/sidelink, positioning, security assurance &
lawful intercept, management/OAM, broadcast, IoT**, plus the NTN satellite chain.

> Companion detailed files (part of this set):
> - `LTE_5G_SPEC_INDEX.md` — per-stage call flow, LTE vs 5G side by side
> - `NTN_SPEC_INDEX.md` — NTN / D2D / satellite, per stage, + non-3GPP adjacent bodies

## READ FIRST — scope & honesty
- **This is the most complete *practical* index, not a certified complete list.** 3GPP has
  ~hundreds of TS/TR plus thousands of change requests across releases. Guaranteeing "every single
  spec/test case" is beyond what I can verify. Use this as a domain map; confirm specifics per release.
- **Confidence legend:** `✅` verified vs 3GPP/ETSI this session · `◆` high confidence, verify
  version/clause · `⚠` verify the number itself.
- **Cutoff ~May 2025.** Rel-18/19 items (NTN regenerative, RedCap evolution, D2D-over-satellite) still moving.
- Non-3GPP items (fronthaul, timing, transport, regulatory) are marked **[non-3GPP]** — they are not
  TS/TR and not 3GPP conformance specs.

---

## PART 1 — The physical/logical chain (what sits where)

```
 UE ──Uu(air)── [RU ── fronthaul ── DU ── midhaul ── CU] ──backhaul── CORE ── Data Network / IMS
  │                        (NG-RAN / E-UTRAN)                (5GC / EPC)
  │
  └─ NTN path:  UE ──service link── SATELLITE(payload) ──feeder link── NTN GATEWAY ── CORE
```

| Segment | LTE | 5G | NTN overlay | Conf |
|---|---|---|---|---|
| UE | TS 36.101/306 | TS 38.101-x/306 | TS 38.101-5 (satellite UE RF) | ◆/✅ |
| Air interface (Uu) | E-UTRA PHY 36.211-214 | NR PHY 38.211-214 | timing/Doppler pre-comp (38.213) | ◆ |
| RU / DU / CU split | (eNB monolithic; CUPS later) | CU/DU: 38.401; F1AP 38.473; E1AP 38.463 | SAN 38.108; gNB-on-sat (Rel-19) | ◆/⚠ |
| Transport | S1/X2 over IP | NG/Xn/F1/E1 over IP | feeder-link transport | ◆ |
| Core | EPC (23.401) | 5GC (23.501/502) | satellite backhaul integration | ◆ |
| Satellite | — | — | payload (transparent vs regenerative), ephemeris (SIB19) | ✅/⚠ |
| Data / voice | IMS (23.228) | IMS (23.228) | data-first; voice emerging | ◆ |

---

## PART 2 — Call flow, all specs (see companion files for the full side-by-side)
Switch-on → cell search → RACH → RRC → attach/registration → auth/security → bearer/PDU session →
mobility → voice. **Full tables are in `LTE_5G_SPEC_INDEX.md` (terrestrial) and `NTN_SPEC_INDEX.md`
(satellite).** Core anchors: RRC 36.331/38.331 · NAS 24.301/24.501 · Arch 23.401/23.501/502 ·
Security 33.401/33.501 · User plane GTP-U 29.281 · N4 PFCP 29.244.

---

## PART 3 — FAILURE, error handling & conformance/test specs
*(This is where "failure specifications" and negative/error test cases live.)*

### 3a. Where failures/cause codes are defined (in the protocol specs)
| Failure domain | LTE | 5G | Conf |
|---|---|---|---|
| NAS reject / cause values (EMM/ESM, 5GMM/5GSM) | TS 24.301 (Annex cause tables) | TS 24.501 (cause tables) | ◆ |
| RRC failure / re-establishment / RLF | TS 36.331 | TS 38.331 | ◆ |
| Radio link monitoring / RLF timers | TS 36.133 | TS 38.133 | ◆ |
| RAN AP cause IEs (setup/HO failure) | S1AP 36.413, X2AP 36.423 | NGAP 38.413, XnAP 38.423, F1AP 38.473 | ◆ |
| Reliability / URLLC / availability KPIs | TS 22.261 | TS 22.261 | ◆ |

### 3b. UE conformance & test specifications (contain the negative/failure test cases)
| Purpose | LTE | 5G | Conf |
|---|---|---|---|
| Common test environment | TS 36.508 | TS 38.508-1 / -2 | ✅ |
| Special conformance test functions | TS 36.509 | TS 38.509 | ✅ |
| RF transmit/receive conformance | TS 36.521-1 | TS 38.521-1 (FR1), -2 (FR2), -3 (interworking) | ✅ |
| RF performance (demod) | TS 36.521-3 (RRM 36.521-3?) | TS 38.521-4 | ⚠ |
| RRM conformance | TS 36.521-3 | TS 38.533 | ✅ |
| Protocol conformance test cases | TS 36.523-1 (cases), -2 (PICS), -3 (TTCN) | TS 38.523-1 / -2 / -3 | ✅ |
| Positioning conformance | TS 37.571-x | TS 37.571-x | ◆ |
| IMS / VoLTE-VoNR conformance | TS 34.229 | TS 34.229 (+ 5G parts) | ⚠ |

### 3c. Base-station / network conformance
| Purpose | LTE | 5G | Conf |
|---|---|---|---|
| BS RF conformance | TS 36.141 (eNB) | TS 38.141-1 (conducted) / -2 (radiated) | ◆ |
| Multi-standard radio BS | TS 37.141 | TS 37.141 | ◆ |
| AAS BS conformance | TS 37.145-1 / -2 | TS 37.145-1 / -2 | ⚠ |
| EMC | TS 36.113 | TS 38.113 | ⚠ |

---

## PART 4 — HARDWARE / RF / antenna / BS classes
| Item | LTE | 5G | Conf |
|---|---|---|---|
| UE RF | TS 36.101 | TS 38.101-1/-2/-3/-4/-5(sat) | ◆/✅ |
| BS RF | TS 36.104 | TS 38.104 | ◆ |
| Satellite Access Node RF | — | TS 38.108 | ✅ |
| AAS BS (active antenna) | TS 37.105 | TS 37.105 | ⚠ |
| Multi-standard radio | TS 37.104 | TS 37.104 | ◆ |
| IAB (integrated access & backhaul) node RF | — | TS 38.174 | ⚠ |
| RF requirements background | RAN4 TRs (e.g. 36.9xx) | RAN4 TRs (e.g. 38.863 NTN coex) | ✅/◆ |

**Software note:** the RAN/core stacks themselves are software; open-source implementations
(OpenAirInterface, srsRAN, Open5GS, free5GC) are **not** 3GPP specs — they *implement* the specs above.

---

## PART 5 — TRANSPORT / FRONTHAUL / TIMING (RU↔DU↔CU) — mostly non-3GPP
| Item | Spec / body | Conf |
|---|---|---|
| Fronthaul split 7.2x (open fronthaul) | **O-RAN** WG4 (CUS-plane, M-plane) **[non-3GPP]** | ◆ |
| CPRI / eCPRI (fronthaul transport) | CPRI Cooperation **[non-3GPP]** | ◆ |
| F1 (CU↔DU) | TS 38.473 (F1AP) | ◆ |
| E1 (CU-CP↔CU-UP) | TS 38.463 (E1AP) | ⚠ |
| Precision time (PTP) | **IEEE 1588v2**; ITU-T **G.8275.1/.2** profiles **[non-3GPP]** | ◆ |
| Synchronous Ethernet | ITU-T **G.8262 / G.8261** **[non-3GPP]** | ⚠ |
| IP / MPLS / Segment Routing backhaul | **IETF** RFCs **[non-3GPP]** | ◆ |
| RAN timing/sync requirements | TS 38.133 (sync accuracy) | ◆ |

---

## PART 6 — V2X (vehicle-to-everything) & sidelink
| Item | LTE (C-V2X) | 5G (NR V2X) | Conf |
|---|---|---|---|
| Service requirements | TS 22.185 | TS 22.186 (eV2X) | ✅ |
| Architecture (stage 2) | TS 23.285 | TS 23.287 | ✅ |
| V2X protocol (stage 3) | TS 24.386 | TS 24.587 | ✅ |
| Application layer enabler | TS 23.286 | TS 23.286 | ◆ |
| RAN study | TR 36.885 | TR 38.885 | ✅ |
| Sidelink PC5 radio | 36.331/36.321/36.213 | 38.331/38.321/38.322/38.323/38.211-214 | ◆ |

---

## PART 7 — ProSe / D2D sidelink (proximity services)
| Item | LTE | 5G | Conf |
|---|---|---|---|
| ProSe architecture | TS 23.303 | TS 23.304 (5G ProSe) | ◆ |
| ProSe protocol | TS 24.334 (PC3), PC5 signalling | TS 24.554 | ⚠ |
| Note | Rel-19 **UE-Satellite-UE** ("D2D over satellite") is NTN-side, not ProSe | | ⚠ |

---

## PART 8 — Positioning / location
| Item | LTE | 5G | Conf |
|---|---|---|---|
| Positioning architecture (stage 2) | TS 36.305 | TS 38.305 | ◆ |
| LPP (UE↔location server) | TS 36.355 | TS 37.355 | ◆ |
| RAN positioning protocol | LPPa: TS 36.455 | NRPPa: TS 38.455 | ◆ |
| SUPL / secure user plane | OMA SUPL **[non-3GPP]** | OMA SUPL | ⚠ |

---

## PART 9 — Security assurance (SCAS) & lawful interception
| Item | Spec | Conf |
|---|---|---|
| General SCAS catalogue | TS 33.117 | ✅ |
| Per-NF SCAS (gNB, AMF, UPF, SMF, UDM, …) | TS 33.511 (gNB), 33.512 (AMF), 33.513 (UPF), 33.514 (UDM)… | ⚠ (verify each) |
| Lawful intercept requirements | TS 33.126 | ✅ |
| LI architecture (stage 2) | TS 33.127 | ✅ |
| LI protocol (stage 3) | TS 33.128 | ✅ |
| Legacy LI (pre-Rel-17) | TS 33.107 / 33.108 | ◆ |

---

## PART 10 — Management / OAM / orchestration / slicing / charging
| Item | Spec | Conf |
|---|---|---|
| 5G network resource model (NRM) | TS 28.541 | ⚠ |
| Network slicing management | TS 28.530 / 28.531 / 28.532 | ⚠ |
| SON / self-organizing networks | TS 28.313 / 32.500-series | ⚠ |
| Charging (5G) | TS 32.240 (principles), TS 32.290+ (5G converged, Nchf) | ⚠ |
| Performance measurements / KPIs | TS 28.552 / 28.554 | ⚠ |
| Fault/config/assurance mgmt | 28-series | ◆ |

---

## PART 11 — Broadcast / multicast (MBMS / MBS)
| Item | LTE | 5G | Conf |
|---|---|---|---|
| Architecture | eMBMS: TS 23.246 | 5G MBS: TS 23.247 | ◆ |
| Delivery / codecs | TS 26.346 | TS 26.346 (+5G MBS media) | ⚠ |

---

## PART 12 — Public warning & emergency
| Item | Spec | Conf |
|---|---|---|
| PWS requirements | TS 22.268 | ◆ |
| Cell broadcast / PWS delivery (ETWS, CMAS, KPAS) | TS 23.041 | ◆ |
| IMS emergency sessions | TS 23.167 | ◆ |
| Emergency numbers / eCall (V2X-adjacent) | TS 22.101 / 26.267 (eCall) | ⚠ |

---

## PART 13 — IoT (cellular IoT) + NTN-IoT
| Item | Spec | Conf |
|---|---|---|
| NB-IoT / eMTC (core changes) | 36-series (211-214, 321-323, 331, 101/104) | ◆ |
| CIoT 5GS optimizations | TS 23.501 / 24.501 | ◆ |
| IoT NTN (satellite) | TR 36.763 (study) + normative CRs to 36-series | ✅ |
| RedCap (reduced capability) | Rel-17/18 features in 38-series (no dedicated series) | ◆ |

---

## PART 14 — NTN satellite chain specifics
| Item | Spec | Conf |
|---|---|---|
| NTN studies | TR 38.811, TR 38.821 | ✅ |
| Satellite UE RF | TS 38.101-5 | ✅ |
| Satellite Access Node RF | TS 38.108 | ✅ |
| NTN RF & coexistence | TR 38.863 | ✅ |
| Ephemeris / timing (SIB19, ta-Common, Koffset) | TS 38.331 + 38.213 | ◆ |
| SA2 satellite architecture | TR 23.737 | ⚠ |
| IoT NTN | TR 36.763 | ✅ |
| Rel-19 (regenerative gNB, store-and-forward, UE-sat-UE, GNSS-independent) | WIs — numbers not stable | ⚠ |
| Spectrum/regulatory | ITU RR; **Res. 253 (WRC-23)**; **WRC-27 AI 1.13** **[non-3GPP]** | ✅ |
| Deployment guidance | **O-RAN NTN white paper**; **GSMA NTN / R21 PRD** **[non-3GPP]** | ✅ |

---

## PART 15 — Adjacent bodies (non-3GPP) — one place
- **ITU-R** — Radio Regulations; Res. 252/253 (WRC-23); WRC-27 AI 1.13 (direct-to-device to IMT).
- **ITU-T** — G.8275.1/.2 (PTP), G.8262 (SyncE) for fronthaul timing.
- **IEEE** — 1588v2 (PTP), 802.1CM (time-sensitive fronthaul).
- **O-RAN Alliance** — open fronthaul (WG4), NTN deployment white paper, nGRG.
- **GSMA** — NTN guidelines, R21 PRD (roaming, TN↔NTN).
- **IETF** — IP/MPLS/Segment Routing transport, IPsec.
- **CPRI Cooperation** — CPRI / eCPRI fronthaul.
- **OMA** — SUPL positioning.

---

## How to close remaining gaps
For any `◆`/`⚠` row, open the 3GPP specifications portal (or ETSI deliver tree) and confirm the
number + current version for your target release. The `✅` rows were verified against 3GPP/ETSI this
session. Tell me a specific domain (e.g. "5GC SBI service specs" or "AAS BS conformance") and I'll
verify those numbers precisely rather than leaving them flagged.
