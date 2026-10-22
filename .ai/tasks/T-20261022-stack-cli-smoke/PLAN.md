# PLAN — T-20261022-stack-cli-smoke hwp2md 스택 확정 + CLI 스캐폴드 + HWP 5.0 스모크 변환

> 작성: planner(fable) · 2026-10-22 12:05 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: DONE)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> 모든 Bash는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. 아래 경로는 전부 이 디렉터리 기준 상대경로다.

## 0. 한 줄 목표
사용자가 `uv sync` 뒤 `uv run hwp2md input.hwp -o out/` 한 줄로 HWP 5.0 바이너리 문서의 본문 단락을 `out/input.md`(Markdown)로 받을 수 있다. 잘못된 입력(없는 파일, HWP가 아닌 파일, 암호화 문서)은 0이 아닌 종료 코드와 한 줄 에러로 거절된다.

## 1. 범위
### 포함 (IN)
- 스택 확정: Python ≥3.11, 패키징 hatchling + uv, 런타임 의존성 `olefile`, 개발 도구 pytest·ruff·mypy. 결정은 `docs/decisions.md`에 날짜+이유로 기록.
- 패키지 `src/hwp2md/` (src 레이아웃) + 콘솔 스크립트 `hwp2md` (`pyproject.toml [project.scripts]`).
- HWP 5.0 바이너리 읽기: OLE 컨테이너(`olefile`) → `FileHeader` 검사 → `BodyText/SectionN` zlib(raw deflate) 해제 → 레코드 순회 → `HWPTAG_PARA_TEXT` 디코드(제어문자 처리) → 단락 문자열 목록.
- Markdown 렌더: 비어 있지 않은 단락을 빈 줄로 구분해 `<stem>.md`로 저장.
- CLI: `hwp2md INPUT [-o OUT_DIR] [--version]`, 종료 코드 0/1/2/3, stdout 2줄(§4.5).
- 합성 HWP 5.0 fixture 생성기 `tests/synth_hwp5.py` (순수 파이썬 CFB writer + HWP 레코드 빌더). 실제 샘플이 `tests/fixtures/*.hwp`에 있으면 E2E가 자동으로 추가 실행.
- 단위 테스트 `tests/unit/`, E2E `tests/e2e/`(실제 `hwp2md` 콘솔 스크립트를 subprocess로 실행).
- 프로젝트 CLAUDE.md 명령 블록과 "orchestrator 전용 파일 (추가분)" 채우기 (orchestrator 직접).
- README에 "설치와 실행 (개발 중)" 절 추가.

### 제외 (OUT) — 절대 건드리지 않는다
- HWPX(XML) 파싱, `lxml` 의존성 선언 (다음 태스크. 이번엔 import도 선언도 하지 않는다).
- 표, 이미지 추출, 각주, 제목 계층(heading) 판별, 목차, `--split`, `--meta`, 섹션 분할, 메타데이터 JSON.
- 암호화·배포용(distribution) 문서 해독, DocInfo(글꼴·문자모양) 해석, PrvText/PrvImage 사용.
- README "하지 않는 것"(역변환 md→hwp, 글꼴·색상 서식 재현) — 제안조차 금지.
- 공개 샘플 HWP 다운로드(네트워크·라이선스). 실제 샘플 확보는 §7 질문.
- GitHub Actions 워크플로, LICENSE 파일, PyPI 배포.
- `doc/my_info/` (워크스페이스 읽기 전용 원본) 접근.

### 건드리면 안 되는 파일/디렉토리
- 서브에이전트 전 단계: `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.gitignore`, `uv.lock`, `.claude/**`, `docs/vision.md`, `src/.gitkeep`(삭제는 orchestrator가 S3 커밋 때).
- `pyproject.toml`은 Stage 1에서만 쓴다. 그 뒤 변경이 필요하면 NEEDS로 보고하고 orchestrator가 10줄 이하만 직접 고친다.
- `src/hwp2md/cli.py`는 Stage 6에서만 쓴다 (프로젝트 orchestrator 전용 파일 추가분, §4.8).

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| S1 | 설치 후 콘솔 스크립트가 동작 | `uv sync && uv run hwp2md --version` | stdout `hwp2md 0.1.0`, 종료 코드 0 |
| S2 | 합성 HWP 1개 → Markdown 변환 | `D=$(mktemp -d) && PYTHONPATH=tests uv run python -c "from pathlib import Path; from synth_hwp5 import write_hwp5; write_hwp5(Path('$D/sample.hwp'), ['테스트 문서 제목','본문 단락 1','','본문 단락 2'])" && uv run hwp2md $D/sample.hwp -o $D/out; echo "exit=$?"; cat $D/out/sample.md` | stdout 1행 `✓ sample.hwp → <D>/out/sample.md`, 2행 `  단락 3개`, `exit=0`, 파일 내용이 정확히 `테스트 문서 제목\n\n본문 단락 1\n\n본문 단락 2\n` |
| S3 | 실패 경로: 없는 파일 | `uv run hwp2md /nonexistent/x.hwp -o /tmp; echo "exit=$?"` | stderr `hwp2md: error: file not found: /nonexistent/x.hwp`, `exit=2` |
| S4 | 실패 경로: HWP가 아닌 파일 | `D=$(mktemp -d) && printf 'plain text' > $D/fake.hwp && uv run hwp2md $D/fake.hwp -o $D; echo "exit=$?"` | stderr `hwp2md: error: not an HWP 5.0 file: <D>/fake.hwp`, `exit=3` |
| S5 | E2E 테스트 통과 | `uv run pytest tests/e2e -q` | `failed` 0, `error` 0, passed ≥5. skipped는 `test_real_fixture_converts` 1건만 허용(실제 샘플이 없을 때 빈 parametrize) |
| S6 | 단위 테스트·린트·타입 통과 | `uv run pytest tests/unit -q && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | 네 명령 모두 종료 코드 0, mypy `Success: no issues found` |
| S7 | 익명화 검사 통과 | `/Users/illi/illy-projects/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` | `sanitize-check: OK (...)`, 종료 코드 0 |
| S8 | CLAUDE.md 명령 블록 완성 | `grep -c "채워 넣을 것" CLAUDE.md; grep -E "^(TEST_CMD|E2E_CMD|E2E_ONE):" CLAUDE.md` | 첫 명령 `0`, 둘째 명령이 §4.7의 세 줄과 글자 단위로 같음 |
| S9 | 결정 기록 | `grep -c "^## 2026-10-22" docs/decisions.md` | `3` |
| S10 | README 실행 방법 | `grep -c "uv run hwp2md" README.md` | `1` 이상 |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 오류(같은 예외 메시지 또는 같은 assert)로 수정 2회 실패.
- 동일 단계 재시도 3회 초과 (RETRY 3번째까지 허용, 4번째 시도 금지).
- 단계 하나에 20분 또는 도구 호출 상한 초과: implementer 40회(에이전트 하드 상한 60회에서 PARTIAL 반환), test-writer 40회, reviewer 25회, runner 15회, scribe 15회.
- `uv lock`/`uv sync`가 네트워크 오류(`Failed to fetch`, `Connection`, `timed out`)로 실패 — 재시도 1회 후 BLOCKED (사용자 네트워크 확인).
- Stage 1 이후 `pyproject.toml` 변경(의존성 추가 등) 없이 진행 불가 → NEEDS 보고. orchestrator가 10줄 이하면 직접 수정, 아니면 BLOCKED.
- 합성 fixture를 `olefile.OleFileIO`가 열지 못하는 문제를 Stage 4에서 2회 수정해도 못 고침 → BLOCKED, §7 질문 3의 대안(실제 샘플 제공)으로 사용자 결정.
- OUT 범위(HWPX, 표, 이미지, 각주) 코드를 넣어야만 테스트가 통과하는 상황 → BLOCKED (넣지 않는다).
- 테스트를 skip/약화해야만 통과 → 금지. 실패로 보고.

## 4. 인터페이스 계약 (모든 단계가 이 값을 그대로 쓴다. 바꾸면 BLOCKED)

### 4.1 패키지 레이아웃 (새 파일 경로는 이것만 허용)
```
pyproject.toml                       # Stage 1 (orchestrator 전용 파일, 전용 단계)
uv.lock                              # orchestrator가 `uv lock`으로 생성·커밋
src/hwp2md/__init__.py               # Stage 3 생성(__version__), Stage 5에서 export 추가
src/hwp2md/py.typed                  # Stage 3 (빈 파일)
src/hwp2md/errors.py                 # Stage 3
src/hwp2md/hwp5/__init__.py          # Stage 3 (빈 파일 또는 docstring 1줄)
src/hwp2md/hwp5/records.py           # Stage 3
src/hwp2md/hwp5/reader.py            # Stage 5
src/hwp2md/render.py                 # Stage 5
src/hwp2md/convert.py                # Stage 5
src/hwp2md/cli.py                    # Stage 6 (프로젝트 orchestrator 전용 파일 추가분, 전용 단계)
tests/synth_hwp5.py                  # Stage 4 (pytest pythonpath=tests 로 `import synth_hwp5`)
tests/unit/test_hwp5_records.py      # Stage 3
tests/unit/test_synth_hwp5.py        # Stage 4
tests/unit/test_convert.py           # Stage 5
tests/e2e/conftest.py                # Stage 8
tests/e2e/test_cli_convert.py        # Stage 8
tests/fixtures/.gitkeep              # Stage 8 (실제 샘플 *.hwp 를 사용자가 넣는 자리, *.hwp 는 .gitignore)
docs/decisions.md, README.md         # Stage 7
CLAUDE.md, .gitignore                # Stage 2 (orchestrator 직접)
```
`tests/` 아래에 `__init__.py`를 만들지 않는다 (rootdir 기반 수집 + pythonpath 설정으로 충분).

### 4.2 pyproject.toml (Stage 1은 이 내용을 그대로 쓴다. 주석 제외 추가·삭제 금지)
```toml
[project]
name = "hwp2md"
version = "0.1.0"
description = "Convert HWP 5.0 documents to Markdown without Hancom Office"
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["olefile>=0.46"]

