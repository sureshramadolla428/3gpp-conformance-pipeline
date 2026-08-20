# NTN 3GPP Conformance Test Cases
**New test cases — no existing files modified.**  
All evidence auto-saved to Windows Desktop via VMware shared folder.

---

## How evidence is saved automatically

```
Ubuntu VM runs test
       ↓
capture-l2l3.sh captures UE + gNB + core logs + pcaps
       ↓
Saved to: ~/leo-evidence/l2l3_<TEST-ID>_<TIMESTAMP>/
       ↓
VMware shared folder syncs automatically
       ↓
Windows Desktop: Setup Instructions\evidence\<TEST-ID>_<TIMESTAMP>\
       ├── core.pcap          ← CN5G bridge (N2/N3/SBI)
       ├── f1.pcap            ← F1 interface (CU↔DU)
       ├── ue_dataplane.pcap  ← oaitun_ue1 (UE tunnel)
       ├── gnb.log            ← gNB log
       ├── ue.log             ← UE log
       ├── run.log            ← test script output
       └── meta.txt           ← test metadata + OAI version
```

---

## Step 0 — One-time Windows folder setup (do this first)

### In VMware Settings (on Windows):

1. Open **VMware Workstation / Fusion**
2. Go to **VM → Settings → Shared Folders**
3. Click **Add** and map:
   ```
   Windows path:  C:\Users\sures\OneDrive\Desktop\Setup Instructions\evidence
   VM name:       ntn-evidence
   ```
4. Tick **Enable this share** → OK

### In Ubuntu VM terminal:

```bash
# Verify the share is visible
ls /mnt/hgfs/

# Create the evidence output folder (mirrors Windows Desktop)
mkdir -p /mnt/hgfs/ntn-evidence

# Set the default output directory for all test runs
echo 'export NTN_EVIDENCE_DIR="/mnt/hgfs/ntn-evidence"' >> ~/.bashrc
source ~/.bashrc

# Verify it works
echo "test" > /mnt/hgfs/ntn-evidence/verify.txt
# Check on Windows Desktop → Setup Instructions\evidence\verify.txt should appear
```

### Shortcut alias (paste into Ubuntu terminal once):

```bash
cat >> ~/.bashrc << 'EOF'

# NTN test runner — saves evidence directly to Windows Desktop
ntn-run() {
  local test_id="$1"
  local run_cmd="$2"
  local out_dir="/mnt/hgfs/ntn-evidence/${test_id}_$(date +%Y%m%d_%H%M%S)"
  echo "[NTN] Running $test_id → $out_dir"
  bash ~/oai-config/validation/capture-l2l3.sh \
    --test-id "$test_id" \
    --run-cmd "$run_cmd" \
    --out-dir "$out_dir"
}
EOF
source ~/.bashrc
```

After this, every test is just: `ntn-run TC-NTN-001 'bash ~/oai-config/...'`

---

## Test Cases

---

### TC-NTN-001 — LEO Attach + SIB19 Timing Conformance

**3GPP reference:** TS 38.331 §6.3.1 (SIB19), TS 38.300 §9.2.6 (NTN TA)  
**What it proves:** gNB broadcasts correct SIB19 with ta-Common and Koffset values; UE attaches successfully using NTN timing advance  
**Expected result:** PASS — PDU session up, ping succeeds, SIB19 present in capture  
**Based on:** `TC-PATHC-LEO` from existing catalog

**Ubuntu terminal — run this:**
```bash
ntn-run TC-NTN-001 'bash ~/oai-config/path-c/pathc-bringup-du0.sh'
```

**What gets saved to Windows:**
```
evidence\TC-NTN-001_<timestamp>\
  ├── core.pcap        ← verify SIB19 in here with tshark
  ├── f1.pcap          ← F1 setup messages
  ├── ue_dataplane.pcap
  ├── run.log          ← look for "PDU SESSION ESTABLISHED" + ping output
  └── meta.txt
```

**Verify SIB19 in saved pcap (run on Windows with Wireshark or tshark):**
```
tshark -r core.pcap -Y "nr-rrc.sib19" -V | grep -i "ta-Common\|koffset\|epochTime"
```

