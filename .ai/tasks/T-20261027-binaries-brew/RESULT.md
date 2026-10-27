# RESULT — T-20261027-binaries-brew OS별 실행 파일 + GitHub Release + Homebrew 탭

> 작성: scribe · 2026-10-27 21:22 · 최종 상태: DONE_WITH_ISSUES
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 됨: v0.1.4 배포. GitHub Release 에 실행 파일 4개 + SHA256SUMS, 4개 러너 스모크 success (Release run 40501210934). PyPI 0.1.4. `brew install ilyos-numon/tap/hwp2md` 설치·brew test 통과 (확인 후 uninstall/untap 완료).
- 안 됨/미확인: S7 lint·mypy, S8 actionlint, S9 권한 grep, S13 `shasum -c` 는 실행 로그가 없다 (리뷰어 PASS 판정에만 근거). 재확인 필요.
- 지금 바로 쓸 수 있다. 실행 파일은 미서명이라 macOS Gatekeeper / Windows SmartScreen 경고가 뜬다 (README 안내).

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| S1 | 로컬 실행 파일 빌드 | ✅ | `logs/s2-build.log` `build_binary: OK build/bin/hwp2md-macos-arm64 18481232`, `logs/s6-build.log` 18481408 bytes (≤80 MiB) |
| S2 | 실행 파일 버전 | ✅ | `logs/s7-release.log` `hwp2md 0.1.4`, `logs/s9-brew.log` `hwp2md 0.1.4` |
| S3 | formula 생성기 단위 | ✅ (건수 확인 필요) | `logs/s3-unit.log` 전체 unit 828 passed. test_update_formula 개별 건수 로그 없음 |
| S4 | 실행 파일 E2E | ✅ | `logs/s6-e2e.log` 7 passed |
| S5 | 전체 E2E | ✅ | `logs/e2e.log` 157 passed, exit=0 |
| S6 | 단위 회귀 | ✅ | `logs/s4-unit.log` 828 passed |
| S7 | lint·타입 | ❓ 확인 필요 | 실행 로그 없음. 리뷰어 PASS 판정만 |
| S8 | 워크플로우 정적 검사 | ❓ 확인 필요 | `logs/s5-actionlint.log` 0줄 (빈 파일). 리뷰어 PASS 판정만 |
| S9 | 권한·기존 job 불변 | ❓ 확인 필요 | grep 결과 로그 없음. 리뷰어 PASS 판정만 |
| S10 | Release 자산 5개 | ✅ | `logs/s7-release.log` SHA256SUMS, hwp2md-linux-x64, hwp2md-macos-arm64, hwp2md-macos-x64, hwp2md-windows-x64.exe |
| S11 | 각 OS 러너 스모크 | ✅ | `logs/s7-release.log` binaries 4개 job 모두 success |
| S12 | PyPI 게시 | ✅ | `logs/s7-release.log` pypi 0.1.4 |
| S13 | 체크섬 | ❓ 확인 필요 | `shasum -a 256 -c` 로그 없음. 리뷰어: formula sha256 = 실제 SHA256SUMS |
| S14 | Homebrew | ✅ | `logs/s9-brew.log` 설치, `hwp2md 0.1.4`, brew test 통과 |
| S15 | 익명화 | ✅ | 최종 재실행 `sanitize-check: OK (22 patterns, hwp2md)`, exit 0 |
| S16 | OpenSpec | ✅ | `logs/openspec-validate.log` `Change 'binaries-brew' is valid`, 아카이브 완료 `logs/openspec-archive.log` |

UI 변경 없음 (스크린샷 기준 없음).

