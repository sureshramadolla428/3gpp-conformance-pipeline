# Cursor Runbook — TC-SEC-002 (5G-AKA RES* == XRES*)  [standalone, own logs]

Run inside the OAI NTN lab repo on the Ubuntu VM. Produces its OWN evidence folder.
This is the complex one: RES* is recomputed OFFLINE and compared to the network XRES*.

## RULES
- Never modify/rename/delete existing files. New files only under the evidence folder below.
- Report match / no-match. Do NOT declare PASS/FAIL. Print commands and wait for confirmation.

## STEP 1 — discover
```bash
docker network ls ; ip -br addr        # CN5G bridge <BR>
ls -R ~ | grep -iE "bringup|cn5g|gnb|ue|udm|hss|start" | head -40
# where are K / OPc / IMSI configured? (UDM/HSS or subscriber db)
grep -rilE "opc|\bkey\b|imsi" ~ 2>/dev/null | grep -iE "conf|yaml|db|json" | head
```
Report: <BR>, bring-up scripts, and the file holding K/OPc/IMSI.

## STEP 2 — evidence folder
```bash
TID=TC-SEC-002; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"; echo "$OUT"
```

## STEP 3 — run with AMF debug logging + capture
```bash
sudo tcpdump -i <BR> -w "$OUT/core.pcap" &  echo $! > "$OUT/cap.pid"
<start CN5G core (AMF debug/verbose)> 2>&1 | tee "$OUT/amf.log"
<start gNB NTN> 2>&1 | tee "$OUT/gnb.log" &
<start nrUE NTN> 2>&1 | tee "$OUT/ue.log" &
sleep 25
sudo kill "$(cat "$OUT/cap.pid")"
```

## STEP 4 — collect crypto inputs from the SAME run
```bash
# subscriber key material (from config) — copy the relevant lines, do NOT edit originals
grep -iE "opc|\bkey\b|imsi|amf" <UDM/HSS conf> > "$OUT/aka_inputs.txt"
# observed RAND / XRES* / result (from AMF log or the Authentication Request in core.pcap)
grep -iE "rand|xres|res\*|authentication (accept|reject|failure)" "$OUT/amf.log" | tee "$OUT/aka_observed.txt"
tshark -r "$OUT/core.pcap" -Y 'nas-5gs.mm.message_type==0x56' -V 2>/dev/null | grep -iE "rand|autn" | tee -a "$OUT/aka_observed.txt"
```
CRITICAL: the RAND, K, OPc and SNN must all be from THIS run, or RES* will not match.

## STEP 5 — offline recompute (report match only)
```bash
python3 -c "from pipeline.features.aka import impl_claude; \
print(impl_claude.run(log='$OUT/amf.log', inputs='$OUT/aka_inputs.txt').metrics)"
```
Report: res_star_match, snn_correct, auth_reject. Verify the Annex A.4 KDF and the SNN format
("5G:mnc<MNC>.mcc<MCC>.3gppnetwork.org") in the reference before trusting the result.

## STEP 6 — handoff
```bash
echo "Evidence: $OUT"
```
Saves: core.pcap, amf.log, gnb.log, ue.log, aka_inputs.txt, aka_observed.txt. Change nothing outside "$OUT".
