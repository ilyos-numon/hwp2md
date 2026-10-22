# image-extraction Specification

## Purpose
HWP 5.0·HWPX 문서에 임베디드된 이미지를 출력 폴더에 파일로 추출하고, Markdown 본문의 제자리에 `.md` 기준 상대 경로 이미지 링크로 보존한다. 사용자는 한컴 없이 그림이 살아 있는 Markdown을 얻는다.

## Requirements

### Requirement: 본문 이미지는 파일로 추출되고 Markdown 제자리에 링크된다
변환기는 본문 흐름(최상위 단락과 그 안의 그림 개체)에 있는 임베디드 이미지를 `<출력 폴더>/<입력 파일 stem>_images/img_NNN.<ext>`에 원본 바이트 그대로 저장하고, Markdown의 그 위치에 `![그림 N](<stem>_images/img_NNN.<ext>)` 한 줄을 출력해야 한다(SHALL). `NNN`은 고유 원본의 첫 등장 순서(1부터, 3자리 0 채움), `N`은 문서 안 이미지 링크의 등장 순서(1부터)다. `<ext>`는 원본 확장자를 소문자로 쓰고, 확장자 정보가 없으면 바이트 시그니처(PNG·JPEG·GIF·BMP)로 정하고, 그래도 모르면 `bin`이다. 링크 경로의 공백은 `%20`으로 쓴다.

#### Scenario: HWP 5.0 문서의 그림 두 장
- **WHEN** 단락, PNG 그림, 2수준 제목, JPG 그림, 단락 순서인 HWP 5.0 문서 `doc.hwp`를 `out/`으로 변환한다
- **THEN** `out/doc_images/img_001.png`와 `out/doc_images/img_002.jpg`가 원본 바이트와 동일하게 생성되고, `out/doc.md`는 `단락\n\n![그림 1](doc_images/img_001.png)\n\n## 제목\n\n![그림 2](doc_images/img_002.jpg)\n\n단락\n` 구조다

#### Scenario: HWPX 문서는 같은 결과를 낸다
- **WHEN** 같은 내용의 HWPX 문서 `doc.hwpx`를 변환한다
- **THEN** Markdown 바이트와 이미지 파일 바이트가 HWP 5.0 변환 결과와 동일하다

#### Scenario: 압축되지 않은 HWP 5.0 문서
- **WHEN** FileHeader 압축 비트가 꺼진 HWP 5.0 문서를 변환한다
- **THEN** 압축 문서와 동일한 Markdown·이미지 파일을 낸다

### Requirement: 같은 원본을 여러 번 참조하면 파일은 하나다
한 문서에서 같은 바이너리 항목(HWP 5.0 BinData ID, HWPX binaryItemIDRef)을 여러 그림 개체가 참조하면 변환기는 파일을 한 번만 저장하고(SHALL), 각 참조 위치에는 같은 파일을 가리키는 링크를 등장 순서의 `그림 N` 번호로 출력해야 한다.

#### Scenario: 한 이미지를 두 번 삽입
- **WHEN** PNG 그림, 단락, 같은 PNG 그림 순서인 문서 `doc`를 변환한다
- **THEN** 이미지 파일은 `img_001.png` 1개이고, Markdown은 `![그림 1](doc_images/img_001.png)\n\n단락\n\n![그림 2](doc_images/img_001.png)\n`이며 이미지 수는 2, 파일 수는 1로 보고된다

### Requirement: 표 셀·머리말·꼬리말·글상자 안 이미지와 해석 불가 참조는 건너뛴다
변환기는 표 셀 안, 머리말·꼬리말·글상자(도형 텍스트) 안의 그림 개체, 외부 파일 링크(LINK) 그림, 바이너리 본체가 없는 참조에 대해 파일을 만들지 않고 링크도 출력하지 않아야 한다(SHALL). 건너뛴 참조는 이미지 수에 세지 않고, 경고도 출력하지 않는다. 이미지 번호(`img_NNN`, `그림 N`)는 실제로 출력된 이미지만으로 매긴다.

#### Scenario: 표 셀 안 그림
- **WHEN** 첫 셀에 JPG 그림과 "값" 단락, 둘째 셀에 "나"가 있는 1×2 표 다음에 PNG 그림이 오는 문서 `doc`를 변환한다
- **THEN** 표는 `| 값 | 나 |`로 렌더되고, 이미지 파일은 `img_001.png` 1개뿐이며 Markdown은 `| 값 | 나 |\n|---|---|\n\n![그림 1](doc_images/img_001.png)\n`이다

