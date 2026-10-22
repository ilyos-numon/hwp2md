# PLAN — T-20261022-table-markdown HWP 5.0 표(HWPTAG_TABLE) → Markdown 표 변환

> 작성: planner(fable) · 2026-10-22 13:50 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: DONE)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> 모든 Bash는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. 아래 경로는 전부 이 디렉터리 기준 상대경로다. BASE=`6e24c12` (브랜치 `ai/T-20261022-table-markdown`).
> HWP 버전은 hex(`0x05000006`)로만 적는다. 점으로 이어진 4마디 버전 표기는 플랜·코드·문서 어디에도 쓰지 않는다 (익명화 검사의 IPv4 패턴에 걸림).

## 0. 한 줄 목표
사용자가 `uv run hwp2md input.hwp -o out/` 한 줄로 HWP 5.0 문서의 표를 본문 단락 흐름 속 제자리에 Markdown 표(`| a | b |` + `|---|---|`)로 받을 수 있고, 병합 셀은 빈 칸으로, 셀 안의 여러 단락은 `<br>`로 이어진 한 칸으로 받을 수 있다. CLI 2행은 `  단락 N개 · 표 M개`로 표 개수를 함께 보여준다.

## 1. 범위
### 포함 (IN)
- 블록 모델 `src/hwp2md/blocks.py`: `Paragraph(text)`, `Table(rows)`, `Block = Paragraph | Table`.
- 표 레코드 파서 `src/hwp2md/hwp5/body.py`: 레코드 level + `CTRL_HEADER(ctrl_id "tbl ")` → `TABLE` → `LIST_HEADER`(셀) → 셀 단락 구조를 §4.3 알고리즘대로 조립해 `list[Block]`을 만든다. 병합 셀(col_span/row_span > 1)은 원 셀 자리에 텍스트, 덮인 칸은 `""`.
- `src/hwp2md/hwp5/records.py`에 상수 `CTRL_ID_TABLE` 1개 추가.
- `src/hwp2md/hwp5/reader.py`에 `read_blocks(path) -> list[Block]` 추가. 기존 `read_paragraphs`는 호환 래퍼로 유지.
- `src/hwp2md/render.py`에 `render_blocks(blocks) -> str` 추가(Markdown 표 규칙 §4.5). 기존 `render_markdown(paragraphs: Sequence[str])`은 호환 래퍼로 유지(동작 불변).
- `src/hwp2md/convert.py`: `read_blocks` + `render_blocks` 사용, `ConvertResult.table_count` 추가.
- `src/hwp2md/__init__.py`: `Block`, `Paragraph`, `Table` export.
- `src/hwp2md/cli.py`: 2행을 `  단락 N개 · 표 M개`로 (orchestrator 전용 파일 → 전용 단계 Stage 4).
- 합성 fixture 생성기 `tests/synth_hwp5.py` 확장: `SynthTable`/`SynthCell`, 단락 목록 원소로 `SynthTable`을 넣으면 자리표시자 단락 + 표 컨트롤 레코드를 생성 (§4.4). 기존 `write_hwp5(path, paragraphs, *, properties)` 호출 방식은 그대로 동작.
- 단위 테스트 추가(`tests/unit/test_hwp5_body.py` 신규, `tests/unit/test_synth_hwp5.py`·`tests/unit/test_convert.py` 케이스 추가), E2E 추가(`tests/e2e/test_cli_table.py` 신규, `tests/e2e/test_cli_convert.py` 2곳 수정 §4.7).
- 문서: `docs/decisions.md` 결정 2건(§4.8), `README.md` "현재 지원" 1줄 갱신(§4.9).
- 기존 단위 35개·E2E 7개는 회귀 없이 통과한다. 유일한 의도적 변경은 E2E `test_convert_synthetic_success`의 2행 기대 문자열(§4.7-1, CLI 형식 변경에 따른 갱신)과 `test_real_fixture_converts` 강화(§4.7-2).

### 제외 (OUT) — 절대 건드리지 않는다
- 이미지(BinData) 추출, 각주·미주, 제목 계층(heading), 목차, HWPX, `--split`/`--meta`.
- 셀 서식(배경·테두리·정렬·너비·높이), 세로 쓰기, 표 캡션 레코드 해석, 표 속성(attr) 해석.
- 중첩 표의 구조 재현(§7-4 기본값: 부모 셀 텍스트로 평탄화), 병합 셀 복원 이상의 레이아웃 재현.
- `DocInfo` 해석(글꼴·스타일), 암호화·배포용 문서 해독, 깨진 OLE의 `OSError` 매핑(전 태스크 알려진 문제, 별도).
- README "하지 않는 것"(역변환 md→hwp, 글꼴·색상 서식 재현) — 제안조차 금지.
- 공개 샘플 다운로드(네트워크), 실제 샘플 커밋(`tests/fixtures/**`는 gitignore), `tests/fixtures/README.md` 수정.
- `pyproject.toml` 변경(의존성 추가 없음), `uv.lock`, GitHub Actions, LICENSE.
- `doc/my_info/`(워크스페이스 읽기 전용 원본) 접근.

