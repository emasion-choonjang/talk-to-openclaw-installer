#!/usr/bin/env python3
import argparse
import json
import glob
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Tuple

LABEL = "ai.sori.bridge"
PLIST_NAME = f"{LABEL}.plist"
DEFAULT_VENV_DIR = pathlib.Path.home() / ".local" / "share" / "sori-bridge" / "venv"
DEFAULT_REQUIREMENTS = pathlib.Path(__file__).resolve().with_name("bridge_requirements.txt")
BUILTIN_REQUIREMENTS = [
    "edge-tts>=6.1.12",
    "faster-whisper>=1.0.3",
]


def run(cmd: list[str]) -> Tuple[int, str, str]:
    cp = subprocess.run(cmd, capture_output=True, text=True)
    return cp.returncode, cp.stdout.strip(), cp.stderr.strip()


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def default_python() -> str:
    return sys.executable


def plist_path() -> pathlib.Path:
    return pathlib.Path.home() / "Library" / "LaunchAgents" / PLIST_NAME


def venv_python_path(venv_dir: pathlib.Path) -> pathlib.Path:
    return venv_dir / "bin" / "python"


def ensure_venv_python(base_python: str, venv_dir: pathlib.Path) -> Tuple[bool, str]:
    py = venv_python_path(venv_dir)
    if py.exists():
        return True, str(py)

    venv_dir.parent.mkdir(parents=True, exist_ok=True)
    code, out, err = run([base_python, "-m", "venv", str(venv_dir)])
    if code != 0:
        return False, err or out or "venv_create_failed"
    if not py.exists():
        return False, "venv_python_not_found"
    return True, str(py)