#### Scenario: 바이너리가 없는 참조
- **WHEN** 단락, 본체가 없는 PNG 참조, 실제 PNG 그림, 단락 순서인 문서 `doc`를 변환한다
- **THEN** Markdown은 `앞\n\n![그림 1](doc_images/img_001.png)\n\n뒤\n`이고 파일은 `img_001.png` 1개, 종료 코드 0이다

#### Scenario: HWPX 머리말 안 그림은 제외된다
- **WHEN** 머리말(`hp:ctrl/hp:header`) 안 `hp:pic` 1개와 본문 최상위 `hp:pic` 1개가 같은 바이너리를 참조하는 실제 HWPX 샘플 `브라더 공공기관 보고서 양식.hwpx`를 변환한다
- **THEN** 이미지 수 1, 파일 `img_001.png` 1개(46249바이트, PNG)이고 Markdown에 `![그림 1](브라더%20공공기관%20보고서%20양식_images/img_001.png)` 한 줄만 있으며 단락 32개·표 8개는 변하지 않는다

### Requirement: 이미지가 없는 문서의 출력은 바뀌지 않는다
이미지가 없는 문서에서 변환기는 `_images` 폴더를 만들지 않고(SHALL), Markdown 바이트와 CLI 표준 출력 2행(`  단락 N개 · 표 M개[ · 제목 K개]`)을 이 변경 이전과 동일하게 유지해야 한다.

#### Scenario: 기존 합성 fixture와 실제 샘플 4개
- **WHEN** 이미지가 없는 합성 fixture(단락·표·제목)와 실제 샘플 `form200005063113.hwp`, `form210001070268.hwp`, `(서식1) 비영리법인 현황 제출 양식.hwpx`, `(서식2) 사업실적 및 사업계획 제출 양식.hwpx`를 변환한다
- **THEN** 표준 출력은 정확히 2행이고 `이미지` 글자가 없으며, `<stem>_images` 폴더가 생기지 않고, 단락·표·제목 수가 이전과 같다(각 (118, 8, 0), (47, 0, 0), (1, 1, 0), (80, 31, 0))

### Requirement: CLI는 이미지 수와 저장 위치를 보고한다
이미지가 1개 이상 출력되면 CLI는 2행 끝에 ` · 이미지 K개`(K = 링크 수)를 덧붙이고, 3행에 `  이미지: <출력 폴더>/<stem>_images/ (n files)`(n = 저장한 파일 수)를 출력해야 한다(SHALL). 종료 코드와 1행 형식은 바뀌지 않는다.

#### Scenario: 그림 두 장과 제목 하나
- **WHEN** 단락 2개·제목 1개·그림 2개(서로 다른 원본)인 `doc.hwp`를 `out/`으로 변환한다
- **THEN** 표준 출력은 `✓ doc.hwp → out/doc.md`, `  단락 2개 · 표 0개 · 제목 1개 · 이미지 2개`, `  이미지: out/doc_images/ (2 files)` 세 줄이고 종료 코드 0이다

#### Scenario: 라이브러리 결과 객체
- **WHEN** 같은 문서를 `convert()`로 변환한다
- **THEN** 결과의 `image_count == 2`, `image_dir == out/doc_images`, `image_files`는 `img_001.png`, `img_002.jpg` 경로 2개이며, 이미지가 없는 문서에서는 `image_count == 0`, `image_dir is None`, `image_files == ()`이다

### Requirement: 손상된 그림 레코드와 과대 바이너리는 오류다
HWP 5.0의 `BIN_DATA` 또는 `SHAPE_COMPONENT_PICTURE` 레코드가 필요한 길이보다 짧으면, 또는 HWPX의 `BinData/*` 엔트리 하나가 50MB를 넘으면 변환기는 `Hwp2mdError`(CLI 종료 코드 1)로 실패해야 하며(SHALL) 부분 출력 파일을 남기지 않아야 한다.

#### Scenario: 잘린 그림 레코드
- **WHEN** `SHAPE_COMPONENT_PICTURE` payload가 72바이트인 HWP 5.0 문서를 CLI로 변환한다
- **THEN** 종료 코드 1, stderr에 `truncated SHAPE_COMPONENT_PICTURE record`가 있고 `.md` 파일이 생기지 않는다
