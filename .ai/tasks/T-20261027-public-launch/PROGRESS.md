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
