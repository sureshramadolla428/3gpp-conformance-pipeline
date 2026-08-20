# Interview prep — 5G 3GPP Conformance Pipeline

Confident **and** honest. A good interviewer will probe; the honest answers below *are* the strong
answers. Never claim the offline models converged on their own, never claim NTN hardware, never
claim the SUCI FAIL is a UE bug.

---

## 1. The 45-second pitch
> "I built an automated 3GPP conformance pipeline for a 5G/NTN OpenAirInterface lab. It takes a spec
> requirement — SUCI privacy, 5G-AKA, registration, PDU session, multi-PLMN SIB1 — turns it into a
> machine-checkable contract, and a Python + tshark verifier reads a real capture and returns
> PASS/FAIL with the evidence and the governing TS clause. Two things make it more than a demo: it
> caught a real privacy defect — a null-scheme SUCI leaking the IMSI in cleartext, which a naive
> check passes — and I recompute the Milenage crypto offline to *prove* authentication instead of
> trusting a log line. Then I added an offline-AI layer: a local RAG over 3GPP specs drafts the same
> verifiers, and a diff harness calibrates them against a spec-correct reference until all three
> agree — which surfaced exactly how and where open-source models fail on protocol code."

## 2. Four differentiator stories
1. **SUCI null-scheme leak** — counts said "SUCI present" (naive pass), but scheme id 0 = IMSI in
   cleartext → FAIL. Class of bug that slips past surface checks. (security depth)
2. **AKA verified, not assumed** — recomputed RES* via Milenage + Annex A.4/A.5 KDF and matched the
   network HXRES* bit-for-bit; reconciled OAI's SHA-256 truncation. (crypto rigor)
3. **Three-model calibration** — Claude reference vs two offline RAG models; diff flags every metric
   deviation; agreement freezes golden. (systems + AI evaluation)
4. **Diff caught what verdicts hid** — after verdicts already matched, the diff flagged the offline
   impls emitting fewer diagnostic fields — a metric-level divergence a verdict-only check misses.

---

## 3. Question bank

### About the project & value
**Q. Give me the one-line version.**
A. "A spec-to-evidence regression guard: it checks a real 5G capture against the 3GPP rulebook and
proves PASS/FAIL — and it caught a real IMSI-privacy leak that a naive check calls conformant."

**Q. Why does this matter to an operator/vendor?**
A. "Config changes silently break conformance and you find out in a field trial. This turns a spec
clause into a CI check, so a regression shows up on the next capture, not months later. My own
Gate-2 example — a CU/DU PLMN-order mismatch breaking authentication — is exactly that class."

**Q. Isn't this just OAI setup?**
A. "Bringing up OAI is table stakes. The work is the verification layer: specs → deterministic
checks, offline crypto recompute, and the AI-calibration harness. The lab is just the capture
source; the verifiers are vendor-neutral because tshark dissects any capture."

**Q. How is this different from Keysight / R&S / commercial conformance test systems?**
A. "Those are certified RF+protocol conformance suites on real test equipment. Mine is a lightweight,
scriptable, CI-friendly regression guard for a software lab — and it doubles as an honest evaluation
of whether offline LLMs can author protocol checks. Complementary, not a replacement."

### The AI / calibration (they will dig here)
**Q. Did the AI actually work, or did you fix it?**
A. "I fixed it — and that's the finding. The raw offline drafts were confidently wrong: llama3
hallucinated a `tshark -z crypto` command instead of Milenage; mistral left stub functions and even
a syntax error. I corrected them to the reference. The whole point is you can't trust raw offline
output — the human-authored spec + reference + diff are what make it trustworthy."

**Q. So 'three models agree' is misleading?**
A. "I'm precise about it: they agree because I calibrated the offline impls to a correct reference,
not because they autonomously produced correct code. It's human-in-the-loop calibration. Claiming
autonomous convergence would be dishonest — and a next step is a feedback loop to actually measure
the models improving."

**Q. Then what's the point of the offline models at all?**
A. "Two things. One, they draft ~70% of the structure correctly, which is a real accelerator. Two —
and this is the deliverable — the calibration log is a concrete, reproducible map of *where*
spec-grounded local models fail on 3GPP code. That's useful evidence for anyone deploying offline AI
in a no-cloud telecom environment."

**Q. Why three models instead of one reference?**
A. "Cross-check. If two offline models agree with each other but disagree with the reference, it's a
systematic offline gap; if they disagree with each other, one's just wrong. Diversity makes a single
model's quirk less likely to pass silently."

**Q. Why RAG instead of just prompting the model?**
A. "Grounding. The RAG retrieves the actual TS clauses so the draft is anchored to the spec, not the
model's priors. It still hallucinated the crypto — which tells you retrieval helps with *what* to
check but not with *how* to implement the hard parts."

