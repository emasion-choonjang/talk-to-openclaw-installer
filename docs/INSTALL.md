# INSTALL

## 1) stable manifest 조회
앱/포털은 먼저 `stable.json`을 조회합니다.

예시:
```json
{
  "version": "1.0.12",
  "asset_url": "https://github.com/<org>/talk-to-openclaw-installer/releases/download/v1.0.12/sori-bridge-macos-arm64.tar.gz",
  "sha256": "<sha256>",
  "install_script_url": "https://github.com/<org>/talk-to-openclaw-installer/releases/download/v1.0.12/install.sh"
}
```

## 2) binary 설치 실행
```bash
ASSET_URL=<stable.json의 asset_url> \
ASSET_SHA256=<stable.json의 sha256> \
PUBLIC_HOST=<맥IP> \
BRIDGE_PORT=18890 \
TTS_ENGINE=edge \
bash installer/install.sh
```

## 3) 결과
- `~/Library/Application Support/SORI/bridge/releases/<version>/` 압축 해제
- `~/Library/Application Support/SORI/bridge/current` 심볼릭 링크 갱신
- `~/Library/LaunchAgents/ai.sori.bridge.plist` 생성/갱신
- `launchctl bootstrap` / `kickstart`

## 4) 상태 확인
```bash
launchctl print gui/$(id -u)/ai.sori.bridge
curl -sS http://127.0.0.1:18890/health
```