---

### TC-NTN-002 — SIB19 ta-Common / Koffset Encoding Verification

**3GPP reference:** TS 38.331 §6.3.1 Table — SIB19 fields: ta-Common, ta-CommonDrift, Koffset  
**What it proves:** The encoded SIB19 values match what the config file specifies (no silent encoding error)  
**Expected result:** PASS — tshark-decoded ta-Common matches gnb-du0.conf value  
**Based on:** Your existing SIB19 NTN encoding work in `docs/OAI_ISSUE_nr_update_sib19.md`

**Ubuntu terminal — run this:**
```bash
ntn-run TC-NTN-002 'bash ~/oai-config/path-c/pathc-bringup-du0.sh'

# After run completes, extract ta-Common from the saved pcap:
LATEST=$(ls -dt /mnt/hgfs/ntn-evidence/TC-NTN-002_* | head -1)
tshark -r "$LATEST/core.pcap" \
  -Y "nr-rrc.sib19" -T fields \
  -e nr-rrc.ta-Common \
  -e nr-rrc.kOffset 2>/dev/null | head -5
```

**Then check against your config:**
```bash
grep -i "ta_common\|koffset\|ntn" ~/oai-config/path-c/gnb-du0*.conf | head -10
```

**Expected:** tshark-decoded value == config file value → conformance proven

---

### TC-NTN-003 — 5G-AKA with Correct PLMN Order (Gate-2 Regression Guard)

**3GPP reference:** TS 33.501 §6.1.3.2, TS 23.003 §28.7  
**What it proves:** After the plmn_list order fix, AKA succeeds (RES* == XRES*) — guards against regression  
**Expected result:** PASS — Registration Accept on AMF-2 for IMSI 208930000000001  
**Based on:** Your Gate-2 fix in `oai-config/multi-plmn/second-amf/fix-gate2-sib1-order.sh`

**Ubuntu terminal — run this:**
```bash
ntn-run TC-NTN-003 'bash ~/oai-config/multi-plmn/second-amf/fix-gate2-sib1-order.sh'
```

**Verify AKA success in saved logs:**
```bash
LATEST=$(ls -dt /mnt/hgfs/ntn-evidence/TC-NTN-003_* | head -1)
echo "=== AKA result ==="
grep -i "registration accept\|5gmm-registered\|authentication\|res\*" "$LATEST/run.log" | tail -20
```

**Expected lines in run.log:**
```
Registration Accept
5GMM-REGISTERED
```

---

### TC-NTN-004 — SUCI Conformance During NTN Attach

**3GPP reference:** TS 33.501 §6.1.3  
**What it proves:** UE uses SUCI (not clear IMSI) during initial NTN registration  
**Expected result:** PASS — SUCI IE present, SMC/SMP exchange confirmed in core.pcap  
**Based on:** `TC-CAP-SUCI` from existing catalog

**Ubuntu terminal — run this:**
```bash
ntn-run TC-NTN-004 'bash ~/oai-config/capture-suci-attach.sh'
```

**Verify SUCI in saved pcap:**
```bash
LATEST=$(ls -dt /mnt/hgfs/ntn-evidence/TC-NTN-004_* | head -1)
tshark -r "$LATEST/core.pcap" \
  -Y "nas-5gs.mm.suci.scheme_id || nas-5gs.mm.message_type == 0x5d" \
  -T fields -e frame.number -e nas-5gs.mm.message_type 2>/dev/null
```

**Or run the pipeline verifier directly against the saved pcap:**
```bash
cd ~/5g-conformance-pipeline   # if cloned on VM
python3 -c "
from pipeline.features.suci import impl_claude
from pathlib import Path
r = impl_claude.run('$LATEST/core.pcap')
print(r.verdict, r.notes)
"
```

---

### TC-NTN-005 — F1 Handover in NTN (AWGN Channel)

**3GPP reference:** TS 38.401 §8.9 (F1 interface handover)  
**What it proves:** F1 HO signalling completes, UE stays registered, UP continues post-HO  
**Expected result:** PASS — HO complete in signalling; ping survives HO  
**Based on:** `TC-PATHC-HO-AWGN` from existing catalog

