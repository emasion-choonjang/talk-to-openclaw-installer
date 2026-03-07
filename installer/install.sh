#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-1.0.12}"
PAIRING_CODE="${PAIRING_CODE:-}"
BRIDGE_PORT="${BRIDGE_PORT:-18890}"
PUBLIC_HOST="${PUBLIC_HOST:-127.0.0.1}"
TTS_ENGINE="${TTS_ENGINE:-edge}"
OPENCLAW_AGENT="${OPENCLAW_AGENT:-sori-bridge}"
OPENCLAW_THINKING="${OPENCLAW_THINKING:-minimal}"
ASSET_URL="${ASSET_URL:-}"
ASSET_SHA256="${ASSET_SHA256:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LEGACY_BOOTSTRAP_URL="${INSTALLER_BOOTSTRAP_URL:-https://github.com/emasion-choonjang/talk-to-openclaw-installer/releases/download/v${VERSION}/sori_agent.py}"

INSTALL_ROOT="${HOME}/Library/Application Support/SORI/bridge"
RELEASES_DIR="${INSTALL_ROOT}/releases"
RELEASE_DIR="${RELEASES_DIR}/${VERSION}"
CURRENT_LINK="${INSTALL_ROOT}/current"
PLIST_PATH="${HOME}/Library/LaunchAgents/ai.sori.bridge.plist"
LEGACY_ROOT="${HOME}/.local/share/sori-bridge"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

log() {
  echo "[installer] $*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[installer] ERROR: required command not found: $1" >&2
    exit 1
  }
}

prune_old_releases() {
  [[ -d "$RELEASES_DIR" ]] || return 0
  local keep_dir
  keep_dir="$(cd "$RELEASE_DIR" && pwd -P)"
  find "$RELEASES_DIR" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r candidate; do
    [[ -n "$candidate" ]] || continue
    local candidate_dir
    candidate_dir="$(cd "$candidate" && pwd -P)"
    if [[ "$candidate_dir" != "$keep_dir" ]]; then
      rm -rf "$candidate"
    fi
  done
}

remove_legacy_runtime() {
  rm -rf "$LEGACY_ROOT/bridge" "$LEGACY_ROOT/venv"
}

write_plist() {
  mkdir -p "$(dirname "$PLIST_PATH")"
  cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key><string>ai.sori.bridge</string>
    <key>ProgramArguments</key>
    <array>
      <string>${CURRENT_LINK}/sori-bridge</string>
    </array>
    <key>WorkingDirectory</key><string>${CURRENT_LINK}</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>/tmp/sori_bridge.out.log</string>
    <key>StandardErrorPath</key><string>/tmp/sori_bridge.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
      <key>OPENCLAW_HOST</key><string>0.0.0.0</string>
      <key>OPENCLAW_PORT</key><string>${BRIDGE_PORT}</string>
      <key>OPENCLAW_PUBLIC_HOST</key><string>${PUBLIC_HOST}</string>
      <key>TTS_ENGINE</key><string>${TTS_ENGINE}</string>
      <key>OPENCLAW_DEFAULT_AGENT</key><string>${OPENCLAW_AGENT}</string>
      <key>OPENCLAW_THINKING_LEVEL</key><string>${OPENCLAW_THINKING}</string>
    </dict>
  </dict>
</plist>
PLIST
}

install_binary() {
  require_cmd curl
  require_cmd tar
  require_cmd launchctl
  require_cmd shasum

  if [[ -z "$ASSET_URL" || -z "$ASSET_SHA256" ]]; then
    echo "[installer] ERROR: ASSET_URL and ASSET_SHA256 are required for binary install" >&2
    exit 1
  fi

  rm -rf "$RELEASE_DIR"
  mkdir -p "$RELEASE_DIR"
  ARCHIVE_PATH="$TMP_DIR/sori-bridge-macos-arm64.tar.gz"

  log "downloading bridge binary: $ASSET_URL"
  curl -fsSL "$ASSET_URL" -o "$ARCHIVE_PATH"

  ACTUAL_SHA256="$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}')"
  if [[ "$ACTUAL_SHA256" != "$ASSET_SHA256" ]]; then
    echo "[installer] ERROR: asset sha256 mismatch" >&2
    echo "expected: $ASSET_SHA256" >&2
    echo "actual:   $ACTUAL_SHA256" >&2
    exit 1
  fi

  log "extracting bridge binary"
  tar -xzf "$ARCHIVE_PATH" -C "$RELEASE_DIR"
  chmod +x "$RELEASE_DIR/sori-bridge"
  ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

  write_plist

  UID_NUM="$(id -u)"
  launchctl bootout "gui/${UID_NUM}" ai.sori.bridge >/dev/null 2>&1 || true
  launchctl bootstrap "gui/${UID_NUM}" "$PLIST_PATH"
  launchctl kickstart -k "gui/${UID_NUM}/ai.sori.bridge"

  prune_old_releases
  remove_legacy_runtime
  log "binary install done"
}

install_legacy_python() {
  require_cmd curl
  require_cmd "$PYTHON_BIN"

  if [[ -z "$PAIRING_CODE" ]]; then
    echo "[installer] ERROR: PAIRING_CODE is required for legacy install" >&2
    exit 1
  fi

  AGENT_PATH="$TMP_DIR/sori_agent.py"
  log "downloading legacy agent: $LEGACY_BOOTSTRAP_URL"
  curl -fsSL "$LEGACY_BOOTSTRAP_URL" -o "$AGENT_PATH"
  log "installing legacy launchd service"
  "$PYTHON_BIN" "$AGENT_PATH" install \
    --pairing-code "$PAIRING_CODE" \
    --bridge-port "$BRIDGE_PORT" \
    --public-host "$PUBLIC_HOST" \
    --tts-engine "$TTS_ENGINE" \
    --openclaw-agent "$OPENCLAW_AGENT"
}

if [[ -n "$ASSET_URL" ]]; then
  install_binary
else
  install_legacy_python
fi
