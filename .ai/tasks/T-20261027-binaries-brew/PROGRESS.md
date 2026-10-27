# PROGRESS — T-20261027-binaries-brew

> append-only.

---

## [2026-10-27 20:53] S0 | planner(opus) | DONE
- 한 일: PLAN 10단계, PyInstaller 사용자 확인, §7 기본값
- 변경 파일(미커밋, .ai 제외): openspec/changes/binaries-brew/ 
- 커밋: 6212771 [T-20261027-adoption-links][done] 사용 현황 배지·uvx 안내·프로젝트 링크, PyPI 0.1.3
- 다음: S1

## [2026-10-27 20:53] S1 | orchestrator | START
- 한 일: 빌더 결정 기록
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 29267c8 [T-20261027-binaries-brew][plan] OS별 실행 파일 + Homebrew 탭 (approved, PyInstaller 사용자 확인)

## [2026-10-27 20:53] S1 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 29267c8 [T-20261027-binaries-brew][plan] OS별 실행 파일 + Homebrew 탭 (approved, PyInstaller 사용자 확인)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 20:55] S1 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): docs/decisions.md packaging/ scripts/build_binary.py 
- 커밋: 2398153 [T-20261027-binaries-brew][S1][wip] auto checkpoint (stop)

## [2026-10-27 20:56] S1 | implementer(opus) | DONE
- 한 일: decisions.md 빌더 비교·Homebrew 결정, 출처 3+1
- 변경 파일(미커밋, .ai 제외): docs/decisions.md packaging/ scripts/build_binary.py 
- 커밋: 2398153 [T-20261027-binaries-brew][S1][wip] auto checkpoint (stop)
- 다음: S2

## [2026-10-27 20:56] S2 | implementer(opus) | DONE
- 한 일: build_binary.py·hwp2md_entry.py, macos-arm64 17.6MiB 7초, --version·not-HWP rc=3·serve health·pkg zip 2·LANG=C 변환 OK
- 변경 파일(미커밋, .ai 제외): packaging/ scripts/build_binary.py 
- 커밋: 3f97129 [T-20261027-binaries-brew][s1] 빌더 결정 기록
- 다음: S3

## [2026-10-27 20:56] S3 | orchestrator | START
- 한 일: formula 생성기
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ac76054 [T-20261027-binaries-brew][s2] PyInstaller 빌드 스크립트

## [2026-10-27 20:56] S3 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ac76054 [T-20261027-binaries-brew][s2] PyInstaller 빌드 스크립트
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 20:57] S3 | implementer(opus) | DONE
- 한 일: update_formula.py·단위 8·탭 README, ruby -c OK, unit 828
- 변경 파일(미커밋, .ai 제외): packaging/homebrew/ scripts/update_formula.py tests/unit/test_update_formula.py 
- 커밋: d26bcec [T-20261027-binaries-brew][S3][wip] auto checkpoint (stop)
- 다음: S4

## [2026-10-27 20:57] S4 | orchestrator | START
- 한 일: 설치 문서·CHANGELOG·0.1.4
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4c7bcdf [T-20261027-binaries-brew][s3] Homebrew formula 생성기

## [2026-10-27 20:58] S4 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4c7bcdf [T-20261027-binaries-brew][s3] Homebrew formula 생성기

## [2026-10-27 20:58] S4 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4c7bcdf [T-20261027-binaries-brew][s3] Homebrew formula 생성기
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 20:59] S4 | implementer(opus) | DONE
- 한 일: README·README.en Python 없이 소절, releasing binaries·탭 갱신, CHANGELOG 0.1.4, __version__ 0.1.4. unit 828, e2e 12
- 변경 파일(미커밋, .ai 제외): CHANGELOG.md README.en.md README.md docs/releasing.md src/hwp2md/__init__.py 
- 커밋: be379f7 [T-20261027-binaries-brew][S4][wip] auto checkpoint (stop)
- 다음: S5
