# OS별 단일 실행 파일 + GitHub Release 자산 + Homebrew 탭

## Why

hwp2md 는 PyPI(`hwp2markdown`)와 `uvx` 로만 받을 수 있어 Python·uv 가 없는 사용자는 쓰지 못한다. HWP 를 다루는 사용자 다수는 Python 을 설치하지 않는다. OS별 실행 파일 하나를 내려받거나 `brew install` 한 줄로 설치할 수 있어야 한다.

## What Changes

- PyInstaller(onefile)로 `hwp2md` 단일 실행 파일을 만드는 `scripts/build_binary.py` 와 진입 스크립트 `packaging/pyinstaller/hwp2md_entry.py` 를 더한다. web extra(Starlette·uvicorn), `static/`(vendor 글꼴 포함), `/pkg/hwp2md.zip` 이 쓰는 `hwp2md`·`olefile` 의 `.py` 원본을 실행 파일 안에 싣는다.
- 대상 4종: `hwp2md-windows-x64.exe`, `hwp2md-macos-arm64`, `hwp2md-macos-x64`, `hwp2md-linux-x64`. 코드 서명은 하지 않는다(macOS 는 PyInstaller 의 ad-hoc 서명만).
- `.github/workflows/release.yml` 에 OS matrix job `binaries`(빌드 → 같은 러너에서 스모크)와 job `github-release`(`contents: write` 는 이 job 에만, 4개 실행 파일 + `SHA256SUMS` 업로드)를 더한다. 기존 `build`·`publish`(Trusted Publishing)는 바꾸지 않는다.
- `scripts/update_formula.py` 가 Release 의 `SHA256SUMS` 로 Homebrew 바이너리 formula 를 생성한다. 새 공개 저장소 `ilyos-numon/homebrew-tap` 의 `Formula/hwp2md.rb` 에 orchestrator 가 커밋·push 한다(토큰 secret 없음).
- 실행 파일 스모크를 E2E 로 둔다: `tests/e2e/test_binary_smoke.py` (`--version`, 합성 HWPX 변환, serve 헬스·static·pkg zip, 손상 파일·not-HWP 입력의 비0 종료).
- README·README.en 설치 절(brew·실행 파일 다운로드, Gatekeeper·SmartScreen 경고 해제), `docs/releasing.md`, `CHANGELOG.md`, `docs/decisions.md`(빌더 비교와 출처 URL) 갱신, 버전 0.1.4.

## Capabilities

### New Capabilities
- `binary-distribution`: OS별 단일 실행 파일, Release 자산·체크섬, Homebrew 탭 formula, 실행 파일 스모크

### Modified Capabilities
- 없음 (`distribution` 의 PyPI 요구사항은 그대로다)

## Impact

- 새 파일: `scripts/build_binary.py`, `scripts/update_formula.py`, `packaging/pyinstaller/hwp2md_entry.py`, `packaging/homebrew/README.md`, `tests/unit/test_update_formula.py`, `tests/e2e/test_binary_smoke.py`
- 변경: `.github/workflows/release.yml`, `README.md`, `README.en.md`, `docs/releasing.md`, `docs/decisions.md`, `CHANGELOG.md`, `src/hwp2md/__init__.py`(버전)
- 새 외부 저장소: `ilyos-numon/homebrew-tap` (공개)
- `pyproject.toml`·`uv.lock` 은 바꾸지 않는다. PyInstaller 는 `uv run --with pyinstaller==6.22.3` 으로만 쓴다.
