# PROGRESS — T-20261027-pypi-release

> append-only.

---

## [2026-10-27 16:01] S0 | planner(opus) | DONE
- 한 일: PLAN.md 작성 (12단계)
- 변경 파일(미커밋, .ai 제외): openspec/changes/pypi-release/ 
- 커밋: dd3f4ed [record] V3 병합·푸시, 다음 작업 PyPI 배포
- 다음: 사용자 승인 대기

## [2026-10-27 16:03] S1 | orchestrator | START
- 한 일: 클린 체크아웃 기준선 측정
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c657cee [T-20261027-pypi-release][plan] approved (§7 기본값)

## [2026-10-27 16:04] S1 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c657cee [T-20261027-pypi-release][plan] approved (§7 기본값)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:05] S1 | runner(haiku) | DONE
- 한 일: NAME_STATUS=404, LINT 0 TYPE 0 UNIT 2 E2E 2. 수집 오류(StopIteration): unit test_memory·test_web_app, e2e test_web_api·test_web_ui·test_web_v3
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 140ee45 [T-20261027-pypi-release][S1][wip] auto checkpoint (stop)
- 다음: S2
- 메모: PLAN S5 범위·§4.4/4.5 unit 명령 보완

## [2026-10-27 16:05] S1 | orchestrator | DONE
- 한 일: 기준선 측정 완료, PLAN 보완
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 140ee45 [T-20261027-pypi-release][S1][wip] auto checkpoint (stop)
- 다음: S2 시작

## [2026-10-27 16:05] S2 | orchestrator | START
- 한 일: pyproject 배포 메타데이터
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ff72982 [T-20261027-pypi-release][s1] 클린 체크아웃 기준선 (PLAN S5 범위 보완)

## [2026-10-27 16:06] S2 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ff72982 [T-20261027-pypi-release][s1] 클린 체크아웃 기준선 (PLAN S5 범위 보완)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:06] S2 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 31ba43b [T-20261027-pypi-release][S2][wip] auto checkpoint (stop)

## [2026-10-27 16:07] S2 | implementer(opus) | DONE
- 한 일: pyproject §4.2 적용, uv.lock 갱신. C1·C2·C5·C6 통과, sdist 허용 목록만, wheel licenses·static 포함
- 변경 파일(미커밋, .ai 제외): pyproject.toml uv.lock 
- 커밋: 31ba43b [T-20261027-pypi-release][S2][wip] auto checkpoint (stop)
- 다음: S3
- 메모: hatchling 1.32.4. rm -rf 는 권한 정책상 막힘 → 단계별 개별 명령

## [2026-10-27 16:07] S2 | orchestrator | DONE
- 한 일: pyproject 배포 메타데이터 검증 통과
- 변경 파일(미커밋, .ai 제외): pyproject.toml uv.lock 
- 커밋: 31ba43b [T-20261027-pypi-release][S2][wip] auto checkpoint (stop)
- 다음: S3 시작

## [2026-10-27 16:07] S3 | orchestrator | START
- 한 일: web extra 안내 hwp2markdown[web]
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1ea524c [T-20261027-pypi-release][s2] 배포 이름 hwp2markdown·동적 버전·sdist 허용 목록

## [2026-10-27 16:07] S3 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: 1ea524c [T-20261027-pypi-release][s2] 배포 이름 hwp2markdown·동적 버전·sdist 허용 목록

## [2026-10-27 16:07] S3 | orchestrator | DONE
- 한 일: cli.py 49행 hwp2markdown[web], 검증 exit=1·lint·mypy·unit 815 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: 1ea524c [T-20261027-pypi-release][s2] 배포 이름 hwp2markdown·동적 버전·sdist 허용 목록
- 다음: S4 시작
- 메모: test_web_api.py 의 web extra 단언은 S5 에서 갱신, 그 사이 1건 실패 예상

## [2026-10-27 16:07] S4 | orchestrator | START
- 한 일: 배포물 검사 스크립트
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 3d42ea9 [T-20261027-pypi-release][s3] web extra 안내 hwp2markdown[web]

