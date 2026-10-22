# PLAN — T-20261022-heading-levels hwp2md 제목 계층(heading) 지원

> 작성: planner fable · 2026-10-22 18:50 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> BASE: `ce0a3f5654351f1d89e11075f8c05fed4a5be775` (main 동일) · 브랜치 `ai/T-20261022-heading-levels` · 현재 단위 113 · E2E 21 통과(합계 134)

## 0. 한 줄 목표
사용자는 `hwp2md input.hwp|input.hwpx -o out/` 한 줄로, 문서의 개요(outline) 수준이 적용된 단락이 Markdown 제목(`#`~`######`)으로 바뀐 `.md`를 얻고, CLI 2행에서 `제목 K개`를 볼 수 있다. HWP 5.0과 HWPX는 같은 입력 내용에서 바이트 단위로 같은 Markdown을 낸다.

## 1. 범위
### 포함 (IN)
- 블록 모델: `src/hwp2md/blocks.py` `Paragraph`에 `level: int = 0` 필드 추가(0 본문, 1~6 제목). 기존 `Paragraph("text")` 호출·동등 비교 호환(§4.2).
- 렌더러: `src/hwp2md/render.py` — `level ≥ 1`인 Paragraph를 `#`×level + 공백 + 텍스트로 렌더(§4.2-C).
- 변환 결과: `src/hwp2md/convert.py` `ConvertResult.heading_count` 추가, `paragraph_count`는 본문(level 0)만(§4.2-D).
- HWP 5.0: `DocInfo` 스트림에서 `HWPTAG_PARA_SHAPE`(0x19) 레코드만 해석하는 `src/hwp2md/hwp5/docinfo.py` 신규. `PARA_HEADER`의 `para_shape_id`(UINT16 @12)로 문단 모양을 찾아 개요 비트로 수준 판정(§4.3). `hwp5/body.py`·`hwp5/reader.py` 연결(§4.4). `records.py`에 태그 상수 2줄.
- HWPX: `Contents/header.xml`의 `hh:paraPr/hh:heading[@type="OUTLINE"]/@level`을 읽는 `src/hwp2md/hwpx/header.py` 신규. `hp:p/@paraPrIDRef`로 연결(§4.6). `hwpx/body.py`·`hwpx/reader.py` 연결(§4.7).
- 합성 생성기 확장: `tests/synth_hwp5.py`(`SynthHeading`, DocInfo PARA_SHAPE·STYLE 레코드, PARA_HEADER id 지정), `tests/synth_hwpx.py`(header.xml paraPr/heading/styles, `hp:p` paraPrIDRef 지정). **제목이 없는 기존 입력에서는 바이트 불변**(§4.5·§4.8의 sha256으로 검증).
- CLI 2행: 제목이 1개 이상일 때만 ` · 제목 K개` 추가(§4.12, orchestrator 전용 단계).
- 문서: `docs/decisions.md` 3건, `README.md` "현재 지원" 1줄, `tests/fixtures/README.md` 기대값 안내(§4.14·§4.15).
- 단위 테스트 신규 3파일 + 기존 3파일에 케이스 추가, E2E 신규 `tests/e2e/test_cli_heading.py` + 기존 E2E 정규식 2줄(§4.13).

### 제외 (OUT) — 절대 건드리지 않는다
- 문단 머리 모양 **번호(2)·글머리표(3)** 의 리스트 렌더(`-`, `1.`). 이번에는 본문 단락으로 둔다.
- DocInfo의 다른 레코드(글꼴·문자 모양·탭·번호 정의·ID_MAPPINGS 등) 해석. STYLE(0x1A)은 생성기가 쓰되 파서는 읽지 않는다(§7-2).
- HWPX `hh:style` 이름/`styleIDRef` 기반 판정, `hh:numbering`·`hh:bullet` 해석.
- 제목 번호 자동 부여("1.", "가." 생성), 목차 생성, `--split`/`--meta`, 이미지·각주, 1행 표 처리 개선, 본문 첫 글자 `#` 이스케이프.
- `docs/vision.md` 수정, 의존성 추가·제거, `uv.lock` 변경.
- 기존 단위 113·E2E 21 테스트의 수정 — 단 §4.13-A의 **정규식 2줄**만 예외(기존 케이스 이름·수·단언 의미 불변).

### 건드리면 안 되는 파일/디렉토리
- `src/hwp2md/cli.py` (orchestrator 전용. Stage 7만), `pyproject.toml`, `uv.lock`, `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.gitignore`, `.claude/**`
- `docs/vision.md`, `tests/fixtures/*.hwp`, `tests/fixtures/hwpx/*.hwpx`, `tests/fixtures/unsupported/**`
- `src/hwp2md/detect.py`, `src/hwp2md/errors.py`, `src/hwp2md/__init__.py`, `tests/e2e/conftest.py`, `tests/e2e/test_cli_table.py`
- `tests/unit/test_hwp5_body.py`, `tests/unit/test_hwp5_records.py`, `tests/unit/test_hwpx_body.py`, `tests/unit/test_hwpx_reader.py`, `tests/unit/test_detect.py` (기존 그대로 통과해야 한다)

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| S1 | 합성 제목 fixture가 두 포맷에서 같은 Markdown | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e/test_cli_heading.py -q` | `12 passed`(합성 7 + 실제 샘플 5), failed 0 |
| S2 | E2E 전체 통과 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e -q` | `33 passed`(기존 21 + 신규 12), failed 0, skipped 0 |
| S3 | 기존 테스트 회귀 없음 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit -q` | `143 passed` 이상(기존 113 + 신규 30 이상), failed 0 |
| S4 | 린트·포맷·타입 | `cd /Users/illi/illy-projects/hwp2md && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | `All checks passed!`, `already formatted`, `Success: no issues found in 16 source files` |
| S5 | 실제 HWP 5.0 샘플 제목 판정 | `cd /Users/illi/illy-projects/hwp2md && uv run hwp2md tests/fixtures/form200005063113.hwp -o /tmp/h2m && grep -cE '^#{1,6} ' /tmp/h2m/form200005063113.md` | stdout 2행 `  단락 100개 · 표 8개 · 제목 18개`, grep → `18` |
| S6 | 실제 샘플 4개 출력 불변(회귀) | §4.16-C 블록 | 2행이 `  단락 47개 · 표 0개`, `  단락 1개 · 표 1개`, `  단락 80개 · 표 31개`, `  단락 32개 · 표 8개`(`제목` 없음), `exit=0` 5회 |
| S7 | 제목 없는 기존 입력의 합성 바이트 불변 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit/test_synth_hwp5.py tests/unit/test_synth_hwpx.py -q -k "unchanged or sha or deterministic"` | failed 0 (§4.5-F·§4.8-E의 sha256 일치) |
| S8 | 기존 E2E 파일 수정 범위 | `cd /Users/illi/illy-projects/hwp2md && git diff ce0a3f5654351f1d89e11075f8c05fed4a5be775 --stat -- tests/e2e/test_cli_convert.py tests/e2e/test_cli_hwpx.py` | 두 파일 각 `1 +, 1 -` (정규식 1줄씩) |
| S9 | 익명화 | `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` | `sanitize-check: OK` |
| S10 | 증거 파일 | `ls .ai/tasks/T-20261022-heading-levels/screenshots` | `heading_hwp5.md`, `heading_hwpx.md`, `heading_edge.md`, `heading_cell.md`, 실제 샘플 `.md` 5개 포함. reviewer가 `heading_hwp5.md`를 Read로 열어 `# 문서 제목`·`## 1. 사업 개요`·`### 가. 세부 내용` 3줄과 표 1개를 눈으로 확인 |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 오류로 수정 2회 실패
- 동일 단계 재시도 3회 초과
- 단계 하나 도구 호출 상한 초과: implementer 40회, test-writer 30회, reviewer 15회, runner 10회, scribe 10회 (초과 시 PARTIAL 보고 후 orchestrator 반환)
- 단계 하나 30분 초과
- §4 계약(필드명·시그니처·바이트 레이아웃·XML 요소명·기대 숫자)을 바꿔야만 진행 가능 → BLOCKED(planner 재호출)
- OUT 범위 파일(§1) 수정 없이는 진행 불가
- 기존 단위·E2E 테스트가 §4.13-A 정규식 2줄 외의 수정 없이는 통과하지 않음
- 실제 샘플 기대값(§4.11)과 구현 결과가 다르고 원인이 샘플 조사 오류로 판명 → BLOCKED(기대값은 계약이므로 planner가 재조사)

## 4. 인터페이스 계약 (모든 단계가 이 값을 그대로 쓴다. 바꾸면 BLOCKED)

### 4.1 파일 레이아웃 (새 파일 경로는 이것만 허용)
```
src/hwp2md/blocks.py                    # Stage 1 (level 필드)
src/hwp2md/render.py                    # Stage 1
src/hwp2md/convert.py                   # Stage 1 (heading_count)
tests/unit/test_render_heading.py       # Stage 1 신규
tests/synth_hwp5.py                     # Stage 2
tests/unit/test_synth_hwp5.py           # Stage 2 (케이스 추가, 기존 케이스 불변)
src/hwp2md/hwp5/records.py              # Stage 3 (상수 2줄 추가만)
src/hwp2md/hwp5/docinfo.py              # Stage 3 신규
src/hwp2md/hwp5/body.py                 # Stage 3
src/hwp2md/hwp5/reader.py               # Stage 3
tests/unit/test_hwp5_docinfo.py         # Stage 3 신규
tests/synth_hwpx.py                     # Stage 4
tests/unit/test_synth_hwpx.py           # Stage 4 (케이스 추가, 기존 케이스 불변)
src/hwp2md/hwpx/header.py               # Stage 5 신규
src/hwp2md/hwpx/reader.py               # Stage 5
src/hwp2md/hwpx/body.py                 # Stage 5
tests/unit/test_hwpx_header.py          # Stage 5 신규
tests/unit/test_cross_format.py         # Stage 5 (케이스 추가, 기존 케이스 불변)
docs/decisions.md, README.md, tests/fixtures/README.md   # Stage 6
src/hwp2md/cli.py                       # Stage 7 (orchestrator 전용 파일, 전용 단계)
tests/e2e/test_cli_heading.py           # Stage 8 신규
tests/e2e/test_cli_convert.py           # Stage 8 (79행 정규식 1곳만)
tests/e2e/test_cli_hwpx.py              # Stage 8 (32행 정규식 1곳만)
.ai/tasks/T-20261022-heading-levels/RESULT.md, .ai/STATE.md   # Stage 9 (scribe)
```
`tests/` 아래에 `__init__.py`를 만들지 않는다. `src/hwp2md/__init__.py`는 수정하지 않는다(새 export 없음).

### 4.2 블록 모델·렌더·변환 결과 (Stage 1) — §7-1 기본값 (a) 필드 추가
**A. `blocks.py`**
```python
@dataclass(frozen=True)
class Paragraph:
    text: str
    level: int = 0   # 0 = 본문, 1~6 = Markdown 제목 수준 (리더가 clamp 해서 넣는다)
```
- `Paragraph("a") == Paragraph("a", 0)` 이고 `Paragraph("a", 1) != Paragraph("a")`. `Table`·`Block` 불변.

**B. 제목 수준 공식 (두 리더 공통)**: 원본 개요 수준 `raw`(0 기준, HWP 5.0 비트 25~27 값 / HWPX `level` 속성 값) → `level = min(raw + 1, 6)`. 즉 개요 1~6 → `#`~`######`, 개요 7 이상 → `######`(§7-3 기본값 clamp). 머리 모양이 개요(OUTLINE)가 아니면 `level = 0`.

