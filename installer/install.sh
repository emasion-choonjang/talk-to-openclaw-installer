#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-1.0.18}"
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

detect_openclaw_bin() {
  if command -v openclaw >/dev/null 2>&1; then
    command -v openclaw
    return
  fi
  local candidate
  for candidate in \
    "/opt/homebrew/bin/openclaw" \
    "/usr/local/bin/openclaw" \
    "$HOME/bin/openclaw"; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done
  while IFS= read -r candidate; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done < <(find "$HOME/.nvm/versions/node" -type f -path '*/bin/openclaw' 2>/dev/null | sort -r)
  echo "openclaw"
}

detect_node_bin() {
  local openclaw_bin="${1:-}"
  if command -v node >/dev/null 2>&1; then
    command -v node
    return
  fi
  local candidate
  if [[ -n "$openclaw_bin" && "$openclaw_bin" != "openclaw" ]]; then
    candidate="$(dirname "$openclaw_bin")/node"
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  fi
  for candidate in \
    "/opt/homebrew/bin/node" \
    "/usr/local/bin/node" \
    "$HOME/bin/node"; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done
  while IFS= read -r candidate; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done < <(find "$HOME/.nvm/versions/node" -type f -path '*/bin/node' 2>/dev/null | sort -r)
  echo "node"
}

append_path_segment() {
  local dir="${1:-}"
  [[ -n "$dir" ]] || return 0
  case ":${LAUNCH_PATH}:" in
    *":${dir}:"*) ;;
    *) LAUNCH_PATH="${LAUNCH_PATH:+${LAUNCH_PATH}:}${dir}" ;;
  esac
}

build_launch_path() {
  local openclaw_bin="${1:-}"
  local node_bin="${2:-}"
  LAUNCH_PATH=""
  append_path_segment "$(dirname "$openclaw_bin")"
  append_path_segment "$(dirname "$node_bin")"
  append_path_segment "/opt/homebrew/bin"
  append_path_segment "/usr/local/bin"
  append_path_segment "/usr/bin"
  append_path_segment "/bin"
  append_path_segment "/usr/sbin"
  append_path_segment "/sbin"
  echo "$LAUNCH_PATH"
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
  local openclaw_bin node_bin launch_path
  openclaw_bin="$(detect_openclaw_bin)"
  node_bin="$(detect_node_bin "$openclaw_bin")"
  launch_path="$(build_launch_path "$openclaw_bin" "$node_bin")"

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
      <key>OPENCLAW_BIN</key><string>${openclaw_bin}</string>
      <key>PATH</key><string>${launch_path}</string>
    </dict>
  </dict>
</plist>
PLIST
}

restart_launch_agent() {
  local uid_num bootstrap_log print_log enable_log bootstrap_output
  uid_num="$(id -u)"
  bootstrap_log="$TMP_DIR/bootstrap.log"
  print_log="$TMP_DIR/launchctl-print.log"
  enable_log="$TMP_DIR/launchctl-enable.log"

  launchctl bootout "gui/${uid_num}" ai.sori.bridge >/dev/null 2>&1 || true
  launchctl bootout "gui/${uid_num}/ai.sori.bridge" >/dev/null 2>&1 || true
  launchctl enable "gui/${uid_num}/ai.sori.bridge" >"$enable_log" 2>&1 || true

  if ! launchctl bootstrap "gui/${uid_num}" "$PLIST_PATH" >"$bootstrap_log" 2>&1; then
    if launchctl print "gui/${uid_num}/ai.sori.bridge" >"$print_log" 2>&1 && grep -q "state = running" "$print_log"; then
      log "launchctl bootstrap reported transient failure but service is running"
    else
      bootstrap_output="$(cat "$bootstrap_log" 2>/dev/null || true)"
      if printf '%s' "$bootstrap_output" | grep -qi 'try re-running the command as root'; then
        echo "[installer] ERROR: launchctl bootstrap failed in user domain (root not required). GUI user session/disabled service/state issue." >&2
      fi
      printf '%s
' "$bootstrap_output" >&2
      return 1
    fi
  fi

  if ! launchctl kickstart -k "gui/${uid_num}/ai.sori.bridge" >>"$bootstrap_log" 2>&1; then
    cat "$bootstrap_log" >&2
    return 1
  fi
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
  restart_launch_agent

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
