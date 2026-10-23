# PLAN — T-20261023-web-preview hwp2md 웹 미리보기 (메모리 변환 API + `hwp2md serve` + 브라우저 전용 Pyodide 모드)

> 작성: planner opus · 2026-10-23 10:00 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> BASE: 프로젝트 저장소 브랜치 `ai/T-20261023-web-preview` HEAD `5979e12` · 단위 240 passed · E2E 46 passed · Python 3.12.13 · olefile 0.47

## 0. 한 줄 목표
사용자는 `pip install 'hwp2md[web]'` 후 `hwp2md serve` 로 연 로컬 화면에 HWP/HWPX 를 끌어다 놓아, 렌더된 Markdown 미리보기(이미지 포함)와 원문을 보고 `.md`+이미지 zip 을 내려받을 수 있고, "브라우저 안에서만 처리" 를 켜면 파일을 서버로 한 바이트도 보내지 않고 같은 결과를 얻을 수 있다. 기존 `hwp2md INPUT -o OUT` 과 `convert()` 는 그대로다.

### 0.1 OpenSpec 연동
- change: `openspec/changes/web-preview/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate web-preview` (planner 확인: `Change 'web-preview' is valid`, `--strict` 도 통과)
- capability: `memory-conversion`(신규), `web-preview`(신규)
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행.

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | pyproject web extra + dev 의존성, `uv sync`, chromium 설치, METADATA 확인 | S1 |
| 2.1 | Pyodide+lxml 스파이크: 샘플 5개 Markdown 네이티브와 5/5 동일 | S2 |
| 3.1 | `source.py` + detect/hwp5/hwpx 리더 `Path \| bytes` 입력 | S3 |
| 3.2 | `test_source_bytes.py`: bytes/경로 동일, 100B 입력 경로 오인 없음, `<memory>` 라벨 | S3 |
| 4.1 | `memory.py` 9개 심볼 + `errors.py` 예외 2개 | S4 |
| 4.2 | `convert()` 공통 계산 공유(출력 불변) + `__init__` export | S4 |
| 4.3 | `test_memory.py`: 동일성·쓰기 차단·zip·data URI·오류 코드·웹 모듈 차단 | S4 |
| 5.1 | `web/app.py` `create_app()` 엔드포인트 5개 | S5 |
| 5.2 | `build_runtime_zip()` + `/pkg/hwp2md.zip` + `web/server.py` `serve()` | S5 |
| 5.3 | `test_web_app.py` (TestClient) | S5 |
| 6.1 | `cli.py` `serve` 분기 | S6 |
| 7.1 | 서버 모드 화면 (`index.html`·`app.js`·`style.css`·`vendor/marked.min.js`) + 스모크 스크린샷 | S7 |
| 7.2 | 브라우저 전용 모드 (`pyodide-runner.js` + 토글) + 스모크 | S8 |
| 8.1 | `tests/e2e/test_web_api.py` + conftest 서버 픽스처 | S9 |
| 8.2 | `tests/e2e/test_web_ui.py` 두 모드·무전송·동일성·스크린샷 + E2E 전체 | S10 |
| 9.1 | README·decisions 문서 + sanitize-check | S11 |
| 10.1 | 리뷰·RESULT·STATE | S12 |

## 1. 범위
### 포함 (IN)
- 바이트 입력: 신규 `src/hwp2md/source.py`; `src/hwp2md/detect.py` `detect_format`, `src/hwp2md/hwp5/reader.py` `read_hwp5_package`·`read_blocks`, `src/hwp2md/hwpx/reader.py` `read_hwpx_package`·`read_blocks` 가 `Path | bytes` 를 받는다 (§4-A).
- 메모리 API: 신규 `src/hwp2md/memory.py` (§4-B), `src/hwp2md/errors.py` 예외 2개 추가, `src/hwp2md/convert.py` 내부 공유, `src/hwp2md/__init__.py` export 2개.
- 웹 서버: 신규 `src/hwp2md/web/__init__.py`, `web/app.py`, `web/server.py` (§4-C, §4-D).
- 화면: 신규 `src/hwp2md/web/static/index.html`, `app.js`, `style.css`, `pyodide-runner.js`, `vendor/marked.min.js` (§4-E).
- CLI: `src/hwp2md/cli.py` 에 `serve` 하위 명령 분기 (§4-F).
- 의존성: `pyproject.toml` extra `web` + dev 그룹 (§4-G). Playwright chromium 다운로드(~150MB).
- 테스트: 단위 `tests/unit/test_source_bytes.py`, `test_memory.py`, `test_web_app.py`; E2E `tests/e2e/test_web_api.py`, `test_web_ui.py`, `tests/e2e/conftest.py`(픽스처 추가만).
- 스파이크·스모크(커밋되는 증거): `.ai/tasks/T-20261023-web-preview/spike/run_spike.py`, `spike.html`, `ui_smoke.py`.
- 문서: `README.md` "설치와 실행" 절, `docs/decisions.md` 4건.

### 제외 (OUT) — 절대 건드리지 않는다
- 파싱 로직(`hwp5/body.py`, `hwp5/docinfo.py`, `hwp5/records.py`, `hwpx/body.py`, `hwpx/header.py`, `hwpx/bindata.py`), 렌더러 `render.py`, `blocks.py`, `images.py` — 변환 결과 규칙은 바뀌지 않는다.
- 기존 테스트 파일 전부(`tests/unit/test_*.py` 기존 16개, `tests/e2e/test_cli_*.py` 5개, `tests/synth_*.py`) — 수정·삭제 금지.
- 여러 파일 동시 변환, 변환 이력·저장, 인증, 원격 공개 배포, HTTPS.
- Pyodide/lxml 오프라인 동봉, Web Worker, PWA·서비스 워커.
- `tests/fixtures/**` 추가·수정 (오류 케이스 입력은 테스트가 tmp 에 생성).
- GitHub Actions, PyPI 배포, Docker.

### 건드리면 안 되는 파일/디렉토리
- orchestrator 전용(서브에이전트 쓰기 금지): `pyproject.toml`, `uv.lock`, `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.gitignore`, `src/hwp2md/cli.py`(S6 에서만 implementer 쓰기 범위).
- `doc/my_info/**`(루트), `tests/fixtures/**`, `openspec/specs/**`(archive 때 orchestrator 가 반영).

## 2. 성공 기준 (전부 만족해야 DONE)
`T=.ai/tasks/T-20261023-web-preview` · 모든 명령은 `cd /Users/illi/illy-projects/hwp2md && ` 접두.

| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| C1 | 기존 단위 테스트 회귀 없음 + 신규 단위 | `uv run pytest tests/unit -q` | 실패 0, passed ≥ 284 (기존 240 + S3 ≥10 + S4 ≥20 + S5 ≥14) |
| C2 | E2E 전체 통과 (기존 46 + 신규) | S10 검증 블록 (runner) | `exit=0`, 실패 0, passed ≥ 66 (기존 46 + S9 ≥12 + S10 ≥8), `seconds` ≤ 300 |
| C3 | 린트·타입 | `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | 종료 0, mypy `Success: no issues found` |
| C4 | 메모리 API = 경로 API | `uv run pytest tests/unit/test_memory.py -q -k "same_as_convert"` | 5개 샘플 전부 pass |
| C5 | 디스크 쓰기 없음 (정적) | `grep -nE -e tempfile -e write_bytes -e write_text -e 'open\(' src/hwp2md/memory.py src/hwp2md/web/app.py src/hwp2md/source.py` | 출력 0줄 |
| C6 | 디스크 쓰기 없음 (동적) | E2E `test_web_api.py::test_no_files_written` | pass (cwd·TMPDIR 아래 파일 0개) |
| C7 | 기본 설치는 웹 없이 동작 | `uv run python -c "import sys; sys.modules['starlette']=None; sys.modules['uvicorn']=None; import hwp2md, hwp2md.memory; print('hwp2md.web' in sys.modules)"` | `False` 출력, 종료 0 |
| C8 | extra 미설치 안내 | `uv run python -c "import sys; sys.modules['starlette']=None; sys.modules['uvicorn']=None; from hwp2md.cli import main; raise SystemExit(main(['serve','--no-browser']))"; echo exit=$?` | stderr 에 `hwp2md[web]`, `exit=1` |
| C9 | 기존 CLI 불변 | `uv run hwp2md --help > /private/tmp/claude-501/help.after.txt; diff /private/tmp/claude-501/help.after.txt $T/logs/help.before.txt` (before 는 S1 에서 저장) + 기존 E2E 46개 pass | `diff` 출력 0줄, 46 passed |
| C10 | 서버 기동 | `uv run hwp2md serve --no-browser --port 8765 &` 후 `curl -sf http://localhost:8765/api/health` | `{"ok":true,"version":"0.1.0"}` |
| C11 | 브라우저 모드 무전송 | E2E `test_web_ui.py::test_browser_mode_sends_no_file` | pass: 브라우저 모드 non-GET 요청 0, `/api/` 요청 0; 서버 모드 대조군 POST 1 (본문 길이 = 파일 크기) |
| C12 | 두 모드 출력 동일 | E2E `test_web_ui.py::test_modes_produce_identical_markdown` | 5개 샘플 모두 server `#raw` == browser `#raw` == CLI `.md` |
| C13 | wheel 에 정적 파일 포함, extra 선언 | 표 아래 C13 블록 | 첫 줄 숫자 ≥ 5, 둘째 줄 `1` |
| C14 | 화면 확인 — 서버 모드 | 스크린샷 `$T/screenshots/web_server_preview.png` | 드롭 영역, 왼쪽 렌더 미리보기(제목·표·그림 1장 보임), 오른쪽 원문 Markdown, 활성화된 "zip 다운로드" 버튼, 상태 "서버 모드" |
| C15 | 화면 확인 — 브라우저 모드 | 스크린샷 `$T/screenshots/web_browser_preview.png` | 토글 켜짐, 상태 문구 "브라우저 모드: 파일이 서버로 전송되지 않습니다", 같은 문서 미리보기·원문 |
| C16 | 화면 확인 — 오류 | 스크린샷 `$T/screenshots/web_error.png` | `#error` 에 "HWP 5.0 또는 HWPX 파일이 아닙니다" |
| C17 | OpenSpec | `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate web-preview` | `Change 'web-preview' is valid`, tasks.md 17개 전부 `[x]` |
| C18 | 익명화 | `$ILLY_ROOT/scripts/sanitize-check.sh hwp2md` | OK |

C13 블록:
```bash
cd /Users/illi/illy-projects/hwp2md && W=/private/tmp/claude-501/hwp2md-wheel && rm -rf $W && uv build --wheel -o $W >/dev/null 2>&1
unzip -l $W/hwp2md-0.1.0-py3-none-any.whl | grep -c "hwp2md/web/static/"
unzip -p $W/hwp2md-0.1.0-py3-none-any.whl hwp2md-0.1.0.dist-info/METADATA | grep -c "Provides-Extra: web"
```

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 동일 단계 재시도 3회 초과 → BLOCKED.
- 같은 오류(같은 테스트 id + 같은 assertion 또는 같은 예외 타입·메시지)로 수정 2회 실패 → BLOCKED.
- 단계 하나 도구 호출 40회 목표, 60회 초과 → PARTIAL 기록 후 orchestrator 반환. 단계 하나 벽시계 45분 초과 → PARTIAL.
- **스파이크(S2) BLOCKED 조건** (하나라도):
  1. jsDelivr CDN 의 `pyodide.js` 또는 lxml 패키지 로드가 3회 연속 네트워크 오류(프록시·DNS·TLS) → BLOCKED `NEEDS: Pyodide 동봉 여부 결정`.
  2. `await pyodide.loadPackage("lxml")` 가 시도 버전 3개(0.27.7, 0.26.4, 0.28.x 최신) 모두에서 실패 → BLOCKED.
  3. `import hwp2md` 가 Pyodide 에서 실패하고 원인이 hwp2md 소스 수정(이 플랜 OUT 파일)을 요구 → BLOCKED.
  4. 샘플 5개 중 1개라도 Pyodide Markdown ≠ 네이티브 Markdown → BLOCKED (diff 첫 20줄을 `logs/s2-spike.log` 에 남김).
  5. Pyodide+lxml 로드 시간 > 120초 (3회 측정 중앙값) → BLOCKED `NEEDS: 브라우저 모드 유지 여부`.
- Playwright chromium 다운로드 실패(프록시) 2회 → BLOCKED `NEEDS: 브라우저 설치 경로`.
- OUT 범위 파일(파싱 로직·기존 테스트) 수정 없이는 진행 불가 → BLOCKED (수정하지 않는다).
- 기존 E2E/단위 테스트가 1개라도 실패하는데 원인이 이번 변경 → 그 단계 RETRY. 테스트 수정으로 해결 금지.
- §4 계약 변경이 필요 → BLOCKED (planner 재호출).
- 자격증명·결제·외부 계정 필요 → BLOCKED.

## 4. 인터페이스 계약 (병렬 작업 전 확정)

### 4-A. 바이트 입력 (`src/hwp2md/source.py`, S3)
```python
# src/hwp2md/source.py
from pathlib import Path
from typing import BinaryIO
Source = Path | bytes
MEMORY_LABEL = "<memory>"
def source_label(src: Source) -> str: ...          # Path → str(path), bytes → "<memory>"
def as_binary_io(src: Source) -> BinaryIO | str:    # bytes → io.BytesIO(src), Path → str(src)
    ...
```
- `detect_format(path: Source) -> DocFormat`: bytes 면 `olefile.isOleFile(io.BytesIO(data))`, `zipfile.is_zipfile(io.BytesIO(data))`, `zipfile.ZipFile(io.BytesIO(data))`. **bytes 를 olefile 에 직접 넘기지 않는다** (1536B 미만 bytes 는 경로로 해석됨). 오류 메시지의 `{path}` 자리는 `source_label(src)`. Path 입력의 메시지 문자열은 기존과 동일.
- `read_hwp5_package(path: Source)`, `hwp5.reader.read_blocks(path: Source)`, `read_hwpx_package(path: Source)`, `hwpx.reader.read_blocks(path: Source)` 동일 규칙. 기존 호환 래퍼(`read_streams`, `read_sections`, `read_package`, `read_paragraphs`)는 시그니처를 `Source` 로 넓히는 것만 허용.
- `convert.read_blocks(path: Source) -> list[Block]`.

