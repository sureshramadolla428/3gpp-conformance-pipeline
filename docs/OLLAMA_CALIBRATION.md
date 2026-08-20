# Offline calibration — generate llama3 / mistral verifiers, then diff against Claude

This is the bottom half of the pipeline diagram: the offline models write their own
verifiers, `diff_report.py` compares all three against the Claude REFERENCE, and you
correct the offline ones until they agree. When they agree, the result is frozen as golden.

The core principle: **give the offline model the spec, NOT Claude's code.** If it saw
`impl_claude.py` it would just copy it and there would be nothing to calibrate. It must
reason from the human-authored `spec.md` on its own — the divergences are the whole point.

---

## 0. One-time setup (Windows PowerShell)
```powershell
# Install Ollama: https://ollama.com/download  (then reopen PowerShell)
ollama --version
ollama pull llama3
ollama pull mistral
```

---

## 1. The contract each offline impl must satisfy
Every `impl_<model>.py` must expose `run(...)` returning a `pipeline.shared.result.VerificationResult`
and emit exactly the metric keys the reference uses:

| feature | run() input | required metric keys | FAIL when |
|---|---|---|---|
| suci | pcap or folder | ngap_frames, nas_frames, security_mode_command, security_mode_complete, suci_frames, **null_scheme_frames**, clear_imsi_frames | null_scheme_frames > 0 (or SMC/SMP/SUCI missing) |
| registration | pcap or folder | ngap_frames, nas_frames, reg_request, auth_present, security_complete, reg_accept, reg_reject | reg_reject > 0 or sequence incomplete |
| aka | evidence folder | auth_request, auth_request_seen, auth_response_seen, inputs_available, res_star_match, snn_correct, auth_reject | auth_reject or RES* mismatch |
| pdu_session | evidence folder | registered, nas_frames, pdu_session_frames, pdu_req, pdu_accept, gtpu_frames, ping_ok, pdu_reject | pdu_reject or user plane incomplete |
| sib1 | evidence folder | sib1_frames, configs_present, plmn_count, cu_first_plmn, du_first_plmn, plmn_order_match, target_plmn_present, plmn_order_mismatch | plmn_order_mismatch |

The exact prompt for each is already in the header of every `impl_llama3.py` / `impl_mistral.py`.

---

## 2. Generate an offline impl (repeat per feature × per model)
Feed the model the spec plus the header prompt. Example — suci with llama3:
```powershell
$feature = "suci"; $model = "llama3"
$spec = Get-Content "pipeline\features\$feature\spec.md" -Raw
$prompt = @"
Write a Python module with a function run(pcap) that returns a
pipeline.shared.result.VerificationResult. Use tshark via subprocess to parse the pcap.
You may import: from pipeline.shared.tshark import find_tshark, count, count_msg_type
Emit EXACTLY these metric keys and this verdict logic from the spec below.
model='$model', feature='$feature'. Output ONLY Python code, no prose.

SPEC:
$spec
"@
$prompt | ollama run $model | Out-File -Encoding utf8 "pipeline\features\$feature\impl_$model.generated.py"
```
Then open `impl_$model.generated.py`, strip any markdown fences / prose, and paste the working
`run()` into `impl_$model.py` (replace the NOT-IMPLEMENTED stub body). Keep the
`MODEL / FEATURE / TS_CLAUSE` constants intact.

> Expect the first output to be imperfect — wrong field names, missing metrics, wrong verdict
> order. That is normal and is exactly what the diff step is for.

---

## 3. Compare against the Claude reference
```powershell
python compare\diff_report.py --feature suci
# or all five at once:
python compare\diff_report.py --all
```
Read the table. Each metric row shows CLAUDE vs LLAMA3 vs MISTRAL:
- `✅ agree` — offline matches the reference.
- `⚠ DISAGREE` + `[NEEDS CORRECTION]` — the offline impl is wrong on that metric.
- `NOT YET WRITTEN` — still a stub (generate it first).

---

## 4. The correction loop (the calibration)
For each `[NEEDS CORRECTION]`:
1. Open the offending `impl_llama3.py` / `impl_mistral.py`.
2. Fix that metric (usually a filter name, a count, or the verdict ordering) so it matches
   the reference logic in `spec.md`.
3. Re-run `python compare\diff_report.py --feature <feature>`.
4. Repeat until every row reads `✅ agree`.

Keep a note of each fix — those notes ARE the calibration data (where offline 3GPP reasoning
went wrong), and they make great material for the write-up.

---

## 5. Golden + CI
When all three agree, `diff_report.py` freezes the Claude result as `golden/<feature>_claude.json`.
That golden is then the offline oracle — no internet needed to re-verify.

Note on `suci`: the correct verdict for the current capture is **FAIL** (null-scheme SUCI). So
"all three agree" here means all three return FAIL, and the golden is a FAIL. That is correct —
the golden captures the true result for this evidence, not a forced PASS. To get a PASS golden,
provision a real ECIES key in OAI, re-capture, and re-run.

Finally, `pytest` (+ the GitHub Actions CI in `.github/workflows/ci.yml`) runs the human-owned
tests on every push, so a regression can't slip back in.

---

## Quick reference
```powershell
# generate (per feature/model), paste into impl_<model>.py, then:
python compare\diff_report.py --all      # see all disagreements
pytest -v                                # run the human-owned oracle
```
