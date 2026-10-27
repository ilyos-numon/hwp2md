# RESULT — T-20261027-public-launch 공개 출시 (브라우저 체험·공개 저장소·PyPI·영어 지원)

> 작성: scribe · 2026-10-27 20:04 · 최종 상태: DONE (gate 5/6, 아래 "알려진 문제" 참조)
> 사용자는 이 파일만 읽고 받아들일지 판단한다.

## 결론 (3줄)
- 저장소 공개(https://github.com/ilyos-numon/hwp2md), 체험 사이트(https://ilyos-numon.github.io/hwp2md/, 브라우저 안 변환, ko/en), PyPI `hwp2markdown` 0.1.2 (영어 지원판; 0.1.1 은 영어 전 판으로 먼저 게시됨) 모두 완료.
- 성공 기준 C1~C30 전부 PASS. 실제 Pages 11 passed (ko+en 포함).
- 지금 바로 사용 가능. 단 gate 5/6 (오탐 1건, 아래 참조). 체험 링크·`pip install hwp2markdown` 즉시 사용 가능.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| C1 | 정적 빌드 생성 | ✅ | `logs/s17-local.log` build_pages OK dist-pages |
| C2 | 루트 절대 경로 0 | ✅ | `logs/s17-local.log` pages=0 |
| C3 | 단위 테스트 | ✅ | `logs/s17-local.log` 820 passed |
| C4 | lint | ✅ | `logs/s17-local.log` lint=0 |
| C5 | 타입 검사 | ✅ | `logs/s17-local.log` mypy=0, Success 34 files |
| C6 | 로컬 E2E 전체 | ✅ | `logs/e2e.log` 142 passed exit=0 |
| C7 | 정적 사이트 스크린샷 | ✅ | `screenshots/pages-landing.png`, `pages-convert-done.png`, `pages-cdn-blocked.png` (리뷰어 판정 PASS) |
| C8 | 패키지 메타데이터 | ✅ | PROGRESS 483행 (0.1.1 시점 7), 0.1.2 로 재확인 |
| C9 | 배포물 검사 | ✅ | `logs/s17-local.log` check_dist OK sdist=68 wheel=68; `logs/s6-docs.log` twine PASSED |
| C10 | README 상대 링크 0 | ✅ | `logs/s6-docs.log` relative=0 |
| C11 | 워크플로우 문법 | ✅ | 리뷰어 PASS (CI·Pages 실행 성공으로 간접 확인). 전용 로그 없음 |
| C12 | HEAD 익명화 | ✅ | `logs/s17-local.log` sanitize-check OK (22 patterns), sanitize=0 |
| C13 | 이력 익명화·금지 경로 (V1~V3) | ✅ | PROGRESS 276행: V1 0, V2 0, V3 0 |
| C14 | v0.1.0 내용 동일 (V4) | ✅ | PROGRESS 276행: same 5/5 |
| C15 | 공개·원격 정리 | ✅ | PROGRESS 276행: PUBLIC, heads 1, main 일치 |
| C16 | Pages 배포 | ✅ | `logs/s11-pages.log` 200 ×3 (`/`, `convert.html`, `pkg/hwp2md.zip`); PROGRESS 287행 |
| C17 | 실제 Pages E2E | ✅ | `logs/s17-live.log` 11 passed. 기대 파일명 `pages-live-done.png` 없음 → 실제 `screenshots/pages-live-convert-done.png` |
| C18 | PyPI 게시 버전 | ✅ | `logs/s18-release.log` R3 0.1.2 (0.1.1 기준이 아니라 0.1.2 로 충족) |
| C19 | 새 환경 설치 | ✅ | `logs/s18-release.log` R2 `hwp2md 0.1.2` (0.1.1 기준이 아니라 0.1.2 로 충족) |
| C20 | 저장소 메타 | ✅ | description·homepage·topics 설정 (S1). 리뷰어 PASS |
| C21 | CI·Pages·Release green | ✅ | `logs/s18-release.log` release 40492693803 exit=0, build·publish success. CI·Pages 리뷰어 PASS |
| C22 | OpenSpec 검증 | ✅ | `logs/openspec-validate.log` "Change 'public-launch' is valid" |
| C23 | 홍보 초안 | ✅ | `docs/launch/community-post.md`, `docs/launch/sns-post.md` 존재, 글자 수 리뷰어 PASS |
| C24 | i18n JS 문법 | ✅ | `node --check` 5파일, 리뷰어 PASS |
| C25 | i18n E2E | ✅ | `logs/s15-e2e.log` 8 passed (skip 0) |
| C26 | 기존 E2E 단언 불변 | ✅ | PROGRESS 342행: 단언 변경 0, 5파일 36 passed (locale="ko-KR" 추가만) |
| C27 | 영어 스크린샷 | ✅ | `screenshots/i18n-en-convert-done.png`, `i18n-en-error.png`, `i18n-en-about.png`, `i18n-pages-en-done.png` (리뷰어 직접 판정 PASS) |
| C28 | README 영어판 | ✅ | relative=0, `^## ` 개수 동일, `README.en.md` 링크 1 (PROGRESS 483행) |
| C29 | Pages 영어 반영 | ✅ | `static/js/i18n.js`, `i18n-about.js` 200, `lang-toggle` 존재 (리뷰어 PASS) |
| C30 | 실제 Pages 영어 E2E | ✅ | `logs/s17-live.log` 11 passed (C17 과 같은 실행에 포함). `screenshots/i18n-pages-live-en-done.png` |

## 변경 요약
- 커밋 범위: `main..HEAD` = 3 commits (`0d96e12..09e4216`), main 최신 `6bcc4f0`
- 추가/수정 파일: 14개 (`git diff --stat main..HEAD`: 166 insertions, 7 deletions). 핵심: `scripts/build_pages.py`, `src/hwp2md/web/static/js/i18n.js`, `tests/e2e/test_pages_site.py`, `tests/e2e/test_i18n.py`, `README.md`, `README.en.md`, `.github/workflows/pages.yml`, `pyproject.toml`
- 새 의존성: 없음 (영어 사전은 순수 JS 객체)
- 새 환경변수: 없음 (`HWP2MD_PAGES_URL` 은 E2E 선택 실행용)

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → pass (820 passed)
- E2E: `uv run pytest tests/e2e -q` → pass (142 passed, exit 0). 실제 Pages (`HWP2MD_PAGES_URL` 지정 시 `test_pages_site.py`·`test_i18n.py` live 케이스) → 11 passed
  - 정적 사이트 landing→변환→상태 "브라우저 모드" 확인 (ko/en)
  - 실패 경로: 비-HWP 파일, CDN 차단 시 오류 표시
  - i18n: navigator·query·저장 토글·알 수 없는 lang 폴백·skipped 접두·소개 페이지 토글

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md && uv run hwp2md serve --no-browser --port 8770   # 로컬 웹
# 체험: https://ilyos-numon.github.io/hwp2md/
pip install hwp2markdown && hwp2md 문서.hwp -o out/
```

## 진행 중 생긴 일
- S10 force-push·공개 전환·v0.1.1 태그는 세션 권한 판정에 막혀 사용자가 직접 실행. 이후 v0.1.2 태그는 사용자 지시로 orchestrator 가 실행.
- filter-repo 2회 실행 (1회차 뒤 스캐폴드 CLAUDE.md 끝 내부 메모 규칙 보강 후 재실행).
- landing.js 제목 중복 버그 수정.
- gate 5/6 — "E2E 변경" 항목은 main 선병합 오탐 (이 태스크에서 `test_pages_site.py`·`test_i18n.py` 추가, 5파일 locale 고정). 나머지 통과.
- 백업: `/Users/illi/hwp2md-backups/` (`hwp2md-pre-filter-20261027.bundle`, `hwp2md-pre-filter-20261027-merged.bundle`, `pre-filter-refs.txt`, `pre-filter-refs-merged.txt`, `pre-filter-clone/`, `filter/`).
- 스크린샷 (8개): `screenshots/pages-landing.png`, `pages-convert-done.png`, `pages-cdn-blocked.png`, `i18n-en-convert-done.png`, `i18n-en-error.png`, `i18n-en-about.png`, `i18n-pages-en-done.png`, `i18n-pages-live-en-done.png` (+ `pages-live-*.png` 3장 추가 존재).

## 못 한 것 / 알려진 문제
- gate 5/6: "E2E 변경" 항목 오탐 (main 선병합 탓). 실제 E2E 테스트 파일은 이 태스크에서 추가됨 — 판정 근거: `logs/gate.log`
- GitHub 가 옛 SHA 를 잠시 보여 줄 수 있음 (캐시). 시간이 지나면 해소.
- CLI 출력은 한국어 유지 (영어화 OUT).
- Python 3.14 손상 zip 문구 차이 (CLI 와 웹 문구가 다름).
- 현재 체크아웃 브랜치는 `ai/T-20261027-public-launch`(HEAD `09e4216`). main(`6bcc4f0`)보다 3커밋 앞서 있다 (`git log main..HEAD`). main 반영 여부 확인 필요.
- 확인 필요: `.ai/STATE.md` 의 "브랜치" 값은 실제 git 기준 `ai/T-20261027-public-launch` 로 기록.

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- PyPI 최종 버전 0.1.2 (0.1.1 은 영어 전 판으로 이미 게시됨 → 영어 지원판은 0.1.2). 근거: PyPI 는 같은 버전 재업로드 불가.
- C17·C18·C19 의 0.1.1 기준은 0.1.2 로 대체해 충족.

## 후속 제안 (별도 태스크로)
- `docs/launch` 홍보 초안 게시 (사용자 직접)
- pepy 배지 집계는 하루 뒤 확인
- Python 3.14 손상 zip 문구 정리
- 실제 차트 HWP 샘플 확보
- CLI 출력 영어화 여부 결정

## 비용
- 서브에이전트 호출: 다수 (정확한 수 확인 필요 — PROGRESS 참조)
- 재시도: 2회 (S12, S18) · 차단: 3회 (S10 ×2, S12) — 모두 PROGRESS 에 기록
