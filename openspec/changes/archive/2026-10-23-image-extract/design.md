# Design

## Context

- 리더는 `list[Block]`(`Paragraph | Table`)을 돌려주고 `render_blocks`가 Markdown을 만든다(decisions 2026-10-22 블록 모델). 이미지는 같은 리스트에 얹는 세 번째 블록이다.
- HWP 5.0 리더(`hwp5/body.py`)는 `CTRL_HEADER` ctrl_id가 `tbl `이면 표를 조립하고, 그 외 컨트롤은 안쪽 `PARA_HEADER`(ctrl_level+1)만 흘려보낸다. 그림 개체는 ctrl_id `gso ` 아래 `SHAPE_COMPONENT`(0x4C) → `SHAPE_COMPONENT_PICTURE`(0x55) 레코드로 들어 있고, 바이너리는 `DocInfo`의 `BIN_DATA`(0x12) 레코드(1-based 등장 순서 = BinData ID)가 가리키는 `BinData/BIN%04X.<ext>` 스트림이다. 레이아웃은 pyhwp(독립 구현) 소스와 교차 확인했다: `SHAPE_COMPONENT_PICTURE` = BorderLine 12B + ImageRect 32B + ImageClip 16B + Margin 8B + PictureInfo(INT8, INT8, BYTE, **UINT16 bindata_id**) → bindata_id는 offset 71. `BIN_DATA` = UINT16 속성(비트 0~3 종류 0 LINK/1 EMBEDDING/2 STORAGE, 비트 4~5 압축 0 기본/1 압축/2 비압축) + EMBEDDING이면 UINT16 storage_id + BSTR ext.
- HWPX 리더(`hwpx/body.py`)는 `hp:run` 자식 중 `hp:t`·`hp:tbl`만 보고 나머지(`hp:ctrl`, `hp:pic`, …)는 무시한다. 실제 샘플(`브라더 공공기관 보고서 양식.hwpx`)에서 그림은 `hp:run/hp:pic/hc:img@binaryItemIDRef="image1"`, 바이너리는 zip 엔트리 `BinData/image1.png`, 매핑은 `Contents/content.hpf`의 `opf:item id="image1" href="BinData/image1.png"`다. `header.xml`에는 binData 목록이 없다. 같은 샘플의 다른 `hp:pic` 하나는 머리말(`hp:ctrl/hp:header/hp:subList`) 안에 있다.
- 실제 HWP 5.0 샘플 2개에는 `BinData` 스토리지·`BIN_DATA` 레코드·`gso` 컨트롤이 전부 0개다. HWP 5.0 양성 검증은 합성 fixture가 담당한다.
- 제약: 의존성 추가 없음(이미지 변환 안 함), 익명화 규칙, `cli.py`는 orchestrator 전용 파일(별도 단계), 기존 fixture 바이트 불변(sha256 테스트 9개).

## Goals / Non-Goals

**Goals:**
- `Image` 블록 하나로 두 포맷을 통일하고, 같은 입력 내용에서 Markdown·이미지 파일 바이트가 동일하게 나온다.
- 이미지가 없는 문서는 코드 경로·출력이 바이트 단위로 변하지 않는다.
- 리더는 파일명을 정하고(`img_NNN.<ext>`, 원본별 1개), 렌더러는 상대 경로를, `convert`는 파일 쓰기를 맡는다.

**Non-Goals:**
- 이미지 포맷 변환(WMF/EMF → PNG 등), 크기 조정, alt 텍스트 추출(`hp:shapeComment`).
- 표 셀·머리말·꼬리말·글상자 안 이미지, OLE 개체, 외부 링크 이미지.
- `--images` 같은 CLI 옵션(폴더 이름·끄기). 메타데이터(JSON) 출력.

## Decisions