### 4-B. 메모리 API (`src/hwp2md/memory.py`, S4)
```python
from dataclasses import dataclass
from typing import Literal, Any
MAX_INPUT_BYTES = 50 * 1024 * 1024          # 52428800
ErrorCode = Literal["empty", "too_large", "not_hwp", "unsupported", "convert_failed"]
STATUS_BY_CODE: dict[ErrorCode, int] = {"empty": 400, "too_large": 413, "not_hwp": 415,
                                        "unsupported": 415, "convert_failed": 422}
MIME_BY_EXT = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
               "gif": "image/gif", "bmp": "image/bmp"}   # 그 밖: "application/octet-stream"

@dataclass(frozen=True)
class MemoryImage:
    file_name: str          # "img_001.png"
    data: bytes
    @property
    def mime(self) -> str: ...

@dataclass(frozen=True)
class MemoryResult:
    stem: str               # safe_stem(filename)
    markdown: str           # convert() 가 쓰는 .md 와 바이트 동일 (상대 링크)
    image_dir: str          # f"{stem}_images" (이미지 없어도 값은 채움)
    images: tuple[MemoryImage, ...]   # 고유 file_name 첫 등장 순 (convert 의 image_files 순서와 같음)
    paragraph_count: int
    table_count: int
    heading_count: int
    image_count: int        # Image 블록 수(재참조 포함)

def safe_stem(filename: str) -> str: ...      # "/"·"\\" 로 쪼갠 마지막 요소의 PurePosixPath(..).stem, strip;
                                              # "" / "." / ".." → "document"
def convert_bytes(data: bytes, filename: str = "document.hwp") -> MemoryResult: ...
    # len(data)==0 → EmptyInputError; > MAX_INPUT_BYTES → InputTooLargeError; 그 외 리더 예외 그대로 전파
def markdown_with_data_uris(result: MemoryResult) -> str: ...
    # 각 이미지마다 "](" + image_dir.replace(" ", "%20") + "/" + file_name + ")" 를
    # "](data:<mime>;base64,<b64>)" 로 str.replace
def build_zip(result: MemoryResult) -> bytes: ...
    # zipfile.ZipFile(io.BytesIO(), "w", ZIP_DEFLATED); ZipInfo(name, date_time=(1980,1,1,0,0,0));
    # 엔트리: f"{stem}.md" (markdown.encode("utf-8")), 이미지 있으면 f"{image_dir}/{file_name}" 순서대로
def to_payload(result: MemoryResult) -> dict[str, Any]: ...
    # {"name": stem, "markdown": ..., "preview_markdown": markdown_with_data_uris(...),
    #  "image_dir": ..., "images": [{"file_name","mime","size"}],
    #  "counts": {"paragraphs","tables","headings","images"}}
def error_code(exc: BaseException) -> ErrorCode: ...
    # EmptyInputError→empty, InputTooLargeError→too_large, NotHwpFileError→not_hwp,
    # UnsupportedHwpError→unsupported, 그 외 전부→convert_failed  (isinstance 순서 주의: 하위 클래스 먼저)
def convert_to_response(data: bytes, filename: str) -> tuple[int, dict[str, Any]]: ...
    # 성공 (200, to_payload(r)); 실패 (STATUS_BY_CODE[c], {"error": {"code": c, "message": str(exc)}}). 예외 전파 없음
```
- `errors.py` 추가: `class EmptyInputError(Hwp2mdError)`, `class InputTooLargeError(Hwp2mdError)`.
- `convert.py`: 블록→카운트 계산을 `memory` 와 공유하는 private 헬퍼 1개로 묶는다(이름 자유, 예 `_count_blocks(blocks) -> tuple[int, int, int, int]`). `convert()` 시그니처·반환·파일 출력·`FileNotFoundError(str(path))` 동작 불변. **순환 import 금지**: `memory.py` 가 `convert.py` 를 import 하고, 반대는 하지 않는다.
- `__init__.py`: `from .memory import MemoryResult, convert_bytes` 추가, `__all__` 에 2개 추가(정렬 유지). `hwp2md.web` 은 import 하지 않는다.

### 4-C. HTTP API (`src/hwp2md/web/app.py`, S5)
```python
def create_app() -> starlette.applications.Starlette: ...
def build_runtime_zip() -> bytes: ...
STATIC_DIR: Path = Path(__file__).parent / "static"
```
| 메서드·경로 | 요청 | 응답 |
|-------------|------|------|
| `GET /` | - | `STATIC_DIR/index.html`, `text/html; charset=utf-8` |
| `GET /static/{path}` | - | `StaticFiles(directory=STATIC_DIR)` |
| `GET /api/health` | - | 200 `{"ok": true, "version": hwp2md.__version__}` |
| `POST /api/convert?name=<url-encoded 파일명>` | body = 원본 바이트, `Content-Type: application/octet-stream` | `convert_to_response(body, name)` 의 status + JSON body (`ensure_ascii=False`, `application/json`) |
| `POST /api/zip?name=<…>` | 같음 | 성공: 200 `application/zip`, `Content-Disposition: attachment; filename*=UTF-8''{urllib.parse.quote(stem + ".zip")}`, body = `build_zip(convert_bytes(...))`. 실패: `/api/convert` 와 같은 오류 JSON·status |
| `GET /pkg/hwp2md.zip` | - | 200 `application/zip`, `Cache-Control: no-store`, body = 앱 생성 시 1회 만든 `build_runtime_zip()` |
- `name` 없으면 `"document.hwp"`. `Content-Length` 헤더 값 > `MAX_INPUT_BYTES`(`hwp2md.memory.MAX_INPUT_BYTES` 를 요청 시점에 참조 — 테스트 monkeypatch 가능) 면 body 를 읽지 않고 413 `{"error":{"code":"too_large","message":"input exceeds 52428800 bytes"}}`. 헤더가 없으면 읽은 뒤 `convert_to_response` 가 판단.
- `build_runtime_zip()` 엔트리: `hwp2md/` 아래 모든 `*.py` 와 `py.typed` (경로 구성 요소에 `web` 또는 `__pycache__` 가 있으면 제외) + `olefile/` 아래 `*.py` (`Path(olefile.__file__).parent.glob("*.py")`). 엔트리 이름은 `hwp2md/memory.py` 형태, 날짜 1980-01-01.
- 업로드 바이트를 디스크에 쓰지 않는다(§2 C5 grep 이 0줄이어야 하므로 `app.py` 에 `open(` 문자열도 쓰지 않는다 — index 는 `FileResponse`, 소스 읽기는 `Path.read_bytes()`).

### 4-D. 서버 실행 (`src/hwp2md/web/server.py`, S5)
```python
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8765
def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, *, open_browser: bool = True) -> int: ...
```
- 시작 전 `socket` 으로 (host, port) bind 시험 → 실패 시 stderr `hwp2md: error: port {port} already in use`, return 1.
- stdout 1줄 `hwp2md serve: http://{host}:{port}/ (Ctrl+C 로 종료)` 출력 후(flush) `uvicorn.run(create_app(), host=host, port=port, log_level="warning")`. `open_browser` 면 `threading.Timer(1.0, webbrowser.open, [url])`. KeyboardInterrupt → return 0. 정상 종료 return 0.
- `src/hwp2md/web/__init__.py` 는 docstring 1줄만 (starlette import 금지).

