# PROGRESS — T-20261027-public-launch

> append-only.

---

## [2026-10-27 17:39] S0 | planner(opus) | DONE
- 한 일: PLAN.md 14단계, §7 기본값 자동 승인
- 변경 파일(미커밋, .ai 제외): openspec/changes/public-launch/ 
- 커밋: 53c1bb0 [record] STATE 정리
- 다음: /implement S1

## [2026-10-27 17:39] S1 | orchestrator | START
- 한 일: 공개 전 설정 정리
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 66390cb [T-20261027-public-launch][plan] 공개 출시: 브라우저 체험 사이트·저장소 공개·PyPI 보강 (approved, §7 기본값)

## [2026-10-27 17:40] S1 | orchestrator | DONE
- 한 일: dist-pages/ 무시, CLAUDE.md 내부 메모 절 삭제, gh description·homepage·topics 9개
- 변경 파일(미커밋, .ai 제외): .gitignore CLAUDE.md 
- 커밋: 66390cb [T-20261027-public-launch][plan] 공개 출시: 브라우저 체험 사이트·저장소 공개·PyPI 보강 (approved, §7 기본값)
- 다음: S2 시작

## [2026-10-27 17:40] S2 | orchestrator | START
- 한 일: 정적 사이트 meta 훅
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 3629806 [T-20261027-public-launch][s1] 공개 전 설정 정리

## [2026-10-27 17:40] S2 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 3629806 [T-20261027-public-launch][s1] 공개 전 설정 정리
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 17:41] S2 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/js/app.js src/hwp2md/web/static/pyodide-runner.js 
- 커밋: 6d1e272 [T-20261027-public-launch][S2][wip] auto checkpoint (stop)

## [2026-10-27 17:41] S2 | implementer(opus) | DONE
- 한 일: app.js STATIC_SITE·ABOUT_URL·staticSite getter, pyodide-runner PKG_URL meta. serve E2E 45·unit 26 통과, 정적 수동 확인(상대 fetch, 실패 시 browser 유지)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/js/app.js src/hwp2md/web/static/pyodide-runner.js 
- 커밋: 6d1e272 [T-20261027-public-launch][S2][wip] auto checkpoint (stop)
- 다음: S3
- 메모: app.css .switch display 가 hidden 을 덮어 style.display=none 병행

## [2026-10-27 17:41] S2 | orchestrator | DONE
- 한 일: 정적 사이트 meta 훅 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/js/app.js src/hwp2md/web/static/pyodide-runner.js 
- 커밋: 6d1e272 [T-20261027-public-launch][S2][wip] auto checkpoint (stop)
- 다음: S3 시작

## [2026-10-27 17:41] S3 | orchestrator | START
- 한 일: 정적 빌드 스크립트
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 8fd9d53 [T-20261027-public-launch][s2] 정적 사이트 meta 설정

## [2026-10-27 17:42] S3 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 8fd9d53 [T-20261027-public-launch][s2] 정적 사이트 meta 설정
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 17:42] S3 | orchestrator | PARTIAL
- 한 일: 사용자 지시로 중단(한도). S3 implementer 중지, 파일 변경 없음
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4c9ee4b [T-20261027-public-launch][S3][wip] auto checkpoint (stop)
- 다음: S3 부터 재개: implementer 에 PLAN §4.1~4.3·§5 Stage 3 그대로 위임 (BASE=8fd9d53)

## [2026-10-27 18:12] S3 | orchestrator | START
- 한 일: resume: S3 처음부터 (파일 변경 없음)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c4eb5cf [T-20261027-public-launch][wip] S3 전 중단 (사용자 지시)

## [2026-10-27 18:12] S3 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c4eb5cf [T-20261027-public-launch][wip] S3 전 중단 (사용자 지시)

## [2026-10-27 18:12] S3 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c4eb5cf [T-20261027-public-launch][wip] S3 전 중단 (사용자 지시)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 18:14] S3 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): scripts/build_pages.py tests/unit/test_build_pages.py 
- 커밋: a97cb65 [T-20261027-public-launch][S3][wip] auto checkpoint (stop)

## [2026-10-27 18:14] S3 | implementer(opus) | DONE
- 한 일: build_pages.py + 단위 5 passed, C1·C2·C4·C5 통과, 하위 경로 수동 변환 done
- 변경 파일(미커밋, .ai 제외): scripts/build_pages.py tests/unit/test_build_pages.py 
- 커밋: a97cb65 [T-20261027-public-launch][S3][wip] auto checkpoint (stop)
- 다음: S4
- 메모: missing-title BuildError, out 이 파일이면 exit 2

## [2026-10-27 18:14] S3 | orchestrator | DONE
- 한 일: 정적 빌드 스크립트 검증 통과
- 변경 파일(미커밋, .ai 제외): scripts/build_pages.py tests/unit/test_build_pages.py 
- 커밋: a97cb65 [T-20261027-public-launch][S3][wip] auto checkpoint (stop)
- 다음: S4 시작

## [2026-10-27 18:14] S4 | orchestrator | START
- 한 일: 정적 사이트 E2E
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 06dc6df [T-20261027-public-launch][s3] 정적 빌드 스크립트

## [2026-10-27 18:15] S4 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 06dc6df [T-20261027-public-launch][s3] 정적 빌드 스크립트
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 18:15] S4 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_pages_site.py 
- 커밋: 2a671b0 [T-20261027-public-launch][S4][wip] auto checkpoint (stop)

## [2026-10-27 18:16] S4 | test-writer(sonnet) | DONE
- 한 일: test_pages_site.py 3 passed (landing→convert 성공, not_hwp, cdn_blocked), 스크린샷 3장, skip 0
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_pages_site.py 
- 커밋: 2a671b0 [T-20261027-public-launch][S4][wip] auto checkpoint (stop)
- 다음: S5
- 메모: HWP2MD_PAGES_URL 로 실제 Pages 대상 실행 가능(S13)

## [2026-10-27 18:16] S4 | orchestrator | DONE
- 한 일: 정적 사이트 E2E 검증 통과
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_pages_site.py 
- 커밋: 2a671b0 [T-20261027-public-launch][S4][wip] auto checkpoint (stop)
- 다음: S5 시작

## [2026-10-27 18:16] S5 | orchestrator | START
- 한 일: 패키지 메타데이터
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 48f7562 [T-20261027-public-launch][s4] 정적 사이트 E2E

## [2026-10-27 18:16] S5 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 48f7562 [T-20261027-public-launch][s4] 정적 사이트 E2E
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 18:16] S5 | implementer(opus) | DONE
- 한 일: pyproject description·keywords·classifiers 16·urls 4, METADATA grep 6, twine·check_dist OK
- 변경 파일(미커밋, .ai 제외): pyproject.toml 
- 커밋: 03dd059 [T-20261027-public-launch][S5][wip] auto checkpoint (stop)
- 다음: S6

## [2026-10-27 18:16] S5 | orchestrator | DONE
- 한 일: 패키지 메타데이터 검증 통과
- 변경 파일(미커밋, .ai 제외): pyproject.toml 
- 커밋: 03dd059 [T-20261027-public-launch][S5][wip] auto checkpoint (stop)
- 다음: S6 시작

## [2026-10-27 18:16] S6 | orchestrator | START
- 한 일: README·CHANGELOG·0.1.1
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6413aa5 [T-20261027-public-launch][s5] 패키지 메타데이터

## [2026-10-27 18:17] S6 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6413aa5 [T-20261027-public-launch][s5] 패키지 메타데이터
- 메모: STATE.md의 '다음 행동' 확인 후 이어서
