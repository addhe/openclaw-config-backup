---
name: chrome-headless
description: Run Chromium/Chrome in headless mode for screenshots, PDF prints, or scripted browsing on this Ubuntu CLI host. Use when a task needs a real browser engine (Chromium) without GUI, such as capturing pages, testing rendering, or feeding artifacts into other workflows.
---

# Chrome Headless Skill

## Overview
Use this skill whenever you need a real Chromium browser on this headless Ubuntu VM. It describes how to launch the installed `chromium-browser` snap in headless mode, capture screenshots/PDFs, and troubleshoot typical issues (sandboxing, missing dependencies, etc.). Pair it with OpenClaw's built-in `browser` tool when a remote-controlled browser session is required; fall back to the CLI workflow below for purely local/batch rendering.

## Quick Start
1. Ensure Chromium is available (already installed via snap):
   ```bash
   chromium-browser --version
   ```
2. Use the helper script to fetch a page and save an artifact:
   ```bash
   skills/chrome-headless/scripts/run_headless_chromium.sh \
     "https://example.com" artifacts/example.png 1280 720 30
   ```
   - Output extension `.png/.jpg` ⇒ screenshot.
   - Output extension `.pdf` ⇒ printed PDF.
   - Optional width/height/timeouts default to 1280×720 and 30 s.
3. Consume the artifact (attach, analyze, or archive) per the main task.

## Workflow Details
### 1. Decide which pathway to use
- **Need interactive browsing or automated DOM actions** → prefer OpenClaw `browser` tool (already available). It spawns a managed Chrome instance with DOM access.
- **Need quick render/export only** → run the headless script locally; it is deterministic and requires no remote session.

### 2. Local headless rendering
- Script path: `skills/chrome-headless/scripts/run_headless_chromium.sh`
- Flags already set: `--headless=new --disable-gpu --no-sandbox --disable-dev-shm-usage --hide-scrollbars`.
- For long pages printed to PDF, pass a `.pdf` output path; Chromium auto-selects page size.
- For SPA pages that need time to settle, consider wrapping the script call in `sleep`/`wait` logic or extend the timeout argument.

### 3. Post-processing
- Screenshots land exactly where you point the script; move them into `/tmp` or the workspace as needed.
- When sharing to chat, ensure file paths are accessible (copy into workspace first).

## Troubleshooting
| Symptom | Fix |
| --- | --- |
| `chromium-browser: command not found` | Re-run `sudo snap install chromium` or ensure `/snap/bin` is in PATH. |
| Timeout triggered | Increase the last argument (>30 s) or verify the target URL is reachable from this VM. |
| Blank screenshots | Add a short `sleep` before capturing (wrap script) or load a specific route with query params that force data to appear server-side. |
| Needs custom headers/auth | Use `chromium-browser` directly with `--user-data-dir` pointing to a temp profile where you log in once (document any credentials separately). |

## Resources
- `scripts/run_headless_chromium.sh` – wrapper for Chromium headless screenshots/PDF export.

## Verification checklist
- Chromium installed via snap (`chromium-browser --version`).
- Script is executable (`chmod +x` already applied).
- `browser` tool confirmed available for OpenClaw sessions.
