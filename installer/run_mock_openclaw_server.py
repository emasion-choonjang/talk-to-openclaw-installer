#!/usr/bin/env python3
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from collections import deque
from io import BytesIO
from array import array
import fcntl
import json
import ipaddress
import importlib.util
import math
import glob
import base64
import hashlib
import hmac
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import wave
import queue
import random
from pathlib import Path

HOST = os.environ.get("OPENCLAW_HOST", "0.0.0.0")
PORT = int(os.environ.get("OPENCLAW_PORT", "8080"))
PUBLIC_HOST = os.environ.get("OPENCLAW_PUBLIC_HOST", "127.0.0.1")
VOICE = os.environ.get("OPENCLAW_TTS_VOICE", "Yuna")
TTS_ENGINE = os.environ.get("TTS_ENGINE", "say").strip().lower()
PIPER_BIN = os.environ.get("PIPER_BIN", os.path.expanduser("~/Library/Python/3.14/bin/piper"))
PIPER_MODEL = os.environ.get("PIPER_MODEL", "")
PIPER_CONFIG = os.environ.get("PIPER_CONFIG", "")
PIPER_SPEAKER = os.environ.get("PIPER_SPEAKER", "").strip()
PIPER_LENGTH_SCALE = os.environ.get("PIPER_LENGTH_SCALE", "").strip()
PIPER_NOISE_SCALE = os.environ.get("PIPER_NOISE_SCALE", "").strip()
PIPER_NOISE_W_SCALE = os.environ.get("PIPER_NOISE_W_SCALE", "").strip()
PIPER_SENTENCE_SILENCE = os.environ.get("PIPER_SENTENCE_SILENCE", "").strip()
PIPER_VOLUME = os.environ.get("PIPER_VOLUME", "").strip()
XTTS_MODEL = os.environ.get("XTTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2").strip()
XTTS_LANGUAGE = os.environ.get("XTTS_LANGUAGE", "ko").strip()
XTTS_SPEAKER_WAV = os.environ.get("XTTS_SPEAKER_WAV", "").strip()
XTTS_DEVICE = os.environ.get("XTTS_DEVICE", "").strip()
XTTS_SPEED = os.environ.get("XTTS_SPEED", "1.0").strip()
XTTS_SPLIT_SENTENCES = os.environ.get("XTTS_SPLIT_SENTENCES", "false").strip().lower()
XTTS_TEMPERATURE = os.environ.get("XTTS_TEMPERATURE", "").strip()
XTTS_TOP_K = os.environ.get("XTTS_TOP_K", "").strip()
XTTS_TOP_P = os.environ.get("XTTS_TOP_P", "").strip()
XTTS_REPETITION_PENALTY = os.environ.get("XTTS_REPETITION_PENALTY", "").strip()
FFMPEG_AUDIO_FILTER = os.environ.get("FFMPEG_AUDIO_FILTER", "afade=t=in:st=0:d=0.02").strip()
SAY_GAIN_DB = os.environ.get("SAY_GAIN_DB", "6").strip()
SAY_TAIL_SILENCE_SEC = os.environ.get("SAY_TAIL_SILENCE_SEC", "0.18").strip()
OPENCLAW_DIALOG_TARGET = os.environ.get("OPENCLAW_DIALOG_TARGET", "").strip()
OPENCLAW_DIALOG_SESSION_ID = os.environ.get("OPENCLAW_DIALOG_SESSION_ID", "").strip()
OPENCLAW_DIALOG_AGENT = os.environ.get("OPENCLAW_DIALOG_AGENT", "").strip()
OPENCLAW_DEFAULT_SESSION_ID = os.environ.get(
    "OPENCLAW_DEFAULT_SESSION_ID",
    f"sori-bridge-{PUBLIC_HOST.replace('.', '-')}",
).strip()
OPENCLAW_DIALOG_TIMEOUT_SEC = int(os.environ.get("OPENCLAW_DIALOG_TIMEOUT_SEC", "20"))
OPENCLAW_DEFAULT_AGENT = os.environ.get("OPENCLAW_DEFAULT_AGENT", "sori-bridge").strip() or "sori-bridge"
OPENCLAW_BOOTSTRAP_MODEL = os.environ.get("OPENCLAW_BOOTSTRAP_MODEL", "anthropic/claude-haiku-4-5").strip()
OPENCLAW_THINKING_LEVEL = os.environ.get("OPENCLAW_THINKING_LEVEL", "minimal").strip().lower()
OPENCLAW_BIN_RAW = os.environ.get("OPENCLAW_BIN", "openclaw").strip() or "openclaw"
OPENCLAW_NO_EMOJI = os.environ.get("OPENCLAW_NO_EMOJI", "1").strip().lower() in ("1", "true", "yes", "on")
EDGE_TTS_PYTHON = os.environ.get("EDGE_TTS_PYTHON", "").strip() or sys.executable
EDGE_TTS_VOICE = os.environ.get("EDGE_TTS_VOICE", "ko-KR-SunHiNeural").strip()
EDGE_TTS_RATE = os.environ.get("EDGE_TTS_RATE", "+0%").strip()
EDGE_TTS_PITCH = os.environ.get("EDGE_TTS_PITCH", "+0Hz").strip()
EDGE_TTS_VOLUME = os.environ.get("EDGE_TTS_VOLUME", "+0%").strip()
EDGE_GAIN_DB = os.environ.get("EDGE_GAIN_DB", "0").strip()
EDGE_AUDIO_FILTER = os.environ.get("EDGE_AUDIO_FILTER", "alimiter=limit=0.90").strip()
EDGE_TAIL_SILENCE_SEC = os.environ.get("EDGE_TAIL_SILENCE_SEC", "0.35").strip()
STT_ENGINE = os.environ.get("STT_ENGINE", "faster-whisper").strip().lower()
STT_MODEL = os.environ.get("STT_MODEL", "small").strip()
STT_DEVICE = os.environ.get("STT_DEVICE", "auto").strip()
STT_COMPUTE_TYPE = os.environ.get("STT_COMPUTE_TYPE", "int8").strip()
STT_LANGUAGE = os.environ.get("STT_LANGUAGE", "ko").strip()
STT_BEAM_SIZE = int(os.environ.get("STT_BEAM_SIZE", "2"))
STT_VAD_FILTER = os.environ.get("STT_VAD_FILTER", "1").strip().lower() in ("1", "true", "yes", "on")
STT_CONDITION_PREV_TEXT = os.environ.get("STT_CONDITION_PREV_TEXT", "0").strip().lower() in ("1", "true", "yes", "on")
STT_INITIAL_PROMPT = os.environ.get("STT_INITIAL_PROMPT", "").strip()
STT_TIMEOUT_SEC = int(os.environ.get("STT_TIMEOUT_SEC", "35"))
ASR_TURN_WAIT_SEC = int(os.environ.get("ASR_TURN_WAIT_SEC", "80"))
ASR_ONLY_MODE = os.environ.get("ASR_ONLY_MODE", "0").strip().lower() in ("1", "true", "yes", "on")
INSTALLER_BOOTSTRAP_URL = os.environ.get(
    "INSTALLER_BOOTSTRAP_URL",
    "https://github.com/emasion-choonjang/talk-to-openclaw-installer/releases/download/v1.0.12/sori_agent.py",
).strip()
CLOVA_API_BASE = os.environ.get("CLOVA_API_BASE", "https://naveropenapi.apigw.ntruss.com/tts-premium/v1").strip()
CLOVA_API_KEY_ID = os.environ.get("CLOVA_API_KEY_ID", "").strip()
CLOVA_API_KEY = os.environ.get("CLOVA_API_KEY", "").strip()
CLOVA_SPEAKER = os.environ.get("CLOVA_SPEAKER", "nara").strip()
CLOVA_VOLUME = os.environ.get("CLOVA_VOLUME", "0").strip()
CLOVA_SPEED = os.environ.get("CLOVA_SPEED", "-1").strip()
CLOVA_PITCH = os.environ.get("CLOVA_PITCH", "0").strip()
CLOVA_ALPHA = os.environ.get("CLOVA_ALPHA", "0").strip()
CLOVA_END_PITCH = os.environ.get("CLOVA_END_PITCH", "0").strip()
CLOVA_EMOTION = os.environ.get("CLOVA_EMOTION", "").strip()
CLOVA_EMOTION_STRENGTH = os.environ.get("CLOVA_EMOTION_STRENGTH", "").strip()
CLOVA_SAMPLE_RATE = os.environ.get("CLOVA_SAMPLE_RATE", "16000").strip()
OPENCLAW_DIALOG_ROUTE_FILE = os.environ.get("OPENCLAW_DIALOG_ROUTE_FILE", "/tmp/openclaw_dialog_route.json").strip()

QUEUE = deque()
WAV_STORE = {}
NEXT_ID = int(time.time() * 1000)
XTTS_RUNTIME = None
STT_RUNTIME = None
STT_REQUEST_LOCK = threading.Lock()
DIALOG_REQUEST_LOCK = threading.Lock()
PAIRING_SESSIONS = {}
PAIRING_TICKETS = {}
PAIRING_LOCK = threading.Lock()
PAIRING_TTL_SEC = int(os.environ.get("PAIRING_TTL_SEC", "600"))
CURRENT_BRIDGE_ENDPOINT = f"http://{PUBLIC_HOST}:{PORT}"
LAST_INSTALL_RESULT = {"status": "none", "updated_at_ms": 0, "reason": ""}
CURRENT_DIALOG_TARGET = OPENCLAW_DIALOG_TARGET
CURRENT_DIALOG_SESSION_ID = OPENCLAW_DIALOG_SESSION_ID or OPENCLAW_DEFAULT_SESSION_ID
CURRENT_DIALOG_AGENT = OPENCLAW_DIALOG_AGENT or OPENCLAW_DEFAULT_AGENT
LAST_TTS_PULL_AT_MS = 0
LAST_TTS_PULL_IP = ""
LAST_DIALOG_METRICS = {}
LAST_TTS_PULL_METRICS = {}
SORI_AGENT_SCRIPT = str(Path(__file__).resolve().parent / "sori_agent.py")
ASR_EVENTS = deque(maxlen=80)
ASR_EVENTS_LOCK = threading.Lock()
TURN_EVENTS = deque(maxlen=300)
TURN_EVENTS_LOCK = threading.Lock()
EVENT_SEQ = 0
EVENT_SEQ_LOCK = threading.Lock()
LOG_QUEUE: "queue.Queue[dict]" = queue.Queue(maxsize=2000)
TURN_JOB_QUEUE: "queue.Queue[dict]" = queue.Queue(maxsize=32)
BRIDGE_LOG_PATH = os.environ.get("BRIDGE_LOG_PATH", "data/logs/bridge/events.jsonl").strip()
BRIDGE_AUTH_SECRET = os.environ.get("BRIDGE_AUTH_SECRET", "dev-bridge-secret").strip()
JWT_ISSUER = os.environ.get("BRIDGE_JWT_ISSUER", "sori-bridge").strip()
JWT_AUDIENCE = os.environ.get("BRIDGE_JWT_AUDIENCE", "sori-mobile").strip()
JWT_DEFAULT_TTL_SEC = int(os.environ.get("BRIDGE_JWT_TTL_SEC", "3600"))
AUTH_REQUIRED_V2 = os.environ.get("BRIDGE_AUTH_REQUIRED_V2", "1").strip().lower() in ("1", "true", "yes", "on")
INSTANCE_LOCK_HANDLE = None


def save_dialog_route_state() -> None:
    payload = {
        "target": CURRENT_DIALOG_TARGET,
        "session_id": CURRENT_DIALOG_SESSION_ID,
        "agent": CURRENT_DIALOG_AGENT,
        "updated_at_ms": now_ms(),
    }
    try:
        tmp = f"{OPENCLAW_DIALOG_ROUTE_FILE}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        os.replace(tmp, OPENCLAW_DIALOG_ROUTE_FILE)
    except Exception:
        pass


