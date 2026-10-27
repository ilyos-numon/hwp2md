# PLAN — T-20261027-binaries-brew OS별 단일 실행 파일 + GitHub Release 자산 + Homebrew 탭

> 작성: opus (planner) · 2026-10-27 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: DONE)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> 환경 사실(planner 확인): 로컬 `uname -m` = arm64, Homebrew 7.0.9 있음, ruby 2.6 있음, actionlint 없음, `uv run python` = 3.12.13 (Py_ENABLE_SHARED=1). `ilyos-numon/homebrew-tap` 저장소는 아직 없음(404). PyInstaller 최신 릴리스 v6.22.3.

## 0. 한 줄 목표
사용자는 Python 없이 GitHub Release 에서 OS별 실행 파일 하나를 내려받거나 `brew install ilyos-numon/tap/hwp2md` 한 줄로 설치해 `hwp2md 문서.hwp -o out/` 과 `hwp2md serve` 를 쓸 수 있다.

### 0.1 OpenSpec 연동
- change: `openspec/changes/binaries-brew/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate binaries-brew` (planner 작성 시점 `Change 'binaries-brew' is valid`)
- capability: `binary-distribution` (신규). 기존 `distribution` 요구사항은 바꾸지 않는다.
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행.

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | decisions.md 빌더 비교·결정·출처 URL | S1 |
| 1.2 | build_binary.py + 진입 스크립트, 로컬 macOS arm64 빌드 | S2 |
| 2.1 | update_formula.py + 단위 테스트 + 탭 README 원본 | S3 |
| 3.1 | README·README.en·releasing·CHANGELOG·버전 0.1.4 | S4 |
| 4.1 | release.yml binaries·github-release job | S5 |
| 5.1 | test_binary_smoke.py 작성·로컬 전체 검증 | S6 |
| 6.1 | main 반영·CI·태그 v0.1.4·Release·PyPI 확인 | S7 |
| 6.2 | homebrew-tap 저장소 생성·formula push | S8 |
| 7.1 | 배포물 E2E (체크섬·실행 파일·brew install/test·러너 로그) | S9 |
| 7.2 | 리뷰·RESULT | S10 |

## 1. 범위
### 포함 (IN)
- `scripts/build_binary.py` (신규): PyInstaller onefile 빌드, 플랫폼 자동 판별, 데이터 동봉.
- `packaging/pyinstaller/hwp2md_entry.py` (신규): 동결 진입점, stdout/stderr UTF-8 보정 후 `hwp2md.cli.main()`.
- `scripts/update_formula.py` (신규) + `tests/unit/test_update_formula.py` (신규) + `packaging/homebrew/README.md` (신규, 탭 저장소 README 원본).
- `tests/e2e/test_binary_smoke.py` (신규): 실행 파일 스모크 = E2E (성공·실패 경로).
- `.github/workflows/release.yml`: job `binaries`(matrix 4) + `github-release` 추가.
- `README.md`, `README.en.md` 설치 절, `docs/releasing.md`, `docs/decisions.md`, `CHANGELOG.md`, `src/hwp2md/__init__.py`(`__version__ = "0.1.4"`).
- 외부: 공개 저장소 `ilyos-numon/homebrew-tap` (`Formula/hwp2md.rb`, `README.md`), GitHub Release `v0.1.4`, PyPI `hwp2markdown` 0.1.4.

### 제외 (OUT) — 절대 건드리지 않는다
- 코드 서명·공증(Apple Developer ID, notarization, Authenticode 인증서 구매). 경고 해제 안내만.
- Docker 이미지, winget·scoop·apt·snap·AUR, Homebrew core 등록, Homebrew cask.
- Linux arm64·Windows arm64·macOS universal2 실행 파일.
- 탭 자동 갱신(크로스 저장소 PAT·secret) — §7 Q3 대안으로만.
- `release.yml` 의 기존 `build`·`publish` job 내용, Trusted Publishing·environment `pypi` 설정.
- `pyproject.toml`·`uv.lock` (PyInstaller 는 `uv run --with` 로만), `.github/workflows/ci.yml`, `.github/workflows/pages.yml`.
- `src/hwp2md/cli.py`, `src/hwp2md/web/**` 의 동작 변경 (실행 파일은 코드 수정 없이 데이터 동봉으로 맞춘다).
- 기존 테스트 수정·skip.

