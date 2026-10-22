# PLAN — T-20261022-hwpx-reader HWPX(zip/XML) 입력 지원: 본문 단락·표 → 같은 Markdown

> 작성: planner(fable) · 2026-10-22 14:55 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> 모든 Bash는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. 아래 경로는 전부 이 디렉터리 기준 상대경로다. BASE=`e13ae706b1f56e8d4cb4460e6cb6e2f38e0c21dc` (브랜치 `ai/T-20261022-hwpx-reader`, main과 동일).
> 버전 문자열은 점 3개짜리(IPv4 패턴)로 쓰지 않는다. lxml·lxml-stubs의 구체 버전 번호는 플랜·코드·문서 어디에도 적지 않는다(`lxml>=5`처럼 하한만).
> 실제 샘플의 본문 내용은 인용하지 않는다. 숫자(요소 수·표 수)만 쓴다. XML 네임스페이스 URI는 §4 코드 블록의 상수로만 적는다.

## 0. 한 줄 목표
사용자가 `uv run hwp2md input.hwpx -o out/` (또는 HWPX 내용인데 확장자가 `.hwp`인 파일) 한 줄로, HWP 5.0과 똑같은 규칙의 Markdown(본문 단락 + Markdown 표, 병합 셀 빈 칸, 셀 내 단락 `<br>`)과 같은 CLI 2행 `  단락 N개 · 표 M개`를 받을 수 있다. 포맷은 확장자가 아니라 파일 내용으로 판별된다.

## 1. 범위
### 포함 (IN)
- 포맷 감지 `src/hwp2md/detect.py`: `detect_format(path) -> "hwp5" | "hwpx"` (OLE 시그니처 → hwp5, zip + `mimetype`==`application/hwp+zip` 또는 `Contents/section0.xml` 존재 → hwpx, 그 외 `NotHwpFileError`). §4.2.
- HWPX 리더 `src/hwp2md/hwpx/reader.py`: zip에서 `Contents/section<N>.xml`을 N 오름차순으로 읽어 lxml 보안 파서로 파싱, `read_blocks(path) -> list[Block]`. 섹션 XML 50MB 상한. §4.3.
- 요소 → 블록 매핑 `src/hwp2md/hwpx/body.py`: `hp:p`/`hp:run`/`hp:t`(+인라인 `hp:tab`, `hp:lineBreak`) → `Paragraph`, `hp:tbl`/`hp:tr`/`hp:tc`/`hp:cellAddr`/`hp:cellSpan`/`hp:subList` → `Table`(그리드 배치·병합·중첩 평탄화, HWP 5.0 쪽과 같은 규칙). §4.4.
- `src/hwp2md/convert.py`: `read_blocks(path)` 디스패처 추가(감지 → 포맷별 리더), `convert()`는 그것을 호출. `ConvertResult`·CLI 출력 불변. `src/hwp2md/__init__.py`에 `detect_format`, `DocFormat` export. §4.5.
- 의존성: 런타임 `lxml>=5`, dev `lxml-stubs` (orchestrator 전용 Stage 1). §4.12.
- 합성 HWPX 생성기 `tests/synth_hwpx.py`(zip + 최소 XML 6개 엔트리, `synth_hwp5`의 `SynthTable`/`SynthCell`/fixture 상수 재사용) + 단위 테스트 4개 파일 신규(`test_hwpx_body.py`, `test_hwpx_reader.py`, `test_synth_hwpx.py`, `test_detect.py`, `test_cross_format.py`). §4.6·§4.7.
- E2E `tests/e2e/test_cli_hwpx.py` 신규(합성 성공 3 + 확장자 위장 1 + 포맷 교차 1 + 실패 2 + 실제 샘플 3). §4.8.
- 실제 샘플 3개를 `tests/fixtures/unsupported/hwpx/` → `tests/fixtures/hwpx/`로 이동(orchestrator, `mv`; gitignore 대상이라 git 변경 없음) + `tests/fixtures/README.md` 갱신. §7-5.
- 문서: `docs/decisions.md` 3건 추가(§4.9), `README.md` "현재 지원"·실행 예시 갱신(§4.10).

### 제외 (OUT) — 절대 건드리지 않는다
- 이미지(`hp:pic`, `BinData/`), 각주·미주(`hp:footNote`/`hp:endNote`) 본문 반영, 제목 계층(`header.xml` 스타일), `--split`/`--meta`.
- 머리말·꼬리말·쪽번호·도형(`hp:ctrl`, `hp:rect`, `hp:line`, `hp:container`, `hp:equation`) 텍스트 추출 — 이번 태스크는 **무시**(§7-3 기본값).
- 암호화·배포용 HWPX 판정, `content.hpf` spine 기반 섹션 탐색(섹션 파일명 glob으로 충분), `settings.xml`·`Preview/` 읽기.
- HWP 5.0 리더(`src/hwp2md/hwp5/**`)·`render.py`·`blocks.py`·`errors.py` 변경. 두 포맷의 결과 차이는 §8에 적고 통일은 후속 태스크.
- CLI 인자·출력 형식 변경(에러 문구 변경은 §7-2를 택했을 때만 Stage 4b).
- HWP 3.0 지원, `uv.lock` 수동 편집, lxml 외 XML 라이브러리(defusedxml 등) 추가.