def load_dialog_route_state() -> None:
    global CURRENT_DIALOG_TARGET, CURRENT_DIALOG_SESSION_ID, CURRENT_DIALOG_AGENT
    if CURRENT_DIALOG_TARGET or CURRENT_DIALOG_SESSION_ID or CURRENT_DIALOG_AGENT:
        return
    try:
        if not os.path.exists(OPENCLAW_DIALOG_ROUTE_FILE):
            return
        with open(OPENCLAW_DIALOG_ROUTE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            return
        CURRENT_DIALOG_TARGET = str(payload.get("target") or "").strip()
        CURRENT_DIALOG_SESSION_ID = str(payload.get("session_id") or "").strip()
        CURRENT_DIALOG_AGENT = str(payload.get("agent") or "").strip()
    except Exception:
        return


def resolve_openclaw_bin(raw: str) -> str:
    candidate = (raw or "").strip() or "openclaw"
    if os.path.sep in candidate and os.path.isfile(candidate):
        return candidate
    found = shutil.which(candidate)
    if found:
        return found
    # launchd often misses Homebrew/user paths; probe common install locations.
    probe_paths = [
        "/opt/homebrew/bin/openclaw",
        "/usr/local/bin/openclaw",
        os.path.expanduser("~/bin/openclaw"),
    ]
    nvm_candidates = sorted(
        glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/openclaw")),
        reverse=True,
    )
    probe_paths.extend(nvm_candidates)
    for path in probe_paths:
        if os.path.isfile(path):
            return path
    return candidate


OPENCLAW_BIN = resolve_openclaw_bin(OPENCLAW_BIN_RAW)


def now_ms() -> int:
    return int(time.time() * 1000)


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def jwt_sign_hs256(claims: dict) -> str:
    if not BRIDGE_AUTH_SECRET:
        raise RuntimeError("bridge auth secret is not configured")
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p = b64url_encode(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
    msg = f"{h}.{p}".encode("ascii")
    sig = hmac.new(BRIDGE_AUTH_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    return f"{h}.{p}.{b64url_encode(sig)}"


def jwt_verify_hs256(token: str) -> dict:
    if not BRIDGE_AUTH_SECRET:
        raise RuntimeError("bridge auth secret is not configured")
    parts = token.split(".")
    if len(parts) != 3:
        raise RuntimeError("invalid_jwt_format")
    h, p, s = parts
    msg = f"{h}.{p}".encode("ascii")
    expected = hmac.new(BRIDGE_AUTH_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    got = b64url_decode(s)
    if not hmac.compare_digest(expected, got):
        raise RuntimeError("invalid_jwt_signature")
    payload = json.loads(b64url_decode(p).decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("invalid_jwt_payload")
    now = int(time.time())
    exp = int(payload.get("exp", 0))
    if exp and now >= exp:
        raise RuntimeError("jwt_expired")
    if payload.get("iss") != JWT_ISSUER:
        raise RuntimeError("invalid_jwt_issuer")
    if JWT_AUDIENCE and payload.get("aud") != JWT_AUDIENCE:
        raise RuntimeError("invalid_jwt_audience")
    return payload


def issue_access_token(pairing_code: str, subject: str, ttl_sec: int) -> tuple[str, int]:
    ttl = max(300, min(7200, int(ttl_sec or JWT_DEFAULT_TTL_SEC)))
    now = int(time.time())
    claims = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": subject,
        "pc": pairing_code,
        "iat": now,
        "exp": now + ttl,
        "scope": "chat events",
    }
    return jwt_sign_hs256(claims), ttl


def next_event_seq() -> int:
    global EVENT_SEQ
    with EVENT_SEQ_LOCK:
        EVENT_SEQ += 1
        return EVENT_SEQ


def enrich_event(stream: str, event: dict) -> dict:
    out = dict(event or {})
    out.setdefault("stream", stream)
    out.setdefault("source", "bridge")
    out.setdefault("source_ts_ms", now_ms())
    out.setdefault("event_seq", next_event_seq())
    return out


def push_asr_event(event: dict) -> None:
    payload = enrich_event("asr", event)
    with ASR_EVENTS_LOCK:
        ASR_EVENTS.append(payload)
    enqueue_bridge_log("asr_event", payload)


def push_turn_event(event: dict) -> None:
    payload = enrich_event("turn", event)
    with TURN_EVENTS_LOCK:
        TURN_EVENTS.append(payload)
    enqueue_bridge_log("turn_event", payload)


def collect_v2_events(since_seq: int = 0, limit: int = 200) -> list[dict]:
    with ASR_EVENTS_LOCK:
        asr = list(ASR_EVENTS)
    with TURN_EVENTS_LOCK:
        turn = list(TURN_EVENTS)
    merged = asr + turn
    merged.sort(key=lambda x: int(x.get("event_seq", 0)))
    if since_seq > 0:
        merged = [e for e in merged if int(e.get("event_seq", 0)) > since_seq]
    if limit > 0 and len(merged) > limit:
        merged = merged[-limit:]
    return merged


def enqueue_bridge_log(kind: str, payload: dict) -> None:
    item = {
        "schema_version": "1.0",
        "ts_wall_ms": now_ms(),
        "component": "bridge",
        "kind": kind,
        "payload": payload,
    }
    try:
        LOG_QUEUE.put_nowait(item)
    except queue.Full:
        # Do not block serving path; drop and continue.
        pass


def is_localhost_ip(ip: str) -> bool:
    return ip in ("127.0.0.1", "::1", "localhost")


def request_bridge_endpoint(handler: BaseHTTPRequestHandler) -> str:
    host_header = (handler.headers.get("Host") or "").strip()
    if host_header:
        if ":" in host_header:
            return f"http://{host_header}"
        return f"http://{host_header}:{PORT}"
    return CURRENT_BRIDGE_ENDPOINT


def request_bridge_host_port(handler: BaseHTTPRequestHandler) -> tuple[str, int]:
    host_header = (handler.headers.get("Host") or "").strip()
    if host_header:
        if ":" in host_header:
            host, port = host_header.rsplit(":", 1)
            try:
                return host, int(port)
            except ValueError:
                return host, PORT
        return host_header, PORT
    return PUBLIC_HOST, PORT


def maybe_read_device_config(ip: str, timeout_sec: float = 0.35) -> dict | None:
    try:
        with urlopen(f"http://{ip}:18991/device/config", timeout=timeout_sec) as resp:
            if resp.status != 200:
                return None
            payload = json.loads(resp.read().decode("utf-8"))
            if isinstance(payload, dict) and ("endpoint" in payload or payload.get("ok") is True):
                return payload
    except Exception:
        return None
    return None


def discover_esp_device_ip(preferred_client_ip: str = "") -> tuple[str | None, str]:
    started = time.time()
    max_scan_sec = 8.0

    # 1) Try ARP cache first (fast) using known ESP32 OUI prefix d4:e9:f4.
    try:
        cp = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=1.0)
        if cp.returncode == 0:
            for line in cp.stdout.splitlines():
                low = line.lower()
                if " d4:e9:f4:" in low or " d4:e9:f4" in low:
                    m = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", line)
                    if m:
                        ip = m.group(1)
                        if maybe_read_device_config(ip) is not None:
                            return ip, "arp_oui"
    except Exception:
        pass

    # 2) Scan client subnet for :18991/device/config.
    seed_ip = preferred_client_ip.strip() if preferred_client_ip else ""
    try:
        if not seed_ip:
            seed_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        seed_ip = ""

    if not seed_ip:
        return None, "no_seed_ip"

    try:
        net = ipaddress.ip_network(f"{seed_ip}/24", strict=False)
    except Exception:
        return None, "invalid_seed_ip"

    # Prefer ARP-visible hosts in subnet first (faster than full /24).
    arp_candidates: list[str] = []
    try:
        cp = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=1.0)
        if cp.returncode == 0:
            for line in cp.stdout.splitlines():
                m = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", line)
                if not m:
                    continue
                ip = m.group(1)
                if ip.startswith("127."):
                    continue
                if ip == seed_ip:
                    continue
                if ipaddress.ip_address(ip) in net:
                    arp_candidates.append(ip)
    except Exception:
        pass

    checked = set()
    for ip in arp_candidates:
        if ip in checked:
            continue
        checked.add(ip)
        if maybe_read_device_config(ip, timeout_sec=0.20) is not None:
            return ip, "arp_subnet"
        if (time.time() - started) >= max_scan_sec:
            return None, "scan_timeout"

    # Bounded fallback scan.
    for host in net.hosts():
        if (time.time() - started) >= max_scan_sec:
            return None, "scan_timeout"
        ip = str(host)
        if ip == seed_ip:
            continue
        if ip in checked:
            continue
        if maybe_read_device_config(ip, timeout_sec=0.20) is not None:
            return ip, "subnet_scan"
    return None, "not_found"


def installer_status() -> dict:
    if not os.path.exists(SORI_AGENT_SCRIPT):
        return {"ok": False, "installed": False, "running": False, "error": "sori_agent.py not found"}
    try:
        cp = subprocess.run(
            [sys.executable, SORI_AGENT_SCRIPT, "status"],
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        if cp.returncode != 0:
            return {"ok": False, "installed": False, "running": False, "error": (cp.stderr or cp.stdout).strip()}
        payload = json.loads(cp.stdout or "{}")
        if not isinstance(payload, dict):
            return {"ok": False, "installed": False, "running": False, "error": "invalid status payload"}
        return payload
    except Exception as exc:
        return {"ok": False, "installed": False, "running": False, "error": str(exc)}


def infer_openclaw_dialog_route() -> dict:
    """
    Try to infer a usable OpenClaw dialog route from recent sessions.
    Returns: {"target": str, "session_id": str, "agent": str, "source": str} or {}.
    """
    try:
        cp = subprocess.run(
            [OPENCLAW_BIN, "status", "--json"],
            capture_output=True,
            text=True,
            timeout=8.0,
            check=False,
        )
        if not (cp.stdout or "").strip():
            return {}
        payload = json.loads(cp.stdout or "{}")
        recent = (payload.get("sessions") or {}).get("recent") or []
        if not isinstance(recent, list):
            recent = []
        preferred_channels = (":telegram:", ":whatsapp:", ":discord:", ":slack:", ":signal:")
        # 1) Prefer non-cron/channel sessions.
        for item in recent:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("sessionId") or "").strip()
            key = str(item.get("key") or "").strip()
            if not sid:
                continue
            if ":cron:" in key:
                continue
            if any(ch in key for ch in preferred_channels):
                return {
                    "target": "",
                    "session_id": sid,
                    "agent": str(item.get("agentId") or "").strip(),
                    "source": "status.recent.channel",
                }
        # 2) Any non-cron recent session.
        for item in recent:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("sessionId") or "").strip()
            key = str(item.get("key") or "").strip()
            if sid and ":cron:" not in key:
                return {
                    "target": "",
                    "session_id": sid,
                    "agent": str(item.get("agentId") or "").strip(),
                    "source": "status.recent",
                }
        # 3) Fallback: any recent session id.
        for item in recent:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("sessionId") or "").strip()
            if sid:
                return {
                    "target": "",
                    "session_id": sid,
                    "agent": str(item.get("agentId") or "").strip(),
                    "source": "status.recent.fallback",
                }
    except Exception:
        return {}
    return {}


def ensure_dialog_route() -> tuple[bool, str]:
    global CURRENT_DIALOG_TARGET, CURRENT_DIALOG_SESSION_ID, CURRENT_DIALOG_AGENT
    if CURRENT_DIALOG_TARGET or CURRENT_DIALOG_SESSION_ID or CURRENT_DIALOG_AGENT:
        return True, "already_set"
    inferred = infer_openclaw_dialog_route()
    if inferred:
        CURRENT_DIALOG_TARGET = str(inferred.get("target") or "").strip()
        CURRENT_DIALOG_SESSION_ID = str(inferred.get("session_id") or "").strip()
        CURRENT_DIALOG_AGENT = str(inferred.get("agent") or "").strip()
        if CURRENT_DIALOG_TARGET or CURRENT_DIALOG_SESSION_ID or CURRENT_DIALOG_AGENT:
            save_dialog_route_state()
            return True, str(inferred.get("source") or "inferred")
    # Last resort: bridge dedicated sub-session first, then default agent id.
    if OPENCLAW_DEFAULT_SESSION_ID:
        CURRENT_DIALOG_SESSION_ID = OPENCLAW_DEFAULT_SESSION_ID
    if OPENCLAW_DEFAULT_AGENT:
        CURRENT_DIALOG_AGENT = OPENCLAW_DEFAULT_AGENT
    save_dialog_route_state()
    return True, "default_session" if not inferred else "default_session_after_infer"


