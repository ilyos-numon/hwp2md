# Proposal

## Why

README MVP 4종(본문·제목·표·이미지) 중 이미지만 남았다. 현재 리더는 HWP 5.0의 `gso` 그림 개체와 HWPX의 `hp:pic`를 버리므로, 공고문·보고서의 추진 체계도·도표 그림이 Markdown에서 사라지고 그 자리도 남지 않는다. vision 시나리오 1(`out/<문서>_images/img_001.png` + `![그림 1](...)`)을 실제로 동작하게 만든다.

## What Changes

- 블록 모델에 `Image` 블록을 추가하고, 두 리더(HWP 5.0·HWPX)가 본문 흐름의 제자리에 `Image` 블록을 넣는다.
- 변환(`convert`)이 이미지 바이트를 `<out>/<stem>_images/img_NNN.<ext>` 파일로 저장하고, Markdown에는 `.md` 기준 상대 경로 `![그림 N](<stem>_images/img_NNN.<ext>)`를 쓴다. 같은 원본을 여러 번 참조하면 파일은 1개, 링크는 참조 수만큼이다.
- HWP 5.0: `DocInfo`의 `BIN_DATA` 레코드와 `BinData/BIN%04X.<ext>` 스트림, 본문의 `gso` 컨트롤 → `SHAPE_COMPONENT_PICTURE` 레코드(BinData ID)를 해석한다. 압축 문서는 스트림을 raw deflate로 해제한다.
- HWPX: `Contents/content.hpf` manifest(`opf:item id→href`)와 `BinData/*` 엔트리, 본문의 `hp:pic/hc:img@binaryItemIDRef`(그룹 `hp:container` 안 포함)를 해석한다.
- 제외(이번 범위에서 블록을 만들지 않음): 표 셀 안 이미지, 머리말·꼬리말·글상자 안 이미지, 외부 링크(LINK) 이미지, 바이너리가 없는 참조. 전부 조용히 건너뛴다.
- CLI 2행에 이미지가 1개 이상일 때만 ` · 이미지 K개`를 덧붙이고, 3행 `  이미지: <out>/<stem>_images/ (n files)`를 출력한다. 이미지가 없는 문서의 출력은 바이트 단위로 바뀌지 않는다.
- 합성 fixture 생성기(`tests/synth_hwp5.py`, `tests/synth_hwpx.py`)에 이미지 항목을 추가한다. 이미지가 없는 기존 fixture는 바이트 불변.

## Capabilities

### New Capabilities
- `image-extraction`: 문서 안의 임베디드 이미지를 파일로 추출하고 Markdown 본문의 제자리에 상대 경로 이미지 링크로 보존하는 동작(파일명·폴더 규칙, 재사용·누락·제외 규칙, CLI 요약 표기).

### Modified Capabilities
(없음 — `openspec/specs/`에 기존 capability가 없다)

## Impact

- 코드: `src/hwp2md/blocks.py`, `render.py`, `convert.py`, 신규 `images.py`; `hwp5/records.py`, `hwp5/docinfo.py`, `hwp5/body.py`, `hwp5/reader.py`; `hwpx/body.py`, `hwpx/reader.py`, 신규 `hwpx/bindata.py`; `cli.py`(2·3행).
- 공개 API: `Block = Paragraph | Table | Image`; `ConvertResult`에 `image_count`, `image_dir`, `image_files` 필드 추가(기본값 있음, 기존 필드 불변); `render_blocks(blocks, *, image_dir="")` 키워드 인자 추가. 기존 호출은 전부 호환.
- 테스트: 단위 신규 3파일 + 기존 3파일 추가, E2E 신규 `tests/e2e/test_cli_image.py` + 기존 E2E 정규식 3줄.
- 의존성 추가 없음(이미지 포맷 변환 없음, 바이트 그대로 저장).
- 실제 샘플: HWPX 샘플 1개(`브라더 공공기관 보고서 양식.hwpx`)에 본문 이미지 1개가 있어 실제 검증이 가능하다. HWP 5.0 실제 샘플 2개에는 이미지가 없어 합성 fixture로 검증한다.