[project.scripts]
hwp2md = "hwp2md.cli:main"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.10"]

[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/hwp2md"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src"]

[[tool.mypy.overrides]]
module = "olefile"
ignore_missing_imports = true
```
- mypy strict에서 `olefile` 반환값은 `Any`다. 반환 전에 `bytes(...)`, `list[...]` 변환 또는 `typing.cast`로 좁혀 `warn_return_any`를 피한다.
- `uv sync`는 `dev` 그룹을 기본 설치하고 패키지를 editable로 설치한다. `.venv/bin/hwp2md`가 생긴다.

### 4.3 공개 API (`src/hwp2md/`)
```python
# errors.py
class Hwp2mdError(Exception): """hwp2md 최상위 예외 (CLI 종료 코드 1)"""
class NotHwpFileError(Hwp2mdError): """OLE 아님 / FileHeader 시그니처 불일치 / BodyText/Section0 없음 (종료 코드 3)"""
class UnsupportedHwpError(Hwp2mdError): """암호화 또는 배포용 문서 (종료 코드 3)"""

# hwp5/records.py
HWPTAG_BEGIN = 0x10
HWPTAG_DOCUMENT_PROPERTIES = 0x10   # DocInfo 첫 레코드 (파서는 읽지 않음, fixture가 씀)
HWPTAG_PARA_HEADER = 0x42           # 66
HWPTAG_PARA_TEXT = 0x43             # 67
HWPTAG_PARA_CHAR_SHAPE = 0x44       # 68
HWPTAG_PARA_LINE_SEG = 0x45         # 69
HWPTAG_CTRL_HEADER = 0x47           # 71
HWPTAG_LIST_HEADER = 0x48           # 72
HWPTAG_TABLE = 0x4D                 # 77

@dataclass(frozen=True)
class Record:
    tag_id: int
    level: int
    payload: bytes

def iter_records(data: bytes) -> Iterator[Record]:
    """레코드 헤더 UINT32 LE: tag_id = v & 0x3FF, level = (v >> 10) & 0x3FF, size = (v >> 20) & 0xFFF.
    size == 0xFFF 이면 바로 다음 UINT32 LE 가 실제 size. 헤더 또는 payload가 잘리면 Hwp2mdError("truncated record at offset N")."""

def decode_para_text(payload: bytes) -> str:
    """UTF-16LE WCHAR 배열을 단락 문자열로. 규칙은 §4.4-C. 결과는 .strip() 적용."""

# hwp5/reader.py
HWP5_SIGNATURE = b"HWP Document File" + b"\x00" * 15     # 32 bytes
FILE_HEADER_SIZE = 256

@dataclass(frozen=True)
class FileHeader:
    version: tuple[int, int, int, int]   # (MM, nn, PP, rr)
    compressed: bool                      # properties bit 0
    encrypted: bool                       # properties bit 1
    distribution: bool                    # properties bit 2

def parse_file_header(raw: bytes) -> FileHeader:
    """len(raw) != 256 또는 raw[:32] != HWP5_SIGNATURE → NotHwpFileError.
    version = struct.unpack('<I', raw[32:36])[0] → ((v>>24)&0xFF, (v>>16)&0xFF, (v>>8)&0xFF, v&0xFF).
    properties = struct.unpack('<I', raw[36:40])[0]."""

