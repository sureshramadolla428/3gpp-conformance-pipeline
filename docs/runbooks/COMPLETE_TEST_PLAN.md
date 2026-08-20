# Complete Test Plan — 5G / NTN Conformance (5 test cases)

Each test case below is self-contained: **definition → pass/fail criteria → setup → run → save logs →
verify.** Run on the OpenAirInterface NTN lab (Ubuntu VM, RFsim SAT_LEO, CN5G).

Test cases:
- TC-SEC-001  SUCI privacy
- TC-REG-001  Registration success
- TC-SEC-002  5G-AKA RES* == XRES*
- TC-PDU-001  PDU session + user plane
- TC-SEC-003  Multi-PLMN SIB1 / MOCN order

---

## GLOBAL SETUP (do once)

### Prerequisites
- OAI gNB (NTN), OAI nrUE (NTN), OAI CN5G running over RFsimulator SAT_LEO.
- `tshark`, `tcpdump`, `python3` installed.
- The 5G-conformance-pipeline repo available on the VM (for the verifier handoff).

### Golden rules (apply to every test)
1. Never modify/rename/delete existing files. Create NEW files only under `~/leo-evidence/<TID>_<UTC>/`.
2. Config change needed? COPY into the evidence folder, edit the copy, launch from the copy.
3. Start captures BEFORE the UE attaches.
4. Report the counts observed — do NOT declare PASS/FAIL (the verifier decides).

### Discovery (run once, reuse the answers)
```bash
docker network ls ; ip -br addr          # CN5G bridge <BR> (N2/NGAP) and N3 interface <N3>
ip -br addr | grep -iE "oaitun|gtp"      # UE tunnel (oaitun_ue1)
ls -R ~ | grep -iE "bringup|pathc|cn5g|gnb|ue|start" | head -40   # bring-up scripts
tshark -v | head -1
mkdir -p ~/leo-evidence
```
Record: `<BR>` = CN5G bridge, `<N3>` = N3 interface, and the core/gNB/UE start commands.

---

## TC-SEC-001 — SUCI privacy

### Definition
feature: suci · ts_clause: TS 33.501 §6.12 (SUCI), TS 24.501 §8.2.6 (Reg Request), §9.7 (message types) ·
interface: N2/NGAP · capture: pcap on N2 during initial registration.
**Purpose:** UE uses a concealed SUCI in the initial Registration Request and does not expose IMSI/SUPI in clear text.

### Pass / fail criteria
- Preconditions (→ INCONCLUSIVE if unmet): P1 ngap_frames>0 ; P2 registration_request_frames>0
- MUST (all → PASS): M1 Registration Request (msg 0x41) ; M2 SUCI in 5GS mobile identity
- MUST NOT (any → FAIL): N1 IMSI in identity ; N2 SUPI in identity
- Verdict: `if not(P1&P2): INCONCLUSIVE ; elif N1|N2: FAIL ; elif M1&M2: PASS ; else INCONCLUSIVE`

### Setup + run
```bash
TID=TC-SEC-001; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"
sudo tcpdump -i <BR> -w "$OUT/core.pcap" &  echo $! > "$OUT/cap.pid"   # capture FIRST
<start CN5G core> 2>&1 | tee "$OUT/core_boot.log"
<start gNB NTN>   2>&1 | tee "$OUT/gnb.log" &
<start nrUE NTN>  2>&1 | tee "$OUT/ue.log"  &
sleep 25                                     # let registration complete
sudo kill "$(cat "$OUT/cap.pid")"
{ echo "utc=$(date -u)"; echo "bridge=<BR>"; echo "tshark=$(tshark -v|head -1)";
  grep -iE "imsi|plmn|suci|scheme" <ue/gnb conf>; } > "$OUT/meta.txt"
```

### Save logs → `$OUT/`
core.pcap, gnb.log, ue.log, core_boot.log, meta.txt

