# PLAN — T-20261022-image-extract hwp2md 이미지 추출 (HWP 5.0·HWPX → out/<stem>_images/ + 상대 경로 링크)

> 작성: planner fable · 2026-10-22 23:40 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> BASE: main `3e8248d` · 브랜치 `ai/T-20261022-image-extract` · 현재 단위 171 · E2E 33 통과(합계 204) · mypy 16 source files · ruff format 36 files

## 0. 한 줄 목표
사용자는 `hwp2md input.hwp|input.hwpx -o out/` 한 줄로, 문서 본문의 임베디드 이미지가 `out/<stem>_images/img_001.png …` 파일로 추출되고 Markdown의 제자리에 `![그림 1](<stem>_images/img_001.png)` 상대 경로 링크로 남은 `.md`를 얻을 수 있다. CLI 2행에 `이미지 K개`, 3행에 저장 폴더가 보인다. HWP 5.0과 HWPX는 같은 입력 내용에서 바이트 단위로 같은 Markdown과 같은 이미지 파일을 낸다. (README MVP 4종 중 마지막 항목)

### 0.1 OpenSpec 연동
- change: `openspec/changes/image-extract/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate image-extract` (planner 확인: `Change 'image-extract' is valid`, `--strict`도 통과)
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행.

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | `Image` 블록 + `images.py`(확장자 정규화·`ImageNamer`) + `test_images.py` | S1 |
| 1.2 | `render_blocks(…, image_dir=)` 가 `![그림 N](dir/file)` 렌더(공백→`%20`) | S1 |
| 1.3 | `convert()` 이미지 파일 쓰기 + `ConvertResult.image_count/image_dir/image_files`, 이미지 없으면 폴더 없음 | S1 |
| 2.1 | 합성 HWP 5.0: `SynthImage`·BIN_DATA·BinData 스트림·gso 레코드·fixture 4종 + 구조 테스트 | S2 |
| 2.2 | 이미지 없는 기존 HWP 5.0 fixture sha256 6종·DocInfo 30B 불변 | S2 |
| 3.1 | `records.py` 상수 4개, `docinfo.py` `BinDataEntry`·`parse_bin_data`·`DocInfo.bin_data` | S3 |
| 3.2 | `reader.py` `Hwp5Package`·`read_hwp5_package`·`BinDataStore.resolve` | S3 |
| 3.3 | `body.py` `parse_picture_bindata_id`·gso 분기·셀 `None`·flatten Image 무시 → fixture 4종 블록 일치 | S3 |
| 4.1 | 합성 HWPX: `pic_paragraph_xml`·셀 그림·manifest item·`BinData/image{k}.{ext}` 엔트리 + 구조 테스트 | S4 |
| 4.2 | 이미지 없는 기존 HWPX fixture sha256 3종·content.hpf 불변 | S4 |
| 5.1 | `hwpx/bindata.py` `parse_manifest`·`BinItemStore`, `reader.py` `HwpxPackage`·`read_hwpx_package`(50MB 상한) | S5 |
| 5.2 | `hwpx/body.py` `hp:pic`·`hp:container` → Image, `hp:ctrl`·셀 제외 → fixture 4종 블록 일치 | S5 |
| 5.3 | `test_cross_format.py` 이미지 fixture 4종 두 포맷 동일성 | S5 |
| 6.1 | `docs/decisions.md` 3건, `README.md`, `tests/fixtures/README.md` | S6 |
| 7.1 | `cli.py` 2행 ` · 이미지 K개`, 3행 `  이미지: <dir>/ (n files)` | S7 |
| 8.1 | `tests/e2e/test_cli_image.py` 신규 + 기존 E2E 정규식 3줄 | S8 |
| 8.2 | E2E 전체 45 passed + 증거 파일 | S8 |
| 9.1 | reviewer 증거 확인 → scribe RESULT/STATE | S9 |

## 1. 범위
### 포함 (IN)
- 블록 모델: `src/hwp2md/blocks.py`에 `Image(file_name, data)` 추가, `Block = Paragraph | Table | Image`(§4.2-A). `src/hwp2md/__init__.py` export 1줄.
- 이미지 헬퍼 신규 `src/hwp2md/images.py`: `IMAGE_DIR_SUFFIX`, `image_dir_name`, `sniff_ext`, `normalize_ext`, `ImageNamer`(§4.2-B).
- 렌더러 `src/hwp2md/render.py`: `render_blocks(blocks, *, image_dir="")`, `Image` → `![그림 N](dir/file)`(§4.2-C).
- 변환 `src/hwp2md/convert.py`: 이미지 파일 쓰기, `ConvertResult` 필드 3개 추가(§4.2-D).
- HWP 5.0: `records.py` 상수 4줄, `docinfo.py` BIN_DATA 파싱, `reader.py` BinData 스트림 수집·`BinDataStore`, `body.py` gso→그림 레코드→Image(§4.3·§4.4).
- HWPX: 신규 `hwpx/bindata.py`(manifest·`BinItemStore`), `reader.py` BinData 엔트리 수집, `body.py` `hp:pic`·`hp:container`(§4.6·§4.7).
- 합성 생성기 확장 `tests/synth_hwp5.py`·`tests/synth_hwpx.py`(`SynthImage`, fixture 4종). 이미지 없는 입력에서 바이트 불변(§4.5·§4.8).
- CLI 2행·3행(§4.12, orchestrator 전용 단계).
- 문서: `docs/decisions.md` 3건, `README.md` 2곳, `tests/fixtures/README.md` 1절(§4.14).
- 단위 테스트 신규 3파일(`test_images.py`, `test_hwp5_bindata.py`, `test_hwpx_bindata.py`) + 기존 3파일 추가(`test_synth_hwp5.py`, `test_synth_hwpx.py`, `test_cross_format.py`), E2E 신규 `tests/e2e/test_cli_image.py` + 기존 E2E 정규식 3줄(§4.13).

### 제외 (OUT) — 절대 건드리지 않는다
- 표 셀 안 이미지의 셀 내 인라인 렌더(`| ![..] |`). 이번에는 셀 안 이미지를 해석하지 않는다(§7-4).
- 머리말·꼬리말·글상자(도형 텍스트)·각주 안 이미지. HWPX `hp:ctrl` 무시 정책 유지(§7-5).
- 외부 링크(BIN_DATA 종류 LINK) 이미지, OLE 개체(`SHAPE_COMPONENT_OLE`), STORAGE 종류 바이너리.
- 이미지 포맷 변환(WMF/EMF→PNG), 크기 조정, Pillow 등 의존성 추가(§7-7).
- alt 텍스트 추출(`hp:shapeComment`, 캡션). alt 는 `그림 N` 고정.
- CLI 옵션 추가(`--images`, `--no-images`, 폴더명 지정). `cli.py`는 S7의 2행·3행 외 변경 없음.
- `--split`, `--meta`, 각주, 리스트 렌더, `read_paragraphs`·`render_markdown` 호환 래퍼의 동작 변경.
- HWP 5.0 "표 아닌 컨트롤 안 단락 흘려보냄" 정책 변경(머리말 안 gso 가 HWP 5.0 에서는 흘러나올 수 있음 — 실제 샘플 영향 없음, 통일은 각주 태스크).

### 건드리면 안 되는 파일/디렉토리
- `src/hwp2md/cli.py` (orchestrator 전용. S7만), `pyproject.toml`, `uv.lock`, `CLAUDE.md`, `.ai/STATE.md`(S9 scribe 제외), `.ai/tasks/*/PLAN.md`, `.gitignore`, `.claude/**`, `openspec/**`(orchestrator 가 tasks.md 체크)
- `docs/vision.md`, `tests/fixtures/*.hwp`, `tests/fixtures/hwpx/*.hwpx`, `tests/fixtures/unsupported/**`, `tests/e2e/conftest.py`
- `src/hwp2md/detect.py`, `src/hwp2md/errors.py`, `src/hwp2md/hwpx/header.py`
- `tests/unit/test_hwp5_body.py`, `tests/unit/test_hwp5_records.py`, `tests/unit/test_hwp5_docinfo.py`, `tests/unit/test_hwpx_body.py`, `tests/unit/test_hwpx_reader.py`, `tests/unit/test_hwpx_header.py`, `tests/unit/test_detect.py`, `tests/unit/test_convert.py`, `tests/unit/test_render_heading.py`, `tests/e2e/test_cli_table.py` (기존 그대로 통과해야 한다)

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| S1 | 합성 이미지 fixture 가 두 포맷에서 같은 Markdown·같은 파일 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e/test_cli_image.py -q` | `13 passed`(합성 8 + 실제 샘플 5), failed 0 |
| S2 | E2E 전체 통과 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/e2e -q` | `46 passed`(기존 33 + 신규 13), failed 0, skipped 0 |
| S3 | 기존 테스트 회귀 없음 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit -q` | `216 passed` 이상(기존 171 + 신규 45 이상), failed 0 |
| S4 | 린트·포맷·타입 | `cd /Users/illi/illy-projects/hwp2md && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | `All checks passed!`, `… already formatted`(42 files), `Success: no issues found in 18 source files` |
| S5 | 실제 HWPX 샘플 이미지 추출 | `cd /Users/illi/illy-projects/hwp2md && rm -rf /tmp/h2m && uv run hwp2md "tests/fixtures/hwpx/브라더 공공기관 보고서 양식.hwpx" -o /tmp/h2m && shasum -a 256 "/tmp/h2m/브라더 공공기관 보고서 양식_images/img_001.png" && grep -c '^!\[그림 1\](브라더%20공공기관%20보고서%20양식_images/img_001.png)$' "/tmp/h2m/브라더 공공기관 보고서 양식.md"` | stdout 2행 `  단락 32개 · 표 8개 · 이미지 1개`, 3행 `  이미지: /tmp/h2m/브라더 공공기관 보고서 양식_images/ (1 files)`, sha256 `f9be5b73bc6b32a79f15e52fd850b24c95203459756867104a6c297dbfc58632`, grep → `1` |
| S6 | 이미지 없는 실제 샘플 4개 출력 불변 | `cd /Users/illi/illy-projects/hwp2md && rm -rf /tmp/h2m2 && for f in tests/fixtures/form200005063113.hwp tests/fixtures/form210001070268.hwp "tests/fixtures/hwpx/(서식1) 비영리법인 현황 제출 양식.hwpx" "tests/fixtures/hwpx/(서식2) 사업실적 및 사업계획 제출 양식.hwpx"; do uv run hwp2md "$f" -o /tmp/h2m2 \| sed -n '2,3p'; done; ls /tmp/h2m2 \| grep -c _images` | 정확히 4줄 `  단락 118개 · 표 8개`, `  단락 47개 · 표 0개`, `  단락 1개 · 표 1개`, `  단락 80개 · 표 31개`(3행 없음, `이미지` 글자 없음), 마지막 grep → `0` |
| S7 | 이미지 없는 기존 합성 입력의 바이트 불변 | `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit/test_synth_hwp5.py tests/unit/test_synth_hwpx.py -q -k "unchanged or sha256"` | failed 0 (기존 sha256 9개 + DocInfo·header 바이트 테스트 전부 통과) |
| S8 | 기존 E2E 파일 수정 범위 | `cd /Users/illi/illy-projects/hwp2md && git diff 3e8248d --stat -- tests/e2e/test_cli_convert.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py` | 세 파일 각 `1 +, 1 -` (정규식 1줄씩) |
| S9 | 익명화 | `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` | `sanitize-check: OK` |
| S10 | 증거 파일 | `ls .ai/tasks/T-20261022-image-extract/screenshots` | `image_hwp5.md`, `image_hwpx.md`, `image_reuse.md`, `image_cell.md`, `image_missing.md`, `image_hwp5_img_001.png`, `real_hwpx_img_001.png`, 실제 샘플 `.md` 5개. reviewer 가 `image_hwp5.md`를 Read 로 열어 `![그림 1](doc_images/img_001.png)`·`## 1. 결과`·`![그림 2](doc_images/img_002.jpg)` 3줄을, `real_hwpx_img_001.png`를 Read 로 열어 로고 그림이 보이는지 눈으로 확인 |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 오류로 수정 2회 실패
- 동일 단계 재시도 3회 초과
- 단계 하나 도구 호출 상한 초과: implementer 40회, test-writer 30회, reviewer 15회, runner 10회, scribe 10회 (초과 시 PARTIAL 보고 후 orchestrator 반환)
- 단계 하나 30분 초과
- §4 계약(필드명·시그니처·바이트 레이아웃·XML 요소명·파일명 규칙·기대 숫자)을 바꿔야만 진행 가능 → BLOCKED(planner 재호출)
- OUT 범위 파일(§1) 수정 없이는 진행 불가
- 기존 단위·E2E 테스트가 §4.13-A 정규식 3줄 외의 수정 없이는 통과하지 않음
- 실제 샘플 기대값(§4.11)과 구현 결과가 다르고 원인이 샘플 조사 오류로 판명 → BLOCKED(기대값은 계약이므로 planner 가 재조사)
- 의존성 추가가 필요하다고 판단됨(Pillow 등) → BLOCKED(§7-7 은 기본값 거절)