def purge_expired_pairing_state() -> None:
    now = now_ms()
    with PAIRING_LOCK:
        expired_codes = [code for code, session in PAIRING_SESSIONS.items() if session["expires_at_ms"] <= now]
        for code in expired_codes:
            PAIRING_SESSIONS.pop(code, None)
        expired_tickets = [ticket for ticket, data in PAIRING_TICKETS.items() if data["expires_at_ms"] <= now]
        for ticket in expired_tickets:
            PAIRING_TICKETS.pop(ticket, None)


def create_pairing_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(alphabet[secrets.randbelow(len(alphabet))] for _ in range(6))


def generate_tone_wav(sample_rate: int = 16000, freq_hz: int = 660, duration_sec: float = 1.2, amp: int = 14000) -> bytes:
    num_samples = int(sample_rate * duration_sec)
    bio = BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            s = int(amp * math.sin(2.0 * math.pi * freq_hz * (i / sample_rate)))
            frames += int(s).to_bytes(2, byteorder="little", signed=True)
        wf.writeframes(bytes(frames))
    return bio.getvalue()




def acquire_instance_lock(port: int):
    lock_path = f"/tmp/sori-bridge-{port}.lock"
    handle = open(lock_path, "a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise RuntimeError(f"bridge_already_running_on_port_{port}")
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    return handle

def synthesize_text_wav(text: str) -> bytes:
    text = sanitize_tts_text(text)
    if not text:
        return generate_tone_wav(duration_sec=0.6)
    started_at = time.time()
    print(f"[tts] synth start engine={TTS_ENGINE} text_len={len(text)}", flush=True)
    if TTS_ENGINE == "edge":
        wav = synthesize_text_wav_with_edge(text)
        if wav is not None:
            print(f"[tts] synth done engine=edge bytes={len(wav)} elapsed={time.time()-started_at:.3f}s", flush=True)
            return wav
        print("[tts] edge failed, fallback to say", flush=True)
    if TTS_ENGINE == "clova":
        wav = synthesize_text_wav_with_clova(text)
        if wav is not None:
            print(f"[tts] synth done engine=clova bytes={len(wav)} elapsed={time.time()-started_at:.3f}s", flush=True)
            return wav
        print("[tts] clova failed, fallback to say", flush=True)
    if TTS_ENGINE == "xtts":
        wav = synthesize_text_wav_with_xtts(text)
        if wav is not None:
            print(f"[tts] synth done engine=xtts bytes={len(wav)} elapsed={time.time()-started_at:.3f}s", flush=True)
            return wav
        print("[tts] xtts failed, fallback to piper/say", flush=True)
    if TTS_ENGINE == "piper":
        wav = synthesize_text_wav_with_piper(text)
        if wav is not None:
            print(f"[tts] synth done engine=piper bytes={len(wav)} elapsed={time.time()-started_at:.3f}s", flush=True)
            return wav
        print("[tts] piper failed, fallback to say", flush=True)
    wav = synthesize_text_wav_with_say(text)
    print(f"[tts] synth done engine=say bytes={len(wav)} elapsed={time.time()-started_at:.3f}s", flush=True)
    return wav

def sanitize_tts_text(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.upper().startswith("MEDIA:"):
            continue
        line = re.sub(r"^[\-*•]+\s*", "", line)
        line = line.replace("**", "").replace("__", "").replace("`", "")
        lines.append(line)
    text = " ".join(lines)
    # Remove common emoji/symbol ranges to avoid awkward pronunciation by Korean TTS engines.
    text = re.sub(r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\u2600-\u26FF]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 280:
        text = text[:280].rsplit(" ", 1)[0] + "."
    return text

def synthesize_text_wav_with_clova(text: str) -> bytes | None:
    if not CLOVA_API_KEY_ID or not CLOVA_API_KEY:
        print("[tts] clova unavailable: set CLOVA_API_KEY_ID/CLOVA_API_KEY", flush=True)
        return None
    body = {
        "speaker": CLOVA_SPEAKER,
        "text": text,
        "format": "wav",
        "sampling-rate": CLOVA_SAMPLE_RATE or "16000",
        "volume": CLOVA_VOLUME or "0",
        "speed": CLOVA_SPEED or "-1",
        "pitch": CLOVA_PITCH or "0",
        "alpha": CLOVA_ALPHA or "0",
        "end-pitch": CLOVA_END_PITCH or "0",
    }
    if CLOVA_EMOTION:
        body["emotion"] = CLOVA_EMOTION
    if CLOVA_EMOTION_STRENGTH:
        body["emotion-strength"] = CLOVA_EMOTION_STRENGTH
    data = urlencode(body).encode("utf-8")
    req = Request(
        f"{CLOVA_API_BASE}/tts",
        data=data,
        headers={
            "X-NCP-APIGW-API-KEY-ID": CLOVA_API_KEY_ID,
            "X-NCP-APIGW-API-KEY": CLOVA_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            wav = resp.read()
        if not wav:
            print("[tts] clova returned empty body", flush=True)
            return None
        return canonicalize_wav_bytes(wav)
    except Exception as exc:
        print(f"[tts] clova request failed: {exc}", flush=True)
        return None

def synthesize_text_wav_with_edge(text: str) -> bytes | None:
    with tempfile.TemporaryDirectory(prefix="openclaw_edge_tts_") as td:
        mp3 = os.path.join(td, "tts.mp3")
        wav = os.path.join(td, "tts.wav")
        cmd = [
            EDGE_TTS_PYTHON,
            "-m",
            "edge_tts",
            "--voice",
            EDGE_TTS_VOICE,
            "--text",
            text,
            "--write-media",
            mp3,
            "--rate",
            EDGE_TTS_RATE or "+0%",
            "--pitch",
            EDGE_TTS_PITCH or "+0Hz",
            "--volume",
            EDGE_TTS_VOLUME or "+0%",
        ]
        cp = subprocess.run(cmd, capture_output=True, text=True)
        if cp.returncode != 0:
            print(f"[tts] edge_tts failed: {cp.stderr[:300]}", flush=True)
            return None
        if not os.path.exists(mp3):
            print("[tts] edge_tts output missing", flush=True)
            return None

        ffmpeg_path = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
        if ffmpeg_path.returncode == 0:
            edge_filter_parts = []
            if EDGE_GAIN_DB:
                edge_filter_parts.append(f"volume={EDGE_GAIN_DB}dB")
            if EDGE_AUDIO_FILTER:
                edge_filter_parts.append(EDGE_AUDIO_FILTER)
            if EDGE_TAIL_SILENCE_SEC:
                edge_filter_parts.append(f"apad=pad_dur={EDGE_TAIL_SILENCE_SEC}")
            cp2 = subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    mp3,
                    *([] if not edge_filter_parts else ["-af", ",".join(edge_filter_parts)]),
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    wav,
                ],
                capture_output=True,
                text=True,
            )
            if cp2.returncode == 0 and os.path.exists(wav):
                with open(wav, "rb") as f:
                    return canonicalize_wav_bytes(f.read())
            print(f"[tts] edge ffmpeg normalize failed: {cp2.stderr[:300]}", flush=True)

        normalized = convert_wav_to_16k_mono(mp3)
        if normalized is not None:
            return normalized
        return None


def synthesize_text_wav_with_say(text: str) -> bytes:
    say_path = subprocess.run(["which", "say"], capture_output=True, text=True)
    if say_path.returncode != 0:
        return generate_tone_wav()

    with tempfile.TemporaryDirectory(prefix="openclaw_tts_") as td:
        aiff = os.path.join(td, "tts.aiff")
        wav = os.path.join(td, "tts.raw.wav")
        subprocess.run(["say", "-v", VOICE, "-o", aiff, text], check=True)
        ffmpeg_path = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
        if ffmpeg_path.returncode == 0:
            out = os.path.join(td, "tts.wav")
            say_filter_parts = []
            if SAY_GAIN_DB:
                say_filter_parts.append(f"volume={SAY_GAIN_DB}dB")
            if FFMPEG_AUDIO_FILTER:
                say_filter_parts.append(FFMPEG_AUDIO_FILTER)
            if SAY_TAIL_SILENCE_SEC:
                say_filter_parts.append(f"apad=pad_dur={SAY_TAIL_SILENCE_SEC}")
            cp = subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    aiff,
                    *([] if not say_filter_parts else ["-af", ",".join(say_filter_parts)]),
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    out,
                ],
                capture_output=True,
                text=True,
            )
            if cp.returncode == 0 and os.path.exists(out):
                with open(out, "rb") as f:
                    return canonicalize_wav_bytes(f.read())
        normalized = convert_wav_to_16k_mono(aiff)
        if normalized is not None:
            return normalized
        with open(wav, "rb") as f:
            return f.read()

def convert_wav_to_16k_mono(input_wav: str) -> bytes | None:
    ffmpeg_path = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
    if ffmpeg_path.returncode == 0:
        with tempfile.TemporaryDirectory(prefix="openclaw_wav_norm_") as td:
            out_wav = os.path.join(td, "tts_16k.wav")
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", input_wav]
            if FFMPEG_AUDIO_FILTER:
                cmd.extend(["-af", FFMPEG_AUDIO_FILTER])
            cmd.extend(["-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", out_wav])
            cp = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            if cp.returncode == 0 and os.path.exists(out_wav):
                with open(out_wav, "rb") as f:
                    return canonicalize_wav_bytes(f.read())
            print(f"[tts] ffmpeg normalize failed: {cp.stderr[:300]}", flush=True)

    afconvert_path = subprocess.run(["which", "afconvert"], capture_output=True, text=True)
    if afconvert_path.returncode != 0:
        return None
    with tempfile.TemporaryDirectory(prefix="openclaw_wav_norm_") as td:
        out_wav = os.path.join(td, "tts_16k.wav")
        cp = subprocess.run(
            ["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", input_wav, out_wav],
            capture_output=True,
            text=True,
        )
        if cp.returncode != 0 or not os.path.exists(out_wav):
            print(f"[tts] afconvert failed: {cp.stderr[:300]}", flush=True)
            return None
        with open(out_wav, "rb") as f:
            return canonicalize_wav_bytes(f.read())

def canonicalize_wav_bytes(wav_bytes: bytes) -> bytes:
    """
    Repack WAV into a minimal PCM RIFF container.
    This removes non-standard chunks (e.g., FLLR/LIST) that can confuse simple decoders.
    """
    try:
        bio = BytesIO(wav_bytes)
        with wave.open(bio, "rb") as src:
            channels = src.getnchannels()
            sampwidth = src.getsampwidth()
            framerate = src.getframerate()
            frames = src.readframes(src.getnframes())
        out = BytesIO()
        with wave.open(out, "wb") as dst:
            dst.setnchannels(channels)
            dst.setsampwidth(sampwidth)
            dst.setframerate(framerate)
            dst.writeframes(frames)
        return out.getvalue()
    except Exception:
        return wav_bytes


