# Push to GitHub — step by step (PowerShell)

Everything below is run from the repo root:
```powershell
cd "C:\Users\sures\OneDrive\Desktop\Setup Instructions\5g-conformance-pipeline"
```

> The `.gitignore` already keeps raw captures (`*.pcap`), AI drafts (`*.generated.py`, `*.raw.txt`),
> caches, and lab internals out of git. The multi-GB RAG (`3GPP_Spec_Test`), the OAI lab, and raw
> `evidence/` captures live in **separate folders** and are **not** part of this push.

---

## 0. One-time setup
```powershell
winget install Git.Git          # if git isn't installed (reopen PowerShell after)
git --version
git config --global user.name  "Suresh Ramadolla"
git config --global user.email "you@example.com"
```

## 1. Initialise the repo + first commit
```powershell
git init
git add .
git status                       # SNAP: shows what will be committed (pcaps/drafts excluded)
git commit -m "5G 3GPP conformance pipeline: 3-model verifiers, RAG calibration, docs"
```

## 2. Create the GitHub repo
**Option A — website:** go to github.com → New repository → name `3gpp-conformance-pipeline` →
choose **Private** (recommended, since it references your labs) or Public → **Create** (do NOT add a
README/License there, you already have them).

**Option B — GitHub CLI (if installed):**
```powershell
winget install GitHub.cli
gh auth login
gh repo create 3gpp-conformance-pipeline --private --source=. --remote=origin --push
```
(Option B does steps 3–4 for you.)

## 3. Connect the remote (skip if you used `gh`)
```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/3gpp-conformance-pipeline.git
```

## 4. Push
```powershell
git push -u origin main
```
Enter your GitHub credentials / token if prompted. Done — refresh the repo page.

## 5. Later changes
```powershell
git add .
git commit -m "describe the change"
git push
```

---

## Screenshots for the GitHub post

The full curated list (results, code, flowcharts) is in **[SCREENSHOTS.md](SCREENSHOTS.md)**. The
essential ones to run and snap (Win + Shift + S) before/after pushing:

```powershell
# short prompt for clean shots
function prompt { "PS> " }

cls; python compare\diff_report.py --all          # SNAP: all three models agree
cls; python compare\diff_report.py --feature suci # SNAP: the IMSI-leak FAIL
cls; python -m pytest -q                          # SNAP: tests green
cls; tree /F pipeline\features\suci               # SNAP: the 3-model file layout
cls; git log --oneline                            # SNAP: your commit (optional)
```

On the GitHub repo page itself, good snaps are: the rendered **README** (the Mermaid flowchart shows
automatically), the file tree, and `docs/` opened.

---

## Recommended GitHub repo settings
- **Description:** "Offline 3GPP 5G/NTN conformance pipeline — spec → 3 graders → golden. Logs from OpenAirInterface / UERANSIM / Open5GS."
- **Topics:** `5g` `3gpp` `ntn` `conformance-testing` `openairinterface` `ueransim` `open5gs` `rag` `ollama` `python`
- **Visibility:** Private if it references internal lab configs; Public if you want it on your profile.
- Pin it on your GitHub profile.
