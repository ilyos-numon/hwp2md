# Design

## Context

- `convert(path, out_dir)` 는 `read_blocks(path)` → `render_blocks(blocks, image_dir=<stem>_images)` → `.md` 쓰기 → `_write_images` 순이다. 리더 입구는 경로만 받는다: `detect_format` 은 `olefile.isOleFile(str(path))`·`zipfile.is_zipfile(path)`, HWP 5.0 은 `olefile.OleFileIO(str(path))`, HWPX 는 `zipfile.ZipFile(path)`. 이후 파싱은 전부 바이트 기반이라 입구 3곳만 바꾸면 메모리 입력이 된다.
- 함정: olefile 0.47 의 `isOleFile(filename)`·`OleFileIO(filename)` 은 1536바이트 미만 `bytes` 를 **파일 경로로** 해석한다. 그래서 bytes 는 반드시 `io.BytesIO` 로 감싸서 넘긴다.
- 오류 메시지에 `{path}` 가 들어간다. bytes 입력은 라벨 `<memory>` 를 쓰고, 경로 입력의 문자열은 그대로 둔다.
- 의존성은 lxml·olefile 뿐. Pyodide 배포판에는 lxml 이 들어 있고 olefile 은 순수 파이썬(`olefile/__init__.py`, `olefile/olefile.py`) 이다. hwp2md 는 C 확장이 없다.
- `cli.py` 는 orchestrator 전용 파일(프로젝트 CLAUDE.md) 이라 serve 분기는 그 파일만 갖는 단계에서 넣는다. `pyproject.toml` 도 orchestrator 전용.
- 제약: macOS·zsh, `timeout` 없음, Docker 금지.

## Goals / Non-Goals

**Goals:**
- 하나의 Python 함수(`hwp2md.memory.convert_to_response`, `build_zip`)를 서버와 Pyodide 가 똑같이 호출해 두 모드 출력이 구조적으로 같아진다.
- 업로드 바이트는 서버 프로세스 메모리에서만 다룬다.
- 기본 설치·기존 CLI·`convert()` 출력은 바이트 단위로 불변.

**Non-Goals:**
- 여러 파일 동시 변환, 변환 이력, 사용자 계정, 원격 배포(localhost 기본, 인증 없음).
- Pyodide·lxml 오프라인 동봉(CDN 사용). Web Worker 분리.
- 미리보기 서식 편집, Markdown → HWP 역변환(README "하지 않는 것").

## Decisions

1. **웹 프레임워크: Starlette + uvicorn (extra `web`)** — 대안 A 표준 라이브러리 `http.server`: 의존성 0 이지만 라우팅·정적 파일·테스트 클라이언트를 직접 짜야 하고 ThreadingHTTPServer 종료 처리가 번거롭다. 대안 B FastAPI: pydantic 까지 끌어온다(이 앱엔 스키마 검증이 필요 없음). Starlette 는 순수 파이썬 소형 의존성, `StaticFiles`·`TestClient`(httpx) 를 제공, 타입 힌트 포함으로 mypy strict 통과가 쉽다.
2. **업로드는 raw body (`application/octet-stream`) + `?name=`** — multipart 를 쓰면 `python-multipart` 의존성이 추가된다. 브라우저는 `fetch(url, {method:"POST", body: file})` 로 충분하다.
3. **바이트 입력은 `Source = Path | bytes` + `io.BytesIO` 래핑** (`src/hwp2md/source.py`) — 리더 시그니처를 `Path | bytes` 로 넓히고, 경로 분기는 기존 코드 그대로 둔다.
4. **결과/오류 직렬화는 `memory.convert_to_response` 하나** — 서버는 status·body 를 JSONResponse 로, 브라우저는 `json.dumps(body, ensure_ascii=False)` 를 JS 로 넘긴다. 오류 코드 표가 한 곳에 있어 두 모드 문구가 갈라지지 않는다.
5. **브라우저에 hwp2md 를 싣는 방식: 서버가 실행 중인 소스를 zip 으로 즉석 제공 (`GET /pkg/hwp2md.zip`)** — `hwp2md/**/*.py` + `py.typed`(단, `hwp2md/web/**` 제외) + 설치된 `olefile/*.py` 를 앱 생성 시 메모리 zip 으로 만든다. Pyodide 는 `unpackArchive` 후 `sys.path` 에 추가. 대안 wheel 빌드는 hatchling 이 런타임에 필요하고, micropip+PyPI 는 olefile 을 위해 외부 PyPI 접근이 필요하다. 즉석 zip 은 서버 모드와 같은 소스 버전을 보장한다.
6. **Pyodide 로딩: jsDelivr CDN, 버전 고정** (`https://cdn.jsdelivr.net/pyodide/v<VER>/full/`) — 동봉하면 저장소·wheel 이 수십 MB 늘어난다. CDN 요청은 GET 이고 파일 바이트를 담지 않는다. 버전은 스파이크 단계가 lxml 로드·5개 샘플 변환 성공을 확인한 값으로 고정한다(우선 시도 0.27.7).
7. **미리보기 렌더러: 동봉 `marked` (UMD, 고정 버전) + HTML 이스케이프 훅** — 두 모드가 같은 JS 렌더러를 쓰므로 미리보기도 같다. 원시 HTML 은 hwp2md 표 셀의 `<br>` 만 허용하고 나머지는 이스케이프한다(문서 텍스트가 HTML 로 해석되지 않게).
8. **zip 엔트리 날짜 고정 (1980-01-01)** — 두 모드·두 번 실행에서 엔트리 메타데이터가 같다. 압축 바이트는 zlib 구현 차이로 다를 수 있으므로 동일성 검증은 엔트리 이름·내용 기준.
9. **`hwp2md serve` 분기는 `argv[0] == "serve"` 일 때만** — 기존 파서(`INPUT` 위치 인자)와 `--help` 출력을 건드리지 않는다. 이름이 정확히 `serve` 인 파일은 `./serve` 로 변환한다(README 에 적음).

## Risks / Trade-offs

- [Pyodide CDN 접근 불가(프록시)] → 스파이크 단계에서 먼저 확인. 실패하면 BLOCKED 로 멈추고 동봉 방식 결정을 사용자에게 넘긴다.
- [Pyodide 의 lxml 버전이 보안 파서 옵션(`resolve_entities`, `no_network`)을 다르게 처리] → 스파이크가 5개 샘플 Markdown 동일성으로 확인. 다르면 BLOCKED.
- [브라우저 모드 첫 로딩 10~40초] → 상태 표시(`#mode-status` loading) 와 E2E 대기 상한 120초.
- [E2E 가 인터넷(CDN)에 의존] → 결정성 원칙과 긴장. 브라우저 모드 테스트는 CDN 필요를 테스트 docstring 과 README 에 적고, 실패는 실패로 보고한다(skip 금지).

## Migration Plan

새 기능 추가뿐이다. 기존 사용자는 업데이트 후에도 `pip install hwp2md` 로 같은 동작을 얻고, 웹이 필요하면 `pip install 'hwp2md[web]'`.

## Open Questions

PLAN.md §7 에 기본값과 함께 있다(프레임워크, Pyodide 로딩, 패키지 전달, 렌더러, 포트).