### 건드리면 안 되는 파일/디렉토리
- 서브에이전트 전 단계: `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.gitignore`, `pyproject.toml`, `uv.lock`, `.claude/**`, `docs/vision.md`, `tests/fixtures/**`(읽기만), `src/hwp2md/errors.py`, `src/hwp2md/py.typed`.
- `src/hwp2md/cli.py`는 Stage 4에서만 쓴다 (프로젝트 orchestrator 전용 파일 추가분).
- `src/hwp2md/hwp5/records.py`는 Stage 1에서만 쓰고 §4.2의 상수 1줄 외 변경 금지 (`iter_records`, `decode_para_text`, 기존 상수 불변).
- scribe는 `.ai/` 밖 파일을 쓰지 않는다 (문서 변경은 Stage 5 implementer).

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| S1 | 합성 표 fixture → Markdown 표, 위치 보존 | `D=$(mktemp -d) && PYTHONPATH=tests uv run python -c "from pathlib import Path; from synth_hwp5 import write_hwp5, FIXTURE_ITEMS_WITH_TABLE; write_hwp5(Path('$D/table.hwp'), FIXTURE_ITEMS_WITH_TABLE)" && uv run hwp2md $D/table.hwp -o $D/out; echo "exit=$?"; cat $D/out/table.md` | stdout 2행 `  단락 2개 · 표 1개`, `exit=0`, 파일 내용이 §4.6 `EXPECTED_MARKDOWN_WITH_TABLE`과 글자 단위로 같음 |
| S2 | 병합 셀·이스케이프·`<br>` | `D=$(mktemp -d) && PYTHONPATH=tests uv run python -c "from pathlib import Path; from synth_hwp5 import write_hwp5, FIXTURE_ITEMS_MERGED; write_hwp5(Path('$D/merged.hwp'), FIXTURE_ITEMS_MERGED)" && uv run hwp2md $D/merged.hwp -o $D/out; echo "exit=$?"; cat $D/out/merged.md` | 2행 `  단락 1개 · 표 1개`, `exit=0`, 내용 == §4.6 `EXPECTED_MARKDOWN_MERGED` |
| S3 | 표 없는 기존 fixture 결과 불변 | `D=$(mktemp -d) && PYTHONPATH=tests uv run python -c "from pathlib import Path; from synth_hwp5 import write_hwp5, FIXTURE_PARAGRAPHS; write_hwp5(Path('$D/sample.hwp'), FIXTURE_PARAGRAPHS)" && uv run hwp2md $D/sample.hwp -o $D/out; echo "exit=$?"; cat $D/out/sample.md` | 2행 `  단락 3개 · 표 0개`, `exit=0`, 내용 == `테스트 문서 제목\n\n본문 단락 1\n\n본문 단락 2\n` |
| S4 | 실제 샘플(표 8개)에서 표 추출 | `D=$(mktemp -d) && uv run hwp2md tests/fixtures/form200005063113.hwp -o $D; echo "exit=$?"; grep -cE '^\|(---\|)+$' $D/form200005063113.md; grep -c '| 표준근로계약서 |' $D/form200005063113.md` | 2행이 정규식 `^  단락 \d+개 · 표 8개$`, `exit=0`, 첫 grep `8`, 둘째 grep `1` 이상 (샘플 파일이 없으면 이 행은 "N/A — 샘플 없음"으로 RESULT에 기록) |
| S5 | 표 없는 실제 샘플 회귀 없음 | `D=$(mktemp -d) && uv run hwp2md tests/fixtures/form210001070268.hwp -o $D; echo "exit=$?"; grep -cE '^\|' $D/form210001070268.md` | 2행이 정규식 `^  단락 \d+개 · 표 0개$`, `exit=0`, grep `0` (샘플 없으면 N/A) |
| S6 | E2E 테스트 통과 | `uv run pytest tests/e2e -q` | `failed` 0, `error` 0, passed 11 (실제 샘플 2개 있을 때; 없으면 passed 9 + skipped 1) |
| S7 | 단위 테스트·린트·타입 통과(회귀 없음) | `uv run pytest tests/unit -q && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | 네 명령 모두 종료 코드 0, unit passed ≥ 55 (기존 35 전부 포함), mypy `Success: no issues found` |
| S8 | 익명화 검사 통과 | `/Users/illi/illy-projects/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` | `sanitize-check: OK`, 종료 코드 0 |
| S9 | 결정 기록 | `grep -c "^## 2026-10-22" docs/decisions.md` | `5` (기존 3 + 신규 2) |
| S10 | README 현재 지원 갱신 | `grep -c "Markdown 표" README.md` | `1` 이상 |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 오류(같은 예외 메시지 또는 같은 assert)로 수정 2회 실패.
- 동일 단계 재시도 3회 초과 (RETRY 3번째까지 허용, 4번째 시도 금지).
- 단계 하나에 20분 또는 도구 호출 상한 초과: implementer 40회(Stage 5는 15회; 에이전트 하드 상한 60회에서 PARTIAL 반환), test-writer 40회, reviewer 25회, runner 15회, scribe 15회.
- §4 계약(타입·시그니처·바이트 레이아웃·기대 Markdown 문자열)을 바꿔야만 테스트가 통과 → BLOCKED (계약 변경은 planner 재호출).
- `pyproject.toml` 변경(의존성 추가 등) 없이 진행 불가 → NEEDS 보고. orchestrator가 10줄 이하면 직접 수정, 아니면 BLOCKED.
- 실제 샘플 `form200005063113.hwp`에서 Stage 3 검증(table_count == 8)이 2회 수정 후에도 실패 → BLOCKED (§8 LIST_HEADER 레이아웃 리스크. 셀 hex를 PROGRESS에 붙여 사용자 판단).
- OUT 범위(이미지·각주·HWPX·셀 서식) 코드를 넣어야만 통과하는 상황 → BLOCKED (넣지 않는다).
- 기존 단위 테스트 35개 중 하나라도 수정·삭제·skip이 필요해지는 상황 → BLOCKED. 기존 E2E 수정은 §4.7의 2곳만 허용.
- 테스트를 skip/약화해야만 통과 → 금지. 실패로 보고.

## 4. 인터페이스 계약 (모든 단계가 이 값을 그대로 쓴다. 바꾸면 BLOCKED)

### 4.1 파일 레이아웃 (새 파일 경로는 이것만 허용)
```
src/hwp2md/blocks.py                 # Stage 1 신규
src/hwp2md/hwp5/body.py              # Stage 1 신규
src/hwp2md/hwp5/records.py           # Stage 1 (상수 1줄 추가만)
tests/unit/test_hwp5_body.py         # Stage 1 신규
tests/synth_hwp5.py                  # Stage 2
tests/unit/test_synth_hwp5.py        # Stage 2 (케이스 추가, 기존 케이스 불변)
src/hwp2md/hwp5/reader.py            # Stage 3
src/hwp2md/render.py                 # Stage 3
src/hwp2md/convert.py                # Stage 3
src/hwp2md/__init__.py               # Stage 3
tests/unit/test_convert.py           # Stage 3 (케이스 추가, 기존 케이스 불변)
src/hwp2md/cli.py                    # Stage 4 (orchestrator 전용 파일 추가분, 전용 단계)
docs/decisions.md, README.md         # Stage 5
tests/e2e/test_cli_table.py          # Stage 6 신규
tests/e2e/test_cli_convert.py        # Stage 6 (§4.7의 2곳만 수정)
```
`tests/` 아래에 `__init__.py`를 만들지 않는다. `tests/e2e/conftest.py`는 수정하지 않는다.

### 4.2 공개 API·타입 (`src/hwp2md/`)
```python
# blocks.py (신규)
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Paragraph:
    text: str                      # 비어 있지 않은 본문 단락 텍스트 (decode_para_text 결과, 줄바꿈 "\n" 포함 가능)

@dataclass(frozen=True)
class Table:
    rows: list[list[str]]          # row_count × col_count 직사각형. 셀 텍스트는 셀 단락들을 "\n"으로 join한 원문(이스케이프 전). 병합으로 덮인 칸·빈 셀은 ""
    @property
    def row_count(self) -> int: ...   # len(self.rows)
    @property
    def col_count(self) -> int: ...   # len(self.rows[0]) if self.rows else 0

Block = Paragraph | Table

# hwp5/records.py (추가 1줄. 나머지 불변)
CTRL_ID_TABLE = b"tbl "[::-1]      # == b" lbt". 파일에는 ctrl_id 4바이트가 역순으로 저장된다 (실제 샘플에서 확인: b' lbt', b'dces'(secd), b'dloc'(cold))

# hwp5/body.py (신규)
@dataclass(frozen=True)
class TableHeader:
    row_count: int                 # UINT16 @4
    col_count: int                 # UINT16 @6

@dataclass(frozen=True)
class CellHeader:
    col: int                       # UINT16 @8
    row: int                       # UINT16 @10
    col_span: int                  # UINT16 @12
    row_span: int                  # UINT16 @14

def parse_table_header(payload: bytes) -> TableHeader:
    """len(payload) < 8 → Hwp2mdError("truncated TABLE record"). 나머지 바이트(여백·행별 셀 수·테두리 ID·zone)는 읽지 않는다."""

def parse_cell_header(payload: bytes) -> CellHeader:
    """len(payload) < 16 → Hwp2mdError("truncated LIST_HEADER record"). offset 0~7(단락 수·속성·예약)은 읽지 않는다."""

def parse_blocks(records: Iterable[Record]) -> list[Block]:
    """§4.3 알고리즘. 섹션 하나의 레코드 시퀀스 → 블록 목록."""

# hwp5/reader.py (추가. 기존 함수 불변)
def read_blocks(path: Path) -> list[Block]:
    """read_sections(path) 의 각 섹션에 iter_records → parse_blocks 를 적용해 순서대로 이어 붙인다."""

def read_paragraphs(path: Path) -> list[str]:
    """호환 래퍼: [b.text for b in read_blocks(path) if isinstance(b, Paragraph)]. (본문 단락만. 표 셀 텍스트는 포함하지 않는다)"""

# render.py
def render_blocks(blocks: Sequence[Block]) -> str:
    """§4.5. 각 블록을 문자열로 바꿔 '\n\n' 으로 join, 끝에 '\n' 1개. 블록 0개면 ''. Paragraph.text 가 '' 이면 건너뛴다."""

def render_markdown(paragraphs: Sequence[str]) -> str:
    """호환 래퍼(동작 불변): render_blocks([Paragraph(p) for p in paragraphs if p])."""

# convert.py
@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int           # Paragraph 블록 수 (표 셀 단락은 세지 않는다)
    table_count: int               # Table 블록 수 (중첩 표는 평탄화되므로 세지 않는다)
    markdown: str

def convert(path: str | Path, out_dir: str | Path = ".") -> ConvertResult:
    """기존 동작 유지. blocks = read_blocks(source); markdown = render_blocks(blocks);
    paragraph_count = sum(isinstance(b, Paragraph) and bool(b.text) for b in blocks); table_count = sum(isinstance(b, Table) for b in blocks)."""