def install_bridge_dependencies(venv_python: str, requirements_path: pathlib.Path) -> Tuple[bool, str]:
    code, out, err = run([venv_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    if code != 0:
        return False, f"pip_bootstrap_failed: {err or out}"

    if requirements_path.exists():
        install_cmd = [venv_python, "-m", "pip", "install", "-r", str(requirements_path)]
    else:
        install_cmd = [venv_python, "-m", "pip", "install", *BUILTIN_REQUIREMENTS]
    code, out, err = run(install_cmd)
    if code != 0:
        return False, f"pip_install_failed: {err or out}"
    return True, "ok"


def verify_bridge_runtime(venv_python: str) -> Tuple[bool, str]:
    code, out, err = run([venv_python, "-m", "edge_tts", "--help"])
    if code != 0:
        return False, f"edge_tts_missing: {err or out}"
    code, out, err = run([venv_python, "-c", "import faster_whisper; print('ok')"])
    if code != 0:
        return False, f"faster_whisper_missing: {err or out}"
    return True, "ok"


def detect_openclaw_bin() -> str:
    found = shutil.which("openclaw")
    if found:
        return found
    candidates = [
        "/opt/homebrew/bin/openclaw",
        "/usr/local/bin/openclaw",
        os.path.expanduser("~/bin/openclaw"),
    ]
    candidates.extend(
        sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/openclaw")), reverse=True)
    )
    for path in candidates:
        if os.path.isfile(path):
            return path
    return "openclaw"


def write_plist(
    py_bin: str,
    bridge_script: str,
    work_dir: str,
    port: int,
    public_host: str,
    tts_engine: str,
    installer_bootstrap_url: str,
) -> pathlib.Path:
    p = plist_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    out_log = "/tmp/sori_bridge.out.log"
    err_log = "/tmp/sori_bridge.err.log"
    installer_env = (
        f"\n      <key>INSTALLER_BOOTSTRAP_URL</key><string>{installer_bootstrap_url}</string>"
        if installer_bootstrap_url
        else ""
    )
    default_path = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    py_dir = str(pathlib.Path(py_bin).resolve().parent)
    merged_path = f"{py_dir}:{default_path}"
    openclaw_bin = detect_openclaw_bin()
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key><string>{LABEL}</string>
    <key>ProgramArguments</key>
    <array>
      <string>{py_bin}</string>
      <string>{bridge_script}</string>
    </array>
    <key>WorkingDirectory</key><string>{work_dir}</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>{out_log}</string>
    <key>StandardErrorPath</key><string>{err_log}</string>
    <key>EnvironmentVariables</key>
    <dict>
      <key>OPENCLAW_HOST</key><string>0.0.0.0</string>
      <key>OPENCLAW_PORT</key><string>{port}</string>
      <key>OPENCLAW_PUBLIC_HOST</key><string>{public_host}</string>
      <key>TTS_ENGINE</key><string>{tts_engine}</string>
      <key>OPENCLAW_DIALOG_TIMEOUT_SEC</key><string>12</string>
      <key>ASR_TURN_WAIT_SEC</key><string>18</string>
      <key>PATH</key><string>{merged_path}</string>
      <key>OPENCLAW_BIN</key><string>{openclaw_bin}</string>
{installer_env}
    </dict>
  </dict>
</plist>
'''
    p.write_text(content, encoding="utf-8")
    return p


def bootstrap(plist: pathlib.Path) -> dict:
    uid = str(os.getuid())
    run(["launchctl", "bootout", f"gui/{uid}", LABEL])
    code, out, err = run(["launchctl", "bootstrap", f"gui/{uid}", str(plist)])
    if code != 0:
        return {"ok": False, "error": err or out}
    return {"ok": True}


def start_service() -> dict:
    uid = str(os.getuid())
    code, out, err = run(["launchctl", "kickstart", "-k", f"gui/{uid}/{LABEL}"])
    return {"ok": code == 0, "error": err or out if code != 0 else None}


def stop_service() -> dict:
    uid = str(os.getuid())
    code, out, err = run(["launchctl", "bootout", f"gui/{uid}", LABEL])
    return {"ok": code == 0, "error": err or out if code != 0 else None}


def status() -> dict:
    uid = str(os.getuid())
    p = plist_path()
    code, out, err = run(["launchctl", "print", f"gui/{uid}/{LABEL}"])
    running = code == 0 and "state = running" in out
    pid = None
    if running:
        for line in out.splitlines():
            s = line.strip()
            if s.startswith("pid ="):
                try:
                    pid = int(s.split("=", 1)[1].strip())
                except Exception:
                    pid = None
                break
    return {
        "ok": True,
        "installed": p.exists(),
        "running": running,
        "pid": pid,
        "label": LABEL,
        "plist": str(p),
        "print_error": None if code == 0 else (err or out),
    }


def uninstall() -> dict:
    _ = stop_service()
    p = plist_path()
    try:
        if p.exists():
            p.unlink()
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def cmd_install(args: argparse.Namespace) -> int:
    root = repo_root()
    bridge_script = str(root / "scripts" / "dev" / "run_mock_openclaw_server.py")
    if not pathlib.Path(bridge_script).exists():
        print(json.dumps({"ok": False, "step": "precheck", "error": "bridge_script_not_found"}, ensure_ascii=False))
        return 1

    base_python = args.python or default_python()
    venv_dir = pathlib.Path(args.venv_dir).expanduser()
    ok, payload = ensure_venv_python(base_python, venv_dir)
    if not ok:
        print(json.dumps({"ok": False, "step": "venv", "error": payload}, ensure_ascii=False))
        return 1
    py_bin = payload

    if not args.skip_deps:
        req_path = pathlib.Path(args.requirements).expanduser()
        ok, payload = install_bridge_dependencies(py_bin, req_path)
        if not ok:
            print(json.dumps({"ok": False, "step": "deps_install", "error": payload}, ensure_ascii=False))
            return 1
        ok, payload = verify_bridge_runtime(py_bin)
        if not ok:
            print(json.dumps({"ok": False, "step": "deps_verify", "error": payload}, ensure_ascii=False))
            return 1

    plist = write_plist(
        py_bin,
        bridge_script,
        str(root),
        args.bridge_port,
        args.public_host,
        args.tts_engine,
        args.installer_bootstrap_url,
    )
    boot = bootstrap(plist)
    if not boot.get("ok"):
        print(json.dumps({"ok": False, "step": "bootstrap", "error": boot.get("error")}, ensure_ascii=False))
        return 1
    kick = start_service()
    if not kick.get("ok"):
        print(json.dumps({"ok": False, "step": "kickstart", "error": kick.get("error")}, ensure_ascii=False))
        return 1
    payload = {
        "ok": True,
        "label": LABEL,
        "plist": str(plist),
        "bridge_port": args.bridge_port,
        "pairing_code": args.pairing_code,
        "installer_bootstrap_url": args.installer_bootstrap_url,
        "venv_python": py_bin,
        "requirements": str(pathlib.Path(args.requirements).expanduser()),
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SORI mac agent installer")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("install")
    pi.add_argument("--pairing-code", default="")
    pi.add_argument("--bridge-port", type=int, default=18890)
    pi.add_argument("--public-host", default="127.0.0.1")
    pi.add_argument("--tts-engine", default="edge")
    pi.add_argument("--installer-bootstrap-url", default="")
    pi.add_argument("--python", default="")
    pi.add_argument("--venv-dir", default=str(DEFAULT_VENV_DIR))
    pi.add_argument("--requirements", default=str(DEFAULT_REQUIREMENTS))
    pi.add_argument("--skip-deps", action="store_true")

    sub.add_parser("status")
    sub.add_parser("start")
    sub.add_parser("stop")
    sub.add_parser("uninstall")
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == "install":
        return cmd_install(args)
    if args.cmd == "status":
        print(json.dumps(status(), ensure_ascii=False))
        return 0
    if args.cmd == "start":
        print(json.dumps(start_service(), ensure_ascii=False))
        return 0
    if args.cmd == "stop":
        print(json.dumps(stop_service(), ensure_ascii=False))
        return 0
    if args.cmd == "uninstall":
        print(json.dumps(uninstall(), ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