### Verify (self-check counts, then pipeline)
```bash
P="$OUT/core.pcap"
echo "ngap:   $(tshark -r "$P" -Y ngap 2>/dev/null | wc -l)"
echo "regreq: $(tshark -r "$P" -Y 'nas-5gs.mm.message_type==0x41' 2>/dev/null | wc -l)"
tshark -r "$P" -Y 'nas-5gs.mm.message_type==0x41' -V 2>/dev/null | grep -iE "SUCI|IMSI|scheme|protection"
python3 -c "from pipeline.features.suci import impl_claude; print(impl_claude.run('$P').verdict)"
```
Watch for a NULL-SCHEME SUCI (protection scheme 0) — "SUCI present" but IMSI still leaks.

---

## TC-REG-001 — Registration success

### Definition
feature: registration · ts_clause: TS 24.501 §5.5.1, §9.7 · interface: N2/NGAP · capture: N2 pcap during registration.
**Purpose:** UE completes initial registration end to end and reaches 5GMM-REGISTERED.

### Pass / fail criteria
- Preconditions (→ INCONCLUSIVE): P1 ngap_frames>0 ; P2 nas_frames>0
- MUST (all → PASS): M1 Reg Request (0x41) ; M2 Auth Request(0x56)+Response(0x57) ; M3 SMC(0x5d)+SMP(0x5e) ; M4 Reg Accept(0x42)
- MUST NOT (→ FAIL): N1 Reg Reject (0x44)
- Verdict: `if not(P1&P2): INCONCLUSIVE ; elif N1: FAIL ; elif M1..M4: PASS ; else FAIL`

### Setup + run
```bash
TID=TC-REG-001; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"
sudo tcpdump -i <BR> -w "$OUT/core.pcap" &  echo $! > "$OUT/cap.pid"
<start CN5G core> 2>&1 | tee "$OUT/core_boot.log"
<start gNB NTN>   2>&1 | tee "$OUT/gnb.log" &
<start nrUE NTN>  2>&1 | tee "$OUT/ue.log"  &
sleep 25 ; sudo kill "$(cat "$OUT/cap.pid")"
```

### Save logs → `$OUT/`
core.pcap, gnb.log, ue.log, core_boot.log

### Verify
```bash
P="$OUT/core.pcap"
for m in 0x41:RegReq 0x56:AuthReq 0x57:AuthResp 0x5d:SMC 0x5e:SMP 0x42:RegAccept 0x44:RegReject; do
  hex=${m%%:*}; name=${m##*:}
  echo "$name($hex): $(tshark -r "$P" -Y "nas-5gs.mm.message_type==$hex" 2>/dev/null | wc -l)"
done
python3 -c "from pipeline.features.registration import impl_claude; print(impl_claude.run('$P').verdict)"
```

---

## TC-SEC-002 — 5G-AKA RES* == XRES*

### Definition
feature: aka · ts_clause: TS 33.501 §6.1.3.2, Annex A.4 (RES/XRES), TS 23.003 §28.x (SNN) ·
interface: AMF/gNB logs + offline Milenage recompute · capture: run/AMF log + known K,OPc,RAND,XRES*,PLMN.
**Purpose:** UE-derived RES* matches network XRES* (auth succeeds), and the Serving Network Name is well formed.

### Pass / fail criteria
- Preconditions (→ INCONCLUSIVE): P1 auth_request ; P2 inputs_available
- MUST (all → PASS): M1 Auth Request seen ; M2 Auth Response/RES* available ; M3 recomputed RES*==XRES* ; M4 SNN well formed
- MUST NOT (→ FAIL): N1 Authentication Reject / MAC failure
- Verdict: `if not(P1&P2): INCONCLUSIVE ; elif N1: FAIL ; elif M1..M4: PASS ; else FAIL`

