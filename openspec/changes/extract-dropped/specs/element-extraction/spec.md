## ADDED Requirements

### Requirement: 하이퍼링크는 Markdown 링크로 출력된다
변환기는 HWP 5.0 필드(`%hlk` 컨트롤과 필드 시작·끝 제어문자 사이 글자), HWPX `hp:fieldBegin[@type="HYPERLINK"]`…`hp:fieldEnd`, HWPML `FIELDBEGIN[@Type="Hyperlink"]`…`FIELDEND` 를 읽어 표시 글자와 주소를 `[글자](주소)` 로 출력해야 한다(SHALL). 주소 스킴이 `http`·`https`·`mailto` 가 아니거나(책갈피·문서 안 이동·`javascript:` 등) 주소가 비면 표시 글자만 출력한다. 글자의 `[`·`]` 는 `\[`·`\]`, 주소의 공백·`(`·`)`·`<`·`>` 는 `%20`·`%28`·`%29`·`%3C`·`%3E` 로 쓴다.

#### Scenario: 웹 주소 링크
- **WHEN** "앞 " + 링크(표시 "누리집", 주소 `https://example.org/a b`) + " 뒤" 인 단락을 가진 HWP 5.0 문서를 변환한다
- **THEN** Markdown 은 `앞 [누리집](https://example.org/a%20b) 뒤\n` 이고 HWPX 로 만든 같은 문서도 같은 바이트를 낸다

#### Scenario: 허용하지 않는 스킴
- **WHEN** 주소가 `javascript:alert(1)` 인 링크(표시 "클릭")를 변환한다
- **THEN** Markdown 은 `클릭` 만 담고 `](` 를 담지 않는다

### Requirement: 각주와 미주는 Markdown 각주로 출력된다
변환기는 각주·미주 컨트롤(HWP 5.0 `fn  `·`en  `, HWPX `hp:footNote`·`hp:endNote`, HWPML `FOOTNOTE`·`ENDNOTE`)을 본문 위치에 각주 `[^n]`·미주 `[^en]` 참조로 남기고, 내용 단락은 문서 맨 끝에 `[^n]: 내용` 정의로 출력해야 한다(SHALL). 번호는 종류별로 문서 읽기 순서 1부터 매긴다. 내용이 여러 단락이면 둘째 단락부터 빈 줄 뒤 공백 4칸 들여쓰기로 잇는다. 각주 내용 단락은 단락 수(`counts.paragraphs`)에 세지 않고, 본문 단락으로 섞이지 않는다.

#### Scenario: 각주 하나
- **WHEN** 단락 "가" + 각주(내용 "주석") + "나" 를 가진 문서를 HWP 5.0 과 HWPX 로 각각 변환한다
- **THEN** 두 Markdown 이 모두 `가[^1]나\n\n[^1]: 주석\n` 이고 단락 수는 1 이다

#### Scenario: 각주와 미주 번호 공간
- **WHEN** 각주 2개와 미주 1개가 이 순서로 있는 문서를 변환한다
- **THEN** 참조는 `[^1]`, `[^2]`, `[^e1]` 이고 정의는 문서 끝에 각주 1·2, 미주 1 순서로 나온다

### Requirement: 머리말과 꼬리말은 본문에서 빠지고 건너뜀으로 보고된다
변환기는 세 포맷 모두 머리말·꼬리말 컨트롤 안의 글·표·그림을 본문 블록으로 내보내지 않아야 하고(SHALL), 컨트롤 하나마다 건너뜀 종류 `header_footer` 를 1 더해야 한다.

#### Scenario: HWP 5.0 머리말 텍스트가 본문에 섞이지 않는다
- **WHEN** 본문 단락 "본문" 과 머리말 컨트롤(안쪽 단락 "머리말", 그림 1개)을 가진 HWP 5.0 문서를 변환한다
- **THEN** Markdown 은 `본문\n` 이고 이미지 파일이 없으며 `skipped` 는 `[{"kind": "header_footer", "label": "머리말·꼬리말", "count": 1}]` 이다

### Requirement: 수식은 LaTeX 로, 실패하면 원문 스크립트로 출력된다
변환기는 수식 컨트롤(HWP 5.0 `eqed` + `EQEDIT` 레코드의 스크립트, HWPX `hp:equation/hp:script`, HWPML `EQUATION/SCRIPT`)의 스크립트를 `hwp2md.equation.to_latex` 로 바꿔, 단락 안에서는 `$LaTeX$`, 단락에 수식 하나뿐이면 `$$LaTeX$$` 로 출력해야 한다(SHALL). 변환이 실패하면 원문 스크립트를 코드 스팬(`` `스크립트` ``)으로 출력해 정보를 잃지 않는다.

#### Scenario: 분수
- **WHEN** 스크립트 `a over b` 인 수식 하나만 있는 단락을 변환한다
- **THEN** Markdown 은 `$$` 로 시작해 `$$\n` 으로 끝나는 한 줄이고 그 사이에 `\frac` 이 있다