## 4. 인터페이스 계약 (모든 단계가 이 값을 그대로 쓴다. 바꾸면 BLOCKED)

### 4.1 파일 레이아웃 (새 파일 경로는 이것만 허용)
```
src/hwp2md/blocks.py                    # S1 (Image 추가)
src/hwp2md/images.py                    # S1 신규
src/hwp2md/render.py                    # S1
src/hwp2md/convert.py                   # S1
src/hwp2md/__init__.py                  # S1 (Image export 1줄 + __all__ 1줄)
tests/unit/test_images.py               # S1 신규
tests/synth_hwp5.py                     # S2
tests/unit/test_synth_hwp5.py           # S2 (케이스 추가, 기존 23개 불변)
src/hwp2md/hwp5/records.py              # S3 (상수 4줄 추가만)
src/hwp2md/hwp5/docinfo.py              # S3
src/hwp2md/hwp5/reader.py               # S3
src/hwp2md/hwp5/body.py                 # S3
tests/unit/test_hwp5_bindata.py         # S3 신규
tests/synth_hwpx.py                     # S4
tests/unit/test_synth_hwpx.py           # S4 (케이스 추가, 기존 16개 불변)
src/hwp2md/hwpx/bindata.py              # S5 신규
src/hwp2md/hwpx/reader.py               # S5
src/hwp2md/hwpx/body.py                 # S5
tests/unit/test_hwpx_bindata.py         # S5 신규
tests/unit/test_cross_format.py         # S5 (케이스 추가, 기존 5개 불변)
docs/decisions.md, README.md, tests/fixtures/README.md   # S6
src/hwp2md/cli.py                       # S7 (orchestrator 전용 파일, 전용 단계)
tests/e2e/test_cli_image.py             # S8 신규
tests/e2e/test_cli_convert.py           # S8 (79행 정규식 1곳만)
tests/e2e/test_cli_heading.py           # S8 (45행 정규식 1곳만)
tests/e2e/test_cli_hwpx.py              # S8 (32행 정규식 1곳만)
.ai/tasks/T-20261022-image-extract/RESULT.md, .ai/STATE.md   # S9 (scribe)
```
`tests/` 아래에 `__init__.py`를 만들지 않는다. `src/hwp2md/hwp5/__init__.py`·`hwpx/__init__.py`는 수정하지 않는다.

### 4.2 블록 모델·이미지 헬퍼·렌더·변환 결과 (S1) — §7-1·2·3·8 기본값
**A. `blocks.py`**
```python
@dataclass(frozen=True)
class Image:
    file_name: str  # "img_001.png" — 리더가 부여. 같은 원본(바이너리 항목)은 같은 file_name
    data: bytes     # 원본 바이트 (변환 없음)


Block = Paragraph | Table | Image
```
- `Paragraph`·`Table` 불변. `__init__.py`: `from .blocks import Block, Image, Paragraph, Table`, `__all__`에 `"Image"` 추가(알파벳 순 위치: `"Hwp2mdError"` 다음).

**B. `images.py` (신규)**
```python
IMAGE_DIR_SUFFIX = "_images"
_MAGIC: tuple[tuple[bytes, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8\xff", "jpg"), (b"GIF87a", "gif"), (b"GIF89a", "gif"), (b"BM", "bmp"),
)

def image_dir_name(stem: str) -> str:
    """f"{stem}{IMAGE_DIR_SUFFIX}" """

def sniff_ext(data: bytes) -> str | None:
    """_MAGIC 순서대로 startswith. 없으면 None."""

def normalize_ext(ext: str | None, data: bytes) -> str:
    """ext 를 strip() 후 앞의 '.' 제거·소문자. 결과가 "" 이면 sniff_ext(data), 그것도 None 이면 "bin"."""

class ImageNamer:
    """같은 key 는 같은 이름. 첫 등장 순서대로 img_001, img_002, … (3자리 0 채움, 1000 이상은 자릿수 늘어남)."""
    def __init__(self) -> None: ...            # self._names: dict[str, str] = {}
    def name_for(self, key: str, ext: str) -> str:
        """key 가 처음이면 f"img_{len(self._names) + 1:03d}.{ext}" 를 등록·반환, 아니면 등록된 이름 반환(ext 무시)."""
```

**C. `render.py`**
```python
def _render_image(img: Image, n: int, image_dir: str) -> str:
    """path = f"{image_dir}/{img.file_name}" if image_dir else img.file_name
    return f"![그림 {n}]({path.replace(' ', '%20')})" """

def render_blocks(blocks: Sequence[Block], *, image_dir: str = "") -> str:
    """Image 블록마다 n 을 1부터 증가(등장 순, file_name 중복 무관). Paragraph/Table 처리·"\\n\\n" join·끝 "\\n"·빈 문자열 생략은 불변."""
```
- `render_markdown` 호환 래퍼 불변. `image_dir=""`(기본)인 기존 호출은 바이트 동일.

**D. `convert.py`**
```python
@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int
    table_count: int
    heading_count: int
    markdown: str
    image_count: int = 0                 # Image 블록 수 (링크 수. 같은 파일 재참조도 센다)
    image_dir: Path | None = None        # image_files 가 비어 있지 않을 때만 out_dir / image_dir_name(stem)
    image_files: tuple[Path, ...] = ()   # 실제로 쓴 파일(고유 file_name 첫 등장 순). 절대/상대는 out_dir 과 같은 기준


def _write_images(blocks: Sequence[Block], target: Path) -> tuple[Path, ...]:
    """Image 블록을 순회해 처음 보는 file_name 마다 target / file_name 에 data 를 쓴다(bytes, 덮어쓰기).
    Image 가 0개면 target 을 만들지 않고 () 반환. 1개 이상이면 target.mkdir(parents=True, exist_ok=True) 후 쓴다."""
```
- `convert()`: `image_dir_rel = image_dir_name(source.stem)`; `markdown = render_blocks(blocks, image_dir=image_dir_rel)`; `files = _write_images(blocks, target_dir / image_dir_rel)`; `image_count = sum(isinstance(b, Image) for b in blocks)`; `image_dir = target_dir / image_dir_rel if files else None`. `.md` 쓰기·다른 카운트·`read_blocks` 디스패처 불변. 이미지가 없는 문서는 Markdown 바이트가 현재와 동일.
- 링크 경로의 기준은 `.md` 파일 위치(같은 out_dir) → `<stem>_images/img_NNN.<ext>` 상대 경로. 공백만 `%20`(다른 문자는 그대로).

### 4.3 HWP 5.0 DocInfo BIN_DATA — 바이트 레이아웃 (S3 파서, S2 생성기가 같은 값을 쓴다)
근거: HWP 5.0 스펙 표 12·13 + pyhwp `binmodel/tagid18_bin_data.py`(독립 구현) 교차 확인. 실제 HWP 5.0 샘플 2개에는 BIN_DATA 레코드가 0개라 실제 바이트 검증은 없다(§8).

**A. 레코드 태그 (`records.py`에 4줄 추가. 기존 줄 불변)**
```python
HWPTAG_BIN_DATA = 0x12  # 18. DocInfo 바이너리 데이터 (ID = 등장 순서, 1부터)
HWPTAG_SHAPE_COMPONENT = 0x4C  # 76. 개체 요소 (파서는 읽지 않음, fixture가 씀)
HWPTAG_SHAPE_COMPONENT_PICTURE = 0x55  # 85. 그림 개체 (UINT16 bindata_id @71)
CTRL_ID_GSO = b"gso "[::-1]  # == b" osg". 그리기 개체 컨트롤
```
**B. BIN_DATA payload**
| offset | 타입 | 뜻 |
|---|---|---|
| 0 | UINT16 attr | 비트 0~3 종류: 0 LINK, 1 EMBEDDING, 2 STORAGE · 비트 4~5 압축: 0 문서 기본, 1 압축, 2 비압축 |
| 2 | UINT16 storage_id | EMBEDDING·STORAGE 만. 스트림 `BinData/BIN{storage_id:04X}.{ext}` |
| 4 | BSTR ext | EMBEDDING 만: UINT16 글자 수 n + UTF-16LE n글자 (예: "png" → `03 00 70 00 6e 00 67 00`) |
| LINK | BSTR abspath, BSTR relpath | 파서는 읽지 않음 (LINK 는 건너뜀) |

**C. `docinfo.py`**
```python
BIN_DATA_LINK, BIN_DATA_EMBEDDING, BIN_DATA_STORAGE = 0, 1, 2

@dataclass(frozen=True)
class BinDataEntry:
    storage_type: int   # attr & 0xF
    compression: int    # (attr >> 4) & 0x3
    storage_id: int     # EMBEDDING/STORAGE: UINT16 @2 ; LINK: 0
    ext: str            # EMBEDDING: BSTR @4 를 strip·소문자·앞 '.' 제거 ; 그 외 ""

def parse_bin_data(payload: bytes) -> BinDataEntry:
    """len < 2 → Hwp2mdError("truncated BIN_DATA record"). EMBEDDING/STORAGE 인데 len < 4,
    EMBEDDING 인데 len < 6 또는 6 + 2n → 같은 메시지."""

@dataclass(frozen=True)
class DocInfo:
    para_shapes: tuple[ParaShape, ...]
    bin_data: tuple[BinDataEntry, ...] = ()   # 등장 순서. bindata_id = index + 1

    def heading_level(self, para_shape_id: int) -> int: ...   # 불변
    def bin_data_entry(self, bindata_id: int) -> BinDataEntry | None:
        """1 <= bindata_id <= len(bin_data) 면 bin_data[bindata_id - 1], 아니면 None."""

EMPTY_DOCINFO = DocInfo(para_shapes=())   # bin_data 기본값 ()
def parse_docinfo(data: bytes) -> DocInfo:   # PARA_SHAPE 와 BIN_DATA(0x12) 를 각각 등장 순서대로 수집. data == b"" → EMPTY_DOCINFO
```
기존 `DocInfo((ParaShape(...),))` 위치 인자 호출·`test_hwp5_docinfo.py` 전부 그대로 통과해야 한다.

### 4.4 HWP 5.0 본문 그림 개체 — 레코드 트리·파서 (S3)
근거: pyhwp `binmodel/tagid69_shape_component_picture.py` — `ShapePicture` = `BorderLine`(COLORREF 4 + INT32 4 + UINT32 4 = 12) + `ImageRect`(Coord×4 = 32) + `ImageClip`(SHWPUNIT×4 = 16) + `Margin`(HWPUNIT16×4 = 8) + `PictureInfo`(INT8 brightness, INT8 contrast, BYTE effect, **UINT16 bindata_id**) → bindata_id offset = 12+32+16+8+3 = **71**, 최소 길이 73. 이후 BYTE border_transparency, UINT32 instance_id, 그림 효과(버전별)는 읽지 않는다.