**C. `render.py`**
```python
def _render_paragraph(p: Paragraph) -> str:
    """level <= 0 → p.text 그대로(현재 동작).
    level >= 1 → text = p.text.replace("\n", " ").strip(); text 가 "" 이면 "" (블록 생략);
                 아니면 "#" * min(p.level, 6) + " " + text."""
```
- `render_blocks`는 `Paragraph`면 `_render_paragraph`, `Table`이면 `_render_table`을 쓰고, 나머지(빈 문자열 생략, `"\n\n"` join, 끝 `"\n"`)는 불변. 제목 앞뒤 빈 줄 1개는 이 join으로 자동 충족.
- `render_markdown` 호환 래퍼 불변.

**D. `convert.py`**
```python
@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int   # Paragraph 이고 text 비어 있지 않고 level == 0
    table_count: int       # 불변
    heading_count: int     # Paragraph 이고 text 비어 있지 않고 level >= 1
    markdown: str
```
- 필드 순서는 위와 같다(위치 인자 생성은 코드에 없음). `read_blocks` 디스패처 불변.

### 4.3 HWP 5.0 DocInfo — 바이트 레이아웃과 파서 (Stage 3, 생성기는 Stage 2가 같은 값을 쓴다)
**A. 레코드 태그 (`records.py`에 2줄 추가. 기존 줄 불변)**
```python
HWPTAG_PARA_SHAPE = 0x19  # 25. DocInfo 문단 모양 (ID = 등장 순서)
HWPTAG_STYLE = 0x1A  # 26. DocInfo 스타일 (파서는 읽지 않음, fixture가 씀)
```
**B. DocInfo 스트림**: `BodyText/SectionN`과 같은 레코드 포맷·같은 압축 규칙(FileHeader 속성 bit0). 실제 샘플 2개 모두 레코드 level은 DOCUMENT_PROPERTIES·ID_MAPPINGS가 0, 나머지 1 — 파서는 DocInfo의 level을 보지 않는다. PARA_SHAPE 레코드는 등장 순서가 곧 `para_shape_id`(0부터).

**C. PARA_SHAPE payload** — 파서는 **offset 0의 UINT32 속성1만** 읽는다. 길이는 버전에 따라 42(샘플 `0x05000006`)·46(샘플 `0x05000202`)·54(생성기 `0x05000300`) 바이트.
| 비트 | 뜻 | 파서 사용 |
|---|---|---|
| 23~24 | 문단 머리 모양 종류: 0 없음, 1 개요, 2 번호, 3 글머리표 | `heading_type = (attr1 >> 23) & 0x3` |
| 25~27 | 문단 수준 0~6 (= 개요 1~7) | `heading_level = (attr1 >> 25) & 0x7` |
실제 샘플 확인값: 개요 1~7 문단 모양의 attr1 = `0x00802980`, `0x02800180`, `0x04800180`, `0x06800180`, `0x08800180`, `0x0A800180`, `0x0C800180`(샘플 1) — head 비트 1, level 비트 0~6. `len(payload) < 4` → `Hwp2mdError("truncated PARA_SHAPE record")`.

**D. 생성기용 PARA_SHAPE payload 54 bytes (버전 0x05000300)**: `UINT32 attr1` + `INT32 ×6 = 0`(왼쪽·오른쪽 여백, 들여쓰기, 문단 간격 위·아래, 줄 간격(구)) + `UINT16 ×3 = 0`(탭 정의 ID, 번호/글머리 ID, 테두리/배경 ID) + `INT16 ×4 = 0`(테두리 간격) + `UINT32 attr2 = 0` + `UINT32 attr3 = 0` + `UINT32 줄 간격 = 0`. `attr1`: 본문 `0`, 개요 L(1~7) → `(1 << 23) | ((L - 1) << 25)`.

**E. 생성기용 STYLE payload (파서는 읽지 않는다. 실제 샘플 길이 32/40 과 일치하는 레이아웃)**: `UINT16 n1` + 한글 이름 UTF-16LE(n1 WCHAR) + `UINT16 n2` + 영문 이름 UTF-16LE(n2 WCHAR) + `UINT8 속성 = 0` + `UINT8 다음 스타일 ID = 자기 ID` + `INT16 언어 ID = 1042` + `UINT16 para_shape_id` + `UINT16 char_shape_id = 0` + `UINT16 0`. 이름: ID 0 `"바탕글"`/`"Normal"`(32 bytes), ID L(1~7) `f"개요 {L}"`/`f"Outline {L}"`(40 bytes), para_shape_id = L.

**F. PARA_HEADER payload (22 bytes, 전 태스크 §4.4-D)**: 파서는 `para_shape_id = UINT16 @12`, `style_id = UINT8 @14` 를 읽되 **판정에는 `para_shape_id`만** 쓴다(§7-2 기본값). `len(payload) < 14` → 수준 0(예외 아님).

**G. `src/hwp2md/hwp5/docinfo.py` 공개 API**
```python
"""DocInfo stream: paragraph shapes (outline level) only."""
from __future__ import annotations
import struct
from dataclasses import dataclass
from ..errors import Hwp2mdError
from .records import HWPTAG_PARA_SHAPE, iter_records

HEADING_OUTLINE = 1          # 속성1 비트 23~24 값
MAX_HEADING_LEVEL = 6        # Markdown 상한

@dataclass(frozen=True)
class ParaShape:
    heading_type: int        # 0~3
    heading_level: int       # 0~7 (비트 값 그대로)

@dataclass(frozen=True)
class DocInfo:
    para_shapes: tuple[ParaShape, ...]
    def heading_level(self, para_shape_id: int) -> int:
        """0 <= id < len(para_shapes) 이고 heading_type == HEADING_OUTLINE 이면 min(heading_level + 1, MAX_HEADING_LEVEL), 아니면 0."""

EMPTY_DOCINFO = DocInfo(para_shapes=())

def parse_para_shape(payload: bytes) -> ParaShape:
    """len < 4 → Hwp2mdError("truncated PARA_SHAPE record"). attr1 = struct.unpack_from("<I", payload, 0)[0]."""

def parse_docinfo(data: bytes) -> DocInfo:
    """iter_records(data) 에서 tag_id == HWPTAG_PARA_SHAPE 만 순서대로 parse_para_shape. 다른 태그는 건너뛴다.
    data == b"" → EMPTY_DOCINFO. 잘린 레코드는 iter_records 의 Hwp2mdError 그대로 전파."""
```

### 4.4 HWP 5.0 본문·리더 연결 (Stage 3)
```python
# hwp5/body.py — 시그니처 변경(기본값으로 기존 호출 호환). 알고리즘은 전 태스크 §4.3 그대로, 아래 3곳만 추가
def parse_blocks(records: Iterable[Record], docinfo: DocInfo = EMPTY_DOCINFO) -> list[Block]
def _heading_level(para_header_payload: bytes, docinfo: DocInfo) -> int:
    """len(payload) < 14 → 0. para_shape_id = struct.unpack_from("<H", payload, 12)[0]; return docinfo.heading_level(para_shape_id)."""
def _parse_paragraph(recs, i, level, docinfo) -> tuple[str, int, list[Block], int]:
    """반환 (text, heading_level, trailing, next_i). heading_level = _heading_level(recs[i].payload, docinfo) (i 는 PARA_HEADER)."""
def _parse_table(recs, i, ctrl_level, docinfo) -> tuple[Table | None, int]
```
- `Paragraph`를 만드는 두 곳(최상위 단락, 표 아닌 컨트롤 안에서 흘러나오는 단락)은 `Paragraph(text, heading_level)`. 표 셀 단락은 텍스트만 쓰므로 수준을 버린다(§7-5 기본값: 표 안 제목은 셀 텍스트).
- 긴 제목도 제목으로 둔다(길이 제한 없음, §7-5).
```python
# hwp5/reader.py — 기존 함수 동작 불변, 1개 추가 + read_blocks 변경
def read_streams(path: Path) -> tuple[bytes, list[bytes]]:
    """(DocInfo 바이트 — 압축이면 해제, 스트림이 없으면 b"" ; [Section0, Section1, ...]).
    OLE 검사·FileHeader 검사·encrypted/distribution 예외·Section0 없음 예외는 현재 read_sections 와 글자 그대로 같다(코드를 이 함수로 옮긴다)."""
def read_sections(path: Path) -> list[bytes]:
    """호환 래퍼: return read_streams(path)[1]"""
def read_blocks(path: Path) -> list[Block]:
    """docinfo_raw, sections = read_streams(path); docinfo = parse_docinfo(docinfo_raw);
    각 섹션 parse_blocks(iter_records(section), docinfo) 를 이어 붙인다."""
```
- `read_paragraphs` 호환 래퍼는 불변(제목 텍스트도 포함해 돌려준다 — 제목도 Paragraph이므로).

### 4.5 합성 HWP 5.0 생성기 확장 (`tests/synth_hwp5.py`, Stage 2) — 기존 함수·상수의 바이트 출력은 제목 없는 입력에서 불변
```python
HWPTAG_PARA_SHAPE = 0x19   # 모듈 상수로 직접 정의 (records.py 는 Stage 3 에서 같은 값을 갖게 된다. import 하지 않는다)
HWPTAG_STYLE = 0x1A

@dataclass(frozen=True)
class SynthHeading:
    text: str
    level: int                    # 1~7 (개요 1~7). para_shape_id = style_id = level 로 기록

@dataclass(frozen=True)
class SynthCell:
    paragraphs: tuple[str | SynthHeading, ...]   # 타입만 넓어짐. 기존 tuple[str, ...] 값 그대로 유효
    col: int; row: int; col_span: int = 1; row_span: int = 1

Item = str | SynthTable | SynthHeading

def has_heading(items: Sequence[Item]) -> bool
    # items 에 SynthHeading 이 있거나, SynthTable 의 어느 셀 paragraphs 에 SynthHeading 이 있으면 True
def build_paragraph(text: str, *, last: bool, level: int = 0, para_shape_id: int = 0, style_id: int = 0) -> bytes
    # PARA_HEADER = struct.pack("<IIHBBHHHI", nchars, 0, para_shape_id, style_id, 0, 1, 0, 1, 0). 기본값이면 기존 바이트와 동일
def build_para_shape(*, outline_level: int) -> bytes        # §4.3-D 54 bytes. outline_level 0 → attr1 0, 1~7 → (1<<23)|((L-1)<<25)
def build_style(index: int) -> bytes                        # §4.3-E. index 0 바탕글/Normal(para_shape 0), 1~7 개요 L/Outline L(para_shape L)
def build_docinfo(*, outline: bool = False) -> bytes
    # outline False → 현재와 바이트 동일(DOCUMENT_PROPERTIES 1개, 30 bytes, sha256 39f61ef96a725101222bf887e50fcaac3c9b9c80c3610caa593c582870d031d4)
    # outline True  → DOCUMENT_PROPERTIES + build_record(HWPTAG_PARA_SHAPE, 1, build_para_shape(outline_level=i)) for i in range(8) + build_record(HWPTAG_STYLE, 1, build_style(i)) for i in range(8)
def build_table_control(table, *, level, last) -> bytes
    # 셀 단락 p 가 SynthHeading 이면 build_paragraph(p.text, last=..., level=level+2, para_shape_id=p.level, style_id=p.level), str 이면 기존과 동일
def build_section0(items: Sequence[Item]) -> bytes
    # SynthHeading h → build_paragraph(h.text, last=..., para_shape_id=h.level, style_id=h.level). str/SynthTable 은 기존과 동일
def build_hwp5(items: Sequence[Item], *, properties: int = 0x1) -> bytes
    # docinfo = build_docinfo(outline=has_heading(items)). 나머지 동일
def write_hwp5(path, items, *, properties=0x1) -> Path        # 불변
```
- **태그 상수 순서**: Stage 2는 `records.py`를 쓰지 못하므로 `synth_hwp5.py` 안에 위 두 상수를 모듈 상수로 직접 정의한다. Stage 3에서 `records.py`에 같은 값을 추가하고, `test_hwp5_docinfo.py`가 두 값의 동일성을 검사한다(§4.10-C 1).
- **F. 바이트 불변 검증값 (sha256, BASE 기준. Stage 2 테스트가 고정한다)**
  | 입력 | `build_hwp5(items)` (압축) | `build_hwp5(items, properties=0)` |
  |---|---|---|
  | `FIXTURE_PARAGRAPHS` | `8e17f5de3eabea84e476d13d0e5dc993e629de8597d850b75921ad37c05b8b4b` | `50f3b370aa8f41c2ccc8ca961500567a956de10baebe4bb957b8848a1980b030` |
  | `FIXTURE_ITEMS_WITH_TABLE` | `b3635fb47a3412ca763b8491d9b61e8e8eb400d7950292a0dc500df201ffd7ee` | `93121aecd08248f24ac247473cd0ec96348eb28b832d2dc2a670d7ec3da4a689` |
  | `FIXTURE_ITEMS_MERGED` | `223eb106e7f43245822cc178f919abba72d2a45e42fa386d4cf6e38b4796d33e` | `bb8c92ff627fbca29984d7371c9db1c0cb98bfbe08cfec250a03d69ec03ad097` |
  기존 `_BASE_PLAIN_SECTION_SHA256`(section0) 테스트도 그대로 통과해야 한다.

