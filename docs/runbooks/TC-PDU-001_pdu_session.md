# Cursor Runbook — TC-PDU-001 (PDU session + user plane)  [standalone, own logs]

Run inside the OAI NTN lab repo on the Ubuntu VM. Produces its OWN evidence folder.
Captures BOTH N2 (5GSM signalling) and N3 (GTP-U), plus a ping result.

## RULES
- Never modify/rename/delete existing files. New files only under the evidence folder below.
- Start captures BEFORE attach. Report counts. Do NOT declare PASS/FAIL. Confirm commands first.

## STEP 1 — discover
```bash
docker network ls ; ip -br addr        # CN5G bridge <BR> (N2) and the N3 interface <N3>
ip -br addr | grep -iE "oaitun|gtp|n3"  # UE tunnel (oaitun_ue1) and N3 iface
ls -R ~ | grep -iE "bringup|cn5g|gnb|ue|start" | head -40
```
Report: <BR>, <N3>, UE tunnel name, bring-up scripts.

## STEP 2 — evidence folder
```bash
TID=TC-PDU-001; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"; echo "$OUT"
```

## STEP 3 — capture (two interfaces) + run + ping
```bash
sudo tcpdump -i <BR> -w "$OUT/core.pcap" &  echo $! > "$OUT/cap1.pid"   # N2
sudo tcpdump -i <N3> -w "$OUT/n3.pcap"   &  echo $! > "$OUT/cap2.pid"   # N3/GTP-U
<start CN5G core> 2>&1 | tee "$OUT/core_boot.log"
<start gNB NTN> 2>&1 | tee "$OUT/gnb.log" &
<start nrUE NTN> 2>&1 | tee "$OUT/ue.log" &
sleep 25
ping -I oaitun_ue1 -c 20 <core/DN IP> 2>&1 | tee "$OUT/run.log"
sudo kill "$(cat "$OUT/cap1.pid")" "$(cat "$OUT/cap2.pid")"
{ echo "utc=$(date -u)"; echo "bridge=<BR>"; echo "n3=<N3>"; echo "tshark=$(tshark -v|head -1)"; } > "$OUT/meta.txt"
```

## STEP 4 — self-check (report counts)
```bash
echo "pdu_req:    $(tshark -r "$OUT/core.pcap" -Y 'nas-5gs.sm.message_type==0xc1' 2>/dev/null | wc -l)"
echo "pdu_accept: $(tshark -r "$OUT/core.pcap" -Y 'nas-5gs.sm.message_type==0xc2' 2>/dev/null | wc -l)"
echo "pdu_reject: $(tshark -r "$OUT/core.pcap" -Y 'nas-5gs.sm.message_type==0xc3' 2>/dev/null | wc -l)"
echo "gtpu:       $(tshark -r "$OUT/n3.pcap"   -Y gtp 2>/dev/null | wc -l)"
grep -iE "packet loss|rtt" "$OUT/run.log"
```
Verify the 5GSM field name `nas-5gs.sm.message_type` and which pcap actually holds N3.

## STEP 5 — handoff
```bash
echo "Evidence: $OUT"
echo "Verify:   python3 -c \"from pipeline.features.pdu_session import impl_claude; print(impl_claude.run('$OUT/core.pcap','$OUT/n3.pcap','$OUT/run.log').verdict)\""
```
Saves: core.pcap, n3.pcap, run.log, gnb.log, ue.log, core_boot.log, meta.txt. Change nothing outside "$OUT".