### 4-E. 화면 DOM·JS 계약 (S7, S8, S10 공유)
| 선택자 | 역할 |
|--------|------|
| `body[data-state]` | `idle` \| `converting` \| `done` \| `error` |
| `#drop-zone` | 드롭 대상(dragover/drop), 클릭 시 `#file-input.click()` |
| `#file-input` | `<input type="file" accept=".hwp,.hwpx">` (숨김 가능, `set_input_files` 대상) |
| `#mode-toggle` | `<input type="checkbox">`, 라벨 텍스트 "브라우저 안에서만 처리" |
| `#mode-status[data-state]` | `server` "서버 모드" \| `loading` "브라우저 모드 준비 중…" \| `browser` "브라우저 모드: 파일이 서버로 전송되지 않습니다" \| `error` "브라우저 모드를 불러오지 못했습니다: <msg>" |
| `#file-name` | 현재 파일명 |
| `#result-meta` | `단락 N개 · 표 M개 · 제목 K개 · 이미지 I개` |
| `#preview` | `marked` 로 렌더한 `preview_markdown` HTML |
| `#raw` | `<pre>`, `textContent = markdown` (상대 링크, 그대로) |
| `#download` | `<button>`, 결과 전 `disabled`. 클릭 시 `<stem>.zip` 다운로드 (서버 모드: 보관 중인 File 을 `POST /api/zip` 재전송 → Blob; 브라우저 모드: Pyodide `build_zip`) |
| `#error` | `role="alert"`, 오류 없으면 `hidden` |
- 오류 문구(code → 표시): `empty` "빈 파일입니다", `too_large` "파일이 너무 큽니다 (최대 50MB)", `not_hwp` "HWP 5.0 또는 HWPX 파일이 아닙니다", `unsupported` "암호화되었거나 배포용 문서라 변환할 수 없습니다", `convert_failed` "변환 중 오류가 발생했습니다: " + message.
- 서버 모드 변환: `fetch("/api/convert?name=" + encodeURIComponent(file.name), {method: "POST", headers: {"Content-Type": "application/octet-stream"}, body: file})`.
- `marked` 설정: 동봉 `vendor/marked.min.js` (marked **12.0.2** UMD, `https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js` 를 S7 에서 1회 내려받아 커밋, 파일 첫 줄 라이선스 주석 유지). `marked.use({renderer: {html(token) { /^<br\s*\/?>$/i.test(token.text ?? token) ? "<br>" : escapeHtml(...) }}})` — `<br>` 만 통과, 그 밖 원시 HTML 은 이스케이프.
- 브라우저 모드 (`pyodide-runner.js`, 전역 `window.Hwp2mdBrowser`):
```js
// PYODIDE_VERSION 은 S2 스파이크가 확정한 값 (기본 "0.27.7")
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
window.Hwp2mdBrowser = {
  async load(): Promise<void>,      // <script src=PYODIDE_BASE+"pyodide.js"> 주입 → loadPyodide({indexURL: PYODIDE_BASE})
                                    // → loadPackage("lxml") → fetch("/pkg/hwp2md.zip") (GET)
                                    // → pyodide.unpackArchive(buf, "zip", {extractDir: "/hwp2md_pkg"})
                                    // → runPython("import sys; sys.path.insert(0, '/hwp2md_pkg'); import hwp2md.memory")
  async convert(file: File): Promise<{status: number, body: object}>,
                                    // bytes = new Uint8Array(await file.arrayBuffer());
                                    // Python: json.dumps(convert_to_response(bytes(data), name)) → JSON.parse
  async zip(file: File): Promise<Blob>,   // Python: build_zip(convert_bytes(bytes(data), name)) → Uint8Array → Blob("application/zip")
};
```
- 브라우저 모드에서 `fetch`·`XMLHttpRequest`·`sendBeacon` 으로 파일 바이트를 보내는 코드 경로가 없어야 한다. 토글을 끄면 서버 모드로 돌아간다(Pyodide 는 메모리에 유지).
- 다운로드 파일명: `<stem>.zip` (`body.name` 사용).

### 4-F. CLI (`src/hwp2md/cli.py`, S6)
- `main(argv)`: `args = list(sys.argv[1:] if argv is None else argv)`; `args[:1] == ["serve"]` 이면 `_serve_main(args[1:])` 반환, 아니면 기존 코드 경로 그대로(기존 `_build_parser`·출력·종료 코드·`--help` 텍스트 불변).
- `_serve_main(argv)`: `argparse.ArgumentParser(prog="hwp2md serve")`, `--host`(기본 `localhost`), `--port`(int, 기본 8765), `--no-browser`(store_true). `try: from .web.server import serve` `except ImportError:` → stderr `hwp2md: error: web extra not installed — pip install 'hwp2md[web]'`, return 1. 성공 시 `return serve(host, port, open_browser=not no_browser)`.

### 4-G. 의존성 (`pyproject.toml`, S1, orchestrator)
```toml
[project.optional-dependencies]
web = ["starlette>=0.37", "uvicorn>=0.30"]

[dependency-groups]
dev = [ ...기존 4개..., "starlette>=0.37", "uvicorn>=0.30", "httpx>=0.27", "playwright>=1.45" ]
```
- dev 그룹에 web 패키지를 중복으로 넣는 이유: `uv sync`(INSTALL_CMD)가 extra 를 빼고 동기화하면 starlette 가 제거되므로, 개발 환경에서는 항상 설치되게 한다. "extra 없는 기본 설치" 검증은 §2 C7·C8 의 `sys.modules` 차단으로 한다.

### 4-H. E2E 공용 픽스처 (`tests/e2e/conftest.py` 추가분, S9 작성 → S10 사용)
```python
@pytest.fixture(scope="session")
def web_server(tmp_path_factory) -> Iterator[WebServer]: ...
# WebServer = dataclass(base_url: str, port: int, cwd: Path, tmpdir: Path, proc: subprocess.Popen[str])
# 빈 포트(socket bind 0) 선택, cwd=tmp_path_factory.mktemp("srv_cwd"), env TMPDIR=mktemp("srv_tmp"),
# [hwp2md_bin, "serve", "--no-browser", "--port", str(port)] 실행, /api/health 를 0.5초 간격 60회 폴링,
# 종료 시 proc.terminate(); proc.wait(10)
REAL_SAMPLES: list[Path]  # tests/fixtures/*.hwp 2개 + tests/fixtures/hwpx/*.hwpx 3개, 이름순 정렬 (unsupported/ 제외)
```

## 5. 단계 (Stage)
공통: 모든 Bash 는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작. 단계 시작 시 orchestrator 가 `git rev-parse HEAD > $T/.base-s<n>`. 각 단계 완료 조건에는 공통으로 "PROGRESS 기록 + `scripts/sanitize-check.sh hwp2md` OK + 커밋 `[T-20261023-web-preview][sN] ...`" 이 포함된다. 단계 공통 회귀 검증 `uv run pytest tests/unit -q && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` 은 S3 이후 모든 코드 단계의 검증에 포함된다(아래 "공통 회귀").

### Stage 1 — 의존성 추가와 브라우저 설치 (orchestrator)
- 목적: web extra·dev 의존성을 선언하고 Playwright chromium 을 설치한다.
- 담당: orchestrator 직접 (pyproject.toml 은 전용 파일, 변경 8줄 이하) → 설치는 runner(haiku)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §4-G
- 쓰기 범위: `pyproject.toml`, `uv.lock`(uv 가 갱신), `CLAUDE.md` 명령 블록 `INSTALL_CMD: uv sync && uv run playwright install chromium`
- 추가 행동: S6 전 `uv run hwp2md --help > $T/logs/help.before.txt` 저장 (C9 기준선).
- 검증: `uv sync && uv run playwright install chromium && uv run python -c "import starlette, uvicorn, httpx, playwright; print('ok')"` → `ok`; `uv build --wheel -o /private/tmp/claude-501/hwp2md-wheel-s1 && unzip -p /private/tmp/claude-501/hwp2md-wheel-s1/hwp2md-0.1.0-py3-none-any.whl hwp2md-0.1.0.dist-info/METADATA | grep -c "Provides-Extra: web"` → `1`; `uv run pytest tests/unit tests/e2e -q` → 286 passed.
- 완료 조건: 위 검증 + 커밋 `[T-20261023-web-preview][s1] deps: web extra, dev starlette/uvicorn/httpx/playwright`.
- 실패 시: `uv sync` 해석 실패 → 하한 버전을 낮추지 말고 오류 원문으로 BLOCKED. chromium 다운로드 실패 2회 → BLOCKED.