# __init__.py (Stage 3 최종 상태)
from .blocks import Block, Paragraph, Table
from .convert import ConvertResult, convert
from .errors import Hwp2mdError, NotHwpFileError, UnsupportedHwpError
__version__ = "0.1.0"
__all__ = ["Block", "ConvertResult", "Hwp2mdError", "NotHwpFileError", "Paragraph", "Table", "UnsupportedHwpError", "__version__", "convert"]
```
- `Table`은 `frozen=True`지만 `rows`가 list라 해시 불가 — 해시하지 않는다(set/dict 키 금지). 동등 비교(`==`)는 테스트에서 사용.
- mypy strict 통과 필수. `Block` 타입 별칭은 모듈 수준 `Block = Paragraph | Table` (런타임 유효).

### 4.3 레코드 → 블록 조립 알고리즘 (`parse_blocks`, 구현은 이 의사코드와 같은 동작이어야 한다)
실제 샘플(`form200005063113.hwp`, 0x05000006)에서 확인한 레코드 배열 — 표 하나:
```
PARA_HEADER  lvl0  (control_mask bit11 set)        ← 자리표시자 단락
  PARA_TEXT  lvl1  WCHAR: [11, ctrl_id 2WCHAR, 0×4, 11, 13] → decode_para_text == ""
  PARA_CHAR_SHAPE lvl1 · PARA_LINE_SEG lvl1
  CTRL_HEADER lvl1  payload[:4] == b" lbt" (44 bytes)
    TABLE       lvl2  (22~50 bytes: rows, cols …)
    LIST_HEADER lvl2  (38 bytes; 셀 1)
    PARA_HEADER lvl2 → PARA_TEXT lvl3 … (셀 1의 단락들, LIST_HEADER의 단락 수만큼)
    LIST_HEADER lvl2  (셀 2) → PARA_HEADER lvl2 …
PARA_HEADER  lvl0                                   ← 다음 본문 단락
```
규칙: 셀 단락(PARA_HEADER)은 LIST_HEADER의 **자식이 아니라 형제**(같은 level)다. "현재 셀"은 가장 최근 LIST_HEADER가 정한다.

```python
def parse_blocks(records):
    recs = list(records); blocks = []; i = 0
    while i < len(recs):
        r = recs[i]
        if r.tag_id == HWPTAG_PARA_HEADER and r.level == 0:
            text, trailing, i = _parse_paragraph(recs, i, level=0)
            if text: blocks.append(Paragraph(text))
            blocks.extend(trailing)             # 이 단락에 달린 표(들)·다른 컨트롤 안 단락(§7-5 기본값)
        else:
            i += 1                              # 최상위에 PARA_HEADER 가 아닌 레코드(없어야 정상)는 무시
    return blocks

def _parse_paragraph(recs, i, level) -> tuple[str, list[Block], int]:
    # recs[i] 는 PARA_HEADER(level). 자식은 level+1. 반환 i 는 이 단락에 속하지 않는 첫 레코드 인덱스
    i += 1; text = ""; trailing: list[Block] = []
    while i < len(recs) and recs[i].level > level:
        r = recs[i]
        if r.tag_id == HWPTAG_PARA_TEXT and r.level == level + 1:
            text = decode_para_text(r.payload); i += 1
        elif r.tag_id == HWPTAG_CTRL_HEADER and r.level == level + 1 and r.payload[:4] == CTRL_ID_TABLE:
            table, i = _parse_table(recs, i, ctrl_level=level + 1)
            if table is not None: trailing.append(table)
        elif r.tag_id == HWPTAG_CTRL_HEADER and r.level == level + 1:
            # 표가 아닌 컨트롤(구역 정의·단 정의·글상자·머리말 등). §7-5 기본값: 안쪽 단락을 그대로 흘려보낸다
            ctrl_level = r.level; i += 1
            while i < len(recs) and recs[i].level > ctrl_level:
                if recs[i].tag_id == HWPTAG_PARA_HEADER and recs[i].level == ctrl_level + 1:
                    t2, tr2, i = _parse_paragraph(recs, i, level=ctrl_level + 1)
                    if t2: trailing.append(Paragraph(t2))
                    trailing.extend(tr2)
                else:
                    i += 1
        else:
            i += 1                              # PARA_CHAR_SHAPE, PARA_LINE_SEG, 그 외 하위 레코드
    return text, trailing, i

def _parse_table(recs, i, ctrl_level) -> tuple[Table | None, int]:
    # recs[i] 는 CTRL_HEADER(tbl). TABLE/LIST_HEADER/셀 PARA_HEADER 는 모두 ctrl_level+1
    i += 1; header = None; cells: list[tuple[CellHeader, list[str]]] = []; current = None
    while i < len(recs) and recs[i].level > ctrl_level:
        r = recs[i]
        if r.tag_id == HWPTAG_TABLE and r.level == ctrl_level + 1:
            header = parse_table_header(r.payload); i += 1
        elif r.tag_id == HWPTAG_LIST_HEADER and r.level == ctrl_level + 1:
            current = (parse_cell_header(r.payload), []); cells.append(current); i += 1
        elif r.tag_id == HWPTAG_PARA_HEADER and r.level == ctrl_level + 1 and current is not None:
            text, trailing, i = _parse_paragraph(recs, i, level=ctrl_level + 1)
            if text: current[1].append(text)
            for b in trailing:                  # 셀 안의 중첩 표·컨트롤 단락 → 부모 셀 텍스트로 평탄화 (§7-4 기본값)
                if isinstance(b, Paragraph): current[1].append(b.text)
                else:
                    flat = " ".join(c for row in b.rows for c in row if c)
                    if flat: current[1].append(flat)
        else:
            i += 1
    if header is None or header.row_count == 0 or header.col_count == 0:
        return None, i                          # 표 레코드 없음·빈 표 → 블록 없음
    return Table(rows=_place_cells(header, cells)), i

def _place_cells(header, cells) -> list[list[str]]:
    rows, cols = header.row_count, header.col_count
    grid: list[list[str | None]] = [[None] * cols for _ in range(rows)]
    for cell, paras in cells:
        text = "\n".join(paras)
        r, c = cell.row, cell.col
        if not (0 <= r < len(grid) and 0 <= c < cols) or grid[r][c] is not None:
            # 좌표가 범위 밖이거나 이미 찬 자리 → 읽기 순서로 첫 빈 칸(None). 없으면 새 행을 추가해 그 첫 칸
            slot = next(((rr, cc) for rr in range(len(grid)) for cc in range(cols) if grid[rr][cc] is None), None)
            if slot is None:
                grid.append([None] * cols); slot = (len(grid) - 1, 0)
            r, c = slot
        grid[r][c] = text
        for rr in range(r, min(r + max(cell.row_span, 1), len(grid))):
            for cc in range(c, min(c + max(cell.col_span, 1), cols)):
                if (rr, cc) != (r, c) and grid[rr][cc] is None:
                    grid[rr][cc] = ""           # 병합으로 덮인 칸
    return [[x if x is not None else "" for x in row] for row in grid]