### Technical depth (protocol/security)
**Q. Walk me through the SUCI check.**
A. "TS 33.501 §6.12: the UE must conceal the SUPI. The 5GS mobile identity must be SUCI-type, and
crucially the protection scheme must not be null. My verifier counts SUCI frames and null-scheme
frames; scheme 0 means the IMSI rides in cleartext inside the SUCI, so it's FAIL even though the
identity 'is a SUCI'. On this capture null_scheme_frames was 2 — a real leak."

**Q. How do you verify 5G-AKA without the UE's secret runtime state?**
A. "I recompute it. With K and OPc from the subscriber config and the RAND from the exchange, I run
Milenage f2 to get RES, then the Annex A.4 KDF (FC 0x6B over SNN, RAND, RES) to get RES*, then the
Annex A.5 SHA-256 to get HRES*, and compare to the network's HXRES* in the AMF log. It matched
exactly — 98ffc4… → 671faf…."

**Q. What's the Serving Network Name got to do with it?**
A. "The SNN (`5G:mnc…mcc….3gppnetwork.org`) is an input to the RES* KDF. If the UE derives it from
the wrong PLMN — e.g. a CU/DU SIB1 order mismatch — RES* ≠ XRES* and auth fails. That's the Gate-2
root cause, and my SIB1 verifier guards against exactly that ordering divergence."

**Q. INCONCLUSIVE vs FAIL — why two failure-ish states?**
A. "Separating 'unusable capture' from 'real violation'. If NAS frames are missing, the capture
started too late — that's INCONCLUSIVE, not FAIL. Reporting FAIL there would be a false positive.
It's a small thing that matters a lot for trust."

**Q. How do you handle Wireshark version differences?**
A. "Field names differ (hyphen vs underscore across 3.x/4.x). The helpers try both variants, and
anything I couldn't confirm on-box is flagged in code. I confirmed the real filters against the
actual captures rather than trusting field names from memory."

**Q. What are the limits — where does this NOT work?**
A. "NTN here is software-only, OAI RFsimulator, not radio hardware, so no RF conformance. True
inter-satellite handover doesn't complete in RFsim — I documented that as a known limit rather than
faking it. And voice/VoNR isn't covered. I'm explicit about all three."

### Engineering / scale
**Q. How would you add a new test case?**
A. "New feature folder, write spec.md (MUST/MUST NOT + metric keys + verdict logic), an impl_claude
reference + a pytest, register it in diff_report's FEATURES map, capture evidence, run. The design is
one folder per feature so it scales linearly."

**Q. Could this run fully offline / air-gapped for a security-sensitive operator?**
A. "Yes. The verifiers use no AI and no internet — pure Python + tshark + Milenage. The AI is only in
the authoring layer and runs on local Ollama. In a strict shop you'd make a human or a local model
the reference instead of Claude; the pattern is identical."

**Q. How do you keep it from regressing?**
A. "Golden files freeze the agreed result, a human-owned pytest oracle asserts the criteria
independently of the verifiers, and CI runs it on every change. A config that breaks conformance
fails the build."

**Q. What would you improve with more time?**
A. "Move the crypto and a tshark field-whitelist into shared libraries and add an auto-repair loop
(compile → run → diff → re-prompt) so the offline models can't hallucinate the hard parts; and a
feedback loop that feeds corrections back so the offline system needs less correction over time —
that would let me honestly claim the AI *improves*."

### Behavioural
**Q. What was the hardest part?**
A. "Two things: matching OAI's exact HXRES* truncation for the AKA crypto, and realizing the offline
models fake the hard parts — which is what drove me to build the calibration harness instead of
trusting the drafts."

**Q. What did you personally do vs the AI?**
A. "I designed the architecture, wrote the specs and the reference verifiers' logic, did the protocol
debugging (the SUCI leak, the AKA/SNN reasoning), and calibrated the offline output. AI assisted with
drafting and boilerplate. I can walk you through any file and explain every check."

**Q. Sell me on one number.**
A. "`null_scheme_frames = 2`. Two frames where the identity decoded as SUCI but carried the IMSI in
the clear — the pipeline caught a real privacy hole that counting alone passes."

---

## 4. Honesty guardrails (say them before they catch you)
- NTN is **software-only** (RFsim), not radio hardware.
- The SUCI **FAIL** is a real **lab-config** defect (null scheme), not a UE bug.
- The offline models **drafted**; a human **calibrated**. Not autonomous convergence.
- I did the debugging + architecture; AI assisted with drafting.

## 5. Tailor per role
- **Conformance / test automation** → lead with spec-to-evidence + CI + the regression-guard framing.
- **Security** → lead with the SUCI leak + the AKA offline recompute.
- **AI / ML / platform** → lead with the RAG generation + calibration harness and the honest
  LLM-failure findings.
- **RAN / protocol** → lead with the SNN/PLMN-order (Gate-2) reasoning and the NTN limits you named.

## 6. 30-second close
> "The through-line is: turn a spec clause into a deterministic, evidenced check; prove the hard parts
> (crypto) instead of trusting logs; and use offline AI carefully — as a drafter that a spec-correct
> reference keeps honest. It caught a real IMSI leak, it runs air-gapped, and it's a CI regression
> guard I could drop into a lab tomorrow."
