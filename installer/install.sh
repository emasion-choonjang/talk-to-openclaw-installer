#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP_URL_DEFAULT="https://github.com/emasion-choonjang/talk-to-openclaw-installer/releases/download/v1.0.4/sori_agent.py"
BOOTSTRAP_URL="${INSTALLER_BOOTSTRAP_URL:-$BOOTSTRAP_URL_DEFAULT}"
PAIRING_CODE="${PAIRING_CODE:-}"
BRIDGE_PORT="${BRIDGE_PORT:-18890}"
PUBLIC_HOST="${PUBLIC_HOST:-127.0.0.1}"
TTS_ENGINE="${TTS_ENGINE:-edge}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
EXPECTED_SHA256="${EXPECTED_SHA256:-}"

if [[ -z "$PAIRING_CODE" ]]; then
  echo "[installer] ERROR: PAIRING_CODE is required"
  echo "Usage example: PAIRING_CODE=ABC123 PUBLIC_HOST=192.168.0.10 bash installer/install.sh"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
AGENT_PATH="$TMP_DIR/sori_agent.py"

echo "[installer] downloading agent from: $BOOTSTRAP_URL"
curl -fsSL "$BOOTSTRAP_URL" -o "$AGENT_PATH"

if [[ -n "$EXPECTED_SHA256" ]]; then
  ACTUAL_SHA256="$(shasum -a 256 "$AGENT_PATH" | awk '{print $1}')"
  if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
    echo "[installer] ERROR: sha256 mismatch"
    echo "expected: $EXPECTED_SHA256"
    echo "actual:   $ACTUAL_SHA256"
    exit 1
  fi
fi

echo "[installer] installing launchd service"
"$PYTHON_BIN" "$AGENT_PATH" install \
  --pairing-code "$PAIRING_CODE" \
  --bridge-port "$BRIDGE_PORT" \
  --public-host "$PUBLIC_HOST" \
  --tts-engine "$TTS_ENGINE"

echo "[installer] done"