```
- 표 위치: 자리표시자 단락의 텍스트가 비어 있지 않으면 `Paragraph` 먼저, 그 뒤에 그 단락의 표(들) 순서대로. 비어 있으면 표만 낸다.
- 레코드 level 검사는 전부 `== level + 1`(직계) 또는 `> level`(하위 전체) 두 가지만 쓴다.

### 4.4 HWP 5.0 표 관련 바이트 레이아웃 (파서 읽는 위치 + 생성기 쓰는 값. 전 태스크 §4.4-A~H와 모순 없음)
**A. PARA_TEXT 안의 표 자리표시자 (확장 컨트롤 코드 11, 8 WCHAR = 16 bytes)**
`struct.pack("<H", 11) + CTRL_ID_TABLE + b"\x00" * 8 + struct.pack("<H", 11)` 그 뒤 `b"\r\x00"`(코드 13). `decode_para_text`는 코드 11에서 8 WCHAR를 건너뛰므로 결과는 `""`. nchars = 9. 자리표시자 단락의 PARA_HEADER `control_mask` = `0x00000800` (bit 11). 그 외 PARA_HEADER 필드는 전 태스크 §4.4-D와 같다.

**B. CTRL_HEADER (tag 0x47) 표 컨트롤 payload — 44 bytes (생성기 값; 파서는 `[:4]`만 읽는다)**
| offset | 크기 | 값 |
|---|---|---|
| 0 | 4 | `CTRL_ID_TABLE` (= `b" lbt"`) |
| 4 | 4 | 속성 UINT32 = 0 |
| 8 | 8 | 세로·가로 오프셋 INT32 ×2 = 0 |
| 16 | 8 | 너비·높이 UINT32 = 10000, 2000 |
| 24 | 4 | z-order INT32 = 0 |
| 28 | 8 | 바깥 여백 UINT16 ×4 = 0 |
| 36 | 4 | 인스턴스 ID UINT32 = 0 |
| 40 | 4 | 쪽 나눔 방지 UINT32 = 0 |

**C. TABLE (tag 0x4D) payload — 파서는 offset 4·6만 읽는다. 생성기 길이 = 18 + 2×rows + 4**
| offset | 크기 | 값 |
|---|---|---|
| 0 | 4 | 속성 UINT32 = `0x04000006` (실제 샘플 값) |
| 4 | 2 | 행 수 UINT16 |
| 6 | 2 | 열 수 UINT16 |
| 8 | 2 | 셀 간격 UINT16 = 0 |
| 10 | 8 | 안쪽 여백 UINT16 ×4 = 141 |
| 18 | 2×rows | 행별 셀 수 UINT16 (= 그 행에 `row == r`인 셀 개수) |
| 18+2×rows | 2 | 테두리/배경 ID UINT16 = 1 |
| 20+2×rows | 2 | 유효 zone 수 UINT16 = 0 (버전 0x05000100 이상에만 존재. 생성기 버전 0x05000300 이므로 쓴다. 실제 샘플 0x05000006 에는 없고 길이 22였다 — 파서는 이 영역을 읽지 않는다) |

**D. LIST_HEADER (tag 0x48) 표 셀 payload — 38 bytes (실제 샘플 전 셀 길이 38로 확인). 파서는 offset 8~15만 읽는다**
| offset | 크기 | 값 |
|---|---|---|
| 0 | 2 | 단락 수 UINT16 (= 셀 단락 개수) |
| 2 | 2 | 0 |
| 4 | 4 | 속성 UINT32 = `0x20` (실제 샘플 바이트 `00 00 20 00 00 00`과 같은 패턴) |
| 8 | 2 | 열 주소 col UINT16 (0부터) |
| 10 | 2 | 행 주소 row UINT16 (0부터) |
| 12 | 2 | 열 병합 col_span UINT16 (≥1) |
| 14 | 2 | 행 병합 row_span UINT16 (≥1) |
| 16 | 4 | 셀 너비 UINT32 = 5000 |
| 20 | 4 | 셀 높이 UINT32 = 1000 |
| 24 | 8 | 셀 여백 UINT16 ×4 = 141 |
| 32 | 2 | 테두리/배경 ID UINT16 = 1 |
| 34 | 4 | 텍스트 너비 UINT32 = 5000 (너비와 같은 값) |
검증 근거(실제 샘플 hex): 1×1 셀 `0100 0000 2000 0000 | 0000 0000 0100 0100` → col 0, row 0, span 1×1 · 5×6 표의 첫 셀 `… | 0000 0000 0100 0300` → row_span 3 · 같은 표 7번째 셀 `… | 0200 0100 0400 0100` → col 2, row 1, col_span 4. 열 합(1+1+4 = 6) 일치.

**E. 셀 단락**: `build_paragraph(text, last=..., level=L)` — PARA_HEADER level L, 하위 레코드 level L+1 (전 태스크 §4.4-D/E 와 같은 바이트, level만 다름). 셀의 마지막 단락만 `last=True`(bit31). 표 컨트롤의 L = 자리표시자 단락 level + 2 (최상위 표면 2).

**F. 레코드 순서(생성기 출력, 표 1개·셀 k개)**: 자리표시자 PARA_HEADER(lvl0) → PARA_TEXT(lvl1, A) → PARA_CHAR_SHAPE(lvl1) → PARA_LINE_SEG(lvl1) → CTRL_HEADER(lvl1, B) → TABLE(lvl2, C) → [LIST_HEADER(lvl2, D) → 셀 단락들(lvl2/3, E)] × k. 셀은 `cells` 순서대로(행 우선으로 정의해 둔다).

### 4.5 Markdown 표 렌더 규칙 (`render_blocks`)
- `Paragraph` → `text` 그대로 (현재 동작과 동일).
- `Table` → 줄 목록을 `"\n"`으로 join (끝 줄바꿈 없음; 블록 사이 `"\n\n"`이 표 앞뒤 빈 줄을 만든다):
  1. 헤더 행: `rows[0]` (§7-2 기본값: 첫 행을 헤더로)
  2. 구분선: `"|" + "---|" * col_count`  → 예 `|---|---|`
  3. 본문 행: `rows[1:]` 각각
- 행 한 줄 = `"| " + " | ".join(cells) + " |"`. 빈 셀이면 `|  |`(공백 2개)가 된다.
- 셀 텍스트 변환 순서: `text.replace("|", "\\|")` → `.replace("\n", "<br>")` → `.strip()`. (§7-1 기본값: 셀 내 복수 단락·줄바꿈은 `<br>`)
- `row_count == 0` 또는 `col_count == 0`인 Table은 파서가 만들지 않으므로 렌더러는 가정하지 않고 그대로 처리한다(빈 리스트면 `""` 반환 → `render_blocks`가 빈 문자열 블록을 건너뛴다).
- 블록 문자열 중 `""`인 것은 제외하고 `"\n\n"`으로 join, 끝에 `"\n"` 1개. 전부 비면 `""`.

### 4.6 합성 생성기 확장 (`tests/synth_hwp5.py`) — 기존 함수·상수는 글자 하나도 바꾸지 않는다
```python
from hwp2md.blocks import Paragraph, Table  # EXPECTED_BLOCKS_* 용 import 추가
from hwp2md.hwp5.records import CTRL_ID_TABLE, HWPTAG_CTRL_HEADER, HWPTAG_LIST_HEADER, HWPTAG_TABLE  # import 추가

@dataclass(frozen=True)
class SynthCell:
    paragraphs: tuple[str, ...]        # 셀 단락. 빈 튜플 허용(빈 셀) — 그래도 LIST_HEADER 는 쓴다 (단락 수 0, 단락 레코드 없음)
    col: int
    row: int
    col_span: int = 1
    row_span: int = 1

@dataclass(frozen=True)
class SynthTable:
    rows: int
    cols: int
    cells: tuple[SynthCell, ...]       # 행 우선 순서로 정의

Item = str | SynthTable                # 단락 목록 원소. str = 본문 단락, SynthTable = 자리표시자 단락 + 표

def build_paragraph(text: str, *, last: bool, level: int = 0) -> bytes       # level 키워드 추가(기본 0 → 기존 호출 불변). 하위 레코드는 level+1
def build_ctrl_header_table(table: SynthTable) -> bytes                      # §4.4-B 44 bytes (레코드 헤더 제외 payload)
def build_table_record(table: SynthTable) -> bytes                           # §4.4-C payload
def build_cell_header(cell: SynthCell) -> bytes                              # §4.4-D 38 bytes payload
def build_table_control(table: SynthTable, *, level: int, last: bool) -> bytes
    # §4.4-F 전체: 자리표시자 단락(level, nchars 9, control_mask 0x800, last 반영) + CTRL_HEADER(level+1) + TABLE(level+2) + [LIST_HEADER(level+2) + 셀 단락(level+2)]×k
def build_section0(items: Sequence[Item]) -> bytes                           # str → build_paragraph(level=0), SynthTable → build_table_control(level=0). 마지막 원소만 last=True
def build_hwp5(items: Sequence[Item], *, properties: int = 0x1) -> bytes
def write_hwp5(path: Path, items: Sequence[Item], *, properties: int = 0x1) -> Path   # 시그니처 타입만 Sequence[str] → Sequence[Item] 으로 넓어짐

# 공용 fixture (E2E·단위 테스트가 이 이름을 그대로 import)
FIXTURE_TABLE = SynthTable(rows=2, cols=2, cells=(
    SynthCell(("구분",), col=0, row=0), SynthCell(("내용",), col=1, row=0),
    SynthCell(("지원 규모",), col=0, row=1), SynthCell(("총 30억 원",), col=1, row=1),
))
FIXTURE_ITEMS_WITH_TABLE: list[Item] = ["표 앞 단락", FIXTURE_TABLE, "표 뒤 단락"]
EXPECTED_MARKDOWN_WITH_TABLE = "표 앞 단락\n\n| 구분 | 내용 |\n|---|---|\n| 지원 규모 | 총 30억 원 |\n\n표 뒤 단락\n"
EXPECTED_BLOCKS_WITH_TABLE = [Paragraph("표 앞 단락"), Table([["구분", "내용"], ["지원 규모", "총 30억 원"]]), Paragraph("표 뒤 단락")]

