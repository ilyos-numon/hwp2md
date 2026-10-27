# RESULT — T-20261027-pypi-release PyPI 배포(hwp2markdown) + GitHub Actions CI

> 작성: scribe · 2026-10-27 16:31 · 최종 상태: DONE_WITH_ISSUES (S12 릴리스 게이트 대기)
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 무엇이 되었나: S1~S11 완료. 배포 이름 `hwp2markdown`, 동적 버전, sdist 허용 목록, `scripts/check_dist.py`, `real_samples` 마커, CI(`ci.yml`)·릴리스(`release.yml`) 워크플로우, 배포 E2E 4건이 들어갔다. 실제 CI 6 job 전부 success.
- 무엇이 안 되었나: 실제 PyPI 게시(S12)는 하지 않았다. 사용자 수동 작업 U1·U2와 "v0.1.0 게시 승인"(U3)이 필요하다.
- 지금 바로 쓸 수 있나: 로컬 빌드·CI 기준으로는 쓸 수 있다. PyPI 설치(`pip install 'hwp2markdown[web]'`)는 S12 후에만 가능하다.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| C1 | 빌드 산출물 이름 | ✅ | `hwp2markdown-0.1.0` whl·tar.gz 2개 (PROGRESS S2) |
| C2 | twine check --strict | ✅ | 두 줄 PASSED (PROGRESS S8 기준 재확인, 수치 로그 경로 확인 필요) |
| C3 | 배포물 구조 검사 | ✅ | `check_dist: OK sdist=66 wheel=66` (PROGRESS S4, `logs/s4-check-dist.log`) |
| C4 | 배포물 익명화 검사 | ✅ | sanitize OK, exit 0 (PROGRESS S4) |
| C5 | 버전 단일 출처 | ✅ | `version =` 0건, `uv lock --check` exit 0 (PROGRESS S2) |
| C6 | lint·mypy·unit | ✅ | lint·mypy exit 0, unit 815 passed (PROGRESS S3·S5, `logs/s5-markers.log`) |
| C7 | 로컬 E2E 전체 | ✅ | 131 passed (PROGRESS S9, `logs/e2e.log`) |
| C8 | 클린 복사본 E2E (`-m "not real_samples"`) | ✅ | e2e 81 passed 35 deselected, 클린 unit 780 passed 19 deselected (PROGRESS S5·S9) |
| C9 | 배포 E2E 성공·실패 경로 | ✅ | `test_dist_package.py` 4 passed (PROGRESS S9) |
| C10 | 워크플로우 문법 (actionlint 1.7.12) | ✅ | ci.yml·release.yml exit 0 (PROGRESS S6·S7) |
| C11 | 실제 CI | ✅ | run 40467253929: 6 job success (PROGRESS S10, `logs/s10-ci.log`) |
| C12 | 저장소 익명화 | ✅ | sanitize OK, exit 0 (PROGRESS S9 RETRY 후 재확인) |
| C13 | OpenSpec validate | ✅ | `Change 'pypi-release' is valid` (PLAN §2) |
| R1 | Release 실행 (S12) | ⏳ | S12 대기 |
| R2 | PyPI 설치 (S12) | ⏳ | S12 대기 |
| R3 | PyPI 메타데이터 (S12) | ⏳ | S12 대기 |

## 변경 요약
- 커밋 범위: `c657cee..54d34ab` (26 commits, `git log main..HEAD`)
- 추가/수정 파일: 34개 (+1549 / -34) — 핵심: `pyproject.toml`, `uv.lock`, `scripts/check_dist.py`, `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `tests/e2e/test_dist_package.py`, `tests/conftest.py`, `docs/releasing.md`, `README.md`
- 새 의존성: 없음 (빌드 백엔드 hatchling 하한 `>=1.27`, 설치본 1.32.4. CI 전용으로 twine>=6.1 · actionlint-py 는 uvx 실행)
- 새 환경변수: 없음

## 테스트
- 단위/통합: `uv run pytest tests/unit -q -m "not real_samples"` (클린) → 780 passed, 19 deselected / 로컬 `uv run pytest tests/unit -q` → 815 passed
- E2E: `uv run pytest tests/e2e -q` (로컬) → 131 passed / 클린 `-m "not real_samples"` → 81 passed, 35 deselected
  - `test_dist_package.py` — 성공 1건(wheel 설치 후 `hwp2md --version`·`serve`·`/api/health`), 실패 3건(`forbidden-path`, `version-mismatch`, `pattern-hit`)

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md && uv sync --locked && uv build --out-dir dist && uv run python scripts/check_dist.py dist
```

## 진행 중 고친 것
- S1: 클린 복사본에서 단위 테스트 2개 파일(`test_memory`, `test_web_app`)도 수집 오류 → S5 범위 확장(`test_source_bytes`, `tests/conftest.py` 추가)
- S9: 루프백 IP 리터럴이 sanitize 에 걸려 `localhost` 로 교체 (RETRY 1회)
- S10: 첫 CI 실패 2건 — (a) 로컬 ruff 캐시가 import 정렬 오류를 가림 → `--no-cache` 로 검사, (b) Linux 에서 TIME_WAIT 재바인드는 양쪽 `SO_REUSEADDR` 필요 → 테스트 리스너에 uvicorn 과 같은 옵션 (RETRY 1회)

## 못 한 것 / 알려진 문제
- R1~R3 (PyPI 게시·설치 확인) — S12 게이트 대기 — 사용자 U1·U2·U3 필요
- Python 3.14 에서 `test_detect::test_corrupt_zip_raises` 오류 문구 차이 — CI 는 3.11·3.13 만 돌리므로 영향 없음 — 후속 과제
- README 그림이 PyPI 페이지에서 깨짐 — 저장소 비공개 — 공개 전환 시 절대 URL 검토 (Q4 기본값 유지)
- `ubuntu-latest` 가 Ubuntu 26 으로 이동 중 (CI 경고) — 후속 점검
- 고유명사 검사는 로컬 전용 (CI 에 넣지 않음, Q5 기본값)
- 동봉 GSAP 은 OSI 라이선스가 아님 (기존 `vendor/gsap/LICENSE.md` 안내) — 공개 배포 사실 기록
- S11 reviewer `VERDICT: PASS` — 입력에 결과 없음, 확인 필요

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- 첫 릴리스 버전 `0.1.0` 유지 (Q1 기본값)
- CI·Release 는 구조 검사만, 고유명사 검사는 로컬 C4·C12 (Q5 기본값)
- `environment: pypi` 사용 여부는 U2 생성 후 확인 (Q2 기본값 대체안 미적용)
- `python-version` 을 전 job 에 명시 (3.14 회피)

## 후속 제안 (별도 태스크로)
- 3.14 호환 `test_corrupt_zip_raises` 문구 정리
- 공개 전환 시 README 그림 절대 URL 적용
- 0.1.1 이후 릴리스 자동화(버전 증가·CHANGELOG) 검토

## 비용
- 서브에이전트 호출: 8회 (opus 6 — S2·S4·S5·S6·S7·S8 implementer / sonnet 1 — S9 test-writer / haiku 1 — S1 runner). S11 reviewer 호출 수는 확인 필요
- 재시도: 2회 (S9 sanitize, S10 CI) · 차단: 0회
