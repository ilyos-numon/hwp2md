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