### 건드리면 안 되는 파일/디렉토리
- orchestrator 전용: `pyproject.toml`, `uv.lock`, `.gitignore`, `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.github/**` (S5 단독 단계에서 `release.yml` 만), `src/hwp2md/cli.py`.
- `src/hwp2md/**` 전체 (S4 의 `src/hwp2md/__init__.py` 버전 한 줄만 예외), `tests/e2e/conftest.py`, 기존 `tests/**/*.py`.
- `doc/my_info/` (워크스페이스 루트, 읽기 전용).

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| S1 | 로컬 실행 파일 빌드 | `cd /Users/illi/illy-projects/hwp2md && unset VIRTUAL_ENV && uv run --with pyinstaller==6.22.3 python scripts/build_binary.py --out build/bin` | 종료 0, 마지막 줄 `build_binary: OK build/bin/hwp2md-macos-arm64 <bytes>`, bytes ≤ 83886080(80 MiB) |
| S2 | 실행 파일 버전 | `build/bin/hwp2md-macos-arm64 --version` | 종료 0, `hwp2md 0.1.4` (S4 이전엔 `hwp2md 0.1.3`) |
| S3 | formula 생성기 단위 테스트 | `uv run pytest tests/unit/test_update_formula.py -q` | 실패 0, 5개 이상 pass |
| S4 | 실행 파일 E2E (성공·실패 경로) | `HWP2MD_BINARY=build/bin/hwp2md-macos-arm64 uv run pytest tests/e2e/test_binary_smoke.py -q` | 실패 0, 7개 이상 pass (§4.6 케이스) |
| S5 | 전체 E2E 회귀 없음 | `uv run pytest tests/e2e -q` | 실패 0 (`test_binary_smoke.py` 는 env 없을 때 세션당 1회 빌드) |
| S6 | 단위 회귀 없음 | `uv run pytest tests/unit -q` | 실패 0 |
| S7 | lint·타입 | `uv run ruff check --no-cache src tests scripts packaging && uv run ruff format --no-cache --check src tests scripts packaging && uv run mypy src` | 종료 0 |
| S8 | 워크플로우 정적 검사 | `uvx --from actionlint-py actionlint .github/workflows/release.yml` (실패 시 `ruby -ryaml -e 'YAML.load_file(".github/workflows/release.yml")'`) | 종료 0, 출력 없음 |
| S9 | 권한·기존 job 불변 | `command grep -c "contents: write" .github/workflows/release.yml` · `git diff main -- .github/workflows/release.yml \| command grep '^-[^-]'` | `1` · 출력 없음(삭제·수정 줄 0) |
| S10 | Release 자산 | `GH_TOKEN=$(gh auth token --user ilyos-numon) gh release view v0.1.4 -R ilyos-numon/hwp2md --json assets --jq '[.assets[].name]\|sort\|join(",")'` | `SHA256SUMS,hwp2md-linux-x64,hwp2md-macos-arm64,hwp2md-macos-x64,hwp2md-windows-x64.exe` |
| S11 | 각 OS 러너 스모크 | `gh run view <릴리스 run id> -R ilyos-numon/hwp2md --json jobs --jq '.jobs[]\|select(.name\|startswith("binaries"))\|.conclusion'` | `success` 4줄 |
| S12 | PyPI 게시 유지 | `curl -sf https://pypi.org/pypi/hwp2markdown/0.1.4/json \| python3 -c "import sys,json;print(json.load(sys.stdin)['info']['version'])"` | `0.1.4` |
| S13 | 체크섬 | Release 자산 5개를 빈 디렉터리에 받아 `shasum -a 256 -c SHA256SUMS` | 4줄 모두 `OK`, 종료 0 |
| S14 | Homebrew | `brew install ilyos-numon/tap/hwp2md && brew test hwp2md && $(brew --prefix)/bin/hwp2md --version` | 각 종료 0, 마지막 출력 `hwp2md 0.1.4` |
| S15 | 익명화 | `cd /Users/illi/illy-projects && ./scripts/sanitize-check.sh hwp2md` (루트에서 실행해야 함 — 프로젝트 폴더에서는 path not found) | 종료 0 |
| S16 | OpenSpec | `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate binaries-brew` | `is valid` |

UI 변경 없음 — 스크린샷 기준 없음 (serve 화면은 기존 E2E 가 이미 본다. 실행 파일 serve 는 HTTP 로 확인).

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 단계 재시도 3회 초과.
- 같은 오류로 수정 2회 실패 (예: PyInstaller 가 같은 hidden import 로 두 번 실패).
- 단계 하나 도구 호출 40회 초과 → PARTIAL 반환, 60회에서 강제 중단. 빌드·CI 대기 포함 단계당 45분 초과.
- 실행 파일이 80 MiB 초과 → 제외 모듈 조정 1회 후에도 초과면 BLOCKED (§8).
- `src/hwp2md/cli.py`·`src/hwp2md/web/**`·`pyproject.toml` 수정 없이는 동결 실행 파일이 동작하지 않음 → BLOCKED (planner 재호출, 해당 파일 단독 단계 신설).
- Release CI 의 같은 job 이 같은 원인으로 2회 실패 → 태그 삭제 후 BLOCKED (PyPI 는 이미 게시됐을 수 있음: 그 경우 다음 수정은 0.1.5).
- 새 공개 저장소 생성·공개 노출이 권한 판정에 막힘 → 사용자 수동 단계 U1(§5 S8) 로 넘기고 그 단계만 BLOCKED, 나머지 기록은 진행.
- 자격증명·결제·PAT 발급이 필요해짐 → BLOCKED.

## 4. 인터페이스 계약 (병렬 작업 전 확정)

### 4.1 플랫폼·자산 이름 (모든 단계 공통, 변경 금지)
| platform | 러너 (release.yml) | 자산 이름 | 판별 (`sys.platform`, `platform.machine().lower()`) |
|----------|-------------------|-----------|------|
| `windows-x64` | `windows-2022` | `hwp2md-windows-x64.exe` | `win32`, `amd64`/`x86_64` |
| `macos-arm64` | `macos-15` | `hwp2md-macos-arm64` | `darwin`, `arm64` |
| `macos-x64` | `macos-15-intel` | `hwp2md-macos-x64` | `darwin`, `x86_64` |
| `linux-x64` | `ubuntu-22.04` | `hwp2md-linux-x64` | `linux`, `x86_64`/`amd64` |

자산에 버전을 넣지 않는다. 고정 링크: `https://github.com/ilyos-numon/hwp2md/releases/latest/download/<자산 이름>`. 버전 링크: `https://github.com/ilyos-numon/hwp2md/releases/download/v<버전>/<자산 이름>`. 압축하지 않은 실행 파일 그대로.

### 4.2 `scripts/build_binary.py` CLI
```
python scripts/build_binary.py [--out DIR] [--platform {windows-x64,macos-arm64,macos-x64,linux-x64}]
  --out       기본 build/bin (저장소 루트 기준, .gitignore 의 build/ 에 포함)
  --platform  기본 자동 판별(§4.1). 현재 OS 와 다른 값은 종료 2 (교차 빌드 안 함)
종료: 0 성공 | 1 PyInstaller 실패 또는 산출물 없음 | 2 사용법·지원 안 하는 플랫폼·PyInstaller 미설치
stdout 마지막 줄(성공): build_binary: OK <out>/<자산 이름> <bytes>
stderr(2): build_binary: unsupported platform <sys.platform>/<machine>
           build_binary: PyInstaller not installed — uv run --with pyinstaller==6.22.3 python scripts/build_binary.py
```
PyInstaller 호출(`PyInstaller.__main__.run([...])`) 필수 옵션: `--onefile --noconfirm --clean --console --name <자산 이름에서 .exe 뺀 것> --distpath <out> --workpath build/pyinstaller/work --specpath build/pyinstaller --collect-submodules uvicorn --hidden-import hwp2md.web.server --hidden-import hwp2md.web.app --add-data <stage>/hwp2md<sep>hwp2md --add-data <stage>/olefile<sep>olefile --exclude-module tkinter --exclude-module pytest --exclude-module playwright --exclude-module mypy` + 진입 스크립트 `packaging/pyinstaller/hwp2md_entry.py`. `<sep>` 는 `os.pathsep`.
- `<stage>` = `build/pyinstaller/stage` (매 실행 시 지우고 새로 만든다). `stage/hwp2md` = `src/hwp2md` 복사(`__pycache__`·`*.pyc` 제외), `stage/olefile` = 설치된 `olefile` 패키지의 `*.py` 만.
- 결과 파일이 없으면 종료 1.