def read_sections(path: Path) -> list[bytes]:
    """olefile.isOleFile(path) False → NotHwpFileError. 'FileHeader' 스트림 없음 → NotHwpFileError.
    encrypted 또는 distribution → UnsupportedHwpError.
    'BodyText/Section<N>' 스트림을 N 오름차순으로 읽어 compressed면 zlib.decompressobj(-15)로 해제(flush 포함), 아니면 그대로.
    Section0 이 없으면 NotHwpFileError."""

def read_paragraphs(path: Path) -> list[str]:
    """read_sections → 각 섹션 iter_records → tag_id == HWPTAG_PARA_TEXT 인 레코드만 decode_para_text.
    level 무시(표 셀 안 단락도 평문 단락으로 나온다 — 이번 범위에서 허용). 빈 문자열은 제외."""

# render.py
def render_markdown(paragraphs: Sequence[str]) -> str:
    """빈 문자열을 제외한 단락을 '\n\n' 으로 join 하고 끝에 '\n' 1개. 단락이 0개면 ''."""

# convert.py
@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int
    markdown: str

def convert(path: str | Path, out_dir: str | Path = ".") -> ConvertResult:
    """path 가 파일이 아니면 FileNotFoundError(str(path)). out_dir 을 mkdir(parents=True, exist_ok=True).
    output = Path(out_dir) / f"{Path(path).stem}.md" (덮어쓰기), encoding='utf-8', newline='\n'.
    paragraph_count = render 에 포함된(비어 있지 않은) 단락 수."""

# __init__.py (Stage 5 최종 상태)
__version__ = "0.1.0"
from .convert import ConvertResult, convert
from .errors import Hwp2mdError, NotHwpFileError, UnsupportedHwpError
__all__ = ["ConvertResult", "Hwp2mdError", "NotHwpFileError", "UnsupportedHwpError", "__version__", "convert"]

# cli.py
def main(argv: Sequence[str] | None = None) -> int:
    """§4.5. argparse 사용. 예외를 종료 코드로 바꾸고 traceback 을 출력하지 않는다. `if __name__ == "__main__": raise SystemExit(main())`"""
```

### 4.4 HWP 5.0 바이트 레이아웃 상수 (한컴 HWP 5.0 공개 명세 기준. 생성기와 파서가 공유)
**A. FileHeader 스트림 (정확히 256 bytes)**
| offset | 크기 | 값 |
|---|---|---|
| 0 | 32 | `b"HWP Document File"` + `\x00`×15 |
| 32 | 4 | 버전 UINT32 LE `0x05000300` → 튜플 (5, 0, 3, 0) |
| 36 | 4 | 속성 UINT32 LE. bit0 압축, bit1 암호화, bit2 배포용, bit3 스크립트, bit4 DRM, bit5 XMLTemplate, bit6 히스토리, bit7 전자서명, bit8 공인인증서 암호화, bit9 전자서명 예비, bit10 공인인증서 DRM, bit11 CCL. 기본 fixture 값 `0x00000001` |
| 40 | 4 | 추가 속성 UINT32 LE = 0 |
| 44 | 4 | 암호화 버전 UINT32 LE = 0 |
| 48 | 1 | KOGL 국가 = 0 |
| 49 | 207 | 예약, 0 |

**B. 스트림 압축**: 속성 bit0 = 1 이면 `DocInfo`, `BodyText/SectionN` 스트림 전체가 zlib raw deflate(헤더 없음). 해제 `zlib.decompressobj(-15)`, 생성 `zlib.compressobj(9, zlib.DEFLATED, -15)` + `.flush()`.

**C. PARA_TEXT WCHAR 제어문자 (코드 0~31). 그 외 코드는 문자**
- 8 WCHAR(16 bytes)를 차지하는 코드 (확장·인라인 컨트롤): `{1,2,3,4,5,6,7,8,9,11,12,14,15,16,17,18,19,20,21,22,23}`. 처리: 코드 9(탭)만 `" "` 출력, 나머지는 출력 없음. 모두 i += 8.
- 1 WCHAR 코드: `0` 출력 없음 · `10` 줄바꿈 → `"\n"` · `13` 단락 끝 → 디코드 종료(이후 바이트 무시) · `24` 하이픈 → `"-"` · `25~29` 예약, 출력 없음 · `30` 묶음 빈칸, `31` 고정폭 빈칸 → `" "`.
- 구현: 유지할 WCHAR 바이트를 bytearray에 모은 뒤 마지막에 한 번 `decode("utf-16-le", errors="replace")` (서로게이트 쌍 보존). payload 길이가 홀수면 마지막 1바이트 무시. 결과 `.strip()`.

**D. PARA_HEADER 레코드 payload (22 bytes, 버전 5.0.3 rr<2 이므로 추적 변경 2바이트 없음)**
```
UINT32 nchars          # 단락 글자 수(WCHAR 단위, 끝의 13 포함). 섹션 마지막 단락이면 bit31(0x80000000) set
UINT32 control_mask    # 0
UINT16 para_shape_id   # 0
UINT8  para_style_id   # 0
UINT8  column_type     # 0
UINT16 char_shape_count   # 1
UINT16 range_tag_count    # 0
UINT16 line_seg_count     # 1
UINT32 para_instance_id   # 0
```
**E. 단락 1개의 레코드 순서 (fixture 생성기 출력)**
1. PARA_HEADER (tag 0x42, level 0, 22 bytes)
2. PARA_TEXT (tag 0x43, level 1, nchars×2 bytes) = `text.encode("utf-16-le") + b"\r\x00"`
3. PARA_CHAR_SHAPE (tag 0x44, level 1, 8 bytes) = `UINT32 0, UINT32 0` (위치 0, 글자모양 id 0)
4. PARA_LINE_SEG (tag 0x45, level 1, 36 bytes) = 0×36
- 레코드 헤더 계산 예: tag 0x43, level 1, size 4 → `0x00400443`. size ≥ 0xFFF 이면 헤더 size 필드 = 0xFFF 뒤에 UINT32 실제 size (파서는 반드시 지원, 생성기는 짧은 텍스트만 쓰므로 미사용).
- `nchars` = `len(text.encode("utf-16-le")) // 2 + 1`. 빈 단락("")도 PARA_TEXT 2 bytes(`\r\x00`)를 쓴다 (실제 한컴 파일은 생략하지만 파서는 양쪽을 처리).

**F. DocInfo 스트림 (fixture만, 파서는 읽지 않음)**: 레코드 1개 HWPTAG_DOCUMENT_PROPERTIES(tag 0x10, level 0, 26 bytes) = `UINT16 section_count=1, page_start=1, footnote_start=1, endnote_start=1, picture_start=1, table_start=1, equation_start=1, UINT32 list_id=0, UINT32 para_id=0, UINT32 char_pos=0`. 압축 여부는 속성 bit0을 따른다.