**A. 레코드 트리** (단락 level L)
```
PARA_HEADER(L) · PARA_TEXT(L+1, 확장 컨트롤 11 + " osg" 자리표시자) · PARA_CHAR_SHAPE(L+1) · PARA_LINE_SEG(L+1)
CTRL_HEADER(L+1, payload[:4] == CTRL_ID_GSO)
  SHAPE_COMPONENT(L+2)                     # 그룹($con)이면 안쪽에 SHAPE_COMPONENT 가 더 중첩됨
    SHAPE_COMPONENT_PICTURE(L+3)           # 파서는 level 을 보지 않고 gso 서브트리(level > ctrl level) 안의 모든 0x55 를 순서대로 쓴다
```
**B. `body.py`**
```python
class ImageResolver(Protocol):
    def resolve(self, bindata_id: int) -> Image | None: ...

def parse_picture_bindata_id(payload: bytes) -> int:
    """len(payload) < 73 → Hwp2mdError("truncated SHAPE_COMPONENT_PICTURE record"). return UINT16 LE @71."""

def parse_blocks(records: Iterable[Record], docinfo: DocInfo = EMPTY_DOCINFO,
                 bin_data: ImageResolver | None = None) -> list[Block]

def _parse_paragraph(recs, i, level, docinfo, bin_data) -> tuple[str, int, list[Block], int]:
    # 기존 분기 순서 유지. 표 분기 다음, 일반 컨트롤 분기 앞에 추가:
    #   elif r.tag_id == HWPTAG_CTRL_HEADER and r.level == level + 1 and r.payload[:4] == CTRL_ID_GSO:
    #       images, i = _parse_gso(recs, i, r.level, bin_data); trailing.extend(images)
    # 일반 컨트롤 분기의 안쪽 단락 재귀에는 bin_data 를 그대로 넘긴다.

def _parse_gso(recs, i, ctrl_level, bin_data) -> tuple[list[Image], int]:
    """i 는 CTRL_HEADER 위치. i += 1 후 recs[i].level > ctrl_level 인 동안:
    tag == HWPTAG_SHAPE_COMPONENT_PICTURE → bid = parse_picture_bindata_id(payload);
    bin_data 가 None 이 아니고 resolve(bid) 가 Image 면 append. 그 외 레코드는 건너뜀. (list, i) 반환."""

def _parse_table(recs, i, ctrl_level, docinfo) -> tuple[Table | None, int]:
    # 셀 단락: _parse_paragraph(recs, i, ctrl_level + 1, docinfo, None)  ← 셀 안 이미지는 해석·명명하지 않는다 (§7-4)
    # flatten 루프: isinstance(b, Paragraph) → text, isinstance(b, Table) → flat, 그 외(Image) → 무시
```
**C. `reader.py`**
```python
@dataclass(frozen=True)
class Hwp5Package:
    header: FileHeader
    docinfo: bytes             # 압축이면 해제됨, 없으면 b""
    sections: list[bytes]      # 압축이면 해제됨, Section<N> 오름차순
    bin_data: dict[str, bytes] # "BinData/<NAME>" 스트림 원본 바이트(해제 안 함). 키 = <NAME> (대소문자 원본 그대로)

def read_hwp5_package(path: Path) -> Hwp5Package
    # 기존 read_streams 본문 + ole.listdir() 중 첫 요소가 "BinData" 인 스트림 전부 수집. 예외 종류·메시지 불변.
def read_streams(path: Path) -> tuple[bytes, list[bytes]]   # 호환 래퍼: pkg = read_hwp5_package(path); return pkg.docinfo, pkg.sections
def read_sections(path) -> list[bytes]                      # 불변 (read_streams(path)[1])

class BinDataStore:
    """ImageResolver 구현. 문서 하나당 인스턴스 하나(ImageNamer 포함)."""
    def __init__(self, docinfo: DocInfo, streams: Mapping[str, bytes], *, compressed: bool) -> None
    def resolve(self, bindata_id: int) -> Image | None:
        # 1) 캐시에 있으면 그대로 반환 (None 결과도 캐시)
        # 2) entry = docinfo.bin_data_entry(bindata_id); entry 가 None 이거나 storage_type != BIN_DATA_EMBEDDING → None
        # 3) 스트림: 이름을 .upper() 로 비교. 1차 f"BIN{entry.storage_id:04X}.{entry.ext}".upper() 정확 일치,
        #    2차 f"BIN{entry.storage_id:04X}.".upper() 로 시작하는 이름 중 sorted() 첫 것. 없으면 None
        # 4) 압축 해제: entry.compression == 2 → raw ; == 1 → _inflate ; == 0 → compressed 이면 _inflate 아니면 raw.
        #    _inflate 가 zlib.error 를 내면 raw 를 쓴다
        # 5) ext = normalize_ext(entry.ext, data); Image(file_name=self._namer.name_for(str(bindata_id), ext), data=data)

def read_blocks(path: Path) -> list[Block]:
    # pkg = read_hwp5_package(path); docinfo = parse_docinfo(pkg.docinfo)
    # store = BinDataStore(docinfo, pkg.bin_data, compressed=pkg.header.compressed)
    # 섹션마다 parse_blocks(iter_records(section), docinfo, store)
def read_paragraphs(path) -> list[str]   # 불변
```

### 4.5 합성 HWP 5.0 생성기 확장 (`tests/synth_hwp5.py`, S2) — 이미지 없는 입력에서 바이트 불변
```python
@dataclass(frozen=True)
class SynthImage:
    data: bytes
    ext: str                # "png" 등 소문자, 점 없음
    missing: bool = False   # True → 참조(BIN_DATA 레코드 / manifest item / hc:img)만 쓰고 바이너리 본체(스트림·zip 엔트리)는 쓰지 않는다

@dataclass(frozen=True)
class SynthCell:
    paragraphs: tuple[str | SynthHeading | SynthImage, ...]   # SynthImage 허용 추가. 나머지 필드 불변

Item = str | SynthTable | SynthHeading | SynthImage

def collect_images(items: Sequence[Item]) -> list[SynthImage]:
    """문서 순서(최상위 항목 순, 표는 cells 순 → paragraphs 순)로 처음 보는 SynthImage(동등 비교)만 모은다. 바이너리 항목 k = index + 1."""

def build_bin_data(storage_id: int, ext: str) -> bytes:
    """struct.pack("<HHH", 0x0001, storage_id, len(ext)) + ext.encode("utf-16-le")   # EMBEDDING, 압축 비트 0(문서 기본). "png" → 12 bytes"""

def build_docinfo(*, outline: bool = False, images: Sequence[SynthImage] = ()) -> bytes:
    """DOCUMENT_PROPERTIES → [BIN_DATA(level 1) × len(images), k=1..] → (outline 이면) PARA_SHAPE×8 + STYLE×8. images=() 이면 현재와 바이트 동일(30 B / outline 레코드 포함 시 §이전 플랜 값)."""

_PIC_W, _PIC_H = 8196, 3382
CHID_PIC = b"$pic"[::-1]            # == b"cip$"
_SHAPE_COMPONENT_LEN = 196          # chid0(4)+chid(4)+188 zero bytes. 파서는 읽지 않는다
_PIC_BINDATA_ID_OFFSET = 71

def build_ctrl_header_gso() -> bytes:
    """CTRL_ID_GSO + struct.pack("<IiiIIiHHHHII", 0, 0, 0, _PIC_W, _PIC_H, 0, 0, 0, 0, 0, 0, 0)  # 44 bytes, 표 컨트롤과 같은 모양"""
def build_shape_component_pic() -> bytes:
    """CHID_PIC + CHID_PIC + b"\\x00" * 188   # 196 bytes"""
def build_picture_record(bindata_id: int) -> bytes:
    """struct.pack("<IiI", 0, 0, 0)                           # BorderLine 12
     + struct.pack("<8i", 0, 0, _PIC_W, 0, _PIC_W, _PIC_H, 0, _PIC_H)   # ImageRect 32
     + struct.pack("<4i", 0, 0, 0, 0)                          # ImageClip 16
     + struct.pack("<4H", 0, 0, 0, 0)                          # Margin 8
     + struct.pack("<bbBH", 0, 0, 0, bindata_id)               # PictureInfo 5 → bindata_id @71
     + struct.pack("<BI", 0, 0)                                # border_transparency, instance_id → 총 78 bytes"""

def build_picture_control(bindata_id: int, *, level: int, last: bool) -> bytes:
    """표 자리표시자 단락과 같은 구조(§4.4-A): PARA_HEADER(level, ctrl mask 0x800, nchars 9 | last bit) · PARA_TEXT(level+1,
    pack("<H",11) + CTRL_ID_GSO + 8 zero + pack("<H",11) + b"\\r\\x00") · PARA_CHAR_SHAPE · PARA_LINE_SEG ·
    CTRL_HEADER(level+1, build_ctrl_header_gso()) · SHAPE_COMPONENT(level+2, build_shape_component_pic()) ·
    SHAPE_COMPONENT_PICTURE(level+3, build_picture_record(bindata_id))"""

def build_table_control(table, *, level, last, images: Sequence[SynthImage] = ()) -> bytes
    # 셀 단락이 SynthImage p 면 build_picture_control(images.index(p) + 1, level=level + 2, last=(i == last_index)); 나머지 불변
def build_section0(items: Sequence[Item], images: Sequence[SynthImage] | None = None) -> bytes
    # images None → collect_images(items). SynthImage item → build_picture_control(images.index(item) + 1, level=0, last=last)
def build_cfb(streams: Mapping[str, bytes]) -> bytes
    # 키: 필수 3개("FileHeader", "DocInfo", "BodyText/Section0") + 선택 "BinData/<NAME>" 임의 개수. 그 외 키 → ValueError. 각 스트림 < 4096 bytes 유지.
    # BinData 키가 없으면 현재 코드 경로와 바이트 동일.
    # BinData 키가 있으면: ministream 순서 = _STREAM_KEYS 순 → BinData 키를 (len(NAME), NAME.upper()) 로 정렬한 순.
    #   디렉터리 엔트리: 0 Root(child=1) · 1 BodyText(left=2, right=3, child=4) · 2 DocInfo(left=5) · 3 FileHeader · 4 Section0 ·
    #   5 "BinData" storage(child=6) · 6.. 각 스트림(이름 = NAME, 정렬 순서대로 right 로 연결, 마지막은 NOSTREAM)
    #   (CFB 형제 비교 규칙 = 이름 길이 → 대문자 사전순: BinData(7) < DocInfo(7) < BodyText(8) < FileHeader(10) 이므로 BinData 는 DocInfo 의 left)
    #   entries_count = len(entries); dir_sectors = ceil(entries_count * 128 / 512) 로 일반화. FAT 체인·MiniFAT 1섹터(128 미니섹터) 제한 유지.
def build_hwp5(paragraphs, *, properties=0x1) -> bytes
    # images = collect_images(paragraphs); docinfo = build_docinfo(outline=has_heading(paragraphs), images=images)
    # streams["BinData/BIN{k:04X}.{img.ext}"] = compress_raw(img.data) if properties & 1 else img.data  (k = index+1, missing 은 제외)
```
- **E. 바이트 불변 검증**: 기존 `test_synth_hwp5.py`의 sha256 6개(`test_fixture_bytes_unchanged_sha256`)·`_BASE_DOCINFO_SHA256`·`_BASE_PLAIN_SECTION_SHA256`가 수정 없이 통과해야 한다(이미지 없는 입력 → `collect_images == []` → 모든 새 분기 비활성).

### 4.6 HWPX 바이너리 참조 — XML 레이아웃·파서 (S5, 생성기 S4 가 같은 값을 쓴다)
근거: 실제 샘플 `브라더 공공기관 보고서 양식.hwpx` 조사(§4.11). `hp:pic` 자식 `hc:img`(core 네임스페이스) 의 `binaryItemIDRef="image1"` → `Contents/content.hpf` 의 `<opf:item id="image1" href="BinData/image1.png" media-type="image/png" isEmbeded="1"/>` → zip 엔트리 `BinData/image1.png`. `header.xml` 에는 binData 목록이 없다.

**A. `hwpx/bindata.py` (신규)**
```python
HWPX_CONTENT_HPF = "Contents/content.hpf"
NS_OPF = "http://www.idpf.org/2007/opf/"
OPF_ITEM = f"{{{NS_OPF}}}item"
BIN_DATA_PREFIX = "BinData/"
MAX_IMAGE_BYTES = 50 * 1024 * 1024

def parse_manifest(data: bytes) -> dict[str, str]:
    """opf:item 전부에서 id → href (둘 다 있는 것만). 파서 옵션은 reader.make_parser() 와 동일(resolve_entities=False, no_network=True, huge_tree=False).
    XMLSyntaxError → {} (manifest 가 깨져도 변환은 계속, 이름 fallback 사용)."""

class BinItemStore:
    """문서 하나당 인스턴스 하나(ImageNamer 포함)."""
    def __init__(self, manifest: Mapping[str, str], entries: Mapping[str, bytes]) -> None   # entries 키 = zip 엔트리 전체 이름("BinData/image1.png")
    def resolve(self, item_id: str) -> Image | None:
        # 1) 캐시 (None 포함)
        # 2) href = manifest.get(item_id); href 가 entries 에 있으면 (href, entries[href])
        #    아니면 sorted(entries) 중 name.startswith(f"{BIN_DATA_PREFIX}{item_id}.") 첫 것; 없으면 None
        # 3) ext = 선택된 이름의 마지막 '.' 뒤 (없으면 None) → normalize_ext(ext, data)
        # 4) Image(file_name=self._namer.name_for(item_id, ext), data=data)
```
**B. `hwpx/reader.py`**
```python
@dataclass(frozen=True)
class HwpxPackage:
    header: bytes | None      # Contents/header.xml
    sections: list[bytes]
    manifest: bytes | None    # Contents/content.hpf
    bin_data: dict[str, bytes]   # "BinData/" 로 시작하고 "/" 로 끝나지 않는 엔트리 전부. file_size > MAX_IMAGE_BYTES → Hwp2mdError(f"binary item too large: {name} ({size} bytes)")

def read_hwpx_package(path: Path) -> HwpxPackage      # 기존 read_package 본문 + manifest + bin_data. 예외 종류·메시지 불변
def read_package(path: Path) -> tuple[bytes | None, list[bytes]]   # 호환 래퍼: (pkg.header, pkg.sections)
def read_blocks(path: Path) -> list[Block]:
    # pkg = read_hwpx_package(path); info = …(불변); manifest = parse_manifest(pkg.manifest) if pkg.manifest is not None else {}
    # store = BinItemStore(manifest, pkg.bin_data); 섹션마다 parse_section(root, info, store)
```
**C. `hwpx/body.py`**
```python
NS_HC = "http://www.hancom.co.kr/hwpml/2011/core"   # synth_hwpx.NS_HC 와 같은 값 (S5 테스트가 동일성 확인)
HP_PIC = f"{{{NS_HP}}}pic"
HP_CONTAINER = f"{{{NS_HP}}}container"
HC_IMG = f"{{{NS_HC}}}img"

def parse_paragraph(p, header: HeaderInfo = EMPTY_HEADER, bin_items: BinItemStore | None = None) -> list[Block]:
    # run 자식: HP_T → buf ; HP_TBL → flush + table ; HP_PIC → _append_image(child) ;
    #           HP_CONTAINER → for pic in child.iter(HP_PIC): _append_image(pic) ; 그 외(secPr, ctrl, footNote, rect, …) 무시
    # _append_image(pic): bin_items None → 아무것도 안 함. img = pic.find(HC_IMG); img None 또는 binaryItemIDRef 없음/"" → 아무것도 안 함.
    #                     image = bin_items.resolve(ref); image 가 None → 아무것도 안 함 ; 있으면 flush() 후 blocks.append(image)
def parse_section(root, header: HeaderInfo = EMPTY_HEADER, bin_items: BinItemStore | None = None) -> list[Block]
# _cell_text 는 parse_paragraph(p) 를 bin_items 없이 호출(셀 안 이미지 해석 안 함 — hwp5 와 동일). flatten 에 isinstance(b, Table) 명시, 그 외 무시
```