### 4.3 `packaging/pyinstaller/hwp2md_entry.py`
```python
# 동작 계약: stdout·stderr 의 encoding 이 utf-8(대소문자·하이픈 무시)이 아니면
#   stream.reconfigure(encoding="utf-8", errors="replace") 후
#   raise SystemExit(hwp2md.cli.main())
from hwp2md.cli import main
```
`hwp2md.cli` 는 수정하지 않는다.

### 4.4 `SHA256SUMS` 형식
- 실행 파일 4개만, 파일 이름 오름차순, 줄 형식 `<소문자 hex 64자><공백 2칸><자산 이름>\n`, UTF-8, 마지막 줄도 `\n`. `sha256sum`·`shasum -a 256 -c` 호환. 생성: `github-release` job 에서 `sha256sum hwp2md-* | sort -k2 > SHA256SUMS`.

### 4.5 `scripts/update_formula.py` CLI (stdlib 만)
```
python scripts/update_formula.py --version X.Y.Z [--sums PATH | --sums-url URL] [--repo OWNER/NAME] [--out PATH]
  --version   필수, ^\d+\.\d+\.\d+$ (앞에 v 붙이면 종료 2)
  --sums      로컬 SHA256SUMS 파일
  --sums-url  둘 다 없으면 https://github.com/<repo>/releases/download/v<version>/SHA256SUMS 를 urllib 로 받는다
  --repo      기본 ilyos-numon/hwp2md
  --out       기본 stdout. 부모 디렉터리가 없으면 만든다
종료: 0 성공 | 1 SHA256SUMS 형식 오류·필수 자산 누락·내려받기 실패 | 2 사용법
stderr: update_formula: OK <out|-> version=<v>
        update_formula: FAIL missing <자산 이름>
        update_formula: FAIL bad line <줄 번호>
        update_formula: FAIL download <url>: <이유>
```
필수 자산: `hwp2md-macos-arm64`, `hwp2md-macos-x64`, `hwp2md-linux-x64` (windows 줄은 있어도 무시). 같은 입력 → 바이트 단위 같은 출력. 순수 함수 `render_formula(version: str, repo: str, sums: dict[str, str]) -> str` 와 `parse_sums(text: str) -> dict[str, str]` 를 모듈 수준에 둔다(단위 테스트용).

생성 formula 구조 (정확히 이 모양, 2칸 들여쓰기):
```ruby
class Hwp2md < Formula
  desc "Convert Korean HWP, HWPX and HWPML documents to Markdown"
  homepage "https://github.com/ilyos-numon/hwp2md"
  version "0.1.4"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/ilyos-numon/hwp2md/releases/download/v0.1.4/hwp2md-macos-arm64"
      sha256 "<64 hex>"
    end
    on_intel do
      url "https://github.com/ilyos-numon/hwp2md/releases/download/v0.1.4/hwp2md-macos-x64"
      sha256 "<64 hex>"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/ilyos-numon/hwp2md/releases/download/v0.1.4/hwp2md-linux-x64"
      sha256 "<64 hex>"
    end
  end

  def install
    bin.install Dir["hwp2md-*"].first => "hwp2md"
  end

  test do
    assert_match "hwp2md #{version}", shell_output("#{bin}/hwp2md --version")
    (testpath/"note.txt").write "not a hwp document"
    output = shell_output("#{bin}/hwp2md #{testpath}/note.txt -o #{testpath}/out 2>&1", 3)
    assert_match "not an HWP 5.0 file", output
  end
end
```
파일 첫 줄 위에 주석 `# Generated by scripts/update_formula.py in ilyos-numon/hwp2md. Do not edit by hand.` 한 줄.

### 4.6 `tests/e2e/test_binary_smoke.py` 계약
- 실행 파일 결정: env `HWP2MD_BINARY` 가 있으면 그 경로(없는 파일이면 `pytest.fail`). 없으면 session fixture 가 `uv run --with pyinstaller==6.22.3 python scripts/build_binary.py --out <tmp_path_factory 디렉터리>` 를 1회 실행(타임아웃 900초)하고 `build_binary: OK` 줄의 경로를 쓴다. 빌드 실패는 `pytest.fail` (skip 금지).
- 모든 subprocess 는 `env` 에서 `PYTHONIOENCODING`·`PYTHONUTF8` 를 제거한 상태로 실행한다(동결 진입점의 UTF-8 보정을 검증하기 위해). `PATH` 는 유지.
- 케이스 (최소 7개):
  1. `--version` → 0, stdout `hwp2md <hwp2md.__version__>`.
  2. 합성 HWPX(`tests/synth_hwpx.write_hwpx` 사용) 변환 → 0, `<out>/<stem>.md` 존재, 합성 문단 텍스트 포함, stdout 에 `✓`.
  3. 합성 HWP 5.0(`synth_hwp5.write_hwp5`, `FIXTURE_PARAGRAPHS`) 변환 → 0, `.md` 에 첫 문단 텍스트.
  4. not-HWP(`note.txt`) → 종료 3, stderr 에 `hwp2md: error: not an HWP 5.0 file`, `Traceback` 없음.
  5. 손상 HWPX(정상 HWPX 의 앞 100바이트, 확장자 `.hwpx`) → 종료 ≠ 0, stderr 에 `hwp2md: error:`, `Traceback` 없음.
  6. 없는 파일 → 종료 2, stderr `hwp2md: error: file not found`.
  7. `serve --no-browser --port <빈 포트>` → 60초 안에 `/api/health` 200 + `version` 일치, `/static/vendor/fonts/PretendardVariable.woff2` 200 + 본문이 `src/hwp2md/web/static/vendor/fonts/PretendardVariable.woff2` 와 같음, `/` 200 + `text/html`, `/pkg/hwp2md.zip` 200 + 항목에 `hwp2md/__init__.py`·`hwp2md/convert.py`·`olefile/olefile.py` 있고 `hwp2md/web/` 접두 항목 0개, `POST /api/convert?name=a.hwpx` (합성 HWPX 본문) 200. 종료 시 프로세스 terminate→5초 후 kill.