### Stage 2 — Pyodide 스파이크 (브라우저 안 import·변환 실증)
- 목적: CDN Pyodide + lxml 에서 현재 hwp2md 소스가 import 되고 샘플 5개 Markdown 이 네이티브와 같음을 증명하고 Pyodide 버전을 확정한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S1
- 입력: `src/hwp2md/**`(읽기만), `tests/fixtures/*.hwp`, `tests/fixtures/hwpx/*.hwpx`, §3 스파이크 BLOCKED 조건, §4-E 의 Pyodide 로딩 순서
- 쓰기 범위 (이것만):
  - `.ai/tasks/T-20261023-web-preview/spike/run_spike.py`
  - `.ai/tasks/T-20261023-web-preview/spike/spike.html`
  - `.ai/tasks/T-20261023-web-preview/logs/s2-spike.log`
  - 임시 산출물은 `/private/tmp/claude-501/hwp2md-spike/` 아래에만 (커밋 안 함)
- 방법(고정): `run_spike.py` 가 (1) `src/hwp2md` (web/ 제외) + `olefile/*.py` 를 `pkg.zip` 으로, 샘플 5개와 `spike.html` 을 `/private/tmp/claude-501/hwp2md-spike/www/` 에 복사, (2) `subprocess.Popen([sys.executable, "-m", "http.server", "8799", "--bind", "localhost"], cwd=www)`, (3) Playwright sync chromium headless 로 `spike.html?v=<VER>` 열기, (4) 페이지가 Pyodide 로드 → `loadPackage("lxml")` → `pkg.zip` unpack → 각 샘플을 `pyodide.FS.writeFile` 후 `hwp2md.convert(path, "/tmp/out")` 의 `markdown` 반환, (5) 네이티브 `hwp2md.convert(sample, tmp)` markdown 과 비교, (6) 로드 시간을 3회 측정(페이지 새로 열기), (7) http.server 종료. 버전 시도 순서 `0.27.7` → `0.26.4` → `0.28` 계열 최신(jsDelivr 에 존재하는 것). 처음 5/5 를 낸 버전으로 확정.
- 산출물: `logs/s2-spike.log` 에 `PYODIDE_VERSION=<v>`, `LXML_VERSION=<v>`, `LOAD_SECONDS=<a>,<b>,<c>`, 샘플별 `FIXTURE <name> OK|DIFF`, 마지막 줄 `SPIKE OK 5/5` 또는 `SPIKE FAIL <사유>`.
- 검증: `uv run python .ai/tasks/T-20261023-web-preview/spike/run_spike.py > .ai/tasks/T-20261023-web-preview/logs/s2-spike.log 2>&1; tail -1 .ai/tasks/T-20261023-web-preview/logs/s2-spike.log` → `SPIKE OK 5/5`
- 완료 조건: 검증 + 보고서에 확정 `PYODIDE_VERSION` 기재 (orchestrator 가 PROGRESS 에 기록, S8 프롬프트에 그 값을 넣는다) + 커밋 `[…][s2] spike: pyodide <v> + lxml converts 5/5 samples`.
- 실패 시: §3 스파이크 BLOCKED 조건 1~5. 해당하면 BLOCKED, S3 이후 진행 안 함(S3·S4 는 브라우저 모드와 무관하지만 사용자 결정 후 범위가 바뀔 수 있으므로 멈춘다).

### Stage 3 — 리더 바이트 입력
- 목적: 포맷 감지와 두 리더가 `bytes` 를 디스크 없이 읽는다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S2
- 입력: §4-A, `src/hwp2md/detect.py`, `hwp5/reader.py`, `hwpx/reader.py`, `convert.py`(read_blocks 만)
- 쓰기 범위:
  - `src/hwp2md/source.py` (신규)
  - `src/hwp2md/detect.py`
  - `src/hwp2md/hwp5/reader.py`
  - `src/hwp2md/hwpx/reader.py`
  - `tests/unit/test_source_bytes.py` (신규)
- 참고: `convert.read_blocks` 의 타입 힌트 확장은 S4 에서 한다(이 단계 쓰기 범위 아님). 이 단계 테스트는 `detect_format`·각 리더 `read_blocks` 를 직접 호출한다.
- 테스트 케이스(최소): 샘플 5개 `read_blocks(path) == read_blocks(path.read_bytes())`; `detect_format(bytes)` 가 hwp5 2개·hwpx 3개 판정; 100바이트 `b"x"*100` → `NotHwpFileError` 이고 `builtins.open` 을 감시(monkeypatch)해 그 bytes 를 경로로 여는 호출 0회; 깨진 zip bytes(`b"PK\x03\x04" + b"\0"*200`) → `NotHwpFileError`, 메시지에 `<memory>`; Path 입력 오류 메시지가 기존 문자열 그대로(`not an HWP 5.0 or HWPX file: <path>`).
- 검증: `uv run pytest tests/unit/test_source_bytes.py -q` → 실패 0, ≥ 10 passed; 공통 회귀 → 240 + 신규 passed, ruff·mypy 0.
- 완료 조건: 검증 + 커밋 `[…][s3] readers accept bytes via BytesIO`.
- 실패 시: 기존 테스트 실패 → 이 단계 diff 를 `git restore` 후 RETRY(최대 3).

### Stage 4 — 메모리 변환 API
- 목적: `convert_bytes` 와 미리보기·zip·응답 함수를 제공하고 `convert()` 출력은 불변으로 둔다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S3
- 입력: §4-B, `src/hwp2md/convert.py`, `images.py`, `render.py`(읽기만), `errors.py`
- 쓰기 범위:
  - `src/hwp2md/memory.py` (신규)
  - `src/hwp2md/convert.py`
  - `src/hwp2md/errors.py`
  - `src/hwp2md/__init__.py`
  - `tests/unit/test_memory.py` (신규)
- 테스트 케이스(최소): `test_same_as_convert[<샘플 5개>]`(markdown 바이트, 카운트 4종, images 이름·바이트·순서 == `convert()` 디스크 출력); `브라더…hwpx` 이미지 1개 46249B·mime `image/png`; 쓰기 차단 가드(`builtins.open` 쓰기 모드 `w/a/x/+`, `Path.write_bytes`, `Path.write_text`, `tempfile.mkstemp/mkdtemp/NamedTemporaryFile/TemporaryDirectory` 를 예외로 monkeypatch) 하에서 `convert_bytes`+`build_zip`+`to_payload` 성공; zip 엔트리 이름·`date_time == (1980,1,1,0,0,0)`·압축 해제 바이트 == 디스크 출력; 이미지 없는 문서 zip 엔트리 1개·`markdown_with_data_uris == markdown`; `safe_stem` 표(`"a/b/c.hwp"→"c"`, `"C:\\x\\y.hwpx"→"y"`, `""→"document"`, `".."→"document"`, `"a.b.hwp"→"a.b"`); `convert_to_response` 5종 코드·status(too_large 는 `monkeypatch.setattr(memory, "MAX_INPUT_BYTES", 10)`), 예외 미전파; subprocess 로 C7 명령과 같은 웹 모듈 차단 import + `convert_bytes` 성공 + `hwp2md.web` 미로드.
- 검증: `uv run pytest tests/unit/test_memory.py -q` → 실패 0, ≥ 20 passed; C5 grep (`src/hwp2md/memory.py src/hwp2md/source.py` 대상) → 0줄; C7 → `False`; 공통 회귀 → 기존 240 포함 실패 0.
- 완료 조건: 검증 + 커밋 `[…][s4] memory conversion API (convert_bytes, zip, payload)`.
- 실패 시: `convert()` 관련 기존 테스트 실패 → 공유 헬퍼 되돌리고 `convert.py` 는 `read_blocks` 타입만 바꾸는 최소안으로 RETRY.

### Stage 5 — 웹 서버 앱 (Starlette)
- 목적: HTTP API·정적 파일·런타임 패키지 zip·`serve()` 를 제공한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S4
- 입력: §4-C, §4-D, `src/hwp2md/memory.py`
- 쓰기 범위:
  - `src/hwp2md/web/__init__.py` (신규)
  - `src/hwp2md/web/app.py` (신규)
  - `src/hwp2md/web/server.py` (신규)
  - `src/hwp2md/web/static/index.html` (신규, 자리표시: `<!doctype html><title>hwp2md</title><main id="app"></main>` — S7 이 교체)
  - `tests/unit/test_web_app.py` (신규)