### 4.6 HWPX header.xml — 요소·속성과 파서 (Stage 5, 생성기 Stage 4 가 같은 값을 쓴다)
**A. 네임스페이스·요소 (실제 샘플 3개 `Contents/header.xml` 루트 `xmlns` 선언에서 확인)**
```python
# src/hwp2md/hwpx/header.py
NS_HH = "http://www.hancom.co.kr/hwpml/2011/head"
NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"      # body.py 와 같은 값 (hp:switch 가 이 네임스페이스)
HH_HEAD = f"{{{NS_HH}}}head"
HH_PARA_PR = f"{{{NS_HH}}}paraPr"
HH_HEADING = f"{{{NS_HH}}}heading"
HEADING_OUTLINE = "OUTLINE"                                   # heading/@type 값. 그 외 관찰값: NONE, NUMBER, BULLET
MAX_HEADING_LEVEL = 6
```
- 구조(실제 샘플): `hh:head[@version="1.5"][@secCnt]` → `hh:refList` → `hh:paraProperties[@itemCnt]` → `hh:paraPr[@id]` 자식 `hh:align`, `hh:heading[@type][@idRef][@level]`, `hh:breakSetting`, `hh:autoSpacing`, `hp:switch`, `hh:border`. `id`는 0부터 연속(샘플 3개 모두). 또 `hh:refList/hh:styles/hh:style[@id][@name][@engName][@paraPrIDRef]`(이번에는 읽지 않음).
- **`hp:switch` 변형(샘플 2에서 3개)**: `hh:heading`이 직계 자식이 아니라 `hp:switch/hp:case[@hp:required-namespace]/hh:heading`(OUTLINE level 7·8)과 `hp:switch/hp:default/hh:heading`(NONE) 안에 있다. 규칙: `next(pp.iter(HH_HEADING), None)` — paraPr 하위 트리의 **문서 순서 첫 번째** `hh:heading`(직계 자식이 있으면 그것이 먼저 나오고, 없으면 `hp:case` 쪽이 먼저 나온다). `pp.find(...) or ...` 패턴은 쓰지 않는다(자식 없는 lxml 요소는 falsy). level 7·8 은 §4.2-B clamp 로 6.
- `level` 속성은 0 기준(실제 샘플: 스타일 "개요 1" → paraPr heading level="0"). 수준 공식은 §4.2-B.

**B. 공개 API**
```python
@dataclass(frozen=True)
class HeaderInfo:
    para_levels: dict[int, int]      # paraPr id → heading/@level (OUTLINE 인 것만)
    def heading_level(self, para_pr_id: int | None) -> int:
        """para_pr_id 가 None 이거나 para_levels 에 없으면 0, 있으면 min(level + 1, MAX_HEADING_LEVEL)."""

EMPTY_HEADER = HeaderInfo(para_levels={})

def parse_header_xml(data: bytes) -> etree._Element:
    """etree.fromstring(data, _make_parser()). bytes 만 받는다.
    XMLSyntaxError → Hwp2mdError(f"malformed header XML: {exc}"). root.tag != HH_HEAD → Hwp2mdError(f"unexpected header root element: {root.tag}")."""

def _make_parser() -> etree.XMLParser:
    """etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False) — reader.make_parser 와 같은 옵션. 호출마다 새 인스턴스."""

def parse_header(root: etree._Element) -> HeaderInfo:
    """for pp in root.iter(HH_PARA_PR): pid = _int(pp.get("id")); None 이면 건너뜀.
       h = next(pp.iter(HH_HEADING), None); None 이면 건너뜀.  (lxml 요소를 bool 로 쓰지 않는다 — `is None` 비교만)
       h.get("type") != HEADING_OUTLINE 이면 건너뜀. lvl = _int(h.get("level")); None 이면 건너뜀. para_levels[pid] = lvl."""
```
- 순환 import 방지: `header.py` 는 `lxml.etree`, `..errors` 만 import 한다(`reader.py` import 금지 — reader 가 header 를 import 한다). `_make_parser` 옵션 3개는 글자 그대로.

### 4.7 HWPX 본문·리더 연결 (Stage 5)
```python
# hwpx/reader.py — 추가·변경
HWPX_HEADER = "Contents/header.xml"
def read_package(path: Path) -> tuple[bytes | None, list[bytes]]:
    """(header.xml 바이트 — 엔트리 없으면 None ; 섹션 바이트 목록). zip 열기·BadZipFile·section_names·MAX_SECTION_BYTES 검사는 현재 read_sections 와 같다(코드를 옮긴다). header.xml 도 file_size > MAX_SECTION_BYTES 면 Hwp2mdError(f"header XML too large: {size} bytes")."""
def read_sections(path: Path) -> list[bytes]:      # 호환 래퍼: return read_package(path)[1]
def read_blocks(path: Path) -> list[Block]:
    """header_raw, sections = read_package(path); info = EMPTY_HEADER if header_raw is None else parse_header(parse_header_xml(header_raw));
    각 섹션 parse_section(parse_section_xml(data), info) 를 이어 붙인다."""

# hwpx/body.py — 시그니처 변경(기본값으로 기존 호출 호환)
def parse_paragraph(p: etree._Element, header: HeaderInfo = EMPTY_HEADER) -> list[Block]:
    """level = header.heading_level(_int_attr(p, "paraPrIDRef")) 를 한 번 계산. flush() 가 Paragraph(text, level) 을 만든다. 나머지 불변."""
def parse_section(root: etree._Element, header: HeaderInfo = EMPTY_HEADER) -> list[Block]
# _cell_text 는 parse_paragraph(p) 를 기본값으로 호출(셀 단락 수준 무시 — hwp5 와 동일)
```

### 4.8 합성 HWPX 생성기 확장 (`tests/synth_hwpx.py`, Stage 4) — 제목 없는 입력에서 바이트 불변
```python
from synth_hwp5 import Item, SynthCell, SynthHeading, SynthTable, has_heading   # 재정의 금지
NS_HH 는 기존 상수 유지 (header.py 와 같은 값. Stage 5 테스트가 동일성 확인)

def p_attrs(para_pr_id: int) -> str
    # f'paraPrIDRef="{para_pr_id}" styleIDRef="{para_pr_id}" pageBreak="0" columnBreak="0" merged="0"'. 기존 상수 P_ATTRS 는 유지하고 P_ATTRS == p_attrs(0) 이어야 한다
def paragraph_xml(text: str, *, para_id: int, first: bool = False, para_pr_id: int = 0) -> str   # P_ATTRS 자리에 p_attrs(para_pr_id)
def table_xml(table, *, para_id, first=False) -> str        # 자리표시자 p 는 p_attrs(0). 불변
def cell_xml(cell: SynthCell) -> str
    # 셀 단락 p 가 SynthHeading 이면 paragraph_xml(p.text, para_id=0, para_pr_id=p.level), str 이면 기존과 동일. 빈 튜플이면 ("",) 처리 기존과 동일
def section_xml(items: Sequence[Item]) -> bytes
    # SynthHeading h → paragraph_xml(h.text, para_id=i, first=(i == 0), para_pr_id=h.level)
def header_xml(section_count: int, *, outline: bool) -> bytes
    # outline False → 현재 문자열과 바이트 동일:
    #   XML_DECL + f'<hh:head xmlns:hh="{NS_HH}" version="1.5" secCnt="{n}"><hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/><hh:refList/></hh:head>'
    # outline True →
    #   XML_DECL + f'<hh:head xmlns:hh="{NS_HH}" xmlns:hp="{NS_HP}" version="1.5" secCnt="{n}">'
    #   + '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
    #   + '<hh:refList><hh:paraProperties itemCnt="8">' + "".join(para_pr_xml(i) for i in range(8)) + '</hh:paraProperties>'
    #   + '<hh:styles itemCnt="8">' + "".join(style_xml(i) for i in range(8)) + '</hh:styles></hh:refList></hh:head>'
def para_pr_xml(i: int) -> str
    # f'<hh:paraPr id="{i}" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="1" suppressLineNumbers="0" checked="0">'
    # + '<hh:align horizontal="JUSTIFY" vertical="BASELINE"/>'
    # + f'<hh:heading type="{"NONE" if i == 0 else "OUTLINE"}" idRef="0" level="{max(i - 1, 0)}"/></hh:paraPr>'
def style_xml(i: int) -> str
    # name, eng = ("바탕글", "Normal") if i == 0 else (f"개요 {i}", f"Outline {i}")
    # f'<hh:style id="{i}" type="PARA" name="{name}" engName="{eng}" paraPrIDRef="{i}" charPrIDRef="0" nextStyleIDRef="{i}" langID="1042" lockForm="0"/>'
def hwpx_entries(items, *, more_sections=()) -> dict[str, bytes]
    # header = header_xml(n, outline=any(has_heading(s) for s in sections)). 엔트리 순서·나머지 불변
```
- **E. 바이트 불변 검증값 (`build_hwpx(items)` sha256, BASE 기준)**: `FIXTURE_PARAGRAPHS` `b83d0aa5762aeb738f5a78819c0f050098d5eb23d2f960d4e8c0d32ac9530deb` · `FIXTURE_ITEMS_WITH_TABLE` `185204bc869255ddfc9cc1d26ea85a34c6a89cea674f5a99ad5627934f4c0db8` · `FIXTURE_ITEMS_MERGED` `65b87fb60e131bf30b40dc4a03f9beaf82e3b7d11936a134075bcb3118bdc84e`.