**G. OLE/CFB 컨테이너 (fixture 생성기의 순수 파이썬 writer. v3, 512-byte 섹터)**
- 헤더 512 bytes: `[0:8] D0 CF 11 E0 A1 B1 1A E1` · `[8:24]` 0 · `[24:26]` 0x003E · `[26:28]` 0x0003 · `[28:30]` 0xFFFE · `[30:32]` 0x0009(섹터 512) · `[32:34]` 0x0006(미니섹터 64) · `[34:40]` 0 · `[40:44]` 0(v3 디렉터리 섹터 수) · `[44:48]` FAT 섹터 수 = 1 · `[48:52]` 첫 디렉터리 섹터 = 1 · `[52:56]` 0 · `[56:60]` 0x00001000(미니스트림 컷오프) · `[60:64]` 첫 MiniFAT 섹터 · `[64:68]` MiniFAT 섹터 수 = 1 · `[68:72]` 0xFFFFFFFE · `[72:76]` 0 · `[76:512]` DIFAT 109개: [0]=0, 나머지 0xFFFFFFFF.
- 특수 섹터 값: FREESECT 0xFFFFFFFF · ENDOFCHAIN 0xFFFFFFFE · FATSECT 0xFFFFFFFD · NOSTREAM 0xFFFFFFFF.
- 섹터 배치(헤더 다음부터 0번): 0 = FAT(1섹터, UINT32 128개) · 1..D = 디렉터리 (D = ceil(엔트리수×128/512), 엔트리 5개 → 2섹터) · D+1 = MiniFAT(1섹터) · D+2.. = 미니스트림 본체(512 패딩). 총 섹터 > 128 또는 미니섹터 > 128 이면 ValueError.
- 모든 스트림은 미니스트림(64-byte 미니섹터, 각 스트림 64 패딩)에 둔다. 스트림 하나가 4096 bytes 이상이면 ValueError (fixture 범위 밖).
- 디렉터리 엔트리 128 bytes: `[0:64]` 이름 UTF-16LE + null, 0 패딩 · `[64:66]` 이름 바이트 길이(null 포함; "Root Entry"=22) · `[66]` 타입(0 미사용, 1 storage, 2 stream, 5 root) · `[67]` 색 = 1(black; olefile는 검사하지 않음) · `[68:72]` left · `[72:76]` right · `[76:80]` child · `[80:96]` CLSID 0 · `[96:100]` 0 · `[100:116]` 시간 0 · `[116:120]` 시작 섹터(stream: 미니섹터 번호, root: 미니스트림 첫 일반 섹터, storage: 0) · `[120:124]` 크기(stream: 실제 바이트, root: 미니스트림 총 바이트 = 64의 배수, storage: 0) · `[124:128]` 0.
- 엔트리 번호와 트리 (고정): 0 `Root Entry`(type 5, child=1) · 1 `BodyText`(type 1, left=2, right=3, child=4) · 2 `DocInfo`(type 2) · 3 `FileHeader`(type 2) · 4 `Section0`(type 2). 지정하지 않은 left/right/child = NOSTREAM. 정렬 근거: CFB 형제 정렬은 이름 길이 우선(DocInfo 7 < BodyText 8 < FileHeader 10). 미사용 슬롯(5~7)은 type 0, 전부 0 + 포인터 NOSTREAM.
- FAT: 섹터0 → FATSECT · 디렉터리 체인 1→2→ENDOFCHAIN · MiniFAT → ENDOFCHAIN · 미니스트림 체인 순서대로 → ENDOFCHAIN · 나머지 FREESECT. MiniFAT: 각 스트림의 미니섹터 체인 → ENDOFCHAIN, 나머지 FREESECT.
- 검증 기준은 `olefile.OleFileIO(path)`가 열리고 `listdir()`가 `[["BodyText","Section0"],["DocInfo"],["FileHeader"]]`(정렬 후)를 돌려주는 것.

**H. 합성 생성기 시그니처 (`tests/synth_hwp5.py`)**
```python
FIXTURE_PARAGRAPHS: list[str] = ["테스트 문서 제목", "본문 단락 1", "", "본문 단락 2"]   # E2E·단위 테스트 공용. 비어 있지 않은 단락 3개
EXPECTED_MARKDOWN = "테스트 문서 제목\n\n본문 단락 1\n\n본문 단락 2\n"

def compress_raw(data: bytes) -> bytes                      # §4.4-B
def build_file_header(*, properties: int = 0x1) -> bytes    # 256 bytes, §4.4-A
def build_record(tag_id: int, level: int, payload: bytes) -> bytes   # 헤더(+확장 size) + payload
def build_paragraph(text: str, *, last: bool) -> bytes      # §4.4-D/E 레코드 4개
def build_section0(paragraphs: Sequence[str]) -> bytes      # 미압축. 마지막 단락만 last=True
def build_docinfo() -> bytes                                # 미압축, §4.4-F
def build_cfb(streams: Mapping[str, bytes]) -> bytes        # 키: "FileHeader", "DocInfo", "BodyText/Section0" 정확히 3개. §4.4-G
def build_hwp5(paragraphs: Sequence[str], *, properties: int = 0x1) -> bytes
    # bit0 set → DocInfo/Section0 압축. encrypted 등 다른 비트는 FileHeader 에만 반영(본문은 그대로 씀)
def write_hwp5(path: Path, paragraphs: Sequence[str], *, properties: int = 0x1) -> Path   # 부모 디렉터리 생성 후 바이트 저장, path 반환
```

### 4.5 CLI 인터페이스 (`hwp2md`)
```
usage: hwp2md [-h] [-o OUT_DIR] [--version] INPUT
  INPUT            변환할 .hwp 파일 경로
  -o, --out-dir    출력 디렉터리 (기본값 ".", 없으면 생성)
  --version        "hwp2md 0.1.0" 출력 후 종료 코드 0
```
- 성공 stdout (정확히 2줄, 각 줄 끝 `\n`):
  ```
  ✓ {INPUT 파일명(Path(input).name)} → {str(Path(out_dir) / f"{stem}.md")}
    단락 {paragraph_count}개
  ```
  (2행은 공백 2개로 시작. 경로는 resolve 하지 않고 사용자가 준 out_dir 그대로 join.)
- 종료 코드와 stderr 메시지 (모두 `hwp2md: error: ` 접두, 1줄, traceback 없음):
  | 코드 | 상황 | stderr |
  |---|---|---|
  | 0 | 성공 | (없음) |
  | 2 | 인자 오류(argparse 기본) 또는 INPUT 이 파일이 아님 | `hwp2md: error: file not found: {input}` |
  | 3 | `NotHwpFileError` | `hwp2md: error: not an HWP 5.0 file: {input}` |
  | 3 | `UnsupportedHwpError` | `hwp2md: error: unsupported HWP file (encrypted or distribution): {input}` |
  | 1 | 그 외 `Hwp2mdError` 및 예상 못한 예외 | `hwp2md: error: {str(exc)}` |