#### Scenario: 변환 실패
- **WHEN** `to_latex` 가 항상 `None` 을 돌려주도록 바꾼 상태에서 단락 "식 " + 수식(스크립트 `a over b`)을 변환한다
- **THEN** Markdown 은 `식 ` 뒤에 백틱 1개로 감싼 `a over b` 코드 스팬이 오는 한 줄이다

### Requirement: 번호와 글머리표 목록은 Markdown 목록으로 출력된다
변환기는 문단 모양의 머리 종류가 번호(HWP 5.0 속성1 비트 23~24 = 2, HWPX `hh:heading[@type="NUMBER"]`, HWPML `HeadingType="Number"`) 또는 글머리표(= 3, `BULLET`, `Bullet`)인 단락에 `ListInfo` 를 붙여야 한다(SHALL). 렌더는 글머리표 `- `, 숫자 머리(`^\d{1,9}[.)]$`) `<머리> `, 그 밖 머리(`가.`, `(1)` 등)는 목록 문법 없이 `<머리> <글자>` 이다. 수준 들여쓰기는 공백 4칸 × 유효 수준이고, 연속한 목록 항목은 빈 줄 없이 `\n` 하나로 잇는다. 번호 값은 같은 번호 정의·수준의 연속 단락마다 1씩 늘리고 상위 수준이 나오면 하위를 처음으로 되돌리는 근사 계산이다.

#### Scenario: 글머리표 두 항목
- **WHEN** 글머리표 모양 단락 "하나", "둘" 다음에 일반 단락 "끝" 이 오는 문서를 변환한다
- **THEN** Markdown 은 `- 하나\n- 둘\n\n끝\n` 이고 단락 수는 3 이다

#### Scenario: 숫자 번호
- **WHEN** 형식 `^1.` 인 번호 모양 단락 "가", "나" 를 변환한다
- **THEN** Markdown 은 `1. 가\n2. 나\n` 이다

### Requirement: 표 칸 안 그림은 칸 안 이미지 링크로 출력된다
변환기는 표 칸 단락 안의 그림을 해당 칸에 `![그림 N](<stem>_images/img_NNN.<ext>)` 로 출력하고(SHALL), 칸 안 여러 단락·그림은 `<br>` 로 잇는다. 칸 안 그림도 이미지 번호(`img_NNN`, `그림 N`)와 이미지 수를 소비하며, 번호 순서는 문서 순서(표는 행 우선)다.

#### Scenario: 셀 그림과 본문 그림
- **WHEN** 첫 칸에 JPG 그림과 "값", 둘째 칸에 "나" 가 있는 1×2 표 다음에 PNG 그림이 오는 문서 `doc` 를 변환한다
- **THEN** Markdown 은 `| ![그림 1](doc_images/img_001.jpg)<br>값 | 나 |\n|---|---|\n\n![그림 2](doc_images/img_002.png)\n` 이고 이미지 수 2, 파일 2개다

### Requirement: 글상자·도형·묶음 개체 안 글과 그림이 출력된다
변환기는 글상자·도형(사각형·타원·다각형·호·곡선·연결선) 안 문단 목록과 묶음 개체의 자식 개체를 저장 순서대로 순회해, 안쪽 단락을 일반 단락(제목 판정 포함)으로, 안쪽 그림을 이미지 블록으로 앵커 단락 뒤에 출력해야 한다(SHALL). 글맵시와 양식 개체는 건너뛰고 각각 `textart`, `form_control` 로 보고한다.

#### Scenario: 사각형 글상자
- **WHEN** 본문 단락 "앞" 에 단락 2개("상자1", "상자2")와 PNG 그림 1개를 담은 사각형이 붙은 문서를 HWP 5.0 과 HWPX 로 변환한다
- **THEN** 두 Markdown 이 모두 `앞\n\n상자1\n\n상자2\n\n![그림 1](doc_images/img_001.png)\n` 이다

### Requirement: 표와 그림의 캡션은 개체 뒤 단락으로 출력된다
변환기는 표·그림 개체의 캡션 문단 목록을 그 개체 블록 바로 뒤에 일반 단락으로 출력해야 하고(SHALL), HWP 5.0 에서 `TABLE` 레코드보다 앞에 오는 캡션 `LIST_HEADER` 를 표 칸으로 취급하지 않아야 한다.

#### Scenario: 캡션 있는 HWP 5.0 표
- **WHEN** 캡션 "표 1 현황" 이 붙은 1×1 표(칸 "값")를 가진 HWP 5.0 문서를 변환한다
- **THEN** Markdown 은 `| 값 |\n|---|\n\n표 1 현황\n` 이고 표의 칸 수는 1 이다

