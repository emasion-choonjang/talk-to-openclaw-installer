# talk-to-openclaw-installer

SORI/OpenClaw 브릿지의 macOS 설치 부트스트랩 전용 리포지토리.

## Why separate repo?
- 첫 설치 시 브릿지 서버가 아직 없기 때문에, 외부 고정 URL에서 설치 스크립트를 받아야 함
- 버전 고정/롤백/감사 이력 관리가 쉬움

## Quick Start
```bash
PAIRING_CODE=ABC123 \
PUBLIC_HOST=192.168.0.10 \
BRIDGE_PORT=18890 \
TTS_ENGINE=edge \
bash installer/install.sh
```

## Release assets
- `sori_agent.py`
- `install.sh`
- `SHA256SUMS`

## 운영 원칙
- `latest` URL 사용 금지 (버전 태그 고정)
- 가능하면 `EXPECTED_SHA256` 검증 사용
- 설치 실패 시 이전 태그로 즉시 롤백
