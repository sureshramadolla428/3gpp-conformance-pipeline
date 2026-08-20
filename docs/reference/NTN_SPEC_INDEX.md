# NTN / D2D / Satellite — 3GPP Spec Index

Full call flow: **UE switch-on → cell search → random access → RRC → registration →
authentication → PDU session (data) → mobility → voice (VoNR/IMS)**, with the
NTN/satellite overlay called out at each stage.

## Honesty notes (read first)
- **This is comprehensive, not provably exhaustive.** NTN is woven through the core NR/5GC
  specs; guaranteeing "zero omissions" at the clause/CR level is not something I can verify
  from here. Treat this as a strong working index, not a certified list.
- **Confidence legend:**
  - `✅` verified against 3GPP/ETSI this session (title + role confirmed)
  - `◆` high confidence it exists and is foundational — but **verify the exact NTN clause/version**
  - `⚠` medium confidence — **verify the spec number itself** before citing
- **Knowledge cutoff:** my reliable knowledge ends ~May 2025. Release 18/19 items (regenerative
  payload, store-and-forward, direct D2D-over-satellite) were still moving; confirm current status.
- **"D2D" is ambiguous** — see the disambiguation section at the end. This index assumes you mean
  **Direct-to-Device / Direct-to-Cell (satellite→handset)**, which in 3GPP *is* NTN. If you meant
  **Device-to-Device (ProSe/sidelink)**, that's a different spec family, listed separately at the end.

---

## NTN-specific documents (the truly satellite-dedicated ones)

| Spec | Title / role | Conf |
|---|---|---|
| TR 38.811 | Study on NR to support Non-Terrestrial Networks (Rel-15 study) | ✅ |
| TR 38.821 | Solutions for NR to support NTN (Rel-16 study) | ✅ |
| TS 38.101-5 | UE radio transmission and reception; Part 5: **Satellite access** RF & performance (bands n255 L-band, n256 S-band) | ✅ |
| TS 38.108 | **Satellite Access Node (SAN)** radio transmission and reception (the NTN "gNB" RF) | ✅ |
| TR 38.863 | NTN-related RF and co-existence aspects (FR1-NTN) | ✅ |
| TR 36.763 | Study on NB-IoT / eMTC support for NTN (**IoT NTN**, LTE-based, Rel-17) | ✅ |
| TR 22.822 | Study on using satellite access in 5G (SA1) | ◆ |
| TR 23.737 | Study on architecture aspects for using satellite access in 5G (SA2) | ⚠ |
| Rel-19 WIs | Regenerative payload (full gNB on satellite), store-and-forward, UE-Satellite-UE (D2D-over-sat), GNSS-independent operation — **spec numbers not yet stable at my cutoff** | ⚠ |

---

## Stage 0 — UE switch-on / provisioning / identities

| Spec | Role | Conf |
|---|---|---|
| TS 31.101 | UICC–terminal interface, physical/logical characteristics | ◆ |
| TS 31.102 | USIM application (stores SUPI, home-network public key for SUCI) | ◆ |
| TS 23.003 | Numbering, addressing, identification (IMSI, **SUPI, SUCI, GUTI, 5G-S-TMSI**) | ◆ |
| TS 38.306 | UE radio access capabilities | ◆ |
| TS 22.261 | Service requirements for the 5G system (incl. satellite access) | ◆ |
| TS 22.101 | Service principles | ◆ |

NTN overlay: USIM may carry NTN/satellite PLMN config; SUCI keys used identically over satellite.

---

## Stage 1 — Cell search, synchronization, system information (NTN-critical)

| Spec | Role | Conf |
|---|---|---|
| TS 38.211 | Physical channels & modulation (PSS/SSS/SSB, PRACH, reference signals) | ◆ |
| TS 38.212 | Multiplexing & channel coding | ◆ |
| TS 38.213 | Physical-layer procedures for control — **NTN timing, K_offset, timing advance** | ◆ |
| TS 38.214 | Physical-layer procedures for data | ◆ |
| TS 38.304 | UE procedures in idle/inactive (cell selection/reselection) | ◆ |
| TS 38.331 | RRC — **SIB1, SIB19 (satellite ephemeris, ta-Common, ta-CommonDrift, cellSpecificKoffset, epochTime)** | ◆ |
| TS 38.133 | Requirements for RRM support (NTN measurement/timing requirements) | ◆ |
| TS 38.101-1 / -2 | UE RF FR1 / FR2 | ◆ |
| TS 38.101-4 | UE RF performance requirements | ◆ |
| TS 38.101-5 | **Satellite access** UE RF (NTN) | ✅ |
| TS 38.108 | **SAN** RF (NTN base station side) | ✅ |

NTN overlay: UE typically needs **GNSS position** to pre-compensate timing/Doppler — read the
NTN procedures in TS 38.300 / TS 38.331. Positioning specs: TS 37.355 (LPP), TS 38.305 (positioning
stage 2), TS 38.455 (NRPPa) `◆`.

---

## Stage 2 — Random access (NTN: extended RA window, K_offset, TA pre-compensation)