### 4.7 합성 HWPX 생성기 확장 (`tests/synth_hwpx.py`, S4) — 이미지 없는 입력에서 바이트 불변
```python
from synth_hwp5 import Item, SynthCell, SynthHeading, SynthImage, SynthTable, collect_images, has_heading   # 재정의 금지
NS_HC 기존 상수 유지 (body.NS_HC 와 같은 값)

def pic_xml(k: int, *, pic_id: int) -> str:
    # f'<hp:pic id="{pic_id}" zOrder="0" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="{pic_id + 1000}" reverse="0">'
    # + '<hp:offset x="0" y="0"/><hp:orgSz width="8196" height="3382"/><hp:curSz width="0" height="0"/><hp:flip horizontal="0" vertical="0"/>'
    # + '<hp:rotationInfo angle="0" centerX="4098" centerY="1691" rotateimage="1"/><hp:renderingInfo/>'
    # + f'<hc:img binaryItemIDRef="image{k}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
    # + '<hp:imgRect/><hp:imgClip left="0" right="0" top="0" bottom="0"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="0" dimheight="0"/><hp:effects/>'
    # + '<hp:sz width="8196" widthRelTo="ABSOLUTE" height="3382" heightRelTo="ABSOLUTE" protect="0"/>'
    # + '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
    # + '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment/></hp:pic>'
def pic_paragraph_xml(k: int, *, para_id: int, first: bool = False) -> str:
    # f'<hp:p id="{para_id}" {P_ATTRS}>' + (SECPR_RUN if first else "") + f'<hp:run charPrIDRef="0">{pic_xml(k, pic_id=2000 + para_id)}</hp:run></hp:p>'
def cell_xml(cell: SynthCell, images: Sequence[SynthImage] = ()) -> str
    # 셀 단락이 SynthImage 면 pic_paragraph_xml(images.index(p) + 1, para_id=0); 나머지 불변
def table_xml(table, *, para_id, first=False, images: Sequence[SynthImage] = ()) -> str   # cell_xml 에 images 전달
def section_xml(items: Sequence[Item], images: Sequence[SynthImage] | None = None) -> bytes
    # images None → collect_images(items). SynthImage item → pic_paragraph_xml(images.index(item) + 1, para_id=i, first=(i == 0))
def manifest_items(images: Sequence[SynthImage]) -> str
    # "".join(f'<opf:item id="image{k}" href="BinData/image{k}.{img.ext}" media-type="image/{img.ext}" isEmbeded="1"/>' for k, img in enumerate(images, 1))
def hwpx_entries(items, *, more_sections=()) -> dict[str, bytes]
    # images = 모든 섹션을 순서대로 collect_images 한 뒤 처음 보는 것만 합친 리스트 (섹션 간 공유)
    # content.hpf: header item 바로 뒤에 manifest_items(images) 삽입 (images 비면 현재와 바이트 동일)
    # 엔트리 순서: mimetype, version.xml, META-INF/container.xml, Contents/content.hpf, Contents/header.xml,
    #              BinData/image{k}.{ext} (k 오름차순, missing 제외), Contents/section{i}.xml …
    # section_xml(sec_items, images) 로 호출
```
- **E. 바이트 불변 검증**: 기존 `test_synth_hwpx.py` sha256 3개(`test_fixture_bytes_unchanged_sha256`)·`test_header_default_bytes_unchanged`·엔트리 순서 테스트가 수정 없이 통과해야 한다.

### 4.8 공용 이미지 fixture (`tests/synth_hwp5.py` 끝에 추가. E2E·단위 테스트가 이 이름을 그대로 import)
```python
PNG_1X1: bytes = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415478da63f8cfc0000003010100f70341430000000049454e44ae426082"
)  # 69 bytes, 1×1 RGB PNG. sha256 2e9b06dc65a4dec84a3eb3124553ec93ca27c78221e64ab2177d0f1412cfcb20. hex 상수(zlib 버전 무관)
JPEG_STUB: bytes = b"\xff\xd8\xff\xe0" + bytes(range(16)) + b"\xff\xd9"  # 22 bytes. 유효 JPEG 아님(바이트 왕복만 검증)
FIXTURE_IMAGE_PNG = SynthImage(PNG_1X1, "png")
FIXTURE_IMAGE_JPG = SynthImage(JPEG_STUB, "jpg")

# 모든 EXPECTED_MARKDOWN_IMAGE* 는 입력 파일 stem 이 "doc" 일 때(doc.hwp / doc.hwpx → doc_images/)
FIXTURE_ITEMS_IMAGES: list[Item] = ["그림 앞 단락", FIXTURE_IMAGE_PNG, SynthHeading("1. 결과", 2), FIXTURE_IMAGE_JPG, "그림 뒤 단락"]
EXPECTED_BLOCKS_IMAGES = [Paragraph("그림 앞 단락"), Image("img_001.png", PNG_1X1), Paragraph("1. 결과", 2), Image("img_002.jpg", JPEG_STUB), Paragraph("그림 뒤 단락")]
EXPECTED_MARKDOWN_IMAGES = "그림 앞 단락\n\n![그림 1](doc_images/img_001.png)\n\n## 1. 결과\n\n![그림 2](doc_images/img_002.jpg)\n\n그림 뒤 단락\n"
EXPECTED_COUNTS_IMAGES = (2, 0, 1, 2)                 # (paragraph_count, table_count, heading_count, image_count)
EXPECTED_IMAGE_FILES_IMAGES = ("img_001.png", "img_002.jpg")

FIXTURE_ITEMS_IMAGE_REUSE: list[Item] = [FIXTURE_IMAGE_PNG, "중간 단락", FIXTURE_IMAGE_PNG]
EXPECTED_BLOCKS_IMAGE_REUSE = [Image("img_001.png", PNG_1X1), Paragraph("중간 단락"), Image("img_001.png", PNG_1X1)]
EXPECTED_MARKDOWN_IMAGE_REUSE = "![그림 1](doc_images/img_001.png)\n\n중간 단락\n\n![그림 2](doc_images/img_001.png)\n"
EXPECTED_COUNTS_IMAGE_REUSE = (1, 0, 0, 2)
EXPECTED_IMAGE_FILES_IMAGE_REUSE = ("img_001.png",)

FIXTURE_ITEMS_IMAGE_IN_CELL: list[Item] = [
    SynthTable(rows=1, cols=2, cells=(SynthCell((FIXTURE_IMAGE_JPG, "값"), col=0, row=0), SynthCell(("나",), col=1, row=0))),
    FIXTURE_IMAGE_PNG,
]   # 바이너리 항목: 1 = JPG(셀), 2 = PNG. 셀 이미지는 해석되지 않으므로 PNG 가 img_001 이 된다
EXPECTED_BLOCKS_IMAGE_IN_CELL = [Table([["값", "나"]]), Image("img_001.png", PNG_1X1)]
EXPECTED_MARKDOWN_IMAGE_IN_CELL = "| 값 | 나 |\n|---|---|\n\n![그림 1](doc_images/img_001.png)\n"
EXPECTED_COUNTS_IMAGE_IN_CELL = (0, 1, 0, 1)
EXPECTED_IMAGE_FILES_IMAGE_IN_CELL = ("img_001.png",)

FIXTURE_ITEMS_IMAGE_MISSING: list[Item] = ["앞", SynthImage(b"", "png", missing=True), FIXTURE_IMAGE_PNG, "뒤"]
EXPECTED_BLOCKS_IMAGE_MISSING = [Paragraph("앞"), Image("img_001.png", PNG_1X1), Paragraph("뒤")]
EXPECTED_MARKDOWN_IMAGE_MISSING = "앞\n\n![그림 1](doc_images/img_001.png)\n\n뒤\n"
EXPECTED_COUNTS_IMAGE_MISSING = (2, 0, 0, 1)
EXPECTED_IMAGE_FILES_IMAGE_MISSING = ("img_001.png",)

IMAGE_FIXTURES = [  # (items, expected_blocks, expected_markdown, expected_counts, expected_files) — parametrize 용, ids ["images", "reuse", "in_cell", "missing"]
    (FIXTURE_ITEMS_IMAGES, EXPECTED_BLOCKS_IMAGES, EXPECTED_MARKDOWN_IMAGES, EXPECTED_COUNTS_IMAGES, EXPECTED_IMAGE_FILES_IMAGES),
    (FIXTURE_ITEMS_IMAGE_REUSE, …), (FIXTURE_ITEMS_IMAGE_IN_CELL, …), (FIXTURE_ITEMS_IMAGE_MISSING, …),
]
```
- 그림 자리표시자 단락(hwp5)은 텍스트가 `""`로 디코드되어 Paragraph 를 만들지 않고 trailing Image 만 남는다. hwpx 는 `hp:run` 안에 `hp:pic` 만 있어 `flush()` 가 비어 있다. 두 포맷 블록 리스트가 같다.
- 비압축 변형(properties=0)도 섹션·DocInfo·BinData 각각 4096 bytes 미만.

### 4.9 단위 테스트 계약 (파일·케이스 이름 고정)
**A. `tests/unit/test_images.py` (S1)**
1. `test_image_block_equality_and_block_union` — `Image("a.png", b"x") == Image("a.png", b"x")`, `!= Image("a.png", b"y")`, `"Image" in hwp2md.__all__`
2. `test_image_dir_name` — `image_dir_name("doc") == "doc_images"`, `image_dir_name("브라더 공공기관 보고서 양식") == "브라더 공공기관 보고서 양식_images"`
3. `test_sniff_ext` — PNG_1X1 → "png", JPEG_STUB → "jpg", `b"GIF89a…"` → "gif", `b"BM…"` → "bmp", `b"zzz"` → None
4. `test_normalize_ext` — `("PNG", b"")` → "png", `(".Jpg", b"")` → "jpg", `("", PNG_1X1)` → "png", `(None, b"zzz")` → "bin", `("  ", JPEG_STUB)` → "jpg"
5. `test_image_namer_sequence_and_reuse` — `name_for("a","png") == "img_001.png"`, `name_for("b","jpg") == "img_002.jpg"`, `name_for("a","jpg") == "img_001.png"`(재호출은 ext 무시), `name_for("c","bin") == "img_003.bin"`
6. `test_render_image_with_dir` — `render_blocks([Image("img_001.png", b"")], image_dir="doc_images") == "![그림 1](doc_images/img_001.png)\n"`
7. `test_render_image_without_dir` — `image_dir` 생략 → `"![그림 1](img_001.png)\n"`
8. `test_render_image_numbering_counts_occurrences` — `[Paragraph("a"), Image("img_001.png", b""), Image("img_001.png", b""), Image("img_002.jpg", b"")]` → `"a\n\n![그림 1](doc_images/img_001.png)\n\n![그림 2](doc_images/img_001.png)\n\n![그림 3](doc_images/img_002.jpg)\n"`
9. `test_render_image_dir_space_percent_encoded` — `image_dir="두 단어_images"` → `"![그림 1](두%20단어_images/img_001.png)\n"`
10. `test_render_existing_blocks_unchanged` — `render_blocks([Paragraph("a"), Paragraph("h", 1), Table([["x","y"]])])` 가 `image_dir` 유무에 관계없이 `"a\n\n# h\n\n| x | y |\n|---|---|\n"`
11. `test_write_images_dedupes_and_creates_dir` — `_write_images([Image("img_001.png", b"A"), Image("img_001.png", b"B"), Image("img_002.jpg", b"C")], tmp_path/"d")` → `(d/img_001.png, d/img_002.jpg)`, 내용 `b"A"`·`b"C"`(첫 등장 우선)
12. `test_write_images_no_images_no_dir` — `_write_images([Paragraph("a")], tmp_path/"d") == ()`, `not (tmp_path/"d").exists()`
13. `test_convert_without_images_has_defaults` — `convert(write_hwp5(tmp_path/"s.hwp", FIXTURE_PARAGRAPHS), tmp_path/"out")` → `image_count == 0`, `image_dir is None`, `image_files == ()`, `not (tmp_path/"out"/"s_images").exists()`, `markdown == EXPECTED_MARKDOWN`

