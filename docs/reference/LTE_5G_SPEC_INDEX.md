# LTE (4G / EPS) + 5G (5GS) — 3GPP Spec Index

Full terrestrial call flow: **UE switch-on → cell search → random access → RRC → attach/registration
→ authentication → bearer/PDU session (data) → mobility → voice (VoLTE/VoNR)**, LTE and 5G side by side.

## Honesty notes (read first)
- **Comprehensive, not provably exhaustive.** These are the core specs per stage; per-release change
  requests add detail. Treat as a strong working index, not a certified list.
- **Confidence legend:**
  - `◆` high confidence — foundational spec, stable number; **verify exact version/clause for your release**
  - `⚠` medium confidence — **verify the spec number itself** (mostly granular CN service/Diameter/SBI specs)
  - `✅` confirmed against 3GPP/ETSI earlier this session
- **Source of this list:** mostly my own knowledge (these core specs are stable), not per-line web
  verification. Knowledge cutoff ~May 2025 — confirm current versions on the 3GPP portal.
- LTE = E-UTRAN + EPC (Evolved Packet System). 5G = NR + 5GC (5G System, Standalone).
  This index assumes **5G SA**; NSA (option 3) reuses the EPC with an NR secondary node.

---

## Quick LTE ↔ 5G mapping cheat-sheet

| Function | LTE (4G) | 5G (SA) |
|---|---|---|
| Radio access | E-UTRAN (eNB) | NG-RAN (gNB; CU/DU split) |
| Core | EPC (MME, SGW, PGW, HSS, PCRF) | 5GC (AMF, SMF, UPF, UDM, AUSF, PCF, NRF) |
| NAS | TS 24.301 (EMM/ESM) | TS 24.501 (5GMM/5GSM) |
| RRC | TS 36.331 | TS 38.331 |
| Architecture | TS 23.401 | TS 23.501 / 23.502 |
| Security | TS 33.401 | TS 33.501 |
| User-plane tunnel | GTP-U (TS 29.281) | GTP-U (TS 29.281) |
| CP interface (core) | Diameter / GTP-C | Service-Based Interface (HTTP/2, SBI) |
| Subscriber ID (privacy) | IMSI (sent in clear) | SUPI concealed as **SUCI** |

---

## Stage 0 — UE switch-on / provisioning / identities

| Item | LTE | 5G | Conf |
|---|---|---|---|
| UICC / card platform | TS 31.101 | TS 31.101 | ◆ |
| SIM/USIM application | TS 31.102 (USIM) | TS 31.102 (USIM; stores home-network public key for SUCI) | ◆ |
| Identifiers | TS 23.003 (IMSI, GUTI, S-TMSI) | TS 23.003 (SUPI, SUCI, 5G-GUTI, 5G-S-TMSI) | ◆ |
| UE capabilities | TS 36.306 | TS 38.306 | ◆ |

---

## Stage 1 — Cell search, synchronization, system information

| Layer | LTE | 5G | Conf |
|---|---|---|---|
| PHY channels & modulation | TS 36.211 | TS 38.211 | ◆ |
| Channel coding | TS 36.212 | TS 38.212 | ◆ |
| PHY procedures (control) | TS 36.213 | TS 38.213 | ◆ |
| PHY procedures (data) | TS 36.213 | TS 38.214 | ◆ |
| Idle-mode / cell selection | TS 36.304 | TS 38.304 | ◆ |
| RRC / system information | TS 36.331 (MIB/SIBs) | TS 38.331 (MIB/SIB1/SIBs) | ◆ |
| RRM requirements | TS 36.133 | TS 38.133 | ◆ |
| UE RF | TS 36.101 | TS 38.101-1 (FR1) / -2 (FR2) / -3 (interworking) / -4 (perf) | ◆ |
| Base-station RF | TS 36.104 (eNB) | TS 38.104 (gNB) | ◆ |

---

## Stage 2 — Random access