### 4.9 공용 제목 fixture (`tests/synth_hwp5.py` 끝에 추가. E2E·단위 테스트가 이 이름을 그대로 import)
```python
FIXTURE_ITEMS_HEADINGS: list[Item] = [
    SynthHeading("문서 제목", 1), "본문 단락", SynthHeading("1. 사업 개요", 2),
    FIXTURE_TABLE, SynthHeading("가. 세부 내용", 3), "마지막 단락",
]
EXPECTED_MARKDOWN_HEADINGS = (
    "# 문서 제목\n\n본문 단락\n\n## 1. 사업 개요\n\n| 구분 | 내용 |\n|---|---|\n| 지원 규모 | 총 30억 원 |\n\n"
    "### 가. 세부 내용\n\n마지막 단락\n"
)
EXPECTED_BLOCKS_HEADINGS = [
    Paragraph("문서 제목", 1), Paragraph("본문 단락"), Paragraph("1. 사업 개요", 2),
    Table([["구분", "내용"], ["지원 규모", "총 30억 원"]]), Paragraph("가. 세부 내용", 3), Paragraph("마지막 단락"),
]
EXPECTED_COUNTS_HEADINGS = (2, 1, 3)          # (paragraph_count, table_count, heading_count)

FIXTURE_ITEMS_HEADING_EDGE: list[Item] = [
    SynthHeading("깊은 수준", 7), SynthHeading("", 1), SynthHeading("두 줄\n제목", 2), "본문",
]
EXPECTED_MARKDOWN_HEADING_EDGE = "###### 깊은 수준\n\n## 두 줄 제목\n\n본문\n"
EXPECTED_BLOCKS_HEADING_EDGE = [Paragraph("깊은 수준", 6), Paragraph("두 줄\n제목", 2), Paragraph("본문")]
EXPECTED_COUNTS_HEADING_EDGE = (1, 0, 2)

FIXTURE_ITEMS_HEADING_IN_CELL: list[Item] = [
    SynthHeading("표 제목", 1),
    SynthTable(rows=1, cols=2, cells=(
        SynthCell((SynthHeading("셀 제목", 2),), col=0, row=0), SynthCell(("값",), col=1, row=0),
    )),
]
EXPECTED_MARKDOWN_HEADING_IN_CELL = "# 표 제목\n\n| 셀 제목 | 값 |\n|---|---|\n"
EXPECTED_BLOCKS_HEADING_IN_CELL = [Paragraph("표 제목", 1), Table([["셀 제목", "값"]])]
EXPECTED_COUNTS_HEADING_IN_CELL = (0, 1, 1)
```
- 빈 텍스트 제목(`SynthHeading("", 1)`)은 두 포맷 모두 블록을 만들지 않는다(hwp5: PARA_TEXT가 `\r\x00`만 → `""`; hwpx: `<hp:run charPrIDRef="0"/>`). 개요 7 → `######`. `"\n"`은 hwp5 WCHAR 10 / hwpx `hp:lineBreak` 로 직렬화되고 블록 텍스트에는 `"\n"`으로 남으며 렌더에서 공백이 된다.
- 비압축 변형도 섹션·DocInfo 각각 4096 bytes 미만(DocInfo outline = 30 + 8×58 + 8×(4+32|40) ≈ 830 bytes).

### 4.10 단위 테스트 계약 (파일·케이스 이름 고정)
**A. `tests/unit/test_render_heading.py` (Stage 1)**
1. `test_paragraph_default_level_zero_equality` — `Paragraph("a") == Paragraph("a", 0)`, `.level == 0`, `Paragraph("a", 1) != Paragraph("a")`
2. `test_render_heading_levels` — L=1..6: `render_blocks([Paragraph("t", L)]) == "#" * L + " t\n"`
3. `test_render_heading_clamps_above_six` — `Paragraph("t", 9)` → `"###### t\n"`
4. `test_render_heading_newline_to_space_and_strip` — `Paragraph(" a\nb ", 2)` → `"## a b\n"`
5. `test_render_heading_empty_text_skipped` — `[Paragraph("", 2), Paragraph(" \n ", 3), Paragraph("x")]` → `"x\n"`
6. `test_render_heading_between_paragraphs` — `[Paragraph("a"), Paragraph("h", 1), Paragraph("b")]` → `"a\n\n# h\n\nb\n"`
7. `test_convert_result_has_heading_count` — `convert(write_hwp5(tmp_path/"s.hwp", FIXTURE_PARAGRAPHS), tmp_path/"out")` → `heading_count == 0`, `paragraph_count == 3`

**B. `tests/unit/test_synth_hwp5.py` 추가 (Stage 2. 기존 15개 불변)**
1. `test_docinfo_default_unchanged` — `build_docinfo() == build_docinfo(outline=False)`, `len == 30`, sha256 == §4.5 값, 레코드 1개(tag 0x10)
2. `test_docinfo_outline_records` — `build_docinfo(outline=True)` 레코드 태그 순서 `[0x10] + [0x19]*8 + [0x1A]*8`; PARA_SHAPE payload 전부 54 bytes; shape 0 attr1 == 0; shape L(1..7) attr1 == `(1<<23)|((L-1)<<25)`
3. `test_style_record_layout` — STYLE[2] payload: 길이 40, 이름 `"개요 2"`, 영문 `"Outline 2"`, para_shape_id 2 (§4.3-E 대로 struct 디코드)
4. `test_heading_paragraph_header_ids` — `build_section0(FIXTURE_ITEMS_HEADINGS)` level-0 PARA_HEADER 의 `(para_shape_id, style_id)` == `[(1,1),(0,0),(2,2),(0,0),(3,3),(0,0)]`, payload 전부 22 bytes
5. `test_cell_heading_paragraph_header_ids` — `FIXTURE_ITEMS_HEADING_IN_CELL` 의 level-2 PARA_HEADER `(para_shape_id, style_id)` == `[(2,2),(0,0)]`
6. `test_fixture_bytes_unchanged_sha256` — §4.5-F 표 6개 값 전부 일치 (parametrize)
7. `test_has_heading` — `has_heading(FIXTURE_ITEMS_HEADING_IN_CELL) is True`, `has_heading(FIXTURE_ITEMS_HEADINGS) is True`, `has_heading(FIXTURE_ITEMS_WITH_TABLE) is False`, `has_heading(FIXTURE_PARAGRAPHS) is False`
8. `test_heading_fixture_round_trips_text` — `read_blocks(write_hwp5(tmp_path/"h.hwp", FIXTURE_ITEMS_HEADINGS))` 의 Paragraph 텍스트 == `["문서 제목", "본문 단락", "1. 사업 개요", "가. 세부 내용", "마지막 단락"]`, Table 1개 == `FIXTURE_TABLE` 기대 rows (수준은 보지 않는다 — Stage 3 전)

**C. `tests/unit/test_hwp5_docinfo.py` (Stage 3)**
1. `test_tag_constants_match_generator` — `records.HWPTAG_PARA_SHAPE == synth_hwp5.HWPTAG_PARA_SHAPE == 0x19`, `records.HWPTAG_STYLE == synth_hwp5.HWPTAG_STYLE == 0x1A`
2. `test_parse_para_shape_bits` — attr1 `(1<<23)|(2<<25)` → `ParaShape(1, 2)`; `(2<<23)` → type 2; 3 bytes → `Hwp2mdError` 메시지 `truncated PARA_SHAPE record`
3. `test_parse_docinfo_collects_shapes_in_order` — `parse_docinfo(build_docinfo(outline=True))` → 8개, `heading_type == [0,1,1,1,1,1,1,1]`, `heading_level == [0,0,1,2,3,4,5,6]`
4. `test_parse_docinfo_empty_and_default` — `parse_docinfo(b"") == EMPTY_DOCINFO`, `parse_docinfo(build_docinfo()).para_shapes == ()`
5. `test_heading_level_rule` — outline DocInfo: `heading_level(0) == 0`, `(1) == 1`, `(6) == 6`, `(7) == 6`, `(99) == 0`, `(-1) == 0`; `DocInfo((ParaShape(2, 3), ParaShape(3, 1)))` → 둘 다 0
6. `test_read_blocks_heading_fixtures` — parametrize 3: `(FIXTURE_ITEMS_HEADINGS, EXPECTED_BLOCKS_HEADINGS)`, `(…EDGE…)`, `(…IN_CELL…)` → `read_blocks(write_hwp5(...)) == expected`
7. `test_read_blocks_uncompressed_heading_fixture` — `properties=0` → `== EXPECTED_BLOCKS_HEADINGS`
8. `test_empty_docinfo_stream_means_no_headings` — `build_cfb({"FileHeader": build_file_header(properties=0), "DocInfo": b"", "BodyText/Section0": build_section0(FIXTURE_ITEMS_HEADINGS)})` → 블록 == `[Paragraph(b.text) if isinstance(b, Paragraph) else b for b in EXPECTED_BLOCKS_HEADINGS]`
9. `test_truncated_docinfo_raises` — `"DocInfo": build_docinfo(outline=True)[:-3]`(properties=0) → `Hwp2mdError`, 메시지 `truncated record`
10. `test_read_sections_wrapper_matches_read_streams` — `read_sections(p) == read_streams(p)[1]`, `len(read_streams(p)[0]) > 0`

**D. `tests/unit/test_synth_hwpx.py` 추가 (Stage 4. 기존 9개 불변)**
1. `test_header_default_bytes_unchanged` — `hwpx_entries(FIXTURE_PARAGRAPHS)["Contents/header.xml"]` == §4.8 outline False 문자열의 `.encode("utf-8")`(secCnt 1)
2. `test_fixture_bytes_unchanged_sha256` — §4.8-E 3개 값 일치 (parametrize)
3. `test_header_outline_structure` — `hwpx_entries(FIXTURE_ITEMS_HEADINGS)` header 를 `xml.etree.ElementTree` 로 파싱: `hh:paraPr` 8개 id `"0".."7"`, `(heading/@type, @level)` == `[("NONE","0"), ("OUTLINE","0"), …, ("OUTLINE","6")]`, `hh:style` 8개, style 3 `name="개요 3"`, `paraPrIDRef="3"`
4. `test_heading_paragraph_attrs` — `section_xml(FIXTURE_ITEMS_HEADINGS)` 최상위 `hp:p` 의 `paraPrIDRef` == `["1","0","2","0","3","0"]`, `styleIDRef` 동일
5. `test_cell_heading_paragraph_attrs` — `FIXTURE_ITEMS_HEADING_IN_CELL` 의 첫 `hp:tc` 안 `hp:p` `paraPrIDRef == "2"`
6. `test_p_attrs_zero_equals_constant` — `p_attrs(0) == P_ATTRS`
7. `test_heading_fixture_round_trips_text` — hwpx `read_blocks(write_hwpx(..., FIXTURE_ITEMS_HEADINGS))` Paragraph 텍스트 == B-8 과 같은 리스트(수준은 보지 않는다 — Stage 5 전)