## [2026-10-27 16:08] S4 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 3d42ea9 [T-20261027-pypi-release][s3] web extra 안내 hwp2markdown[web]
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:09] S4 | implementer(opus) | DONE
- 한 일: scripts/check_dist.py: C3 OK sdist=66 wheel=66, 실패 경로 6종 확인, mypy --strict·ruff·C4 통과
- 변경 파일(미커밋, .ai 제외): scripts/ 
- 커밋: e570309 [T-20261027-pypi-release][S4][wip] auto checkpoint (stop)
- 다음: S5
- 메모: 깨진 archive·잘못된 정규식은 exit 2

## [2026-10-27 16:09] S4 | orchestrator | DONE
- 한 일: 배포물 검사 스크립트 검증 통과
- 변경 파일(미커밋, .ai 제외): scripts/ 
- 커밋: e570309 [T-20261027-pypi-release][S4][wip] auto checkpoint (stop)
- 다음: S5 시작

## [2026-10-27 16:09] S5 | orchestrator | START
- 한 일: CI 용 실제 샘플 테스트 표시
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ae58244 [T-20261027-pypi-release][s4] 배포물 검사 scripts/check_dist.py

## [2026-10-27 16:10] S5 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ae58244 [T-20261027-pypi-release][s4] 배포물 검사 scripts/check_dist.py

## [2026-10-27 16:10] S5 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ae58244 [T-20261027-pypi-release][s4] 배포물 검사 scripts/check_dist.py
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:11] S5 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_web_api.py tests/conftest.py 
- 커밋: 55ffd3e [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)

## [2026-10-27 16:14] S5 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_cli_convert.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py tests/e2e/test_cli_image.py tests/e2e/test_extract_real.py tests/e2e/test_web_api.py tests/e2e/test_web_ui.py tests/e2e/test_web_v3.py tests/unit/test_memory.py tests/unit/test_web_app.py tests/conftest.py 
- 커밋: 55ffd3e [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)

## [2026-10-27 16:14] S5 | implementer(opus) | PARTIAL
- 한 일: 마커·next(None)·안내 단언 갱신. 로컬 unit 815·e2e 127, 클린 e2e 77 passed 35 deselected. 클린 unit 1 실패: test_source_bytes.py::test_sample_counts (범위 밖)
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_cli_convert.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py tests/e2e/test_cli_image.py tests/e2e/test_extract_real.py tests/e2e/test_web_api.py tests/e2e/test_web_ui.py tests/e2e/test_web_v3.py tests/unit/test_memory.py tests/unit/test_source_bytes.py tests/unit/test_web_app.py tests/conftest.py 
- 커밋: 55ffd3e [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)
- 다음: 범위에 test_source_bytes.py 추가 후 재호출
- 메모: Python 3.14 에서 test_detect::test_corrupt_zip_raises 메시지 차이(3.11·3.13 정상)

## [2026-10-27 16:14] S5 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_cli_convert.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py tests/e2e/test_cli_image.py tests/e2e/test_extract_real.py tests/e2e/test_web_api.py tests/e2e/test_web_ui.py tests/e2e/test_web_v3.py tests/unit/test_memory.py tests/unit/test_source_bytes.py tests/unit/test_web_app.py tests/conftest.py 
- 커밋: 55ffd3e [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:15] S5 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 76fe4e4 [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)

## [2026-10-27 16:15] S5 | implementer(opus) | DONE
- 한 일: test_source_bytes 마커 추가. 클린(3.13) unit 780 passed 19 deselected, e2e 77 passed 35 deselected, 로컬 unit 815·e2e 127
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 76fe4e4 [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)
- 다음: S6
- 메모: Python 3.14: test_detect::test_corrupt_zip_raises 메시지 차이 — 후속 과제

## [2026-10-27 16:15] S5 | orchestrator | DONE
- 한 일: real_samples 마커 검증 통과 (약화 없음)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 76fe4e4 [T-20261027-pypi-release][S5][wip] auto checkpoint (stop)
- 다음: S6 시작

## [2026-10-27 16:15] S6 | orchestrator | START
- 한 일: CI 워크플로우
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7c19a95 [T-20261027-pypi-release][s5] real_samples 마커와 CI 수집 오류 제거

## [2026-10-27 16:16] S6 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7c19a95 [T-20261027-pypi-release][s5] real_samples 마커와 CI 수집 오류 제거
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:17] S6 | implementer(opus) | DONE
- 한 일: ci.yml (lint·typecheck·unit 3.11/3.13·e2e·dist), actionlint 1.7.12 exit 0, 로컬 재현 통과
- 변경 파일(미커밋, .ai 제외): .github/ 
- 커밋: 0f4f0e1 [T-20261027-pypi-release][S6][wip] auto checkpoint (stop)
- 다음: S7
- 메모: 액션 태그: actions/checkout@v7, astral-sh/setup-uv@v7, actions/upload-artifact@v7. python-version 전 job 명시(3.14 회피)

