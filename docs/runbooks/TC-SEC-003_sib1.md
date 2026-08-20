# Cursor Runbook — TC-SEC-003 (Multi-PLMN SIB1 / MOCN order)  [standalone, own logs]

Run inside the OAI NTN lab repo on the Ubuntu VM. Produces its OWN evidence folder.
In RFsim, over-the-air SIB1 is not a normal pcap interface — compare the CU vs DU config PLMN order,
and optionally confirm via F1AP (f1.pcap on loopback).

## RULES
- Never modify/rename/delete existing files. New files only under the evidence folder below.
- Report the compared PLMN order. Do NOT declare PASS/FAIL. Confirm commands first.

## STEP 1 — discover the CU and DU configs
```bash
ls -R ~ | grep -iE "cu.*conf|du.*conf|gnb.*conf" | head
grep -rilE "plmn|mcc|mnc" ~ 2>/dev/null | grep -iE "conf" | head
```
Report: the exact CU conf and DU conf paths in use.

## STEP 2 — evidence folder
```bash
TID=TC-SEC-003; OUT=~/leo-evidence/${TID}_$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"; echo "$OUT"
```

## STEP 3 — capture the PLMN order (config side)
```bash
cp <CU.conf> "$OUT/cu.conf"          # provenance copies — do NOT edit originals
cp <DU.conf> "$OUT/du.conf"
grep -inE "plmn|mcc|mnc" "$OUT/cu.conf" | tee "$OUT/cu_plmn.txt"
grep -inE "plmn|mcc|mnc" "$OUT/du.conf" | tee "$OUT/du_plmn.txt"
```

## STEP 4 — optional F1 confirmation
```bash
sudo tcpdump -i lo -w "$OUT/f1.pcap" &  echo $! > "$OUT/cap.pid"
<start CU> ... ; <start DU> ... ; sleep 20
sudo kill "$(cat "$OUT/cap.pid")"
tshark -r "$OUT/f1.pcap" -Y f1ap -V 2>/dev/null | grep -iE "plmn|mcc|mnc" | head | tee "$OUT/f1_plmn.txt"
```

## STEP 5 — self-check (report the comparison)
```bash
echo "CU first PLMN:"; head -1 "$OUT/cu_plmn.txt"
echo "DU first PLMN:"; head -1 "$OUT/du_plmn.txt"
echo "Do index-0 PLMNs match? (report yes/no — do not assert PASS)"
```

## STEP 6 — handoff
```bash
echo "Evidence: $OUT"
echo "Verify:   python3 -c \"from pipeline.features.sib1 import impl_claude; print(impl_claude.run(cu='$OUT/cu.conf', du='$OUT/du.conf').verdict)\""
```
Saves: cu.conf, du.conf, cu_plmn.txt, du_plmn.txt, f1.pcap, f1_plmn.txt. Change nothing outside "$OUT".
Note: normalize PLMN format (MCC-MNC, 2- vs 3-digit MNC) before comparing.