### 건드리면 안 되는 파일/디렉토리
- `src/hwp2md/hwp5/**`, `src/hwp2md/render.py`, `src/hwp2md/blocks.py`, `src/hwp2md/errors.py`
- `src/hwp2md/cli.py` (orchestrator 전용. Stage 4b에서만, 그 단계만의 쓰기 범위)
- `pyproject.toml`, `uv.lock`, `CLAUDE.md`, `.gitignore`, `.claude/**`, `.ai/STATE.md`(scribe·orchestrator만), `.ai/tasks/*/PLAN.md`
- `tests/e2e/conftest.py`, `tests/e2e/test_cli_table.py`, `tests/synth_hwp5.py`, `tests/unit/test_hwp5_body.py`, `tests/unit/test_hwp5_records.py`, `tests/unit/test_synth_hwp5.py`, `tests/unit/test_convert.py`
- `tests/e2e/test_cli_convert.py` (§7-2 변경을 택한 경우 58행 1곳만 Stage 6에서 수정)
- `docs/vision.md`, `../doc/my_info/**`, `tests/fixtures/**` 내용(이동만)

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| S1 | 합성 HWPX(단락만) 변환 | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k synthetic_success` | pass. CLI 1행 `✓ sample.hwpx → <out>/sample.md`, 2행 `  단락 3개 · 표 0개`, 파일 내용 == `synth_hwp5.EXPECTED_MARKDOWN` |
| S2 | 합성 HWPX 표·병합 셀 변환 | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k "table_success or merged_table"` | 2 passed. 2행 각각 `  단락 2개 · 표 1개`, `  단락 1개 · 표 1개`, 내용 == `EXPECTED_MARKDOWN_WITH_TABLE` / `EXPECTED_MARKDOWN_MERGED` |
| S3 | `.hwp` 확장자의 HWPX 내용 변환 | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k hwp_extension` | pass. exit 0, `disguised.md` 내용 == `EXPECTED_MARKDOWN` |
| S4 | 같은 내용의 HWP 5.0·HWPX가 같은 Markdown | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k same_markdown` + `uv run pytest tests/unit/test_cross_format.py -q` | pass. 두 `.md` 바이트 동일, CLI 2행 동일 (fixture 3종) |
| S5 | zip이지만 HWPX 아님 → exit 3, 깨진 섹션 XML → exit 1 | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k "not_hwpx or malformed"` | 2 passed. stderr 각각 `not an HWP 5.0 file:`(§7-2 기본값) / `malformed section XML` 포함, `.md` 미생성 |
| S6 | 실제 HWPX 샘플 3개 변환 | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k real_hwpx` | 3 passed. exit 0, 2행 == §4.11 기대값 `(1,1)`, `(80,31)`, `(32,8)`, Markdown 구분선 수 == 표 수 |
| S7 | E2E 전체 통과 (기존 11 + 신규 10) | `uv run pytest tests/e2e -q` | `21 passed`, failed 0, error 0 |
| S8 | 기존 테스트 회귀 없음 + 신규 단위 | `uv run pytest tests/unit -q` | 기존 64개 전부 pass + 신규 ≥ 30 → 합계 ≥ 94 passed, failed 0 |
| S9 | 린트·포맷·타입 | `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | ruff `All checks passed!`, format 변경 파일 0, mypy `Success: no issues found in 14 source files` |
| S10 | 보안 파서 | `uv run pytest tests/unit/test_hwpx_reader.py -q -k entity` | 2 passed (외부 엔티티 미해석, 내부 엔티티 미확장, 예외 없음) |
| S11 | 익명화 검사 | `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` | `sanitize-check: OK` |
| S12 | 결정 기록·문서 | `grep -c '^## 2026-10-22' docs/decisions.md` · `grep -c 'HWPX' README.md` · `grep -c 'hwpx/' tests/fixtures/README.md` | `8` (기존 5 + 신규 3) · `≥ 3` · `≥ 1` |

UI가 없으므로 스크린샷 대신 생성된 `.md`를 `ILLY_SHOT_DIR`(`.ai/tasks/T-20261022-hwpx-reader/screenshots/`)에 복사한다. reviewer는 그 `.md`(합성 3개 + 실제 샘플 3개)를 직접 열어 표 구분선·병합 빈 칸을 눈으로 확인한다.

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 오류(같은 예외 메시지 또는 같은 assert)로 수정 2회 실패.
- 동일 단계 재시도 3회 초과 (RETRY 3번째까지 허용, 4번째 시도 금지).
- 단계 하나에 20분 또는 도구 호출 상한 초과: implementer 40회(Stage 5 문서는 15회), test-writer 40회, reviewer 25회, runner 15회, scribe 15회. 에이전트 하드 상한 60회에서 PARTIAL 반환.
- §4 계약(시그니처·네임스페이스 상수·매핑 규칙·XML 템플릿·기대 Markdown·§4.11 기대 숫자)을 바꿔야만 테스트가 통과 → BLOCKED (계약 변경은 planner 재호출). 단 §4.11 실제 샘플 기대 숫자가 ±0이 아니면 implementer는 실제 출력 숫자와 차이 원인(어느 `hp:p`가 달라졌는지 인덱스)을 NEEDS에 적는다.
- `pyproject.toml`·`uv.lock`·`cli.py` 변경 없이 진행 불가 → NEEDS 보고 → orchestrator가 Stage 1/4b 범위 안이면 직접, 아니면 BLOCKED.
- `uv add "lxml>=5"` 또는 `uv add --dev lxml-stubs`가 실패(네트워크·휠 없음) → BLOCKED (사용자 결정: 재시도 또는 §7-1 대안).
- mypy strict가 `lxml-stubs`로 2회 수정 후에도 실패하고 원인이 스텁 쪽(시그니처 누락) → NEEDS로 §7-1 대안 (b) 전환 요청. orchestrator가 `uv remove --dev lxml-stubs && uv add --dev types-lxml` 후 재실행 1회. 그래도 실패 → BLOCKED.
- 실제 샘플 E2E(S6)가 2회 수정 후에도 §4.11 숫자와 다름 → BLOCKED (실제 출력 2행과 `.md`를 PROGRESS에 붙여 사용자 판단).
- 기존 단위 64개·E2E 11개 중 하나라도 수정·삭제·skip이 필요해지는 상황 → BLOCKED. 예외: §7-2 변경 선택 시 `test_cli_convert.py` 58행 문자열 1곳.
- 테스트를 skip/약화해야만 통과 → 금지. 실패로 보고.

## 4. 인터페이스 계약 (모든 단계가 이 값을 그대로 쓴다. 바꾸면 BLOCKED)

### 4.1 패키지 레이아웃 (새 파일 경로는 이것만 허용)
```
pyproject.toml, uv.lock                  # Stage 1 (orchestrator: uv add)
tests/fixtures/hwpx/*.hwpx               # Stage 1 (orchestrator: mv. gitignore 대상)
src/hwp2md/hwpx/__init__.py              # Stage 2 (docstring 1줄)
src/hwp2md/hwpx/reader.py                # Stage 2
src/hwp2md/hwpx/body.py                  # Stage 2
tests/unit/test_hwpx_body.py             # Stage 2
tests/synth_hwpx.py                      # Stage 3
tests/unit/test_synth_hwpx.py            # Stage 3
tests/unit/test_hwpx_reader.py           # Stage 3
src/hwp2md/detect.py                     # Stage 4
src/hwp2md/convert.py                    # Stage 4 (수정)
src/hwp2md/__init__.py                   # Stage 4 (export 추가)
tests/unit/test_detect.py                # Stage 4
tests/unit/test_cross_format.py          # Stage 4
src/hwp2md/cli.py                        # Stage 4b (조건부, orchestrator 직접)
docs/decisions.md, README.md, tests/fixtures/README.md   # Stage 5
tests/e2e/test_cli_hwpx.py               # Stage 6
tests/e2e/test_cli_convert.py            # Stage 6 (조건부 §7-2, 58행 1곳만)
.ai/tasks/T-20261022-hwpx-reader/RESULT.md, .ai/STATE.md   # Stage 7 (scribe)
```
`tests/` 아래에 `__init__.py`를 만들지 않는다. `pyproject.toml`의 `pythonpath = ["tests"]`로 `import synth_hwpx`가 된다.

### 4.2 포맷 감지 (`src/hwp2md/detect.py`)
```python
"""Detect the container format of an input file by content (never by extension)."""
from __future__ import annotations
import zipfile
from pathlib import Path
from typing import Literal
import olefile
from .errors import NotHwpFileError
from .hwpx.reader import HWPX_MIMETYPE, HWPX_SECTION0

DocFormat = Literal["hwp5", "hwpx"]

def detect_format(path: Path) -> DocFormat:
    """판정 순서 (첫 번째로 맞는 것):
    1. olefile.isOleFile(str(path)) → "hwp5"   (FileHeader 검사는 hwp5 리더가 한다)
    2. zipfile.is_zipfile(path) → ZipFile 열기(zipfile.BadZipFile → NotHwpFileError(f"corrupt zip archive: {path}")).
       names = zf.namelist().
       a. "mimetype" in names 이고 zf.getinfo("mimetype").file_size <= 256 이고 zf.read("mimetype").strip() == HWPX_MIMETYPE → "hwpx"
       b. 아니면 HWPX_SECTION0 in names → "hwpx"
       c. 아니면 NotHwpFileError(f"zip archive is not an HWPX package: {path}")
    3. 그 외(빈 파일·텍스트·HWP 3.0 등) → NotHwpFileError(f"not an HWP 5.0 or HWPX file: {path}")
    확장자(.hwp/.hwpx)는 어떤 경우에도 보지 않는다."""
```

### 4.3 HWPX 리더 공개 API (`src/hwp2md/hwpx/reader.py`)
```python
"""HWPX (OWPML zip package) reader: section XML files -> blocks."""
from __future__ import annotations
import re
import zipfile
from pathlib import Path
from lxml import etree
from ..blocks import Block
from ..errors import Hwp2mdError, NotHwpFileError
from .body import parse_section

HWPX_MIMETYPE = b"application/hwp+zip"
HWPX_SECTION0 = "Contents/section0.xml"
NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"   # 실제 샘플 3개의 루트 요소 xmlns:hp 에서 확인
NS_HS = "http://www.hancom.co.kr/hwpml/2011/section"     # 실제 샘플 3개의 루트 요소 xmlns:hs 에서 확인
HS_SEC = f"{{{NS_HS}}}sec"                                # 섹션 XML 루트 요소 (실제 샘플 3개 모두 hs:sec)
MAX_SECTION_BYTES = 50 * 1024 * 1024                      # zip 엔트리 file_size 상한 (해제 후 크기)
_SECTION_NAME = re.compile(r"^Contents/section(\d+)\.xml$")

def make_parser() -> etree.XMLParser:
    """항상 이 옵션으로만 만든다 (XXE·엔티티 폭발 방어): etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False).
    다른 인자는 기본값. 호출마다 새 인스턴스."""

def section_names(zf: zipfile.ZipFile) -> list[str]:
    """_SECTION_NAME 에 맞는 엔트리를 N(정수) 오름차순으로. [section0, section1, section2, section10] 순서(문자열 정렬 금지).
    HWPX_SECTION0 이 없으면 NotHwpFileError(f"{HWPX_SECTION0} missing")."""

def read_sections(path: Path) -> list[bytes]:
    """zipfile.ZipFile(path) (BadZipFile → NotHwpFileError(f"not a zip archive: {path}")). section_names 순서로 읽는다.
    엔트리의 getinfo(name).file_size > MAX_SECTION_BYTES 이면 읽기 전에 Hwp2mdError(f"section XML too large: {name} ({size} bytes)")."""

def parse_section_xml(data: bytes) -> etree._Element:
    """etree.fromstring(data, make_parser()). bytes 만 받는다(str 은 인코딩 선언 때문에 lxml 이 거부).
    etree.XMLSyntaxError → Hwp2mdError(f"malformed section XML: {exc}").
    root.tag != HS_SEC → Hwp2mdError(f"unexpected root element: {root.tag}")."""

def read_blocks(path: Path) -> list[Block]:
    """[parse_section(parse_section_xml(data)) for data in read_sections(path)] 를 순서대로 이어 붙인다."""
```
- `lxml-stubs` 기준 타입: `etree._Element`, `etree.XMLParser`, `etree.XMLSyntaxError`. `_Element.text`/`.tail`/`.get()`은 `str | None`.
- 중요한 함정: 주석·처리 명령·미해석 엔티티 노드(`_Comment`, `_ProcessingInstruction`, `_Entity`)는 `.tag`가 **문자열이 아니다**(함수 객체). 자식을 순회할 때 반드시 `isinstance(child.tag, str)`로 걸러야 하고, 걸러낸 노드의 `.tail` 텍스트는 유지한다(§4.4 `text_of_t`).
- `src/hwp2md/hwpx/__init__.py` 내용: `"""HWPX (OWPML zip/XML) format readers."""` 1줄.

### 4.4 요소 → 블록 매핑 (`src/hwp2md/hwpx/body.py`) — 구현은 이 의사코드와 같은 동작이어야 한다
```python
"""OWPML section tree -> blocks (paragraphs and tables)."""
from __future__ import annotations
from dataclasses import dataclass
from lxml import etree
from ..blocks import Block, Paragraph, Table

NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"    # reader.py 와 같은 값 (순환 import 방지를 위해 여기도 정의. 단위 테스트가 동일성 확인)
HP_P = f"{{{NS_HP}}}p"; HP_RUN = f"{{{NS_HP}}}run"; HP_T = f"{{{NS_HP}}}t"; HP_TBL = f"{{{NS_HP}}}tbl"
HP_TR = f"{{{NS_HP}}}tr"; HP_TC = f"{{{NS_HP}}}tc"; HP_SUBLIST = f"{{{NS_HP}}}subList"
HP_CELL_ADDR = f"{{{NS_HP}}}cellAddr"; HP_CELL_SPAN = f"{{{NS_HP}}}cellSpan"
# hp:t 의 자식 인라인 요소 → 텍스트. 키는 완전한 태그명. 없는 태그(markpenBegin/End, titleMark, insertBegin/End, deleteBegin/End, fieldBegin/End 등)는 "" (뒤따르는 tail 텍스트는 유지)
INLINE_TEXT: dict[str, str] = {
    f"{{{NS_HP}}}tab": " ",          # HWP 5.0 코드 9 와 동일
    f"{{{NS_HP}}}lineBreak": "\n",   # HWP 5.0 코드 10 과 동일 (§7-4 기본값)
    f"{{{NS_HP}}}nbSpace": " ",      # 코드 30
    f"{{{NS_HP}}}fwSpace": " ",      # 코드 31
    f"{{{NS_HP}}}hypen": "-",        # 코드 24 (OWPML 요소명 철자가 hypen 이다)
}

@dataclass(frozen=True)
class CellSpec:
    row: int          # cellAddr rowAddr. 없으면 tr 인덱스
    col: int          # cellAddr colAddr. 없으면 -1 (→ 첫 빈 칸 배치)
    row_span: int     # cellSpan rowSpan, 없으면 1
    col_span: int     # cellSpan colSpan, 없으면 1
    text: str         # 셀 단락들을 "\n" 으로 join (이스케이프 전)

def text_of_t(t: etree._Element) -> str:
    """parts = [t.text or ""]; for child in t: (isinstance(child.tag, str) 이면 INLINE_TEXT.get(child.tag, "") 추가); child.tail or "" 추가. "".join(parts). strip 하지 않는다."""

def parse_paragraph(p: etree._Element) -> list[Block]:
    """buf: list[str]. for run in p.iterchildren(HP_RUN): for child in run:
         child.tag == HP_T   → buf.append(text_of_t(child))
         child.tag == HP_TBL → flush(); table = parse_table(child); table 이 None 이 아니면 blocks.append(table)
         그 외(hp:secPr, hp:ctrl[header/footer/pageNum/colPr/newNum/pageHiding…], hp:footNote, hp:endNote, hp:pic, hp:rect, hp:line, hp:container, hp:equation, hp:fieldBegin/End, hp:bookmark, 주석 노드…) → 무시 (하위 단락도 흘려보내지 않는다. §7-3 기본값)
       루프 끝에 flush(). flush(): text = "".join(buf).strip(); buf.clear(); text 가 비어 있지 않으면 blocks.append(Paragraph(text)).
       결과 예: 텍스트 run → tbl → 텍스트 run 인 단락은 [Paragraph, Table, Paragraph] (위치 보존). 텍스트 없는 표 단락은 [Table]."""

def parse_table(tbl: etree._Element) -> Table | None:
    """trs = list(tbl.iterchildren(HP_TR)).
       rows = _int_attr(tbl, "rowCnt") or len(trs);  cols = _int_attr(tbl, "colCnt") or max((tc 수 for tr in trs), default=0).
       rows <= 0 or cols <= 0 → None.
       cells = [CellSpec(...) for r_idx, tr in enumerate(trs) for tc in tr.iterchildren(HP_TC)]  — row/col/span 은 tc.find(HP_CELL_ADDR)/tc.find(HP_CELL_SPAN) 의 속성(_int_attr), 기본값은 CellSpec 주석대로. text = _cell_text(tc).
       return Table(rows=_place_cells(rows, cols, cells))."""

def _cell_text(tc: etree._Element) -> str:
    """sub = tc.find(HP_SUBLIST); None 이면 "". parts = []; for p in sub.iterchildren(HP_P): for b in parse_paragraph(p):
         Paragraph → parts.append(b.text) ; Table(중첩 표) → flat = " ".join(c for row in b.rows for c in row if c); flat 이 비어 있지 않으면 parts.append(flat)
       return "\n".join(parts)   — hwp5/body.py 의 셀 평탄화와 같은 결과."""

def _place_cells(rows: int, cols: int, cells: Sequence[CellSpec]) -> list[list[str]]:
    """hwp5/body.py 의 _place_cells 와 같은 동작(복제. hwp5 쪽 코드는 수정 금지):
       grid = rows×cols 의 None. 각 cell: (r,c) 가 범위 밖이거나 이미 찬 자리면 읽기 순서로 첫 None 자리, 없으면 새 행을 덧붙여 (len-1, 0).
       grid[r][c] = text; r..r+max(row_span,1)-1 × c..c+max(col_span,1)-1 범위(그리드 안)의 다른 None 칸은 "" (병합으로 덮인 칸).
       마지막에 None → ""."""

def _int_attr(el: etree._Element | None, name: str) -> int | None:
    """el 이 None 이거나 속성이 없거나 int() 변환 실패 → None."""

def parse_section(root: etree._Element) -> list[Block]:
    """루트(hs:sec)의 직계 자식 hp:p 만 순서대로 parse_paragraph 해 이어 붙인다. 다른 직계 자식은 무시."""
```
- 공백 규칙: run 사이에 구분자를 넣지 않고 이어 붙인다(HWP 5.0 PARA_TEXT와 동일). 단락 텍스트는 마지막에 한 번 `.strip()`. 빈 문자열 Paragraph는 만들지 않는다.
- `Table` 안 셀 텍스트는 strip 하지 않는다(렌더러 `_render_cell`이 strip·`<br>`·`\|` 처리).
- 표 셀 안 단락은 `paragraph_count`에 세지 않는다(기존 `convert`가 최상위 블록만 세므로 자동).

### 4.5 convert.py · `__init__.py` 변경
```python
# convert.py — 기존 import `from .hwp5.reader import read_blocks` 를 아래로 교체. 나머지 함수 본문·ConvertResult 불변
from .detect import detect_format
from .hwp5.reader import read_blocks as read_hwp5_blocks
from .hwpx.reader import read_blocks as read_hwpx_blocks

def read_blocks(path: Path) -> list[Block]:
    """포맷을 감지해 리더를 고른다. "hwp5" → read_hwp5_blocks, "hwpx" → read_hwpx_blocks. 예외는 그대로 전파."""
# convert() 는 위 read_blocks(source) 를 호출 (기존 호출문 그대로). paragraph_count/table_count 계산식 불변.

# __init__.py — 추가 2줄과 __all__ 항목
from .detect import DocFormat, detect_format
__all__ = ["Block", "ConvertResult", "DocFormat", "Hwp2mdError", "NotHwpFileError", "Paragraph", "Table", "UnsupportedHwpError", "__version__", "convert", "detect_format"]
```
- CLI(`cli.py`)는 변경하지 않는다(§7-2 기본값). `NotHwpFileError` → exit 3 `not an HWP 5.0 file: {input}`, `Hwp2mdError`(깨진 XML·과대 섹션) → exit 1 `{str(exc)}`.

### 4.6 합성 HWPX 생성기 (`tests/synth_hwpx.py`) — XML 템플릿은 글자 그대로
```python
"""Synthetic HWPX (OWPML zip) generator. Test-only. Mirrors synth_hwp5 fixtures so both formats can be cross-checked."""
from __future__ import annotations
import io, zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from xml.sax.saxutils import escape
from hwp2md.blocks import Paragraph
from hwp2md.hwpx.reader import HWPX_MIMETYPE, NS_HP, NS_HS
from synth_hwp5 import Item, SynthCell, SynthTable          # 타입 재사용. 재정의 금지

NS_HC = "http://www.hancom.co.kr/hwpml/2011/core"
NS_HH = "http://www.hancom.co.kr/hwpml/2011/head"
NS_HV = "http://www.hancom.co.kr/hwpml/2011/version"
NS_OCF = "urn:oasis:names:tc:opendocument:xmlns:container"
NS_OPF = "http://www.idpf.org/2007/opf/"
XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
P_ATTRS = 'paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"'
SECPR_RUN = (
    '<hp:run charPrIDRef="0">'
    '<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" '
    'tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0"/>'
    '<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl>'
    '</hp:run>'
)   # 섹션 첫 단락의 첫 run. 리더가 무시해야 하는 요소를 실제 파일처럼 넣는다
TBL_ATTRS = ('zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
             'dropcapstyle="None" pageBreak="CELL" repeatHeader="1" cellSpacing="0" borderFillIDRef="1" noAdjust="0"')
TC_ATTRS = 'name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="1"'
SUBLIST_ATTRS = ('id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" '
                 'linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0"')

def text_xml(text: str) -> str
    # escape(text) 후 "\t" → "<hp:tab/>", "\n" → "<hp:lineBreak/>" 치환
def paragraph_xml(text: str, *, para_id: int, first: bool = False) -> str
    # f'<hp:p id="{para_id}" {P_ATTRS}>' + (SECPR_RUN if first else "") + run + '</hp:p>'
    # run = f'<hp:run charPrIDRef="0"><hp:t>{text_xml(text)}</hp:t></hp:run>'  (text == "" 이면 '<hp:run charPrIDRef="0"/>')
def cell_xml(cell: SynthCell) -> str
    # f'<hp:tc {TC_ATTRS}><hp:subList {SUBLIST_ATTRS}>' + "".join(paragraph_xml(t, para_id=0) for t in (cell.paragraphs or ("",)))
    # + '</hp:subList>' + f'<hp:cellAddr colAddr="{cell.col}" rowAddr="{cell.row}"/><hp:cellSpan colSpan="{cell.col_span}" rowSpan="{cell.row_span}"/>'
    # + '<hp:cellSz width="10000" height="1000"/><hp:cellMargin left="141" right="141" top="141" bottom="141"/></hp:tc>'
def table_xml(table: SynthTable, *, para_id: int, first: bool = False) -> str
    # f'<hp:p id="{para_id}" {P_ATTRS}>' + (SECPR_RUN if first else "") + f'<hp:run charPrIDRef="0"><hp:tbl id="{1000 + para_id}" rowCnt="{table.rows}" colCnt="{table.cols}" {TBL_ATTRS}>'
    # + "".join("<hp:tr>" + "".join(cell_xml(c) for c in table.cells if c.row == r) + "</hp:tr>" for r in range(table.rows))
    # + '</hp:tbl></hp:run></hp:p>'
def section_xml(items: Sequence[Item]) -> bytes
    # (XML_DECL + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}" xmlns:hc="{NS_HC}">' + "".join(items[i] 가 str 이면 paragraph_xml(item, para_id=i, first=(i == 0)) 아니면 table_xml(item, para_id=i, first=(i == 0))) + '</hs:sec>').encode("utf-8")
def hwpx_entries(items: Sequence[Item], *, more_sections: Sequence[Sequence[Item]] = ()) -> dict[str, bytes]
    # 삽입 순서 고정: "mimetype", "version.xml", "META-INF/container.xml", "Contents/content.hpf", "Contents/header.xml", "Contents/section0.xml", ("Contents/section1.xml", … more_sections 순서)
    # mimetype            = HWPX_MIMETYPE (개행 없음)
    # version.xml         = XML_DECL + f'<hv:HCFVersion xmlns:hv="{NS_HV}" tagetApplication="WORDPROCESSOR" major="5" minor="1" micro="1" buildNumber="0" os="1" xmlVersion="1.5" application="hwp2md-synth" appVersion="0"/>'   (tagetApplication 철자는 실제 파일과 동일)
    # META-INF/container.xml = XML_DECL + f'<ocf:container xmlns:ocf="{NS_OCF}"><ocf:rootfiles><ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/></ocf:rootfiles></ocf:container>'
    # Contents/content.hpf   = XML_DECL + f'<opf:package xmlns:opf="{NS_OPF}" version="" unique-identifier="" id=""><opf:metadata><opf:title/><opf:language/></opf:metadata><opf:manifest><opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>' + 섹션마다 f'<opf:item id="section{i}" href="Contents/section{i}.xml" media-type="application/xml"/>' + '</opf:manifest><opf:spine><opf:itemref idref="header" linear="yes"/>' + 섹션마다 f'<opf:itemref idref="section{i}" linear="yes"/>' + '</opf:spine></opf:package>'
    # Contents/header.xml    = XML_DECL + f'<hh:head xmlns:hh="{NS_HH}" version="1.5" secCnt="{섹션 수}"><hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/><hh:refList/></hh:head>'
    # Contents/section{i}.xml = section_xml(...)
def build_zip(entries: Mapping[str, bytes]) -> bytes
    # io.BytesIO 에 zipfile.ZipFile(buf, "w"). Mapping 순서대로 zf.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), data, compress_type=(zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED)). 결정적 바이트(같은 입력 → 같은 출력).
def build_hwpx(items: Sequence[Item], *, more_sections: Sequence[Sequence[Item]] = ()) -> bytes   # build_zip(hwpx_entries(...))
def write_hwpx(path: Path, items: Sequence[Item], *, more_sections: Sequence[Sequence[Item]] = ()) -> Path   # 부모 디렉터리 생성 후 저장, path 반환

# 공용 fixture 추가 (synth_hwp5 의 FIXTURE_PARAGRAPHS / FIXTURE_ITEMS_WITH_TABLE / FIXTURE_ITEMS_MERGED 는 그대로 import 해서 쓴다)
FIXTURE_PARAGRAPHS_INLINE: list[str] = ["앞\t뒤", "첫 줄\n둘째 줄"]        # "\t" → hp:tab, "\n" → hp:lineBreak 로 직렬화됨
EXPECTED_BLOCKS_INLINE = [Paragraph("앞 뒤"), Paragraph("첫 줄\n둘째 줄")]
EXPECTED_MARKDOWN_INLINE = "앞 뒤\n\n첫 줄\n둘째 줄\n"
```
- 같은 fixture 상수로 `write_hwp5`와 `write_hwpx`를 만들면 `convert().markdown`이 바이트 단위로 같아야 한다(`EXPECTED_MARKDOWN`, `EXPECTED_MARKDOWN_WITH_TABLE`, `EXPECTED_MARKDOWN_MERGED`).

### 4.7 단위 테스트 계약 (파일·케이스 이름 고정. 모두 `tests/unit/`)
**`test_hwpx_body.py`** (Stage 2) — 헬퍼 `_sec(inner: str) -> etree._Element`: `parse_section_xml((XML_DECL + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}">{inner}</hs:sec>').encode())`. 케이스:
1. `test_ns_constant_matches_reader` — `body.NS_HP == reader.NS_HP`
2. `test_text_runs_concatenated` — run `<hp:t>가</hp:t>` + run `<hp:t>나</hp:t>` → `[Paragraph("가나")]`
3. `test_empty_and_whitespace_paragraph_skipped` — `<hp:p><hp:run charPrIDRef="0"/></hp:p>`, `<hp:t>  </hp:t>` → `[]`
4. `test_inline_tab_linebreak_unknown_keep_tail` — `<hp:t>a<hp:tab/>b<hp:lineBreak/>c<hp:markpenBegin/>d</hp:t>` → `"a b\ncd"`
5. `test_comment_inside_t_ignored` — `<hp:t>a<!-- x -->b</hp:t>` → `"ab"`
6. `test_table_between_text_in_same_paragraph` — run t "앞" · run tbl(1×1 셀 "x") · run t "뒤" → `[Paragraph("앞"), Table([["x"]]), Paragraph("뒤")]`
7. `test_table_only_paragraph` — `[Table(...)]`, Paragraph 없음
8. `test_grid_from_cell_addr` — 2×2, cellAddr 역순으로 적어도 좌표대로 배치
9. `test_merged_cell_blank` — colSpan 3 → `["머리글", "", ""]`
10. `test_cell_paragraphs_joined_with_newline` — 셀 단락 2개 → `"라\n마"`
11. `test_nested_table_flattened` — 셀 안 tbl(1×2 "x","y") → 부모 셀 텍스트 `"x y"`, 결과 Table 1개
12. `test_missing_row_col_cnt_falls_back_to_tr_tc` — rowCnt/colCnt 없음, tr 2·tc 2 → 2×2
13. `test_zero_rows_table_dropped` — rowCnt="0" → `[]`
14. `test_out_of_range_cell_goes_to_first_empty_slot` — rowAddr="9" (2×1 표) → 첫 빈 칸
15. `test_missing_cell_addr_uses_first_empty_slot`
16. `test_ctrl_header_and_footnote_ignored` — `<hp:ctrl><hp:header><hp:subList><hp:p><hp:run><hp:t>머리말</hp:t>…` 과 `<hp:footNote><hp:subList>…<hp:t>각주</hp:t>…` 가 본문 run 옆에 있어도 결과는 본문 Paragraph 1개뿐
17. `test_secpr_and_pic_ignored` — `<hp:secPr/>`, `<hp:pic/>` 만 있는 단락 → `[]`
18. `test_section_only_direct_p_children` — 루트 직계가 아닌 요소 무시, 단락 순서 보존

**`test_synth_hwpx.py`** (Stage 3):
1. `test_mimetype_first_and_stored` — `namelist()[0] == "mimetype"`, `infolist()[0].compress_type == ZIP_STORED`, 내용 `== HWPX_MIMETYPE`
2. `test_entries_exact` — 엔트리 이름 == §4.6 순서의 6개
3. `test_section_parses_with_stdlib` — `xml.etree.ElementTree.fromstring` 성공, 루트 `{NS_HS}sec`, 직계 `hp:p` 수 == len(items), `hp:tbl` 수 == SynthTable 수
4. `test_round_trip_paragraphs` — `hwpx.reader.read_blocks(write_hwpx(FIXTURE_PARAGRAPHS)) == [Paragraph(p) for p in FIXTURE_PARAGRAPHS if p]`
5. `test_round_trip_table` — `== synth_hwp5.EXPECTED_BLOCKS_WITH_TABLE`
6. `test_round_trip_merged` — `== synth_hwp5.EXPECTED_BLOCKS_MERGED`
7. `test_round_trip_inline` — `== EXPECTED_BLOCKS_INLINE`
8. `test_deterministic_bytes` — `build_hwpx(x) == build_hwpx(x)`
9. `test_two_sections_concatenated` — `more_sections=[["둘째 섹션"]]` → 블록 끝에 `Paragraph("둘째 섹션")`, header.xml `secCnt="2"`

**`test_hwpx_reader.py`** (Stage 3):
1. `test_not_a_zip_raises_not_hwp` — 텍스트 파일 → `NotHwpFileError`
2. `test_missing_section0_raises_not_hwp` — `hwpx_entries` 에서 section0 제거 후 `build_zip` → `NotHwpFileError`
3. `test_section_names_numeric_order` — 엔트리 section0·section1·section10·section2 → `section_names` 결과 `[0, 1, 2, 10]` 순
4. `test_malformed_xml_raises_hwp2md_error` — section0 = `b"<hs:sec>unclosed"` → `Hwp2mdError`, 메시지 `malformed section XML` 포함
5. `test_wrong_root_raises_hwp2md_error` — `b'<?xml version="1.0"?><x/>'` → `Hwp2mdError`, `unexpected root element` 포함
6. `test_oversized_section_rejected` — `monkeypatch.setattr(reader, "MAX_SECTION_BYTES", 10)` → `Hwp2mdError`, `too large` 포함
7. `test_external_entity_not_resolved` — section0 앞에 `<!DOCTYPE hs:sec [<!ENTITY xxe SYSTEM "file:///etc/hosts">]>` 를 넣고 `<hp:t>a&xxe;b</hp:t>` → 예외 없이 `[Paragraph("ab")]` (파일 내용 미포함)
8. `test_internal_entity_not_expanded` — `<!ENTITY lol "lol">` + `<hp:t>a&lol;b</hp:t>` → `[Paragraph("ab")]`
9. `test_make_parser_options` — `p = make_parser()`; `p.resolve_entities is False` (lxml 파서 속성으로 확인 가능)

**`test_detect.py`** (Stage 4): `test_hwp5_fixture_is_hwp5`, `test_hwpx_fixture_is_hwpx`, `test_hwpx_with_hwp_extension_is_hwpx`, `test_zip_without_mimetype_but_section0_is_hwpx`, `test_zip_other_mimetype_no_section_raises`, `test_text_file_raises`, `test_empty_file_raises`, `test_corrupt_zip_raises` (`b"PK\x05\x06" + b"\x00" * 18` 같은 빈 zip 은 2-c 로 NotHwpFileError).

**`test_cross_format.py`** (Stage 4): `@pytest.mark.parametrize` 3종(`FIXTURE_PARAGRAPHS`, `FIXTURE_ITEMS_WITH_TABLE`, `FIXTURE_ITEMS_MERGED`) — `convert(write_hwp5(...)).markdown == convert(write_hwpx(...)).markdown` 이고 `paragraph_count`·`table_count` 동일; `test_convert_hwpx_inline_fixture` — `== EXPECTED_MARKDOWN_INLINE`; `test_convert_hwpx_result_fields` — `output == out/sample.md`, `table_count == 0`.

### 4.8 E2E 계약 (`tests/e2e/test_cli_hwpx.py`) — conftest.py 는 수정하지 않는다
```python
from synth_hwp5 import (EXPECTED_MARKDOWN, EXPECTED_MARKDOWN_MERGED, EXPECTED_MARKDOWN_WITH_TABLE,
                        FIXTURE_ITEMS_MERGED, FIXTURE_ITEMS_WITH_TABLE, FIXTURE_PARAGRAPHS, write_hwp5)
from synth_hwpx import build_zip, hwpx_entries, write_hwpx
RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]     # conftest 의 run_cli fixture 사용
REAL_HWPX_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "hwpx"          # §7-5 기본값
REAL_HWPX_FIXTURES = sorted(REAL_HWPX_DIR.glob("*.hwpx"))
REAL_HWPX_EXPECTED: dict[str, tuple[int, int]] = {                                  # (단락 수, 표 수) — §4.11
    "(서식1) 비영리법인 현황 제출 양식.hwpx": (1, 1),
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx": (80, 31),
    "브라더 공공기관 보고서 양식.hwpx": (32, 8),
}
STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개$")
def _copy_evidence(md: Path, name: str) -> None   # Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots")) / name 로 복사(디렉터리 생성)
```
케이스 (이름 고정, 총 7 + 실제 샘플 3 = 10):
1. `test_convert_hwpx_synthetic_success` — `write_hwpx(tmp/"sample.hwpx", FIXTURE_PARAGRAPHS)`; exit 0; 1행 `== f"✓ sample.hwpx → {out_dir / 'sample.md'}"`; 2행 `== "  단락 3개 · 표 0개"`; 내용 `== EXPECTED_MARKDOWN`; 증거 `sample_hwpx.md`
2. `test_convert_hwpx_table_success` — `FIXTURE_ITEMS_WITH_TABLE` → `table.hwpx`; 2행 `"  단락 2개 · 표 1개"`; `== EXPECTED_MARKDOWN_WITH_TABLE`; 증거 `table_hwpx.md`
3. `test_convert_hwpx_merged_table` — `FIXTURE_ITEMS_MERGED` → `merged.hwpx`; 2행 `"  단락 1개 · 표 1개"`; `== EXPECTED_MARKDOWN_MERGED`; 증거 `merged_hwpx.md`
4. `test_hwpx_content_with_hwp_extension_converts` — `write_hwpx(tmp/"disguised.hwp", FIXTURE_PARAGRAPHS)`; exit 0; `disguised.md` 내용 `== EXPECTED_MARKDOWN`
5. `test_hwp5_and_hwpx_same_markdown` — `write_hwp5(tmp/"a.hwp", FIXTURE_ITEMS_WITH_TABLE)` 와 `write_hwpx(tmp/"b.hwpx", FIXTURE_ITEMS_WITH_TABLE)` 각각 변환; 두 `.md` `read_bytes()` 동일; 두 stdout 2행 동일
6. `test_zip_not_hwpx_exit_3` — `build_zip({"mimetype": b"application/epub+zip", "hello.txt": b"hi"})` 를 `notes.hwpx` 로 저장; exit 3; stderr 에 `not an HWP 5.0 file:` 포함(§7-2 대안 선택 시 `not an HWP/HWPX file:`); `notes.md` 미생성
7. `test_hwpx_malformed_section_exit_1` — `e = hwpx_entries(FIXTURE_PARAGRAPHS); e["Contents/section0.xml"] = b"<hs:sec>unclosed"; build_zip(e)` → `broken.hwpx`; exit 1; stderr 에 `malformed section XML` 포함; `broken.md` 미생성
8. `test_real_hwpx_fixture_converts[<name>]` — `@pytest.mark.parametrize("real_hwpx", REAL_HWPX_FIXTURES, ids=lambda p: p.name)`; exit 0; 2행 정규식 매치; `(단락, 표) == REAL_HWPX_EXPECTED[name]` (name 이 dict 에 없으면 이 비교만 생략); `.md` 의 `\|(---\|)+` 전체 일치 줄 수 `== 표 수`; `len(content.strip()) > 0`; 증거 `md.name`
- 폴더가 비어 있으면 pytest 기본 동작(empty parameter set → skipped 1). `pytest.skip`/`mark.skip` 문자열을 코드에 쓰지 않는다 (gate 가 약화로 본다).
- 실제 샘플 파일명에 공백·괄호·한글이 있다. `run_cli` 는 리스트 인자(`shell=False`)이므로 그대로 넘긴다. 따옴표 처리 금지.
- 기존 `test_cli_convert.py`·`test_cli_table.py` 는 수정하지 않는다(§7-2 대안 선택 시 `test_cli_convert.py` 58행 `"not an HWP 5.0 file:"` → `"not an HWP/HWPX file:"` 1곳만).

### 4.9 docs/decisions.md 추가 항목 (Stage 5, 파일 끝에 이 내용을 그대로 덧붙인다)
```
## 2026-10-22 포맷 감지: 확장자가 아니라 파일 내용(OLE 시그니처 / zip + mimetype)으로 판정
- 결정: `convert()`는 `detect_format()`으로 입력을 판정한다. OLE 복합 파일이면 HWP 5.0 리더, zip이고 `mimetype` 엔트리가 `application/hwp+zip`이거나 `Contents/section0.xml`이 있으면 HWPX 리더, 그 외는 `NotHwpFileError`. 확장자(.hwp/.hwpx)는 보지 않는다.
- 이유: 공공기관 배포 파일은 HWPX 내용에 .hwp 확장자가 붙은 경우가 있다. 두 포맷은 첫 바이트(OLE 매직 / zip 매직)로 확실히 구분되므로 내용 판정이 더 정확하고, 사용자는 포맷 차이를 몰라도 된다(vision 시나리오 4).

## 2026-10-22 HWPX 파서: lxml + 보안 파서 옵션(외부 엔티티·네트워크 차단)
- 결정: HWPX 섹션 XML은 `lxml.etree`로 파싱하고 파서는 항상 `XMLParser(resolve_entities=False, no_network=True, huge_tree=False)`로 만든다. 섹션 XML 엔트리가 50MB를 넘으면 거부한다. 타입 검사는 `lxml-stubs`(dev 의존성)로 한다.
- 이유: 외부에서 받은 문서를 그대로 열므로 XXE(외부 엔티티로 로컬 파일 읽기)·엔티티 폭발(billion laughs)·zip 폭탄을 기본으로 막아야 한다. lxml은 수 MB 섹션도 빠르고 네임스페이스 처리가 표준 라이브러리보다 안정적이다.

## 2026-10-22 HWPX 본문 범위: 단락 텍스트와 표만, 머리말·꼬리말·각주·그림·도형은 무시
- 결정: `hp:p`의 `hp:run` 안에서 `hp:t`(텍스트)와 `hp:tbl`(표)만 블록으로 바꾼다. `hp:secPr`, `hp:ctrl`(머리말·꼬리말·쪽번호·단 설정), `hp:footNote`/`hp:endNote`, `hp:pic`, 도형 요소는 건너뛴다. 인라인 요소는 `hp:tab`→공백, `hp:lineBreak`→줄바꿈, 그 외는 빈 문자열(뒤따르는 텍스트는 유지).
- 이유: 머리말·쪽번호는 본문 흐름에 섞이면 RAG 청킹에 잡음이 된다. 각주·그림은 별도 태스크(각주 → 하단 참조, 이미지 → 추출)에서 자기 자리를 갖는다. HWP 5.0 리더의 "표 아닌 컨트롤 단락 흘려보냄"과 다르지만 실제 샘플에서 두 방식의 결과 차이는 없었고, 통일은 각주 태스크에서 한다.
```

### 4.10 README.md · tests/fixtures/README.md 변경 (Stage 5)
README.md "설치와 실행 (개발 중)" 절 — 코드 블록의 둘째 줄 아래에 한 줄 추가, 마지막 문장 교체:
```
uv run hwp2md input.hwp -o out/       # out/input.md 생성
uv run hwp2md input.hwpx -o out/      # HWPX 도 같은 명령 (포맷은 내용으로 판별)
```
`현재 지원: HWP 5.0 바이너리의 본문 단락 텍스트와 표(Markdown 표, 병합 셀은 빈 칸, 셀 내 단락은 <br>). 이미지·각주·HWPX는 진행 중.`
→ `현재 지원: HWP 5.0 바이너리와 HWPX(zip/XML) 두 포맷의 본문 단락 텍스트와 표(Markdown 표, 병합 셀은 빈 칸, 셀 내 단락은 <br>). 포맷은 확장자가 아니라 파일 내용으로 판별한다. 이미지·각주는 진행 중.`

tests/fixtures/README.md 전체를 아래로 교체:
```
# tests/fixtures

실제 샘플 문서 보관 위치. **이 폴더의 문서 파일은 전부 gitignore 대상**이라 커밋되지 않는다 (이 README와 .gitkeep만 추적).

- `*.hwp` (이 폴더 바로 아래) — HWP 5.0 샘플. E2E `test_real_fixture_converts`가 자동으로 찾아 변환을 검증한다.
- `hwpx/*.hwpx` — HWPX(zip/XML) 샘플. E2E `test_real_hwpx_fixture_converts`가 자동으로 찾아 변환을 검증한다. 파일명이 `tests/e2e/test_cli_hwpx.py`의 `REAL_HWPX_EXPECTED`에 있으면 단락·표 수까지 비교한다.
- `unsupported/hwp3/` — HWP 3.0(구형) 샘플. 지원 계획 없음. 거절 메시지 확인용.

E2E는 지정한 폴더만 탐색하므로, 아직 지원하지 않는 포맷은 `unsupported/` 아래에 두면 테스트가 실패하지 않는다.
```

### 4.11 실제 HWPX 샘플 조사 결과 (2026-10-22, 표준 라이브러리로 읽기 전용 조사. implementer는 추측하지 말고 이 숫자를 쓴다)
공통: 3개 모두 `mimetype`이 첫 엔트리(STORED)이고 값은 `application/hwp+zip`. 섹션은 `Contents/section0.xml` 1개. 루트 요소 `hs:sec`, 직계 자식은 `hp:p`만. 네임스페이스 접두사 `hp`/`hs`/`hc`/`hh`의 URI는 §4.3·§4.6 상수와 같다(루트에 15개 xmlns 선언이 있지만 본문 요소는 전부 `hp`). `hp:run`의 자식으로 관찰된 요소: `secPr`, `ctrl`, `tbl`, `t`, `pic`. 모든 `hp:tc`에 `subList`·`cellAddr`·`cellSpan`·`cellSz`·`cellMargin`이 있다(순서도 이대로). `hp:tbl`의 부모 사슬은 `run < p < sec`(최상위) 또는 `run < p < subList < tc < tr < tbl`(중첩). §4.4 규칙을 표준 라이브러리로 시뮬레이션했을 때 cellAddr 범위 밖·중복 배치 0건, 빈 그리드 칸 0건. `hp:lineBreak`·`hp:footNote`·`hp:endNote`는 3개 모두 없음. 텍스트와 표가 같은 `hp:p`에 있는 경우 0건. header.xml 루트는 `hh:head`(속성 `version`, `secCnt`), version.xml 루트는 `hv:HCFVersion`.

| 샘플 (파일명) | zip 엔트리 | section0.xml 크기 | 최상위 `hp:p` | `hp:p` 전체 | `hp:tbl` 최상위 / 중첩 | `hp:tc` | span>1 셀 | `hp:t` 인라인 자식 | `hp:ctrl` 자식 | 그 외 | **기대 (단락, 표)** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `(서식1) 비영리법인 현황 제출 양식.hwpx` | 11 | 약 110 KB | 3 | 140 | 1 / 1 (34×10 표 안에 3×4 표) | 126 | 67 | 없음 | colPr 1 | — | **(1, 1)** |
| `(서식2) 사업실적 및 사업계획 제출 양식.hwpx` | 11 | 약 1.8 MB | 149 | 2452 | 31 / 0 (1×3 표 16개, 최대 35×13) | 2226 | 표당 최대 107 | 없음 | colPr 1 | `cellzoneList` 15 (tbl 자식, 무시) | **(80, 31)** |
| `브라더 공공기관 보고서 양식.hwpx` | 14 (`BinData/image1.png`, `Scripts/*.js` 포함) | 약 60 KB | 59 | 103 | 8 / 0 (3×3 2개, 1×1 1개, 1×7 1개, 1×3 4개) | 30 | 6 | `hp:tab` 5 (text 뒤 tail 텍스트 있음) | colPr 1, pageNum 1, header 1 (subList 안 `hp:p` 1개, 텍스트 없음), pageHiding 2, newNum 1 | `hp:pic` 2 | **(32, 8)** |

- 기대 (단락, 표)는 §4.4 규칙(최상위 `hp:p`의 run 안 `hp:t` 이어 붙여 strip, 비어 있으면 생략; `hp:tbl` 최상위만 Table, 중첩은 평탄화; `hp:ctrl`·`hp:pic`·`hp:secPr` 무시) 그대로 계산한 값이다. §7-3 대안(머리말 흘려보냄)을 택해도 머리말 단락이 비어 있어 숫자는 같다.
- 샘플 2의 1×3 표 16개는 Markdown에서 헤더 행만 있는 표가 된다(전 태스크 알려진 문제. 이번 범위 아님).
- 처리 시간: 1.8 MB 섹션(셀 2226개)도 표준 라이브러리 파싱 1초 미만. lxml은 더 빠르다. E2E 5분 상한에 여유.

### 4.12 의존성 추가 명령 (Stage 1, orchestrator가 직접 실행)
```bash
cd /Users/illi/illy-projects/hwp2md && uv add "lxml>=5" && uv add --dev lxml-stubs && uv sync
cd /Users/illi/illy-projects/hwp2md && uv run python -c "import lxml.etree as e; print('lxml ok', e.LXML_VERSION[0] >= 5)"   # → lxml ok True
cd /Users/illi/illy-projects/hwp2md && git diff --stat   # → pyproject.toml, uv.lock 2개만
```
- `pyproject.toml` 기대 결과: `dependencies = ["olefile>=0.46", "lxml>=5"]`, `dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.10", "lxml-stubs"]` (uv가 하한 버전을 붙이면 그대로 둔다. 순서 무관). `description`은 10줄 이하 설정 변경 허용 범위로 `"Convert HWP 5.0 and HWPX documents to Markdown without Hancom Office"`로 바꿔도 된다(선택).
- §7-1 대안 (b)로 전환할 때: `uv remove --dev lxml-stubs && uv add --dev types-lxml`. 대안 (c): `pyproject.toml`의 `[[tool.mypy.overrides]]`에 `module = "lxml.*"`, `ignore_missing_imports = true` 블록 추가(이 경우 reader·body의 lxml 반환값은 `Any`가 되어 `warn_return_any`를 피하려면 `cast`/명시 타입이 필요 — 코드가 늘어나므로 비권장).

### 4.13 runner 공통 실행 블록 (macOS zsh. `timeout` 명령·`PIPESTATUS` 금지. Bash 도구 timeout 파라미터 600000)
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-hwpx-reader && mkdir -p $T/logs $T/screenshots && \
{ uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src && uv run pytest tests/unit -q; } > $T/logs/s<N>-test.log 2>&1; echo "exit=$?" >> $T/logs/s<N>-test.log; tail -20 $T/logs/s<N>-test.log
```
E2E (Stage 6):
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-hwpx-reader && mkdir -p $T/logs $T/screenshots && \
[ -f $T/logs/e2e.log ] && mv $T/logs/e2e.log $T/logs/e2e.prev.log; \
ILLY_SHOT_DIR=$T/screenshots uv run pytest tests/e2e -q > $T/logs/e2e.log 2>&1; echo "exit=$?" >> $T/logs/e2e.log; \
tail -5 $T/logs/e2e.log; grep -E "passed|failed|error" $T/logs/e2e.log | tail -3; ls $T/screenshots
```
실제 샘플 CLI 직접 실행 (Stage 4 검증):
```bash
cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-hwpx-reader && mkdir -p $T/logs $T/screenshots && OUT=$(mktemp -d) && \
for f in tests/fixtures/hwpx/*.hwpx; do uv run hwp2md "$f" -o "$OUT"; echo "exit=$?"; done > $T/logs/s4-real.log 2>&1; cat $T/logs/s4-real.log; cp "$OUT"/*.md $T/screenshots/
```
기대 stdout(파일명 정렬 순): 2행이 `  단락 1개 · 표 1개`, `  단락 80개 · 표 31개`, `  단락 32개 · 표 8개`, `exit=0` 3번.

## 5. 단계 (Stage) — 전부 순차. 병렬 없음.

### Stage 1 — 의존성 추가(lxml, lxml-stubs)와 실제 샘플 폴더 이동 (orchestrator 전용 파일)
- 목적: 런타임 `lxml>=5`·dev `lxml-stubs`를 선언하고, 지원 예정 샘플을 `tests/fixtures/hwpx/`로 옮겨 이후 단계가 바로 쓰게 한다.
- 담당: orchestrator 직접 (서브에이전트 없음. `pyproject.toml`·`uv.lock`은 전용 파일, 폴더 이동은 gitignore 대상이라 git 변경 없음)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §4.12, §7-1, §7-5
- 쓰기 범위 (이 파일들만 수정/생성):
  - `pyproject.toml`
  - `uv.lock`
  - `tests/fixtures/hwpx/` (mv 로 생성. §7-5 기본값)
- 산출물: lxml 설치된 `.venv`, `tests/fixtures/hwpx/*.hwpx` 3개
- 검증:
  - §4.12 명령 → `lxml ok True`, `git diff --stat` 에 `pyproject.toml`·`uv.lock` 만
  - `cd /Users/illi/illy-projects/hwp2md && mkdir -p tests/fixtures/hwpx && mv tests/fixtures/unsupported/hwpx/*.hwpx tests/fixtures/hwpx/ && rmdir tests/fixtures/unsupported/hwpx && ls tests/fixtures/hwpx | wc -l` → `3`; `git status --short tests/fixtures` → 출력 없음
  - `uv run mypy src && uv run pytest tests/unit -q && uv run pytest tests/e2e -q` → `Success: no issues found in 10 source files`, `64 passed`, `11 passed` (기존 E2E는 `fixtures/*.hwp` 만 보므로 이동 영향 없음)
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev`
- 실패 시: `uv add` 실패 → BLOCKED(§3). `git checkout -- pyproject.toml uv.lock && uv sync` 로 복귀. 폴더 이동은 `mv` 역방향으로 복귀.

### Stage 2 — HWPX 섹션 파서와 리더 (hwpx/body.py, hwpx/reader.py)
- 목적: 섹션 XML 트리를 §4.4 규칙으로 `list[Block]`으로 바꾸고, zip에서 섹션을 안전하게 읽는 `read_blocks(path)`를 만든다.
- 담당: implementer(opus) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 1
- 입력: §1, §4.3, §4.4, §4.7(`test_hwpx_body.py`), §4.11; 참고로 읽을 파일 `src/hwp2md/hwp5/body.py`(`_place_cells` 동작), `src/hwp2md/blocks.py`, `src/hwp2md/errors.py`, `tests/unit/test_hwp5_body.py`(테스트 스타일)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/hwpx/__init__.py`
  - `src/hwp2md/hwpx/reader.py`
  - `src/hwp2md/hwpx/body.py`
  - `tests/unit/test_hwpx_body.py`
- 산출물: §4.3·§4.4의 모든 공개 함수·상수, 단위 테스트 18개
- 검증 (implementer 자체 → runner 재실행, 로그 `logs/s2-test.log`):
  - §4.13 공통 블록 → ruff OK, format 변경 0, `Success: no issues found in 13 source files`, unit `82 passed` 이상(64 + 18), failed 0
  - `cd /Users/illi/illy-projects/hwp2md && uv run python -c "from pathlib import Path; from hwp2md.hwpx.reader import read_blocks; from hwp2md.blocks import Paragraph, Table
for f in sorted(Path('tests/fixtures/hwpx').glob('*.hwpx')):
    b = read_blocks(f); print(sum(isinstance(x, Paragraph) for x in b), sum(isinstance(x, Table) for x in b))"` → 세 줄 `1 1`, `80 31`, `32 8`
  - reviewer: diff가 쓰기 범위 4개 파일뿐, `hwp5/**` 변경 0, `make_parser` 옵션 3개가 §4.3과 글자 그대로, `isinstance(child.tag, str)` 가드 존재
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-hwpx-reader][s2] hwpx: section parser and zip reader`
- 실패 시: 실제 샘플 숫자가 다르면 어느 `hp:p`에서 차이가 나는지 NEEDS에 적고 PARTIAL. orchestrator가 `git restore --source=HEAD` 로 되돌리고 RETRY(최대 3).

### Stage 3 — 합성 HWPX 생성기와 리더 오류·보안 테스트 (synth_hwpx.py)
- 목적: `synth_hwp5`와 같은 fixture 내용을 HWPX zip으로 만들고, 리더의 오류 경로(zip 아님·섹션 없음·깨진 XML·과대·엔티티)를 단위 테스트로 고정한다.
- 담당: implementer(opus) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 2
- 입력: §4.6, §4.7(`test_synth_hwpx.py`, `test_hwpx_reader.py`), `tests/synth_hwp5.py`(import 할 이름·fixture 상수), `tests/unit/test_synth_hwp5.py`(스타일)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/synth_hwpx.py`
  - `tests/unit/test_synth_hwpx.py`
  - `tests/unit/test_hwpx_reader.py`
- 산출물: §4.6의 모든 함수·상수, 단위 테스트 9 + 9 = 18개
- 검증 (로그 `logs/s3-test.log`): §4.13 공통 블록 → ruff OK, mypy `13 source files` Success(tests 는 mypy 대상 아님), unit `100 passed` 이상, failed 0. 특히 `-k entity` 2개 pass.
  - reviewer: `synth_hwp5.py` 변경 0, `SynthTable`/`SynthCell` 재정의 없음(import), XML 템플릿 속성명이 §4.6과 일치(`rowCnt`, `colCnt`, `colAddr`, `rowAddr`, `colSpan`, `rowSpan`), `mimetype` STORED
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-hwpx-reader][s3] tests: synthetic HWPX generator, reader error and entity tests`
- 실패 시: 엔티티 테스트가 lxml 동작 차이로 실패하면 실제 반환값을 NEEDS에 적고 PARTIAL (계약 변경 아님. orchestrator가 분류). RETRY 최대 3.

### Stage 4 — 포맷 감지와 convert 디스패치 (detect.py, convert.py, __init__.py)
- 목적: `convert()`가 파일 내용으로 포맷을 판정해 두 리더 중 하나를 쓰게 하고, 두 포맷 결과가 같음을 단위 테스트로 고정한다. CLI는 변경 없이 HWPX를 받는다.
- 담당: implementer(opus) → runner(haiku) → reviewer(sonnet)
- 병렬 가능: 아니오 · 선행: Stage 3
- 입력: §4.2, §4.5, §4.7(`test_detect.py`, `test_cross_format.py`), `src/hwp2md/convert.py`, `src/hwp2md/__init__.py`, `tests/unit/test_convert.py`(스타일·기존 기대 유지)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/detect.py`
  - `src/hwp2md/convert.py`
  - `src/hwp2md/__init__.py`
  - `tests/unit/test_detect.py`
  - `tests/unit/test_cross_format.py`
- 산출물: `detect_format`, `DocFormat`, `convert.read_blocks` 디스패처, 단위 테스트 8 + 5 = 13개
- 검증 (로그 `logs/s4-test.log`, `logs/s4-real.log`):
  - §4.13 공통 블록 → ruff OK, mypy `Success: no issues found in 14 source files`, unit `113 passed` 이상, failed 0
  - §4.13 실제 샘플 블록 → 2행 `  단락 1개 · 표 1개` / `  단락 80개 · 표 31개` / `  단락 32개 · 표 8개`, `exit=0` 3회, `.md` 3개가 `screenshots/` 에 복사됨
  - `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e -q` → `11 passed` (기존 E2E 회귀 없음. `test_not_hwp_exit_3` 가 여전히 exit 3)
  - reviewer: `cli.py` 변경 0, `ConvertResult` 필드 불변, `detect_format` 에 확장자 비교(`.suffix`) 없음
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-hwpx-reader][s4] convert: content-based format detection, hwpx dispatch`
- 실패 시: `git restore --source=HEAD -- src/hwp2md/convert.py src/hwp2md/__init__.py` + 새 파일 quarantine. RETRY 최대 3.

### Stage 4b — CLI 에러 문구 변경 (cli.py 전용 단계. §7-2에서 "변경"을 택했을 때만 실행, 기본값이면 건너뛴다)
- 목적: `NotHwpFileError` 메시지를 `not an HWP/HWPX file: {input}` 로 바꾼다.
- 담당: orchestrator 직접 (1줄 변경, 10줄 이하 설정 변경 규칙)
- 병렬 가능: 아니오 · 선행: Stage 4
- 쓰기 범위: `src/hwp2md/cli.py` 39행 문자열 1곳
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run hwp2md pyproject.toml -o /tmp/x; echo "exit=$?"` → stderr `hwp2md: error: not an HWP/HWPX file: pyproject.toml`, `exit=3`. (이 시점 `tests/e2e/test_cli_convert.py::test_not_hwp_exit_3` 는 실패 상태가 되며 Stage 6에서 58행을 고친다)
- 완료 조건: 커밋 `[T-20261022-hwpx-reader][s4b] cli: error message covers HWPX`
- 실패 시: `git checkout -- src/hwp2md/cli.py`

### Stage 5 — 결정 기록·README·fixtures README 갱신
- 목적: 포맷 감지·lxml 보안 파서·본문 범위 결정 3건을 기록하고 사용자 문서를 현재 지원 범위에 맞춘다.
- 담당: implementer(opus, 도구 호출 15회 이내) → reviewer(sonnet) (runner 생략: 문서 변경)
- 병렬 가능: 아니오 · 선행: Stage 4 (4b 포함)
- 입력: §4.9, §4.10, 현재 `docs/decisions.md`, `README.md`, `tests/fixtures/README.md`
- 쓰기 범위 (이 파일들만 수정/생성):
  - `docs/decisions.md`
  - `README.md`
  - `tests/fixtures/README.md`
- 산출물: decisions 8건(기존 5 + 3), README 실행 예시 1줄 추가 + "현재 지원" 문장 교체, fixtures README 교체
- 검증:
  - `cd /Users/illi/illy-projects/hwp2md && grep -c '^## 2026-10-22' docs/decisions.md` → `8`
  - `cd /Users/illi/illy-projects/hwp2md && grep -c 'HWPX' README.md` → `3` 이상이고 `grep -c 'HWPX는 진행 중' README.md` → `0`
  - `cd /Users/illi/illy-projects/hwp2md && grep -c 'hwpx/' tests/fixtures/README.md` → `1` 이상, `grep -c 'unsupported/hwpx' tests/fixtures/README.md` → `0`
  - `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → `sanitize-check: OK`
  - `cd /Users/illi/illy-projects/hwp2md && git diff --stat` → 3개 파일만
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-hwpx-reader][s5] docs: decisions (format detection, lxml security, hwpx body scope), README`
- 실패 시: `git checkout -- docs/decisions.md README.md tests/fixtures/README.md`. RETRY 최대 2.

### Stage 6 — E2E 테스트 작성·실행 (필수, 생략 불가)
- 목적: 사용자 관점(콘솔 스크립트 실행)으로 합성·위장 확장자·포맷 교차·실패 2종·실제 샘플 3개를 검증하고 증거 `.md`를 남긴다.
- 담당: test-writer(sonnet) → runner(haiku)
- 병렬 가능: 아니오 · 선행: Stage 5
- 입력: §4.8, §4.6(import 이름), `tests/e2e/conftest.py`(fixture 이름, 수정 금지), `tests/e2e/test_cli_table.py`(스타일), §4.11 기대 숫자
- 쓰기 범위 (이 파일들만 수정/생성):
  - `tests/e2e/test_cli_hwpx.py`
  - `tests/e2e/test_cli_convert.py` (§7-2 대안을 택한 경우에만 58행 1곳. 기본값이면 수정 금지)
- 산출물: E2E 케이스 10개(7 + 실제 샘플 parametrize 3), 증거 `screenshots/sample_hwpx.md`, `table_hwpx.md`, `merged_hwpx.md`, 실제 샘플 `.md` 3개
- 검증 (runner, §4.13 E2E 블록, 로그 `logs/e2e.log`):
  - `uv run pytest tests/e2e -q` → `21 passed`, `exit=0`, failed 0, error 0
  - `ls .ai/tasks/T-20261022-hwpx-reader/screenshots` → `.md` 6개 이상(기존 E2E 증거 포함 시 더 많음)
  - `cd /Users/illi/illy-projects/hwp2md && uv run ruff check tests && uv run ruff format --check tests` → OK
  - `git diff --stat` → `tests/e2e/test_cli_hwpx.py` (+ 조건부 `test_cli_convert.py`) 만
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-hwpx-reader][s6] e2e: hwpx conversion, detection, failure paths, real samples`
- 실패 시: orchestrator가 e2e-standard 표로 분류 — 테스트 파일 안 오류(import·fixture) → test-writer 재호출(2회 실패 시 opus), 구현 오류(assert·exit code) → implementer(opus)에게 해당 Stage 쓰기 범위로 재호출. 같은 오류 2회 → BLOCKED.

### Stage 7 — 리뷰·결과 기록
- 목적: 전 단계 diff와 증거 `.md`를 사람 대신 검토하고 RESULT·STATE를 쓴다.
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: Stage 6
- 입력: `git diff e13ae706b1f56e8d4cb4460e6cb6e2f38e0c21dc...HEAD --stat`, `logs/*.log`, `screenshots/*.md`, PLAN §2, PROGRESS.md
- 쓰기 범위:
  - reviewer: 없음(읽기 전용. 보고서만)
  - scribe: `.ai/tasks/T-20261022-hwpx-reader/RESULT.md`, `/Users/illi/illy-projects/hwp2md/.ai/STATE.md` (이 두 파일만. `.ai/` 밖 금지)
- reviewer 체크: §2 S1~S12 각 항목에 PASS/FAIL + 근거(로그 파일·줄). `screenshots/merged_hwpx.md` 를 열어 `| 머리글 |  |  |` 와 `라<br>마` 가 보이는지, 실제 샘플 `.md` 3개를 열어 구분선 수가 표 수와 같고 머리말 텍스트가 섞이지 않았는지 직접 확인. `hwp5/**`·`render.py`·`blocks.py`·`errors.py`·`conftest.py` 변경 0 확인. `sanitize-check` 재실행.
- scribe: `record-standard.md` 형식 RESULT.md(결론 3줄, 성공 기준 표, 변경 요약, 테스트 수 unit/E2E, 못 한 것: 머리말·각주 무시·두 포맷 컨트롤 처리 차이·1행 표 헤더 문제, 비용), STATE.md 를 IDLE 로 (다음 행동: 사용자 RESULT 검토 → main 병합).
- 검증: `$ILLY_ROOT/scripts/gate.sh -C /Users/illi/illy-projects/hwp2md` → `GATE PASS`
- 완료 조건: RESULT.md 존재 + gate PASS + 커밋 `[T-20261022-hwpx-reader][s7] result`

## 6. 병렬 실행 맵
```
Stage 1(orchestrator) ──> Stage 2 ──> Stage 3 ──> Stage 4 ──(§7-2 변경 시 4b)──> Stage 5 ──> Stage 6(E2E) ──> Stage 7(리뷰·기록)
```
병렬 묶음 없음. 모든 단계가 공유 트리에서 순차로 실행되므로 worktree 격리 불필요. 각 단계 시작 시 orchestrator가 `git rev-parse HEAD > .ai/tasks/T-20261022-hwpx-reader/.base-s<n>` 저장.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [x] 1. lxml 타입 검사 방식: **기본값 (a) `lxml-stubs`를 dev 의존성으로** (lxml 프로젝트가 관리하는 공식 스텁, mypy strict에 바로 붙음). 대안 (b) `types-lxml`(더 세밀한 오버로드, 서드파티) — Stage 1 명령만 `uv add --dev types-lxml` 로 바뀜. 대안 (c) `[[tool.mypy.overrides]] module="lxml.*" ignore_missing_imports=true` — 스텁 없이 진행하되 reader·body 에 `cast` 가 늘어남(비권장).
- [x] 2. 포맷 아님 에러 문구: **기본값 유지 `not an HWP 5.0 file: {input}`** (cli.py 변경 없음, 기존 E2E 불변). 대안: `not an HWP/HWPX file: {input}` 로 변경 — Stage 4b(orchestrator 1줄) 실행 + Stage 6에서 `test_cli_convert.py` 58행 1곳 수정 + §4.8-6 기대 문구 변경.
- [x] 3. 머리말·꼬리말·쪽번호·각주·미주·도형 안의 단락: **기본값 무시** (HWPX는 `hp:ctrl`/`hp:footNote`/`hp:endNote`/도형 요소 전체를 건너뜀. 이유: 머리말·쪽번호가 본문 사이에 끼면 청킹 잡음이고, 각주·그림은 자기 태스크가 따로 있다. HWP 5.0 쪽 "흘려보냄"과 다르지만 실제 샘플 5개(hwp 2 + hwpx 3) 어디서도 결과 차이가 없다). 대안: 일관성을 위해 흘려보냄 — §4.4 `parse_paragraph` 의 "그 외" 분기에서 `hp:ctrl`·`hp:footNote`·`hp:endNote` 아래 `.//hp:subList/hp:p` 를 재귀 `parse_paragraph` 해 현재 위치에 끼워 넣고, 단위 테스트 16번 기대를 `[Paragraph("본문"), Paragraph("머리말"), Paragraph("각주")]` 로, §4.9 셋째 항목 문구 변경. §4.11 기대 숫자는 변하지 않음.
- [x] 4. `hp:lineBreak`(강제 줄바꿈) 처리: **기본값 `"\n"`** (HWP 5.0 코드 10과 동일. 본문 단락에서는 Markdown 소프트 줄바꿈으로 남고, 표 셀에서는 렌더러가 `<br>` 로 바꿈 — 두 포맷 동일 출력). 대안: 공백 한 칸 — `INLINE_TEXT` 의 lineBreak 값과 `EXPECTED_BLOCKS_INLINE`/`EXPECTED_MARKDOWN_INLINE`, 단위 테스트 4번 기대 변경. HWP 5.0 과 결과가 달라지므로 비권장.
- [x] 5. 실제 샘플 폴더: **기본값 `tests/fixtures/unsupported/hwpx/` → `tests/fixtures/hwpx/` 로 이동** (지원하게 되므로 폴더 이름을 맞춤. gitignore 대상이라 git 변경 없음). 대안: 그대로 두기 — Stage 1 의 mv 생략, §4.8 `REAL_HWPX_DIR` 를 `fixtures/unsupported/hwpx` 로, §4.10 fixtures README 문구를 그 경로로.
- 결정 (2026-10-22, 사용자): 5개 모두 기본값. 승인됨. Stage 4b 건너뜀.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| `lxml-stubs` 의 `XMLParser` 시그니처에 `no_network`/`huge_tree` 등 kwarg 가 없어 mypy 실패 | 낮음 | §3 규칙: 2회 수정 후 스텁 원인이면 §7-1 (b) `types-lxml` 로 전환(orchestrator). 그래도 실패면 BLOCKED |
| `uv add "lxml>=5"` 가 현재 파이썬(3.12, macOS arm64)용 휠을 못 받음 | 낮음 | 로그 확인 후 재시도 1회, 실패 시 BLOCKED (네트워크·사용자 결정) |
| 주석·엔티티 노드의 `.tag` 가 함수 객체여서 `child.tag == HP_T` 비교나 `QName(child)` 가 예외 | 중간 | §4.3 함정 명시 + 단위 테스트 5·7·8번이 잡는다. `isinstance(child.tag, str)` 가드 필수 |
| 실제 샘플 기대 숫자 `(1,1)/(80,31)/(32,8)` 가 구현과 1~2 차이(공백만 있는 단락·strip 차이) | 낮음 | §4.4 규칙이 시뮬레이션과 동일(`strip` 후 빈 단락 생략). 차이가 나면 implementer 가 어느 `hp:p` 인지 NEEDS 에 적고 orchestrator 가 규칙 위반인지 판단. 2회 실패 → BLOCKED |
| `resolve_entities=False` 에서 lxml 이 미해석 엔티티를 `_Entity` 노드로 남기지 않고 예외를 내는 등 버전별 동작 차이 | 낮음 | 테스트 7·8 실패 시 실제 동작을 PROGRESS 에 기록. 어느 쪽이든 외부 파일 내용이 출력에 없으면 보안 목표는 달성 — 기대값 조정은 planner 재호출(계약 변경) |
| 실제 샘플 파일명(공백·괄호·한글)이 subprocess·pytest id 에서 깨짐 | 낮음 | 리스트 인자 + `PYTHONIOENCODING=utf-8`(conftest 기존). pytest `ids=lambda p: p.name`. `-k` 필터는 ASCII 테스트 이름만 쓴다 |
| 샘플 2(셀 2226개) 변환이 E2E 전체 시간을 늘림 | 낮음 | 표준 라이브러리 파싱도 1초 미만. E2E 전체 1분 이내 예상 |
| `hwp5/body.py` 의 `_place_cells` 를 import 하거나 공용화하려는 "개선" | 중간 | OUT 명시. hwpx/body.py 에 같은 동작을 복제하고, 통일은 후속 태스크로 RESULT 에 적는다 |
| 두 포맷의 컨트롤 단락 처리 차이(HWP 5.0 흘려보냄 / HWPX 무시)가 나중에 혼란 | 중간 | §4.9 셋째 결정에 명시, RESULT "못 한 것" 에 기록, 각주 태스크에서 통일 |

## 9. 예상 비용
- 예상 단계 수: 7 (+ 조건부 4b) · 서브에이전트 호출: 17회 (implementer 4, test-writer 1, runner 6, reviewer 5, scribe 1; 재시도 여유 +3 = 최대 20) · 주 모델: opus 25% / sonnet 35% / haiku 40%
- 근거: 전 태스크 실적 7단계 17회(단계마다 runner·reviewer 동반). Stage 1·4b 는 orchestrator 직접이라 호출 0.

## 변경 이력
- 2026-10-22 17:59 (orchestrator, S2 reviewer 판정): §4.4 `parse_table` 의사코드의 `_int_attr(...) or len(trs)`를 "속성이 없을 때만 tr/tc 수로 대체, 명시적 0은 표 생략(hwp5/body.py와 동일)"으로 수정. §4.7 케이스 13(rowCnt="0" → [])과 모순이던 의사코드 문구 오류. 계약·범위 변경 아님.