FIXTURE_TABLE_MERGED = SynthTable(rows=2, cols=3, cells=(
    SynthCell(("머리글",), col=0, row=0, col_span=3),
    SynthCell(("가",), col=0, row=1), SynthCell(("나|다",), col=1, row=1), SynthCell(("라", "마"), col=2, row=1),
))
FIXTURE_ITEMS_MERGED: list[Item] = ["제목", FIXTURE_TABLE_MERGED]
EXPECTED_MARKDOWN_MERGED = "제목\n\n| 머리글 |  |  |\n|---|---|---|\n| 가 | 나\\|다 | 라<br>마 |\n"
EXPECTED_BLOCKS_MERGED = [Paragraph("제목"), Table([["머리글", "", ""], ["가", "나|다", "라\n마"]])]
```
- `EXPECTED_MARKDOWN_MERGED`의 `\\|`는 파이썬 소스 표기이며 실제 문자열은 `나\|다`다.
- 비압축(`properties=0`) 변형도 섹션 < 4096 bytes 여야 한다(두 fixture 모두 1500 bytes 미만으로 충분).

### 4.7 E2E 계약 (`tests/e2e/`) — conftest.py 는 수정하지 않는다
**1. `tests/e2e/test_cli_convert.py` 수정 2곳 (그 외 글자 하나도 바꾸지 않는다)**
- `test_convert_synthetic_success`: `assert lines[1] == "  단락 3개"` → `assert lines[1] == "  단락 3개 · 표 0개"`.
- `test_real_fixture_converts`를 아래로 교체 (import `re`·`os`·`shutil` 기존 유지; `REAL_FIXTURE_MIN_TABLES` 모듈 상수 추가):
  ```python
  REAL_FIXTURE_MIN_TABLES = {"form200005063113.hwp": 1}   # 표가 있는 것으로 확인된 샘플만. 없는 샘플은 표 0개여도 통과

  @pytest.mark.parametrize("real_hwp", REAL_FIXTURES, ids=lambda p: p.name)
  def test_real_fixture_converts(real_hwp: Path, tmp_path: Path, run_cli: RunCli) -> None:
      out_dir = tmp_path / "out"
      result = run_cli([str(real_hwp), "-o", str(out_dir)])
      assert result.returncode == 0, result.stderr
      lines = result.stdout.split("\n")
      m = re.match(r"^  단락 (\d+)개 · 표 (\d+)개$", lines[1])
      assert m, lines[1]
      table_count = int(m.group(2))
      md = out_dir / f"{real_hwp.stem}.md"
      content = md.read_text(encoding="utf-8")
      assert len(content.strip()) > 0
      separators = [ln for ln in content.split("\n") if re.fullmatch(r"\|(---\|)+", ln)]
      assert len(separators) == table_count            # 출력된 Markdown 표 수 == CLI 가 보고한 표 수
      assert table_count >= REAL_FIXTURE_MIN_TABLES.get(real_hwp.name, 0)
      evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
      evidence_dir.mkdir(parents=True, exist_ok=True)
      shutil.copyfile(md, evidence_dir / md.name)
  ```
**2. `tests/e2e/test_cli_table.py` 신규 — 케이스 4개 (이름 고정). 모두 conftest의 `run_cli` 사용, `synth_hwp5`에서 import**
  1. `test_convert_table_success` — `write_hwp5(tmp_path/"table.hwp", FIXTURE_ITEMS_WITH_TABLE)`; 종료 0; `lines[0] == f"✓ table.hwp → {out_dir / 'table.md'}"`; `lines[1] == "  단락 2개 · 표 1개"`; 파일 내용 == `EXPECTED_MARKDOWN_WITH_TABLE`; `.md`를 `ILLY_SHOT_DIR/table.md`로 복사.
  2. `test_convert_merged_table` — `FIXTURE_ITEMS_MERGED` → `merged.hwp`; 종료 0; `lines[1] == "  단락 1개 · 표 1개"`; 내용 == `EXPECTED_MARKDOWN_MERGED`; `ILLY_SHOT_DIR/merged.md`로 복사.
  3. `test_convert_table_uncompressed_variant` — `write_hwp5(..., FIXTURE_ITEMS_WITH_TABLE, properties=0)`; 종료 0; 내용 == `EXPECTED_MARKDOWN_WITH_TABLE`.
  4. `test_truncated_section_exit_1` (실패 경로) — `section = build_section0(FIXTURE_ITEMS_WITH_TABLE); data = build_cfb({"FileHeader": build_file_header(properties=0), "DocInfo": build_docinfo(), "BodyText/Section0": section[:-10]})`를 `broken.hwp`에 저장; 종료 1; stderr에 `truncated record` 포함; `out/broken.md` 미생성.
- `pytest.skip(`/`pytest.mark.skip` 문자열을 코드에 쓰지 않는다(gate가 약화로 본다). 실제 샘플이 없으면 빈 parametrize로 skipped 1.
- 기대 총계: 실제 샘플 2개 있을 때 `11 passed` (기존 5 + 실제 2 + 신규 4). 없을 때 `9 passed, 1 skipped`.

### 4.8 CLI 2행 형식 (Stage 4, `src/hwp2md/cli.py`) — §7-3 기본값
```
✓ {Path(input).name} → {str(Path(out_dir) / f"{stem}.md")}
  단락 {result.paragraph_count}개 · 표 {result.table_count}개
```
구분자는 ` · `(공백 + U+00B7 + 공백). 표가 0개여도 항상 출력. 종료 코드·stderr 메시지·`--version`은 전 태스크 §4.5와 동일.

### 4.9 docs/decisions.md 추가 항목 (Stage 5, 파일 끝에 그대로 추가. §7 답이 기본값과 다르면 해당 문장만 orchestrator가 승인 시 치환)
```
## 2026-10-22 블록 모델 도입: 단락·표를 Block 리스트로 추상화
- 결정: reader는 `list[str]` 대신 `list[Block]`(`Paragraph(text)` | `Table(rows)`)을 돌려주고, renderer(`render_blocks`)가 블록 종류별로 Markdown을 만든다. 표는 HWP 5.0 레코드 level과 `CTRL_HEADER(tbl)` → `TABLE` → `LIST_HEADER`(셀) → 셀 단락 순서로 조립한다. 기존 `read_paragraphs`·`render_markdown`은 호환 래퍼로 남긴다.
- 이유: README "기술 방향"(블록 단위 추상화 후 렌더러 분리). 이미지·각주 블록을 같은 리스트에 얹을 수 있고, 표가 본문 단락 흐름 안의 제자리에 놓인다.

## 2026-10-22 표 렌더: 첫 행을 헤더로, 병합 셀은 빈 칸, 셀 내 단락은 <br>
- 결정: Markdown(GFM) 표는 헤더 행이 필수이므로 표의 첫 행을 헤더로 쓴다. 병합 셀(col_span/row_span > 1)은 원 셀 자리에 텍스트를 두고 덮인 칸은 빈 칸으로 둔다. 셀 안의 여러 단락·줄바꿈은 `<br>`로 잇고 `|`는 `\|`로 이스케이프한다. 중첩 표는 부모 셀 텍스트로 평탄화(셀 텍스트를 공백으로 이어 붙임)한다. 표 셀 안 단락은 본문 단락 수에 세지 않는다.
- 이유: GFM은 rowspan/colspan을 표현할 수 없어 행·열 수를 보존하는 쪽을 택했다. 빈 칸으로 두면 열 정렬이 유지되어 RAG 청킹과 사람이 읽는 데 모두 유리하다. 중첩 표는 공공 양식에서 드물고 레이아웃 재현은 범위 밖이다.
```

### 4.10 README 변경 (Stage 5). "## 설치와 실행 (개발 중)" 절의 마지막 줄 1개만 교체
변경 전: `현재 지원: HWP 5.0 바이너리의 본문 단락 텍스트. 표·이미지·각주·HWPX는 진행 중.`
변경 후: `현재 지원: HWP 5.0 바이너리의 본문 단락 텍스트와 표(Markdown 표, 병합 셀은 빈 칸, 셀 내 단락은 <br>). 이미지·각주·HWPX는 진행 중.`

### 4.11 실제 샘플 조사 결과 (읽기 전용, planner 2026-10-22). implementer 가 추측하지 않도록 기록
| 파일 | 버전 | 레코드 수 | `tbl ` 컨트롤 | 비고 |
|---|---|---|---|---|
| `tests/fixtures/form200005063113.hwp` | 0x05000006 | 1163 | **8개** (1×1 ×5, 5×6, 8×2, 15×3) | 셀 67개, LIST_HEADER 전부 38 bytes, TABLE 22/30/36/50 bytes(zone 필드 없음). 병합 셀 다수(rowspan 3, colspan 4·3). 셀당 단락 1~6개. 중첩 표 없음. 자리표시자 PARA_TEXT = `[11, 13]`, 첫 단락은 `[2, 2, 11, 13]`(구역·단 정의 + 표). control_mask `0x0800`/`0x0804` |
| `tests/fixtures/form210001070268.hwp` | 0x05000202 | 268 | **0개** | 컨트롤은 `dces`(secd)·`dloc`(cold)만. "1." "2." "3." 은 표가 아니라 평문 단락 → 이 파일은 표 0개가 정답. 회귀 비교용 |
- 두 파일 모두 `tag 0x42 level 0` 본문 단락 아래 `PARA_TEXT level 1`. 표 셀 단락은 `PARA_HEADER level 2 / PARA_TEXT level 3`.
- `dces` CTRL_HEADER 아래에 `0x49, 0x4A, 0x4B` level 2 레코드가 있다(쪽 정의 등). §4.3의 "표가 아닌 컨트롤" 분기에서 PARA_HEADER 가 아니므로 전부 건너뛴다.

## 5. 단계 (Stage) — 전부 순차. 병렬 없음.

### Stage 1 — 블록 모델과 표 레코드 파서 (blocks.py, hwp5/body.py)
- 목적: §4.2 타입과 §4.3 알고리즘을 구현하고, 손으로 만든 `Record` 리스트로 단위 테스트한다 (파일 I/O 없음).
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §1, §4.2, §4.3, §4.4-C/D(읽는 offset), §4.11, `src/hwp2md/hwp5/records.py`, `src/hwp2md/errors.py`, `tests/unit/test_hwp5_records.py`(헬퍼 스타일 참고)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/blocks.py` (신규)
  - `src/hwp2md/hwp5/body.py` (신규)
  - `src/hwp2md/hwp5/records.py` (`CTRL_ID_TABLE` 상수 1줄 추가만)
  - `tests/unit/test_hwp5_body.py` (신규)
- 산출물: `Paragraph`, `Table`, `Block`, `TableHeader`, `CellHeader`, `parse_table_header`, `parse_cell_header`, `parse_blocks`. 단위 테스트 ≥ 10: (a) `parse_table_header`: §4.4-D 실제 hex `060000040100010000008d008d008d008d0001000100` → rows 1, cols 1; 7 bytes → `Hwp2mdError` (b) `parse_cell_header`: 실제 hex `01000000200000050000000001000100f3580000fe0a00008d008d008d008d000100f3580000` → (col 0, row 0, 1, 1); hex `010000002000000502000100040001004a750000b50b00008d008d008d008d0006004a750000` → (col 2, row 1, col_span 4, row_span 1); 15 bytes → `Hwp2mdError` (c) 레코드 시퀀스 빌더 헬퍼(`Record(tag, level, payload)` 직접 생성)로 §4.3 구조 2×2 표 → `[Paragraph("앞"), Table([["a","b"],["c","d"]]), Paragraph("뒤")]` (d) 자리표시자 텍스트가 비어 있으면 Paragraph 없이 Table만 (e) 자리표시자 텍스트가 있으면 Paragraph 다음에 Table (f) 셀 단락 2개 → `"첫\n둘"` 로 join, 빈 단락 제외 (g) 병합: rows 2 cols 3, 셀 (0,0,span 3×1) + (0,1),(1,1),(2,1) → `[["머리글","",""],["가","나","다"]]` (h) 좌표 범위 밖 셀 → 첫 빈 칸에 배치 (i) TABLE 레코드 없는 `tbl ` 컨트롤 → 블록 없음 (j) 표가 아닌 CTRL_HEADER(`b"dces"`) 와 그 level 2 자식들 → 무시, 본문 단락만 (k) 표가 아닌 컨트롤 안의 PARA_HEADER(level 2) 텍스트 → Paragraph 로 흘러나옴 (l) 셀 안 중첩 표 → 부모 셀 텍스트에 공백 join 으로 평탄화, 최상위 Table 수 1
- 검증: `uv run pytest tests/unit -q` → `failed` 0, passed ≥ 45 (기존 35 전부 포함) · `uv run ruff check src tests && uv run ruff format --check src tests` → 종료 0 · `uv run mypy src` → `Success: no issues found`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser`
- 실패 시: 같은 테스트 2회 연속 실패 → BLOCKED. 도구 호출 상한 40.

### Stage 2 — 합성 생성기 표 확장 (synth_hwp5.py)
- 목적: §4.4-A/B/C/D/E/F 바이트와 §4.6 API로 표가 든 HWP 5.0 fixture를 만들고, Stage 1 파서로 왕복(round-trip)됨을 단위 테스트로 고정한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 1
- 입력: §4.4 전체, §4.6, §4.3(왕복 검증용), `tests/synth_hwp5.py`, `tests/unit/test_synth_hwp5.py`, `src/hwp2md/hwp5/body.py`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/synth_hwp5.py`
  - `tests/unit/test_synth_hwp5.py` (기존 8 케이스 불변, 추가만)
- 산출물: §4.6 전부. 단위 테스트 ≥ 6 추가: (a) `write_hwp5(FIXTURE_ITEMS_WITH_TABLE)` → `read_sections` → `iter_records` → `parse_blocks` == `EXPECTED_BLOCKS_WITH_TABLE` (b) `FIXTURE_ITEMS_MERGED` 왕복 == `EXPECTED_BLOCKS_MERGED` (c) 레코드 검사: CTRL_HEADER 1개, `payload[:4] == b" lbt"`, len 44; TABLE 1개 level 2, len == 18 + 2×2 + 4 == 26; LIST_HEADER 4개 level 2 len 38 (d) 자리표시자 PARA_TEXT: 첫 WCHAR 11, `decode_para_text == ""`, PARA_HEADER nchars 9, control_mask 0x800 (e) 셀 PARA_HEADER level 2 / PARA_TEXT level 3, 셀 마지막 단락만 bit31 (f) `properties=0` 비압축 변형도 (a)와 같은 블록 (g) 기존 `write_hwp5(path, FIXTURE_PARAGRAPHS)` 바이트가 변경 전과 동일 — `build_section0(FIXTURE_PARAGRAPHS)`에 CTRL_HEADER/TABLE/LIST_HEADER 레코드 0개
- 검증: `uv run pytest tests/unit -q` → `failed` 0, passed ≥ 51 · `uv run ruff check src tests && uv run ruff format --check src tests` → 종료 0 · `uv run mypy src` → 종료 0 (src 불변)
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-table-markdown][s2] test: synthetic HWP 5.0 table fixtures (tbl ctrl, TABLE, LIST_HEADER cells)`
- 실패 시: 왕복 테스트가 파서 버그를 드러내면 NEEDS에 레코드 hex를 적고 PARTIAL (Stage 1 쓰기 범위 재호출은 orchestrator가 결정). 같은 오류 2회 → BLOCKED. 상한 40.

### Stage 3 — reader·render·convert 연결 (read_blocks, render_blocks, table_count)
- 목적: 파일 → 블록 → Markdown 표까지 라이브러리 API로 연결하고 실제 샘플에서 표 8개/0개가 나오는지 확인한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 2
- 입력: §4.2(reader, render, convert, `__init__`), §4.5, §4.6 fixture 이름, §4.11, `src/hwp2md/hwp5/reader.py`, `src/hwp2md/render.py`, `src/hwp2md/convert.py`, `src/hwp2md/__init__.py`, `tests/unit/test_convert.py`
- 쓰기 범위 (이 파일들만 수정):
  - `src/hwp2md/hwp5/reader.py`
  - `src/hwp2md/render.py`
  - `src/hwp2md/convert.py`
  - `src/hwp2md/__init__.py`
  - `tests/unit/test_convert.py` (기존 12 케이스 불변, 추가만)
- 산출물: `read_blocks`, `render_blocks`, `ConvertResult.table_count`, export. 단위 테스트 ≥ 6 추가: (a) `convert(write_hwp5(FIXTURE_ITEMS_WITH_TABLE))` → `markdown == EXPECTED_MARKDOWN_WITH_TABLE`, `paragraph_count == 2`, `table_count == 1`, 파일 내용 일치 (b) `FIXTURE_ITEMS_MERGED` → `EXPECTED_MARKDOWN_MERGED`, `paragraph_count 1`, `table_count 1` (c) 기존 `FIXTURE_PARAGRAPHS` → `table_count == 0`, `markdown == EXPECTED_MARKDOWN` (d) `render_blocks([])== ""`, `render_blocks([Paragraph(""), Paragraph("a")]) == "a\n"` (e) `render_blocks([Table([["x|y", "l1\nl2"]])]) == "| x\\|y | l1<br>l2 |\n|---|---|\n"` (f) `render_markdown(["a","","b"]) == "a\n\nb\n"` 유지 확인(기존 테스트와 중복이어도 됨) (g) `read_blocks(FIXTURE_ITEMS_WITH_TABLE 파일) == EXPECTED_BLOCKS_WITH_TABLE`, `read_paragraphs == ["표 앞 단락", "표 뒤 단락"]` (h) `hwp2md.__all__`에 `"Block"`, `"Paragraph"`, `"Table"` 포함
- 검증: `uv run pytest tests/unit -q` → `failed` 0, passed ≥ 57 · `uv run ruff check src tests && uv run ruff format --check src tests` → 종료 0 · `uv run mypy src` → `Success: no issues found` · 실제 샘플(파일이 있을 때만; 없으면 "샘플 없음"으로 보고): `D=$(mktemp -d) && uv run python -c "from hwp2md import convert; r=convert('tests/fixtures/form200005063113.hwp','$D'); print(r.paragraph_count, r.table_count); import re; print(sum(bool(re.fullmatch(r'\\|(---\\|)+', l)) for l in r.markdown.splitlines()))"` → 첫 줄 둘째 숫자 `8`, 둘째 줄 `8` · `D=$(mktemp -d) && uv run python -c "from hwp2md import convert; r=convert('tests/fixtures/form210001070268.hwp','$D'); print(r.table_count, '|' in r.markdown)"` → `0 False`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-table-markdown][s3] feat: read_blocks/render_blocks, markdown tables, ConvertResult.table_count`
- 실패 시: 실제 샘플 table_count ≠ 8 이면 §4.11 대로 레코드를 덤프해 원인(level 판정/LIST_HEADER offset)을 NOTES에 적는다. 같은 오류 2회 → BLOCKED(§3). 상한 40.