- 포트: `_free_port()` 패턴(소켓 bind 0). 8770·8771 고정 사용 금지.

### 4.7 release.yml 추가 job 계약
```yaml
  binaries:
    needs: build
    strategy: { fail-fast: false, matrix: { include: [§4.1 4행: os, platform, asset] } }
    runs-on: ${{ matrix.os }}
    timeout-minutes: 45
    defaults: { run: { shell: bash } }
    # permissions 없음 (워크플로우 기본 contents: read)
    steps: checkout@v7 → actions/setup-python@v6 (python-version "3.12", id py)
           → astral-sh/setup-uv@v7 (enable-cache: true)
           → uv sync --locked --python "${{ steps.py.outputs.python-path }}"
           → uv run --with pyinstaller==6.22.3 python scripts/build_binary.py --out build/bin
           → HWP2MD_BINARY="build/bin/${{ matrix.asset }}" uv run pytest tests/e2e/test_binary_smoke.py -q
           → actions/upload-artifact@v7 (name: bin-${{ matrix.platform }}, path: build/bin/${{ matrix.asset }}, if-no-files-found: error)
  github-release:
    needs: [binaries, publish]
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps: actions/download-artifact@v8 (pattern: bin-*, merge-multiple: true, path: assets)
           → cd assets && sha256sum hwp2md-* | sort -k2 > SHA256SUMS
           → GH_TOKEN=${{ github.token }}: gh release view "$GITHUB_REF_NAME" 가 성공하면
               gh release upload "$GITHUB_REF_NAME" assets/* --clobber
             아니면 gh release create "$GITHUB_REF_NAME" assets/* --verify-tag --title "$GITHUB_REF_NAME" --generate-notes
             (-R "$GITHUB_REPOSITORY" 명시, checkout 없음)
```
기존 `build`·`publish` 와 최상위 `permissions: contents: read` 는 한 글자도 바꾸지 않는다. 새 job 은 파일 끝에 추가한다.

### 4.8 Homebrew 탭 저장소
- 이름 `ilyos-numon/homebrew-tap` (공개, 기본 브랜치 `main`, 라이선스 파일 없음 — README 에 MIT 와 원 저장소 링크). 구조: `README.md`(= `packaging/homebrew/README.md` 복사), `Formula/hwp2md.rb`(= update_formula.py 출력).
- 로컬 작업 위치: `/Users/illi/illy-projects/hwp2md/build/homebrew-tap` (`build/` 는 gitignore). 탭 커밋 메시지: `hwp2md <버전>`.

## 5. 단계 (Stage)
모든 Bash 는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. uv 앞에는 `unset VIRTUAL_ENV;`, grep 은 `command grep`, ruff 는 `--no-cache`. gh 는 `GH_TOKEN=$(gh auth token --user ilyos-numon)`.

### Stage 1 — 빌더 비교 결정 기록 (decisions.md)
- 목적: 빌더 후보 비교와 PyInstaller 채택 이유·출처 URL 을 남긴다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: 없음
- 입력: 이 플랜 §8 "빌더 비교표", `docs/decisions.md` 끝 30줄 형식.
- 쓰기 범위: `docs/decisions.md` (끝에 절 2개 추가: `## 2026-10-27 단일 실행 파일 빌더: PyInstaller onefile`, `## 2026-10-27 Homebrew: 바이너리 formula + 수동 탭 갱신`)
- 산출물: 비교표(stars·최근 push·라이선스·의존성·통합 난이도), 결정, 이유, 출처 URL 3개(`https://github.com/pyinstaller/pyinstaller`, `https://github.com/Nuitka/Nuitka`, `https://github.com/ofek/pyapp`) + PyInstaller 라이선스 문서 URL `https://pyinstaller.org/en/stable/license.html`. 수치는 "2026-10-27 GitHub API 기준" 명시.
- 검증: `command grep -c "github.com/pyinstaller/pyinstaller\|github.com/Nuitka/Nuitka\|github.com/ofek/pyapp" docs/decisions.md` → `3` 이상, `cd /Users/illi/illy-projects && ./scripts/sanitize-check.sh hwp2md` (루트에서 실행해야 함 — 프로젝트 폴더에서는 path not found) → 0
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261027-binaries-brew][s1] 빌더 결정 기록`
- 실패 시: `git restore docs/decisions.md` 후 재시도.

### Stage 2 — PyInstaller 빌드 스크립트와 로컬 실행 파일
- 목적: §4.2·§4.3 대로 빌드 스크립트·진입점을 쓰고 macOS arm64 실행 파일을 로컬에서 만든다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S1
- 입력: §4.1~4.3, `src/hwp2md/web/app.py`(`STATIC_DIR`, `build_runtime_zip`), `src/hwp2md/cli.py`(읽기만).
- 쓰기 범위:
  - `scripts/build_binary.py` (신규)
  - `packaging/pyinstaller/hwp2md_entry.py` (신규)
- 산출물: `build/bin/hwp2md-macos-arm64` (커밋 안 함).
- 검증 (모두):
  - `unset VIRTUAL_ENV; uv run --with pyinstaller==6.22.3 python scripts/build_binary.py --out build/bin` → 종료 0, `build_binary: OK build/bin/hwp2md-macos-arm64 <bytes>` (≤ 80 MiB)
  - `build/bin/hwp2md-macos-arm64 --version` → `hwp2md 0.1.3`
  - `env -u PYTHONIOENCODING LANG=C LC_ALL=C build/bin/hwp2md-macos-arm64 /etc/hosts; echo rc=$?` → `rc=3`, stderr `hwp2md: error: not an HWP 5.0 file`, Traceback 없음
  - `build/bin/hwp2md-macos-arm64 serve --no-browser --port 8789 &` 후 최대 60초 `curl -sf http://localhost:8789/api/health` → `{"ok":true,"version":"0.1.3"}`, `curl -s http://localhost:8789/pkg/hwp2md.zip -o /private/tmp/claude-501/pkg.zip && unzip -l /private/tmp/claude-501/pkg.zip | command grep -c "olefile/olefile.py\|hwp2md/convert.py"` → `2`, 서버 종료(kill)
  - `uv run python scripts/build_binary.py --platform linux-x64; echo rc=$?` → `rc=2`
  - `unset VIRTUAL_ENV; uv run ruff check --no-cache scripts packaging && uv run ruff format --no-cache --check scripts packaging` → 0