- 테스트 케이스(최소, `starlette.testclient.TestClient`): `/api/health` 200·버전; `/` 200 `text/html`; `/api/convert` 샘플 2개(hwp5 1, 이미지 있는 hwpx 1) 200·`markdown == convert_bytes(...).markdown`·`preview_markdown` 에 `data:image/png;base64,`; 한글 파일명 `?name=` 인코딩; not_hwp 415; empty 400; `memory.MAX_INPUT_BYTES` 를 10 으로 monkeypatch 하고 11바이트 이상 body 전송 → 413 `too_large`; `/api/zip` 200·`Content-Disposition` 에 `filename*=UTF-8''`·zip 엔트리; `/api/zip` not_hwp 415 JSON; `/pkg/hwp2md.zip` 에 `hwp2md/__init__.py`, `hwp2md/memory.py`, `hwp2md/hwpx/reader.py`, `olefile/__init__.py` 있고 `hwp2md/web/` 로 시작하는 엔트리 0개·`__pycache__` 0개; 쓰기 차단 가드 하 convert·zip 200; `serve()` 포트 사용 중 → 1 과 stderr 문구(소켓을 먼저 점유해 검증, uvicorn 은 띄우지 않음).
- 검증: `uv run pytest tests/unit/test_web_app.py -q` → 실패 0, ≥ 14 passed; C5 grep(`src/hwp2md/web/app.py` 포함 3파일) → 0줄; 공통 회귀.
- 완료 조건: 검증 + 커밋 `[…][s5] web app: convert/zip/health/pkg endpoints, serve()`.
- 실패 시: mypy 가 starlette/uvicorn 타입으로 실패 → `# type: ignore[...]` 는 줄 단위·코드 지정만 허용, 2회 실패 시 BLOCKED `NEEDS: mypy override (pyproject)`.

### Stage 6 — CLI `serve` 하위 명령 (cli.py 전용 단계)
- 목적: `hwp2md serve` 를 연결하고 기존 CLI 동작을 유지한다.
- 담당: implementer(opus) — 쓰기 범위가 orchestrator 전용 파일 1개뿐인 단계(프로젝트 CLAUDE.md 규칙)
- 병렬 가능: 아니오 · 선행: S5
- 입력: §4-F, `src/hwp2md/cli.py`, `src/hwp2md/web/server.py`(읽기만)
- 쓰기 범위:
  - `src/hwp2md/cli.py`
- 검증: (1) `uv run hwp2md --help | diff - .ai/tasks/T-20261023-web-preview/logs/help.before.txt` → 출력 0줄; (2) C8 명령 → stderr `hwp2md[web]`, `exit=1`; (3) `uv run hwp2md serve --no-browser --port 8765 > /private/tmp/claude-501/serve.log 2>&1 & for i in $(seq 1 30); do curl -sf http://localhost:8765/api/health && break; sleep 1; done; lsof -ti tcp:8765 | xargs kill 2>/dev/null` → `{"ok":true,"version":"0.1.0"}`; (4) `uv run pytest tests/e2e -q` → 46 passed; (5) `uv run hwp2md serve --help` 종료 0, `--port` 포함; 공통 회귀.
- 완료 조건: 검증 + 커밋 `[…][s6] cli: serve subcommand`. **이어서 orchestrator 작업**: `CLAUDE.md` 명령 블록을 `DEV_CMD: uv run hwp2md serve --no-browser --port 8765`, `DEV_URL: http://localhost:8765`, `DEV_READY: curl -sf http://localhost:8765/api/health >/dev/null` 로 갱신하고 같은 커밋 또는 `[…][s6] claude.md: dev commands` 로 커밋.
- 실패 시: (1) diff 가 0줄이 아니면 RETRY — 기존 파서 코드에 손대지 않는 방향으로.

### Stage 7 — 서버 모드 화면
- 목적: 드롭→미리보기·원문·zip 다운로드·오류 표시 화면을 만든다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S6
- 입력: §4-E, §4-C
- 쓰기 범위:
  - `src/hwp2md/web/static/index.html`
  - `src/hwp2md/web/static/app.js` (신규)
  - `src/hwp2md/web/static/style.css` (신규)
  - `src/hwp2md/web/static/vendor/marked.min.js` (신규, `curl -fsSL https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js -o …`)
  - `.ai/tasks/T-20261023-web-preview/spike/ui_smoke.py` (신규)
- 화면 요구: 상단 제목 "hwp2md 미리보기"·드롭 영역("HWP·HWPX 파일을 끌어다 놓거나 클릭해서 선택")·`#mode-toggle`(이 단계에서는 `disabled`, 라벨 표시)·`#mode-status` "서버 모드"; 아래 2단(왼쪽 `#preview`, 오른쪽 `#raw`), 너비 900px 미만에서는 세로 배치; 표에 테두리, 이미지는 `max-width:100%`. 외부 CDN 의존 없음(서버 모드는 오프라인 동작).
- `ui_smoke.py <mode>`: `mode=server` 이면 `hwp2md serve --no-browser --port 8766` 를 띄우고 Playwright headless 로 `브라더 공공기관 보고서 양식.hwpx` 를 `#file-input` 에 넣고 `body[data-state=done]` 대기 후 `#preview img` 1개(`naturalWidth>0`)·`#preview table` 8개 확인, 스크린샷 `$ILLY_SHOT_DIR/smoke_server.png`(기본 `.ai/tasks/T-20261023-web-preview/screenshots/`), 서버 종료. 확인 실패 시 종료 코드 1. (S8 이 `mode=browser` 분기를 추가)
- 검증: `uv run python .ai/tasks/T-20261023-web-preview/spike/ui_smoke.py server; echo exit=$?` → `exit=0` + 스크린샷 존재; `uv run pytest tests/unit/test_web_app.py -q` 실패 0; `uv build --wheel -o /private/tmp/claude-501/hwp2md-wheel-s7 && unzip -l /private/tmp/claude-501/hwp2md-wheel-s7/*.whl | grep -c "hwp2md/web/static/"` → ≥ 4.
- 완료 조건: 검증 + orchestrator 가 `smoke_server.png` 를 Read 로 열어 드롭 영역·미리보기·원문이 보이는지 확인 + 커밋 `[…][s7] web ui: server mode preview, raw, zip download`.
- 실패 시: marked 다운로드 실패 2회 → BLOCKED `NEEDS: 렌더러 결정`(§7 Q4 대안).

### Stage 8 — 브라우저 전용 모드 (Pyodide)
- 목적: 토글을 켜면 Pyodide 로 브라우저 안에서 변환·zip 하고 파일을 보내지 않는다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S7 (같은 파일 `app.js`·`index.html`)
- 입력: §4-E 브라우저 모드, S2 확정 `PYODIDE_VERSION`(orchestrator 가 프롬프트에 기재), `spike/spike.html`(로딩 코드 참고)
- 쓰기 범위:
  - `src/hwp2md/web/static/pyodide-runner.js` (신규)
  - `src/hwp2md/web/static/app.js`
  - `src/hwp2md/web/static/index.html`
  - `src/hwp2md/web/static/style.css`
  - `.ai/tasks/T-20261023-web-preview/spike/ui_smoke.py`
