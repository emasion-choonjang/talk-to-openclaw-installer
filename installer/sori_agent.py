#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import subprocess
import sys
from typing import Tuple

LABEL = "ai.sori.bridge"
PLIST_NAME = f"{LABEL}.plist"


def run(cmd: list[str]) -> Tuple[int, str, str]:
    cp = subprocess.run(cmd, capture_output=True, text=True)
    return cp.returncode, cp.stdout.strip(), cp.stderr.strip()


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def default_python() -> str:
    return sys.executable


def plist_path() -> pathlib.Path:
    return pathlib.Path.home() / "Library" / "LaunchAgents" / PLIST_NAME


def write_plist(py_bin: str, bridge_script: str, port: int, public_host: str, tts_engine: str) -> pathlib.Path:
    p = plist_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    out_log = "/tmp/sori_bridge.out.log"
    err_log = "/tmp/sori_bridge.err.log"
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
    <key>WorkingDirectory</key><string>{repo_root()}</string>
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
    bridge_script = str(repo_root() / "scripts" / "dev" / "run_mock_openclaw_server.py")
    py_bin = args.python or default_python()
    plist = write_plist(py_bin, bridge_script, args.bridge_port, args.public_host, args.tts_engine)
    boot = bootstrap(plist)
    if not boot.get("ok"):
        print(json.dumps({"ok": False, "step": "bootstrap", "error": boot.get("error")}, ensure_ascii=False))
        return 1
    kick = start_service()
    if not kick.get("ok"):
        print(json.dumps({"ok": False, "step": "kickstart", "error": kick.get("error")}, ensure_ascii=False))
        return 1
    payload = {"ok": True, "label": LABEL, "plist": str(plist), "bridge_port": args.bridge_port, "pairing_code": args.pairing_code}
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
    pi.add_argument("--python", default="")

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
