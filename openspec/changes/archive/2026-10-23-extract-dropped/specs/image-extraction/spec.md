## REMOVED Requirements

### Requirement: 표 셀·머리말·꼬리말·글상자 안 이미지와 해석 불가 참조는 건너뛴다
**Reason**: 표 칸·글상자 안 그림을 이제 추출한다(`element-extraction`). 건너뛰는 범위가 머리말·꼬리말과 해석 불가 참조로 줄고, 건너뛴 것을 보고하게 되어 요구를 새로 쓴다.
**Migration**: 아래 ADDED 요구 "머리말·꼬리말 안 이미지와 해석 불가 참조는 건너뛰고 보고한다" 와 `element-extraction` 의 "표 칸 안 그림은 칸 안 이미지 링크로 출력된다", "글상자·도형·묶음 개체 안 글과 그림이 출력된다" 로 대체한다. 셀 안 그림이 번호를 소비하므로 셀 그림이 있는 문서는 `img_NNN`·`그림 N` 번호가 바뀐다.

## ADDED Requirements

### Requirement: 머리말·꼬리말 안 이미지와 해석 불가 참조는 건너뛰고 보고한다
변환기는 세 포맷 모두 머리말·꼬리말 안의 그림 개체에 대해 파일을 만들지 않고 링크도 출력하지 않아야 한다(SHALL). 외부 파일 링크(LINK) 그림과 바이너리 본체가 없는 참조도 파일·링크를 만들지 않고 각각 건너뜀 종류 `image_link`, `image_missing` 으로 센다(머리말·꼬리말 안 그림은 그 컨트롤의 `header_footer` 1개로만 센다). 건너뛴 참조는 이미지 수에 세지 않고 번호(`img_NNN`, `그림 N`)를 소비하지 않는다. 표준 오류에 경고를 쓰지 않는다.

#### Scenario: HWP 5.0 머리말 안 그림
- **WHEN** 머리말 컨트롤 안 단락에 PNG 그림 1개, 본문에 같은 바이너리를 참조하는 그림 1개가 있는 HWP 5.0 문서 `doc` 를 변환한다
- **THEN** Markdown 에 `![그림 1](doc_images/img_001.png)` 한 줄만 있고 이미지 수 1, 파일 1개, 머리말 단락 글자는 출력에 없다

#### Scenario: HWPX 머리말 안 그림
- **WHEN** 머리말(`hp:ctrl/hp:header`) 안 `hp:pic` 1개와 본문 최상위 `hp:pic` 1개가 같은 바이너리를 참조하는 HWPX 문서 `doc` 를 변환한다
- **THEN** 결과가 앞 시나리오의 HWP 5.0 결과와 같다

#### Scenario: 바이너리가 없는 참조
- **WHEN** 단락, 본체가 없는 PNG 참조, 실제 PNG 그림, 단락 순서인 문서 `doc` 를 변환한다
- **THEN** Markdown 은 `앞\n\n![그림 1](doc_images/img_001.png)\n\n뒤\n` 이고 파일은 `img_001.png` 1개, `skipped` 는 `image_missing` 1, 종료 코드 0, 표준 오류는 비어 있다

## MODIFIED Requirements

### Requirement: 이미지가 없는 문서의 출력은 바뀌지 않는다
이미지가 없는 문서에서 변환기는 `_images` 폴더를 만들지 않아야 하고(SHALL), CLI 표준 출력 2행 형식 `  단락 N개 · 표 M개[ · 제목 K개]` 를 유지해야 한다. 건너뛴 요소가 있을 때만 그 뒤에 `  건너뜀: …` 한 줄이 붙는다. 이 변경에서 새로 추출하는 요소(링크·각주·수식·목록·캡션·글상자·차트)가 없는 문서의 Markdown 바이트는 이전과 같다.

#### Scenario: 기존 합성 fixture와 실제 샘플 4개
- **WHEN** 이미지·새 요소가 없는 합성 fixture(단락·표·제목)와 `tests/samples.py` 의 기존 실제 샘플 목록 중 이미지가 없는 4개를 변환한다
- **THEN** 합성 fixture 의 표준 출력은 정확히 2행이고 `이미지`·`건너뜀` 글자가 없으며 Markdown 이 이 변경 이전 기대값(`tests/synth_hwp5.py` 의 `EXPECTED_MARKDOWN_HEADINGS` 등)과 같고, 실제 샘플 4개는 `<stem>_images` 폴더가 생기지 않으며 단락·표·제목 수가 기준선(S1 기록)과 같거나, 다르면 그 차이가 구조 탐색으로 센 캡션·글상자·차트 개수와 같다
