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

## [2026-10-27 20:59] S5 | orchestrator | START
- 한 일: release.yml 실행 파일 job
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4980088 [T-20261027-binaries-brew][s4] 설치 문서와 0.1.4

## [2026-10-27 20:59] S5 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4980088 [T-20261027-binaries-brew][s4] 설치 문서와 0.1.4
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 21:00] S5 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): .github/workflows/release.yml 
- 커밋: 4a1fa29 [T-20261027-binaries-brew][S5][wip] auto checkpoint (stop)

## [2026-10-27 21:00] S5 | implementer(opus) | DONE
- 한 일: release.yml binaries(matrix 4)·github-release 추가, 기존 job 무변경, actionlint 0
- 변경 파일(미커밋, .ai 제외): .github/workflows/release.yml 
- 커밋: 4a1fa29 [T-20261027-binaries-brew][S5][wip] auto checkpoint (stop)
- 다음: S6
- 메모: setup-python@v6 사용

## [2026-10-27 21:00] S6 | orchestrator | START
- 한 일: 실행 파일 E2E
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7f2eb2c [T-20261027-binaries-brew][s5] Release 실행 파일 job

## [2026-10-27 21:00] S6 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7f2eb2c [T-20261027-binaries-brew][s5] Release 실행 파일 job
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 21:03] S6 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_binary_smoke.py 
- 커밋: e602450 [T-20261027-binaries-brew][S6][wip] auto checkpoint (stop)

## [2026-10-27 21:04] S6 | test-writer(sonnet) | DONE
- 한 일: test_binary_smoke.py 7 passed, 전체 e2e 157 exit=0, unit 828, lint·mypy 0
- 변경 파일(미커밋, .ai 제외): tests/e2e/test_binary_smoke.py 
- 커밋: e602450 [T-20261027-binaries-brew][S6][wip] auto checkpoint (stop)
- 다음: S7

## [2026-10-27 21:04] S7 | orchestrator | START
- 한 일: main 반영·CI·v0.1.4
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 41cecb0 [T-20261027-binaries-brew][s6] 실행 파일 스모크 E2E

## [2026-10-27 21:09] S7 | orchestrator | DONE
- 한 일: CI 40500913688 success, v0.1.4 Release 40501210934: build·publish·binaries 4·github-release success, 자산 5, latest 다운로드 체크섬 OK·실행 0.1.4, PyPI 0.1.4
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b73d27 [T-20261027-binaries-brew][s7] 시작 기록
- 다음: S8 탭

## [2026-10-27 21:09] S8 | orchestrator | START
- 한 일: homebrew-tap 저장소·formula
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 90c7318 [T-20261027-binaries-brew][s7] v0.1.4 Release 확인

## [2026-10-27 21:09] S8 | orchestrator | BLOCKED
- 한 일: 공개 저장소 생성(gh repo create --public)이 세션 자동 권한 판정에 막힘. 로컬 build/homebrew-tap 준비 완료: formula 0.1.4 생성, ruby -c OK, brew style 0 offenses, 커밋 377949f, origin 설정
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 90c7318 [T-20261027-binaries-brew][s7] v0.1.4 Release 확인
- 다음: 사용자 U1(웹에서 homebrew-tap 공개 저장소 생성, README 체크 해제) → git -C build/homebrew-tap push -u origin main → S9

## [2026-10-27 21:19] S8 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 9ea74c8 [T-20261027-binaries-brew][s8] 탭 준비 완료, 저장소 생성 대기

## [2026-10-27 21:19] S8 | orchestrator | DONE
- 한 일: 사용자가 탭 저장소 생성(이름 오타 hombrew-tap → orchestrator 가 homebrew-tap 으로 rename), push 권한 허용 후 formula push (탭 377949f)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 9ea74c8 [T-20261027-binaries-brew][s8] 탭 준비 완료, 저장소 생성 대기
- 다음: S9

## [2026-10-27 21:19] S9 | orchestrator | DONE
- 한 일: Release 자산 5·latest 다운로드 체크섬 OK·실행 0.1.4, brew tap·install·hwp2md --version 0.1.4·brew test OK, 확인 후 uninstall·untap (Q5)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 9ea74c8 [T-20261027-binaries-brew][s8] 탭 준비 완료, 저장소 생성 대기
- 다음: S10 리뷰
