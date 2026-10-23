# PLAN — T-20261023-docs-finalize 개발 마무리 문서화

> 작성: orchestrator(opus) · 2026-10-23 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 승인: 사용자 지시 "추가 개발하지 말고 개발 마무리. e2e 안 돌려도 됨. 문서화를 잘하고 마무리" (2026-10-23)

## 0. 한 줄 목표
처음 보는 사람이 README 하나로 hwp2md가 무엇이고 세 가지 사용 방식(CLI·웹·라이브러리)을 어떻게 쓰는지, 무엇이 되고 무엇이 아직 안 되는지 알 수 있고, docs/system-overview.md 로 내부 구조를 이해할 수 있다.

### 0.1 OpenSpec 연동
OpenSpec: 사용 안 함 (문서 전용 태스크, 동작 변경 없음 — 전역 규칙의 "동작이 바뀌지 않는 작업" 예외)

## 1. 범위
### 포함 (IN)
- `README.md` 전면 재구성 (포트폴리오용)
- `docs/system-overview.md` 신규 (vision.md 가 예고한 내부 구조 문서)
- `docs/images/*.png` 신규 (합성 데모 문서로 찍은 화면)
- `CLAUDE.md` "현재 단계" 줄 갱신 (orchestrator)

### 제외 (OUT)
- `src/**`, `tests/**`, `pyproject.toml` — 코드·테스트·의존성 변경 없음
- 새 기능(각주, --split, --meta, 일괄 변환, 품질 비교표, PyPI/CI) — 로드맵으로만 적는다
- `docs/vision.md`, `docs/decisions.md` 기존 내용 수정
- E2E 실행 (사용자 면제)

### 건드리면 안 되는 파일/디렉토리
- `tests/fixtures/**` 의 실제 샘플을 화면·문서에 노출하지 않는다 (제3자 문서, gitignore 대상)

## 2. 성공 기준
| # | 기준 | 검증 | 기대 |
|---|------|------|------|
| D1 | 코드 불변 | `git diff --name-only main -- src tests pyproject.toml uv.lock` | 0줄 |
| D2 | 단위 회귀 | `uv run pytest tests/unit -q` | 실패 0 (338 passed) |
| D3 | README 필수 절 | `grep -cE '^## ' README.md` 및 절 이름 확인 | 소개·빠른 시작(CLI/웹/라이브러리)·지원 범위·구조·개인정보·테스트·한계·로드맵·문서 링크 |
| D4 | README 명령이 실제와 일치 | `uv run hwp2md --help`, `uv run hwp2md serve --help` 와 대조 | 옵션 이름 일치 |
| D5 | 이미지 링크 유효 | README·system-overview 의 `docs/images/*` 경로가 실제 파일 | 전부 존재 |
| D6 | 익명화 | `scripts/sanitize-check.sh hwp2md` + 화면에 제3자 로고·문서 없음(눈으로 확인) | OK |

## 3. 실패 기준
- 단계 재시도 2회 초과 → BLOCKED. 코드 수정이 필요해지면 즉시 BLOCKED (OUT).

## 5. 단계
### S1 — 데모 화면 + 문서 작성 (implementer, opus)
- 쓰기 범위: `README.md`, `docs/system-overview.md`, `docs/images/**`, `.ai/tasks/T-20261023-docs-finalize/demo/**`
- 데모 문서: `tests/synth_hwpx.py` 로 합성 HWPX(제목·본문·표·그림 1개) 생성 → `hwp2md serve` 로컬 실행 → Playwright 로 서버 모드·브라우저 모드 화면 캡처. 스크립트는 `.ai/.../demo/` 에 둔다.
- 검증: D1~D6
### S2 — 리뷰 (reviewer, sonnet): README·system-overview 를 코드와 대조, 화면 확인
### S3 — 마감 (orchestrator): CLAUDE.md 현재 단계, RESULT(scribe), STATE, 커밋, main 병합

## 6. 병렬 실행 맵
S1 → S2 → S3 (순차)

## 7. 사용자 확인
- 없음 (지시로 확정)