**E. `tests/unit/test_hwpx_header.py` (Stage 5)** — 헬퍼 `_head(inner: str) -> etree._Element` = `parse_header_xml((XML_DECL + f'<hh:head xmlns:hh="{NS_HH}" xmlns:hp="{NS_HP}" version="1.5" secCnt="1">{inner}</hh:head>').encode())`
1. `test_ns_constant_matches_generator_and_body` — `header.NS_HH == synth_hwpx.NS_HH`, `header.NS_HP == body.NS_HP`
2. `test_parse_header_outline_levels` — `parse_header(parse_header_xml(hwpx_entries(FIXTURE_ITEMS_HEADINGS)["Contents/header.xml"]))` → `para_levels == {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6}`; `heading_level(1) == 1`, `(7) == 6`, `(0) == 0`, `(None) == 0`, `(99) == 0`
3. `test_heading_inside_switch_case_used` — paraPr id 5 에 `<hp:switch><hp:case hp:required-namespace="x"><hh:heading type="OUTLINE" idRef="0" level="7"/></hp:case><hp:default><hh:heading type="NONE" idRef="0" level="0"/></hp:default></hp:switch>` → `heading_level(5) == 6`
4. `test_number_and_bullet_not_heading` — type `NUMBER`·`BULLET` level 2 → 0
5. `test_missing_level_or_bad_id_ignored` — OUTLINE 인데 level 없음 → 0; `id="x"` 인 paraPr 건너뜀(예외 없음)
6. `test_wrong_root_raises` — `parse_header_xml(b'<?xml version="1.0"?><x/>')` → `Hwp2mdError` `unexpected header root element`
7. `test_malformed_header_raises` — `b"<hh:head"` → `Hwp2mdError` `malformed header XML`
8. `test_parser_blocks_entities` — `_make_parser().resolve_entities is False`
9. `test_missing_header_entry_means_no_headings` — `entries = hwpx_entries(FIXTURE_ITEMS_HEADINGS); del entries["Contents/header.xml"]; build_zip` → `read_blocks` == `[Paragraph(b.text) if isinstance(b, Paragraph) else b for b in EXPECTED_BLOCKS_HEADINGS]`
10. `test_read_blocks_heading_fixtures` — parametrize 3 (C-6 과 같은 쌍) → hwpx `read_blocks(write_hwpx(...)) == expected`

**F. `tests/unit/test_cross_format.py` 추가 (Stage 5. 기존 3개 불변)**
1. `test_heading_fixtures_same_markdown_both_formats` — parametrize 3 `(items, expected_markdown, expected_counts)`: hwp5·hwpx `convert().markdown` 둘 다 `== expected_markdown`, `(paragraph_count, table_count, heading_count) == expected_counts` 양쪽 동일
2. `test_read_paragraphs_includes_heading_text` — hwp5 `read_paragraphs(write_hwp5(..., FIXTURE_ITEMS_HEADINGS)) == ["문서 제목", "본문 단락", "1. 사업 개요", "가. 세부 내용", "마지막 단락"]`

### 4.11 실제 샘플 조사 결과 (2026-10-22 planner, 읽기 전용. implementer·test-writer는 추측하지 말고 이 숫자를 쓴다)
**HWP 5.0** (`DocInfo` 압축, PARA_HEADER 전부 22 bytes)
| 파일 | 버전 | DocInfo 레코드 | PARA_SHAPE 수(길이) | 개요 비트가 선 문단 모양 id → 개요 수준 | 최상위 단락 중 개요 단락(비어 있지 않음) | 표 셀 안 개요 단락 | 현재 (단락, 표) | **기대 (단락, 표, 제목)** |
|---|---|---|---|---|---|---|---|---|
| `form200005063113.hwp` | `0x05000006` | 208 (0x19 ×64, 0x1A ×12) | 64 (42 B) | 4→1, 5→2, 6→3, 7→4, 8→5, 9→6, 10→7 | **18**: 수준1 ×6(id 4), 수준2 ×4(id 5), 수준3 ×4(id 6), 수준7 ×4(id 10). 전부 텍스트 있음, 줄바꿈 없음, 최대 63자 | 14 (셀 텍스트로만) | (118, 8) | **(100, 8, 18)** — Markdown 제목 줄 분포 `# `×6, `## `×4, `### `×4, `###### `×4 |
| `form210001070268.hwp` | `0x05000202` | 55 (0x19 ×13, 0x1A ×14) | 13 (46 B) | 4→1 … 10→7 | 0 (본문 단락의 para_shape_id 는 1·2 만) | 0 | (47, 0) | **(47, 0, 0)** |
- 두 파일 모두 본문 `style_id`는 전부 0(바탕글) — 스타일로는 판정 불가, 문단 모양으로만 판정 가능(§7-2 근거). STYLE 레코드 이름은 `바탕글/Normal, 본문/Body, 개요 1~7/Outline 1~7, 쪽 번호, 머리말, 각주(, 미주, 메모)`, 길이 26~44.
- 샘플 1 현재 출력 `.md` 284줄 중 `#`로 시작하는 줄 0 → 제목 줄 수 세기(`^#{1,6} `)가 정확하다.

**HWPX** (`Contents/header.xml` 루트 `hh:head version="1.5"`, `hh:refList` 자식 순서 `fontfaces, borderFills, charProperties, tabProperties, numberings, paraProperties, styles(, memoProperties)`)
| 파일 | header.xml | paraPr 수 | heading type 분포 | OUTLINE paraPr id → level | 최상위 `hp:p` 중 OUTLINE 참조 | 전체 `hp:p` 중 OUTLINE 참조 | **기대 (단락, 표, 제목)** |
|---|---|---|---|---|---|---|---|
| `(서식1) 비영리법인 현황 제출 양식.hwpx` | 64 KB | 17 | NONE 10, OUTLINE 7 | 13→0, 12→1, 11→2, 10→3, 9→4, 8→5, 7→6 | 0 | 0 | **(1, 1, 0)** |
| `(서식2) 사업실적 및 사업계획 제출 양식.hwpx` | 204 KB | 82 | NONE 75, OUTLINE 10 (그중 3개는 `hp:switch/hp:case` 안, level 7·8·7) | 3→0, 4→1, 5→2, 6→3, 7→4, 8→5, 9→6, 19→7, 17→8, 18→7 | 0 | 0 | **(80, 31, 0)** |
| `브라더 공공기관 보고서 양식.hwpx` | 115 KB | 41 | NONE 34, OUTLINE 7 | 15→0, 14→1, 13→2, 12→3, 11→4, 10→5, 9→6 | 0 | 0 | **(32, 8, 0)** |
- 모든 `hp:p`에 `paraPrIDRef`·`styleIDRef` 속성이 있다. 스타일 `개요 N`은 `paraPrIDRef`로 OUTLINE paraPr를 가리키며 0-기준 level = N−1 (수준 공식 §4.2-B 근거).
- HWPX 실제 양성 샘플은 없다. 양성 검증은 HWP 5.0 샘플 1 + 합성 fixture(§4.9)가 담당한다(§8 리스크, §7-7).

### 4.12 CLI 2행 (Stage 7, `src/hwp2md/cli.py`) — §7-4 기본값: 제목 0개면 표기 생략
현재 49행 `print(f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개")` 1줄을 아래 3줄로 교체(그 외 글자 하나도 바꾸지 않는다):
```python
    summary = f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개"
    if result.heading_count:
        summary += f" · 제목 {result.heading_count}개"
    print(summary)
```
- 결과: 제목 0개 → `  단락 N개 · 표 M개`(현재와 동일) / 제목 K≥1 → `  단락 N개 · 표 M개 · 제목 K개`. 구분자 ` · `(공백 + U+00B7 + 공백). 종료 코드·stderr·`--version` 불변.

### 4.13 E2E 계약
**A. 기존 파일 수정 — 정확히 2줄 (Stage 8, test-writer). 다른 글자는 바꾸지 않는다**
- `tests/e2e/test_cli_convert.py` 79행: `m = re.match(r"^  단락 (\d+)개 · 표 (\d+)개$", lines[1])` → `m = re.match(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 \d+개)?$", lines[1])`
- `tests/e2e/test_cli_hwpx.py` 32행: `STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개$")` → `STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 \d+개)?$")`
- 이유: 실제 샘플 `form200005063113.hwp` 2행이 `  단락 100개 · 표 8개 · 제목 18개`가 되어 `$` 앵커 정규식이 깨진다. 그룹 1·2 의미는 불변이므로 기존 단언은 그대로다.

**B. `tests/e2e/test_cli_heading.py` 신규 — conftest의 `run_cli` 사용, `synth_hwp5`·`synth_hwpx`에서 import. 케이스 이름 고정**
```python
REAL_HWP5 = sorted(Path(__file__).resolve().parents[1].joinpath("fixtures").glob("*.hwp"))
REAL_HWPX = sorted(Path(__file__).resolve().parents[1].joinpath("fixtures", "hwpx").glob("*.hwpx"))
REAL_EXPECTED: dict[str, tuple[int, int, int]] = {           # (단락, 표, 제목) §4.11
    "form200005063113.hwp": (100, 8, 18),
    "form210001070268.hwp": (47, 0, 0),
    "(서식1) 비영리법인 현황 제출 양식.hwpx": (1, 1, 0),
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx": (80, 31, 0),
    "브라더 공공기관 보고서 양식.hwpx": (32, 8, 0),
}
REAL_HEADING_LEVELS: dict[str, dict[int, int]] = {"form200005063113.hwp": {1: 6, 2: 4, 3: 4, 6: 4}}
STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 (\d+)개)?$")
HEADING_LINE = re.compile(r"^(#{1,6}) \S")
```
1. `test_convert_heading_hwp5_success` — `write_hwp5(tmp_path/"heading.hwp", FIXTURE_ITEMS_HEADINGS)`; 종료 0; `lines[0] == f"✓ heading.hwp → {out_dir / 'heading.md'}"`; `lines[1] == "  단락 2개 · 표 1개 · 제목 3개"`; 내용 `== EXPECTED_MARKDOWN_HEADINGS`; 증거 `ILLY_SHOT_DIR/heading_hwp5.md`
2. `test_convert_heading_hwpx_success` — `write_hwpx(tmp_path/"heading.hwpx", FIXTURE_ITEMS_HEADINGS)`; 같은 단언(`heading.hwpx`); 증거 `heading_hwpx.md`
3. `test_heading_edge_cases_same_in_both_formats` — `FIXTURE_ITEMS_HEADING_EDGE` 를 `edge.hwp`·`edge.hwpx` 로 각각 변환(out 디렉터리 분리); 둘 다 종료 0, `lines[1] == "  단락 1개 · 표 0개 · 제목 2개"`, 내용 `== EXPECTED_MARKDOWN_HEADING_EDGE`, 두 `.md` 바이트 동일; 증거 `heading_edge.md`
4. `test_heading_in_table_cell_stays_cell_text` — `FIXTURE_ITEMS_HEADING_IN_CELL` 두 포맷; `lines[1] == "  단락 0개 · 표 1개 · 제목 1개"`; 내용 `== EXPECTED_MARKDOWN_HEADING_IN_CELL`; 증거 `heading_cell.md`
5. `test_no_heading_keeps_two_field_summary` (회귀) — `write_hwp5(..., FIXTURE_PARAGRAPHS)` → `lines[1] == "  단락 3개 · 표 0개"`, 내용 `== EXPECTED_MARKDOWN`, `"제목" not in result.stdout`; `write_hwpx(..., FIXTURE_ITEMS_WITH_TABLE)` → `lines[1] == "  단락 2개 · 표 1개"`, 내용 `== EXPECTED_MARKDOWN_WITH_TABLE`
6. `test_heading_uncompressed_variant` — `write_hwp5(..., FIXTURE_ITEMS_HEADINGS, properties=0)` → 종료 0, 내용 `== EXPECTED_MARKDOWN_HEADINGS` (비압축 DocInfo 경로)
7. `test_truncated_docinfo_exit_1` (실패 경로) — `build_cfb({"FileHeader": build_file_header(properties=0), "DocInfo": build_docinfo(outline=True)[:-3], "BodyText/Section0": build_section0(FIXTURE_ITEMS_HEADINGS)})` → `broken.hwp`; 종료 1; stderr 에 `truncated record`; `out/broken.md` 미생성
8. `test_real_fixture_headings[<name>]` — `@pytest.mark.parametrize("real", REAL_HWP5 + REAL_HWPX, ids=lambda p: p.name)`; 종료 0; `m = STDOUT_LINE2.match(lines[1])` 존재; `(p, t, h) = (int(m[1]), int(m[2]), int(m[3] or 0))`; `real.name in REAL_EXPECTED` 이면 `(p, t, h) == REAL_EXPECTED[real.name]`; `.md` 의 `HEADING_LINE` 일치 줄 수 `== h`; `real.name in REAL_HEADING_LEVELS` 이면 `dict(Counter(len(mm.group(1)) for ln in content.split("\n") if (mm := HEADING_LINE.match(ln)))) == REAL_HEADING_LEVELS[real.name]`; `len(content.strip()) > 0`; 증거 `ILLY_SHOT_DIR/{md.name}`
- `pytest.skip(`/`pytest.mark.skip` 문자열을 코드에 쓰지 않는다. 실제 샘플이 없으면 빈 parametrize 로 skipped.
- 기대 총계: 실제 샘플 5개 있을 때 신규 `12 passed`, 전체 `33 passed`. 실제 샘플이 하나도 없으면 신규 `7 passed, 1 skipped`.