- `{input}`은 사용자가 준 문자열 그대로. stdout/stderr 는 UTF-8 (`sys.stdout.reconfigure` 는 쓰지 않는다; 테스트가 `PYTHONIOENCODING=utf-8` 을 넣는다).

### 4.6 E2E 계약 (`tests/e2e/`)
- `conftest.py` fixtures: `hwp2md_bin: str` = `shutil.which("hwp2md")`, None 이면 `pytest.fail("hwp2md console script not on PATH — run `uv sync`")` · `synthetic_hwp(tmp_path) -> Path` = `write_hwp5(tmp_path/"sample.hwp", FIXTURE_PARAGRAPHS)` · `run_cli(args: list[str]) -> subprocess.CompletedProcess[str]` = `subprocess.run([hwp2md_bin, *args], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=60)`.
- 실제 샘플 탐색: `REAL_FIXTURES = sorted(Path(__file__).resolve().parents[1].joinpath("fixtures").glob("*.hwp"))`; `@pytest.mark.parametrize("real_hwp", REAL_FIXTURES, ids=lambda p: p.name)`. 비어 있으면 pytest 기본 동작으로 skipped 1건 (`pytest.skip`/`mark.skip` 문자열을 코드에 쓰지 않는다 — gate 가 테스트 약화로 본다).
- 증거 저장: 성공 케이스는 생성된 `.md` 를 `Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots")) / "sample.md"` 로 복사(디렉터리 생성). runner 가 `ILLY_SHOT_DIR=.ai/tasks/T-20261022-stack-cli-smoke/screenshots` 로 실행.
- 테스트 케이스 (이름 고정):
  1. `test_convert_synthetic_success` — 종료 0, stdout 1행 == `f"✓ sample.hwp → {out_dir / 'sample.md'}"`, 2행 == `"  단락 3개"`, 파일 내용 == `EXPECTED_MARKDOWN`
  2. `test_convert_uncompressed_variant` — `properties=0` fixture, 종료 0, 파일 내용 == `EXPECTED_MARKDOWN`
  3. `test_missing_input_exit_2` — 종료 2, stderr 에 `file not found:` 포함
  4. `test_not_hwp_exit_3` — `fake.hwp`(내용 `b"plain text, not an ole file\n" * 100`), 종료 3, stderr 에 `not an HWP 5.0 file:` 포함, `.md` 미생성
  5. `test_encrypted_flag_exit_3` — `properties=0x3`, 종료 3, stderr 에 `unsupported HWP file` 포함
  6. `test_real_fixture_converts[<name>]` — 종료 0, stdout 2행이 정규식 `^  단락 \d+개$`, `.md` 존재하고 `len(content.strip()) > 0`

### 4.7 CLAUDE.md 명령 블록 최종 값 (Stage 2에서 orchestrator가 그대로 치환)
```
INSTALL_CMD: uv sync
DEV_CMD: (none)
DEV_URL: (none)
DEV_READY: (none)
BUILD_CMD: (none)
LINT_CMD: uv run ruff check src tests && uv run ruff format --check src tests
TYPECHECK_CMD: uv run mypy src
TEST_CMD: uv run pytest tests/unit -q
E2E_CMD: uv run pytest tests/e2e -q
E2E_ONE: uv run pytest {file} -q
E2E_DIR: tests/e2e
```

### 4.8 CLAUDE.md "orchestrator 전용 파일 (추가분)" 최종 값
```
- `src/hwp2md/cli.py` (CLI 진입점. 변경은 그 파일만 갖는 별도 단계로)
- `pyproject.toml` 의 `[project.scripts]` (상위 목록에 이미 포함, 재확인용)
```
`.gitignore` 추가 2줄: `tests/fixtures/*.hwp`, `tests/e2e/screenshots/`.