- 완료 조건: 검증 통과 + PROGRESS 기록(빌드 시간·크기) + 커밋 `[T-20261027-binaries-brew][s2] PyInstaller 빌드 스크립트`
- 실패 시: hidden import 누락이면 `--hidden-import` 추가(같은 오류 2회 → BLOCKED). `app.py` 수정이 필요하다고 판단되면 고치지 말고 BLOCKED + NEEDS.

### Stage 3 — Homebrew formula 생성기
- 목적: §4.5 대로 `update_formula.py` 와 단위 테스트, 탭 README 원본을 쓴다.
- 담당: implementer(opus) · 병렬 가능: 아니오(순차 권장, 이유 §6) · 선행: S2
- 입력: §4.4·§4.5·§4.8, `tests/unit/test_build_pages.py`(importlib 로 스크립트 로드하는 패턴).
- 쓰기 범위:
  - `scripts/update_formula.py` (신규)
  - `tests/unit/test_update_formula.py` (신규)
  - `packaging/homebrew/README.md` (신규, 영어+한국어 3~5줄씩: `brew install ilyos-numon/tap/hwp2md`, 원 저장소 링크, "formula 는 생성물" 안내, MIT)
- 단위 테스트 최소 케이스: 정상 생성(버전·URL 3개·sha256 3개 포함, windows 줄 무시), 결정성(두 번 같은 출력), 누락 자산 → 종료 1 + `FAIL missing hwp2md-macos-x64`, 잘못된 줄 → 종료 1 + `FAIL bad line 2`, `--version v0.1.4` → 종료 2, `--out` 이 없는 부모 디렉터리 생성.
- 검증: `unset VIRTUAL_ENV; uv run pytest tests/unit/test_update_formula.py -q` → 실패 0, ≥5 pass · 생성물을 `ruby -c <파일>` → `Syntax OK` · `uv run ruff check --no-cache scripts tests && uv run ruff format --no-cache --check scripts tests` → 0
- 완료 조건: 검증 통과 + 커밋 `[T-20261027-binaries-brew][s3] Homebrew formula 생성기`
- 실패 시: 재시도 상한 3회, 같은 실패 2회 → BLOCKED.

### Stage 4 — 설치 문서·CHANGELOG·버전 0.1.4
- 목적: 사용자가 Python 없이 설치하는 방법과 릴리스 절차를 문서화하고 버전을 0.1.4 로 올린다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S3
- 입력: §4.1·§4.7·§4.8, README.md 47~80행 설치 절, README.en.md 48~70행, `docs/releasing.md` 전체.
- 쓰기 범위:
  - `README.md` (설치 절 맨 앞에 "Python 없이" 소절: brew 한 줄, 실행 파일 표(OS·자산·`releases/latest/download` 링크), macOS `xattr -d com.apple.quarantine <파일>`·`chmod +x`, Windows SmartScreen "추가 정보 → 실행", 체크섬 `shasum -a 256 -c SHA256SUMS`/PowerShell `Get-FileHash`. "English" 요약 절에 brew 한 줄 추가)
  - `README.en.md` (같은 내용 영어)
  - `docs/releasing.md` (워크플로우 절에 `binaries`·`github-release`, 릴리스 순서에 "Homebrew 탭 갱신" 단계: `uv run python scripts/update_formula.py --version X.Y.Z --out build/homebrew-tap/Formula/hwp2md.rb` → 탭 커밋·push, 실패 대응에 `binaries` 실패 시 재실행·태그 재생성, `macos-15-intel` 러너 소멸 시 대응)
  - `CHANGELOG.md` (`## [0.1.4] - 2026-10-27` Added: OS별 실행 파일·Release 자산·SHA256SUMS·Homebrew 탭)
  - `src/hwp2md/__init__.py` (`__version__ = "0.1.4"` 한 줄만)
- 검증: `uv run python -c "import hwp2md;print(hwp2md.__version__)"` → `0.1.4` · `command grep -c "brew install ilyos-numon/tap/hwp2md" README.md README.en.md` → 각 ≥1 · `command grep -c "xattr -d com.apple.quarantine" README.md README.en.md` → 각 ≥1 · `unset VIRTUAL_ENV; uv run pytest tests/unit -q` → 실패 0 · `uv run pytest tests/e2e/test_project_links.py tests/e2e/test_dist_package.py -q` → 실패 0 · sanitize-check → 0
- 완료 조건: 검증 통과 + 커밋 `[T-20261027-binaries-brew][s4] 설치 문서와 0.1.4`
- 실패 시: 기존 테스트가 README 문자열에 의존해 실패하면 README 를 고쳐 맞춘다(테스트 수정 금지).

### Stage 5 — release.yml 실행 파일 job (orchestrator 전용 파일 단독 단계)
- 목적: §4.7 대로 `binaries`·`github-release` job 을 추가한다.
- 담당: implementer(opus) · 병렬 가능: 아니오(이 파일만 단독) · 선행: S4
- 입력: §4.1·§4.4·§4.7, 현재 `.github/workflows/release.yml`, `.github/workflows/ci.yml`(액션 버전 참고).
- 쓰기 범위:
  - `.github/workflows/release.yml` (이 파일만)
- 검증: §2 S8·S9 명령 · `command grep -c "macos-15-intel\|ubuntu-22.04\|windows-2022\|macos-15$\|macos-15\"" .github/workflows/release.yml` → ≥4 · `command grep -n "tests/e2e/test_binary_smoke.py" .github/workflows/release.yml` → 1줄
- 완료 조건: 검증 통과 + 커밋 `[T-20261027-binaries-brew][s5] Release 실행 파일 job`
- 실패 시: actionlint 경고는 수정 1회, 같은 경고 2회 → BLOCKED. 기존 job 줄이 diff 에 `-` 로 나타나면 즉시 되돌리고 재작성.