- `ui_smoke.py browser`: 서버(8766) 기동 → 토글 클릭 → `#mode-status[data-state=browser]` 120초 대기 → `page.on("request")` 기록 비우기 → 샘플 5개를 차례로 넣고 각 `#raw` 를 저장 → `#download` 클릭 다운로드 1회 → 기록 중 `method != "GET"` 0개·URL 경로 `/api/` 0개 확인 → 같은 5개를 토글 끈 서버 모드로 넣어 `#raw` 비교 5/5 동일 → 스크린샷 `smoke_browser.png`. 실패 시 종료 1.
- 검증: `uv run python .ai/tasks/T-20261023-web-preview/spike/ui_smoke.py browser; echo exit=$?` → `exit=0`; `uv run python .ai/tasks/T-20261023-web-preview/spike/ui_smoke.py server` → `exit=0`(회귀); `grep -nE "sendBeacon|XMLHttpRequest" src/hwp2md/web/static/*.js` → 0줄.
- 완료 조건: 검증 + orchestrator 가 `smoke_browser.png` 확인(상태 문구 "브라우저 모드: 파일이 서버로 전송되지 않습니다") + 커밋 `[…][s8] web ui: browser-only mode via pyodide`.
- 실패 시: S2 에서 된 로딩이 여기서 실패 → spike.html 과 diff 비교 후 RETRY(최대 3). 출력 불일치 → BLOCKED(§3 같은 오류 2회 규칙).

### Stage 9 — E2E: 서버 프로세스·HTTP API·CLI
- 목적: 실제 `hwp2md serve` 프로세스를 상대로 API·저장 흔적 없음·CLI 분기를 검증한다.
- 담당: test-writer(sonnet) → runner(haiku)
- 병렬 가능: 예 — S11 과 병렬 (worktree 격리, 쓰기 범위 교집합 없음: S9 `tests/e2e/**` ↔ S11 `README.md`, `docs/decisions.md`) · 선행: S8
- 입력: §4-C, §4-D, §4-F, §4-H, `tests/e2e/conftest.py`, `tests/e2e/test_cli_convert.py`(스타일 참고)
- 쓰기 범위:
  - `tests/e2e/conftest.py` (기존 내용 유지, §4-H 픽스처·`REAL_SAMPLES` 추가만)
  - `tests/e2e/test_web_api.py` (신규)
- 케이스(최소 12): health; `/` html 에 `id="drop-zone"`; 샘플 5개 parametrize `/api/convert` markdown == CLI 로 tmp 에 변환한 `.md` 바이트; 이미지 hwpx `/api/zip` 엔트리 2개·바이트 == CLI 출력; not_hwp 415; empty 400; Content-Length 초과 413(httpx 로 헤더 지정); `/pkg/hwp2md.zip` 목록; `test_no_files_written`(모든 요청 후 `web_server.cwd`·`web_server.tmpdir` 아래 `rglob("*")` 0개); 포트 점유 상태에서 두 번째 `hwp2md serve --port <같은 포트>` → 종료 1·stderr `already in use`; C8 extra 미설치 subprocess → 1·`hwp2md[web]`; 기존 변환 `hwp2md <synthetic_hwp> -o tmp` 종료 0(분기 회귀).
- 검증: `uv run pytest tests/e2e/test_web_api.py -q` → 실패 0, ≥ 12 passed; `uv run pytest tests/e2e -q` → 기존 46 포함 실패 0.
- 완료 조건: 검증 + `logs/s9-e2e-api.log` + 커밋 `[…][s9] e2e: web api, no-disk, serve cli`.
- 실패 시: §5 E2E 실패 분류표(e2e-standard)대로 test-writer/implementer 재호출. test-writer 2회 실패 → opus.

### Stage 10 — E2E: 화면 두 모드·무전송·출력 동일·스크린샷
- 목적: 사용자 관점에서 두 모드를 검증하고 스크린샷을 남긴다.
- 담당: test-writer(sonnet) → runner(haiku)
- 병렬 가능: 아니오 · 선행: S9 (conftest 픽스처 사용)
- 입력: §4-E, §4-H, `spike/ui_smoke.py`(로직 참고), S2 확정 버전
- 쓰기 범위:
  - `tests/e2e/test_web_ui.py` (신규)
- 구성: Playwright sync API 직접 사용(pytest-playwright 플러그인 없음). module scope `browser` 1개, 브라우저 모드 page 는 module scope 로 Pyodide 1회만 로드. 스크린샷 경로 `os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots")`. 브라우저 모드 테스트 docstring 에 "jsDelivr CDN 접근 필요" 명시(skip 금지).
- 케이스(최소 8): `test_server_mode_preview`(이미지 hwpx: img 1·data URI·naturalWidth>0·table 8·`#raw` 에 `![그림 1](브라더%20공공기관%20보고서%20양식_images/img_001.png)`·`#result-meta` "이미지 1개" → `web_server_preview.png`); `test_drop_event`(DataTransfer 로 `#drop-zone` 에 drop 이벤트 dispatch → done); `test_server_mode_zip_download`(`expect_download`, 파일명 `<stem>.zip`, 엔트리·바이트 == CLI); `test_error_display`(tmp 의 `not.hwp` 텍스트 파일 → `#error` 문구 → `web_error.png`); `test_browser_mode_sends_no_file`(C11: 대조군 서버 모드 POST 1개·`post_data_buffer` 길이 == 파일 크기, 브라우저 모드 5개 + zip 1회 후 non-GET 0·`/api/` 0 → `web_browser_preview.png`); `test_modes_produce_identical_markdown`(C12, 5개); `test_browser_mode_zip_matches_server`(엔트리 이름·바이트 동일); `test_browser_mode_error_same_code`(같은 텍스트 파일 → 같은 `#error` 문구).
- 검증 (runner, 한 번의 Bash):
  ```bash
  cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261023-web-preview; mkdir -p $T/logs $T/screenshots
  [ -f $T/logs/e2e.log ] && mv $T/logs/e2e.log $T/logs/e2e.prev.log
  START=$(date +%s); ILLY_SHOT_DIR=$T/screenshots uv run pytest tests/e2e -q > $T/logs/e2e.log 2>&1; echo "exit=$?" >> $T/logs/e2e.log; echo "seconds=$(( $(date +%s) - START ))" >> $T/logs/e2e.log
  tail -3 $T/logs/e2e.log; grep -E "failed|FAILED|Error" $T/logs/e2e.log | head -10; ls $T/screenshots
  ```
  (macOS 에 `timeout` 없음 → Bash 도구 timeout 600000 으로 상한) → `exit=0`, `seconds` ≤ 300, passed ≥ 66, 스크린샷 3개(`web_server_preview.png`, `web_browser_preview.png`, `web_error.png`) 존재.
- 완료 조건: 검증 + reviewer 가 아닌 orchestrator 1차 Read 로 스크린샷 3개 비어 있지 않음 확인 + 커밋 `[…][s10] e2e: web ui both modes, no-upload, parity, screenshots`.
- 실패 시: 플레이키(같은 테스트가 재실행 시 통과) 1회라도 → 실패로 보고, 대기 조건 수정은 test-writer, 2회 실패 → opus.

### Stage 11 — 문서 (README·decisions)
- 목적: 설치·실행 방법과 결정 기록을 남긴다.
- 담당: implementer(opus)
- 병렬 가능: 예 — S9 와 병렬 (worktree 격리) · 선행: S8
- 입력: 이 플랜 §4·§7 결정값, `logs/s2-spike.log`(PYODIDE_VERSION), README "설치와 실행" 절, `docs/decisions.md` 형식
- 쓰기 범위:
  - `README.md` ("설치와 실행 (개발 중)" 절과 "현재 지원" 문단만)
  - `docs/decisions.md` (끝에 4건 추가만)