**Ubuntu terminal — run this:**
```bash
ntn-run TC-NTN-005 'PATHC_CHANNEL=AWGN bash ~/oai-config/path-c/pathc-du1-ho.sh'
```

**Verify HO in saved files:**
```bash
LATEST=$(ls -dt /mnt/hgfs/ntn-evidence/TC-NTN-005_* | head -1)
echo "=== HO signalling ==="
grep -i "handover\|ho complete\|path switch\|ue context" "$LATEST/run.log" | head -20
echo "=== Ping survival ==="
grep -i "icmp\|bytes from\|ping" "$LATEST/run.log" | tail -10
```

---

### TC-NTN-006 — Dynamic NTN Timing Hot-Reload

**3GPP reference:** TS 38.331 §5.2.2 (SIB scheduling), TR 38.821 §5.4 (NTN timing)  
**What it proves:** NTN timing parameters (ta-Common, Koffset) update without full restart  
**Expected result:** PASS — new SIB19 timing visible in pcap after reload, UE stays attached  
**Based on:** `automation/dynamic_ntn_timing.py` + `automation/live_ntn_timing_reload.sh`

**Ubuntu terminal — run this:**
```bash
ntn-run TC-NTN-006 'bash ~/automation/live_ntn_timing_reload.sh'
```

**Verify timing change in captures:**
```bash
LATEST=$(ls -dt /mnt/hgfs/ntn-evidence/TC-NTN-006_* | head -1)
tshark -r "$LATEST/core.pcap" \
  -Y "nr-rrc.sib19" -T fields \
  -e frame.time -e nr-rrc.ta-Common 2>/dev/null
# Should show two different ta-Common values (before and after reload)
```

---

## Quick Reference — Run All 6 Tests in Sequence

```bash
# On Ubuntu VM — paste this block to run all NTN test cases

echo "=== TC-NTN-001: LEO Attach ==="
ntn-run TC-NTN-001 'bash ~/oai-config/path-c/pathc-bringup-du0.sh'

echo "=== TC-NTN-002: SIB19 Encoding ==="
ntn-run TC-NTN-002 'bash ~/oai-config/path-c/pathc-bringup-du0.sh'

echo "=== TC-NTN-003: 5G-AKA Gate-2 ==="
ntn-run TC-NTN-003 'bash ~/oai-config/multi-plmn/second-amf/fix-gate2-sib1-order.sh'

echo "=== TC-NTN-004: SUCI ==="
ntn-run TC-NTN-004 'bash ~/oai-config/capture-suci-attach.sh'

echo "=== TC-NTN-005: F1 HO ==="
ntn-run TC-NTN-005 'PATHC_CHANNEL=AWGN bash ~/oai-config/path-c/pathc-du1-ho.sh'

echo "=== TC-NTN-006: Dynamic Timing ==="
ntn-run TC-NTN-006 'bash ~/automation/live_ntn_timing_reload.sh'

echo "=== All done. Evidence on Windows Desktop: Setup Instructions\evidence\ ==="
```

---

## What you will see on Windows Desktop after running

```
C:\Users\sures\OneDrive\Desktop\Setup Instructions\evidence\
├── TC-NTN-001_20260723_143000\
│   ├── core.pcap          ← open in Wireshark
│   ├── f1.pcap
│   ├── ue_dataplane.pcap
│   ├── gnb.log
│   ├── ue.log
│   ├── run.log
│   └── meta.txt
├── TC-NTN-002_20260723_144500\
│   └── ...
└── TC-NTN-003_20260723_150000\
    └── ...
```

Each folder is named by test case + timestamp. Open any `.pcap` in Wireshark on Windows directly.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `/mnt/hgfs/ntn-evidence` not found | VMware Tools not installed: `sudo apt install open-vm-tools` |
| `ntn-run: command not found` | Run `source ~/.bashrc` again |
| `core.pcap` empty | CN5G not up when test ran — check `meta.txt` for `cn_if=` |
| `ue_dataplane.pcap` missing | UE tunnel (oaitun_ue1) never came up — check `run.log` for errors |