### Stage 6 — 실행 파일 E2E 작성·로컬 실행 (필수, 생략 불가)
- 목적: §4.6 스모크를 E2E 로 쓰고 로컬 전체 검증을 통과시킨다.
- 담당: test-writer(sonnet, 2회 실패 → opus) → runner(haiku, 2회 실패 → sonnet)
- 병렬 가능: 아니오 · 선행: S5
- 입력: §4.6, `tests/e2e/conftest.py`(`_free_port`·`web_server` 패턴, 수정 금지), `tests/synth_hwpx.py`·`tests/synth_hwp5.py`(사용만), `build/bin/hwp2md-macos-arm64`(S2 산출물은 0.1.3 이므로 runner 가 먼저 재빌드).
- 쓰기 범위: `tests/e2e/test_binary_smoke.py` (신규)
- 검증 (runner, 로그 `logs/s6-e2e.log`, `logs/e2e.log`):
  1. `unset VIRTUAL_ENV; uv run --with pyinstaller==6.22.3 python scripts/build_binary.py --out build/bin` → OK
  2. `HWP2MD_BINARY=build/bin/hwp2md-macos-arm64 uv run pytest tests/e2e/test_binary_smoke.py -q` → 실패 0, ≥7 pass
  3. `uv run pytest tests/e2e -q` (env 없이, 빌드 포함) → 실패 0
  4. `uv run pytest tests/unit -q` → 실패 0
  5. `uv run ruff check --no-cache src tests scripts packaging && uv run ruff format --no-cache --check src tests scripts packaging && uv run mypy src` → 0
- 완료 조건: 5개 모두 통과 + 커밋 `[T-20261027-binaries-brew][s6] 실행 파일 스모크 E2E`
- 실패 시: 실행 파일 결함(테스트가 아닌 빌드 문제)이면 S2 재진입 1회(쓰기 범위 S2 그대로). 테스트 약화 금지.

### Stage 7 — main 반영·태그 v0.1.4·Release 확인
- 목적: 변경을 main 에 올리고 태그로 PyPI·Release 를 게시한다.
- 담당: orchestrator(git·gh) + runner(haiku: CI·Release 대기·로그) · 병렬 가능: 아니오 · 선행: S6
- 쓰기 범위: 파일 없음 (git 조작만: `ai/T-20261027-binaries-brew` → main fast-forward 또는 merge, push, 태그)
- 절차: `git checkout main && git merge --ff-only ai/T-20261027-binaries-brew && git push origin main` → `gh run watch` 로 main 의 `CI` 전 job success → `git tag -a v0.1.4 -m "v0.1.4" && git push origin v0.1.4` → `Release` 실행 대기(`gh run watch <id> --exit-status`, 최대 45분).
- 검증: §2 S10·S11·S12.
- 완료 조건: 세 검증 통과 + PROGRESS 에 run id 기록 + 기록 커밋 `[T-20261027-binaries-brew][s7] v0.1.4 릴리스`
- 실패 시: `binaries` 실패 → 로그 tail 200줄을 runner 가 요약 → 원인이 build_binary/테스트면 S2 또는 S6 재진입 후 `docs/releasing.md` 절차대로 태그 삭제·재생성(PyPI 가 이미 0.1.4 를 게시했으면 `__version__` 0.1.5 로 올리고 CHANGELOG 항목 추가 — 범위 변경이므로 PROGRESS 기록). `publish` 실패는 기존 releasing.md 절차.

### Stage 8 — Homebrew 탭 저장소 생성·formula push (사용자 수동 가능 단계)
- 목적: 공개 탭 저장소에 v0.1.4 formula 를 올린다.
- 담당: orchestrator (gh·git, 서브에이전트 없음) · 병렬 가능: 아니오 · 선행: S7
- 쓰기 범위: 외부 저장소 `ilyos-numon/homebrew-tap` 과 로컬 `build/homebrew-tap/**` (gitignore 대상, hwp2md 저장소 파일 변경 없음)
- 절차:
  1. `GH_TOKEN=$(gh auth token --user ilyos-numon) gh repo create ilyos-numon/homebrew-tap --public --description "Homebrew tap for hwp2md" --clone=false`
  2. 막히면(권한 판정·거절) 사용자 수동 U1: github.com 우상단 `+` → `New repository` → Owner `ilyos-numon`, Repository name `homebrew-tap`, Description `Homebrew tap for hwp2md`, `Public` 선택, "Add a README file" 체크 해제, .gitignore·license `None` → `Create repository`. 완료 후 사용자가 "탭 만들었음" 이라고 알리면 3번부터.
  3. `git clone https://github.com/ilyos-numon/homebrew-tap.git build/homebrew-tap` (빈 저장소면 `git init -b main` + remote add)
  4. `unset VIRTUAL_ENV; uv run python scripts/update_formula.py --version 0.1.4 --out build/homebrew-tap/Formula/hwp2md.rb` → `update_formula: OK`
  5. `cp packaging/homebrew/README.md build/homebrew-tap/README.md`
  6. `cd build/homebrew-tap && git add -A && git commit -m "hwp2md 0.1.4" && git push -u origin main` (push 가 막히면 U2: 사용자가 터미널에서 같은 명령 실행)
- 검증: `gh api repos/ilyos-numon/homebrew-tap --jq '.visibility'` → `public` · `gh api repos/ilyos-numon/homebrew-tap/contents/Formula/hwp2md.rb --jq .name` → `hwp2md.rb` · `ruby -c build/homebrew-tap/Formula/hwp2md.rb` → `Syntax OK` · `brew style build/homebrew-tap/Formula/hwp2md.rb` → 종료 0 (style 위반은 update_formula 템플릿을 S3 범위로 1회 수정 후 재생성)
- 완료 조건: 검증 통과 + PROGRESS 기록(탭 커밋 SHA) + hwp2md 기록 커밋 `[T-20261027-binaries-brew][s8] Homebrew 탭 0.1.4`
- 실패 시: U1/U2 대기 중이면 STATE 에 BLOCKED(사용자 수동 단계) 와 정확한 클릭 경로를 적는다.