1. **`Image(file_name, data)` 블록, 파일명은 리더가 부여** — 대안: 리더가 원본 키만 넣고 `convert`가 이름을 매긴다. 렌더러와 `convert`가 같은 매핑을 두 번 계산해야 하고 테스트에서 블록 동등 비교가 어려워진다. 리더 안의 `ImageNamer`(원본 키 → `img_NNN.<ext>`, 첫 등장 순)가 단순하다. 두 포맷의 "원본 키"는 각각 BinData ID 문자열, `binaryItemIDRef`다.
2. **렌더러는 `image_dir` 키워드 인자로 상대 폴더명을 받는다** (`render_blocks(blocks, *, image_dir="")`) — 리더는 출력 stem을 모르므로 폴더명은 `convert`가 `f"{stem}_images"`로 정해 넘긴다. alt는 렌더러가 `Image` 블록 등장 순으로 `그림 N`을 매긴다. 링크의 공백은 `%20`(CommonMark 링크 목적지는 공백을 허용하지 않고, 전체 percent-encoding은 한글 경로를 읽을 수 없게 한다).
3. **셀 안 이미지는 해석 자체를 하지 않는다** — HWP 5.0 `_parse_table`은 셀 단락을 `bin_data=None`으로 파싱하고, HWPX `_cell_text`는 `bin_items` 없이 `parse_paragraph`를 호출한다. 그래야 두 포맷에서 번호 매김이 같다(셀 이미지가 `img_001`을 선점하지 않는다). GFM 셀 안 이미지 인라인은 후속 과제.
4. **HWPX `hp:ctrl`은 계속 무시** — 머리말·꼬리말 안 그림은 본문 흐름이 아니고(decisions 2026-10-22 HWPX 본문 범위), 실제 샘플에서 같은 로고가 머리말에 중복 삽입돼 있어 RAG 잡음이 된다. HWP 5.0 쪽은 기존 "표 아닌 컨트롤 안 단락 흘려보냄" 정책과 함께 유지하고 통일은 각주 태스크에서 한다(실제 HWP 5.0 샘플에 영향 없음).
5. **HWP 5.0 BinData 스트림 압축 해제 규칙** — `BIN_DATA` 압축 비트 2 → raw, 1 → raw deflate 해제, 0 → FileHeader 압축 비트를 따른다. 해제 중 `zlib.error`면 raw 바이트를 쓴다(pyhwp는 헤더 비트만 보지만, 비트 2가 명시된 문서에서 깨지지 않게 한다). 스트림 이름은 `BIN{storage_id:04X}.{ext}`를 대문자 비교로 찾고, 없으면 `BIN{storage_id:04X}.`로 시작하는 첫 스트림을 쓴다(확장자 대소문자 불일치 대비).
6. **HWPX 바이너리는 패키지 읽기 시점에 전부 메모리에 올린다** — `read_hwpx_package`가 `BinData/*` 엔트리를 50MB 상한으로 읽어 dict로 들고 `BinItemStore`가 참조를 해석한다. 지연 읽기는 zip 핸들을 파싱 동안 열어 둬야 해서 현재 구조(바이트 반환 → 파싱)를 깨뜨린다. 상한은 섹션 XML과 같은 50MB.
7. **manifest가 없거나 id가 없을 때의 fallback** — `BinData/<id>.*` 엔트리를 정렬해 첫 것을 쓴다. 실제 샘플은 manifest가 있지만 다른 생성기(비한컴)가 생략할 수 있다.
8. **합성 fixture 생성기 확장은 조건부** — `build_cfb`는 `BinData/<NAME>` 키가 있을 때만 `BinData` 스토리지 디렉터리 엔트리(DocInfo의 left 자식, 이름 정렬 규칙상 `BinData` < `DocInfo`)와 스트림 엔트리를 추가한다. 키가 없으면 현재와 바이트 동일. 1×1 PNG는 zlib 버전에 따라 바뀌지 않게 hex 상수로 고정한다.

## Risks / Trade-offs

- [HWP 5.0 그림 레코드 offset 71을 실제 바이트로 검증하지 못했다(실제 샘플에 이미지 없음)] → pyhwp 소스와 스펙 표(BorderLine/ImageRect/ImageClip/Margin/PictureInfo)로 교차 확인했고, 파서는 길이 73 미만이면 오류를 내므로 틀리면 조용히 잘못된 ID를 쓰는 대신 ID가 BinData 범위 밖(→ 건너뜀) 또는 오류로 드러난다. 사용자가 이미지 있는 HWP 5.0 샘플을 `tests/fixtures/`에 넣으면 E2E가 자동 포함한다.
- [CFB 디렉터리 트리 확장 실수로 olefile이 BinData 스토리지를 못 읽음] → 단위 테스트가 `olefile.listdir()`로 스트림 존재와 바이트를 직접 확인한다. BST 순서는 (이름 길이, 대문자 이름) 비교 규칙을 따른다.
- [HWPX `hp:container` 그룹 안 그림을 실제 샘플로 확인하지 못함] → OWPML 요소명대로 구현하고 합성 테스트 없이 두되, `iter()`로 깊이 무관하게 찾으므로 구조 차이에 둔감하다.
- [대용량 이미지 다수 문서의 메모리] → 50MB/엔트리 상한. 20개 샘플 규모의 MVP에서는 수용.
- [`%20` 치환이 다른 특수문자(`(`, `)`, `#`)는 다루지 않음] → 실제 샘플 stem의 괄호는 균형이 맞아 CommonMark에서 유효. 후속에서 필요하면 `<...>` 감싸기로 전환.

## Migration Plan

- 호환 유지: `read_streams`·`read_package`는 래퍼로 남긴다. `ConvertResult` 새 필드는 기본값이 있고 끝에 추가한다. `Paragraph`·`Table` 불변. 롤백은 브랜치 폐기.

## Open Questions

- 없음. 사용자 확인 사항은 PLAN §7에 기본값과 함께 모았고, 기본값으로 진행해도 스펙·접근·작업 분해가 바뀌지 않는다.