**B. `tests/unit/test_synth_hwp5.py` 추가 (S2. 기존 23개 불변)**
1. `test_collect_images_order_and_dedupe` — `collect_images(FIXTURE_ITEMS_IMAGE_IN_CELL) == [FIXTURE_IMAGE_JPG, FIXTURE_IMAGE_PNG]`, `collect_images(FIXTURE_ITEMS_IMAGE_REUSE) == [FIXTURE_IMAGE_PNG]`, `collect_images(FIXTURE_ITEMS_HEADINGS) == []`
2. `test_bin_data_record_layout` — `build_bin_data(1, "png") == bytes.fromhex("0100 0100 0300 7000 6e00 6700".replace(" ", ""))`(12 B)
3. `test_docinfo_with_images_records` — `build_docinfo(images=[FIXTURE_IMAGE_PNG, FIXTURE_IMAGE_JPG])` 레코드 태그 순서 `[0x10, 0x12, 0x12]`, level `[0, 1, 1]`; `build_docinfo()` 는 `build_docinfo(images=())` 와 바이트 동일(30 B)
4. `test_picture_record_offsets` — `build_picture_record(7)` 길이 78, `struct.unpack_from("<H", payload, 71) == (7,)`, `payload[:12] == b"\x00"*12`
5. `test_picture_control_record_tree` — `iter_records(build_picture_control(1, level=0, last=True))` 의 `(tag, level)` == `[(0x42,0),(0x43,1),(0x44,1),(0x45,1),(0x47,1),(0x4C,2),(0x55,3)]`; CTRL_HEADER payload[:4] == `CTRL_ID_GSO`; SHAPE_COMPONENT payload 길이 196, 앞 8 B == `CHID_PIC*2`; PARA_TEXT 디코드 == `""`
6. `test_bindata_streams_in_cfb` — `write_hwp5(tmp/"i.hwp", FIXTURE_ITEMS_IMAGES)`: `olefile.listdir()` 에 `["BinData","BIN0001.png"]`, `["BinData","BIN0002.jpg"]` 포함; `_inflate(스트림) == PNG_1X1`, `== JPEG_STUB`; `properties=0` 이면 raw 바이트가 그대로
7. `test_missing_image_has_record_but_no_stream` — `FIXTURE_ITEMS_IMAGE_MISSING`: DocInfo BIN_DATA 레코드 2개(storage_id 1, 2), `BinData` 스트림은 `BIN0002.png` 하나
8. `test_cell_image_paragraph_levels` — `FIXTURE_ITEMS_IMAGE_IN_CELL` 섹션에서 SHAPE_COMPONENT_PICTURE 레코드 2개: level `[5, 3]`(셀 안 L=2 단락 → +3, 최상위 → 3), bindata_id `[1, 2]`
9. `test_build_cfb_rejects_unknown_key` — `build_cfb({…3개…, "Other/x": b""})` → `ValueError`
10. `test_image_fixture_round_trips_text` — `read_blocks(write_hwp5(tmp/"i.hwp", FIXTURE_ITEMS_IMAGES))` 의 Paragraph 텍스트 == `["그림 앞 단락", "1. 결과", "그림 뒤 단락"]` (S3 전에는 Image 블록 없음 — 이 단언만)

**C. `tests/unit/test_hwp5_bindata.py` (S3)**
1. `test_tag_constants_match_generator` — `records.HWPTAG_BIN_DATA == 0x12`, `HWPTAG_SHAPE_COMPONENT == 0x4C`, `HWPTAG_SHAPE_COMPONENT_PICTURE == 0x55`, `records.CTRL_ID_GSO == b" osg"`
2. `test_parse_bin_data_embedding` — `parse_bin_data(build_bin_data(3, "PNG"))` == `BinDataEntry(1, 0, 3, "png")`
3. `test_parse_bin_data_link_and_storage` — attr `0x0000` + 아무 BSTR → `storage_type 0, storage_id 0, ext ""`; attr `0x0022`(STORAGE, 비압축) + `storage_id 5` → `BinDataEntry(2, 2, 5, "")`
4. `test_parse_bin_data_truncated` — `b"\x01"`, `b"\x01\x00\x01"`, `b"\x01\x00\x01\x00\x03\x00p\x00"` 각각 `Hwp2mdError` 메시지 `truncated BIN_DATA record`
5. `test_parse_docinfo_collects_bin_data` — `parse_docinfo(build_docinfo(outline=True, images=[FIXTURE_IMAGE_PNG, FIXTURE_IMAGE_JPG]))` → `bin_data` 길이 2, ext `["png","jpg"]`, `para_shapes` 8개(기존 동작 유지); `bin_data_entry(0) is None`, `(1).storage_id == 1`, `(3) is None`
6. `test_parse_picture_bindata_id` — `build_picture_record(9)` → 9; 72 B → `Hwp2mdError` `truncated SHAPE_COMPONENT_PICTURE record`
7. `test_store_resolve_compressed_and_raw` — `read_hwp5_package(write_hwp5(…, FIXTURE_ITEMS_IMAGES))` → `BinDataStore(parse_docinfo(pkg.docinfo), pkg.bin_data, compressed=True).resolve(1) == Image("img_001.png", PNG_1X1)`, `resolve(2) == Image("img_002.jpg", JPEG_STUB)`; `properties=0` 변형에서도 같은 결과
8. `test_store_resolve_missing_link_and_out_of_range` — missing fixture: `resolve(1) is None`, `resolve(2) == Image("img_001.png", PNG_1X1)`(번호는 해석된 순서); `resolve(99) is None`; LINK 엔트리(수작업 `DocInfo(para_shapes=(), bin_data=(BinDataEntry(0,0,0,""),))`) → `resolve(1) is None`
9. `test_store_case_insensitive_stream_name` — `BinDataStore(docinfo, {"BIN0001.PNG": PNG_1X1}, compressed=False).resolve(1) == Image("img_001.png", PNG_1X1)`; `{"bin0001.jpeg": JPEG_STUB}` (ext "png" 기록) → 2차 탐색으로 찾고 ext 는 `normalize_ext("png", …) == "png"`
10. `test_store_inflate_fallback_to_raw` — `compressed=True` 인데 스트림이 raw PNG → `zlib.error` 흡수 → `data == PNG_1X1`
11. `test_read_blocks_image_fixtures` — parametrize `IMAGE_FIXTURES` 4개 → `read_blocks(write_hwp5(tmp/"doc.hwp", items)) == expected_blocks`
12. `test_read_blocks_uncompressed_image_fixture` — `properties=0`, `FIXTURE_ITEMS_IMAGES` → `== EXPECTED_BLOCKS_IMAGES`
13. `test_gso_without_resolver_yields_no_image` — `parse_blocks(iter_records(build_section0(FIXTURE_ITEMS_IMAGES)))`(bin_data 생략) → Paragraph 3개만, Image 0개
14. `test_read_streams_wrapper_unchanged` — `read_streams(p) == (pkg.docinfo, pkg.sections)`

**D. `tests/unit/test_synth_hwpx.py` 추가 (S4. 기존 16개 불변)**
1. `test_ns_hc_constant_present` — `synth_hwpx.NS_HC == "http://www.hancom.co.kr/hwpml/2011/core"`
2. `test_entries_with_images_order_and_bytes` — `hwpx_entries(FIXTURE_ITEMS_IMAGES)` 키 순서 == `ENTRY_NAMES[:5] + ["BinData/image1.png", "BinData/image2.jpg", "Contents/section0.xml"]`; 값 `== PNG_1X1`, `== JPEG_STUB`
3. `test_manifest_items_inserted_after_header` — content.hpf 를 `xml.etree.ElementTree` 로 파싱: `opf:item` id 순서 `["header", "image1", "image2", "section0"]`; image1 `href="BinData/image1.png"`, `media-type="image/png"`, `isEmbeded="1"`
4. `test_content_hpf_unchanged_without_images` — `hwpx_entries(FIXTURE_ITEMS_HEADINGS)["Contents/content.hpf"]` 가 BASE 와 동일: item id 순서 `["header", "section0"]`, `b"BinData" not in` 바이트
5. `test_pic_paragraph_structure` — `section_xml(FIXTURE_ITEMS_IMAGES)` 최상위 `hp:p[1]` 의 run 자식 == `[hp:pic]`, `hp:pic/hc:img@binaryItemIDRef == "image1"`, `hp:p[3]` → `"image2"`
6. `test_cell_image_paragraph` — `FIXTURE_ITEMS_IMAGE_IN_CELL`: 첫 `hp:tc` 의 `hp:p` 2개, 첫 번째에 `hc:img@binaryItemIDRef == "image1"`, 두 번째 텍스트 "값"; 최상위 pic → `"image2"`
7. `test_missing_image_has_manifest_but_no_entry` — `FIXTURE_ITEMS_IMAGE_MISSING`: manifest item `image1`·`image2` 둘 다 있고 엔트리는 `BinData/image2.png` 만
8. `test_image_fixture_round_trips_text` — hwpx `read_blocks(write_hwpx(tmp/"doc.hwpx", FIXTURE_ITEMS_IMAGES))` Paragraph 텍스트 == `["그림 앞 단락", "1. 결과", "그림 뒤 단락"]` (S5 전 — 이 단언만)

**E. `tests/unit/test_hwpx_bindata.py` (S5)**
1. `test_ns_constants_match_generator` — `body.NS_HC == synth_hwpx.NS_HC`, `bindata.NS_OPF == synth_hwpx.NS_OPF`, `bindata.HWPX_CONTENT_HPF == "Contents/content.hpf"`
2. `test_parse_manifest_ids_to_href` — `parse_manifest(hwpx_entries(FIXTURE_ITEMS_IMAGES)["Contents/content.hpf"])` == `{"header": "Contents/header.xml", "image1": "BinData/image1.png", "image2": "BinData/image2.jpg", "section0": "Contents/section0.xml"}`
3. `test_parse_manifest_malformed_returns_empty` — `parse_manifest(b"<opf:package") == {}`; `parse_manifest(b'<?xml version="1.0"?><x/>') == {}`
4. `test_store_resolve_via_manifest` — `BinItemStore({"image1": "BinData/image1.png"}, {"BinData/image1.png": PNG_1X1}).resolve("image1") == Image("img_001.png", PNG_1X1)`; 두 번째 `resolve("image1")` 동일 객체 동등
5. `test_store_fallback_by_name` — manifest `{}`, entries `{"BinData/image1.PNG": PNG_1X1}` → `resolve("image1") == Image("img_001.png", PNG_1X1)`(ext 소문자화); `resolve("nope") is None`
6. `test_store_sniffs_ext_when_unknown` — entries `{"BinData/image1": PNG_1X1}`(확장자 없음), manifest `{"image1": "BinData/image1"}` → `file_name == "img_001.png"`; `{"BinData/image1.dat": b"zzz"}` → `"img_001.dat"`
7. `test_read_hwpx_package_collects_bin_data` — `read_hwpx_package(write_hwpx(…, FIXTURE_ITEMS_IMAGES))` → `bin_data` 키 `{"BinData/image1.png", "BinData/image2.jpg"}`, `manifest is not None`, `header is not None`, `len(sections) == 1`; `read_package(p) == (pkg.header, pkg.sections)`
8. `test_read_hwpx_package_rejects_large_bin_data` — `monkeypatch.setattr(hwpx.reader, "MAX_IMAGE_BYTES", 10)` 후 `read_hwpx_package(...)` → `Hwp2mdError` 메시지 `binary item too large`
9. `test_read_blocks_image_fixtures` — parametrize `IMAGE_FIXTURES` 4개 → hwpx `read_blocks(write_hwpx(tmp/"doc.hwpx", items)) == expected_blocks`
10. `test_pic_inside_ctrl_header_ignored` — 수작업 섹션 XML: `hp:p/hp:run/hp:ctrl/hp:header/hp:subList/hp:p/hp:run/hp:pic(hc:img image1)` + 최상위 `hp:p/hp:run/hp:pic(image1)` → `parse_section(root, EMPTY_HEADER, store)` 결과 Image 1개 `img_001.png`
11. `test_pic_inside_container_extracted` — `hp:p/hp:run/hp:container/hp:pic(image1)` + `hp:pic(image2)` → Image 2개 순서대로 `img_001.png`, `img_002.jpg`
12. `test_pic_without_img_or_ref_skipped` — `hp:pic` 에 `hc:img` 없음 / `binaryItemIDRef` 없음 / `""` → Image 0개, 예외 없음
13. `test_parse_paragraph_without_store_yields_no_image` — `parse_paragraph(p)`(bin_items 생략) → Paragraph 만

**F. `tests/unit/test_cross_format.py` 추가 (S5. 기존 5개 불변)**
1. `test_image_fixtures_same_result_both_formats` — parametrize `IMAGE_FIXTURES` 4개(ids `images, reuse, in_cell, missing`): `convert(write_hwp5(tmp/"doc.hwp", items), tmp/"out5")`·`convert(write_hwpx(tmp/"doc.hwpx", items), tmp/"outx")` 각각 `markdown == expected_markdown`, `(paragraph_count, table_count, heading_count, image_count) == expected_counts`, `tuple(p.name for p in image_files) == expected_files`, 각 파일 바이트 == 해당 fixture 바이트(`img_001.png` → PNG_1X1 / `img_002.jpg` → JPEG_STUB), `image_dir == out/"doc_images"`; 두 결과 `markdown` 바이트 동일
2. `test_image_fixture_no_jpg_file_when_only_in_cell` — in_cell fixture 두 포맷 모두 `out/doc_images` 안 파일 목록 == `["img_001.png"]`