def synthesize_text_wav_with_piper(text: str) -> bytes | None:
    if not PIPER_MODEL:
        print("[tts] PIPER_MODEL is empty", flush=True)
        return None
    if not os.path.exists(PIPER_MODEL):
        print(f"[tts] PIPER_MODEL not found: {PIPER_MODEL}", flush=True)
        return None
    if not os.path.exists(PIPER_BIN):
        print(f"[tts] PIPER_BIN not found: {PIPER_BIN}", flush=True)
        return None

    with tempfile.TemporaryDirectory(prefix="openclaw_piper_") as td:
        wav = os.path.join(td, "tts.wav")
        cmd = [PIPER_BIN, "--model", PIPER_MODEL, "--output-file", wav]
        if PIPER_CONFIG and os.path.exists(PIPER_CONFIG):
            cmd.extend(["--config", PIPER_CONFIG])
        if PIPER_SPEAKER:
            cmd.extend(["--speaker", PIPER_SPEAKER])
        if PIPER_LENGTH_SCALE:
            cmd.extend(["--length-scale", PIPER_LENGTH_SCALE])
        if PIPER_NOISE_SCALE:
            cmd.extend(["--noise-scale", PIPER_NOISE_SCALE])
        if PIPER_NOISE_W_SCALE:
            cmd.extend(["--noise-w-scale", PIPER_NOISE_W_SCALE])
        if PIPER_SENTENCE_SILENCE:
            cmd.extend(["--sentence-silence", PIPER_SENTENCE_SILENCE])
        if PIPER_VOLUME:
            cmd.extend(["--volume", PIPER_VOLUME])
        cp = subprocess.run(cmd, input=text + "\n", text=True, capture_output=True)
        if cp.returncode != 0:
            print(f"[tts] piper failed: {cp.stderr[:300]}", flush=True)
            return None
        if not os.path.exists(wav):
            print("[tts] piper output missing", flush=True)
            return None
        normalized = convert_wav_to_16k_mono(wav)
        if normalized is not None:
            return normalized
        with open(wav, "rb") as f:
            return f.read()

def load_xtts_runtime():
    global XTTS_RUNTIME
    if XTTS_RUNTIME is not None:
        return XTTS_RUNTIME
    if importlib.util.find_spec("TTS") is None:
        print("[tts] xtts unavailable: pip install TTS", flush=True)
        return None
    try:
        from TTS.api import TTS as CoquiTTS  # type: ignore
        tts = CoquiTTS(XTTS_MODEL)
        if XTTS_DEVICE and hasattr(tts, "to"):
            tts = tts.to(XTTS_DEVICE)
        XTTS_RUNTIME = tts
        return XTTS_RUNTIME
    except Exception as exc:
        print(f"[tts] xtts load failed: {exc}", flush=True)
        return None

def synthesize_text_wav_with_xtts(text: str) -> bytes | None:
    if not XTTS_SPEAKER_WAV:
        print("[tts] XTTS_SPEAKER_WAV is empty", flush=True)
        return None
    if not os.path.exists(XTTS_SPEAKER_WAV):
        print(f"[tts] XTTS_SPEAKER_WAV not found: {XTTS_SPEAKER_WAV}", flush=True)
        return None

    tts = load_xtts_runtime()
    if tts is None:
        return None
    try:
        speed = float(XTTS_SPEED) if XTTS_SPEED else 1.0
    except ValueError:
        speed = 1.0
    split_sentences = XTTS_SPLIT_SENTENCES in ("1", "true", "yes", "on")
    xtts_kwargs = {}
    if XTTS_TEMPERATURE:
        try:
            xtts_kwargs["temperature"] = float(XTTS_TEMPERATURE)
        except ValueError:
            pass
    if XTTS_TOP_K:
        try:
            xtts_kwargs["top_k"] = int(XTTS_TOP_K)
        except ValueError:
            pass
    if XTTS_TOP_P:
        try:
            xtts_kwargs["top_p"] = float(XTTS_TOP_P)
        except ValueError:
            pass
    if XTTS_REPETITION_PENALTY:
        try:
            xtts_kwargs["repetition_penalty"] = float(XTTS_REPETITION_PENALTY)
        except ValueError:
            pass

    with tempfile.TemporaryDirectory(prefix="openclaw_xtts_") as td:
        wav = os.path.join(td, "tts.wav")
        try:
            tts.tts_to_file(
                text=text,
                language=XTTS_LANGUAGE,
                speaker_wav=XTTS_SPEAKER_WAV,
                speed=speed,
                split_sentences=split_sentences,
                file_path=wav,
                **xtts_kwargs,
            )
        except Exception as exc:
            print(f"[tts] xtts synth failed: {exc}", flush=True)
            return None

        if not os.path.exists(wav):
            print("[tts] xtts output missing", flush=True)
            return None
        normalized = convert_wav_to_16k_mono(wav)
        if normalized is not None:
            return normalized
        with open(wav, "rb") as f:
            return f.read()

def run_openclaw_agent(
    message: str,
    target: str,
    timeout_sec: int,
    session_id: str = "",
    agent: str = "",
) -> str:
    cmd = [OPENCLAW_BIN, "agent"]
    if target:
        cmd.extend(["--to", target])
    elif session_id:
        cmd.extend(["--session-id", session_id])
    elif agent:
        cmd.extend(["--agent", agent])
    # No explicit target: fall back to local/default OpenClaw context.
    outbound_message = message
    if OPENCLAW_NO_EMOJI:
        outbound_message = (
            "이모지는 절대 사용하지 말고, 한국어 평문으로 짧고 명확하게 답해줘. "
            "한 문장으로, 최대 22자 내외로 답해줘. "
            + message
        )
    if OPENCLAW_THINKING_LEVEL in ("off", "minimal", "low", "medium", "high"):
        cmd.extend(["--thinking", OPENCLAW_THINKING_LEVEL])
    cmd.extend(["--message", outbound_message, "--json", "--timeout", str(timeout_sec)])
    cp = None
    for attempt in range(3):
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True, check=True)
            break
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"OpenClaw CLI not found: '{OPENCLAW_BIN}'. "
                "Set OPENCLAW_BIN or install OpenClaw CLI in /opt/homebrew/bin."
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").lower()
            lock_like = (
                "session file locked" in stderr
                or "sessions.json.lock" in stderr
                or "timeout 10000ms" in stderr
            )
            if lock_like and attempt < 2:
                backoff_sec = 0.4 + random.random() * 0.8
                print(
                    f"[dialog:retry] reason=session_lock attempt={attempt+1} sleep={backoff_sec:.2f}s",
                    flush=True,
                )
                time.sleep(backoff_sec)
                continue
            raise
    if cp is None:
        raise RuntimeError("OpenClaw invocation failed")
    payload = json.loads(cp.stdout)
    if "result" in payload and "payloads" in payload["result"]:
        items = payload["result"]["payloads"]
    else:
        items = payload.get("payloads", [])
    text = ""
    for item in (items or []):
        candidate = sanitize_tts_text(item.get("text") or "")
        if candidate:
            text = candidate
            break
    if text:
        return text

    # JSON shape fallback: pull text-like fields recursively.
    def _collect_strings(obj: object, out: list[str]) -> None:
        if isinstance(obj, str):
            s = sanitize_tts_text(obj)
            if s:
                out.append(s)
            return
        if isinstance(obj, list):
            for v in obj:
                _collect_strings(v, out)
            return
        if isinstance(obj, dict):
            # Prioritize common text keys first.
            for k in ("text", "message", "content", "reply"):
                if k in obj:
                    _collect_strings(obj.get(k), out)
            for _k, v in obj.items():
                _collect_strings(v, out)

    candidates: list[str] = []
    _collect_strings(payload, candidates)
    for c in candidates:
        if len(c) >= 2:
            return c

    raise RuntimeError(f"No OpenClaw payload text found: {cp.stdout[:240]}")


def transcribe_wav_bytes(wav_bytes: bytes) -> str:
    global STT_RUNTIME
    if not wav_bytes or len(wav_bytes) < 44:
        raise RuntimeError("empty wav payload")
    if STT_ENGINE in ("", "none", "disabled", "off"):
        raise RuntimeError("STT engine disabled")

    if STT_ENGINE != "faster-whisper":
        raise RuntimeError(f"Unsupported STT_ENGINE: {STT_ENGINE}")

    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "faster-whisper not installed. install: pip install faster-whisper"
        ) from exc

    if STT_RUNTIME is None:
        STT_RUNTIME = WhisperModel(
            STT_MODEL,
            device=STT_DEVICE,
            compute_type=STT_COMPUTE_TYPE,
        )

    boosted_wav_bytes = wav_bytes
    try:
        with wave.open(BytesIO(wav_bytes), "rb") as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            pcm = wf.readframes(wf.getnframes())
        if channels == 1 and sampwidth == 2 and framerate == 16000 and pcm:
            samples = array("h")
            samples.frombytes(pcm)
            peak = max((abs(int(s)) for s in samples), default=0)
            # Low input level: create boosted fallback wav for 3rd attempt.
            if peak > 0 and peak < 4200:
                gain = 3
                boosted = array("h")
                for s in samples:
                    v = int(s) * gain
                    if v > 32767:
                        v = 32767
                    elif v < -32768:
                        v = -32768
                    boosted.append(v)
                out = BytesIO()
                with wave.open(out, "wb") as wf2:
                    wf2.setnchannels(1)
                    wf2.setsampwidth(2)
                    wf2.setframerate(16000)
                    wf2.writeframes(boosted.tobytes())
                boosted_wav_bytes = out.getvalue()
    except Exception:
        boosted_wav_bytes = wav_bytes

    with tempfile.NamedTemporaryFile(prefix="openclaw_asr_", suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes)
        tmp_path = tmp.name
    boosted_tmp_path = None
    if boosted_wav_bytes is not wav_bytes:
        with tempfile.NamedTemporaryFile(prefix="openclaw_asr_boost_", suffix=".wav", delete=False) as tmp2:
            tmp2.write(boosted_wav_bytes)
            boosted_tmp_path = tmp2.name

    try:
        attempts = [
            {
                "name": "primary",
                "path": tmp_path,
                "vad_filter": STT_VAD_FILTER,
                "beam_size": max(1, STT_BEAM_SIZE),
                "initial_prompt": STT_INITIAL_PROMPT if STT_INITIAL_PROMPT else None,
            },
            # Fallback for short/weak speech: disable VAD and widen search once.
            {
                "name": "fallback_no_vad",
                "path": tmp_path,
                "vad_filter": False,
                "beam_size": max(2, STT_BEAM_SIZE + 1),
                "initial_prompt": None,
            },
        ]
        if boosted_tmp_path is not None:
            attempts.append(
                {
                    "name": "fallback_boosted_no_vad",
                    "path": boosted_tmp_path,
                    "vad_filter": False,
                    "beam_size": max(2, STT_BEAM_SIZE + 1),
                    "initial_prompt": None,
                }
            )
        started_at = time.time()
        for idx, attempt in enumerate(attempts):
            result_box: dict[str, object] = {}
            error_box: dict[str, Exception] = {}

            def _run_transcribe() -> None:
                try:
                    segments, _info = STT_RUNTIME.transcribe(
                        str(attempt["path"]),
                        language=STT_LANGUAGE,
                        beam_size=int(attempt["beam_size"]),
                        vad_filter=bool(attempt["vad_filter"]),
                        condition_on_previous_text=STT_CONDITION_PREV_TEXT,
                        initial_prompt=attempt["initial_prompt"],
                    )
                    text = " ".join((seg.text or "").strip() for seg in segments).strip()
                    result_box["text"] = text
                except Exception as exc:
                    error_box["exc"] = exc

            th = threading.Thread(target=_run_transcribe, daemon=True)
            th.start()
            elapsed = time.time() - started_at
            remain = max(3.0, float(STT_TIMEOUT_SEC) - elapsed)
            th.join(timeout=remain)
            if th.is_alive():
                # Timeout means model/runtime is still blocked in worker thread.
                # Do not launch extra attempts; fail fast so device can back off/retry next turn.
                print(f"[asr:retry] reason=timeout attempt={attempt['name']}", flush=True)
                raise RuntimeError(f"stt_timeout_{STT_TIMEOUT_SEC}s")
            if "exc" in error_box:
                if idx == len(attempts) - 1:
                    raise error_box["exc"]
                print(f"[asr:retry] reason=exception attempt={attempt['name']} err={error_box['exc']}", flush=True)
                continue
            text = str(result_box.get("text", "")).strip()
            if text:
                if idx > 0:
                    print(f"[asr:retry] recovered_by={attempt['name']}", flush=True)
                return text
            if idx < len(attempts) - 1:
                print(f"[asr:retry] reason=empty attempt={attempt['name']}", flush=True)
        raise RuntimeError("stt_empty_result")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        if boosted_tmp_path is not None:
            try:
                os.unlink(boosted_tmp_path)
            except Exception:
                pass