### Requirement: 차트와 OLE 개체는 데이터 표 또는 이미지로 출력된다
변환기는 HWP 5.0 `SHAPE_COMPONENT_OLE` 의 BinData, HWPX `hp:ole` 의 `BinData/*.ole`(앞 4바이트 길이 접두를 벗긴 CFB), HWPX `hp:chart/@chartIDRef` 가 가리키는 차트 XML 을 읽어, OOXML 차트(`OOXMLChartContents` 스트림 또는 `c:chartSpace` XML)의 캐시값을 `차트: <제목>`(제목 없으면 `차트`) 단락과 첫 행이 `항목`·계열 이름인 Markdown 표로 출력해야 한다(SHALL). OOXML 차트가 없고 `\x01Ole10Native` 원본이 PNG·JPEG·GIF·BMP 이면 이미지로 출력한다. 구형 차트(`Contents` 만 있음)는 `chart_legacy`, 그 밖은 `ole` 로 건너뜀 보고한다.

#### Scenario: 막대 차트 캐시값
- **WHEN** 제목 "실적", 범주 "1월"·"2월", 계열 "매출"(값 10, 20) 인 OOXML 차트를 담은 OLE 개체가 있는 HWP 5.0 문서를 변환한다
- **THEN** Markdown 은 `차트: 실적\n\n| 항목 | 매출 |\n|---|---|\n| 1월 | 10 |\n| 2월 | 20 |\n` 이고 표 수는 1 이다

#### Scenario: 구형 차트
- **WHEN** CFB 안에 `Contents` 스트림만 있는 OLE 개체를 변환한다
- **THEN** 블록이 추가되지 않고 `skipped` 에 `chart_legacy` 1 이 있다

### Requirement: 필드 표시 글자는 보존된다
변환기는 누름틀·날짜·경로 등 하이퍼링크가 아닌 필드의 시작·끝 사이에 저장된 표시 글자를 본문 글자로 그대로 출력해야 한다(SHALL). 필드 값을 다시 계산하지 않는다.

#### Scenario: 누름틀
- **WHEN** 단락 "이름: " + 누름틀 필드(표시 글자 "홍길동") 를 변환한다
- **THEN** Markdown 은 `이름: 홍길동\n` 이다

### Requirement: 건너뛴 요소는 종류별 개수로 보고된다
변환기는 출력하지 못한 요소를 종류 `header_footer`(머리말·꼬리말), `memo`(메모), `hidden_comment`(숨은 설명), `chart_legacy`(데이터를 꺼낼 수 없는 차트), `ole`(그 밖의 OLE 개체), `textart`(글맵시), `form_control`(양식 개체), `image_link`(외부 연결 그림), `image_missing`(본체 없는 그림) 별로 세어 `ConvertResult.skipped`·`MemoryResult.skipped`(0 인 종류 제외, 위 순서의 `(kind, count)` 튜플), API 페이로드 `skipped`(`[{"kind", "label", "count"}]`, 항상 존재), CLI 표준 출력 마지막 줄 `  건너뜀: <라벨> <n>개[ · …]`(건너뛴 것이 있을 때만)로 보고해야 한다(SHALL).

#### Scenario: 건너뜀이 없는 문서
- **WHEN** 단락만 있는 문서를 CLI 로 변환한다
- **THEN** 표준 출력은 기존 2줄 그대로이고 API `skipped` 는 `[]` 이다

#### Scenario: 본체 없는 그림
- **WHEN** 단락, 본체가 없는 PNG 참조, 실제 PNG 그림, 단락 순서인 문서를 CLI 로 변환한다
- **THEN** 표준 출력 4행이 `  건너뜀: 본체 없는 그림 1개` 이고 종료 코드 0 이다

### Requirement: 세 입력 포맷은 같은 내용에 같은 Markdown 을 낸다
같은 요소 구성(링크·각주·미주·수식·목록·칸 그림·글상자·캡션·머리말)으로 만든 HWP 5.0·HWPX·HWPML 합성 문서는 같은 Markdown 바이트와 같은 `skipped` 를 내야 한다(SHALL).

#### Scenario: 교차 포맷 동일성
- **WHEN** `tests/unit/test_cross_format_extract.py` 의 요소별 합성 fixture 를 세 포맷으로 만들어 변환한다
- **THEN** fixture 마다 세 Markdown 과 세 `skipped` 가 같다

### Requirement: 추출하지 못하는 요소는 문서로 남긴다
저장소는 `docs/extraction-limits.md` 에 끝까지 추출하지 못하는 요소(비밀번호 문서, DRM 파일, 구형 차트 데이터, WMF/EMF 변환, 필드 값 재계산, 정확한 목록 번호, 수식 완전 변환, 글상자 시각적 순서, 단락 중간 그림 위치, 글맵시·양식 개체, 메모·숨은 설명, 서식)를 요소·상태·이유·대안 열을 가진 표로 적어야 하고(SHALL), 건너뜀 종류마다 한 행이 있어야 한다.

#### Scenario: 건너뜀 종류와 문서 대응
- **WHEN** `hwp2md.skips.SKIP_LABELS` 의 라벨 9개를 `docs/extraction-limits.md` 에서 찾는다
- **THEN** 9개 모두 표 행에 나온다