### Stage 9 — 배포물 E2E (Release 자산·brew install/test·러너 로그)
- 목적: 사용자가 실제로 받는 경로(다운로드·brew)로 동작을 확인한다.
- 담당: runner(haiku, 2회 실패 → sonnet) · 병렬 가능: 아니오 · 선행: S8
- 쓰기 범위: `logs/s9-dist-e2e.log` 와 `/private/tmp/claude-501/` 아래 임시 디렉터리만 (저장소 파일 변경 없음)
- 절차·검증:
  1. 새 빈 디렉터리 `D=/private/tmp/claude-501/rel-v0.1.4` 에 `gh release download v0.1.4 -R ilyos-numon/hwp2md -D $D` → `cd $D && shasum -a 256 -c SHA256SUMS` → 4줄 `OK` (§2 S13)
  2. `chmod +x $D/hwp2md-macos-arm64 && HWP2MD_BINARY=$D/hwp2md-macos-arm64 uv run pytest tests/e2e/test_binary_smoke.py -q` (hwp2md 저장소에서) → 실패 0
  3. Gatekeeper 안내 검증: `xattr -w com.apple.quarantine "0081;00000000;Safari;" $D/hwp2md-macos-arm64 && xattr -d com.apple.quarantine $D/hwp2md-macos-arm64 && $D/hwp2md-macos-arm64 --version` → `hwp2md 0.1.4` (격리 속성을 단 상태로 실행하지는 않는다 — GUI 대화상자가 뜰 수 있음)
  4. `brew install ilyos-numon/tap/hwp2md && brew test hwp2md && $(brew --prefix)/bin/hwp2md --version` → `hwp2md 0.1.4` (§2 S14). `brew` 가 없거나 설치가 네트워크 외 원인으로 실패하면 대체 검증: `brew` 없이 `ruby -c` + 1번 체크섬과 formula 의 sha256 3개 일치 대조(`command grep sha256 build/homebrew-tap/Formula/hwp2md.rb`), 그리고 RESULT 에 "brew 실검증 미실시" 명시
  5. 다른 OS: §2 S11 결과 + `gh run view <id> --log -R ilyos-numon/hwp2md | command grep -E "binaries.*(passed|failed)"` → 4개 플랫폼 모두 `passed`, `failed` 0
  6. 정리: `brew uninstall hwp2md && brew untap ilyos-numon/tap` (§7 Q5 기본값)
- 완료 조건: 1~5 통과 + 로그 저장 + 커밋 `[T-20261027-binaries-brew][s9] 배포물 E2E`
- 실패 시: brew 설치 실패 원인이 formula 면 S8 재진입 1회(템플릿 수정은 S3 범위), 실행 파일 결함이면 BLOCKED(0.1.5 필요 — 사용자 RESULT 검토로).

### Stage 10 — 리뷰·결과 기록
- 담당: reviewer(sonnet) → scribe(haiku) · 선행: S9
- 리뷰 범위: `git diff <S1 시작 base>..HEAD` (경로: scripts/, packaging/, tests/, .github/workflows/release.yml, README*, docs/, CHANGELOG.md, src/hwp2md/__init__.py) + 탭 저장소 formula. 확인: OUT 위반 0, `contents: write` 가 `github-release` 에만, 기존 job 무변경, 테스트 skip/약화 0, 익명화.
- 쓰기 범위: `.ai/tasks/T-20261027-binaries-brew/RESULT.md` (scribe), `.ai/STATE.md` 는 orchestrator
- 검증: sanitize-check 0 · `openspec validate binaries-brew` valid → orchestrator 가 `openspec archive binaries-brew` (tasks 전부 체크 후)
- 완료 조건: RESULT.md 존재(결론 3줄·성공 기준 표·사용자 수동 단계 수행 여부) + 커밋 `[T-20261027-binaries-brew][done] ...`

## 6. 병렬 실행 맵
```
S1 → S2 → S3 → S4 → S5 → S6(E2E) → S7(release) → S8(tap) → S9(배포물 E2E) → S10(리뷰)
```
- 전 단계 순차. S2(`scripts/build_binary.py`, `packaging/pyinstaller/hwp2md_entry.py`)와 S3(`scripts/update_formula.py`, `tests/unit/test_update_formula.py`, `packaging/homebrew/README.md`)는 경로 단위로 겹치지 않아 병렬이 가능하지만, 각 10분 안쪽이고 worktree 격리가 main 기준으로 갈라지는 문제가 있어 순차로 둔다(병렬로 바꾸면 수동 worktree 격리 필수).
- S5 는 orchestrator 전용 파일 단독 단계라 병렬 불가. S7~S9 는 외부 상태(태그·Release·탭)에 순서 의존.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
사용자 지시 "그래 다 해줘" 에 따라 아래 기본값으로 자동 진행한다.
- [ ] Q1 빌더: PyInstaller 6.22.3 onefile 로 할까요? (대안: Nuitka — 시작 속도는 빠르나 빌드가 길고 C 컴파일러 필요, GitHub 라이선스 표기 AGPL-3.0 확인 필요 / PyApp — 첫 실행 때 내려받기 필요)
  - 기본값: PyInstaller (planner 추천). 라이선스 GPL-2.0-or-later + 부트로더 예외 → 만든 실행 파일은 MIT 로 배포 가능. GPL 계열이라 글로벌 규칙상 사전 확인 대상이므로 이 질문으로 확인을 갈음한다.
- [ ] Q2 자산 형식: 압축 없는 실행 파일, 이름에 버전 없음(`hwp2md-macos-arm64` 등)?
  - 기본값: 그렇게 한다 (`releases/latest/download/...` 고정 링크가 README 에서 영구 유효).
- [ ] Q3 탭 갱신 방식: 릴리스마다 orchestrator 가 `update_formula.py` 로 생성·push (토큰 없음) vs Release 워크플로우가 크로스 저장소 PAT(fine-grained, homebrew-tap contents:write)로 자동 push
  - 기본값: 수동 생성·push (secret 불필요). 자동화는 후속 태스크.