### 4.10 실제 샘플 조사 결과 (2026-10-22 planner, 읽기 전용. implementer·test-writer는 추측하지 말고 이 숫자를 쓴다)
**HWP 5.0**
| 파일 | 버전 | OLE 스트림 | `BinData` 스토리지 | DocInfo BIN_DATA 레코드 | Section0 CTRL_HEADER ctrl_id 분포 | 0x4C·0x55 레코드 | 현재 (단락, 표, 제목) | **기대 (단락, 표, 제목, 이미지)** |
|---|---|---|---|---|---|---|---|---|
| `form200005063113.hwp` | `0x05000006` | FileHeader, DocInfo, BodyText/Section0, PrvImage, PrvText, SummaryInformation | **없음** | **0** | `secd` 1, `cold` 1, `tbl ` 8, `nwno` 2 (gso 0) | 0 · 0 | (118, 8, 0) | **(118, 8, 0, 0)** — 출력 불변 |
| `form210001070268.hwp` | `0x05000202` | + DocOptions/_LinkDoc, Scripts/* | **없음** | **0** | `secd` 1, `cold` 1 (gso 0) | 0 · 0 | (47, 0, 0) | **(47, 0, 0, 0)** — 출력 불변 |
- 실제 HWP 5.0 양성 샘플은 없다. 그림 레코드 레이아웃(§4.3·§4.4)은 스펙 + pyhwp 소스로 교차 확인했고 실제 바이트 검증은 사용자가 샘플을 추가할 때 E2E 가 자동 수행한다(§7-9, §8). 저장소 밖 로컬 `.hwp` 는 HWP 3.0 이거나 비공개 자료라 조사하지 않았다.

**HWPX**
| 파일 | zip 엔트리 수 | `BinData/*` | section0 `hp:pic` | `hc:img@binaryItemIDRef` | `hp:container` | manifest(`content.hpf`) image item | header.xml binData 목록 | 현재 (단락, 표, 제목) | **기대 (단락, 표, 제목, 이미지)** |
|---|---|---|---|---|---|---|---|---|---|
| `(서식1) 비영리법인 현황 제출 양식.hwpx` | 11 | 없음 | 0 | 0 | 0 | 없음 | 없음 | (1, 1, 0) | **(1, 1, 0, 0)** |
| `(서식2) 사업실적 및 사업계획 제출 양식.hwpx` | 11 | 없음 | 0 | 0 | 0 | 없음 | 없음 | (80, 31, 0) | **(80, 31, 0, 0)** |
| `브라더 공공기관 보고서 양식.hwpx` | 14 | `BinData/image1.png` **46249 B**, PNG(`89 50 4E 47`), sha256 `f9be5b73bc6b32a79f15e52fd850b24c95203459756867104a6c297dbfc58632` | **2** (둘 다 `image1` 참조) | 2 | 0 | `<opf:item id="image1" href="BinData/image1.png" media-type="image/png" isEmbeded="1"/>` | 없음 | (32, 8, 0) | **(32, 8, 0, 1)** · 파일 `img_001.png` 1개 |
- 브라더 샘플의 `hp:pic` 위치: ① `hs:sec/hp:p/hp:run/hp:ctrl/hp:header/hp:subList/hp:p/hp:run/hp:pic` — **머리말 안** → `hp:ctrl` 무시 정책으로 제외. ② `hs:sec/hp:p[17]/hp:run/hp:pic` (최상위 59개 `hp:p` 중 18번째, `paraPrIDRef=23`) — run 자식은 `hp:pic` 하나, 다음 run 의 `hp:t` 는 빈 문자열 → 단락 수 32 불변, Image 1개. `hp:pic` 자식 `hc:img` 속성: `binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"`. `hp:pic` 속성 `textWrap="TOP_AND_BOTTOM"`, `hp:pos/@treatAsChar` 존재 — 파서는 보지 않는다.
- 기대 Markdown 줄: `![그림 1](브라더%20공공기관%20보고서%20양식_images/img_001.png)` 정확히 1줄. 폴더 `브라더 공공기관 보고서 양식_images/`.

### 4.11 CLI 2행·3행 (S7, `src/hwp2md/cli.py`) — §7-10 기본값
현재 49~52행
```python
    summary = f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개"
    if result.heading_count:
        summary += f" · 제목 {result.heading_count}개"
    print(summary)
```
을 아래로 교체(그 외 글자 하나도 바꾸지 않는다):
```python
    summary = f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개"
    if result.heading_count:
        summary += f" · 제목 {result.heading_count}개"
    if result.image_count:
        summary += f" · 이미지 {result.image_count}개"
    print(summary)
    if result.image_files:
        print(f"  이미지: {result.image_dir}/ ({len(result.image_files)} files)")
```
- 결과: 이미지 0개 → 현재와 동일 2행 / 이미지 K≥1 → 2행 `… · 이미지 K개` + 3행 `  이미지: <out_dir>/<stem>_images/ (n files)`. 구분자 ` · `(공백 + U+00B7 + 공백). 종료 코드·stderr·`--version`·1행 불변. `image_dir` 는 `-o` 로 받은 경로 기준(1행의 `{result.output}` 과 같은 기준).

### 4.12 E2E 계약 (S8)
**A. 기존 파일 수정 — 정확히 3줄 (test-writer). 다른 글자는 바꾸지 않는다**
- `tests/e2e/test_cli_convert.py` 79행: `(?: · 제목 \d+개)?$"` → `(?: · 제목 \d+개)?(?: · 이미지 \d+개)?$"`
- `tests/e2e/test_cli_heading.py` 45행: `(?: · 제목 (\d+)개)?$")` → `(?: · 제목 (\d+)개)?(?: · 이미지 \d+개)?$")`
- `tests/e2e/test_cli_hwpx.py` 32행: `(?: · 제목 \d+개)?$")` → `(?: · 제목 \d+개)?(?: · 이미지 \d+개)?$")`
- 이유: 브라더 샘플의 2행이 `  단락 32개 · 표 8개 · 이미지 1개`가 되어 `$` 앵커 정규식 2개(heading·hwpx)가 깨진다. convert 쪽은 HWP 5.0 샘플 추가 대비. 그룹 번호·의미 불변이므로 기존 단언은 그대로다.

**B. `tests/e2e/test_cli_image.py` 신규 — conftest의 `run_cli` 사용, `synth_hwp5`·`synth_hwpx`에서 import. 케이스 이름 고정**
```python
REAL_HWP5 = sorted(Path(__file__).resolve().parents[1].joinpath("fixtures").glob("*.hwp"))
REAL_HWPX = sorted(Path(__file__).resolve().parents[1].joinpath("fixtures", "hwpx").glob("*.hwpx"))
REAL_IMAGE_EXPECTED: dict[str, tuple[int, int, dict[str, str]]] = {   # (이미지 링크 수, 파일 수, {파일명: sha256}) §4.10
    "form200005063113.hwp": (0, 0, {}),
    "form210001070268.hwp": (0, 0, {}),
    "(서식1) 비영리법인 현황 제출 양식.hwpx": (0, 0, {}),
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx": (0, 0, {}),
    "브라더 공공기관 보고서 양식.hwpx": (1, 1, {"img_001.png": "f9be5b73bc6b32a79f15e52fd850b24c95203459756867104a6c297dbfc58632"}),
}
STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 (\d+)개)?(?: · 이미지 (\d+)개)?$")
STDOUT_LINE3 = re.compile(r"^  이미지: (.+)/ \((\d+) files\)$")
IMAGE_LINE = re.compile(r"^!\[그림 (\d+)\]\((\S+)\)$")
```
증거 복사 헬퍼 `_copy_evidence(src: Path, name: str)` — `ILLY_SHOT_DIR`(기본 `tests/e2e/screenshots`) 아래로 복사(.md 와 .png 모두 사용. .jpg 스텁은 복사하지 않는다).
1. `test_convert_images_hwp5_success` — `write_hwp5(tmp_path/"doc.hwp", FIXTURE_ITEMS_IMAGES)`, `out_dir = tmp_path/"out"`; 종료 0; `lines[0] == f"✓ doc.hwp → {out_dir / 'doc.md'}"`; `lines[1] == "  단락 2개 · 표 0개 · 제목 1개 · 이미지 2개"`; `lines[2] == f"  이미지: {out_dir / 'doc_images'}/ (2 files)"`; `lines[3] == ""`; md 내용 `== EXPECTED_MARKDOWN_IMAGES`; `(out_dir/"doc_images"/"img_001.png").read_bytes() == PNG_1X1`, `img_002.jpg == JPEG_STUB`; `sorted(os.listdir(out_dir/"doc_images")) == ["img_001.png", "img_002.jpg"]`; 증거 `image_hwp5.md`, `image_hwp5_img_001.png`
2. `test_convert_images_hwpx_success` — `write_hwpx(tmp_path/"doc.hwpx", FIXTURE_ITEMS_IMAGES)`; 같은 단언(`doc.hwpx`); 증거 `image_hwpx.md`
3. `test_image_reuse_single_file_both_formats` — `FIXTURE_ITEMS_IMAGE_REUSE` 두 포맷(`doc.hwp`/`doc.hwpx`, out5/outx): 2행 `"  단락 1개 · 표 0개 · 이미지 2개"`, 3행 `(1 files)`, md `== EXPECTED_MARKDOWN_IMAGE_REUSE`, 파일 목록 `["img_001.png"]`, `md5.read_bytes() == mdx.read_bytes()`; 증거 `image_reuse.md`
4. `test_image_in_table_cell_not_extracted_both_formats` — `FIXTURE_ITEMS_IMAGE_IN_CELL`: 2행 `"  단락 0개 · 표 1개 · 이미지 1개"`, 3행 `(1 files)`, md `== EXPECTED_MARKDOWN_IMAGE_IN_CELL`, 파일 목록 `["img_001.png"]`(`.jpg` 없음), 두 포맷 바이트 동일; 증거 `image_cell.md`
5. `test_missing_binary_skipped_both_formats` — `FIXTURE_ITEMS_IMAGE_MISSING`: 종료 0, 2행 `"  단락 2개 · 표 0개 · 이미지 1개"`, 3행 `(1 files)`, md `== EXPECTED_MARKDOWN_IMAGE_MISSING`, stderr `== ""`; 증거 `image_missing.md`
6. `test_no_image_keeps_two_line_output` — `write_hwp5(tmp/"plain.hwp", FIXTURE_ITEMS_HEADINGS)`: `result.stdout.split("\n") == [f"✓ plain.hwp → {out / 'plain.md'}", "  단락 2개 · 표 1개 · 제목 3개", ""]`, `not (out/"plain_images").exists()`; hwpx `FIXTURE_ITEMS_WITH_TABLE` → `[…, "  단락 2개 · 표 1개", ""]`, `"이미지" not in result.stdout`
7. `test_images_uncompressed_variant` — `write_hwp5(tmp/"doc.hwp", FIXTURE_ITEMS_IMAGES, properties=0)` → md `== EXPECTED_MARKDOWN_IMAGES`, `img_001.png == PNG_1X1`
8. `test_truncated_picture_record_exit_1` — `build_cfb({"FileHeader": build_file_header(properties=0), "DocInfo": build_docinfo(images=[FIXTURE_IMAGE_PNG]), "BodyText/Section0": build_section0(…)})` 에서 Section0 은 `build_picture_control(1, level=0, last=True)` 의 마지막 레코드(SHAPE_COMPONENT_PICTURE) payload 를 72 B 로 자른 수작업 바이트(`build_record(HWPTAG_SHAPE_COMPONENT_PICTURE, 3, build_picture_record(1)[:72])` 로 교체) → 종료 1, stderr 에 `truncated SHAPE_COMPONENT_PICTURE record`, `.md`·`_images` 없음
9. `test_real_fixture_images` — parametrize `REAL_HWP5 + REAL_HWPX` (ids = 이름): 종료 0; `m = STDOUT_LINE2.match(lines[1])`; `images = int(m[4] or 0)`; `(images, files, shas) = REAL_IMAGE_EXPECTED[name]`(없는 이름은 검사 생략, 변환 성공만); `images == 기대`; 이미지 0 이면 `len(lines) == 3`(2행 + 빈 줄)·`_images` 폴더 없음; 1 이상이면 `STDOUT_LINE3.match(lines[2])` 의 그룹2 == files, 폴더 `out/f"{stem}_images"` 안 파일 수 == files, 각 파일 sha256 == 기대; md 에서 `IMAGE_LINE` 매치 줄 수 == images 이고 각 경로가 `f"{stem.replace(' ', '%20')}_images/"` 로 시작; 증거 md 복사(`md.name`) + 이미지가 있으면 `img_001.png` 를 `real_hwpx_img_001.png` 로 복사
→ 합성 8 + 실제 5 = **13**? 아니오: 케이스 8(truncated)은 §2-S1 의 "합성 7"에 포함되지 않으므로 **S1·S2 숫자를 다음으로 확정한다: 합성 8 + 실제 5 = 13, E2E 전체 46.** (§2 표의 `12 passed`·`45 passed` 는 각각 `13 passed`·`46 passed` 로 읽는다 — 아래 "변경 이력 0" 참고)

### 4.13 문서 계약 (S6)
**A. `docs/decisions.md` 끝에 3건 추가 (기존 형식 `## 2026-10-22 <제목>` / `- 결정:` / `- 이유:`)**
1. `## 2026-10-22 이미지 블록: Image(file_name, data), out/<stem>_images/img_NNN.<ext>, 링크 ![그림 N](<stem>_images/…)` — 결정: 블록 모델 세 번째 블록, 리더가 원본별 파일명 부여(첫 등장 순 3자리), 렌더러가 등장 순 `그림 N` alt 와 `.md` 기준 상대 경로(공백 → `%20`), convert 가 고유 파일만 쓴다. 같은 원본 재참조는 파일 1개·링크 N개. 포맷 변환 없음(바이트 그대로). 이유: vision 시나리오 1 레이아웃, 블록 모델 일관성, 두 포맷 동일 출력, 의존성 0.
2. `## 2026-10-22 이미지 제외 범위: 표 셀·머리말·꼬리말·글상자 안 그림, LINK 그림, 본체 없는 참조는 건너뜀` — 결정: 셀 단락은 바이너리 해석 없이 파싱(번호 선점 방지), HWPX `hp:ctrl` 무시 유지, HWP 5.0 LINK/STORAGE 종류 무시, 누락 참조는 경고 없이 생략. 이유: GFM 셀 안 이미지는 후속, 머리말 로고는 RAG 잡음(실제 샘플에서 동일 로고가 머리말에 중복), 외부 경로는 재현 불가.
3. `## 2026-10-22 HWP 5.0 BinData 해석: BIN_DATA(0x12) 1-based ID → BinData/BIN%04X.<ext>, 그림 레코드(0x55) offset 71, 압축은 레코드 비트 → 헤더 비트 → zlib 실패 시 raw` — 결정·이유 §4.3·§4.4 요약 + pyhwp 교차 확인 근거 + 실제 HWP 5.0 양성 샘플 부재.

**B. `README.md`**
- "현재 지원:" 문장의 `… 셀 내 단락은 <br>).` 뒤 `이미지·각주는 진행 중.` → `이미지(본문 그림을 out/<입력 파일명>_images/img_001.png … 로 추출하고 Markdown 제자리에 상대 경로 링크. 표 셀·머리말 안 그림은 제외). 포맷은 … 각주는 진행 중.` 형태로 1문장 교체(기존 "포맷은 확장자가 아니라 …" 문장 유지).
- "설치와 실행" 코드 블록의 `uv run hwp2md input.hwp -o out/       # out/input.md 생성` 주석을 `# out/input.md (+ 이미지가 있으면 out/input_images/)` 로 교체.

**C. `tests/fixtures/README.md`** 끝에 1절: 이미지가 있는 샘플을 추가할 때 `tests/e2e/test_cli_image.py` 의 `REAL_IMAGE_EXPECTED` 에 `(링크 수, 파일 수, {파일명: sha256})` 을 적는 방법, 기대값이 없으면 변환 성공과 "Markdown 이미지 줄 수 == CLI 이미지 수"만 검사한다는 설명. 현재 `브라더 공공기관 보고서 양식.hwpx` 가 유일한 양성 샘플(머리말 그림 1개는 제외됨)이라는 메모.

## 5. 단계 (Stage)

### Stage 1 — 블록 모델·이미지 헬퍼·렌더·변환 결과
- 목적: `Image` 블록, `images.py`, `render_blocks(image_dir=)`, `convert()` 파일 쓰기와 `ConvertResult` 필드를 §4.2 대로 만들고 리더 없이 단위 테스트로 검증한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §1, §4.1, §4.2, §4.8(PNG_1X1·JPEG_STUB 상수는 테스트 안에서 직접 정의해 쓴다 — S2 전이므로 synth 에서 import 하지 않는다), §4.9-A, `src/hwp2md/blocks.py`, `render.py`, `convert.py`, `__init__.py`, `tests/unit/test_convert.py`(기존 패턴)
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/blocks.py`
  - `src/hwp2md/images.py` (신규)
  - `src/hwp2md/render.py`
  - `src/hwp2md/convert.py`
  - `src/hwp2md/__init__.py` (import 1줄 + `__all__` 1줄)
  - `tests/unit/test_images.py` (신규)
  - (6개. `__init__.py` 변경은 2줄이라 쪼개지 않는다)
- 산출물: `Image`, `image_dir_name`, `sniff_ext`, `normalize_ext`, `ImageNamer`, `_render_image`, `render_blocks(…, image_dir)`, `_write_images`, `ConvertResult` 필드 3개
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit -q` → `184 passed` 이상(171 + 13), failed 0 · `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` → 통과, mypy `17 source files`
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields`
- 실패 시: `git restore` 로 S1 파일 되돌리고 재시도(상한 §3). 기존 `test_convert.py`·`test_render_heading.py` 가 깨지면 구현 오류(테스트 수정 금지).

### Stage 2 — 합성 HWP 5.0 생성기: 이미지 항목·BinData 스토리지
- 목적: `tests/synth_hwp5.py` 가 §4.5·§4.8 대로 `SynthImage` 를 DocInfo BIN_DATA·`BinData/BIN%04X.<ext>` 스트림·gso 레코드 트리로 직렬화하고, 이미지 없는 입력에서 바이트가 변하지 않음을 증명한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 1 (`Image` 를 EXPECTED_BLOCKS 에 쓴다)
- 입력: §4.3, §4.4-A, §4.5, §4.8, §4.9-B, `tests/synth_hwp5.py`, `tests/unit/test_synth_hwp5.py`
- 쓰기 범위:
  - `tests/synth_hwp5.py`
  - `tests/unit/test_synth_hwp5.py` (케이스 추가만. 기존 23개 케이스·상수 수정 금지)
- 산출물: `SynthImage`, `collect_images`, `build_bin_data`, `build_ctrl_header_gso`, `build_shape_component_pic`, `build_picture_record`, `build_picture_control`, `build_cfb` BinData 확장, `build_docinfo(images=)`, fixture 4종·`IMAGE_FIXTURES`
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit/test_synth_hwp5.py -q` → `33 passed`(23 + 10), failed 0 · `uv run pytest tests/unit -q` failed 0 · LINT_CMD 통과(tests 포함)
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s2] tests: synthetic hwp5 images (BIN_DATA, BinData storage, gso picture records)`
- 실패 시: sha256 테스트가 깨지면 "이미지 없는 경로가 바뀐 것" — 조건 분기를 고친다. olefile 이 `BinData` 를 못 읽으면 디렉터리 엔트리 left/right/child 를 §4.5 대로 재검토. 2회 실패 → BLOCKED.

### Stage 3 — HWP 5.0 리더: BIN_DATA·BinData 스트림·gso 그림 → Image
- 목적: §4.3·§4.4 대로 DocInfo BIN_DATA 파싱, BinData 스트림 수집·압축 해제·해석(`BinDataStore`), 본문 gso 분기를 구현해 `read_blocks` 가 fixture 4종에서 `EXPECTED_BLOCKS_IMAGE*` 를 돌려준다.
- 담당: implementer(opus)
- 병렬 가능: 예 (Stage 4 와, worktree 격리) · 선행: Stage 2
- 입력: §4.3, §4.4, §4.8, §4.9-C, `src/hwp2md/hwp5/*.py`, `tests/unit/test_hwp5_docinfo.py`(기존 패턴, 수정 금지)
- 쓰기 범위:
  - `src/hwp2md/hwp5/records.py` (상수 4줄 추가만)
  - `src/hwp2md/hwp5/docinfo.py`
  - `src/hwp2md/hwp5/reader.py`
  - `src/hwp2md/hwp5/body.py`
  - `tests/unit/test_hwp5_bindata.py` (신규)
- 산출물: `BinDataEntry`, `parse_bin_data`, `DocInfo.bin_data`·`bin_data_entry`, `Hwp5Package`, `read_hwp5_package`, `BinDataStore`, `ImageResolver`, `parse_picture_bindata_id`, `_parse_gso`
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit/test_hwp5_bindata.py -q` → `17 passed`(14 케이스, parametrize 4) · `uv run pytest tests/unit -q` failed 0 · `uv run mypy src` 통과 · `uv run hwp2md tests/fixtures/form200005063113.hwp -o /tmp/h2m-s3 | sed -n 2p` → `  단락 118개 · 표 8개`
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s3] hwp5: BIN_DATA + BinData streams + gso picture -> Image block`
- 실패 시: 기존 `test_hwp5_docinfo.py`·`test_hwp5_body.py` 가 깨지면 시그니처 기본값 누락 — 기본값으로 호환 유지. 2회 실패 → BLOCKED.

### Stage 4 — 합성 HWPX 생성기: hp:pic·manifest·BinData 엔트리
- 목적: `tests/synth_hwpx.py` 가 §4.7 대로 `SynthImage` 를 `hp:pic/hc:img`·manifest item·`BinData/image{k}.{ext}` 엔트리로 직렬화하고, 이미지 없는 입력에서 바이트가 변하지 않음을 증명한다.
- 담당: implementer(opus)
- 병렬 가능: 예 (Stage 3 과, worktree 격리) · 선행: Stage 2
- 입력: §4.6-A(상수), §4.7, §4.8, §4.9-D, `tests/synth_hwpx.py`, `tests/unit/test_synth_hwpx.py`
- 쓰기 범위:
  - `tests/synth_hwpx.py`
  - `tests/unit/test_synth_hwpx.py` (케이스 추가만. 기존 16개 불변)
- 산출물: `pic_xml`, `pic_paragraph_xml`, `cell_xml(images=)`, `table_xml(images=)`, `section_xml(images=)`, `manifest_items`, `hwpx_entries` 확장
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit/test_synth_hwpx.py -q` → `24 passed`(16 + 8), failed 0 · LINT_CMD 통과
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s4] tests: synthetic hwpx images (hp:pic/hc:img, manifest items, BinData entries)`
- 실패 시: sha256·`test_header_default_bytes_unchanged`·엔트리 순서 테스트가 깨지면 이미지 없는 경로 분기 수정. 2회 실패 → BLOCKED.

### Stage 5 — HWPX 리더: manifest·BinData 엔트리·hp:pic → Image + 교차 포맷 검증
- 목적: §4.6 대로 `hwpx/bindata.py`·`reader.py`·`body.py` 를 구현해 `read_blocks` 가 fixture 4종에서 `EXPECTED_BLOCKS_IMAGE*` 를 돌려주고, 두 포맷 `convert()` 결과(Markdown·카운트·파일 바이트)가 동일함을 `test_cross_format.py` 로 증명한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 3, Stage 4 (둘 다 병합된 뒤)
- 입력: §4.2, §4.6, §4.8, §4.9-E·F, §4.10 HWPX 표, `src/hwp2md/hwpx/*.py`, `tests/unit/test_hwpx_reader.py`·`test_hwpx_body.py`(기존 패턴, 수정 금지)
- 쓰기 범위:
  - `src/hwp2md/hwpx/bindata.py` (신규)
  - `src/hwp2md/hwpx/reader.py`
  - `src/hwp2md/hwpx/body.py`
  - `tests/unit/test_hwpx_bindata.py` (신규)
  - `tests/unit/test_cross_format.py` (케이스 추가만. 기존 5개 불변)
- 산출물: `parse_manifest`, `BinItemStore`, `HwpxPackage`, `read_hwpx_package`, `HP_PIC`·`HP_CONTAINER`·`HC_IMG`, `parse_paragraph(…, bin_items)`, cross-format 테스트 2개
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run pytest tests/unit/test_hwpx_bindata.py tests/unit/test_cross_format.py -q` → `16 + 10 = 26 passed`(13 케이스 parametrize 4 → 16; 기존 5 + 신규 4 + 1 = 10) · `uv run pytest tests/unit -q` → `216 passed` 이상, failed 0 · `uv run mypy src` → `18 source files` · `uv run hwp2md "tests/fixtures/hwpx/브라더 공공기관 보고서 양식.hwpx" -o /tmp/h2m-s5 | sed -n 2p` → `  단락 32개 · 표 8개`(CLI 는 S7 전이므로 `이미지` 표기 없음) 그리고 `shasum -a 256 "/tmp/h2m-s5/브라더 공공기관 보고서 양식_images/img_001.png"` → `f9be5b73…`
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s5] hwpx: content.hpf manifest + BinData entries + hp:pic -> Image, cross-format parity`
- 실패 시: 두 포맷 결과가 다르면 §4.8 fixture 의 기대 블록을 기준으로 리더 쪽을 고친다(fixture·기대값 수정 금지). 2회 실패 → BLOCKED.

### Stage 6 — 문서·결정 기록
- 목적: §4.13 대로 `docs/decisions.md` 3건, `README.md` 2곳, `tests/fixtures/README.md` 1절을 쓴다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 5
- 입력: §4.13, §4.10, `docs/decisions.md`, `README.md`, `tests/fixtures/README.md`
- 쓰기 범위:
  - `docs/decisions.md`
  - `README.md`
  - `tests/fixtures/README.md`
- 산출물: 결정 3건, README 2줄, fixtures README 1절
- 검증: `cd /Users/illi/illy-projects/hwp2md && grep -c "^## 2026-10-22" docs/decisions.md` → `14`(기존 11 + 3) · `grep -c "_images" README.md` → `2` 이상 · `grep -c "REAL_IMAGE_EXPECTED" tests/fixtures/README.md` → `1` · `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → `sanitize-check: OK`
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s6] docs: image extraction decisions, README, fixtures guide`
- 실패 시: sanitize 실패 시 해당 단어 제거 후 재실행.

### Stage 7 — CLI 2행·3행 (orchestrator 전용 파일, 단독 단계)
- 목적: §4.11 대로 `cli.py` 의 요약 출력에 ` · 이미지 K개` 와 3행 `  이미지: <dir>/ (n files)` 를 추가한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 (다른 어떤 단계와도 동시에 두지 않는다) · 선행: Stage 6
- 입력: §4.11, `src/hwp2md/cli.py`
- 쓰기 범위:
  - `src/hwp2md/cli.py`
- 산출물: 49~52행 교체(§4.11 블록)
- 검증: `cd /Users/illi/illy-projects/hwp2md && uv run python -c "import sys; sys.path.insert(0,'tests'); from synth_hwp5 import write_hwp5, FIXTURE_ITEMS_IMAGES, FIXTURE_ITEMS_HEADINGS; from pathlib import Path; write_hwp5(Path('/tmp/h2m-s7/doc.hwp'), FIXTURE_ITEMS_IMAGES); write_hwp5(Path('/tmp/h2m-s7/plain.hwp'), FIXTURE_ITEMS_HEADINGS)" && uv run hwp2md /tmp/h2m-s7/doc.hwp -o /tmp/h2m-s7/out && uv run hwp2md /tmp/h2m-s7/plain.hwp -o /tmp/h2m-s7/out | wc -l` → doc: 2행 `  단락 2개 · 표 0개 · 제목 1개 · 이미지 2개`, 3행 `  이미지: /tmp/h2m-s7/out/doc_images/ (2 files)`; plain: `wc -l` → `2` · `uv run pytest tests/e2e -q` → 기존 33 중 실패는 **정확히 2개**(`test_cli_heading.py::test_real_fixture_headings[브라더…]`, `test_cli_hwpx.py::test_real_hwpx_fixture_converts[브라더…]` — 정규식 `$` 앵커, S8 에서 고친다), 그 외 통과 · `uv run mypy src` 통과
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s7] cli: image count and image dir lines`
- 실패 시: 예상 외 E2E 실패가 더 있으면 S7 변경을 되돌리고 원인을 S5 구현 오류로 분류해 implementer 재호출.

### Stage 8 — E2E 테스트 작성·실행 (필수, 생략 불가)
- 목적: §4.12 대로 `tests/e2e/test_cli_image.py` 를 작성하고 기존 정규식 3줄을 고친 뒤 E2E 전체를 실행해 증거를 남긴다.
- 담당: test-writer(sonnet) → runner(haiku)
- 병렬 가능: 아니오 · 선행: Stage 7
- 입력: §4.8, §4.10, §4.11, §4.12, `tests/e2e/conftest.py`, `tests/e2e/test_cli_heading.py`(패턴)
- 쓰기 범위 (test-writer):
  - `tests/e2e/test_cli_image.py` (신규)
  - `tests/e2e/test_cli_convert.py` (79행 1곳)
  - `tests/e2e/test_cli_heading.py` (45행 1곳)
  - `tests/e2e/test_cli_hwpx.py` (32행 1곳)
- 산출물: E2E 13 케이스(합성 8 + 실제 5), 정규식 3줄
- 검증 (runner, 한 번의 Bash):
  ```bash
  cd /Users/illi/illy-projects/hwp2md && T=.ai/tasks/T-20261022-image-extract; mkdir -p $T/logs $T/screenshots
  [ -f $T/logs/e2e.log ] && mv $T/logs/e2e.log $T/logs/e2e.prev.log
  ILLY_SHOT_DIR=$T/screenshots uv run pytest tests/e2e -q > $T/logs/e2e.log 2>&1; echo "exit=$?" >> $T/logs/e2e.log
  tail -3 $T/logs/e2e.log; grep -E "failed|FAILED|Error" $T/logs/e2e.log | head -10; ls $T/screenshots
  ```
  → `46 passed`, `exit=0`, screenshots 에 §2-S10 목록 · `uv run ruff check src tests && uv run ruff format --check src tests` 통과 · `git diff 3e8248d --stat -- tests/e2e/test_cli_convert.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py` → 각 `1 +, 1 -`
- 완료 조건: 검증 통과 + PROGRESS + 커밋 `[T-20261022-image-extract][s8] e2e: image extraction both formats, reuse/cell/missing, real samples`
- 실패 시: 실패 분류(e2e-standard 표) — 테스트 파일 안 오류 → test-writer 재호출(2회 실패 → opus), 구현 단언 실패 → implementer(해당 단계 파일만). 테스트 약화·skip 금지.

### Stage 9 — 리뷰·결과 기록
- 목적: reviewer 가 `git diff 3e8248d` 와 증거 파일을 §2 표와 대조하고, scribe 가 RESULT.md·STATE.md 를 쓴다.
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: Stage 8
- 입력: §2, §4.10, `.ai/tasks/T-20261022-image-extract/screenshots/*`, `logs/e2e.log`, PROGRESS.md
- 쓰기 범위 (scribe): `.ai/tasks/T-20261022-image-extract/RESULT.md`, `.ai/STATE.md`
- 산출물: RESULT.md(성공 기준 S1~S10 표에 실제 값, 증거 경로, 미해결 리스크), STATE.md(IDLE, 다음 행동 = main 병합 명령)
- 검증: reviewer 보고 `STATUS: DONE` + S10 의 "눈으로 확인" 2건(`image_hwp5.md` 3줄, `real_hwpx_img_001.png` 그림) 명시 · `ls .ai/tasks/T-20261022-image-extract/RESULT.md` 존재 · `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → OK
- 완료 조건: 커밋 `[T-20261022-image-extract][done] image extraction (HWP 5.0 BinData + HWPX hp:pic -> out/<stem>_images)`
- 실패 시: reviewer 가 §2 미달을 찾으면 해당 단계 implementer 재호출(상한 §3).

## 6. 병렬 실행 맵
```
S1 ──> S2 ──┬──> S3 (hwp5 리더) ──┐
            └──> S4 (hwpx 생성기) ─┴──> S5 ──> S6 ──> S7(cli, 단독) ──> S8(E2E) ──> S9(리뷰·기록)
```
- S3 ∥ S4: 쓰기 범위 대조 — S3 = `src/hwp2md/hwp5/{records,docinfo,reader,body}.py`, `tests/unit/test_hwp5_bindata.py` / S4 = `tests/synth_hwpx.py`, `tests/unit/test_synth_hwpx.py`. 교집합 없음. 둘 다 쓰는 단계이므로 **worktree 격리**(`isolation: "worktree"`)로 띄우고 orchestrator 가 S3 → S4 순으로 diff 를 적용·검증한다. 공유 계약은 §4.5 의 `SynthImage`·`collect_images`·fixture(S2 에서 이미 확정)와 §4.2 `Image`(S1). 10분 안쪽이면 순차(S3 → S4)로 해도 된다.
- 나머지는 전부 순차. S7 은 orchestrator 전용 파일이라 어떤 단계와도 병렬로 두지 않는다.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [x] 1. 이미지 파일명 규칙 — 기본값: `img_001.png`(고유 원본의 첫 등장 순 3자리, 원본 확장자 소문자). 대안: HWPX 원본 이름(`image1.png`) 유지 / HWP 5.0 스토리지 이름(`BIN0001.png`) 유지.
- [x] 2. 출력 폴더 — 기본값: `<out>/<입력 파일 stem>_images/`(vision 시나리오 1). 대안: `<out>/images/` 공용 폴더.
- [x] 3. alt 텍스트 — 기본값: `그림 N`(문서 안 링크 등장 순). 대안: 파일명 / `hp:shapeComment` 텍스트(HWPX 만 가능, OUT).
- [x] 4. 표 셀 안 이미지 — 기본값: 추출하지 않고 링크도 넣지 않는다(셀 텍스트만). 대안: 셀 안에 `![그림 N](…)` 인라인(GFM 지원, 두 포맷 번호 매김 설계 변경 필요 → 후속 태스크).
- [x] 5. 머리말·꼬리말·글상자 안 이미지 — 기본값: 제외(HWPX `hp:ctrl` 무시 정책 유지. HWP 5.0 은 기존 흘려보냄 정책 유지, 실제 샘플 영향 없음). 대안: 머리말 그림도 추출.
- [x] 6. 외부 링크(LINK) 그림·본체 없는 참조 — 기본값: 조용히 건너뜀(경고 없음, 번호 매김에서 제외). 대안: stderr 에 `hwp2md: warning: …` 1줄.
- [x] 7. 지원 포맷 — 기본값: BinData 바이트를 그대로 저장(png/jpg/gif/bmp/wmf/emf/… 변환 없음, 확장자 모르면 시그니처 → `bin`). 대안: Pillow 로 PNG 변환(의존성 추가 → 이번 태스크 거절, 후속).
- [x] 8. 같은 원본 재참조 — 기본값: 파일 1개, 링크는 참조 수만큼(`그림 1`, `그림 2` 가 같은 파일을 가리킴). 대안: 참조마다 파일 복제.
- [x] 9. 이미지가 있는 실제 HWP 5.0 샘플 — 기본값: 없음, 합성 fixture 로 검증(그림 레코드 offset 은 pyhwp 교차 확인). 사용자가 `tests/fixtures/*.hwp` 에 넣으면 E2E 가 자동 포함하고 `REAL_IMAGE_EXPECTED` 에 기대값을 추가한다.
- [x] 10. CLI 3행 표기 — 기본값: vision 그대로 `  이미지: <out>/<stem>_images/ (n files)`(이미지 ≥1 일 때만). 대안: 3행 없이 2행만.
- 기본값: 답이 없으면 위 10개 전부 기본값으로 진행한다.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| HWP 5.0 그림 레코드 offset 71·BIN_DATA 레이아웃을 실제 바이트로 검증하지 못함(실제 샘플 이미지 0) | 중 | 스펙 + pyhwp(독립 구현) 소스 교차 확인(§4.3·§4.4 근거). 파서는 길이 73 미만이면 오류, ID 범위 밖이면 건너뜀 → 조용한 오염 대신 드러난다. 사용자 샘플 추가 시 E2E 자동 검증(§7-9) |
| CFB 디렉터리 트리 확장 실수(olefile 이 `BinData` 를 못 찾음 / 기존 바이트 변동) | 중 | §4.5 엔트리 번호·left/right/child 고정, `olefile.listdir()` 단위 테스트, sha256 9개 회귀 테스트 |
| HWPX `hp:container` 그룹 안 그림을 실제 샘플로 확인하지 못함 | 중 | `iter(HP_PIC)` 로 깊이 무관 탐색, 수작업 XML 단위 테스트(§4.9-E-11). 틀려도 그림 누락만 발생(출력 깨짐 없음) |
| 두 포맷 번호 매김 불일치(셀·누락·재사용) | 중 | 셀은 해석 금지, 누락은 namer 호출 전 None, 재사용은 캐시 — fixture 4종 cross-format 바이트 비교(§4.9-F) |
| `%20` 치환이 다른 특수문자(`(`, `)`, `#`)를 다루지 않음 | 하 | 실제 샘플 stem 의 괄호는 균형 → CommonMark 유효. 문제가 되면 후속에서 `<…>` 감싸기 |
| 대용량 이미지 다수 문서의 메모리(HWPX 바이너리 전부 선읽기) | 하 | 엔트리당 50MB 상한(`Hwp2mdError`). MVP 규모(20개 샘플)에서 수용 |
| `.jpg` 스텁 등 증거 파일이 커밋에 섞임 | 하 | 증거는 `.md` 와 `.png` 만 복사(`.png` 는 gitignore) |
| 기존 E2E 정규식 `$` 앵커가 S7 직후 2개 깨짐 | 확정 | S7 검증에 "정확히 2개 실패"를 명시하고 S8 에서 3줄 수정 |

## 9. 예상 비용
- 예상 단계 수: 9 · 서브에이전트 호출: 11회(implementer 7, test-writer 1, runner 1, reviewer 1, scribe 1) · 주 모델: opus 7 / sonnet 2 / haiku 2
- 가장 큰 단계: S3(hwp5 리더 5파일)·S2(CFB 확장). 각 도구 호출 40회 이내 목표.

## 변경 이력
- 0 (planner, 작성 시): §4.12-B 에 잘린 그림 레코드 E2E(케이스 8)를 추가하면서 합성 케이스가 7 → 8 이 되었다. §2 표의 S1 `12 passed` → **13 passed**, S2 `45 passed` → **46 passed** 로 읽는다. 단위 테스트 기대치 `216 이상` 은 그대로.
