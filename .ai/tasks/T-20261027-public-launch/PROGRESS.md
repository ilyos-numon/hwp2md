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

## [2026-10-27 18:17] S6 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): README.md src/hwp2md/__init__.py 
- 커밋: 2790166 [T-20261027-public-launch][S6][wip] auto checkpoint (stop)

## [2026-10-27 18:18] S6 | implementer(opus) | DONE
- 한 일: README 배지5·체험 링크·30초 데모·English·절대 URL, CHANGELOG 0.1.0/0.1.1, __version__ 0.1.1, releasing Pages 절, decisions 2항목. unit 820, C8~C12 통과
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md docs/releasing.md src/hwp2md/__init__.py CHANGELOG.md 
- 커밋: 2790166 [T-20261027-public-launch][S6][wip] auto checkpoint (stop)
- 다음: S7

## [2026-10-27 18:18] S6 | orchestrator | DONE
- 한 일: README·CHANGELOG·0.1.1 검증 통과
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md docs/releasing.md src/hwp2md/__init__.py CHANGELOG.md 
- 커밋: 2790166 [T-20261027-public-launch][S6][wip] auto checkpoint (stop)
- 다음: S7 시작

## [2026-10-27 18:18] S7 | orchestrator | START
- 한 일: Pages 워크플로우·이슈 템플릿
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 8bf492e [T-20261027-public-launch][s6] README·CHANGELOG·0.1.1

## [2026-10-27 18:19] S7 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 8bf492e [T-20261027-public-launch][s6] README·CHANGELOG·0.1.1
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 18:19] S7 | implementer(opus) | DONE
- 한 일: pages.yml(비공개면 build 건너뜀)·bug_report.yml·config.yml, actionlint 0, yaml ok, 로컬 빌드 OK
- 변경 파일(미커밋, .ai 제외): .github/ISSUE_TEMPLATE/ .github/workflows/pages.yml 
- 커밋: d1f4653 [T-20261027-public-launch][S7][wip] auto checkpoint (stop)
- 다음: S8
- 메모: configure-pages@v6, upload-pages-artifact@v5, deploy-pages@v5

## [2026-10-27 18:19] S7 | orchestrator | DONE
- 한 일: Pages 워크플로우·이슈 템플릿 검증 통과
- 변경 파일(미커밋, .ai 제외): .github/ISSUE_TEMPLATE/ .github/workflows/pages.yml 
- 커밋: d1f4653 [T-20261027-public-launch][S7][wip] auto checkpoint (stop)
- 다음: S8 시작

## [2026-10-27 18:19] S8 | orchestrator | START
- 한 일: 홍보 초안
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c85664e [T-20261027-public-launch][s7] Pages 워크플로우·이슈 템플릿

## [2026-10-27 18:20] S8 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c85664e [T-20261027-public-launch][s7] Pages 워크플로우·이슈 템플릿
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 18:20] S8 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0b73f8a [T-20261027-public-launch][S8][wip] auto checkpoint (stop)

## [2026-10-27 18:20] S8 | implementer(opus) | DONE
- 한 일: docs/launch community-post(제목 3·본문 2206자)·sns-post(442자·해시태그 5), sanitize OK
- 변경 파일(미커밋, .ai 제외): docs/launch/ 
- 커밋: 0b73f8a [T-20261027-public-launch][S8][wip] auto checkpoint (stop)
- 다음: S9

## [2026-10-27 18:20] S8 | orchestrator | DONE
- 한 일: 홍보 초안 검증 통과
- 변경 파일(미커밋, .ai 제외): docs/launch/ 
- 커밋: 0b73f8a [T-20261027-public-launch][S8][wip] auto checkpoint (stop)
- 다음: S9 시작

## [2026-10-27 18:20] S9 | orchestrator | START
- 한 일: 게이트 전 전체 검증 + 브랜치 CI
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6ddc765 [T-20261027-public-launch][s8] 홍보 초안

## [2026-10-27 18:24] S9 | orchestrator | DONE
- 한 일: 로컬: lint·mypy·unit 820·dist OK(0.1.1)·pages 빌드·e2e 134 exit=0·sanitize OK. 브랜치 CI run 40480246576 6 job success
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: cbe79b4 [T-20261027-public-launch][s9] 로컬 검증 기록
- 다음: S10 게이트 준비

## [2026-10-27 18:24] S10 | orchestrator | START
- 한 일: 게이트 준비: PR 0건·bundle 백업
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 675b244 [T-20261027-public-launch][s9] 게이트 전 검증 기록

## [2026-10-27 18:24] S10 | orchestrator | PARTIAL
- 한 일: 게이트 준비 완료: PR 0건, bundle 백업·verify·복원 클론(v0.1.0 확인), 지울 경로 145건(고유 73)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 675b244 [T-20261027-public-launch][s9] 게이트 전 검증 기록
- 다음: 사용자 승인 후 §5 Stage 10 절차 3번부터

## [2026-10-27 18:25] S10 | orchestrator | START
- 한 일: 사용자 승인: '응 모든거 진행해. 승인' (force-push + 공개 전환)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 03e8faf [T-20261027-public-launch][s10] 게이트 준비 기록 (백업 완료)

## [2026-10-27 18:27] S10 | orchestrator | BLOCKED
- 한 일: 로컬: main 병합(12a9360→재작성 후 bb92d8a), filter-repo 2회(스캐폴드 CLAUDE.md 끝 메모 규칙 추가), V1=0 V2=0 V3=0 V4 same 5/5, unit 820, sanitize OK. 원격 force-push 가 세션 권한 설정에 막힘(원격 변경 없음)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: bb92d8a Merge ai/T-20261027-public-launch: 공개 출시 준비
- 다음: 사용자가 force-push 허용 또는 직접 실행 → 원격 main 외 브랜치 삭제 → 공개 전환

## [2026-10-27 18:54] S10 | orchestrator | BLOCKED
- 한 일: 사용자가 force-push·브랜치 삭제 직접 실행, 원격 main f565631·v0.1.0 7df3e99 로컬과 일치 확인. 공개 전환 명령은 세션 자동 권한 판정에 막힘
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: f565631 [T-20261027-public-launch][s10] 이력 재작성 완료, push 권한 대기
- 다음: 사용자가 공개 전환 → C13~C15 확인 → S11 Pages

## [2026-10-27 18:58] S10 | orchestrator | DONE
- 한 일: C13 V1~V3 0, C14 V4 same 5/5, C15 public·heads 1·main 일치(사용자가 push·공개 직접 실행). 새 main f565631, 새 v0.1.0 커밋 ad3428b
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5c3928e [T-20261027-public-launch][s10] 원격 이력 교체 확인, 공개 전환 대기
- 다음: S11 Pages

## [2026-10-27 18:58] S11 | orchestrator | START
- 한 일: Pages 활성화
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 04cdef6 [T-20261027-public-launch][s10] 이력 정리·공개 전환 기록

## [2026-10-27 18:59] S11 | orchestrator | DONE
- 한 일: Pages build_type=workflow 활성화, pages run 40484851333 build·deploy success, /, convert.html, pkg/hwp2md.zip 200 (C16)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: da0311d [T-20261027-public-launch][s11] Pages 활성화 시작
- 다음: S12 v0.1.1

## [2026-10-27 18:59] S12 | orchestrator | START
- 한 일: v0.1.1 릴리스
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: e2b118a [T-20261027-public-launch][s11] Pages 배포 기록