| Layer | LTE | 5G | Conf |
|---|---|---|---|
| MAC (RACH, timing advance) | TS 36.321 | TS 38.321 | ◆ |
| PHY RACH procedures | TS 36.213 | TS 38.213 | ◆ |
| PRACH formats | TS 36.211 | TS 38.211 | ◆ |

---

## Stage 3 — RRC connection + RAN architecture

| Item | LTE | 5G | Conf |
|---|---|---|---|
| Overall RAN description | TS 36.300 | TS 38.300 | ◆ |
| RRC | TS 36.331 | TS 38.331 | ◆ |
| PDCP | TS 36.323 | TS 38.323 | ◆ |
| RLC | TS 36.322 | TS 38.322 | ◆ |
| MAC | TS 36.321 | TS 38.321 | ◆ |
| SDAP (QoS→DRB, 5G only) | — | TS 37.324 | ◆ |
| RAN architecture | TS 36.401 | TS 38.401 (incl. CU/DU) | ◆ |
| Core-facing AP | S1AP: TS 36.413 | NGAP: TS 38.413 | ◆ |
| Inter-node AP | X2AP: TS 36.423 | XnAP: TS 38.423 | ◆ |
| CU/DU F1 | — | F1AP: TS 38.473 | ◆ |
| CU-CP/CU-UP E1 | — | E1AP: TS 38.463 | ⚠ |
| Multi-RAT dual connectivity | TS 37.340 (EN-DC / MR-DC) | TS 37.340 | ◆ |

---

## Stage 4 — NAS attach / registration

| Item | LTE | 5G | Conf |
|---|---|---|---|
| NAS protocol | TS 24.301 (EMM attach / TAU) | TS 24.501 (5GMM registration) | ◆ |
| System architecture | TS 23.401 | TS 23.501 | ◆ |
| Procedures (stage 2) | TS 23.401 | TS 23.502 | ◆ |
| Policy & charging | TS 23.203 | TS 23.503 | ◆ |
| NAS transport over RAN | S1AP Initial UE Message (TS 36.413) | NGAP Initial UE Message (TS 38.413) | ◆ |

---

## Stage 5 — Authentication & security

| Item | LTE | 5G | Conf |
|---|---|---|---|
| Security architecture | TS 33.401 (EPS AKA) | TS 33.501 (5G-AKA, EAP-AKA′, SUCI) | ◆ |
| NAS security mode | TS 24.301 | TS 24.501 (§5.4.2 SMC; §4.4.6 initial-NAS) | ✅ |
| MILENAGE algorithm set | TS 35.205–35.208 | TS 35.205–35.208 | ◆ |
| TUAK algorithm set | TS 35.231–35.233 | TS 35.231–35.233 | ◆ |
| HSS/UDM auth interface | S6a Diameter: TS 29.272 | Nudm/Nausf: TS 29.503 / 29.509 | ⚠ |

---

## Stage 6 — Bearer / PDU session (data)

| Item | LTE | 5G | Conf |
|---|---|---|---|
| Session mgmt NAS | ESM (TS 24.301) | 5GSM (TS 24.501) | ◆ |
| Session/QoS model | EPS bearers (TS 23.401) | PDU sessions / QoS flows (TS 23.501) | ◆ |
| User-plane tunnel | GTP-U: TS 29.281 (S1-U, S5/S8) | GTP-U: TS 29.281 (N3) | ◆ |
| Control-plane core tunnel | GTP-C v2: TS 29.274 (S11, S5/S8, S10) | N4 PFCP: TS 29.244 | ◆ |
| SMF/PGW-C service | — (PGW-C in 29.274) | Nsmf: TS 29.502 | ⚠ |
| AMF service | — (MME) | Namf: TS 29.518 | ⚠ |
| NRF / discovery | — (DNS/static) | Nnrf: TS 29.510 | ⚠ |
| SBI framework | — | TS 29.500 / 29.501 (HTTP/2 + OpenAPI) | ◆ |
| Policy interface | Gx: TS 29.212, Rx: TS 29.214 | Npcf: TS 29.507 / 29.512 | ⚠ |
| Charging | TS 32.240 series | TS 32.240 / TS 32.290+ (Nchf) | ⚠ |