| Spec | Role | Conf |
|---|---|---|
| TS 38.321 | MAC — **RACH procedure, timing advance, NTN TA handling** | ◆ |
| TS 38.213 | RACH physical procedures, PDCCH-ordered RA | ◆ |
| TS 38.211 | PRACH formats | ◆ |
| TS 38.331 | RACH configuration broadcast in SIB | ◆ |

---

## Stage 3 — RRC connection establishment + RAN architecture

| Spec | Role | Conf |
|---|---|---|
| TS 38.300 | NG-RAN overall description & procedures (incl. NTN) | ◆ |
| TS 38.331 | RRC connection setup/reconfiguration | ◆ |
| TS 38.323 | PDCP | ◆ |
| TS 38.322 | RLC | ◆ |
| TS 38.321 | MAC | ◆ |
| TS 38.401 | NG-RAN architecture (CU/DU split) | ◆ |
| TS 38.410 / 38.413 | NG interface general / **NGAP** (application protocol) | ◆ |
| TS 38.420 / 38.423 | Xn interface general / **XnAP** | ◆ |
| TS 38.470 / 38.473 | F1 interface general / **F1AP** (CU↔DU) | ◆ |
| TS 38.415 | PDU session user-plane protocol (NG-U) | ⚠ |

---

## Stage 4 — NAS registration / attach

| Spec | Role | Conf |
|---|---|---|
| TS 24.501 | **5GS NAS protocol** (5GMM registration; carries SUCI in Registration Request) | ◆ |
| TS 23.501 | 5G system architecture | ◆ |
| TS 23.502 | 5G procedures (registration, PDU session, handover, fallback) | ◆ |
| TS 23.503 | Policy & charging control framework | ◆ |
| TS 38.413 | NGAP — Initial UE Message carrying NAS PDU | ◆ |
| TS 23.003 | Identifiers used in registration | ◆ |

---

## Stage 5 — Authentication & security

| Spec | Role | Conf |
|---|---|---|
| TS 33.501 | **5G security architecture** — 5G-AKA, SUCI concealment, key hierarchy | ◆ |
| TS 24.501 | NAS security mode control (§5.4.2), initial-NAS protection (§4.4.6) | ◆ (verified earlier) |
| TS 35.205–35.208 | **MILENAGE** algorithm set (f1–f5, test data) | ◆ |
| TS 35.231–35.233 | **TUAK** algorithm set (alternative to MILENAGE) | ◆ |
| TS 33.102 | 3G security (legacy AKA basis) | ⚠ |
| TS 33.401 | EPS (LTE) security — relevant for EPS-fallback voice | ◆ |

---

## Stage 6 — PDU session establishment (data)

| Spec | Role | Conf |
|---|---|---|
| TS 24.501 | 5GSM (session management NAS) | ◆ |
| TS 23.501 / 23.502 | PDU session, SMF/UPF, QoS (5QI) | ◆ |
| TS 29.244 | **PFCP** (N4, SMF↔UPF) | ◆ |
| TS 29.281 | **GTP-U** (N3 user-plane tunnelling) | ◆ |
| TS 29.274 | GTP-C (EPC interworking / N26) | ◆ |
| TS 29.502 | Nsmf (SMF services, SBI) | ◆ |
| TS 29.518 | Namf (AMF services, SBI) | ⚠ |
| TS 29.500 / 29.501 | 5GC SBI principles / OpenAPI | ◆ |
| TS 38.415 | NG-U PDU session user-plane protocol | ⚠ |

---

## Stage 7 — Data session in progress: mobility & NTN link management

| Spec | Role | Conf |
|---|---|---|
| TS 38.300 | Handover overview; **NTN mobility, feeder-link switchover** | ◆ |
| TS 38.331 | RRC reconfiguration for HO | ◆ |
| TS 38.413 | NGAP handover (N2-based) | ◆ |
| TS 38.423 | XnAP handover (Xn-based) | ◆ |
| TS 38.401 | F1 handover (CU/DU) | ◆ |

NTN overlay: satellite/beam handover, feeder-link switch, and (Rel-19) inter-satellite links &
store-and-forward — Rel-19 spec numbers not stable at my cutoff `⚠`.

---

## Stage 8 — Voice session (VoNR / IMS) + fallback + emergency + SMS

| Spec | Role | Conf |
|---|---|---|
| TS 23.228 | IMS architecture (stage 2) | ◆ |
| TS 24.229 | IMS / SIP call control (stage 3) | ◆ |
| TS 24.173 | IMS multimedia telephony supplementary services | ◆ |
| TS 22.173 | MMTel service requirements | ◆ |
| TS 26.114 | IMS multimedia telephony (MTSI) — media handling | ◆ |
| TS 26.131 / 26.132 | Speech quality / test methods | ⚠ |
| TS 26.441+ (EVS series) | **EVS** codec (26.441 general + 26.442–26.451 for the algorithm/testing) | ⚠ |
| TS 23.167 | IMS **emergency** sessions | ◆ |
| TS 23.040 | SMS (point-to-point) | ◆ |
| TS 24.011 | SMS radio-interface signalling (SMS over NAS) | ◆ |
| TS 23.502 | **EPS fallback / RAT fallback** for voice; N26 interface | ◆ |

