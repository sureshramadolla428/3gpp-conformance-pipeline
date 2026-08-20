# Cursor Runbook — TC-REG-001 (Initial registration success)  [standalone, own logs]

Run inside the OAI NTN lab repo on the Ubuntu VM. Produces its OWN evidence folder.

## RULES
- Never modify/rename/delete existing files. Create NEW files only under the evidence folder below.
- Config edits: copy into evidence folder, edit copy, launch from copy.
- Start the capture BEFORE the UE attaches.
- Report counts. Do NOT declare PASS/FAIL. Print commands and wait for confirmation first.

## STEP 1 — discover
```bash
docker network ls ; ip -br addr        # CN5G bridge <BR> carrying N2 (NGAP/NAS)
ls -R ~ | grep -iE "bringup|pathc|cn5g|gnb|ue|start" | head -40
```
Report: <BR> and bring-up scripts.

## STEP 2 — evidence folder
```bash
TID=TC-REG-001; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"; echo "$OUT"
```

## STEP 3 — capture + run
```bash
sudo tcpdump -i <BR> -w "$OUT/core.pcap" &  echo $! > "$OUT/cap.pid"
<start CN5G core> 2>&1 | tee "$OUT/core_boot.log"
<start gNB NTN>   2>&1 | tee "$OUT/gnb.log" &
<start nrUE NTN>  2>&1 | tee "$OUT/ue.log"  &
sleep 25
sudo kill "$(cat "$OUT/cap.pid")"
{ echo "utc=$(date -u)"; echo "bridge=<BR>"; echo "tshark=$(tshark -v|head -1)"; } > "$OUT/meta.txt"
```

## STEP 4 — self-check (report the 7 counts)
```bash
P="$OUT/core.pcap"
for m in 0x41:RegReq 0x56:AuthReq 0x57:AuthResp 0x5d:SMC 0x5e:SMP 0x42:RegAccept 0x44:RegReject; do
  hex=${m%%:*}; name=${m##*:}
  echo "$name($hex): $(tshark -r "$P" -Y "nas-5gs.mm.message_type==$hex" 2>/dev/null | wc -l)"
done
```
If any read 0, verify the message-type field/hex against TS 24.501 §9.7.

## STEP 5 — handoff
```bash
echo "Evidence: $OUT"
echo "Verify:   python3 -c \"from pipeline.features.registration import impl_claude; print(impl_claude.run('$OUT/core.pcap').verdict)\""
```
Saves: core.pcap, gnb.log, ue.log, core_boot.log, meta.txt. Change nothing outside "$OUT".