### 4.14 docs/decisions.md 추가 항목 (Stage 6. 파일 끝에 추가. 아래 코드블록의 **울타리(```) 줄을 제외한 1~11행**을 그대로 옮긴다. §7 답이 기본값과 다르면 orchestrator가 승인 시 해당 문장만 치환)
```
## 2026-10-22 제목 판정: 문단 모양(PARA_SHAPE/paraPr)의 개요 비트만 본다
- 결정: HWP 5.0은 `DocInfo`의 `HWPTAG_PARA_SHAPE` 속성1 비트 23~24(머리 모양)가 개요(1)일 때 비트 25~27(수준 0~6)을, HWPX는 `header.xml`의 `hh:paraPr/hh:heading[@type="OUTLINE"]/@level`을 제목 수준으로 쓴다. 단락은 `PARA_HEADER.para_shape_id` / `hp:p/@paraPrIDRef`로 문단 모양을 찾는다. 스타일(`STYLE` 레코드, `hh:style`)의 이름·참조는 판정에 쓰지 않는다. 머리 모양이 번호·글머리표인 단락은 본문으로 둔다(리스트 렌더는 후속).
- 이유: 한컴은 스타일을 적용하면 단락의 문단 모양 ID를 바꿔 저장하므로 문단 모양이 실제로 렌더되는 속성이다. 실제 샘플 5개 모두 본문 단락의 스타일 ID가 0(바탕글)이고 개요 정보는 문단 모양에만 있었다. 스타일 이름("개요 N"/"Outline N")은 언어·사용자 설정에 따라 바뀔 수 있다.

## 2026-10-22 제목 수준: 개요 1~6 → `#`~`######`, 7 이상은 `######`로 clamp. 블록은 `Paragraph.level`
- 결정: Markdown 제목 수준 = min(개요 수준 + 1, 6). 별도 `Heading` 블록 대신 `Paragraph`에 `level: int = 0` 필드를 둔다(0 본문). 렌더는 `#`×level + 공백 + 텍스트(내부 줄바꿈은 공백), 빈 텍스트 제목은 생략, 표 셀 안의 개요 단락은 셀 텍스트로만 쓴다. 제목 길이 제한은 두지 않는다.
- 이유: Markdown은 6수준까지만 있고, 개요 7수준은 실제 샘플에서도 쓰이므로(샘플 1에 4개) 버리는 것보다 가장 낮은 제목으로 두는 쪽이 구조를 보존한다. 제목은 HWP에서도 "개요 속성이 붙은 단락"이라 필드 추가가 모델에 맞고, 기존 `Paragraph("text")` 호출·동등 비교·테스트가 그대로 유효하다.