def warmup_stt_runtime() -> None:
    global STT_RUNTIME
    if STT_ENGINE != "faster-whisper":
        return
    if STT_RUNTIME is not None:
        return
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception:
        return
    started = time.time()
    STT_RUNTIME = WhisperModel(
        STT_MODEL,
        device=STT_DEVICE,
        compute_type=STT_COMPUTE_TYPE,
    )
    print(
        f"[asr:warmup] engine={STT_ENGINE} model={STT_MODEL} device={STT_DEVICE} "
        f"compute={STT_COMPUTE_TYPE} elapsed={time.time()-started:.2f}s",
        flush=True,
    )


def execute_dialog_turn(
    asr_text: str,
    skip_openclaw: bool = False,
    to: str = "",
    session_id: str = "",
    agent: str = "",
    timeout_sec: int = OPENCLAW_DIALOG_TIMEOUT_SEC,
) -> dict:
    global LAST_DIALOG_METRICS, CURRENT_DIALOG_AGENT
    asr_text = (asr_text or "").strip()
    if not asr_text:
        raise RuntimeError("asr_text is empty")

    target = (to or CURRENT_DIALOG_TARGET).strip() or CURRENT_DIALOG_TARGET
    session = (session_id or CURRENT_DIALOG_SESSION_ID).strip() or CURRENT_DIALOG_SESSION_ID
    agent_name = (agent or CURRENT_DIALOG_AGENT).strip() or CURRENT_DIALOG_AGENT
    if not skip_openclaw and not (target or session or agent_name):
        route_ok, _ = ensure_dialog_route()
        if route_ok:
            target = CURRENT_DIALOG_TARGET
            session = CURRENT_DIALOG_SESSION_ID
            agent_name = CURRENT_DIALOG_AGENT
    if not skip_openclaw and not (target or session or agent_name):
        agent_name = OPENCLAW_DEFAULT_AGENT
        CURRENT_DIALOG_AGENT = agent_name
        save_dialog_route_state()
        print(f"[dialog:route] fallback agent={agent_name}", flush=True)

    turn_id = secrets.token_hex(6)
    started_at = time.time()
    route_desc = f"to={target or '-'} session={session or '-'} agent={agent_name or '-'}"
    push_turn_event(
        {
            "turn_id": turn_id,
            "event": "speaker.voice_user_committed",
            "status": "ok",
            "text": asr_text,
            "meta": {
                "route": {
                    "to": target or "",
                    "session_id": session or "",
                    "agent": agent_name or "",
                }
            },
        }
    )
    print(
        f"[dialog:start] turn_id={turn_id} asr_len={len(asr_text)} route=({route_desc}) skip_openclaw={int(skip_openclaw)}",
        flush=True,
    )
    if skip_openclaw:
        reply_text = asr_text
        openclaw_ms = 0
    else:
        t0 = time.time()
        reply_text = run_openclaw_agent(
            asr_text,
            target,
            timeout_sec,
            session_id=session,
            agent=agent_name,
        )
        openclaw_ms = int((time.time() - t0) * 1000)
        print(
            f"[dialog:openclaw] turn_id={turn_id} openclaw_ms={openclaw_ms} reply_len={len(reply_text)}",
            flush=True,
        )
    t1 = time.time()
    item = enqueue_tts(reply_text)
    push_turn_event(
        {
            "turn_id": turn_id,
            "event": "speaker.assistant_replied",
            "status": "ok",
            "text": reply_text,
            "id": item.get("id"),
            "meta": {"created_at_ms": item.get("created_at_ms"), "queue_size": len(QUEUE)},
        }
    )
    push_turn_event(
        {
            "turn_id": turn_id,
            "event": "speaker.tts_enqueued",
            "status": "ok",
            "id": item.get("id"),
            "meta": {"queue_size": len(QUEUE), "path": item.get("path"), "created_at_ms": item.get("created_at_ms")},
        }
    )
    tts_ms = int((time.time() - t1) * 1000)
    total_ms = int((time.time() - started_at) * 1000)
    LAST_DIALOG_METRICS = {
        "turn_id": turn_id,
        "asr_text_len": len(asr_text),
        "reply_text_len": len(reply_text),
        "latency_ms": {
            "openclaw": openclaw_ms,
            "tts": tts_ms,
            "total": total_ms,
        },
        "queued_id": item["id"],
        "queued_at_ms": item.get("created_at_ms"),
        "queue_size_after_enqueue": len(QUEUE),
    }
    print(
        (
            f"[dialog:done] turn_id={turn_id} openclaw_ms={openclaw_ms} "
            f"tts_ms={tts_ms} total_ms={total_ms} queued_id={item['id']} "
            f"queue_size={len(QUEUE)}"
        ),
        flush=True,
    )
    return {
        "ok": True,
        "turn_id": turn_id,
        "asr_text": asr_text,
        "reply_text": reply_text,
        "queued": True,
        "id": item["id"],
        "queued_at_ms": item.get("created_at_ms"),
        "queue_size_after_enqueue": len(QUEUE),
        "latency_ms": {"openclaw": openclaw_ms, "tts": tts_ms, "total": total_ms},
    }


def process_asr_turn(
    *,
    turn_id: str,
    wav_bytes: bytes,
    req_id: str,
    asr_only: bool,
    skip_openclaw: bool,
    to: str,
    session_id: str,
    agent: str,
    timeout_sec: int,
) -> dict:
    stt_started = time.time()
    push_asr_event(
        {
            "ts_ms": now_ms(),
            "turn_id": turn_id,
            "req_id": req_id,
            "bytes": len(wav_bytes),
            "status": "processing",
            "text": "",
            "stt_ms": 0,
        }
    )
    asr_text = transcribe_wav_bytes(wav_bytes)
    stt_ms = int((time.time() - stt_started) * 1000)
    print(
        f"[asr:stt] req_id={req_id} stt_ms={stt_ms} text_len={len(asr_text)} text={asr_text!r}",
        flush=True,
    )
    push_asr_event(
        {
            "ts_ms": now_ms(),
            "turn_id": turn_id,
            "req_id": req_id,
            "bytes": len(wav_bytes),
            "status": "ok",
            "text": asr_text,
            "stt_ms": stt_ms,
        }
    )

    if asr_only:
        return {
            "ok": True,
            "mode": "asr_only",
            "asr_text": asr_text,
            "stt": {"engine": STT_ENGINE, "model": STT_MODEL, "latency_ms": stt_ms},
        }

    push_asr_event(
        {
            "ts_ms": now_ms(),
            "turn_id": turn_id,
            "req_id": req_id,
            "bytes": len(wav_bytes),
            "status": "dialog",
            "text": asr_text,
            "stt_ms": stt_ms,
        }
    )
    result = execute_dialog_turn(
        asr_text=asr_text,
        skip_openclaw=skip_openclaw,
        to=to,
        session_id=session_id,
        agent=agent,
        timeout_sec=timeout_sec,
    )
    result["stt"] = {"engine": STT_ENGINE, "model": STT_MODEL, "latency_ms": stt_ms}
    print(
        f"[asr:done] req_id={req_id} queued_id={result['id']} wav_url={result.get('wav_url','-')}",
        flush=True,
    )
    return result


def turn_job_worker() -> None:
    while True:
        job = TURN_JOB_QUEUE.get()
        if job is None:
            return
        done_evt: threading.Event = job["done_evt"]
        result_ref: dict = job["result_ref"]
        try:
            started = now_ms()
            push_turn_event(
                {
                    "turn_id": job.get("turn_id") or "",
                    "req_id": job.get("req_id") or "",
                    "event": "turn.start",
                    "status": "processing",
                    "meta": {"queue_size": TURN_JOB_QUEUE.qsize()},
                }
            )
            result = process_asr_turn(
                turn_id=job.get("turn_id") or "",
                wav_bytes=job["wav_bytes"],
                req_id=job["req_id"],
                asr_only=job["asr_only"],
                skip_openclaw=job["skip_openclaw"],
                to=job["to"],
                session_id=job["session_id"],
                agent=job["agent"],
                timeout_sec=job["timeout_sec"],
            )
            result_ref["ok"] = True
            result_ref["result"] = result
            push_turn_event(
                {
                    "turn_id": job.get("turn_id") or "",
                    "req_id": job.get("req_id") or "",
                    "event": "turn.done",
                    "status": "ok",
                    "latency_ms": now_ms() - started,
                }
            )
        except Exception as exc:
            result_ref["ok"] = False
            result_ref["error"] = exc
            push_asr_event(
                {
                    "ts_ms": now_ms(),
                    "turn_id": job.get("turn_id") or "",
                    "req_id": job.get("req_id") or "",
                    "bytes": len(job.get("wav_bytes") or b""),
                    "status": "error",
                    "text": str(exc)[:160],
                    "stt_ms": 0,
                }
            )
            push_turn_event(
                {
                    "turn_id": job.get("turn_id") or "",
                    "req_id": job.get("req_id") or "",
                    "event": "turn.done",
                    "status": "error",
                    "error": str(exc)[:160],
                }
            )
        finally:
            done_evt.set()
            TURN_JOB_QUEUE.task_done()


def bridge_log_writer() -> None:
    path = Path(BRIDGE_LOG_PATH)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    while True:
        item = LOG_QUEUE.get()
        if item is None:
            return
        try:
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        except Exception:
            pass
        finally:
            LOG_QUEUE.task_done()


def enqueue_tts(text: str) -> dict:
    global NEXT_ID
    wav = synthesize_text_wav(text)
    item_id = str(NEXT_ID)
    NEXT_ID += 1
    WAV_STORE[item_id] = wav
    payload = {
        "id": item_id,
        "text": text,
        "created_at_ms": now_ms(),
    }
    QUEUE.append(payload)
    return payload


TEST_WAV = generate_tone_wav()