## 변경 요약
- 커밋 범위: `29267c8..d33b052` (18 commits, 그중 `[wip] auto checkpoint` 4개). 현재 브랜치 `ai/T-20261027-binaries-brew` 에만 3개(`b2431a9..d33b052`)가 있고 main 에 미반영.
- 추가/수정 파일: 코드·문서 13개 (+951 / -2), 핵심: `scripts/build_binary.py`, `scripts/update_formula.py`, `packaging/pyinstaller/hwp2md_entry.py`, `packaging/homebrew/README.md`, `.github/workflows/release.yml`, `tests/e2e/test_binary_smoke.py`, `tests/unit/test_update_formula.py`, `src/hwp2md/__init__.py`(0.1.4). 아카이브 커밋 대상: `openspec/changes/archive/2026-10-27-binaries-brew/`, `openspec/specs/binary-distribution/`.
- 새 의존성: 없음 (PyInstaller 6.22.3 은 `uv run --with` 로만, pyproject·uv.lock 미변경)
- 새 환경변수: 없음

## 테스트
- 단위: `uv run pytest tests/unit -q` → pass 828
- E2E: `uv run pytest tests/e2e -q` → pass 157 (exit 0)
  - 실행 파일 스모크 — 성공·실패 경로 7개 (`HWP2MD_BINARY` 지정)
- 외부 검증: Release 4개 러너 스모크 success, PyPI 0.1.4, brew install/test 확인

## 실행 방법
```bash
# macOS (Homebrew)
brew install ilyos-numon/tap/hwp2md && hwp2md --version

# 실행 파일 직접 받기 (Python 불필요, 압축 없음)
curl -L -o hwp2md https://github.com/ilyos-numon/hwp2md/releases/latest/download/hwp2md-macos-arm64
# 자산: hwp2md-windows-x64.exe / hwp2md-macos-arm64 / hwp2md-macos-x64 / hwp2md-linux-x64

# 설치 방법 4줄 요약
# 1. 브라우저: 확인 필요 (이 태스크에서 사용 경로 미확정)
# 2. pip / uvx: PyPI `hwp2markdown` 0.1.4 (정확한 명령은 README 확인 필요)
# 3. brew: brew install ilyos-numon/tap/hwp2md
# 4. 실행 파일: GitHub Release latest 의 OS별 파일
```

## 못 한 것 / 알려진 문제
- S8 저장소 생성·push 가 권한 판정에 막혀 BLOCKED 1회 — 사용자가 웹에서 탭 저장소 생성, 이름 오타(hombrew-tap)를 rename, 사용자가 push 권한 허용 후 push 로 해소. 탭 formula 갱신은 수동.
- 실행 파일 미서명 — Gatekeeper/SmartScreen 경고. 서명·공증은 OUT 으로 제외.
- macos-15-intel 러너가 사라지면 macos-x64 빌드 대응 필요.
- 증거 로그 누락 4건 (S7/S8/S9/S13) — 재확인 전까지 PASS 는 리뷰어 판정 기준.
- 작업 트리 미정리: 이 브랜치가 main 에 미병합, `openspec/changes/binaries-brew/` 삭제·아카이브 변경이 커밋되지 않음 (`git status` 기준).

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- 탭 저장소 이름: 오타(hombrew-tap) → homebrew-tap 으로 rename (orchestrator 처리). 이유: 오타 방지.
- PyInstaller 6.22.3 onefile 채택 — 사용자 확인 (PLAN Q1).

## 후속 제안 (별도 태스크로)
- 릴리스마다 `uv run python scripts/update_formula.py --version X.Y.Z --out build/homebrew-tap/Formula/hwp2md.rb` 실행 후 탭 커밋·push (`docs/releasing.md`).
- 탭 formula 자동 갱신 (PAT/secret 필요, 사용자 승인 필요).
- 실행 파일 서명·공증 여부 결정.
- Python 3.14 손상 zip 문구, 실제 차트 HWP 샘플, docs/launch 초안 게시 (사용자 작업).

## 비용
- 서브에이전트 호출: 8회 (opus 6 / sonnet 2 / haiku 0) — PROGRESS 기준 집계 (planner 1, implementer 5, test-writer 1, reviewer 1)
- 재시도: 0회 · 차단: 1회 (S8)