## 2026-10-22 CLI 2행: 제목이 있을 때만 ` · 제목 K개`를 덧붙이고, 제목은 단락 수에서 분리한다
- 결정: `paragraph_count`는 본문 단락(level 0)만, `heading_count`는 제목만 센다. CLI 2행은 `단락 N개 · 표 M개`를 유지하고 제목이 1개 이상일 때만 ` · 제목 K개`를 덧붙인다.
- 이유: vision 시나리오 1의 `제목 12개 · 표 4개` 표기와 맞추면서, 제목이 없는 문서(양식류 대부분)의 출력과 기존 테스트 문자열을 바꾸지 않기 위해서다.
```

### 4.15 README · fixtures README 변경 (Stage 6)
- `README.md` 38행 1줄 교체.
  변경 전: `현재 지원: HWP 5.0 바이너리와 HWPX(zip/XML) 두 포맷의 본문 단락 텍스트와 표(Markdown 표, 병합 셀은 빈 칸, 셀 내 단락은 <br>). 포맷은 확장자가 아니라 파일 내용으로 판별한다. 이미지·각주는 진행 중.`
  변경 후: `현재 지원: HWP 5.0 바이너리와 HWPX(zip/XML) 두 포맷의 본문 단락 텍스트, 제목 계층(개요 1~7수준 → Markdown # ~ ######, 7수준은 ######), 표(Markdown 표, 병합 셀은 빈 칸, 셀 내 단락은 <br>). 포맷은 확장자가 아니라 파일 내용으로 판별한다. 이미지·각주는 진행 중.`
- `tests/fixtures/README.md` (현재 10행. **10행은 전 태스크에서 잘못 복사된 \`\`\` 1줄이므로 삭제한다**): 5행(`*.hwp` 항목)과 6행(`hwpx/*.hwpx` 항목) 끝에 각각 ` 파일명이 \`tests/e2e/test_cli_heading.py\`의 \`REAL_EXPECTED\`에 있으면 (단락, 표, 제목) 수까지 비교한다.` 를 덧붙이고, 9행(`E2E는 지정한 폴더만 …` 문단) 뒤에 아래 2줄(빈 줄 + 문단)을 추가한다(결과 파일은 11행, 마지막 줄이 새 문단):
  ```
  
  개요(제목) 수준이 있는 샘플을 추가할 때: 한글에서 스타일 "개요 1"~"개요 7"을 적용한 문서를 이 폴더(HWP 5.0) 또는 `hwpx/`(HWPX)에 넣고, `REAL_EXPECTED`에 `(단락, 표, 제목)` 기대값을 추가한다. 기대값이 없으면 변환 성공과 "Markdown 제목 줄 수 == CLI 제목 수"만 검사한다.
  ```
  (위 코드블록의 울타리 줄을 제외한 1~2행. 1행은 빈 줄)

### 4.16 runner 공통 실행 블록 (macOS zsh. `timeout` 명령·`PIPESTATUS` 금지. Bash 도구 timeout 파라미터 600000)
**A. 단위·린트·타입 (Stage 1~5, `<N>`은 단계 번호)**
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-heading-levels && mkdir -p $T/logs $T/screenshots && \
{ uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src && uv run pytest tests/unit -q; } > $T/logs/s<N>-test.log 2>&1; echo "exit=$?" >> $T/logs/s<N>-test.log; tail -20 $T/logs/s<N>-test.log
```
**B. HWP 5.0 실제 샘플 수준 분포 (Stage 3)**
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-heading-levels && uv run python -c "
from collections import Counter
from pathlib import Path
from hwp2md.blocks import Paragraph
from hwp2md.hwp5.reader import read_blocks
for f in sorted(Path('tests/fixtures').glob('*.hwp')):
    b = read_blocks(f)
    body = sum(isinstance(x, Paragraph) and x.level == 0 for x in b)
    heads = sum(isinstance(x, Paragraph) and x.level > 0 for x in b)
    dist = dict(sorted(Counter(x.level for x in b if isinstance(x, Paragraph) and x.level).items()))
    print(f.name, body, heads, dist)
" > $T/logs/s3-real.log 2>&1; echo "exit=$?" >> $T/logs/s3-real.log; cat $T/logs/s3-real.log
```
기대: `form200005063113.hwp 100 18 {1: 6, 2: 4, 3: 4, 6: 4}` · `form210001070268.hwp 47 0 {}` · `exit=0`
**C. 실제 샘플 5개 CLI (Stage 7 검증, Stage 9 reviewer 참고)**
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-heading-levels && mkdir -p $T/logs $T/screenshots && OUT=$(mktemp -d) && \
for f in tests/fixtures/*.hwp tests/fixtures/hwpx/*.hwpx; do uv run hwp2md "$f" -o "$OUT"; echo "exit=$?"; done > $T/logs/s7-real.log 2>&1; cat $T/logs/s7-real.log; cp "$OUT"/*.md $T/screenshots/
```
기대 2행(파일 순): `  단락 100개 · 표 8개 · 제목 18개`, `  단락 47개 · 표 0개`, `  단락 1개 · 표 1개`, `  단락 80개 · 표 31개`, `  단락 32개 · 표 8개`, `exit=0` 5회.
**D. E2E (Stage 8)**
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-heading-levels && mkdir -p $T/logs $T/screenshots && \
[ -f $T/logs/e2e.log ] && mv $T/logs/e2e.log $T/logs/e2e.prev.log; \
ILLY_SHOT_DIR=$T/screenshots uv run pytest tests/e2e -q > $T/logs/e2e.log 2>&1; echo "exit=$?" >> $T/logs/e2e.log; \
tail -5 $T/logs/e2e.log; grep -E "passed|failed|error" $T/logs/e2e.log | tail -3; ls $T/screenshots
```

## 5. 단계 (Stage) — 전부 순차. 병렬 없음.

### Stage 1 — 블록 모델 `level` 필드·제목 렌더·`heading_count`
- 목적: `Paragraph.level`과 `#` 렌더, `ConvertResult.heading_count`를 넣어 리더가 수준을 채우면 바로 출력되게 한다(리더는 아직 0만 넣으므로 출력 불변).
- 담당: implementer(opus, 도구 호출 40회 이내) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §1, §4.2, §4.10-A; 읽을 파일 `src/hwp2md/blocks.py`, `src/hwp2md/render.py`, `src/hwp2md/convert.py`, `tests/unit/test_convert.py`(스타일)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/blocks.py`
  - `src/hwp2md/render.py`
  - `src/hwp2md/convert.py`
  - `tests/unit/test_render_heading.py`
- 산출물: §4.2 A·C·D, 단위 테스트 7개
- 검증 (로그 `logs/s1-test.log`): §4.16-A → `All checks passed!`, format 변경 0, `Success: no issues found in 14 source files`, unit `120 passed`(113 + 7), failed 0. `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e -q` → `21 passed`(출력 불변 확인)
  - reviewer: diff가 쓰기 범위 4개뿐, `Paragraph.level` 기본값 0, `render_blocks` 의 join·끝 개행 로직 불변, `paragraph_count` 식에 `level == 0` 포함, `__init__.py`·`cli.py` 변경 0
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count`
- 실패 시: `git restore --source=HEAD -- src/hwp2md/blocks.py src/hwp2md/render.py src/hwp2md/convert.py`, 새 파일 quarantine. RETRY 최대 3.

### Stage 2 — 합성 HWP 5.0 생성기: `SynthHeading`·DocInfo PARA_SHAPE/STYLE·바이트 불변 고정
- 목적: 제목이 든 HWP 5.0 fixture를 만들 수 있게 하고, 제목 없는 입력의 바이트가 BASE와 같음을 sha256으로 고정한다.
- 담당: implementer(opus, 40회) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 1 (`Paragraph(text, level)` 생성자가 §4.9 EXPECTED_BLOCKS에 필요)
- 입력: §4.3-A/C/D/E/F(레이아웃), §4.5, §4.9, §4.10-B; 읽을 파일 `tests/synth_hwp5.py`, `tests/unit/test_synth_hwp5.py`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/synth_hwp5.py`
  - `tests/unit/test_synth_hwp5.py`
- 산출물: §4.5 함수·타입(`SynthHeading`, `has_heading`, `build_para_shape`, `build_style`, `build_docinfo(outline=)`, 확장된 `build_paragraph`/`build_table_control`/`build_section0`/`build_hwp5`), §4.9 fixture 상수 전부, 단위 테스트 8개(기존 15개 불변)
- 검증 (로그 `logs/s2-test.log`): §4.16-A → ruff OK, mypy `14 source files`, unit `133 passed` 이상(120 + 7 + parametrize 6), failed 0. 특히 `-k "sha256 or unchanged"` 전부 pass, 기존 `test_plain_fixture_has_no_table_records` pass
  - reviewer: `src/**` 변경 0, 기존 함수가 중복 정의되지 않고 제자리에서 확장됨(`def build_paragraph` 1개, `def build_section0` 1개, `def build_docinfo` 1개), `HWPTAG_PARA_SHAPE = 0x19`·`HWPTAG_STYLE = 0x1A`가 모듈 상수로 정의됨(records.py import 아님), fixture 상수 값이 §4.9와 글자 그대로
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes`
- 실패 시: sha256 불일치는 기본 인자 경로의 바이트 변경이므로 구현 오류 → 같은 implementer 재호출(RETRY). `git restore --source=HEAD -- tests/synth_hwp5.py tests/unit/test_synth_hwp5.py`. 최대 3.

### Stage 3 — HWP 5.0 DocInfo 파서와 본문·리더 연결
- 목적: `DocInfo`의 PARA_SHAPE를 읽어 `PARA_HEADER.para_shape_id`로 단락 수준을 정하고, 합성 fixture와 실제 샘플 1에서 기대 수준이 나오게 한다.
- 담당: implementer(opus, 40회) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 2
- 입력: §4.3, §4.4, §4.9, §4.10-C, §4.11(HWP 5.0 표), §4.16-B; 읽을 파일 `src/hwp2md/hwp5/records.py`, `src/hwp2md/hwp5/body.py`, `src/hwp2md/hwp5/reader.py`, `tests/synth_hwp5.py`(import 이름), `tests/unit/test_hwp5_body.py`(기존 기대 유지 확인)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/hwp5/records.py` (상수 2줄 추가만)
  - `src/hwp2md/hwp5/docinfo.py`
  - `src/hwp2md/hwp5/body.py`
  - `src/hwp2md/hwp5/reader.py`
  - `tests/unit/test_hwp5_docinfo.py`
- 산출물: §4.3-G 공개 API, §4.4 시그니처, 단위 테스트 10개(parametrize 포함 12건 이상)
- 검증 (로그 `logs/s3-test.log`, `logs/s3-real.log`): §4.16-A → ruff OK, mypy `Success: no issues found in 15 source files`, unit `145 passed` 이상(133 + 9 + parametrize 3), failed 0. §4.16-B → 두 줄 기대값 정확히 일치, `exit=0`. `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e -q` → `21 passed`(CLI 미변경이므로 2행 불변; 샘플 1 `.md`에 `#` 줄이 생기지만 기존 E2E는 `#` 줄을 세지 않는다)
  - reviewer: `records.py` diff가 `+2` 줄만, `parse_blocks`/`parse_paragraph` 기본 인자로 기존 호출 호환, `_parse_table` 안에서는 수준을 쓰지 않음(셀 텍스트만), `read_sections` 가 `read_streams(path)[1]` 래퍼, DocInfo 스트림 없음 → `b""`(예외 아님), `hwpx/**` 변경 0
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level`
- 실패 시: 실제 샘플 분포가 다르면 어느 para_shape_id 에서 다른지 NEEDS에 적고 PARTIAL(기대값은 계약 — orchestrator가 §3 마지막 항목 판단). `git restore --source=HEAD -- src/hwp2md/hwp5/`, 새 파일 quarantine. 최대 3.

### Stage 4 — 합성 HWPX 생성기: header.xml paraPr/heading/styles·바이트 불변 고정
- 목적: 같은 제목 fixture를 HWPX zip으로 만들 수 있게 하고(header.xml에 OUTLINE paraPr, `hp:p`에 `paraPrIDRef`), 제목 없는 입력의 바이트 불변을 sha256으로 고정한다.
- 담당: implementer(opus, 40회) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 3
- 입력: §4.6-A(요소·속성), §4.8, §4.9, §4.10-D; 읽을 파일 `tests/synth_hwpx.py`, `tests/unit/test_synth_hwpx.py`, `tests/synth_hwp5.py`(import 이름)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/synth_hwpx.py`
  - `tests/unit/test_synth_hwpx.py`
- 산출물: §4.8 함수(`p_attrs`, `header_xml`, `para_pr_xml`, `style_xml`, 확장된 `paragraph_xml`/`cell_xml`/`section_xml`/`hwpx_entries`), 단위 테스트 7개(기존 9개 불변)
- 검증 (로그 `logs/s4-test.log`): §4.16-A → ruff OK, mypy `15 source files`, unit `154 passed` 이상(145 + 6 + parametrize 3), failed 0. `-k "sha256 or unchanged"` pass, 기존 `test_entries_exact`·`test_deterministic_bytes` pass
  - reviewer: `src/**`·`synth_hwp5.py` 변경 0, `SynthHeading`/`has_heading` 재정의 없음(import), outline False 헤더 문자열이 §4.8과 글자 그대로, `P_ATTRS` 상수 유지
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes`
- 실패 시: `git restore --source=HEAD -- tests/synth_hwpx.py tests/unit/test_synth_hwpx.py`. 최대 3.

### Stage 5 — HWPX header.xml 파서와 본문·리더 연결·두 포맷 동일성
- 목적: `header.xml`의 OUTLINE paraPr를 읽어 `hp:p/@paraPrIDRef`로 단락 수준을 정하고, 세 제목 fixture에서 hwp5와 Markdown·카운트가 같음을 단위 테스트로 고정한다.
- 담당: implementer(opus, 40회) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 4
- 입력: §4.6, §4.7, §4.9, §4.10-E/F, §4.11(HWPX 표); 읽을 파일 `src/hwp2md/hwpx/reader.py`, `src/hwp2md/hwpx/body.py`, `src/hwp2md/hwp5/docinfo.py`(대칭 구조 참고), `tests/unit/test_hwpx_body.py`(기존 기대 유지), `tests/unit/test_cross_format.py`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/hwpx/header.py`
  - `src/hwp2md/hwpx/reader.py`
  - `src/hwp2md/hwpx/body.py`
  - `tests/unit/test_hwpx_header.py`
  - `tests/unit/test_cross_format.py`
- 산출물: §4.6-B 공개 API, §4.7 시그니처, 단위 테스트 10 + 2개
- 검증 (로그 `logs/s5-test.log`): §4.16-A → ruff OK, mypy `Success: no issues found in 16 source files`, unit `170 passed` 이상(154 + 9 + parametrize 3 + 4), failed 0.
  - `cd /Users/illi/illy-projects/hwp2md && uv run python -c "from pathlib import Path; from hwp2md.blocks import Paragraph; from hwp2md.hwpx.reader import read_blocks
for f in sorted(Path('tests/fixtures/hwpx').glob('*.hwpx')):
    b = read_blocks(f); print(sum(isinstance(x, Paragraph) and x.level == 0 for x in b), sum(isinstance(x, Paragraph) and x.level > 0 for x in b))"` → `1 0`, `80 0`, `32 0`
  - `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e -q` → `21 passed`
  - reviewer: `header.py`가 `reader.py`를 import 하지 않음(순환 방지), `_make_parser()` 옵션 3개가 §4.6과 글자 그대로, `hp:switch` 폴백(`pp.iter(HH_HEADING)`) 존재, `_cell_text` 가 수준을 전달하지 않음, `hwp5/**` 변경 0
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s5] hwpx: header.xml OUTLINE paraPr -> Paragraph.level, cross-format parity`
- 실패 시: `git restore --source=HEAD -- src/hwp2md/hwpx/ tests/unit/test_cross_format.py`, 새 파일 quarantine. 최대 3.

### Stage 6 — 결정 기록·README·fixtures README 갱신
- 목적: 제목 판정 근거·수준 clamp·CLI 표기 결정 3건을 기록하고 사용자 문서를 현재 지원 범위에 맞춘다.
- 담당: implementer(opus, 도구 호출 15회 이내) → reviewer(sonnet) (runner 생략: 문서 변경. scribe는 `.ai/` 밖을 쓰지 못한다)
- 병렬 가능: 아니오 · 선행: Stage 5
- 입력: §4.14, §4.15, 현재 `docs/decisions.md`, `README.md`, `tests/fixtures/README.md`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `docs/decisions.md`
  - `README.md`
  - `tests/fixtures/README.md`
- 산출물: decisions 11건(기존 8 + 3), README 38행 교체, fixtures README 2행 보강 + 1문단 추가
- 검증:
  - `cd /Users/illi/illy-projects/hwp2md && grep -c '^## 2026-10-22' docs/decisions.md` → `11`; `tail -1 docs/decisions.md | grep -c '^\`\`\`'` → `0`(울타리 복사 사고 방지)
  - `cd /Users/illi/illy-projects/hwp2md && grep -c '제목 계층(개요 1~7수준' README.md` → `1`; `grep -c '이미지·각주는 진행 중' README.md` → `1`
  - `cd /Users/illi/illy-projects/hwp2md && grep -c 'REAL_EXPECTED' tests/fixtures/README.md` → `3`; `grep -c '^\`\`\`' tests/fixtures/README.md` → `0`
  - `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → `sanitize-check: OK`
  - `cd /Users/illi/illy-projects/hwp2md && git diff --stat` → 3개 파일만
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s6] docs: heading decisions (para shape source, clamp, CLI), README`
- 실패 시: `git checkout -- docs/decisions.md README.md tests/fixtures/README.md`. RETRY 최대 2.

### Stage 7 — CLI 2행 ` · 제목 K개` (cli.py 전용 단계)
- 목적: 제목이 1개 이상일 때 CLI 2행에 ` · 제목 K개`를 덧붙인다.
- 담당: orchestrator 직접 (3줄 변경, 10줄 이하 규칙. 서브에이전트 없음)
- 병렬 가능: 아니오 · 선행: Stage 6
- 입력: §4.12
- 쓰기 범위: `src/hwp2md/cli.py` 49행 `print(...)` 1줄 → §4.12의 3줄
- 검증: §4.16-C → 기대 2행 5개와 `exit=0` 5회, `.md` 5개가 `screenshots/`에 복사됨. `cd /Users/illi/illy-projects/hwp2md && uv run ruff check src && uv run ruff format --check src && uv run mypy src` → OK. `uv run pytest tests/e2e -q` → **`20 passed, 1 failed`** (`test_real_fixture_converts[form200005063113.hwp]` 의 `$` 정규식 — 예정된 실패, Stage 8 §4.13-A에서 해소. 다른 실패가 있으면 BLOCKED)
- 완료 조건: PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s7] cli: append heading count when present`
- 실패 시: `git checkout -- src/hwp2md/cli.py`

### Stage 8 — E2E 테스트 작성·실행 (필수, 생략 불가)
- 목적: 사용자 관점(콘솔 스크립트 실행)으로 합성 제목 fixture 두 포맷·경계값·표 안 제목·회귀·비압축·실패 경로·실제 샘플 5개를 검증하고 증거 `.md`를 남긴다.
- 담당: test-writer(sonnet, 30회) → runner(haiku, 10회)
- 병렬 가능: 아니오 · 선행: Stage 7
- 입력: §4.13(A·B), §4.9(import 이름), §4.11 기대 숫자, `tests/e2e/conftest.py`(fixture 이름, 수정 금지), `tests/e2e/test_cli_hwpx.py`(스타일·`_copy_evidence` 패턴)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/e2e/test_cli_heading.py`
  - `tests/e2e/test_cli_convert.py` (79행 정규식 1곳만)
  - `tests/e2e/test_cli_hwpx.py` (32행 정규식 1곳만)
- 산출물: E2E 케이스 8개(실제 샘플 parametrize 5 포함 12건), 증거 `heading_hwp5.md`, `heading_hwpx.md`, `heading_edge.md`, `heading_cell.md`, 실제 샘플 `.md` 5개
- 검증 (runner, §4.16-D, 로그 `logs/e2e.log`): `33 passed`, `exit=0`, failed 0, error 0, skipped 0. `cd /Users/illi/illy-projects/hwp2md && uv run ruff check tests && uv run ruff format --check tests` → OK. `git diff --stat` → 3개 파일, 기존 2개 파일은 각 `1 +, 1 -`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-heading-levels][s8] e2e: heading levels both formats, edge cases, real samples`
- 실패 시: orchestrator가 e2e-standard 표로 분류 — 테스트 파일 안 오류(import·fixture·정규식) → test-writer 재호출(2회 실패 시 opus), 구현 오류(assert·exit code·실제 샘플 숫자) → implementer(opus)에게 해당 Stage 쓰기 범위로 재호출. 같은 오류 2회 → BLOCKED.

### Stage 9 — 리뷰·결과 기록
- 목적: 전체 diff와 증거 `.md`를 사람이 보듯 검토하고 RESULT·STATE를 쓴다.
- 담당: reviewer(sonnet, 15회) → scribe(haiku, 10회)
- 병렬 가능: 아니오 · 선행: Stage 8
- 입력: reviewer — `git diff ce0a3f5654351f1d89e11075f8c05fed4a5be775 --stat`, `.ai/tasks/T-20261022-heading-levels/screenshots/heading_hwp5.md`·`heading_hwpx.md`·`form200005063113.md`(Read로 직접 열기), §2 표; scribe — PROGRESS.md 전체, reviewer 보고, §2 표
- 쓰기 범위: reviewer 없음(읽기 전용) · scribe `/Users/illi/illy-projects/hwp2md/.ai/tasks/T-20261022-heading-levels/RESULT.md`, `/Users/illi/illy-projects/hwp2md/.ai/STATE.md`
- 검증: reviewer 보고에 §2 S1~S10 각각 PASS/FAIL과 근거 명령 출력 1줄; `heading_hwp5.md`와 `heading_hwpx.md` 바이트 동일(`cmp`), `form200005063113.md`에 `# `로 시작하는 줄 6개·`###### ` 4개를 눈으로 확인; 쓰기 범위 밖 변경 파일 0(`cli.py`·`pyproject.toml`·`uv.lock`·`__init__.py` 변경은 Stage 7의 cli.py 3줄만). scribe: RESULT.md가 record-standard 절(요약·성공 기준 표·못 한 것·결정 사항·후속 제안) 포함, STATE.md 20줄 이내·상태 `DONE` 대기 표기.
- 완료 조건: RESULT.md 존재 + 커밋 `[T-20261022-heading-levels][s9] docs: RESULT`
- 실패 시: reviewer FAIL 항목은 해당 Stage 담당에게 재호출(RETRY). 2회 실패 → BLOCKED.

## 6. 병렬 실행 맵
```
Stage 1(블록·렌더) → Stage 2(hwp5 생성기) → Stage 3(hwp5 DocInfo 파서) → Stage 4(hwpx 생성기) → Stage 5(hwpx header 파서)
  → Stage 6(문서) → Stage 7(cli.py, orchestrator) → Stage 8(E2E) → Stage 9(리뷰·RESULT)
```
병렬 묶음 없음(전부 순차, worktree 격리 불필요). 이유: 단계마다 앞 단계의 타입·fixture 상수를 import 하고, 단계 하나가 10분 안쪽이다. runner·reviewer는 읽기 전용이므로 같은 트리에서 implementer 뒤에 바로 띄운다.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [x] 7-1 블록 모델: **(a) `Paragraph.level: int = 0` 필드 추가** vs (b) 별도 `Heading(text, level)` 블록. 기본값 (a) — 기존 `Paragraph("x")` 호출·동등 비교·테스트 113개가 무수정으로 유효하고, HWP 모델(개요 속성이 붙은 단락)과 맞다. (b)를 택하면 `Block` Union·render·convert·`__init__` export·`read_paragraphs` 의미가 바뀌어 §4.2·§4.9·§4.10 재작성(planner 재호출).
- [x] 7-2 판정 근거: **문단 모양(PARA_SHAPE 비트 / paraPr heading OUTLINE)만** vs STYLE 레코드·`hh:style` 이름("개요 N") 또는 참조를 보조로. 기본값 문단 모양만 — 실제 샘플 5개 모두 본문 style_id가 0이고 개요 정보는 문단 모양에만 있다. 보조 판정을 원하면 "para_shape_id가 범위 밖일 때만 style → para_shape_id 추적"으로 한정해 Stage 3·5에 20줄 추가(§4.3-G·§4.6-B에 `style_id` 인자 추가, 계약 변경).
- [x] 7-3 개요 7수준(및 HWPX hp10 변형의 8·9수준) 처리: **`######`로 clamp** vs 본문(level 0). 기본값 clamp. 영향: 실제 샘플 1 기대값 — clamp `(100, 8, 18)`, 본문 처리 시 `(104, 8, 14)`이며 §4.11·§4.13·§4.9 EDGE fixture 기대값을 함께 바꿔야 한다.
- [x] 7-4 CLI 2행: **제목 0개면 생략, 1개 이상이면 ` · 제목 K개` 덧붙임(기존 E2E 정규식 2줄 수정)** vs (B) 항상 ` · 제목 K개` 표기(기존 E2E 문자열 단언 6곳 + 정규식 2곳 = 8줄 수정: `test_cli_convert.py` 26·79행, `test_cli_table.py` 38·51행, `test_cli_hwpx.py` 32·49·62·75행) vs (C) CLI 불변(`heading_count`는 라이브러리 결과에만, 기존 테스트 0줄 수정, Stage 7 생략). 기본값 (A). 또한 제목은 **단락 수에서 분리**(단락 N + 제목 K = Paragraph 블록 수). 제목을 단락 수에 포함하길 원하면 §4.2-D·§4.11 숫자 변경.
- [x] 7-5 긴 제목·표 안 제목: **길이 제한 없음, 표 셀 안 개요 단락은 셀 텍스트로만** 기본값. 대안: N자(예 100자) 초과는 본문 처리 — 실제 샘플 1의 제목은 최대 63자라 기대값 불변이지만 규칙이 하나 늘어 §4.2-B에 추가.
- [x] 7-6 HWPX `hp:switch` 안의 heading: **`hp:case` 쪽(최신 앱 기준, OUTLINE level 7·8 → clamp 6)** vs `hp:default` 쪽(NONE → 본문). 기본값 case. 실제 샘플에서는 참조하는 단락이 없어 기대값 불변.
- [x] 7-7 실제 양성 샘플: HWP 5.0은 샘플 1(제목 18개)로 양성 검증이 되지만 HWPX 실제 샘플 3개는 전부 제목 0개. **합성 HWPX fixture로 양성 검증, 실제 HWPX 양성 샘플은 사용자가 `tests/fixtures/hwpx/`에 넣고 `REAL_EXPECTED`에 기대값 추가(fixtures README 안내)** 기본값. 샘플을 지금 넣어 주면 planner가 §4.11에 기대값을 추가한다.
- 결정 (2026-10-22, 사용자): 7개 모두 기본값. 승인됨. 실행은 사용자가 "계속해"라고 할 때 시작(한도 초기화 대기).

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 공공 양식의 "개요" 번호 단락(예: 계약 조항)이 제목으로 렌더되어 사용자가 기대한 "제목"과 다를 수 있다 (실제 샘플 1의 18개가 이 경우일 수 있음) | 중 | 이번 태스크는 HWP의 개요 속성을 그대로 Markdown 제목으로 옮기는 것이 목표(vision `## 1. 사업 개요`). RESULT "알려진 문제"에 적고, 번호 리스트 렌더 태스크에서 머리 모양 2·3과 함께 재검토 |
| HWPX 실제 양성 샘플 부재 — header.xml 파서가 실제 파일에서 OUTLINE 단락을 잡는지 끝까지 확인 못 함 | 높 | header.xml 구조·`hp:switch` 변형은 3개 샘플에서 확인했고 paraPr/heading 파싱(`para_levels`)은 실제 header.xml 3개로 단위 검증 가능(Stage 5 reviewer가 `parse_header` 를 실제 header.xml에 돌려 §4.11 `OUTLINE paraPr id → level` 열과 비교). §7-7 |
| 생성기 기본 경로 바이트 변경(sha256 깨짐) — 기존 `(g)` sha 테스트·E2E `test_truncated_section_exit_1` 영향 | 중 | `build_docinfo(outline=False)`·`build_paragraph` 기본 인자 유지, §4.5-F·§4.8-E 9개 해시로 Stage 2·4에서 즉시 검출 |
| `_parse_paragraph` 4-튜플 변경 시 `_parse_table`의 언패킹 누락 → 런타임 오류 | 중 | mypy strict가 튜플 길이 불일치를 잡는다. 기존 `test_hwp5_body.py` 14개가 그대로 통과해야 함 |
| DocInfo 레코드 중 `size == 0xFFF` 확장 헤더(큰 레코드)가 실제 파일에 있어 파싱 실패 | 낮 | `iter_records`가 이미 확장 size를 지원. 실제 샘플 2개 DocInfo가 예외 없이 끝까지 파싱됨(조사 완료) |
| `#`로 시작하는 본문 단락이 있으면 E2E의 제목 줄 수 비교가 틀어진다 | 낮 | 실제 샘플 5개 현재 출력에 `#` 시작 줄 0 확인. 합성 fixture에는 없음. 본문 `#` 이스케이프는 OUT(후속) |
| Stage 7 뒤 Stage 8 전까지 기존 E2E 1건 예정 실패 상태 | 확정 | Stage 7 검증에 명시(`20 passed, 1 failed`), Stage 8이 정규식 2줄로 해소. 그 사이 커밋 메시지에 "e2e regex pending s8" 메모 |
| 긴 표(셀 2226개) 샘플에서 header.xml 204 KB 추가 파싱으로 시간 증가 | 낮 | lxml 파싱 수십 ms. E2E 전체 5분 상한에 여유(현재 1초 미만) |

## 9. 예상 비용
- 예상 단계 수: 9 · 서브에이전트 호출: 약 18회(재시도 제외, 상한 24회) — implementer 6(S1~S6) · runner 6(S1~S5, S8) · reviewer 6(S1~S6, S9) · test-writer 1(S8) · scribe 1(S9); S7은 orchestrator 직접 · 주 모델: opus 6 / sonnet 8 / haiku 7 (실행 수 기준 약 30/40/30)
- 단위 테스트 신규 약 57건(113 → 170 이상, 성공 기준 S3는 보수적으로 143 이상), E2E 신규 12건(21 → 33)
