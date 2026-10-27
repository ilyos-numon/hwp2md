# RESULT — T-20261027-pypi-release PyPI 배포(hwp2markdown) + GitHub Actions CI

> 작성: scribe · 2026-10-27 17:03 · 최종 상태: 완료 — v0.1.0 PyPI 게시
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 무엇이 되었나: v0.1.0 을 PyPI 에 게시했다 (배포 이름 `hwp2markdown`). main 병합 `abbebb1`, 태그 `v0.1.0`, Release run `40470475676` build·publish success.
- 무엇이 안 되었나: 없음. 게이트 항목 중 "E2E 파일 변경"은 main 병합 순서 때문에 오탐으로 판단 (아래 근거).
- 지금 바로 쓸 수 있나: 예. `pip install 'hwp2markdown[web]'` 후 `hwp2md 문서.hwp -o out/`, `hwp2md serve`.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| C1 | 빌드 산출물 이름 | ✅ | `hwp2markdown-0.1.0` whl·tar.gz 2개 (PROGRESS S2) |
| C2 | twine check --strict | ✅ | 두 줄 PASSED (PROGRESS S8, 수치 로그 경로 확인 필요) |
| C3 | 배포물 구조 검사 | ✅ | `check_dist: OK sdist=66 wheel=66` (`logs/s4-check-dist.log`) |
| C4 | 배포물 익명화 검사 | ✅ | sanitize OK, exit 0 (PROGRESS S4) |
| C5 | 버전 단일 출처 | ✅ | `version =` 0건, `uv lock --check` exit 0 (PROGRESS S2) |
| C6 | lint·mypy·unit | ✅ | lint·mypy exit 0, unit 815 passed (`logs/s5-markers.log`) |
| C7 | 로컬 E2E 전체 | ✅ | 131 passed, exit=0 (`logs/e2e.log`) |
| C8 | 클린 복사본 E2E (`-m "not real_samples"`) | ✅ | e2e 81 passed 35 deselected, unit 780 passed 19 deselected |
| C9 | 배포 E2E 성공·실패 경로 | ✅ | `test_dist_package.py` 4 passed |
| C10 | 워크플로우 문법 (actionlint 1.7.12) | ✅ | ci.yml·release.yml exit 0 |
| C11 | 실제 CI | ✅ | main CI run `40470281059`: 6 job success (typecheck, unit 3.11·3.13, lint, e2e, dist) (`logs/s12-release.log`) |
| C12 | 저장소 익명화 | ✅ | sanitize OK, exit 0 |
| C13 | OpenSpec validate | ✅ | `Change 'pypi-release' is valid` |
| R1 | Release 실행 | ✅ | Release run `40470475676`: build success, publish success, exit=0 |
| R2 | PyPI 설치 | ✅ | 새 venv 에 `hwp2markdown[web]==0.1.0` 설치, `hwp2md 0.1.0` (`logs/s12-release.log`). static about.html·woff2 4개 포함은 리드 보고 기준, 로그에 없음 |
| R3 | PyPI 메타데이터 | ✅ | `0.1.0 ['bdist_wheel', 'sdist']` (`logs/s12-release.log`) |

## 게이트 (`logs/gate.log`)
- 6항목 중 5 통과. ❌ "tests/e2e 에 이번 태스크의 테스트 파일 변경 없음" 1건.
- 오탐 판단 근거: 게이트가 `main...HEAD` 를 보는데 병합 후 main 과 같아 비어 있음. 병합 전 기준 `dd3f4ed..abbebb1` 에서 `tests/e2e` 10파일 변경 (201+ / 7-, `test_dist_package.py` 추가) 확인.
- 게이트 로그 자체는 FAIL 로 남겨둠 (기록 수정 금지).