NTN voice caveat: VoNR over NTN is latency-challenged, especially GEO. Through Rel-17/18 NTN was
**data-first**; direct-to-cell **voice** over satellite is an emerging Rel-18/19 topic — do **not**
assume VoNR-over-NTN is a settled, conformance-ready flow. Verify current status.

---

## EPS / LTE + IoT-NTN equivalents (satellite IoT & voice fallback)

| Spec | Role | Conf |
|---|---|---|
| TS 23.401 | EPS (LTE/EPC) architecture — target for EPS-fallback voice | ◆ |
| TS 24.301 | EPS NAS (EMM/ESM) | ◆ |
| TS 36.331 | LTE RRC (also carries **IoT-NTN** SI over satellite) | ◆ |
| TS 36.211–36.214 | LTE physical layer (IoT-NTN normative changes landed here, not a new series) | ◆ |
| TS 36.321 / 36.322 / 36.323 | LTE MAC / RLC / PDCP | ◆ |
| TS 36.101 / 36.104 | LTE UE / BS RF (NB-IoT/eMTC NTN bands) | ◆ |
| TR 36.763 | IoT-NTN study | ✅ |

---

## If you meant "D2D" = Device-to-Device (ProSe / sidelink), not satellite

Different spec family — listed so nothing is missed:

| Spec | Role | Conf |
|---|---|---|
| TR 36.843 | LTE Device-to-Device proximity services (study) | ⚠ |
| TS 23.303 | Proximity-based services (ProSe) architecture | ◆ |
| TS 24.334 | ProSe protocol (PC3/PC5) | ⚠ |
| TS 23.287 | Architecture for 5G V2X services (sidelink) | ◆ |
| TR 38.885 | NR V2X (study) | ◆ |
| TS 38.331 / 38.321 / 38.213 | NR **sidelink** RRC / MAC / PHY procedures | ◆ |
| TS 38.101-1 Annexes | NR sidelink RF | ⚠ |

Note: Rel-19 **UE-Satellite-UE** ("D2D over satellite") is the convergence point — it's NTN-side,
not ProSe sidelink. If that's your target, track the Rel-19 NTN work items above.

---

## Adjacent (non-3GPP) — mentioned for completeness, not 3GPP specs
These are **not** 3GPP TS/TR and aren't conformance specs — they're regulatory instruments,
white papers, and operator reference documents. Included so the picture is complete.

### ITU-R — spectrum & regulatory (satellite bands, direct-to-device)
| Document | Role | Conf |
|---|---|---|
| ITU Radio Regulations (2023 edition) | Binding international spectrum allocations (MSS, FSS, IMT bands) | ✅ |
| Resolution 253 (WRC-23) | Basis for studying new **MSS allocations for direct space-station → IMT UE connectivity** to complement terrestrial coverage | ✅ |
| Resolution 252 (WRC-23) | Related WRC-23 resolution on satellite/IMT complementary coverage | ◆ |
| WRC-27 Agenda Item 1.13 | Ongoing studies on new MSS allocations to complement terrestrial IMT (direct-to-device) | ✅ |
| ITU-R M-series / S-series Recommendations | Mobile-satellite (M) and fixed-satellite (S) technical characteristics — verify exact rec. numbers for your band | ⚠ |

### O-RAN Alliance — Open RAN + NTN
| Document | Role | Conf |
|---|---|---|
| O-RAN White Paper — "Deployments of O-RAN-based Non-Terrestrial Networks" (O-RAN-2025.04.02.WP.O-RAN_NTN_Deployments, v08.x) | Architecture, status, challenges, security for O-RAN + NTN | ✅ |
| O-RAN nGRG (next Generation Research Group) | 6G/NTN research reports (RR-series) | ◆ |

### GSMA — operator guidelines & roaming
| Document | Role | Conf |
|---|---|---|
| GSMA "Non-Terrestrial Networks — Opportunities and Challenges" | Operator-facing NTN overview | ✅ |
| GSMA R21 PRD (Permanent Reference Document) | Roaming reference doc **being adapted for TN↔NTN roaming** | ✅ |
| GSMA NTN Community / Foundry resources | Trials, demos, TN-NTN integration guidance | ◆ |

### Also relevant (industry / regulatory context)
- **3GPP-vs-proprietary D2D tracks:** industry recognizes three direct-to-device paths — (1) 3GPP-compliant
  NTN, (2) proprietary systems on MSS spectrum, (3) proprietary systems using unmodified 3GPP phones.
  Only track (1) is what your OAI lab and this spec index cover.
- National regulators (FCC in the US "Supplemental Coverage from Space" framework, CEPT/ECC in Europe)
  set the actual operating conditions — verify per market. `⚠`

---

## How to verify / close the gaps
Open the 3GPP specifications portal or the ETSI deliver tree, and cross-check any `◆`/`⚠` entry
against the current version for your target release (Rel-17 for baseline NTN, Rel-18/19 for
direct-to-cell and regenerative). The `✅` rows were confirmed this session; the rest are my best
recall with the exact number or clause flagged for you to confirm.
