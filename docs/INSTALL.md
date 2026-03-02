# INSTALL

## 1) 릴리스 URL 고정
`INSTALLER_BOOTSTRAP_URL`을 GitHub Release의 태그 고정 URL로 설정한다.

예시:
`https://github.com/<org>/talk-to-openclaw-installer/releases/download/v1.0.0/sori_agent.py`

## 2) 설치 실행
```bash
PAIRING_CODE=<6자리코드> \
PUBLIC_HOST=<맥IP> \
BRIDGE_PORT=18890 \
TTS_ENGINE=edge \
bash installer/install.sh
```

## 3) 상태 확인
```bash
python3 installer/sori_agent.py status
curl -sS http://127.0.0.1:18890/health
```