### 4.9 docs/decisions.md 항목 (Stage 7, 이 내용을 그대로 옮긴다)
```
## 2026-10-22 스택: Python 3.11+, olefile, hatchling+uv, ruff+mypy, pytest
- 결정: HWP 5.0 바이너리는 `olefile`(OLE 컨테이너) + `zlib` + 자체 레코드 파서. HWPX는 `lxml`로 파싱하되 HWPX 태스크 시작 때 의존성을 선언한다. 패키징 hatchling(src 레이아웃), 환경 uv, 린트·포맷 ruff, 타입 mypy strict, 테스트 pytest(단위 `tests/unit`, E2E `tests/e2e`는 실제 콘솔 스크립트 실행).
- 이유: 한컴 없이 순수 파이썬으로 동작(README 방향). olefile는 의존성이 없고 HWP OLE 구조에 충분하다. uv는 lock·venv·스크립트 실행을 한 도구로 처리해 에이전트 명령 블록이 짧아진다.

## 2026-10-22 범위: 첫 스모크는 본문 단락 텍스트만
- 결정: 표·이미지·각주·제목 계층·HWPX는 후속 태스크. 이번 태스크는 PARA_TEXT → Markdown 단락만.
- 이유: 파이프라인(OLE → 압축 해제 → 레코드 → 렌더 → CLI)이 끝까지 한 번 돌아가는 것을 먼저 확인하고, 블록 추상화(표·이미지)는 그 위에 얹는다.

## 2026-10-22 테스트 fixture: 공개 샘플 대신 합성 HWP 5.0 생성기
- 결정: `tests/synth_hwp5.py`가 명세 기준 최소 HWP 5.0 파일(OLE + FileHeader + DocInfo + BodyText/Section0)을 코드로 만든다. 실제 샘플은 `tests/fixtures/*.hwp`에 넣으면 E2E가 자동으로 추가 실행한다(라이선스 확인 전까지 커밋하지 않음).
- 이유: 네트워크·라이선스 확인 없이 결정적(deterministic) 테스트가 가능하고, 압축/비압축·암호화 플래그 같은 변형을 바이트 단위로 통제할 수 있다.
```

### 4.10 README 추가 절 (Stage 7, "## MVP" 절 뒤에 추가)
~~~~
## 설치와 실행 (개발 중)
```bash
uv sync                               # .venv 생성 + 개발 의존성 설치
uv run hwp2md input.hwp -o out/       # out/input.md 생성
uv run pytest tests/unit tests/e2e -q # 테스트
```
현재 지원: HWP 5.0 바이너리의 본문 단락 텍스트. 표·이미지·각주·HWPX는 진행 중.
~~~~

## 5. 단계 (Stage) — 전부 순차. 병렬 없음.

### Stage 1 — 패키지 메타데이터 pyproject.toml
- 목적: §4.2 그대로 `pyproject.toml`을 만들어 콘솔 스크립트·의존성·도구 설정을 고정한다.
- 담당: implementer(opus). orchestrator 전용 파일이므로 이 파일만 갖는 전용 단계.
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §4.2, `README.md`(readme 참조 확인만)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `pyproject.toml`
- 산출물: `pyproject.toml`
- 검증 (implementer): `python3.13 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['scripts']['hwp2md'], d['project']['requires-python'], d['tool']['pytest']['ini_options']['pythonpath'])"` → `hwp2md.cli:main >=3.11 ['tests']` · `uv lock --dry-run` → 종료 코드 0 (`Resolved N packages` 출력. 네트워크 필요)
- 완료 조건: 검증 통과 + orchestrator가 `uv lock` 실행해 `uv.lock` 생성 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s1] build: pyproject.toml (hatchling, olefile, dev tools)` (uv.lock 포함)
- 실패 시: 네트워크 오류면 1회 재시도 후 BLOCKED. 그 외 `git restore pyproject.toml`(orchestrator) 후 RETRY. 도구 호출 상한 40.

### Stage 2 — CLAUDE.md 명령 블록·전용 파일 추가분·.gitignore (orchestrator 직접)
- 목적: 에이전트가 실행할 명령 블록을 §4.7 값으로, 전용 파일 추가분을 §4.8로 채운다.
- 담당: orchestrator (Edit 직접. 서브에이전트 호출 없음)
- 병렬 가능: 아니오 · 선행: Stage 1
- 입력: §4.7, §4.8
- 쓰기 범위:
  - `CLAUDE.md` (명령 블록 11줄 치환 + 추가분 2줄)
  - `.gitignore` (`tests/fixtures/*.hwp`, `tests/e2e/screenshots/` 2줄 추가)
- 산출물: 채워진 명령 블록
- 검증: `grep -c "채워 넣을 것" CLAUDE.md` → `0` · `grep -E "^(INSTALL_CMD|LINT_CMD|TYPECHECK_CMD|TEST_CMD|E2E_CMD|E2E_ONE):" CLAUDE.md | wc -l` → `6` · `grep -c "tests/fixtures/\*.hwp" .gitignore` → `1`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures`
- 실패 시: Edit 재시도 (최대 3회). 상한 10회.

### Stage 3 — hwp5 레코드 파서·에러 타입·패키지 뼈대
- 목적: 레코드 헤더 파싱과 PARA_TEXT 제어문자 디코드를 §4.3/§4.4-C 대로 구현하고 단위 테스트로 고정한다. `uv sync`가 처음 성공하는 단계.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 2
- 입력: §4.3(errors, records, `__init__` 의 `__version__`), §4.4-C/E, `pyproject.toml`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/__init__.py` (이 단계에서는 `__version__ = "0.1.0"` 만)
  - `src/hwp2md/py.typed` (빈 파일)
  - `src/hwp2md/errors.py`
  - `src/hwp2md/hwp5/__init__.py` (빈 파일 또는 docstring 1줄)
  - `src/hwp2md/hwp5/records.py`
  - `tests/unit/test_hwp5_records.py`
- 산출물: `iter_records`, `decode_para_text`, 예외 3종, 단위 테스트 ≥6 케이스: (a) 일반 헤더 `0x00400443` → tag 0x43/level 1/size 4 (b) size 0xFFF 확장 헤더 (c) 잘린 payload → `Hwp2mdError` 메시지 `truncated record at offset` (d) 확장 컨트롤 코드 2 뒤 8 WCHAR 건너뛰기 (e) 탭(9)→공백, 하이픈(24)→`-`, 30/31→공백, 10→`\n` (f) 13 이후 바이트 무시 (g) 서로게이트 쌍(예: U+1F600) 보존 (h) 홀수 길이 payload
- 검증: `uv sync` → 종료 0 · `uv run pytest tests/unit -q` → `failed` 0, passed ≥6 · `uv run ruff check src tests && uv run ruff format --check src tests` → 종료 0 · `uv run mypy src` → `Success: no issues found`
- 완료 조건: 검증 통과 + orchestrator가 `src/.gitkeep` 삭제 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder`
- 실패 시: 같은 테스트 2회 연속 실패 → BLOCKED. 상한 40회.

### Stage 4 — 합성 HWP 5.0 생성기 (순수 파이썬 CFB writer)
- 목적: §4.4-A/B/D/E/F/G/H 대로 올바른 HWP 5.0 파일 바이트를 생성하고 `olefile`로 열려 Stage 3 파서로 단락이 복원되는지 단위 테스트로 고정한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 3
- 입력: §4.4 전체, §4.3(records 사용), `src/hwp2md/hwp5/records.py`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/synth_hwp5.py`
  - `tests/unit/test_synth_hwp5.py`
- 산출물: §4.4-H 함수 전부 + `FIXTURE_PARAGRAPHS`, `EXPECTED_MARKDOWN`. 단위 테스트 ≥6: (a) `build_file_header()` 길이 256, `[:32] == HWP5_SIGNATURE`, `[36:40] == 01 00 00 00` (b) `write_hwp5` 결과를 `olefile.isOleFile` True, `OleFileIO.listdir()` 정렬 결과 == `[["BodyText","Section0"],["DocInfo"],["FileHeader"]]` (c) `FileHeader` 스트림 길이 256 (d) Section0 을 `zlib.decompressobj(-15)` 로 해제 후 `iter_records` → PARA_TEXT 레코드 4개, `decode_para_text` 결과 == `FIXTURE_PARAGRAPHS` 각 `.strip()` (e) 마지막 PARA_HEADER nchars bit31 set, 나머지 unset (f) `properties=0` 이면 Section0 이 미압축으로 바로 `iter_records` 가능 (g) 4096 bytes 이상 스트림 → `ValueError`
- 검증: `uv run pytest tests/unit -q` → `failed` 0, passed ≥12 · `uv run ruff check src tests && uv run ruff format --check src tests` → 종료 0 (mypy는 src만 대상이므로 변화 없음, 그래도 `uv run mypy src` 종료 0 확인)
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)`
- 실패 시: `olefile`이 파일을 거부하는 오류를 2회 수정해도 못 고치면 BLOCKED(§3). 상한 40회.

### Stage 5 — hwp5 리더·Markdown 렌더·convert API
- 목적: 파일 경로 → 단락 목록 → Markdown 파일까지 라이브러리 API(`convert`)로 연결한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 4
- 입력: §4.3(reader, render, convert, `__init__` 최종), §4.4-A/B, `tests/synth_hwp5.py`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/hwp5/reader.py`
  - `src/hwp2md/render.py`
  - `src/hwp2md/convert.py`
  - `src/hwp2md/__init__.py` (§4.3 최종 상태로 갱신)
  - `tests/unit/test_convert.py`
- 산출물: `parse_file_header`, `read_sections`, `read_paragraphs`, `render_markdown`, `convert`, `ConvertResult`. 단위 테스트 ≥6: (a) `convert(synthetic, tmp/out)` → `paragraph_count == 3`, 파일 내용 == `EXPECTED_MARKDOWN`, `output == tmp/out/sample.md` (b) `properties=0` 비압축 동일 결과 (c) `properties=0x3` → `UnsupportedHwpError` (d) `properties=0x5` → `UnsupportedHwpError` (e) 텍스트 파일 → `NotHwpFileError` (f) 없는 경로 → `FileNotFoundError` (g) `parse_file_header(b"x"*256)` → `NotHwpFileError`, `len != 256` → `NotHwpFileError` (h) `render_markdown([])` == `""`, `render_markdown(["a","","b"])` == `"a\n\nb\n"`
- 검증: `uv run pytest tests/unit -q` → `failed` 0, passed ≥18 · `uv run ruff check src tests && uv run ruff format --check src tests` → 종료 0 · `uv run mypy src` → `Success: no issues found` · `uv run python -c "import hwp2md; print(hwp2md.__version__, hwp2md.convert.__name__)"` → `0.1.0 convert`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API`
- 실패 시: 같은 오류 2회 → BLOCKED. 상한 40회.

### Stage 6 — CLI 진입점 cli.py
- 목적: §4.5 인터페이스로 `hwp2md` 콘솔 스크립트를 완성한다. 전용 파일(§4.8)이라 이 파일만 갖는 단계.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 5
- 입력: §4.3(cli), §4.5, `src/hwp2md/convert.py`, `src/hwp2md/errors.py`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/cli.py`
- 산출물: `main(argv) -> int`
- 검증 (전부 implementer가 직접 실행, 기대값 글자 단위 대조): `uv run hwp2md --version` → `hwp2md 0.1.0`, 종료 0 · §2 S2 명령 → stdout 2줄·`exit=0`·파일 내용 일치 · §2 S3 → `exit=2` + 메시지 · §2 S4 → `exit=3` + 메시지 · `D=$(mktemp -d) && PYTHONPATH=tests uv run python -c "from pathlib import Path; from synth_hwp5 import write_hwp5; write_hwp5(Path('$D/enc.hwp'), ['x'], properties=0x3)" && uv run hwp2md $D/enc.hwp -o $D; echo "exit=$?"` → stderr `hwp2md: error: unsupported HWP file (encrypted or distribution): <D>/enc.hwp`, `exit=3` · `uv run hwp2md; echo "exit=$?"` → `exit=2` · `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` → 종료 0
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s6] feat(cli): hwp2md INPUT -o OUT_DIR`
- 실패 시: 같은 오류 2회 → BLOCKED. 상한 30회.

### Stage 7 — 결정 기록·README 실행 방법
- 목적: §4.9를 `docs/decisions.md`에, §4.10을 `README.md`에 그대로 옮긴다.
- 담당: scribe(haiku)
- 병렬 가능: 아니오 · 선행: Stage 6
- 입력: §4.9, §4.10, `docs/decisions.md`(현재 제목 1줄만), `README.md`
- 쓰기 범위 (이 파일들만 수정):
  - `docs/decisions.md` (기존 `# 결정 기록` 제목 유지, 아래에 §4.9 3개 항목 추가)
  - `README.md` (`## MVP` 절 뒤에 §4.10 절 추가. 다른 절은 글자 하나도 바꾸지 않는다)
- 산출물: 결정 3건, README 실행 절
- 검증: `grep -c "^## 2026-10-22" docs/decisions.md` → `3` · `grep -c "uv run hwp2md" README.md` → `1` 이상 · `grep -c "하지 않는 것" README.md` → `1` (기존 절 보존) · `/Users/illi/illy-projects/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → `sanitize-check: OK`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s7] docs: stack/scope/fixture decisions, README install section`
- 실패 시: 재시도 최대 3회. 상한 15회.

### Stage 8 — E2E 테스트 작성·실행 (필수, 생략 불가)
- 목적: 실제 `hwp2md` 콘솔 스크립트를 subprocess로 실행하는 E2E 6케이스(§4.6)를 작성하고 runner가 실행·로그·증거를 남긴다.
- 담당: test-writer(sonnet) → runner(haiku)
- 병렬 가능: 아니오 · 선행: Stage 7
- 입력: §4.5, §4.6, `tests/synth_hwp5.py`(import 만), `/Users/illi/illy-projects/docs/policies/e2e-standard.md`
- 쓰기 범위 (test-writer; 이 파일들만 생성):
  - `tests/e2e/conftest.py`
  - `tests/e2e/test_cli_convert.py`
  - `tests/fixtures/.gitkeep`
- 산출물: §4.6 케이스 6개 (실제 샘플 없으면 6번은 빈 parametrize → skipped 1)
- 검증 (test-writer): `uv run pytest tests/e2e -q` → `failed` 0, `error` 0, passed 5, skipped 1(샘플 없을 때) · `uv run ruff check tests && uv run ruff format --check tests` → 종료 0 · `grep -cE "pytest\.skip\(|pytest\.mark\.skip" tests/e2e/*.py` → `0`
- 실행 (runner, Bash 1회, timeout 600000):
  ```bash
  cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-stack-cli-smoke; mkdir -p $T/logs $T/screenshots
  [ -f $T/logs/e2e.log ] && mv $T/logs/e2e.log $T/logs/e2e.prev.log
  ILLY_SHOT_DIR=$T/screenshots timeout 600 uv run pytest tests/e2e -q > $T/logs/e2e.log 2>&1; echo "exit=$?" >> $T/logs/e2e.log
  tail -3 $T/logs/e2e.log; grep -E "passed|failed|error" $T/logs/e2e.log | tail -3; ls -la $T/screenshots; cat $T/screenshots/sample.md
  ```
  기대: `exit=0`, `5 passed, 1 skipped` (샘플 있으면 skipped 0 + 추가 passed), `$T/screenshots/sample.md` 내용이 `EXPECTED_MARKDOWN` 과 같음
- 완료 조건: e2e.log 마지막 줄 `exit=0` + `sample.md` 증거 존재 + PROGRESS 기록 + 커밋 `[T-20261022-stack-cli-smoke][s8] test(e2e): CLI convert success and failure paths`
- 실패 시: 로그 증상으로 분류(e2e-standard 표) — 테스트 파일 오류면 test-writer 재호출(2회 실패 → opus), 구현 오류면 implementer 를 해당 Stage 쓰기 범위로 재호출. 같은 실패 2회 → BLOCKED. test-writer 상한 40회, runner 상한 15회.

### Stage 9 — 리뷰·결과 기록
- 목적: diff 와 CLI 출력 증거를 보고 §2 성공 기준 10개를 표로 판정하고 RESULT.md 를 쓴다.
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: Stage 8
- 입력(reviewer): `git diff 308f1fb...HEAD --stat`, `git diff 308f1fb...HEAD -- src tests pyproject.toml`, `.ai/tasks/T-20261022-stack-cli-smoke/logs/e2e.log`, `.ai/tasks/T-20261022-stack-cli-smoke/screenshots/sample.md`(Read 로 직접 열어 `EXPECTED_MARKDOWN` 과 대조), §1 OUT 목록(HWPX·표·이미지·각주 코드가 없는지 grep: `grep -rniE "lxml|hwpx|HWPTAG_TABLE\b.*=.*\(|footnote" src/` → `records.py` 의 상수 정의 1줄 외 매치 없음)
- 쓰기 범위 (scribe): `.ai/tasks/T-20261022-stack-cli-smoke/RESULT.md`
- 산출물: `RESULT.md` (성공 기준 S1~S10 표: 각 행에 실제 실행 결과 값, reviewer 지적 사항, §7 결정 적용 여부)
- 검증: `test -s .ai/tasks/T-20261022-stack-cli-smoke/RESULT.md && grep -c "^| S" .ai/tasks/T-20261022-stack-cli-smoke/RESULT.md` → `10` 이상 · `/Users/illi/illy-projects/scripts/gate.sh -C /Users/illi/illy-projects/hwp2md` → `GATE PASS`
- 완료 조건: `GATE PASS` + 커밋 `[T-20261022-stack-cli-smoke][s9] docs: RESULT` + orchestrator가 STATE.md 갱신(scribe 재작성)
- 실패 시: reviewer 가 FAIL 판정한 기준이 있으면 해당 Stage 담당을 그 Stage 쓰기 범위로 재호출(최대 2회), 이후 BLOCKED. reviewer 상한 25회, scribe 상한 15회.

## 6. 병렬 실행 맵
```
Stage 1(pyproject) → Stage 2(CLAUDE.md, orchestrator) → Stage 3(records) → Stage 4(synth fixture)
  → Stage 5(reader/render/convert) → Stage 6(cli) → Stage 7(docs) → Stage 8(E2E) → Stage 9(리뷰·RESULT)
```
병렬 묶음 없음. 상위 규칙(코드 없는 프로젝트의 S1 성격) 대로 전 단계 순차. worktree 격리 불필요.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [x] 1. 패키지·환경 관리 도구: **기본값 uv** (`uv sync` / `uv run`). 대안 pip+venv 면 명령 블록을 `python -m venv .venv && .venv/bin/pip install -e . pytest ruff mypy` 계열로 바꾼다 (플랜 §4.7 수정 → 재승인).
- [x] 2. 린트·타입체커: **기본값 ruff(check+format) + mypy strict**. 대안 pyright 면 `TYPECHECK_CMD: uv run pyright src`, dev 그룹에 `pyright` 추가.
- [x] 3. 샘플 HWP 확보: **기본값 합성 fixture 생성기(tests/synth_hwp5.py)만으로 진행**. 공공기관 실제 샘플 `.hwp` 를 `tests/fixtures/` 에 넣어주면 E2E `test_real_fixture_converts` 가 자동 실행된다. 실제 샘플은 라이선스 확인 전까지 커밋하지 않는다(`.gitignore`). 넣어 줄 파일이 있으면 승인 시 경로를 알려 달라.
- [x] 4. Python 최소 버전: **기본값 3.11** (`requires-python >=3.11`; 이 머신에 3.11·3.13 있음). 3.10 지원이 필요하면 `tomllib`·`X | Y` 문법 영향 없음, `target-version` 만 py310 으로.
- [x] 5. `lxml` 의존성 선언 시점: **기본값 HWPX 태스크 때 추가** (이번엔 미선언, 결정 기록에만 명시). 지금 선언하려면 Stage 1 `dependencies` 에 `"lxml>=5"` 추가.
- [x] 6. 라이선스: **기본값 이번 태스크에서는 `pyproject.toml` 에 license 미기재, LICENSE 파일 없음**. MIT 등 결정되면 다음 태스크에서 추가.
- 결정 (2026-10-22, 사용자): 위 6개 모두 기본값으로 진행. 승인됨.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| `uv lock`/`uv sync` 네트워크 차단 (PyPI 접근 불가) | 중 | 1회 재시도 후 BLOCKED. 사용자 네트워크·프록시 확인 |
| 합성 CFB 파일을 `olefile`이 거부 (디렉터리/FAT 체인 오류) | 중 | Stage 4 단위 테스트가 즉시 잡는다. §4.4-G 상수 대조. 2회 실패 → BLOCKED + §7-3 대안(실제 샘플) |
| HWP 5.0 명세 세부(PARA_HEADER 22 vs 24 bytes, nchars bit31)가 실제 한컴 파일과 다름 | 저 | 파서는 PARA_HEADER를 읽지 않고 PARA_TEXT 만 디코드하므로 영향 없음. 실제 샘플이 들어오면 `test_real_fixture_converts` 가 검증 |
| 실제 한컴 파일의 표 셀·머리말 단락이 본문 단락으로 섞여 나옴 | 중 (실제 샘플 있을 때만) | 이번 범위 허용(§4.3 read_paragraphs). RESULT 비고에 기록, 표 태스크에서 level/CTRL_HEADER 처리 |
| mypy strict + untyped `olefile` → `Any` 반환 경고 | 중 | §4.2 메모대로 `bytes(...)`/`cast` 로 좁힘 |
| stdout 의 `✓`/`→` 가 비 UTF-8 콘솔에서 깨짐 | 저 | 테스트는 `PYTHONIOENCODING=utf-8`. Windows 지원은 범위 밖 |
| 익명화 패턴 중 IPv4 정규식이 4마디 버전 문자열(예: 점 4개 버전)과 매치 | 저 | 플랜·코드·문서에 버전은 hex(`0x05000300`) 또는 튜플 `(5, 0, 3, 0)` 로만 적는다 |
| gate 가 `pytest.skip`/`mark.skip` 문자열을 테스트 약화로 판정 | 저 | §4.6: 빈 parametrize 로 skipped 처리. 문자열 자체를 쓰지 않음 |

## 9. 예상 비용
- 예상 단계 수: 9 (서브에이전트 호출 단계 8 + orchestrator 직접 1) · 서브에이전트 호출: 10회 (implementer 5, scribe 2, test-writer 1, runner 1, reviewer 1) · 주 모델: opus 50% / sonnet 20% / haiku 30%

## 변경 이력
- 2026-10-22 12:59 (orchestrator): Stage 7 담당을 scribe(haiku) → implementer(opus)로 변경. 사유: scribe 에이전트 정의가 `.ai/` 밖 파일 수정을 금지해 docs/decisions.md·README.md를 쓸 수 없음. 쓰기 범위·내용(§4.9/§4.10)·검증은 변경 없음(범위 확대 아님).
