#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <url> <output-path> [width height timeout]" >&2
  echo "- output-path ending with .png/.jpg => screenshot" >&2
  echo "- output-path ending with .pdf => print to PDF" >&2
  exit 1
fi

URL="$1"
OUTPUT="$2"
WIDTH="${3:-1280}"
HEIGHT="${4:-720}"
TIMEOUT="${5:-30}"

BROWSER_CMD=""
if command -v chromium-browser &>/dev/null; then
  BROWSER_CMD="$(command -v chromium-browser)"
elif command -v chromium &>/dev/null; then
  BROWSER_CMD="$(command -v chromium)"
elif [[ -x /snap/bin/chromium ]]; then
  BROWSER_CMD="/snap/bin/chromium"
else
  echo "Chromium executable not found (expected chromium-browser or chromium)" >&2
  exit 2
fi

COMMON_ARGS=(
  --headless=new
  --disable-gpu
  --no-sandbox
  --disable-dev-shm-usage
  --window-size="${WIDTH},${HEIGHT}"
  --hide-scrollbars
)

if [[ "${OUTPUT}" == *.pdf ]]; then
  COMMON_ARGS+=("--print-to-pdf=${OUTPUT}")
else
  COMMON_ARGS+=("--screenshot=${OUTPUT}")
fi

/usr/bin/timeout "${TIMEOUT}"s "${BROWSER_CMD}" "${COMMON_ARGS[@]}" "${URL}"
