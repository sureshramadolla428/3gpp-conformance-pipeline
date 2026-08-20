# Cursor Runbook — TC-SEC-001 (SUCI privacy)  [standalone, own logs]

Run inside the OAI NTN lab repo on the Ubuntu VM. Produces its OWN evidence folder.

## RULES
- Never modify/rename/delete existing files. Create NEW files only under the evidence folder below.
- If a config edit is needed: COPY into the evidence folder, edit the copy, launch from the copy.
- Start the capture BEFORE the UE attaches (else the Registration Request / SUCI is lost).
- Report the counts you see. Do NOT declare PASS/FAIL — the verifier decides.
- Print the exact commands and wait for my confirmation before running.

## STEP 1 — discover (report back)
```bash
docker network ls ; ip -br addr        # find the CN5G bridge that carries N2 (NGAP/NAS)
ls -R ~ | grep -iE "bringup|pathc|cn5g|gnb|ue|start" | head -40   # find bring-up scripts
tshark -v | head -1
```
Report: CN5G bridge name (<BR>) and the core/gNB/UE bring-up scripts.

## STEP 2 — set up evidence folder
```bash
TID=TC-SEC-001; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"; echo "$OUT"
```

## STEP 3 — capture + run (capture FIRST)
```bash
sudo tcpdump -i <BR> -w "$OUT/core.pcap" &  echo $! > "$OUT/cap.pid"
<start CN5G core>  2>&1 | tee "$OUT/core_boot.log"
<start gNB NTN>    2>&1 | tee "$OUT/gnb.log" &
<start nrUE NTN>   2>&1 | tee "$OUT/ue.log"  &
sleep 25                                        # let registration complete
sudo kill "$(cat "$OUT/cap.pid")"
```

## STEP 4 — provenance
```bash
{ echo "utc=$(date -u)"; echo "bridge=<BR>"; echo "tshark=$(tshark -v|head -1)";
  echo "--- ue/gnb conf identity ---"; grep -iE "imsi|plmn|suci|scheme" <ue/gnb conf>; } > "$OUT/meta.txt"
```

## STEP 5 — self-check (report counts only)
```bash
P="$OUT/core.pcap"
echo "ngap:   $(tshark -r "$P" -Y ngap 2>/dev/null | wc -l)"
echo "nas:    $(tshark -r "$P" -Y nas-5gs 2>/dev/null | wc -l)"
echo "regreq: $(tshark -r "$P" -Y 'nas-5gs.mm.message_type==0x41' 2>/dev/null | wc -l)"
# SUCI vs IMSI + null-scheme check — VERIFY field names for your Wireshark version:
tshark -r "$P" -Y 'nas-5gs.mm.message_type==0x41' -V 2>/dev/null | grep -iE "SUCI|IMSI|scheme|protection"
```

## STEP 6 — handoff
```bash
echo "Evidence: $OUT"
echo "Verify:   python3 -c \"from pipeline.features.suci import impl_claude; print(impl_claude.run('$OUT/core.pcap').verdict)\""
```
Saves: core.pcap, gnb.log, ue.log, core_boot.log, meta.txt. Change nothing outside "$OUT".
Note: watch for a NULL-SCHEME SUCI (protection scheme 0) — that is "SUCI present" but still leaks the IMSI.