### Stage 4 — CLI 2행에 표 개수 (cli.py 전용 단계)
- 목적: §4.8 형식으로 `  단락 N개 · 표 M개`를 출력한다. orchestrator 전용 파일이므로 이 파일만 갖는 단계.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 3
- 입력: §4.8, `src/hwp2md/cli.py`, `src/hwp2md/convert.py`
- 쓰기 범위 (이 파일만 수정):
  - `src/hwp2md/cli.py`
- 산출물: 2행 f-string 1줄 변경 (`print(f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개")`)
- 검증 (implementer 직접, 기대값 글자 단위 대조): §2 S1 명령 → 2행 `  단락 2개 · 표 1개`, `exit=0`, 내용 == `EXPECTED_MARKDOWN_WITH_TABLE` · §2 S2 명령 → `  단락 1개 · 표 1개` · §2 S3 명령 → `  단락 3개 · 표 0개` · §2 S4·S5 명령(샘플 있을 때) → `표 8개` / `표 0개` · `uv run hwp2md /nonexistent/x.hwp -o $(mktemp -d); echo "exit=$?"` → `exit=2` · `uv run pytest tests/unit -q && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` → 종료 0 · `uv run pytest tests/e2e -q 2>&1 | tail -3` → failed 가 **정확히 1 + 실제 샘플 수**(현재 샘플 2개 → `3 failed, 4 passed`)이고 실패 이름이 `test_convert_synthetic_success`(구 2행 문자열)와 `test_real_fixture_converts[...]`(구 정규식 `^  단락 \d+개$`)만이어야 한다 — 둘 다 Stage 6에서 §4.7-1로 갱신 예정. 다른 이름이 실패하면 이 단계 실패.
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-table-markdown][s4] feat(cli): report table count on summary line`
- 실패 시: 같은 오류 2회 → BLOCKED. 상한 20.

### Stage 5 — 결정 기록·README 현재 지원 갱신
- 목적: §4.9를 `docs/decisions.md`에, §4.10을 `README.md`에 그대로 옮긴다.
- 담당: implementer(opus) (scribe는 `.ai/` 밖을 쓰지 못한다 — 전 태스크 변경 이력 참조)
- 병렬 가능: 아니오 · 선행: Stage 4
- 입력: §4.9, §4.10, `docs/decisions.md`, `README.md`
- 쓰기 범위 (이 파일들만 수정):
  - `docs/decisions.md` (파일 끝에 §4.9 2개 항목 추가. 기존 내용 불변)
  - `README.md` (§4.10 1줄 교체. 다른 줄은 글자 하나도 바꾸지 않는다)
- 산출물: 결정 2건, README 1줄
- 검증: `grep -c "^## 2026-10-22" docs/decisions.md` → `5` · `grep -c "Markdown 표" README.md` → `1` 이상 · `grep -c "하지 않는 것" README.md` → `1` · `git diff --stat -- README.md` → `1 insertion(+), 1 deletion(-)` · `/Users/illi/illy-projects/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → `sanitize-check: OK`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-table-markdown][s5] docs: block model and table rendering decisions, README support line`
- 실패 시: 재시도 최대 3회. 상한 15.

### Stage 6 — E2E 테스트 작성·실행 (필수, 생략 불가)
- 목적: §4.7 대로 실제 `hwp2md` 콘솔 스크립트를 subprocess로 실행하는 표 E2E 4케이스를 새 파일에 쓰고, 기존 파일의 2곳을 갱신한 뒤 runner가 전체를 실행해 로그·증거를 남긴다.
- 담당: test-writer(sonnet) → runner(haiku)
- 병렬 가능: 아니오 · 선행: Stage 5
- 입력: §4.6(fixture 이름·기대 문자열), §4.7, §4.8, `tests/e2e/conftest.py`(읽기만), `tests/e2e/test_cli_convert.py`, `tests/synth_hwp5.py`(import 만), `/Users/illi/illy-projects/docs/policies/e2e-standard.md`
- 쓰기 범위 (test-writer; 이 파일들만):
  - `tests/e2e/test_cli_table.py` (신규)
  - `tests/e2e/test_cli_convert.py` (§4.7-1 두 곳만)
- 산출물: §4.7 케이스 4개 + 기존 파일 2곳 갱신
- 검증 (test-writer): `uv run pytest tests/e2e -q` → `failed` 0, `error` 0, passed 11 (샘플 없으면 9 passed, 1 skipped) · `uv run ruff check tests && uv run ruff format --check tests` → 종료 0 · `grep -cE "pytest\.skip\(|pytest\.mark\.skip" tests/e2e/*.py` → `0` · `git diff --stat -- tests/e2e/test_cli_convert.py` → 변경 줄이 §4.7-1 범위 안(삭제 ≤ 12줄)
- 실행 (runner, Bash 1회, 도구 timeout 파라미터 600000. `timeout` 명령은 쓰지 않는다 — macOS에 없음):
  ```bash
  cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-table-markdown; mkdir -p $T/logs $T/screenshots
  [ -f $T/logs/e2e.log ] && mv $T/logs/e2e.log $T/logs/e2e.prev.log
  ILLY_SHOT_DIR=$T/screenshots uv run pytest tests/e2e -q > $T/logs/e2e.log 2>&1; echo "exit=$?" >> $T/logs/e2e.log
  tail -3 $T/logs/e2e.log; ls -la $T/screenshots; echo "--- table.md"; cat $T/screenshots/table.md; echo "--- merged.md"; cat $T/screenshots/merged.md; echo "--- real"; grep -cE '^\|(---\|)+$' $T/screenshots/form200005063113.md 2>/dev/null || echo "no real sample"
  ```
  기대: `exit=0`, `11 passed`(샘플 없으면 `9 passed, 1 skipped`), `table.md` == `EXPECTED_MARKDOWN_WITH_TABLE`, `merged.md` == `EXPECTED_MARKDOWN_MERGED`, 실제 샘플 구분선 수 `8`
- 완료 조건: e2e.log 마지막 줄 `exit=0` + 증거 3개(`table.md`, `merged.md`, 샘플 있으면 `form200005063113.md`) + PROGRESS 기록 + 커밋 `[T-20261022-table-markdown][s6] test(e2e): markdown table conversion, merged cells, truncated input`
- 실패 시: 로그 증상으로 분류(e2e-standard 표) — 테스트 파일 오류면 test-writer 재호출(2회 실패 → opus), 구현 오류면 implementer를 해당 Stage 쓰기 범위로 재호출. 같은 실패 2회 → BLOCKED. test-writer 상한 40, runner 상한 15.

### Stage 7 — 리뷰·결과 기록
- 목적: diff와 Markdown 증거를 직접 보고 §2 성공 기준 10개를 판정하고 RESULT.md를 쓴다.
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: Stage 6
- 입력(reviewer): `git diff 6e24c12...HEAD --stat`, `git diff 6e24c12...HEAD -- src tests docs README.md`, `.ai/tasks/T-20261022-table-markdown/logs/e2e.log`, `.ai/tasks/T-20261022-table-markdown/screenshots/table.md`·`merged.md`·`form200005063113.md`(Read로 직접 열어 §4.6 기대 문자열과 글자 단위 대조, 실제 샘플은 표 8개가 `|---|` 구분선과 함께 보이고 `| 표준근로계약서 |` 1×1 표가 있는지 눈으로 확인), §1 OUT 검사 `grep -rniE "lxml|hwpx|footnote|BinData" src/` → 매치 없음, §4 계약 준수 검사 `grep -n "def render_markdown\|def read_paragraphs\|def render_blocks\|def read_blocks\|table_count" src/hwp2md/*.py src/hwp2md/hwp5/*.py` → 5개 이름 모두 존재, 기존 테스트 불변 검사 `git diff 6e24c12...HEAD -- tests/unit/test_hwp5_records.py` → 빈 출력, `git diff 6e24c12...HEAD -- tests/unit/test_convert.py tests/unit/test_synth_hwp5.py | grep -c '^-[^-]'` → `0`(삭제 줄 없음), `git diff 6e24c12...HEAD -- tests/e2e/conftest.py` → 빈 출력
- 쓰기 범위 (reviewer): 없음(읽기 전용) · (scribe): `.ai/tasks/T-20261022-table-markdown/RESULT.md`
- 산출물: `RESULT.md` (성공 기준 S1~S10 표: 각 행에 실제 실행 결과 값, reviewer 지적 사항, §7 결정 적용 여부, 실제 샘플 2개의 단락/표 수)
- 검증: `test -s .ai/tasks/T-20261022-table-markdown/RESULT.md && grep -c "^| S" .ai/tasks/T-20261022-table-markdown/RESULT.md` → `10` 이상 · `/Users/illi/illy-projects/scripts/gate.sh -C /Users/illi/illy-projects/hwp2md` → `GATE PASS`
- 완료 조건: `GATE PASS` + 커밋 `[T-20261022-table-markdown][s7] docs: RESULT` + orchestrator가 STATE.md 갱신(scribe 재작성)
- 실패 시: reviewer가 FAIL 판정한 기준이 있으면 해당 Stage 담당을 그 Stage 쓰기 범위로 재호출(최대 2회), 이후 BLOCKED. reviewer 상한 25, scribe 상한 15.

## 6. 병렬 실행 맵
```
Stage 1(blocks·body 파서) → Stage 2(합성 표 fixture) → Stage 3(reader·render·convert) → Stage 4(cli.py 전용)
  → Stage 5(decisions·README) → Stage 6(E2E: test-writer → runner) → Stage 7(리뷰 → RESULT)
```
병렬 묶음 없음. reader/render/convert/synth가 연쇄 의존이라 전 단계 순차. worktree 격리 불필요. 쓰기 범위 교집합: Stage 1·2·3·4·5·6 서로 없음(§4.1 표로 대조 — `records.py`는 Stage 1만, `synth_hwp5.py`는 Stage 2만, `cli.py`는 Stage 4만, `test_cli_convert.py`는 Stage 6만).

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [x] 1. 셀 안에 단락이 여러 개일 때 합치는 방식: **기본값 `<br>`로 잇기** (GitHub·대부분 렌더러가 표 안 `<br>`를 줄바꿈으로 표시). 대안: 공백 한 칸으로 잇기(순수 텍스트 유지, 줄 구분 상실) — 선택 시 §4.5 `replace("\n", "<br>")` → `replace("\n", " ")`, §4.6 `EXPECTED_MARKDOWN_MERGED`의 `라<br>마` → `라 마`, Stage 3 (e) 기대값, §4.9 둘째 항목 문구 변경.
- [x] 2. 표의 첫 행 처리: **기본값 첫 행을 Markdown 헤더 행으로** (GFM 표는 헤더 필수. 공공 양식 표는 대개 첫 행이 항목명). 대안: 빈 헤더 행(`|  |  |`)을 넣고 모든 행을 본문으로 — 선택 시 §4.5 1번 규칙과 §4.6 두 기대 문자열, §4.9 둘째 항목 변경.
- [x] 3. CLI 2행에 표 개수 표기: **기본값 항상 `  단락 N개 · 표 M개`** (표 0개여도 출력. vision.md 시나리오 1의 `제목 12개 · 표 4개 · 이미지 3개` 형태로 확장 가능). 대안: 표가 1개 이상일 때만 ` · 표 M개` 덧붙임 — 선택 시 §4.7-1 첫 수정(`표 0개`) 불필요, §4.7-2 정규식을 `^  단락 (\d+)개( · 표 (\d+)개)?$`로, §2 S3·S5 기대 2행에서 ` · 표 0개` 제거.
- [x] 4. 중첩 표(표 안의 표): **기본값 부모 셀 텍스트로 평탄화** (중첩 표의 셀 텍스트를 공백으로 이어 부모 셀의 단락 하나로). 대안: 중첩 표를 무시(텍스트 유실) — 선택 시 §4.3 `_parse_table`의 `for b in trailing` 블록에서 Table 분기 삭제. (실제 샘플 2개에는 중첩 표가 없어 결과 차이 없음)
- [x] 5. 표가 아닌 컨트롤(글상자·머리말/꼬리말 등) 안의 단락: **기본값 본문 단락으로 흘려보냄** (이전 버전과 같이 텍스트 유실 없음. 자리표시자 단락 바로 뒤 위치). 대안: 버림(본문만 깨끗하게, 머리말 반복 제거) — 선택 시 §4.3 `_parse_paragraph`의 "표가 아닌 컨트롤" 분기를 `i += 1`만 남기고 삭제, Stage 1 (k) 테스트 기대를 "무시"로. (실제 샘플 2개는 해당 컨트롤에 단락이 없어 결과 차이 없음)
- 결정 (2026-10-22, 사용자): 5개 모두 기본값으로 진행. 승인됨.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 다른 버전(0x05000202 이상)의 실제 파일에서 LIST_HEADER 셀 필드 offset이 8이 아님 | 저 | §4.4-D는 0x05000006 샘플 67셀로 확정했고 널리 쓰이는 파서들도 같은 offset을 쓴다. 범위 밖 좌표는 `_place_cells` 첫 빈 칸 fallback으로 텍스트 유실 없이 처리. 표 있는 신버전 샘플이 들어오면 `test_real_fixture_converts`의 구분선 수 == 보고 수 검사가 잡는다 |
| 셀 PARA_HEADER가 LIST_HEADER의 형제(같은 level)라는 구조를 implementer가 자식으로 오해 | 중 | §4.3 의사코드에 명시, Stage 1 (c) 테스트와 Stage 2 왕복 테스트가 즉시 잡는다 |
| 기존 E2E `test_convert_synthetic_success`가 Stage 4~5 사이에 실패 상태 | 확실 | 의도된 1건. Stage 4 검증에 "정확히 1 failed" 로 명시, Stage 6 §4.7-1에서 갱신. gate는 최종 e2e.log만 본다 |
| 합성 fixture의 비압축 섹션이 4096 bytes 초과 → `build_cfb` ValueError | 저 | 두 fixture 모두 1500 bytes 미만. 넘으면 셀 텍스트를 줄이지 말고 BLOCKED(계약 변경) |
| `Table` frozen dataclass + list 필드 → 해시 시 TypeError | 저 | §4.2 메모: 해시하지 않는다. mypy는 통과 |
| 실제 샘플이 머신에 없어 S4·S5 미검증 | 저(현재 2개 존재) | RESULT에 "N/A — 샘플 없음"으로 정직하게 기록. 합성 fixture 기준은 S1~S3로 보장 |
| 익명화 패턴: 셀 텍스트·실제 샘플 내용(회사명 자리표시자 `○○○`, 계약 문구)을 플랜·테스트·RESULT에 인용 | 중 | 플랜은 중립 셀 텍스트(`표준근로계약서` 1×1 표 제목)만 인용. RESULT·PROGRESS에 실제 샘플 본문을 붙이지 않는다. 버전은 hex만 |
| 표 자리표시자 단락에 본문 텍스트가 함께 있는 문서에서 표가 그 단락 뒤로 이동 | 중 | 단락 단위 위치 보존이 이번 범위(§4.3 규칙). RESULT 알려진 문제에 기록 |

## 9. 예상 비용
- 예상 단계 수: 7 · 서브에이전트 호출: 9회 (implementer 5, test-writer 1, runner 1, reviewer 1, scribe 1) · 주 모델: opus 55% / sonnet 25% / haiku 20%