---

## Stage 7 — Mobility / handover

| Item | LTE | 5G | Conf |
|---|---|---|---|
| HO overview | TS 36.300 | TS 38.300 | ◆ |
| RRC reconfiguration | TS 36.331 | TS 38.331 | ◆ |
| Core-controlled (S1/N2) HO | S1AP: TS 36.413 | NGAP: TS 38.413 | ◆ |
| RAN-controlled (X2/Xn) HO | X2AP: TS 36.423 | XnAP: TS 38.423 | ◆ |
| Inter-system (4G↔5G) | TS 23.401 / 23.501 (N26 interface) | TS 23.502 | ◆ |

---

## Stage 8 — Voice (VoLTE / VoNR) + IMS + fallback + SMS

| Item | LTE (VoLTE) | 5G (VoNR) | Conf |
|---|---|---|---|
| IMS architecture (stage 2) | TS 23.228 | TS 23.228 | ◆ |
| IMS call control / SIP (stage 3) | TS 24.229 | TS 24.229 | ◆ |
| MMTel service reqs | TS 22.173 | TS 22.173 | ◆ |
| MMTel supplementary services | TS 24.173 | TS 24.173 | ◆ |
| IMS media / MTSI | TS 26.114 | TS 26.114 | ◆ |
| IMS emergency | TS 23.167 | TS 23.167 | ◆ |
| Speech codecs | AMR/AMR-WB: TS 26.071 / 26.171 / 26.190; EVS: TS 26.441+ | same (EVS: TS 26.441+) | ⚠ |
| Voice fallback | CS Fallback: TS 23.272; SRVCC: TS 23.216 | **EPS fallback / RAT fallback**: TS 23.502 (N26) | ◆ |
| SMS | TS 23.040; TS 24.011; SGs/SGd: TS 29.118 / 29.338 | SMS over NAS: TS 24.501 + TS 23.040; SMSF: TS 29.540 | ⚠ |

---

## Core-network interface protocols (reference)

| Protocol | LTE spec | 5G spec | Conf |
|---|---|---|---|
| GTP-U (user plane) | TS 29.281 | TS 29.281 | ◆ |
| GTP-C v2 (EPC control) | TS 29.274 | — (5GC uses SBI + PFCP) | ◆ |
| PFCP (CP/UP separation, N4) | TS 29.244 (CUPS) | TS 29.244 | ◆ |
| Diameter S6a (MME–HSS) | TS 29.272 | — | ◆ |
| Diameter Gx / Rx | TS 29.212 / 29.214 | — | ◆ |
| SBI (HTTP/2) framework | — | TS 29.500 / 29.501 | ◆ |
| Nudm / Nausf / Nsmf / Namf / Nnrf / Npcf | — | TS 29.503 / 29.509 / 29.502 / 29.518 / 29.510 / 29.507 | ⚠ |

---

## Service & requirements specs (both)
| Spec | Role | Conf |
|---|---|---|
| TS 22.261 | 5G service requirements | ◆ |
| TS 22.101 | Service principles | ◆ |
| TS 22.278 | EPS service requirements | ⚠ |
| TS 22.173 | MMTel (voice) service requirements | ◆ |

---

## How to verify
Cross-check any `◆`/`⚠` entry against the current version for your target release on the 3GPP
specifications portal or the ETSI deliver tree. The `⚠` rows (mostly granular Diameter/SBI service
specs and codec/SMS numbers) are where I'm least certain of the exact number — confirm those first.
The `✅` row (TS 24.501 §4.4.6 / §5.4.2) was verified earlier this session.