class Handler(BaseHTTPRequestHandler):
    server_version = "OpenClawMock/0.2"

    def _send_json(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _read_bearer_token(self) -> str:
        auth = str(self.headers.get("Authorization", "")).strip()
        if not auth.lower().startswith("bearer "):
            return ""
        return auth[7:].strip()

    def _require_v2_auth(self) -> dict | None:
        if not AUTH_REQUIRED_V2:
            return {}
        token = self._read_bearer_token()
        if not token:
            self._send_json(401, {"error": "unauthorized", "detail": "missing_bearer_token"})
            return None
        try:
            claims = jwt_verify_hs256(token)
            pairing_code = str(claims.get("pc") or "").strip().upper()
            if pairing_code:
                with PAIRING_LOCK:
                    session = PAIRING_SESSIONS.get(pairing_code)
                if not session or session.get("status") != "confirmed":
                    self._send_json(401, {"error": "unauthorized", "detail": "pairing_not_confirmed"})
                    return None
            return claims
        except Exception as exc:
            self._send_json(401, {"error": "unauthorized", "detail": str(exc)})
            return None

    def do_GET(self):
        global CURRENT_DIALOG_TARGET, CURRENT_DIALOG_SESSION_ID, CURRENT_DIALOG_AGENT, LAST_TTS_PULL_AT_MS, LAST_TTS_PULL_IP, LAST_TTS_PULL_METRICS
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        purge_expired_pairing_state()

        if path == "/health":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "service": "openclaw-mock",
                    "ts": int(time.time()),
                    "host": socket.gethostname(),
                    "queue_size": len(QUEUE),
                },
            )
            return

        if path == "/api/status":
            with PAIRING_LOCK:
                ticket_count = len(PAIRING_TICKETS)
                session_count = len(PAIRING_SESSIONS)
                last_install = dict(LAST_INSTALL_RESULT)
            dynamic_bridge_endpoint = request_bridge_endpoint(self)
            now = now_ms()
            # Pull interval can stretch when device is busy (mic turn/upload), so keep this window relaxed.
            speaker_recent = bool(
                LAST_TTS_PULL_AT_MS
                and (now - LAST_TTS_PULL_AT_MS) <= 120000
                and not is_localhost_ip(LAST_TTS_PULL_IP)
            )
            self._send_json(
                200,
                {
                    "status": "ok",
                    "service": "openclaw-mock",
                    "bridge_endpoint": dynamic_bridge_endpoint,
                    "queue_size": len(QUEUE),
                    "turn_queue_size": TURN_JOB_QUEUE.qsize(),
                    "pairing": {
                        "active_sessions": session_count,
                        "active_tickets": ticket_count,
                        "last_install": last_install,
                    },
                    "dialog": {
                        "target": CURRENT_DIALOG_TARGET or None,
                        "session_id": CURRENT_DIALOG_SESSION_ID or None,
                        "agent": CURRENT_DIALOG_AGENT or None,
                        "timeout_sec": OPENCLAW_DIALOG_TIMEOUT_SEC,
                    },
                    "speaker": {
                        "last_tts_pull_at_ms": LAST_TTS_PULL_AT_MS or None,
                        "last_tts_pull_ip": LAST_TTS_PULL_IP or None,
                        "recently_connected": speaker_recent,
                        "last_pull": LAST_TTS_PULL_METRICS or None,
                    },
                    "dialog_metrics": LAST_DIALOG_METRICS or None,
                    "asr": {
                        "only_mode": ASR_ONLY_MODE,
                    },
                    "capabilities": {
                        "v2_events_stream": True,
                        "v2_events_poll": True,
                        "v2_chat_turn": True,
                        "v2_auth_required": AUTH_REQUIRED_V2,
                    },
                },
            )
            return

        if path == "/asr/events":
            with ASR_EVENTS_LOCK:
                events = list(ASR_EVENTS)
            self._send_json(200, {"ok": True, "asr_only_mode": ASR_ONLY_MODE, "count": len(events), "events": events})
            return

        if path == "/turn/events":
            with TURN_EVENTS_LOCK:
                events = list(TURN_EVENTS)
            self._send_json(200, {"ok": True, "count": len(events), "events": events})
            return

        if path == "/v2/events":
            claims = self._require_v2_auth()
            if claims is None:
                return
            try:
                since_seq = int(str(qs.get("since_seq", ["0"])[0]).strip() or "0")
            except Exception:
                since_seq = 0
            try:
                limit = int(str(qs.get("limit", ["200"])[0]).strip() or "200")
            except Exception:
                limit = 200
            if limit < 1:
                limit = 1
            if limit > 1000:
                limit = 1000
            events = collect_v2_events(since_seq=since_seq, limit=limit)
            last_seq = events[-1].get("event_seq", since_seq) if events else since_seq
            self._send_json(
                200,
                {
                    "ok": True,
                    "since_seq": since_seq,
                    "last_seq": last_seq,
                    "count": len(events),
                    "events": events,
                },
            )
            return

        if path == "/v2/events/stream":
            claims = self._require_v2_auth()
            if claims is None:
                return
            try:
                since_seq = int(str(qs.get("since_seq", ["0"])[0]).strip() or "0")
            except Exception:
                since_seq = 0
            last_event_id = str(self.headers.get("Last-Event-ID", "")).strip()
            if last_event_id.isdigit():
                since_seq = max(since_seq, int(last_event_id))

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            def send_sse(evt: str, data: dict, event_id: int | None = None):
                payload = json.dumps(data, ensure_ascii=False)
                lines = []
                if event_id is not None:
                    lines.append(f"id: {event_id}\n")
                lines.append(f"event: {evt}\n")
                for ln in payload.splitlines():
                    lines.append(f"data: {ln}\n")
                lines.append("\n")
                self.wfile.write("".join(lines).encode("utf-8"))
                self.wfile.flush()

            started_ms = now_ms()
            stream_timeout_ms = 55000
            heartbeat_every_ms = 5000
            next_hb_ms = started_ms + heartbeat_every_ms
            cursor = since_seq

            try:
                bootstrap = collect_v2_events(since_seq=cursor, limit=300)
                for item in bootstrap:
                    eid = int(item.get("event_seq", 0))
                    send_sse("event", item, eid)
                    cursor = max(cursor, eid)

                while (now_ms() - started_ms) < stream_timeout_ms:
                    updates = collect_v2_events(since_seq=cursor, limit=300)
                    if updates:
                        for item in updates:
                            eid = int(item.get("event_seq", 0))
                            send_sse("event", item, eid)
                            cursor = max(cursor, eid)
                    nowv = now_ms()
                    if nowv >= next_hb_ms:
                        send_sse("heartbeat", {"ts_ms": nowv, "last_seq": cursor}, None)
                        next_hb_ms = nowv + heartbeat_every_ms
                    time.sleep(0.5)
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception:
                return
            return

        if path == "/asr/dashboard":
            html = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>SORI ASR Dashboard</title>