- 내용: README — `pip install 'hwp2md[web]'`(개발: `uv sync`), `hwp2md serve [--port 8765] [--no-browser]`, 화면 사용법 3줄, "브라우저 안에서만 처리" 는 첫 사용 시 jsDelivr 에서 Pyodide(약 10MB+)를 받음·파일은 서버로 가지 않음, 이름이 `serve` 인 파일은 `hwp2md ./serve`, 업로드는 저장하지 않음. decisions — `## 2026-10-23 웹 프레임워크: Starlette+uvicorn (extra web)`, `## 2026-10-23 메모리 변환: Source = Path | bytes, olefile 에는 BytesIO`, `## 2026-10-23 브라우저 모드: Pyodide <v> CDN + 서버가 소스 zip 제공`, `## 2026-10-23 미리보기 렌더러: 동봉 marked 12.0.2, <br> 외 HTML 이스케이프` 각 2~3줄(이유 포함).
- 검증: `grep -c "hwp2md serve" README.md` → ≥ 2; `grep -c "^## 2026-10-23" docs/decisions.md` → 4; `$ILLY_ROOT/scripts/sanitize-check.sh hwp2md` → OK.
- 완료 조건: 검증 + 커밋 `[…][s11] docs: web preview usage and decisions`.
- 실패 시: sanitize 실패 → 해당 문구 수정 RETRY.

### Stage 12 — 리뷰·결과 기록
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: S9, S10, S11
- 입력: `git diff $(cat $T/.base-s1)..HEAD`, `logs/e2e.log`, `logs/s2-spike.log`, 스크린샷 3개 + `smoke_*.png`, §2 표
- 쓰기 범위: reviewer 없음(읽기만). scribe: `.ai/tasks/T-20261023-web-preview/RESULT.md`, `.ai/tasks/T-20261023-web-preview/PROGRESS.md`(끝 항목 추가). `.ai/STATE.md` 는 orchestrator 가 갱신.
- 검증: reviewer 가 §2 C1~C18 각각에 pass/fail + 근거(명령 출력 또는 스크린샷 관찰) 기재, C14~C16 은 스크린샷을 Read 로 직접 열어 판정; OUT 파일(§1) 변경 0 (`git diff --stat $(cat $T/.base-s1)..HEAD -- src/hwp2md/hwp5/body.py src/hwp2md/hwpx/body.py src/hwp2md/render.py src/hwp2md/blocks.py src/hwp2md/images.py tests/unit/test_convert.py tests/e2e/test_cli_convert.py` → 출력 0줄).
- 완료 조건: RESULT.md 존재, 성공 기준 표 전부 pass, orchestrator 가 tasks.md 17개 체크 후 `openspec validate web-preview` → valid, archive 는 사용자 RESULT 검토 후 `/implement` 마감 절차대로. 커밋 `[…][done] ...`.

## 6. 병렬 실행 맵
```
S1(orch) ─> S2 spike ─> S3 ─> S4 ─> S5 ─> S6(cli.py) ─> S7 ─> S8 ─┬─> S9 E2E-api ─> S10 E2E-ui ─┬─> S12 리뷰
                                                                    └─> S11 문서 ────────────────┘
```
- 병렬 묶음: {S9, S11} 만. 쓰기 범위 대조: S9 = `tests/e2e/conftest.py`, `tests/e2e/test_web_api.py` / S11 = `README.md`, `docs/decisions.md` → 교집합 없음(planner 확인). S11 이 쓰는 단계이고 S9 의 test-writer 도 쓰는 단계라 **worktree 격리**(`isolation: "worktree"`)로 띄운다. S9 runner 와 S11 은 포트 공유 없음(S11 은 서버를 띄우지 않음).
- S10 은 S9 의 conftest 픽스처를 쓰므로 순차.
- 그 외 전부 순차: S3→S8 은 같은 파일(`convert.py`, `app.js`, `index.html`)을 잇달아 만지거나 앞 단계 API 를 import 한다.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
> 2026-10-23 사용자 답: "기본값" — Q1~Q7 모두 기본값 채택.
- [x] Q1. 웹 프레임워크 — 기본값: **Starlette + uvicorn** (extra `hwp2md[web]`). 근거: 순수 파이썬 소형 의존성, 정적 파일·TestClient 내장, pydantic 불필요. 대안: 표준 라이브러리 `http.server`(의존성 0, 대신 extra 가 비고 라우팅·테스트를 직접 작성), FastAPI(pydantic 추가).
- [x] Q2. Pyodide 로딩 방식 — 기본값: **jsDelivr CDN, 버전 고정**(S2 가 0.27.7 부터 시도해 확정). 대안: wheel 에 동봉(오프라인 동작, 패키지 수십 MB 증가).
- [x] Q3. hwp2md 소스를 브라우저에 싣는 방식 — 기본값: **서버가 실행 중인 `hwp2md`(web 제외)+`olefile` 소스를 `GET /pkg/hwp2md.zip` 으로 즉석 제공**. 대안: 빌드된 wheel 정적 제공 + micropip(빌드 단계 필요, olefile 은 PyPI 접근 필요).
- [x] Q4. 미리보기 Markdown 렌더러 — 기본값: **marked 12.0.2 를 `static/vendor/` 에 동봉**, `<br>` 외 원시 HTML 이스케이프. 대안: hwp2md 출력(제목·단락·표·이미지)만 다루는 자체 JS 렌더러 ~100줄.
- [x] Q5. 기본 포트·바인드 — 기본값: **localhost:8765**, 외부 바인드는 `--host` 로만. 인증 없음.
- [x] Q6. E2E 가 인터넷(jsDelivr) 접근을 필요로 하는 것 — 기본값: **허용**(브라우저 모드 테스트 3~4개가 CDN 필요, 오프라인이면 실패로 보고·skip 안 함). 대안: 브라우저 모드 테스트를 별도 마커로 분리해 기본 E2E_CMD 에서 제외(이 경우 C11·C12 는 별도 명령으로 검증).
- [x] Q7. Playwright chromium 다운로드(~150MB, `~/Library/Caches/ms-playwright`) — 기본값: **S1 에서 설치**.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| CDN·Playwright 다운로드가 프록시에 막힘 | 중 | S1·S2 초반에 확인, §3 BLOCKED 조건으로 조기 중단 |
| Pyodide lxml 이 보안 파서 옵션을 다르게 처리해 Markdown 차이 | 저 | S2 가 5개 샘플 바이트 비교로 선검증 |
| olefile 이 1536B 미만 bytes 를 경로로 해석 | 확정(코드 확인) | §4-A: 항상 `io.BytesIO` 로 감쌈, S3 테스트로 고정 |
| `uv sync` 가 extra 를 제거해 개발 환경에서 starlette 사라짐 | 확정(uv 기본 exact sync) | §4-G: dev 그룹에 중복 선언 |
| 브라우저 모드 Pyodide 로딩 지연으로 E2E 300초 초과 | 중 | module scope page 로 1회 로드, 대기 상한 120초. 초과 시 Q6 대안(마커 분리)을 RESULT 에 제안 |
| `hwp2md serve` 분기가 `serve` 라는 이름의 입력 파일을 가로챔 | 저 | README 에 `./serve` 안내, 기존 `--help` diff 0줄 검증 |
| 업로드 바이트가 starlette 내부에서 디스크 스풀 | 저 | raw body(`await request.body()`)는 메모리, multipart 미사용. C6 동적 검증 |
| `app.js` 단일 파일을 S7·S8 이 잇달아 수정 | 확정 | 순차 배치, S8 이 S7 ui_smoke `server` 를 회귀로 재실행 |

## 9. 예상 비용
- 예상 단계 수: 12 · 서브에이전트 호출: 약 17회(implementer 8, test-writer 2, runner 4, reviewer 1, scribe 1, 재시도 여유 1) · 주 모델: opus 약 55% / sonnet 25% / haiku 20%
- 시간: 단계당 10~30분, 총 4~6시간(스파이크·브라우저 모드가 가장 긺).
