# Clank & Ratchet / Secret Agent Clank PSP 한글 번역 업데이트 작업 규칙

- 대상은 PSP 액션 게임 **클랭크 & 라쳇: 비밀 미션 이그니션 / 시크릿 에이전트 클랭크**다.
  - 일본판 원본 참조 디스크(`ja`): `UCJS10084` v1.00 (`Clank & Ratchet - Maruhi Mission Ignition! (Japan).iso`)
  - 한국어판 패치 기준 디스크(`ko`): `UCKS45096` v1.00 (`Secret Agent Clank [K].iso`)
- 시작점은 `docs/HANDOFF.md`와 `manifests/sources.json`이다.
- **사용자가 요청한 지속 규칙: 작업 세션을 마칠 때마다 항상 인계 문서를 업데이트한다.**
  - 한국 시간 기준 `docs/HANDOFF_YYYY-MM-DD.md`를 작성·갱신하고 `docs/HANDOFF.md`의 최신 포인터와 요약을 함께 갱신한다.
  - 같은 날 후속 세션은 기존 기록을 `docs/archive/`에 백업하거나 세션 섹션을 누적 보존하며, 이전 검증 산출물을 덮어쓰지 않는다.
  - 인계 문서에는 변경·추가 파일, 원본/산출물 해시(SHA-256), 재현 명령, 검증 결과(정적 분석 / 빌드·패치 / 에뮬레이터 런타임 / 실제 화면·전체 플레이 구분), 미확정 항목, 그리고 **정확한 다음 행동 하나**를 명시한다.
- 루트의 최초 제공 ISO 2종과 `original/iso/` 보존본을 수정하거나 삭제하지 않는다. 작업 시작 전 `python -B scripts/survey.py --verify-source-only`로 양쪽 원본 ISO의 크기와 SHA-256을 검증한다.
- `extracted/`는 재생성 가능한 원본 추출물 전용이다. 일본판(`ja`)과 한국어판(`ko`) 대조 결과 및 번역 업데이트 SSOT는 `workspace/translation/`에 별도로 관리한다.
- 텍스트/자산 패치를 만들기 전 반드시 컨테이너(`LOCALDAT_*.BIN`, `HELPLOCALDAT_*.BIN`, `.WAD` 등)의 무변경 바이트 왕복(round-trip) 일치를 먼저 입증한다.
- 최종 ISO 변경은 원본 기대 바이트와 허용 쓰기 범위를 먼저 등록하고 검증하며, 승인되지 않은 일괄 규칙 치환이나 누락 글리프 무음 대체(silent fallback)를 금지한다.
- 원본/전체 게임 이미지/추출 폰트·그래픽·오디오·덤프는 커밋하거나 공개 패키지에 포함하지 않는다.
- 모든 한국어·일본어 문서와 JSON/JSONL은 UTF-8로 저장하고 깨진 문자 여부를 검사한다.

