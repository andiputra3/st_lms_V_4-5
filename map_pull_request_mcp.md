# MAP PULL REQUEST MCP — ST-LMS v3

**Date:** 2025-07-29
**MCP Server:** `stlms-github` (local MCP, auto-enabled)

---

## PR Workflow

```
User says "buat PR untuk X"
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: stlms_github_status — cek mode, token, repo, internet │
│ STEP 2: stlms_github_on — enable jika belum                    │
│ STEP 3: stlms_github_test — validasi koneksi (PASS wajib)     │
│ STEP 4: stlms_github_pr {phase} — stage→commit→push→PR→STOP  │
│ STEP 5: Return PR URL to user                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Branch Naming Convention

| User Says | Phase Argument | Branch | PR Title |
|-----------|---------------|--------|----------|
| "buat PR untuk phase-01" | `phase-01` | `build/phase-01` | `[ST-LMS] phase-01` |
| "buat PR truth layer" | `truth-layer` | `build/truth-layer` | `[ST-LMS] truth-layer` |
| "buat PR sqlite viewer" | `sqlite-viewer` | `build/sqlite-viewer` | `[ST-LMS] sqlite-viewer` |
| "buat PR dashboard" | `dashboard` | `build/dashboard` | `[ST-LMS] dashboard` |
| "buat PR readme" | `readme` | `build/readme` | `[ST-LMS] readme` |

---

## Current State (2025-07-29)

| Item | Value |
|------|-------|
| Repository | `andiputra3/st_lms_V_4-5` |
| Default Branch | `main` |
| GitHub Mode | `PR` |
| Token | Classic (`ghp_...`) — `repo` scope |
| .gitignore | Excludes `.stlms_github.conf` and `.stlms_github/` |
| Existing PRs | PR #1 (readme — merged) |

---

## MCP Tools Quick Reference

| Tool | When to Use | Returns |
|------|------------|---------|
| `stlms_github_status` | Before any PR — cek readiness | Mode, repo, token, internet, PR capable |
| `stlms_github_on` | If status shows OFF | Enables PR mode |
| `stlms_github_off` | User wants to disable | Disables GitHub |
| `stlms_github_test` | After setup or token change | 5 PASS/FAIL checks |
| `stlms_github_pr` | User says "buat PR" | PR URL or error |
| `stlms_github_setup` | First time or token change | Saves config |
| `stlms_github_token_status` | Check token validity | Masked token + status |
| `stlms_github_reset` | User wants clean slate | Resets all config |

---

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| `GitHub is OFF` | Mode OFF | `stlms_github_on` |
| `Token not set` | No token | `stlms_github_setup` |
| `Repository not found` | Wrong repo name | `stlms_github_setup` |
| `Push failed` | Token lacks `repo` scope | Regenerate classic token with `repo` |
| `No commits between` | No new commits vs main | Auto-handled: commit dibuat di build branch |
| `HTTP 000` | Config has `\r` | Auto-cleaned by `load_conf()` |

---

## What Gets Committed

- **INCLUDED**: All project files (`.md`, `.html`, `.sql`, `.js`, `.json`)
- **EXCLUDED**: `.stlms_github.conf`, `.stlms_github/` (via `.gitignore`)
- **EXCLUDED**: `.git/` (git internal)

---

## PR Template (Auto-generated)

```
Title: [ST-LMS] {phase}

Description:
  Phase: {phase}
  Branch: build/{phase} → main

Files Added: (auto-detected from git diff)
Files Updated: (auto-detected from git diff)

References: MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, STLMS_SQLITE_SCHEMA_V1.sql
Implementation Scope: {phase} components and contracts
Conflict Status: NONE
Ready For Review: YES
```

---

## After PR Creation

1. PR URL ditampilkan
2. Proses **STOP** — tidak ada auto-merge
3. User merge manual di GitHub
4. Setelah merge, user bisa minta PR berikutnya