## 변경 요약
- 커밋 범위: `c657cee..abbebb1` (27 commits, main 기준, 머지 커밋 포함)
- 추가/수정 파일: 30개 (+1124 / -44) — 핵심: `pyproject.toml`, `uv.lock`, `scripts/check_dist.py`, `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `tests/e2e/test_dist_package.py`, `tests/conftest.py`, `docs/releasing.md`, `README.md`. 이전 기록(34개, +1549/-34, `c657cee..54d34ab`)과 수치 차이 — 원인 확인 필요.
- 미병합 기록: `ai/T-20261027-pypi-release` HEAD `5c4778a` 1커밋 (9파일, +88/-3: PROGRESS, OpenSpec 아카이브·main spec 반영). main 에는 아직 없음.
- 새 의존성: 없음 (빌드 백엔드 hatchling `>=1.27`, 설치본 1.32.4. CI 전용 twine·actionlint 는 uvx)
- 새 환경변수: 없음

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → 815 passed / 클린 `-m "not real_samples"` → 780 passed, 19 deselected
- E2E: `uv run pytest tests/e2e -q` → 131 passed, exit=0 (`logs/e2e.log`) / 클린 → 81 passed, 35 deselected
  - `test_dist_package.py` — 성공 1건 (wheel 설치 후 `hwp2md --version`·`serve`·`/api/health`), 실패 3건 (`forbidden-path`, `version-mismatch`, `pattern-hit`)

## 사용 방법
```bash
pip install 'hwp2markdown[web]'
hwp2md 문서.hwp -o out/
hwp2md serve
```
다음 릴리스 절차: `docs/releasing.md`

## 진행 중 고친 것
- S1: 클린 복사본에서 단위 테스트 2개 파일 수집 오류 → 범위 확장 (`tests/conftest.py` 추가)
- S9: 루프백 IP 리터럴이 sanitize 에 걸려 `localhost` 로 교체 (RETRY 1회)
- S10: 첫 CI 실패 2건 — ruff 캐시 가림 (`--no-cache`), Linux TIME_WAIT 재바인드 (`SO_REUSEADDR`) (RETRY 1회)

## 못 한 것 / 알려진 문제
- Python 3.14 에서 `test_detect::test_corrupt_zip_raises` 오류 문구 차이 — CI 는 3.11·3.13 만 돌려 영향 없음 — 후속 과제
- README 그림이 PyPI 페이지에서 깨짐 — 저장소 비공개 상태 — 공개 전환 시 절대 URL 검토
- `ubuntu-latest` 가 Ubuntu 26 으로 이동 중 (CI 경고) — 후속 점검
- 고유명사 검사는 로컬 전용 (CI 미포함, 결정 사항 참조)
- 동봉 GSAP 은 OSI 라이선스가 아님 (`vendor/gsap/LICENSE.md`) — 공개 배포 사실 기록
- S11 reviewer `VERDICT: PASS` — 입력에 결과 없음, 확인 필요
- main 미병합 커밋 `5c4778a` (기록·아카이브) — 병합 여부 결정 필요

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- 첫 릴리스 버전 `0.1.0` 유지 (Q1 기본값)
- CI·Release 는 구조 검사만, 고유명사 검사는 로컬 C4·C12 (Q5 기본값)
- `environment: pypi` 사용 여부 — U2 생성 후 확인 (Q2 기본값 대체안 미적용)
- `python-version` 을 전 job 에 명시 (3.14 회피)

## 후속 제안 (별도 태스크로)
- 3.14 호환 `test_corrupt_zip_raises` 문구 정리
- 실제 차트 HWP 샘플 검증
- Pretendard 서브셋
- 과거 커밋의 샘플 산출물 이력 정리 (사용자 결정)
- 0.1.1 이후 릴리스 자동화 (버전 증가·CHANGELOG) 검토

## 비용
- 서브에이전트 호출: 8회 (opus 6 — S2·S4·S5·S6·S7·S8 implementer / sonnet 1 — S9 test-writer / haiku 1 — S1 runner). S11 reviewer·S12 호출 수는 확인 필요
- 재시도: 2회 (S9 sanitize, S10 CI) · 차단: 0회