### Setup + run
```bash
TID=TC-SEC-002; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"
sudo tcpdump -i <BR> -w "$OUT/core.pcap" & echo $! > "$OUT/cap.pid"
<start CN5G core (AMF debug/verbose)> 2>&1 | tee "$OUT/amf.log"
<start gNB NTN> 2>&1 | tee "$OUT/gnb.log" & <start nrUE NTN> 2>&1 | tee "$OUT/ue.log" &
sleep 25 ; sudo kill "$(cat "$OUT/cap.pid")"
grep -iE "opc|\bkey\b|imsi|amf" <UDM/HSS conf> > "$OUT/aka_inputs.txt"
grep -iE "rand|xres|res\*|authentication" "$OUT/amf.log" | tee "$OUT/aka_observed.txt"
tshark -r "$OUT/core.pcap" -Y 'nas-5gs.mm.message_type==0x56' -V 2>/dev/null | grep -iE "rand|autn" | tee -a "$OUT/aka_observed.txt"
```
CRITICAL: RAND, K, OPc, SNN must ALL be from THIS run or RES* won't match.

### Save logs → `$OUT/`
core.pcap, amf.log, gnb.log, ue.log, aka_inputs.txt, aka_observed.txt

### Verify
```bash
python3 -c "from pipeline.features.aka import impl_claude; print(impl_claude.run(log='$OUT/amf.log', inputs='$OUT/aka_inputs.txt').metrics)"
```
Confirm the Annex A.4 KDF and SNN format ("5G:mnc<MNC>.mcc<MCC>.3gppnetwork.org") in the reference.

---

## TC-PDU-001 — PDU session + user plane

### Definition
feature: pdu_session · ts_clause: TS 24.501 §6.4.1, TS 23.502 §4.3.2, §9.7 · interface: N2 + N3 + UE tunnel ·
capture: core pcap (N2+N3) + run.log (ping).
**Purpose:** UE establishes a PDU session and user-plane traffic flows over N3.

### Pass / fail criteria
- Preconditions (→ INCONCLUSIVE): P1 registered ; P2 nas_frames>0 ; P3 pdu_session_frames>0
- MUST (all → PASS): M1 PDU Est Request (0xc1) ; M2 PDU Est Accept (0xc2) ; M3 GTP-U on N3 ; M4 ping 0% loss
- MUST NOT (→ FAIL): N1 PDU Est Reject (0xc3)
- Verdict: `if not(P1&P2&P3): INCONCLUSIVE ; elif N1: FAIL ; elif M1..M4: PASS ; else FAIL`

### Setup + run
```bash
TID=TC-PDU-001; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"
sudo tcpdump -i <BR> -w "$OUT/core.pcap" & echo $! > "$OUT/cap1.pid"   # N2
sudo tcpdump -i <N3> -w "$OUT/n3.pcap"   & echo $! > "$OUT/cap2.pid"   # N3/GTP-U
<start CN5G core> 2>&1 | tee "$OUT/core_boot.log"
<start gNB NTN> 2>&1 | tee "$OUT/gnb.log" & <start nrUE NTN> 2>&1 | tee "$OUT/ue.log" &
sleep 25
ping -I oaitun_ue1 -c 20 <core/DN IP> 2>&1 | tee "$OUT/run.log"
sudo kill "$(cat "$OUT/cap1.pid")" "$(cat "$OUT/cap2.pid")"
```

### Save logs → `$OUT/`
core.pcap, n3.pcap, run.log, gnb.log, ue.log, core_boot.log

### Verify
```bash
echo "pdu_req:    $(tshark -r "$OUT/core.pcap" -Y 'nas-5gs.sm.message_type==0xc1' 2>/dev/null | wc -l)"
echo "pdu_accept: $(tshark -r "$OUT/core.pcap" -Y 'nas-5gs.sm.message_type==0xc2' 2>/dev/null | wc -l)"
echo "gtpu:       $(tshark -r "$OUT/n3.pcap"   -Y gtp 2>/dev/null | wc -l)"
grep -iE "packet loss|rtt" "$OUT/run.log"
python3 -c "from pipeline.features.pdu_session import impl_claude; print(impl_claude.run('$OUT/core.pcap','$OUT/n3.pcap','$OUT/run.log').verdict)"
```
Over NTN, long RTT is fine — the pass criterion is connectivity, not latency.