- [ ] Q4 Linux 빌드 러너 `ubuntu-22.04` (glibc 2.35 이상에서 실행) — 더 오래된 배포판 지원(manylinux 컨테이너)은 OUT?
  - 기본값: ubuntu-22.04, 오래된 glibc 지원은 OUT (Docker OUT 과 일치).
- [ ] Q5 검증 후 로컬 brew 설치를 지울까요?
  - 기본값: S9 끝에 `brew uninstall hwp2md && brew untap ilyos-numon/tap`.
- [ ] Q6 `homebrew-tap` 공개 저장소 생성이 자동 판정에 막히면 웹에서 직접 만들어 주실 수 있나요? (클릭 경로 S8 U1)
  - 기본값: orchestrator 가 먼저 시도하고, 막히면 STATE 에 BLOCKED 로 U1 경로를 남기고 기다린다.

## 8. 리스크
### 빌더 비교표 (2026-10-27 GitHub API 기준)
| 후보 | stars | 최근 push | 라이선스 | 의존성·툴체인 | 통합 난이도 | 출처 |
|------|-------|-----------|----------|---------------|-------------|------|
| PyInstaller 6.22.3 | 13,136 | 2026-10-25 | GPL-2.0-or-later + 부트로더 예외 (산출물 라이선스 제약 없음) | pip 패키지 + pyinstaller-hooks-contrib, C 컴파일러 불필요 | 낮음: lxml·uvicorn hook 기본, `--add-data` 로 static·`.py` 동봉, 빌드 1~3분 | https://github.com/pyinstaller/pyinstaller |
| Nuitka | 15,207 | 2026-10-26 | GitHub 표기 AGPL-3.0 (이전 Apache-2.0, 재확인 필요) | C 컴파일러(MSVC/clang/gcc) 필수, onefile 은 zstandard | 중~높음: 빌드 10~30분/OS, data 파일·`.py` 원본 별도 지정, 시작 속도는 유리 | https://github.com/Nuitka/Nuitka |
| PyApp | 2,039 | 2026-10-12 | MIT / Apache-2.0 (GitHub 미검출) | Rust 툴체인, 런타임에 Python 배포본·의존성 설치 | 중: 기본은 첫 실행 때 네트워크로 Python·패키지 설치 → "오프라인 단일 파일" 목표와 어긋남, 완전 임베드는 설정 복잡 | https://github.com/ofek/pyapp |
결론: PyInstaller (추천). Homebrew Python 리소스 방식 대신 바이너리 formula 를 쓰는 근거: `lxml` 이 소스 빌드되면 libxml2·libxslt 의존과 빌드 시간이 생기고, 의존성마다 `resource` 블록(url·sha256)을 릴리스마다 갱신해야 한다. 바이너리 formula 는 이미 스모크를 통과한 같은 실행 파일을 쓰므로 검증 대상이 하나로 줄어든다.

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 동결 앱에서 `/pkg/hwp2md.zip` 이 비거나 olefile 누락 (`build_runtime_zip` 이 `.py` 원본을 rglob) | 높음(대응 안 하면 확정) | §4.2 stage 디렉터리로 `.py`·static 을 `--add-data`. §4.6 케이스 7이 zip 항목을 단언 |
| Windows 파이프·`LANG=C` 에서 `✓`·한글 출력 `UnicodeEncodeError` | 중 | §4.3 진입점 UTF-8 보정, E2E 가 `PYTHONIOENCODING`·`PYTHONUTF8` 를 지우고 실행 |
| uvicorn 동적 import(`uvicorn.loops.auto` 등) 누락 | 중 | `--collect-submodules uvicorn`, 케이스 7 serve 헬스체크 |
| python-build-standalone 인터프리터와 PyInstaller 비호환 (CI `e2e` job 은 setup-uv 관리 Python 으로 빌드) | 낮음~중 | 로컬 uv Python 은 Py_ENABLE_SHARED=1 확인됨. CI `e2e` job 에서 실패하면 BLOCKED → ci.yml 에 setup-python 을 쓰는 orchestrator 단독 단계 추가(플랜 변경 이력) |
| CI `e2e` job 시간 증가(세션당 빌드 1회, 약 1~3분) | 높음 | 수용. 30분 timeout 안. 문제되면 후속에서 마커 분리 |
| `macos-15-intel` 러너 미가용·대기열 지연 | 중 | 45분 timeout. 소멸 시 macos-x64 자산·formula `on_intel` 제거하는 후속 변경 (releasing.md 에 기록) |
| Windows Defender·SmartScreen 오탐/경고 | 중 | README 에 "추가 정보 → 실행"과 체크섬 검증. 서명은 OUT |
| macOS Gatekeeper 격리(브라우저 다운로드) | 높음 | README `xattr -d com.apple.quarantine`. brew 설치는 격리 속성 없음. PyInstaller 가 arm64 ad-hoc 서명 자동 수행 |
| onefile 첫 실행 느림·`/tmp` noexec 환경 | 낮음 | README 한계 절에 한 줄. 런타임 tmpdir 옵션은 OUT |
| 태그 후 binaries 실패인데 PyPI 는 이미 게시 | 중 | publish 와 binaries 는 독립, github-release 만 둘 다 필요. 재릴리스는 S7 실패 시 절차(0.1.5) |
| 공개 저장소 생성이 권한 판정에 막힘 | 중 | S8 U1 웹 클릭 경로, STATE BLOCKED |
| Homebrew 가 동결 Mach-O 를 재링크·서명 손상 | 낮음 | S9 `brew test` 로 실검증. 실패 시 formula 에 `skip_clean "bin"` 추가 후 재검증(S3 범위 1회) |

## 9. 예상 비용
- 예상 단계 수: 10 · 서브에이전트 호출: 약 11회 (implementer 5, test-writer 1, runner 3, reviewer 1, scribe 1) + orchestrator 직접 단계 2(S7·S8) · 주 모델: opus 5 / sonnet 2 / haiku 4
- CI: Release 1회 (4 OS × 약 10분), CI 1회. 사용자 개입 가능 지점: 플랜 승인(자동), S8 U1/U2(막힐 때만), RESULT 검토.
