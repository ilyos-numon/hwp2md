# hwpml-input Specification

## Purpose
TBD - created by archiving change extract-dropped. Update Purpose after archive.

## Requirements

### Requirement: HWPML 2.x 문서를 내용으로 판별한다
`detect_format` 은 DRM 서명·OLE·zip 이 아닌 입력에서 BOM(UTF-8, UTF-16LE/BE)을 건너뛴 앞 1024바이트 안에 루트 시작 태그 `<HWPML` 이 있으면 `"hwpml"` 을 돌려줘야 한다(SHALL). 확장자는 보지 않는다. XML 이지만 루트가 `HWPML` 이 아니면 지금처럼 `NotHwpFileError` 다.

#### Scenario: 확장자가 hwp 인 HWPML
- **WHEN** `<?xml version="1.0" encoding="UTF-8"?><HWPML Version="2.1">…` 로 시작하는 파일 `a.hwp` 를 판별한다
- **THEN** 결과는 `"hwpml"` 이다

#### Scenario: HWPML 이 아닌 XML
- **WHEN** `<?xml version="1.0"?><root/>` 바이트를 판별한다
- **THEN** `NotHwpFileError` 가 난다

### Requirement: HWPML 본문·제목·표·그림을 변환한다
HWPML 리더는 `BODY/SECTION/P/TEXT/CHAR` 의 글자(인라인 `TAB`·`NBSPACE`·`FWSPACE` 는 공백, `LINEBREAK` 는 줄바꿈, `HYPEN` 은 `-`)를 단락으로, `P@ParaShape` → `PARASHAPE@HeadingType="Outline"` 의 `@Level`+1(최대 6)을 제목 수준으로, `TABLE/ROW/CELL[@ColAddr,@RowAddr,@ColSpan,@RowSpan]/PARALIST` 를 표로, `PICTURE/IMAGE@BinItem` → `BINITEM[@Type="Embedding"]@BinData` → `TAIL/BINDATASTORAGE/BINDATA[@Id]` 의 Base64 를 이미지로 변환해야 한다(SHALL). Base64 를 푼 바이트가 PNG·JPEG·GIF·BMP 시그니처가 아니면 raw deflate 해제를 시도하고 실패하면 푼 바이트를 그대로 쓴다. `Type="Link"` 그림은 `image_link` 로 건너뛴다. 표·그림 배치·이름 규칙은 HWP 5.0·HWPX 와 같다.

#### Scenario: 합성 HWPML 기본 문서
- **WHEN** 개요 1수준 제목 "제목", 본문 "본문", 1×2 표("가","나"), PNG 그림 1개를 담은 합성 HWPML `doc.hml` 을 변환한다
- **THEN** Markdown 은 `# 제목\n\n본문\n\n| 가 | 나 |\n|---|---|\n\n![그림 1](doc_images/img_001.png)\n` 이고 같은 구성의 HWPX 변환 결과와 같다

### Requirement: HWPML 엔티티는 리터럴 내부 엔티티만 허용한다
HWPML 리더는 문서 앞 내부 DTD 부분집합에서 값에 `&`·`%`·`<` 가 없는 리터럴 일반 엔티티 선언(`<!ENTITY 이름 "값">`)만 받아 본문의 `&이름;` 을 그 값으로 바꾸고, 외부 엔티티(`SYSTEM`·`PUBLIC`)·파라미터 엔티티(`<!ENTITY %`)·그 밖의 선언이 있으면 `Hwp2mdError("unsupported DTD in HWPML")` 로 실패해야 한다(SHALL). XML 파싱은 기존과 같은 `resolve_entities=False, no_network=True, huge_tree=False` 파서로 한다.

#### Scenario: nbsp 엔티티
- **WHEN** `<!DOCTYPE HWPML [<!ENTITY nbsp "&#160;">]>` 를 선언하고 본문에 `가&nbsp;나` 를 쓴 합성 HWPML 을 변환한다
- **THEN** 변환이 성공하고 Markdown 단락은 `가` + U+00A0 + `나` 다

#### Scenario: 외부 엔티티 거부
- **WHEN** `<!DOCTYPE HWPML [<!ENTITY x SYSTEM "file:///etc/passwd">]>` 를 선언한 입력을 변환한다
- **THEN** `Hwp2mdError` 가 나고 메시지에 `unsupported DTD in HWPML` 이 있으며 CLI 종료 코드는 1 이다

### Requirement: HWPML 입력 크기와 인코딩을 제한한다
HWPML 리더는 UTF-8 과 BOM 있는 UTF-16LE/BE 를 받아야 하고(SHALL), Base64 를 푼 BINDATA 하나가 50MB(52428800바이트)를 넘으면 `Hwp2mdError("binary item too large: …")` 로 실패한다. 입력 전체 상한은 기존 메모리 API 상한(50MB)과 같다.

#### Scenario: UTF-16LE HWPML
- **WHEN** 같은 합성 HWPML 을 BOM 있는 UTF-16LE 로 인코딩해 변환한다
- **THEN** UTF-8 판과 같은 Markdown 이 나온다