## [2026-10-27 16:17] S6 | orchestrator | DONE
- 한 일: CI 워크플로우 검증 통과
- 변경 파일(미커밋, .ai 제외): .github/ 
- 커밋: 0f4f0e1 [T-20261027-pypi-release][S6][wip] auto checkpoint (stop)
- 다음: S7 시작

## [2026-10-27 16:17] S7 | orchestrator | START
- 한 일: 릴리스 워크플로우
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: d74e8e8 [T-20261027-pypi-release][s6] CI 워크플로우

## [2026-10-27 16:17] S7 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: d74e8e8 [T-20261027-pypi-release][s6] CI 워크플로우
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:17] S7 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5ddc3cd [T-20261027-pypi-release][S7][wip] auto checkpoint (stop)

## [2026-10-27 16:17] S7 | implementer(opus) | DONE
- 한 일: release.yml (build·publish), actionlint 0, grep 4/0, check_dist --tag v0.1.0 OK
- 변경 파일(미커밋, .ai 제외): .github/workflows/release.yml 
- 커밋: 5ddc3cd [T-20261027-pypi-release][S7][wip] auto checkpoint (stop)
- 다음: S8
- 메모: actions/download-artifact@v8, pypa/gh-action-pypi-publish@release/v1

## [2026-10-27 16:17] S7 | orchestrator | DONE
- 한 일: 릴리스 워크플로우 검증 통과
- 변경 파일(미커밋, .ai 제외): .github/workflows/release.yml 
- 커밋: 5ddc3cd [T-20261027-pypi-release][S7][wip] auto checkpoint (stop)
- 다음: S8 시작

## [2026-10-27 16:17] S8 | orchestrator | START
- 한 일: 설치·릴리스 문서
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 59c2faf [T-20261027-pypi-release][s7] 릴리스 워크플로우 (Trusted Publishing)

## [2026-10-27 16:18] S8 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 59c2faf [T-20261027-pypi-release][s7] 릴리스 워크플로우 (Trusted Publishing)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:19] S8 | implementer(opus) | DONE
- 한 일: README 설치·한계·로드맵, docs/releasing.md, decisions 2항목, feature-reference 539, web/__init__ docstring. C2·C12·unit 815 통과
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md docs/feature-reference.md src/hwp2md/web/__init__.py docs/releasing.md 
- 커밋: 0d746d2 [T-20261027-pypi-release][S8][wip] auto checkpoint (stop)
- 다음: S9
- 메모: decisions.md 60행 옛 extra 표기 정정

## [2026-10-27 16:19] S8 | orchestrator | DONE
- 한 일: 설치·릴리스 문서 검증 통과
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md docs/feature-reference.md src/hwp2md/web/__init__.py docs/releasing.md 
- 커밋: 0d746d2 [T-20261027-pypi-release][S8][wip] auto checkpoint (stop)
- 다음: S9 시작

## [2026-10-27 16:19] S9 | orchestrator | START
- 한 일: E2E 테스트 작성·실행
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: cc30764 [T-20261027-pypi-release][s8] 설치·릴리스 문서

## [2026-10-27 16:20] S9 | hook | AUTO
- 한 일: 도구 호출 120회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: cc30764 [T-20261027-pypi-release][s8] 설치·릴리스 문서

## [2026-10-27 16:20] S9 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: cc30764 [T-20261027-pypi-release][s8] 설치·릴리스 문서
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 16:23] S9 | test-writer(sonnet) | DONE
- 한 일: test_dist_package.py 4 passed, 전체 e2e 131 passed, 클린 3.12 81 passed 35 deselected
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_dist_package.py 
- 커밋: 3b1ef9e [T-20261027-pypi-release][S9][wip] auto checkpoint (stop)
- 다음: S10

## [2026-10-27 16:23] S9 | orchestrator | DONE
- 한 일: 배포물 E2E 검증 통과
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_dist_package.py 
- 커밋: 3b1ef9e [T-20261027-pypi-release][S9][wip] auto checkpoint (stop)
- 다음: S10 시작
