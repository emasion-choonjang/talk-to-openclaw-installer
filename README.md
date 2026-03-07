# talk-to-openclaw-installer

SORI/OpenClaw 브릿지의 macOS Apple Silicon 배포용 저장소입니다.

## Target
- macOS Apple Silicon only
- user-space install only
- OpenClaw는 로컬 설치 상태를 가정

## Distribution model
- 앱과 포털은 직접 `latest` 자산을 실행하지 않습니다.
- 먼저 `stable.json`을 조회한 뒤, 그 manifest가 지정한 pinned version asset을 설치합니다.

## Release assets
- `sori-bridge-macos-arm64.tar.gz`
- `sori-bridge-macos-arm64.sha256`
- `stable.json`
- `install.sh`
- `SHA256SUMS`

## Install modes
### Binary-first
```bash
ASSET_URL=<stable.json의 asset_url> \
ASSET_SHA256=<stable.json의 sha256> \
PUBLIC_HOST=<mac-ip> \
BRIDGE_PORT=18890 \
TTS_ENGINE=edge \
bash installer/install.sh
```

### Legacy fallback
```bash
PAIRING_CODE=ABC123 \
PUBLIC_HOST=<mac-ip> \
BRIDGE_PORT=18890 \
TTS_ENGINE=edge \
bash installer/install.sh
```

## Operations rules
- `latest` 직접 실행 금지
- manifest가 내려준 pinned version만 설치
- SHA256 검증 필수
- 실패 시 `current` 링크를 직전 버전으로 되돌릴 수 있어야 함