---

## TC-SEC-003 — Multi-PLMN SIB1 / MOCN order

### Definition
feature: sib1 · ts_clause: TS 38.331 §6.3.1 (SIB1 plmn-IdentityInfoList), TS 23.003 · interface: SIB1 / F1AP / configs ·
capture: SIB1 or f1.pcap + CU/DU configs.
**Purpose:** DU SIB1 PLMN order matches CU config order so the UE derives the intended serving network path.

### Pass / fail criteria
- Preconditions (→ INCONCLUSIVE): P1 sib1_frames>0 OR configs_present ; P2 plmn_count>=1
- MUST (all → PASS): M1 DU first PLMN == CU first PLMN ; M2 target PLMN present
- MUST NOT (→ FAIL): N1 first-PLMN mismatch
- Verdict: `if not(P1&P2): INCONCLUSIVE ; elif N1: FAIL ; elif M1&M2: PASS ; else FAIL`

### Setup + run
```bash
TID=TC-SEC-003; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"
cp <CU.conf> "$OUT/cu.conf"; cp <DU.conf> "$OUT/du.conf"      # provenance copies, don't edit originals
grep -inE "plmn|mcc|mnc" "$OUT/cu.conf" | tee "$OUT/cu_plmn.txt"
grep -inE "plmn|mcc|mnc" "$OUT/du.conf" | tee "$OUT/du_plmn.txt"
sudo tcpdump -i lo -w "$OUT/f1.pcap" & echo $! > "$OUT/cap.pid"   # optional F1 confirmation
<start CU> ... ; <start DU> ... ; sleep 20 ; sudo kill "$(cat "$OUT/cap.pid")"
tshark -r "$OUT/f1.pcap" -Y f1ap -V 2>/dev/null | grep -iE "plmn|mcc|mnc" | head | tee "$OUT/f1_plmn.txt"
```
Note: in RFsim there is no over-the-air SIB1 pcap — the config comparison is the primary evidence.

### Save logs → `$OUT/`
cu.conf, du.conf, cu_plmn.txt, du_plmn.txt, f1.pcap, f1_plmn.txt

### Verify
```bash
echo "CU first PLMN:"; head -1 "$OUT/cu_plmn.txt"
echo "DU first PLMN:"; head -1 "$OUT/du_plmn.txt"
python3 -c "from pipeline.features.sib1 import impl_claude; print(impl_claude.run(cu='$OUT/cu.conf', du='$OUT/du.conf').verdict)"
```
Normalize PLMN format (MCC-MNC, 2- vs 3-digit MNC) before comparing.

---

## Summary

| Test | Feature | Primary evidence | Verifier exists? |
|---|---|---|---|
| TC-SEC-001 | suci | core.pcap (N2) | yes |
| TC-REG-001 | registration | core.pcap (N2) | not yet |
| TC-SEC-002 | aka | amf.log + inputs + core.pcap | partial |
| TC-PDU-001 | pdu_session | core.pcap + n3.pcap + run.log | not yet |
| TC-SEC-003 | sib1 | cu/du configs + f1.pcap | not yet |

## Caveats (do not trust verdicts until confirmed)
- tshark field names / message-type hex are illustrative until confirmed on your Wireshark version
  (try underscore vs hyphen variants). Confirm hex against TS 24.501 §9.7.
- SUCI: verify the null-scheme case (protection scheme != 0).
- AKA: all crypto inputs must come from the same run.
- SIB1: RFsim has no OTA SIB1 — config/F1 comparison is the evidence.
- The pipeline verifiers exist only for `suci` today; the others need `impl_claude.py` written before
  their handoff commands will run.