<style>
  body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:#0b1220;color:#e5e7eb;padding:20px;max-width:900px;margin:auto}
  .card{background:#111827;border:1px solid #334155;border-radius:14px;padding:14px;margin-bottom:12px}
  h2{margin:0 0 8px 0}
  .muted{color:#9ca3af;font-size:13px}
  .mode{display:inline-block;padding:4px 8px;border-radius:999px;background:#1f2937;border:1px solid #334155;font-size:12px}
  .ok{color:#86efac}
  ul{list-style:none;padding:0;margin:14px 0 0 0}
  li{border-top:1px solid #1f2937;padding:10px 2px}
  .row{display:flex;gap:8px;flex-wrap:wrap;font-size:12px;color:#93c5fd}
  .text{font-size:18px;line-height:1.35;margin-top:4px}
  input,button{font-size:14px}
  input{width:100%;background:#0f172a;border:1px solid #334155;color:#e5e7eb;border-radius:10px;padding:10px}
  button{background:#2563eb;color:#fff;border:0;border-radius:10px;padding:10px 12px;cursor:pointer}
  button:disabled{opacity:.5;cursor:default}
  .state{font-size:13px;color:#cbd5e1;margin-top:8px}
</style></head>
<body>
<div class="card">
  <h2>텍스트 E2E 테스트</h2>
  <div class="muted">텍스트 입력 -> OpenClaw 응답 -> TTS 큐 -> ESP 스피커 pull 확인</div>
  <div style="margin-top:10px"><input id="textInput" value="내일 날씨 알려줘" /></div>
  <div style="margin-top:8px;display:flex;gap:8px">
    <button id="sendBtn" onclick="runTextE2E()">OpenClaw로 테스트</button>
  </div>
  <div id="e2eState" class="state">대기 중</div>
  <div id="e2eReply" class="state"></div>
</div>
<div class="card">
  <h2>ASR 실시간 대시보드</h2>
  <div class="muted">1단계 검증 전용. ASR_ONLY_MODE=1이면 OpenClaw/TTS를 건너뜁니다.</div>
  <div style="margin-top:10px" id="mode" class="mode">mode</div>
  <ul id="list"></ul>
</div>
<div class="card">
  <h2>Turn 타임라인</h2>
  <div class="muted">최근 turn 처리 단계와 상태를 보여줍니다.</div>
  <ul id="turnList"></ul>
</div>
<script>
let pendingQueuedId = '';
let pendingStartedAt = 0;
let polling = false;

function setE2EState(msg){
  document.getElementById('e2eState').textContent = msg;
}

async function runTextE2E(){
  const btn = document.getElementById('sendBtn');
  const text = (document.getElementById('textInput').value || '').trim();
  const replyEl = document.getElementById('e2eReply');
  replyEl.textContent = '';
  if(!text){
    setE2EState('텍스트를 입력해 주세요.');
    return;
  }
  btn.disabled = true;
  setE2EState('OpenClaw 요청 중...');
  try{
    const r = await fetch('/dialog/turn', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({asr_text:text, skip_openclaw:false, timeout_sec:12})
    });
    const j = await r.json();
    if(!r.ok){
      setE2EState('요청 실패: ' + (j.detail || j.error || r.status));
      btn.disabled = false;
      return;
    }
    pendingQueuedId = String(j.id || '');
    pendingStartedAt = Date.now();
    replyEl.textContent = '응답: ' + (j.reply_text || '');
    setE2EState('큐 적재 완료(id=' + pendingQueuedId + '). 스피커 pull 대기...');
    if(!polling){
      polling = true;
      monitorPull();
    }
  }catch(e){
    setE2EState('네트워크 오류: ' + e);
    btn.disabled = false;
  }
}

async function monitorPull(){
  while(polling){
    try{
      const r = await fetch('/api/status', {cache:'no-store'});
      const j = await r.json();
      const lp = (j.speaker || {}).last_pull || {};
      const pulledId = String(lp.id || '');
      if(pendingQueuedId && pulledId === pendingQueuedId){
        const elapsed = Date.now() - pendingStartedAt;
        setE2EState('재생 요청 확인 완료: id=' + pulledId + ' (' + elapsed + 'ms)');
        document.getElementById('sendBtn').disabled = false;
        pendingQueuedId = '';
        polling = false;
        break;
      }
      if(pendingQueuedId && (Date.now() - pendingStartedAt) > 30000){
        setE2EState('30초 내 스피커 pull 확인 실패. 브릿지/ESP 상태 확인 필요');
        document.getElementById('sendBtn').disabled = false;
        pendingQueuedId = '';
        polling = false;
        break;
      }
    }catch(_){}
    await new Promise(res => setTimeout(res, 700));
  }
}

async function tick(){
  try{
    const r = await fetch('/asr/events', {cache:'no-store'});
    const j = await r.json();
    document.getElementById('mode').textContent = j.asr_only_mode ? 'ASR ONLY ON' : 'ASR ONLY OFF';
    const items = (j.events || []).slice().reverse();
    const html = items.map(e => `
      <li>
        <div class="row"><span>${new Date(e.ts_ms).toLocaleTimeString()}</span><span>id=${e.req_id||'-'}</span><span>lat=${e.stt_ms||0}ms</span><span>bytes=${e.bytes||0}</span><span>status=${e.status||'ok'}</span></div>
        <div class="text">${(e.text||'').replaceAll('<','&lt;')}</div>
      </li>
    `).join('');
    document.getElementById('list').innerHTML = html || '<li class="muted">아직 수신된 ASR 이벤트가 없습니다.</li>';
  }catch(_){}
  try{
    const r2 = await fetch('/turn/events', {cache:'no-store'});
    const j2 = await r2.json();
    const items2 = (j2.events || []).slice().reverse().slice(0, 20);
    const html2 = items2.map(e => `
      <li>
        <div class="row"><span>${new Date(e.ts_ms || Date.now()).toLocaleTimeString()}</span><span>turn=${e.turn_id||'-'}</span><span>req=${e.req_id||'-'}</span><span>${e.event||'-'}</span><span>status=${e.status||'-'}</span></div>
        <div class="text">${(e.error||'').replaceAll('<','&lt;')}</div>
      </li>
    `).join('');
    document.getElementById('turnList').innerHTML = html2 || '<li class="muted">아직 turn 이벤트가 없습니다.</li>';
  }catch(_){}
}
setInterval(tick, 700);
tick();
</script>
</body></html>"""
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/installer/status":
            st = installer_status()
            code = 200 if st.get("ok") else 503
            self._send_json(code, st)
            return

        if path == "/installer/instructions":
            code = str(qs.get("pairingCode", [""])[0]).strip().upper()
            if not code:
                self._send_json(400, {"error": "bad_request", "detail": "pairingCode required"})
                return
            bridge_host = request_bridge_host_port(self)[0]
            bridge_base = request_bridge_endpoint(self)
            installer_url = INSTALLER_BOOTSTRAP_URL or f"{bridge_base}/installer/agent.py"
            model_arg = f" --openclaw-model {OPENCLAW_BOOTSTRAP_MODEL}" if OPENCLAW_BOOTSTRAP_MODEL else ""
            cmd = (
                "bash -lc '"
                "set -e; "
                "TMP_DIR=$(mktemp -d); "
                f"curl -fsSL {installer_url} -o \"$TMP_DIR/sori_agent.py\"; "
                f"python3 \"$TMP_DIR/sori_agent.py\" install --pairing-code {code} --bridge-port {PORT} --public-host {bridge_host} --tts-engine {TTS_ENGINE} --openclaw-agent {OPENCLAW_DEFAULT_AGENT}{model_arg} --openclaw-thinking {OPENCLAW_THINKING_LEVEL or 'minimal'} --installer-bootstrap-url {installer_url}"
                "'"
            )
            notes = "Run this on the Mac where OpenClaw is installed."
            if INSTALLER_BOOTSTRAP_URL:
                notes += " Installer is fetched from INSTALLER_BOOTSTRAP_URL."
            else:
                notes += " Installer is fetched from bridge URL (development fallback)."
            self._send_json(
                200,
                {
                    "ok": True,
                    "pairingCode": code,
                    "command": cmd,
                    "installer_url": installer_url,
                    "notes": notes,
                },
            )
            return

        if path == "/installer/agent.py":
            if not os.path.exists(SORI_AGENT_SCRIPT):
                self._send_json(404, {"error": "not_found", "detail": "sori_agent.py not found"})
                return
            with open(SORI_AGENT_SCRIPT, "rb") as fp:
                body = fp.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/x-python; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/discover/device":
            client_ip = self.client_address[0] if self.client_address else ""
            ip, source = discover_esp_device_ip(client_ip)
            if not ip:
                self._send_json(
                    404,
                    {
                        "ok": False,
                        "error": "not_found",
                        "detail": "ESP32 device API not found on local subnet",
                        "source": source,
                    },
                )
                return
            self._send_json(
                200,
                {
                    "ok": True,
                    "ip": ip,
                    "device_api_base_url": f"http://{ip}:18991",
                    "source": source,
                },
            )
            return

        if path == "/pairing/session-status":
            code = str(qs.get("pairingCode", [""])[0]).strip().upper()
            if not code:
                self._send_json(400, {"error": "bad_request", "detail": "pairingCode required"})
                return
            with PAIRING_LOCK:
                session = PAIRING_SESSIONS.get(code)
            if session is None:
                self._send_json(404, {"error": "not_found", "detail": "pairingCode not found"})
                return
            self._send_json(
                200,
                {
                    "pairingCode": code,
                    "status": session.get("status", "pending"),
                    "bridge_endpoint": request_bridge_endpoint(self),
                    "dialog": {
                        "target": CURRENT_DIALOG_TARGET or None,
                        "session_id": CURRENT_DIALOG_SESSION_ID or None,
                        "agent": CURRENT_DIALOG_AGENT or None,
                    },
                    "updated_at_ms": session.get("updated_at_ms", 0),
                },
            )
            return

        if path == "/pairing/activate":
            code = str(qs.get("pairingCode", [""])[0]).strip().upper()
            target = str(qs.get("to", [""])[0]).strip()
            session_id = str(qs.get("session_id", [""])[0]).strip()
            agent = str(qs.get("agent", [""])[0]).strip()
            if not code:
                self._send_json(400, {"error": "bad_request", "detail": "pairingCode required"})
                return
            with PAIRING_LOCK:
                session = PAIRING_SESSIONS.get(code)
                if session is None:
                    self._send_json(404, {"error": "not_found", "detail": "pairingCode not found"})
                    return
                session["status"] = "confirmed"
                session["updated_at_ms"] = now_ms()
            if target:
                CURRENT_DIALOG_TARGET = target
            if session_id:
                CURRENT_DIALOG_SESSION_ID = session_id
            if agent:
                CURRENT_DIALOG_AGENT = agent
            route_ok, route_source = ensure_dialog_route()
            save_dialog_route_state()
            dialog_ready = bool(CURRENT_DIALOG_TARGET or CURRENT_DIALOG_SESSION_ID or CURRENT_DIALOG_AGENT)
            self._send_json(
                200,
                {
                    "ok": True,
                    "pairingCode": code,
                    "status": "confirmed",
                    "dialog_ready": dialog_ready,
                    "warning": None if dialog_ready else "OpenClaw target is not configured yet. Set to/session_id/agent before dialog turn.",
                    "route_source": route_source if route_ok else None,
                    "dialog": {
                        "target": CURRENT_DIALOG_TARGET or None,
                        "session_id": CURRENT_DIALOG_SESSION_ID or None,
                        "agent": CURRENT_DIALOG_AGENT or None,
                    },
                },
            )
            return

        if path == "/pairing/portal":
            html = f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>SORI Pairing Portal</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;padding:20px;max-width:560px;margin:auto;background:#0f172a;color:#e2e8f0}}
  .card{{background:#111827;border:1px solid #334155;border-radius:14px;padding:16px;box-shadow:0 4px 20px rgba(0,0,0,.18)}}
  h2{{margin:0 0 8px 0;font-size:24px}}
  p{{margin:0 0 14px 0;color:#cbd5e1;line-height:1.45}}
  label{{display:block;font-size:13px;color:#cbd5e1;margin-top:10px}}
  input{{width:100%;padding:10px;border-radius:10px;border:1px solid #334155;background:#0b1220;color:#fff;margin-top:6px;box-sizing:border-box}}
  input:focus{{outline:none;border-color:#60a5fa;box-shadow:0 0 0 3px rgba(96,165,250,.15)}}
  button{{margin-top:14px;width:100%;padding:12px;border:0;border-radius:10px;background:#2563eb;color:#fff;font-weight:700;cursor:pointer}}
  button[disabled]{{opacity:.55;cursor:not-allowed}}
  .success{{background:#16a34a}}
  .status{{margin-top:14px;border-radius:10px;padding:12px;font-size:14px;display:none}}
  .status.ok{{display:block;background:#052e16;color:#bbf7d0;border:1px solid #14532d}}
  .status.err{{display:block;background:#450a0a;color:#fecaca;border:1px solid #7f1d1d}}
  .hint{{margin-top:8px;color:#93c5fd;font-size:12px}}
</style></head>
<body>
<div class="card">
<h2>SORI 페어링</h2>
<p>앱의 6자리 코드를 입력하고 연결을 확정하세요.</p>
<p class="hint">네트워크 안내: ESP32는 2.4GHz만 지원합니다. 맥/폰도 같은 로컬망(가능하면 동일 2.4GHz)으로 맞춰주세요.</p>
<label>Pairing Code</label><input id="code" placeholder="ABC123" maxlength="6" inputmode="latin" autocapitalize="characters" pattern="[A-Z0-9]{{6}}" />
<button id="submitBtn" onclick="submitPair()">연결 확정</button>
<div id="status" class="status"></div>
</div>
<script>
const codeEl = document.getElementById('code');
const submitBtn = document.getElementById('submitBtn');
const statusEl = document.getElementById('status');
codeEl.addEventListener('input', () => {{
  const normalized = codeEl.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
  if (codeEl.value !== normalized) codeEl.value = normalized;
}});
function setStatus(type, text){{
  statusEl.className = 'status ' + type;
  statusEl.textContent = text;
}}
async function submitPair(){{
  const code = codeEl.value.trim().toUpperCase();
  if (!/^[A-Z0-9]{{6}}$/.test(code)) {{
    setStatus('err', '코드는 영문 대문자/숫자 6자리여야 합니다.');
    return;
  }}
  submitBtn.disabled = true;
  setStatus('ok', '연결 요청 중...');
  const q=new URLSearchParams({{
    pairingCode:code,
    agent:'{OPENCLAW_DEFAULT_AGENT}',
  }});
  try {{
    const r=await fetch('/pairing/activate?'+q.toString());
    const j=await r.json();
    if(!r.ok){{
      setStatus('err', '연결 실패: ' + (j.detail || '요청을 확인해 주세요.'));
      submitBtn.disabled = false;
      return;
    }}
    setStatus('ok', '연결 요청 완료. 앱으로 돌아가 연결을 마무리해 주세요.');
    await new Promise((resolve) => setTimeout(resolve, 400));
    const s = await fetch('/pairing/session-status?pairingCode=' + encodeURIComponent(code));
    const sj = await s.json();
    const target = sj?.dialog?.target || sj?.dialog?.session_id || sj?.dialog?.agent;
    if (target) {{
      setStatus('ok', 'OpenClaw 연결 요청이 확인됐어요. 이제 앱으로 돌아가 다음 단계로 진행해 주세요.');
    }} else {{
      setStatus('ok', '연결은 확정됐지만 OpenClaw 대상은 아직 없습니다. 앱 안내에 따라 target을 설정하세요.');
    }}
    submitBtn.classList.add('success');
    submitBtn.textContent = '연결 요청 완료';
    submitBtn.disabled = true;
  }} catch (e) {{
    setStatus('err', '네트워크 오류로 연결에 실패했습니다.');
    submitBtn.disabled = false;
  }}
}}
</script></body></html>"""
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/tts/test.wav":
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(TEST_WAV)))
            self.end_headers()
            self.wfile.write(TEST_WAV)
            return

        if path in ("/tts/next", "/tts/pull"):
            LAST_TTS_PULL_AT_MS = now_ms()
            LAST_TTS_PULL_IP = self.client_address[0]
            if not QUEUE:
                print(f"[tts] pull empty path={path} from {self.client_address[0]}", flush=True)
                self.send_response(204)
                self.end_headers()
                return
            item = QUEUE.popleft()
            queue_wait_ms = max(0, LAST_TTS_PULL_AT_MS - int(item.get("created_at_ms", LAST_TTS_PULL_AT_MS)))
            LAST_TTS_PULL_METRICS = {
                "id": item["id"],
                "path": path,
                "queue_wait_ms": queue_wait_ms,
                "pulled_at_ms": LAST_TTS_PULL_AT_MS,
                "client_ip": LAST_TTS_PULL_IP,
                "queue_size_after_pull": len(QUEUE),
            }
            print(
                f"[tts] pull id={item['id']} path={path} wait_ms={queue_wait_ms} from {self.client_address[0]}",
                flush=True,
            )
            self._send_json(
                200,
                {
                    "id": item["id"],
                    "wav_url": f"{request_bridge_endpoint(self)}/tts/item/{item['id']}.wav",
                },
            )
            return

        if path.startswith("/tts/item/") and path.endswith(".wav"):
            item_id = path[len("/tts/item/") : -len(".wav")]
            wav = WAV_STORE.get(item_id)
            if wav is None:
                self._send_json(404, {"error": "not_found", "item_id": item_id})
                return
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.end_headers()
            self.wfile.write(wav)
            return

        if path == "/tts/render":
            text = qs.get("text", [""])[0]
            item = enqueue_tts(text)
            self._send_json(
                200,
                {
                    "queued": True,
                    "id": item["id"],
                    "wav_url": f"{request_bridge_endpoint(self)}/tts/item/{item['id']}.wav",
                },
            )
            return

        self._send_json(404, {"error": "not_found", "path": self.path})

    def do_POST(self):
        global ASR_ONLY_MODE
        parsed = urlparse(self.path)
        purge_expired_pairing_state()
        if parsed.path == "/asr/events/clear":
            with ASR_EVENTS_LOCK:
                ASR_EVENTS.clear()
            self._send_json(200, {"ok": True, "cleared": True, "count": 0})
            return
        if parsed.path == "/asr/mode":
            try:
                payload = self._read_json()
                ASR_ONLY_MODE = bool(payload.get("asr_only", False))
                self._send_json(200, {"ok": True, "asr_only_mode": ASR_ONLY_MODE})
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/v2/auth/token":
            try:
                payload = self._read_json()
                code = str(payload.get("pairingCode", "")).strip().upper()
                subject = str(payload.get("deviceId", "")).strip() or str(payload.get("hostId", "")).strip()
                ttl_sec = int(payload.get("ttlSec", JWT_DEFAULT_TTL_SEC))
                if not code or not subject:
                    self._send_json(400, {"error": "bad_request", "detail": "pairingCode/deviceId required"})
                    return
                with PAIRING_LOCK:
                    session = PAIRING_SESSIONS.get(code)
                if not session or session.get("status") != "confirmed":
                    self._send_json(401, {"error": "unauthorized", "detail": "pairing_not_confirmed"})
                    return
                token, ttl = issue_access_token(code, subject, ttl_sec)
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "token_type": "Bearer",
                        "access_token": token,
                        "expires_in": ttl,
                    },
                )
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/pairing/session":
            try:
                payload = self._read_json()
                device_id = str(payload.get("deviceId", "")).strip()
                app_nonce = str(payload.get("appNonce", "")).strip()
                if not device_id or not app_nonce:
                    self._send_json(400, {"error": "bad_request", "detail": "deviceId/appNonce required"})
                    return
                code = create_pairing_code()
                expires_at_ms = now_ms() + (PAIRING_TTL_SEC * 1000)
                with PAIRING_LOCK:
                    PAIRING_SESSIONS[code] = {
                        "device_id": device_id,
                        "app_nonce": app_nonce,
                        "expires_at_ms": expires_at_ms,
                        "status": "pending",
                        "updated_at_ms": now_ms(),
                    }
                self._send_json(200, {"pairingCode": code, "expiresInSec": PAIRING_TTL_SEC})
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/pairing/confirm":
            try:
                payload = self._read_json()
                code = str(payload.get("pairingCode", "")).strip().upper()
                host_id = str(payload.get("hostId", "")).strip()
                agent_version = str(payload.get("agentVersion", "")).strip()
                if not code or not host_id or not agent_version:
                    self._send_json(400, {"error": "bad_request", "detail": "pairingCode/hostId/agentVersion required"})
                    return
                with PAIRING_LOCK:
                    session = PAIRING_SESSIONS.get(code)
                    if session is None:
                        self._send_json(404, {"error": "not_found", "detail": "pairingCode not found"})
                        return
                    install_ticket = secrets.token_urlsafe(24)
                    PAIRING_TICKETS[install_ticket] = {
                        "pairing_code": code,
                        "host_id": host_id,
                        "agent_version": agent_version,
                        "expires_at_ms": now_ms() + (PAIRING_TTL_SEC * 1000),
                    }
                self._send_json(
                    200,
                    {
                        "installTicket": install_ticket,
                        "bridgeConfig": {
                            "host": request_bridge_host_port(self)[0],
                            "port": request_bridge_host_port(self)[1],
                        },
                    },
                )
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/pairing/install-result":
            try:
                payload = self._read_json()
                install_ticket = str(payload.get("installTicket", "")).strip()
                status = str(payload.get("status", "")).strip().lower()
                bridge_endpoint = str(payload.get("bridgeEndpoint", "")).strip()
                reason = str(payload.get("reason", "")).strip()
                if not install_ticket or status not in ("ok", "failed"):
                    self._send_json(400, {"error": "bad_request", "detail": "installTicket/status required"})
                    return

                global CURRENT_BRIDGE_ENDPOINT, LAST_INSTALL_RESULT
                with PAIRING_LOCK:
                    if install_ticket not in PAIRING_TICKETS:
                        self._send_json(404, {"error": "not_found", "detail": "installTicket not found"})
                        return
                    if status == "ok" and bridge_endpoint:
                        CURRENT_BRIDGE_ENDPOINT = bridge_endpoint
                    LAST_INSTALL_RESULT = {
                        "status": status,
                        "reason": reason,
                        "bridge_endpoint": bridge_endpoint or CURRENT_BRIDGE_ENDPOINT,
                        "updated_at_ms": now_ms(),
                    }
                self._send_json(200, {"accepted": True})
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/tts/push":
            try:
                payload = self._read_json()
                text = str(payload.get("text", "")).strip()
                item = enqueue_tts(text)
                self._send_json(
                    200,
                    {
                        "queued": True,
                        "id": item["id"],
                        "wav_url": f"{request_bridge_endpoint(self)}/tts/item/{item['id']}.wav",
                    },
                )
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/tts/clear":
            try:
                cleared = len(QUEUE)
                QUEUE.clear()
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "cleared": cleared,
                        "wav_store_size": len(WAV_STORE),
                    },
                )
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/v2/chat/turn":
            claims = self._require_v2_auth()
            if claims is None:
                return
            try:
                payload = self._read_json()
                result = execute_dialog_turn(
                    asr_text=str(payload.get("asr_text", "")).strip(),
                    skip_openclaw=bool(payload.get("skip_openclaw", False)),
                    to=str(payload.get("to", "")).strip(),
                    session_id=str(payload.get("session_id", "")).strip(),
                    agent=str(payload.get("agent", "")).strip(),
                    timeout_sec=int(payload.get("timeout_sec", OPENCLAW_DIALOG_TIMEOUT_SEC)),
                )
                result["wav_url"] = f"{request_bridge_endpoint(self)}/tts/item/{result['id']}.wav"
                self._send_json(200, result)
                return
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or str(exc)).strip()
                self._send_json(502, {"error": "openclaw_failed", "detail": detail[:400]})
                return
            except RuntimeError as exc:
                detail = str(exc)
                if detail.startswith("stt_timeout_"):
                    self._send_json(429, {"error": "busy", "detail": "stt_timeout_retry"})
                    return
                self._send_json(400, {"error": "bad_request", "detail": detail})
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/dialog/turn":
            try:
                payload = self._read_json()
                result = execute_dialog_turn(
                    asr_text=str(payload.get("asr_text", "")).strip(),
                    skip_openclaw=bool(payload.get("skip_openclaw", False)),
                    to=str(payload.get("to", "")).strip(),
                    session_id=str(payload.get("session_id", "")).strip(),
                    agent=str(payload.get("agent", "")).strip(),
                    timeout_sec=int(payload.get("timeout_sec", OPENCLAW_DIALOG_TIMEOUT_SEC)),
                )
                result["wav_url"] = f"{request_bridge_endpoint(self)}/tts/item/{result['id']}.wav"
                self._send_json(200, result)
                return
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or str(exc)).strip()
                self._send_json(502, {"error": "openclaw_failed", "detail": detail[:400]})
                return
            except RuntimeError as exc:
                detail = str(exc)
                if detail.startswith("stt_timeout_"):
                    self._send_json(429, {"error": "busy", "detail": "stt_timeout_retry"})
                    return
                self._send_json(400, {"error": "bad_request", "detail": detail})
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        if parsed.path == "/asr/push":
            try:
                qs = parse_qs(parsed.query)
                asr_only = ASR_ONLY_MODE or (str(qs.get("asr_only", ["false"])[0]).lower() in ("1", "true", "yes"))
                content_len = int(self.headers.get("Content-Length", "0"))
                if content_len <= 0:
                    self._send_json(400, {"error": "bad_request", "detail": "audio body required"})
                    return
                if content_len > 2_000_000:
                    self._send_json(400, {"error": "bad_request", "detail": "audio too large"})
                    return
                wav_bytes = self.rfile.read(content_len)
                if not wav_bytes or len(wav_bytes) < 44:
                    self._send_json(400, {"error": "bad_request", "detail": "invalid wav payload"})
                    return
                asr_req_id = secrets.token_hex(4)
                turn_id = str(self.headers.get("X-Turn-Id", "")).strip() or asr_req_id
                print(
                    f"[asr:recv] req_id={asr_req_id} turn_id={turn_id} bytes={len(wav_bytes)} remote={self.client_address[0]}",
                    flush=True,
                )
                push_asr_event(
                    {
                        "ts_ms": now_ms(),
                        "turn_id": turn_id,
                        "req_id": asr_req_id,
                        "bytes": len(wav_bytes),
                        "status": "recv",
                        "text": "",
                        "stt_ms": 0,
                    }
                )

                done_evt = threading.Event()
                result_ref: dict = {}
                try:
                    TURN_JOB_QUEUE.put_nowait(
                        {
                            "turn_id": turn_id,
                            "req_id": asr_req_id,
                            "wav_bytes": wav_bytes,
                            "asr_only": asr_only,
                            "skip_openclaw": str(qs.get("skip_openclaw", ["false"])[0]).lower() in ("1", "true", "yes"),
                            "to": str(qs.get("to", [""])[0]).strip(),
                            "session_id": str(qs.get("session_id", [""])[0]).strip(),
                            "agent": str(qs.get("agent", [""])[0]).strip(),
                            "timeout_sec": int(qs.get("timeout_sec", [str(OPENCLAW_DIALOG_TIMEOUT_SEC)])[0]),
                            "done_evt": done_evt,
                            "result_ref": result_ref,
                        }
                    )
                except queue.Full:
                    print(f"[asr:busy] req_id={asr_req_id} drop=1 reason=turn_queue_full", flush=True)
                    push_asr_event(
                        {
                            "ts_ms": now_ms(),
                            "turn_id": turn_id,
                            "req_id": asr_req_id,
                            "bytes": len(wav_bytes),
                            "status": "busy",
                            "text": "turn_queue_full",
                            "stt_ms": 0,
                        }
                    )
                    self._send_json(429, {"error": "busy", "detail": "turn_queue_full"})
                    return

                if not done_evt.wait(timeout=max(5, ASR_TURN_WAIT_SEC)):
                    push_asr_event(
                        {
                            "ts_ms": now_ms(),
                            "turn_id": turn_id,
                            "req_id": asr_req_id,
                            "bytes": len(wav_bytes),
                            "status": "busy",
                            "text": "turn_timeout_waiting_worker",
                            "stt_ms": 0,
                        }
                    )
                    self._send_json(429, {"error": "busy", "detail": "turn_timeout_waiting_worker"})
                    return

                if result_ref.get("ok"):
                    result = dict(result_ref.get("result") or {})
                    if result.get("id"):
                        result["wav_url"] = f"{request_bridge_endpoint(self)}/tts/item/{result['id']}.wav"
                    self._send_json(200, result)
                    return
                err = result_ref.get("error")
                if isinstance(err, subprocess.CalledProcessError):
                    detail = (err.stderr or str(err)).strip()
                    self._send_json(502, {"error": "openclaw_failed", "detail": detail[:400]})
                    return
                if isinstance(err, RuntimeError):
                    detail = str(err)
                    if detail.startswith("stt_timeout_"):
                        self._send_json(429, {"error": "busy", "detail": "stt_timeout_retry"})
                        return
                    self._send_json(400, {"error": "bad_request", "detail": detail})
                    return
                self._send_json(400, {"error": "bad_request", "detail": str(err)[:400] if err else "unknown"})
                return
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or str(exc)).strip()
                self._send_json(502, {"error": "openclaw_failed", "detail": detail[:400]})
                return
            except Exception as exc:
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return

        self._send_json(404, {"error": "not_found", "path": self.path})

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    try:
        INSTANCE_LOCK_HANDLE = acquire_instance_lock(PORT)
    except RuntimeError as exc:
        print(f"[bridge] {exc}", flush=True)
        raise SystemExit(0)
    load_dialog_route_state()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    threading.Thread(target=bridge_log_writer, daemon=True, name="bridge-log-writer").start()
    threading.Thread(target=turn_job_worker, daemon=True, name="turn-job-worker").start()
    print(
        f"[tts] config engine={TTS_ENGINE} voice={VOICE} xtts_speaker={XTTS_SPEAKER_WAV or '-'}",
        flush=True,
    )
    print(f"OpenClaw mock server listening on http://{HOST}:{PORT} public_host={PUBLIC_HOST}")
    threading.Thread(target=warmup_stt_runtime, daemon=True, name="stt-warmup").start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[bridge] shutdown requested", flush=True)
    finally:
        server.server_close()
