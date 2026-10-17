# 작업 인계 — 2026-10-16 (한국 시간, 초기 구성 스냅샷)

## 세션 목표와 중단 상태

사용자 요청: PSP 액션 게임 `Clank & Ratchet - Maruhi Mission Ignition` 폴더에서 일본판 원본을 기준으로 한글판의 번역을 업데이트하기 위해 먼저 프로젝트 폴더를 구성하고, 작업 후에는 항상 인계 문서를 업데이트할 것.

이 초기 스냅샷에서는 **표준 폴더 구조 생성, 지속 인계 규칙(`AGENTS.md`) 수립, 일본판(`UCJS10084`)·한국판(`UCKS45096`) 원본 ISO 보존 및 SHA-256 등록, ISO9660 전체 파일 인벤토리 비교, 초기 메타데이터·시스템·HUD 로컬 데이터 추출**까지 완료한 시점을 기록한다.

## 보존 원본과 산출물

| 구분 | 디스크 ID / 버전 | 보존 경로 | 크기 (bytes) | SHA-256 |
|---|---|---|---:|---|
| 일본판 원본 (`ja`) | `UCJS10084` / `1.00` | `original/iso/Clank & Ratchet - Maruhi Mission Ignition! (Japan).iso` | 1,115,258,880 | `6ebeaa0021e40b9b150725deb18caeedca7d42b9c0330287ff18e9981c7ea647` |
| 한국판 기준 (`ko`) | `UCKS45096` / `1.00` | `original/iso/Secret Agent Clank [K].iso` | 1,222,705,152 | `f0d5a191bdbf2fc05b403b065cbbb867a8974dd89686b3deb8a0d69601391007` |

- 루트에 제공된 최초 ISO 2종을 삭제하거나 수정하지 않고 그대로 유지했으며, `original/iso/`에 하드링크 보존본을 구성해 두 경로의 크기와 SHA-256 일치를 검증했다.
- ISO9660 정적 비교 요약 (`qa/reports/source_survey.json`):
  - 일본판 파일 총 **834개**, 한국판 파일 총 **829개**, 공통 경로 **820개** (SHA-256 동일 **291개**, 상이 **529개**).
  - 언어별 고유 HUD 로컬 데이터 확인:
    - 일본판 전용: `PSP_GAME/USRDIR/DATA/HUD/LOCALDAT_J.BIN` (185,200 bytes), `HELPLOCALDAT_J.BIN` (43,360 bytes)
    - 한국판 전용: `PSP_GAME/USRDIR/DATA/HUD/LOCALDAT_K.BIN` (157,320 bytes), `HELPLOCALDAT_K.BIN` (34,992 bytes)
- 초기 추출 완료 (`extracted/disc_ja/`, `extracted/disc_ko/`):
  - 양쪽 디스크의 `UMD_DATA.BIN`, `PSP_GAME/PARAM.SFO`, `PSP_GAME/ICON0.PNG`, `PSP_GAME/SYSDIR/*` (`BOOT.BIN`, `EBOOT.BIN`), `PSP_GAME/USRDIR/DATA/HUD/*` 각 18개 파일(총 36개)을 추출하고 원본 extent SHA-256과 대조했다.
- `extracted/text/`, `workspace/analysis/`, `workspace/translation/`, `workspace/font/`, `workspace/graphics/`, `config/`, `build/`, `dist/`, `qa/screenshots/` 폴더를 역할별로 생성했다.

