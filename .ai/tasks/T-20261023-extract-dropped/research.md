# 버려지는 요소 최대 추출 — 조사 결과

작성일 2026-10-23. 구현은 하지 않았다. 다음 단계 planner 의 근거 자료.

조사 방법: 아래 오픈소스를 스크래치 폴더에 얕게 클론해 해당 파일을 직접 읽었고, 한컴 공개 스펙 PDF 5종을 내려받아 텍스트로 확인했다. 우리 저장소의 HWPX 샘플(hwpxlib 테스트 파일)과 `tests/fixtures/hwpx/S0xx` 는 **구조(요소·속성 이름, 바이트 시그니처)만** 확인했고 내용은 옮기지 않았다.

### 확인한 출처 (커밋은 조사 시점)

| 약칭 | 저장소·문서 | 라이선스 | 비고 |
|---|---|---|---|
| 스펙5 | 한컴 「한글 문서 파일 형식 5.0 revision 1.3」 https://cdn.hancom.com/link/docs/한글문서파일형식_5.0_revision1.3.pdf | 한컴 공개 문서 조건(아래 §3) | 레코드·제어문자·필드 구조 |
| 스펙배포 | 「한글 문서 파일 형식 – 배포용 문서 revision 1.2」 https://cdn.hancom.com/link/docs/한글문서파일형식_배포용문서_revision1.2.pdf | 같음 | ViewText 복호화 알고리즘 공개 |
| 스펙수식 | 「한글 문서 파일 형식 – 수식 revision 1.3」 https://cdn.hancom.com/link/docs/한글문서파일형식_수식_revision1.3.pdf | 같음 | 수식 스크립트 문법 |
| 스펙차트 | 「한글 문서 파일 형식 – 차트 revision 1.2」 https://cdn.hancom.com/link/docs/한글문서파일형식_차트_revision1.2.pdf | 같음 | 구형 `Contents`(VtChart 객체 트리) |
| 스펙HWPML | 「한글 문서 파일 구조 3.0 / HWPML revision 1.2」 https://cdn.hancom.com/link/docs/한글문서파일형식3.0_HWPML_revision1.2.pdf | 같음 | II장이 HWPML 요소 정의 |
| pyhwp | https://github.com/mete0r/pyhwp (83239f0) | **AGPL-3.0** | `src/hwp5/distdoc.py`, `binmodel/tagid*.py` |
| hwplib | https://github.com/neolord0/hwplib (6746c27) | Apache-2.0 | Java, HWP 5.0 읽기·쓰기 |
| hwpxlib | https://github.com/neolord0/hwpxlib (f9fd225) | Apache-2.0 | Java, HWPX |
| hwp2hwpx | https://github.com/neolord0/hwp2hwpx (edc0527) | Apache-2.0 | HWP→HWPX 변환기 |
| hwp.js | https://github.com/hahnlee/hwp.js (b631063) | Apache-2.0 | TS 뷰어 |
| hwp-rs | https://github.com/hahnlee/hwp-rs (e41e7b4, 2022 이후 정체) | Apache-2.0 | Rust, 배포용 복호화 포함 |
| rhwp | https://github.com/edwardkim/rhwp (1a76570e) | MIT | Rust, 매우 넓은 범위(OLE·차트·WMF/EMF·HML·비밀번호) |
| unhwp | https://github.com/iyulab/unhwp (a061e12) | MIT | Rust, **HWP/HWPX → Markdown** (각주·수식 LaTeX·굵게) |
| python-hwpx | https://github.com/airmang/python-hwpx (7ca4582, PyPI 6.8.0) | Apache-2.0 | 순수 파이썬(의존성 lxml), EqEdit→LaTeX 포함 |
| hml-equation-parser | https://github.com/OpenBapul/hml-equation-parser (c0997f2, 2023) | Apache-2.0 | 순수 파이썬 수식→LaTeX (setup 이 pypandoc 요구) |
| hwp-eqn-ts | npm `hwp-eqn-ts` 1.1.0 (MIT 표기) | MIT | GitHub 저장소 `franknoh/hwp-eqn-ts` 는 **404** (npm 만 존재) |
| hwp_script_to_latex | RubyGems 1.6.0 (MIT 표기) | MIT | 소스 저장소 `PrivateCoach/hwp_script_to_latex` **404** |
| OWPML 모델 | https://github.com/hancom-io/hwpx-owpml-model | Apache-2.0 | 한컴 공식 C++ OWPML 모델 |
| Pillow WMF | https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html | — | "Windows 에서만 WMF/EMF 읽기" |
| Pyodide 패키지 | https://pyodide.org/en/stable/usage/packages-in-pyodide.html | — | cryptography 47.0.0, pycryptodome 3.23.0 포함 |

---

## 1. 요약 표

추출 가능성: 가능 = 스펙·오픈소스로 구조 확정, 합성 문서로 검증 가능 / 부분 = 일부만 / 불가.

| # | 요소 | HWP 5.0 저장 구조 | HWPX 저장 구조 | 추출 | 근거 | Markdown 표현 제안 | 난이도 | 라이선스 주의 |
|---|---|---|---|---|---|---|---|---|
| 1 | 표 칸 안 그림 | 셀 `LIST_HEADER` 아래 단락의 `CTRL_HEADER(gso)` → `SHAPE_COMPONENT_PICTURE`(0x55) | `hp:tc/hp:subList/hp:p/hp:run/hp:pic` | 가능 | 스펙5 표67·68, hwplib `ForControlTable` | GFM 셀 안 `![그림 N](images/…)` (셀 텍스트와 `<br>` 로 연결) | 하 | 없음 |
| 2 | 글상자 텍스트·그림 | gso 의 `SHAPE_COMPONENT`(0x4C) 아래 `LIST_HEADER`(글상자 12B 속성 뒤따름) + 단락들, 그 뒤 `SHAPE_COMPONENT_RECTANGLE` 등 | `hp:rect`/`hp:ellipse`/`hp:polygon`… 의 `hp:drawText/hp:subList/hp:p` | 가능 | 스펙5 표89·90, hwplib `ForControlRectangle`·`ForTextBox`, hwp-rs `draw_text.rs` | 본문 위치에 일반 단락으로 (선택: `> ` 인용) | 중 | 없음 |
| 3 | 차트·OLE | `$ole`/gso + `SHAPE_COMPONENT_OLE`(0x54, BinData ID @12). BinData `.OLE` = CFB(압축 해제 후). 내부 `OOXMLChartContents`(DrawingML chart XML), `Contents`(구형 VtChart), `\x02OlePres000`(EMF/WMF/DIB 미리보기), `\x01Ole10Native` | `hp:chart/@chartIDRef` → zip 안 차트 XML(OOXML chartSpace) / `hp:ole/@binaryItemIDRef` → `BinData/*.ole` (앞 4바이트 LE 길이 + CFB) | 부분 | 스펙5 "OLE 개체"·"차트 개체" 절, rhwp `parser/ole_container.rs`, hwpxlib `HWPXReader` | 차트: OOXML 캐시값 → Markdown 표 + 제목. 그 밖 OLE: 미리보기 이미지 추출(EMF/WMF/BMP) 또는 `[OLE 개체]` 자리표시 | 중(OOXML)·상(구형 Contents) | 없음 (구현 새로) |
| 4 | 수식 | `eqed` 컨트롤 + `EQEDIT`(0x58): UINT32 속성, WORD len + UTF-16 스크립트, … | `hp:equation/hp:script` 텍스트 | 가능(스크립트) / 부분(LaTeX 정확도) | 스펙5 표105, 스펙수식, hwplib `ForEQEdit` | `$…$` 인라인 / `$$…$$` 블록, 변환 실패 시 `` `원문 스크립트` `` | 하(추출)·중(LaTeX) | python-hwpx·hml-equation-parser 는 Apache-2.0 → NOTICE 필요 |
| 5 | 하이퍼링크 | 제어문자 3(필드 시작)~4(필드 끝) 사이 텍스트 + `CTRL_HEADER('%hlk')` 의 command 문자열 `URL(‘:’ ‘?’ 등 \ 이스케이프);1;0;0;` | `hp:ctrl/hp:fieldBegin[@type="HYPERLINK"]/hp:parameters/hp:stringParam[@name="Command"\|"Path"]` … `hp:fieldEnd` | 가능 | 스펙5 표152, hwplib `ForControlField`·`Inserting_HyperLink`, python-hwpx `oxml/hyperlink_form.py` | `[표시 텍스트](URL)` | 중 | 없음 |
| 6 | 각주·미주 | 제어문자 17 위치 + `CTRL_HEADER('fn  '/'en  ')` 아래 `LIST_HEADER` + 단락 | `hp:ctrl/hp:footNote`·`hp:endNote` (`@number`) `/hp:subList/hp:p` | 가능 | 스펙5 "각주/미주" 절, hwpxlib `FootNoteEndNoteReader`, unhwp `render/markdown.rs` | 본문 `[^n]`, 문서 끝 `[^n]: 내용` | 중 | 없음 |
| 7 | 머리말·꼬리말 | `CTRL_HEADER('head'/'foot')` (UINT32 적용 쪽 bit0~1) + `LIST_HEADER` + 단락 | `hp:ctrl/hp:header`·`hp:footer` (`@applyPageType`) `/hp:subList` | 가능 | 스펙5 표140·141, hwpxlib 샘플 `HeaderFooter.hwpx` | 기본 출력 제외(현재 HWP 5.0 은 본문에 섞임 → 버그 수정 대상). 옵션 시 문서 앞/뒤 블록 | 하 | 없음 |
| 8 | 목록 번호·글머리표 | `PARA_SHAPE` 속성1 bit23~24(2=번호, 3=글머리표), bit25~27 수준, 오프셋 30 UINT16 번호/글머리표 ID → DocInfo `NUMBERING`(0x17)·`BULLET`(0x18) | `hh:paraPr/hh:heading[@type="NUMBER"\|"BULLET"]/@idRef,@level` → `hh:numbering/hh:paraHead[@level,@numFormat,@start]`(텍스트 `^1.`), `hh:bullet/@char` | 가능(번호 계산은 근사) | 스펙5 표38~44, hwpxlib `ElementNames` | 글머리표 `- `, 번호 `1. `(DIGIT) 또는 계산한 머리 문자열("가.") 을 텍스트로, 수준별 들여쓰기 | 중 | 없음 |
| 9 | 자동 필드·책갈피·메모 | 쪽번호 위치 `pgnp`, 자동번호 `atno`(UINT32 종류 bit0~3), 날짜 등 필드 `%dte`/`%ddt` …, 책갈피 `bokm`(+`CTRL_DATA` 이름), 숨은 설명 `tcmt`(+문단), 메모: 필드 `%%me` + 마지막 Section 끝의 `MEMO_LIST`(0x5D)+`LIST_HEADER`+단락 | `hp:pageNum`, `hp:autoNum`, `hp:fieldBegin[@type="DATE"…]`, `hp:bookmark/@name`, `hp:hiddenComment/hp:subList`, 메모 `hp:memogroup/hp:memo` + `hp:fieldBegin[@type="MEMO"]` | 부분 | 스펙5 §4.3.10, hwplib `HWPReader.memo()`, python-hwpx `oxml/memo.py` | 필드: 저장된 표시 텍스트 그대로. 책갈피: `<a id>` 는 GFM 미지원 → 생략. 메모·숨은 설명: 각주와 같은 `[^m1]` 또는 생략 옵션. 쪽번호: 생략 | 중 | 없음 |
| 10 | 도형 안 텍스트·묶음 | 2번과 같은 글상자 구조. 묶음 `$con`: `SHAPE_COMPONENT` 안 자식 개수 WORD + 자식 ctrl ID 배열, 각 자식마다 `SHAPE_COMPONENT` 재귀 | `hp:container` 안 `hp:rect` 등 재귀, 각자 `hp:drawText` | 가능 | 스펙5 표120·121, hwp-rs `container.rs` | 2번과 동일 (자식 순서대로) | 중 | 없음 |
| 11 | 배포용 문서 | FileHeader 속성 bit2. 본문이 `ViewText/Section*`, 각 스트림 첫 레코드 `DISTRIBUTE_DOC_DATA`(0x1C, 256B) → LCG(MSVC rand) 로 XOR → 오프셋 `4+(seed&0xF)` 의 80B 중 앞 16B = AES-128-ECB 키 → 나머지 복호화 → (압축 비트면) raw deflate | 해당 없음 | 가능 | **스펙배포(한컴 공개)**, hwp-rs `section.rs`, pyhwp `distdoc.py`(AGPL, 참고만) | 일반 문서와 같음 | 중 | AES 구현 필요 → 순수 파이썬 직접 구현 또는 `cryptography` 선택 의존성. 한컴 출처 문구 의무 |
| 12 | 비밀번호 문서 | FileHeader 속성 bit1, EncryptVersion(4=한글 7.0 이후). 키는 비밀번호에서 유도 | ODF식 `META-INF/manifest.xml` 의 `encryption-data`(AES-256-CBC + PBKDF2) | **불가**(비밀번호 없이) / 비밀번호 입력 시 가능 | 스펙5 표3(알고리즘 미공개), rhwp `crates/rhwp-password-crypto`(역공학 구현), hwplib·pyhwp 미지원 | 거절 유지. HWPX 도 manifest 검사로 명시 거절 추가 | — | 알고리즘은 한컴 미공개 |
| 13 | 굵게·기울임 | `PARA_CHAR_SHAPE`(0x44): (UINT32 시작 위치, UINT32 CharShape ID) × n → DocInfo `CHAR_SHAPE`(0x15) 오프셋 46 UINT32 속성 bit0 기울임, bit1 진하게 | `hp:run/@charPrIDRef` → `hh:charPr` 자식 `hh:bold`, `hh:italic` 존재 여부 | 가능 | 스펙5 표33·35·61, hwpxlib `ElementNames` | `**…**`, `*…*` (공백 안쪽으로 붙이기) | 중 | 방침상 "서식 재현 안 함" — 옵션으로만 |
| 14 | WMF/EMF → PNG | BinData 확장자 wmf/emf, OLE 미리보기 `\x02OlePres000` 안 EMF/WMF | `BinData/*.wmf`, `*.emf` | 부분 | Pillow 문서(Windows 전용), rhwp `src/wmf`·`src/emf`(Rust, SVG 변환) | 변환 성공 시 PNG, 실패 시 원본 저장 + 링크 유지 | 상(순수 파이썬)·하(외부 도구) | 외부 도구(LibreOffice·Inkscape)는 선택 의존 |
| 15 | HWPML 2.x (.hml) | — (XML 텍스트 파일, 루트 `<HWPML Version="2.x">`) | `HEAD/BODY/TAIL`, `SECTION/P/TEXT/CHAR`, `TABLE/ROW/CELL/PARALIST`, `PICTURE/IMAGE@BinItem` → `BINITEM@BinData` → `TAIL/BINDATASTORAGE/BINDATA`(Base64) | 가능 | 스펙HWPML II장, rhwp `src/parser/hml/`, 샘플 S019·S020 구조 | 기존 블록 모델 그대로 | 중 | 없음 |
| 16 | 문서보안 DRM 파일 | 파일 첫 바이트 `9B 20` + ASCII `DRMONE  This Document is encrypted and protected by …` (OLE·zip 시그니처 없음) | 같은 래퍼 (확장자만 .hwpx) | **불가** | 샘플 S001·S002 헤더 직접 확인, 엔트로피 ≈ 7.97 bit/byte | `drm_protected` 오류로 거절 | 하(판별만) | 상용 DRM 복호화 시도 금지 |

---

## 2. 요소별 상세

공통 메모 (HWP 5.0)

- 태그 번호 (HWPTAG_BEGIN = 0x10): DocInfo `BIN_DATA 0x12`, `CHAR_SHAPE 0x15`, `NUMBERING 0x17`, `BULLET 0x18`, `PARA_SHAPE 0x19`, `DISTRIBUTE_DOC_DATA 0x1C`. 본문 `PARA_HEADER 0x42`, `PARA_TEXT 0x43`, `PARA_CHAR_SHAPE 0x44`, `CTRL_HEADER 0x47`, `LIST_HEADER 0x48`, `SHAPE_COMPONENT 0x4C`, `TABLE 0x4D`, `SHAPE_COMPONENT_LINE 0x4E`, `RECTANGLE 0x4F`, `ELLIPSE 0x50`, `ARC 0x51`, `POLYGON 0x52`, `CURVE 0x53`, `OLE 0x54`, `PICTURE 0x55`, `CONTAINER 0x56`, `CTRL_DATA 0x57`, `EQEDIT 0x58`, `TEXTART 0x5A`, `MEMO_LIST 0x5D`, `CHART_DATA 0x5F` (pyhwp `tagids.py` 와 스펙5 표13·57 일치).
- 컨트롤 ID: 스펙은 `MAKE_4CHID(a,b,c,d) = a<<24|b<<16|c<<8|d` 이고 UINT32 LE 로 저장되므로 **바이트열은 거꾸로**(`'tbl '` → 바이트 ` lbt`). 현재 코드의 `CTRL_ID_TABLE` 비교 방식을 그대로 확장하면 된다.
- 제어 문자(스펙5 표6): extended = 1,2,3,11,12,14,15,16,17,18,21,22,23 (8 WCHAR, 두 번째~일곱 번째 WCHAR 12바이트 중 앞 4바이트가 컨트롤 ID). **확장 제어문자 하나가 같은 단락의 `CTRL_HEADER` 하나와 등장 순서로 1:1 대응**한다. 이걸로 각주 번호·그림·수식의 단락 안 위치를 복원할 수 있다(지금은 위치를 버리고 단락 뒤에 붙인다).
  3=필드 시작, 4=필드 끝(inline), 11=그리기 개체/표, 15=숨은 설명, 16=머리말/꼬리말, 17=각주/미주, 18=자동번호, 21=페이지 컨트롤, 22=책갈피/찾아보기, 23=덧말/글자 겹침.
- `LIST_HEADER`: 스펙은 INT16 문단 수지만 hwp-rs·hwplib 모두 **UINT32(4바이트)로 읽어야 맞다**고 주석. 이어서 UINT32 속성.
- 개체 공통 속성(gso·tbl·eqed 의 `CTRL_HEADER` 본문) 다음에 **캡션이 있으면 `LIST_HEADER`(+캡션 12~14B) 와 단락**이 `SHAPE_COMPONENT`/`TABLE` 레코드보다 먼저 온다 (hwplib `ForGsoControl` 28~44행, `ForControlTable.caption()`).
  → **현재 `_parse_table` 은 `TABLE` 앞의 캡션 `LIST_HEADER` 를 셀로 오인할 수 있다** (level == ctrl_level+1 인 모든 LIST_HEADER 를 셀로 처리). 캡션 있는 표 샘플로 확인 필요. 캡션 자체도 지금 버려지는 요소다(Markdown: 표·그림 아래 `*캡션*` 단락).
- PARA_TEXT 의 확장 제어문자 블록: 코드(2B) + 추가 정보(12B, 앞 4B = 컨트롤 ID) + 코드(2B). hwplib `ParaText.addExtendCharForHyperlinkStart` 가 바이트 순서 근거.

### 2.1 표 칸 안 그림

- HWP 5.0: 셀 단락 파싱 시 `bin_data=None` 으로 넘기고 있어 버려진다(`body.py` `_parse_table` → `_parse_paragraph(..., None)`). 셀 단락의 trailing 블록 중 `Image` 를 셀 내용에 넣으면 된다. 레코드 구조는 본문 그림과 동일(셀 LIST_HEADER 와 같은 level 의 PARA_HEADER 아래 `CTRL_HEADER(gso)` → … → `SHAPE_COMPONENT_PICTURE` 오프셋 71 UINT16 BinData ID).
- HWPX: `hp:tc/hp:subList/hp:p/hp:run/hp:pic/hc:img/@binaryItemIDRef`. 현재 HWPX 셀 처리는 `hp:t` 만 모은다.
- Markdown: GFM 표 셀 안에 `![그림 3](images/img_003.png)` 를 넣으면 대부분 렌더러가 표시한다. 셀 안 줄바꿈은 기존대로 `<br>`. 웹 미리보기 렌더러(§9.6 규칙)가 셀 안 이미지 토큰을 허용하는지 확인 필요.
- 번호 규칙: 셀 안 이미지도 `img_NNN` 번호를 소비하도록 바꾸면 기존 출력 번호가 밀린다 → 결정 기록 필요.
- 합성 문서 최소 구조: 1×1 표 하나, 셀 단락 안 그림 1개, BinData 1개(작은 PNG). HWPX 는 `hp:tc` 안 `hp:pic` 하나 + `content.hpf` 항목.

### 2.2 글상자(텍스트 박스) 안 텍스트와 그림

- HWP 5.0 레코드 순서 (hwplib `ForGsoControl`, `ForControlRectangle`, `ForTextBox`; hwp-rs `shape_object/rectangle.rs`, `draw_text.rs`):
  1. `CTRL_HEADER('gso ')` (L) — 개체 공통 속성
  2. (선택) 캡션 `LIST_HEADER` + 단락, (선택) `CTRL_DATA`
  3. `SHAPE_COMPONENT` (L+1) — gso 이면 컨트롤 ID 가 앞에 두 번 기록됨(hwplib 50행 `readUInt4` 후 판별). 이 ID 로 실제 종류(`$rec`, `$pic`, `$ole`, `$con`…) 결정
  4. (도형일 때, 선택) `LIST_HEADER` (L+2): 문단 리스트 헤더 뒤에 글상자 속성 12B(여백 4×INT16 + 최대 폭 UINT32, 스펙5 표90). 그 뒤 단락들 `PARA_HEADER`(L+2) …
  5. `SHAPE_COMPONENT_RECTANGLE`/`ELLIPSE`/`POLYGON`… (L+2)
- 레벨 관계(LIST_HEADER 와 단락이 같은 level)는 표 셀과 같은 패턴으로 **추정** — 합성 문서·실샘플로 확인 필요.
- 현재 `_parse_gso` 는 하위 트리의 모든 PICTURE 를 모으고 텍스트를 버린다. 개선안: gso 하위를 순회하며 LIST_HEADER 뒤 단락은 `_parse_paragraph` 로 재귀(그림 포함), 단독 그림 개체는 기존처럼 이미지.
- HWPX: `hp:rect`(그리고 `hp:ellipse`, `hp:arc`, `hp:polygon`, `hp:curve`, `hp:connectLine`)의 자식 `hp:drawText/hp:subList/hp:p`. hwpxlib 샘플 `SimpleRectangle.hwpx` 에서 `hp:drawText lastWidth=… > hp:subList > hp:p > hp:run > hp:t` 와 형제 `hp:textMargin` 확인.
- 글맵시(`hp:textart`, HWP `SHAPE_COMPONENT_TEXTART` 0x5A)도 텍스트를 가진다 — HWPX 는 `hp:textart/@text`(hwpxlib `TextArtReader` 기준, 속성명은 합성 시 재확인).
- Markdown: 문서 흐름상 앵커 단락 뒤에 일반 단락으로. 제목 판정은 하지 않는다(본문 수준).
- 합성 문서: 사각형 하나 + 글상자 단락 2개 + 글상자 안 그림 1개.

### 2.3 그래프·차트·OLE

- HWP 5.0 `SHAPE_COMPONENT_OLE`(0x54) 페이로드: hwplib `ForControlOLE` 기준 UINT32 속성(bit16~21 개체 종류: 1 Embedded, 2 Link, 3 Static, 4 Equation), INT32 extent x, INT32 extent y, **UINT16 BinData ID (오프셋 12)**, 테두리 색·두께·속성. 스펙5 표118 은 속성을 UINT16 으로 적었으나 hwplib 은 4바이트로 읽는다 → 오프셋 12 를 1순위, 실샘플로 확인.
- BinData 항목(`BIN_DATA` 종류 STORAGE 또는 확장자 `OLE`)의 스트림은 압축 해제 후 **CFB(OLE 복합 파일)**. HWPX 의 `BinData/*.ole` 은 **앞 4바이트 LE 길이 + CFB** (hwpxlib `SimpleOLE.hwpx` 로 직접 확인: 프리픽스 값 = 나머지 길이, 그 뒤 `D0 CF 11 E0`). rhwp `parse_ole_container` 도 "선언 길이 = 잔여 길이일 때만 벗긴다"는 같은 규칙.
- CFB 내부 스트림 (스펙5 "차트 개체" 절, rhwp `ole_container.rs`):
  - `OOXMLChartContents`: 한글 2018 이후 차트. 루트 `c:chartSpace` 인 DrawingML Chart XML(ECMA-376). `c:ser` 마다 `c:tx`(계열명), `c:cat`(`c:strRef/c:strCache/c:pt/c:v`), `c:val`(`c:numRef/c:numCache/c:pt/c:v`) 캐시값이 들어 있어 **lxml 로 표 복원 가능**. 차트 제목 `c:title//a:t`.
  - `Contents`: 구형(한글 Neo 이하) 차트. 스펙차트의 VtChart 객체 트리(DataGrid 에 데이터). 바이너리 객체 직렬화라 구현 비용 큼 — rhwp `src/ole_chart/` 가 Rust 로 파싱. 1차 범위 밖 권장.
  - `\x02OlePres000`: OLE 표시 캐시. 헤더 뒤 EMF(`EMR_HEADER`, 오프셋 40 에 `" EMF"`) 또는 WMF(`01 00 09 00 03`) 또는 DIB. rhwp `strip_ole_presentation_header`·`wmf_start_offset` 가 시작점 탐색 로직(시그니처 스캔).
  - `\x01Ole10Native`: `[UINT32 LE 길이][원본 바이트]` — 그림판 등 임베딩이면 BMP/PNG 원본. hwpxlib 샘플은 CLSID 0003000A(Paintbrush) 로 이 형식이었다.
  - `CHART_DATA`(0x5F) 레코드: 스펙5 표57 에 "2바이트, 차트 데이터"로만 있음. 내용 미확인.
- HWPX: `hp:chart/@chartIDRef` 를 hwpxlib 가 **zip 엔트리 경로로 그대로** 읽는다(`HWPXReader` 140~144행). 그 XML 은 OOXML chartSpace(hwpxlib `Namespaces.ooxmlchart = http://www.hancom.co.kr/hwpml/2016/ooxmlchart` 래퍼 가능성 — 실샘플 확인 필요). `hp:ole/@binaryItemIDRef` → `content.hpf` 의 `media-type="application/ole"` 항목.
- Markdown: 차트 → `**차트: 제목**` + 계열×범주 표. 차트 데이터가 없으면 미리보기 이미지(EMF/WMF→§2.14) 또는 `[차트]` 자리표시. 일반 OLE → `Ole10Native` 가 이미지면 이미지, 아니면 미리보기, 둘 다 없으면 `[OLE 개체]`.
- 합성 문서: olefile 은 쓰기를 못 하므로 CFB 생성이 필요 — 테스트용 최소 CFB 작성기를 tests 쪽에 두거나(512B 섹터 1~2개면 충분), rhwp 처럼 `mini_cfb` 를 직접 작성. HWPX 차트는 zip 안 차트 XML 하나 + `hp:chart` 로 간단.

### 2.4 수식

- HWP 5.0 `EQEDIT`(0x58): UINT32 속성(bit0 줄/글자 단위), **WORD len + WCHAR[len] 스크립트**, UINT32 글자 크기, COLORREF, INT16 baseline, (UINT16 미문서화), 버전 문자열, 글꼴 이름 (스펙5 표105 + hwplib `ForEQEdit`, hwp-rs `equation.rs` 가 미문서화 UINT16 지적). 컨트롤은 `CTRL_HEADER('eqed')` 아래.
- HWPX: `hp:equation`(속성 `version`, `baseLine`, `font` …) 의 자식 `hp:script` 텍스트. 샘플 `SimpleEquation.hwpx` 에서 `hp:shapeComment`(대체 텍스트 "수식입니다.") 와 `hp:script` 확인.
- 문법: 스펙수식 (EQN 호환: `over`, `sqrt`, `sum _{} ^{}`, `matrix{…#…&…}`, `cases`, `left ( … right )`, `rm`/`it` 글꼴 명령, `~`·`` ` `` 공백, 그리스 문자·기호 명령어).
- LaTeX 변환 오픈소스 (실제 존재 확인):
  - **python-hwpx `src/hwpx/equation/eqedit.py` + `tokens.py`** (Apache-2.0, 표준 라이브러리만, 약 670줄). `eqedit_to_latex()`. NOTICE 에 hml-equation-parser 를 "행동 근거로만 참고한 clean-room" 이라 명시. 그룹 깊이·길이 상한 있음. → **가장 적합한 후보**(벤더링 또는 선택 의존성).
  - hml-equation-parser `hulkEqParser.py`·`hulkReplaceMethod.py`·`convertMap.json` (Apache-2.0, 약 300줄 + 매핑 JSON 281줄). 토큰 치환 + 괄호 짝 찾기로 `over`→`\frac`, `matrix`/`bar`/`brace` 계열을 바꾸는 방식. setup 이 pypandoc 을 요구하지만 변환 함수 자체는 표준 라이브러리만 쓴다.
  - unhwp `src/equation.rs` (MIT, Rust 809줄) — 알고리즘 참고용.
  - hwp-eqn-ts (npm, MIT 표기, GitHub 404), hwp_script_to_latex (Ruby, 저장소 404) — 소스 검증 불가, 제외.
- Markdown: 인라인(`treatAsChar`/글자 단위) `$…$`, 독립 단락이면 `$$…$$`. 변환기가 실패하면 원문 스크립트를 코드 스팬으로 남긴다(정보 손실 없음). 웹 미리보기는 수식 렌더러가 없으므로 텍스트로 보임 — 렌더러 추가는 별도 결정.
- 합성 문서: `eqed` 컨트롤 + EQEDIT 레코드 1개(스크립트 `a over b`), HWPX 는 `hp:equation/hp:script`.

### 2.5 하이퍼링크

- HWP 5.0: PARA_TEXT 안 제어문자 3(필드 시작, extended, 컨트롤 ID `%hlk`) … 표시 텍스트 … 제어문자 4(필드 끝, inline). 대응 `CTRL_HEADER` 레이아웃(스펙5 표152, hwplib `ForControlField`): ctrl ID(4) · UINT32 속성 · BYTE 기타 속성 · **WORD len + WCHAR command** · UINT32 인스턴스 ID. 이어서 `CTRL_DATA`(파라미터 셋, 필드 이름) 가 올 수 있다.
- command 형식(스펙에 없음, 구현에서 확인): `대상;종류;0;0;`. 종류 1 = 웹, 2 = 메일(`mailto:` 꼬리 `;2;0;0`), 0 = 문서 안 책갈피(`?이름`). 대상 안 `:` `?` `;` `#` 는 `\` 로 이스케이프. `|` 앞에 툴팁이 올 수 있음 (python-hwpx `hyperlink_form.py` 의 `hyperlink_target()` 이 복원 규칙: 꼬리 `;\d+;\d+;\d+;?$` 제거 → `|` 앞부분 → `\(.)` 언이스케이프). hwplib 샘플도 `https\://…\?…;1;0;0;` 형식.
- HWPX: `hp:run/hp:ctrl/hp:fieldBegin[@type="HYPERLINK"]` (`@fieldid="627600491"` = `%hlk`) 의 `hp:parameters/hp:stringParam[@name="Path"]`(원문 URL, 웹·메일만) 또는 `[@name="Command"]`. 표시 텍스트는 이후 `hp:t` 들, 끝은 `hp:ctrl/hp:fieldEnd[@beginIDRef]`.
- 필드는 하이퍼링크 외에도 누름틀(`%clk`), 날짜(`%dte`/`%ddt`), 경로, 상호참조, 메일머지, 메모(`%%me`) 등 — 모두 같은 시작/끝 구조라 **표시 텍스트는 이미 본문에 나온다**. 링크만 URL 을 덧붙이면 된다.
- Markdown: `[텍스트](URL)`. URL 의 `)`·공백은 `%29`/`<…>` 처리, `javascript:` 등 스킴은 버린다(웹 미리보기 XSS 규칙과 일치). 책갈피 링크(`?이름`)는 텍스트만.
- 합성 문서: 단락 텍스트 `앞 [3 %hlk] 링크 [4] 뒤` + `CTRL_HEADER('%hlk')` 1개.

### 2.6 각주·미주

- HWP 5.0: 제어문자 17 + `CTRL_HEADER('fn  ')`/`('en  ')`. 스펙5 "각주/미주" 절: 속성 없이 8바이트 직렬화(번호 정보로 쓰지 말 것). 아래 `LIST_HEADER` + 단락들. 번호는 **등장 순서로 매긴다**(unhwp 도 같은 방식, 구역별 `[^구역-n]`).
- HWPX: `hp:ctrl/hp:footNote[@number, @suffixChar, @instId]/hp:subList/hp:p`, `hp:endNote` 동일. 각주 본문 첫 단락 안에 `hp:autoNum numType="FOOTNOTE"` 가 번호를 그린다(본문 텍스트로 취급하지 말 것).
- 현재 동작: HWP 5.0 은 각주 내용이 본문 단락으로 섞이고, HWPX 는 빠진다(feature-reference §12.1).
- Markdown: 본문 위치에 `[^1]`, 문서 끝에 `[^1]: 내용`(여러 단락은 공백 4칸 들여쓰기 이어쓰기). 미주도 같은 형식으로 번호 공간을 분리(`[^e1]`). 블록 모델에 각주 참조·정의 표현을 추가해야 한다(현재 `Paragraph.text` 문자열뿐).
- 합성 문서: 단락 하나에 각주 1개(본문 `가[17]나`), 각주 단락 1개.

### 2.7 머리말·꼬리말

- HWP 5.0: `CTRL_HEADER('head'/'foot')` — UINT32 속성(bit0~1: 0 양쪽, 1 짝수, 2 홀수), HWPUNIT 폭·높이, BYTE×2 참조 여부(스펙5 표140). 그 뒤 `LIST_HEADER` + 단락. 구역마다 여러 개(홀/짝) 있을 수 있다.
- HWPX: `hp:ctrl/hp:header[@applyPageType="BOTH"|"EVEN"|"ODD"]/hp:subList`, `hp:footer` 동일. 머리말 안에 표·쪽번호가 흔하다(S019/S020 HWPML 샘플도 HEADER/FOOTER 안 TABLE).
- 제안: 기본은 **본문에서 제외**(현재 HWP 5.0 이 본문에 섞는 것은 HWPX 와 불일치 → 정리 대상). 필요 시 옵션으로 문서 맨 앞/뒤에 한 번만(중복 제거) 출력.

### 2.8 목록 번호·글머리표

- HWP 5.0 (스펙5 표43·44): `PARA_SHAPE` 속성1 bit23~24 = 머리 모양(0 없음, 1 개요, 2 번호, 3 글머리표), bit25~27 = 수준(0~6 → 1~7수준). 오프셋 30 UINT16 = 번호 ID 또는 글머리표 ID(1부터인지 0부터인지는 **미확인** — hwplib 의 사용처로 확인 필요).
  - `NUMBERING`(0x17): 수준 1~7 각각 [문단 머리 정보 8B(UINT32 속성, HWPUNIT16×2, UINT32 글자모양) + WORD len + WCHAR 형식 문자열(`^1.`, `^n`, `^N`)] , UINT16 시작 번호, (한글 2010 계열 이후 문서 버전부터) 수준별 시작번호 UINT32×7, (5.1+) 수준 8~10 확장. 번호 모양 코드는 스펙5 표41 (0 `1,2,3`, 2 `I,II`, 4 `A,B`, 8 `가,나,다`, 10 `ㄱ,ㄴ` 등) — 문단 머리 정보 속성의 어느 비트에 있는지는 추출한 텍스트에서 잘려 **미확인**.
  - `BULLET`(0x18): 문단 머리 정보 8B + WCHAR 글머리표 문자 + INT32 이미지 글머리 여부 + 4B + WCHAR 체크 글머리표 문자.
- HWPX: `hh:paraPr/hh:heading[@type="NUMBER"|"BULLET", @idRef, @level]` → `hh:numberings/hh:numbering[@id,@start]/hh:paraHead[@level,@start,@numFormat="DIGIT"|"HANGUL_SYLLABLE"…]` 의 텍스트(`^1.`). 글머리표 `hh:bullets/hh:bullet[@id,@char]`. (샘플 header.xml 로 `hh:numbering`·`hh:paraHead` 확인. `hh:bullet` 은 샘플에 없음, 이름은 hwpxlib `ElementNames` 기준.)
- HWPML: `PARASHAPE@HeadingType="Number"|"Bullet"`, `@Heading`(ID), `@Level`; `NUMBERINGLIST/NUMBERING/PARAHEAD@Level,@NumFormat`.
- 번호 계산: 같은 번호 ID·수준의 연속 단락에 카운터를 두고 상위 수준이 나오면 하위 리셋. 시작번호·"새 번호로 시작"(`nwno`) 은 근사.
- Markdown: 글머리표 → `- `(수준당 2칸 들여쓰기). 번호 → `DIGIT` 이고 형식이 `^n.` 계열이면 `1. `, 그 밖(가·나·다, ①, (1))은 **계산된 머리 문자열을 텍스트 앞에 붙인 일반 단락**(Markdown 순서 목록은 숫자만 표현). 현재 "번호 문단은 본문"(feature-reference §4.4) 결정과 충돌하지 않게 옵션 또는 결정 기록 필요.

### 2.9 자동 필드·책갈피·메모

- 쪽 번호: `pgnp`(쪽 번호 위치, 표시 위치 정의) — 본문 텍스트 아님, 버리면 된다. 쪽 번호가 머리말 안 `atno`(종류 0)로 들어가는 경우도 머리말 제외로 함께 빠진다.
- 자동 번호 `atno`(스펙5 표142·143): UINT32 속성(bit0~3 종류: 0 쪽, 1 각주, 2 미주, 3 그림, 4 표, 5 수식), UINT16 번호, WCHAR 사용자 기호·앞/뒤 장식. **캡션의 "그림 1", "표 2" 번호가 여기서 온다** → 캡션을 출력할 때 번호 값 사용 가능. HWPX `hp:autoNum[@num, @numType]`.
- 날짜·파일 경로·요약 등 필드: 필드 시작~끝 사이 **마지막으로 계산된 표시 텍스트**가 PARA_TEXT 에 그대로 있다 → 추가 작업 없이 이미 출력됨. 갱신값 재계산은 불가능하고 불필요.
- 책갈피 `bokm`: 이름은 `CTRL_DATA` 파라미터 셋(스펙5 표50~52: WORD 셋 ID, INT16 개수, 아이템 = WORD ID + WORD 종류 + 데이터, 종류 1 = PIT_BSTR WORD len + WCHAR). HWPX `hp:bookmark/@name`. GFM 은 앵커를 표준으로 지원하지 않아 출력 가치 낮음.
- 숨은 설명 `tcmt`: 문단 리스트만 가짐(스펙5 "숨은 설명" 절). HWPX `hp:hiddenComment/hp:subList`.
- 메모: HWP 5.0 은 필드 `%%me`(범위 표시) + **마지막 Section 스트림의 끝**에 `MEMO_LIST`(0x5D, UINT32 메모 인덱스) → `LIST_HEADER`(INT32 문단 수, UINT32 속성, UINT32 폭·높이) → 단락들 (hwplib `HWPReader.memo()`·`ForMemo`). HWPX 는 섹션 XML 의 `hp:memogroup/hp:memo` + 본문 `hp:fieldBegin[@type="MEMO"]` (python-hwpx `oxml/memo.py`). 필드 CTRL_HEADER 의 메모 인덱스(`%unk` 일 때 추가 INT32, hwplib)로 연결.
- Markdown 제안: 숨은 설명·메모는 각주와 같은 `[^m1]` 정의로, 또는 기본 제외 + 옵션. 개인정보 원칙상 메모(작성자 정보 포함 가능)는 **기본 제외**가 안전.

### 2.10 도형 안 텍스트, 묶음 개체

- 도형 텍스트는 §2.2 와 같은 `LIST_HEADER` 구조(사각형·타원·다각형·호·곡선 모두 가능, hwplib 각 `ForControl*` 에 `ForTextBox` 호출).
- 묶음 `$con` (스펙5 표120·121): `SHAPE_COMPONENT` 안 WORD 개수 + UINT32 컨트롤 ID 배열, 이어서 자식마다 `SHAPE_COMPONENT`(+글상자 LIST_HEADER + 종류별 레코드) 가 **한 단계 깊게** 반복(hwp-rs `ContainerContent`). 재귀 순회로 텍스트와 그림을 자식 순서대로 수집.
- HWPX: `hp:container` 의 자식 `hp:rect`/`hp:pic`/`hp:container`… 재귀. 현재는 `hp:pic` 만 모은다.
- 순서: 자식 배열 순서(z-order 아님). 시각적 읽기 순서와 다를 수 있다 — 한계로 기록.

### 2.11 배포용 문서

- **한컴이 알고리즘을 공식 공개**(스펙배포 2014). 절차:
  1. FileHeader 속성 bit2. 본문은 `BodyText` 대신 `ViewText/Section0..N`. 같은 방식으로 `Scripts/*`, `DocHistory/*` 도 암호화(본문만 필요).
  2. 각 스트림 맨 앞 레코드 `HWPTAG_DISTRIBUTE_DOC_DATA`(0x1C), 크기 256B. (레코드 헤더 4B 는 평문)
  3. seed = 데이터 앞 4B UINT32 LE. MSVC `srand(seed)`/`rand()` = `seed = seed*214013 + 2531011 (mod 2^32)`, 결과 `(seed>>16) & 0x7FFF`.
  4. 256B 난수 배열: 홀수 번째 `rand() & 0xFF` = 값 A, 짝수 번째 `(rand() & 0x0F) + 1` = 반복 횟수 B, A 를 B번 채우기를 256B 까지.
  5. 데이터 XOR 난수 배열. (hwp-rs 는 256B 전체, pyhwp 는 i≥4 만 XOR — 결과에 쓰는 구간은 오프셋 ≥4 라 동일)
  6. offset = `4 + (seed & 0xF)`, 거기서 80B = 비밀번호 SHA1 해시코드(UTF-16 문자열 40자), 그 다음 2B 옵션(0x01 복사 방지, 0x02 인쇄 방지). **키 = 해시코드 앞 16바이트**.
  7. 스트림의 나머지(레코드 다음 바이트 전부)를 **AES-128-ECB** 로 복호화 → FileHeader 압축 비트가 켜져 있으면 raw deflate 해제 → 일반 Section 레코드.
- 오픈소스: hwp-rs `crates/hwp/src/hwp/section.rs::from_distributed` (Apache-2.0), pyhwp `src/hwp5/distdoc.py` (AGPL — 읽고 알고리즘만 확인, 코드 사용 금지), hwplib `getChildStreamReaderForDistribution`, rhwp `src/parser/crypto.rs`.
- AES: 표준 라이브러리에 없다. 선택지 — (a) 순수 파이썬 AES-128 복호(FIPS-197, ECB 이므로 블록 독립, 약 150줄, 속도는 MB당 수 초 수준 예상·미측정) (b) `cryptography` 선택 의존성(`hwp2md[distdoc]`). Pyodide 에 cryptography 47.0.0 과 pycryptodome 이 내장되어 브라우저 모드에서도 로드 가능.
- 법적: 스펙배포 저작권 절은 "누구나 열람·복사·배포·사용 자유, 결과물 저작권은 개발자" + **결과물에 "본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다." 문구를 UI·매뉴얼·도움말·소스에 기재 의무**. 현재 저장소 README·docs·src 에 이 문구가 없다(grep 확인) — 이미 스펙5 를 참고했으므로 이번에 추가 권장. 배포용 문서는 "편집·복사·인쇄 제한" 기능이므로 텍스트 추출이 작성자 의도와 다를 수 있다는 점을 README 에 명시하는 것을 권장(법률 판단은 미확인).
- 합성 문서: 테스트에서 역방향(평문 Section → deflate → AES 암호화 → 앞에 DISTRIBUTE_DOC_DATA 256B: 임의 seed 로 난수 배열 만든 뒤 해시 위치에 키 넣고 XOR)으로 생성. FileHeader bit2 + `ViewText/Section0`.

### 2.12 암호화(비밀번호) 문서

- HWP 5.0: FileHeader bit1, EncryptVersion(스펙5 표3: 1 한글 2.5 이하, 2·3 한글 3.0, 4 한글 7.0 이후). 알고리즘은 **한컴 스펙에 없다**. hwplib("Files with passwords are not supported."), pyhwp(암호문 그대로 반환, 경고), hwp-rs·unhwp(Encrypted 오류) 모두 미지원. rhwp `crates/rhwp-password-crypto/src/lib.rs` 만 구현 — 비밀번호 SHA1 에서 AES-128 키 유도 후 1비트 피드백 시프트 레지스터 방식(함수 `derive…`, `decrypt_hwp5_stream`), 즉 **비밀번호가 반드시 필요**.
- HWPX: `META-INF/manifest.xml` 의 `odf:file-entry/odf:encryption-data`(`algorithm-name` aes256-cbc, `key-derivation-name` pbkdf2, 시작 키 sha256). 역시 비밀번호 필요. 현재 hwp2md 는 HWPX 암호화 검사가 없어 깨진 XML 오류로 끝날 것 — **manifest 에 `encryption-data` 가 있으면 `encrypted` 로 명시 거절** 추가 권장(rhwp `detect_odf_encryption` 과 같은 판별).
- `PrvText` 스트림(미리보기 텍스트, 스펙5 §3.2: 압축·암호화 표시 없음)이 비밀번호 문서에서도 평문인지는 **미확인**. 평문이라면 첫 일부 텍스트만 "부분 추출"로 줄 수 있으나, 작성자가 잠근 문서라 기본 제공은 비권장.
- 결론: 비밀번호 없이 불가. 비밀번호 입력 기능은 프로젝트 범위·보안 정책 결정 사항.

### 2.13 굵게·기울임

- HWP 5.0: `PARA_CHAR_SHAPE`(0x44) = (UINT32 시작 위치[WCHAR 단위, 제어문자 8칸 포함], UINT32 CharShape ID) × n. DocInfo `CHAR_SHAPE`(0x15) 등장 순서 = ID(0부터), **오프셋 46 UINT32 속성**(14+7×4+4), bit0 기울임, bit1 진하게, bit2~3 밑줄, bit15/16 위/아래 첨자, bit18~20 취소선(스펙5 표33·35).
- HWPX: `hp:run/@charPrIDRef` → `hh:charPr[@id]` 의 자식 `hh:bold`, `hh:italic`(존재 = 켜짐), `hh:underline/@type`, `hh:strikeout/@shape`.
- HWPML: `CHARSHAPE` 자식 `BOLD`, `ITALIC` (샘플에서 `BOLD`·`UNDERLINE` 확인).
- Markdown: `**굵게**`, `*기울임*`. 공백·구두점 경계 처리(unhwp `render/markdown.rs` 590~610행 "강조 기호는 비공백에 붙어야 함"), 표 셀·제목에는 적용하지 않기, 전체 단락이 굵으면(제목 대용 서식) 생략 등 휴리스틱 필요. README "서식 완벽 재현 안 함" 방침이므로 **옵션(`--emphasis`) + 결정 기록** 권장.

### 2.14 WMF/EMF → PNG

- Pillow: WMF/EMF **식별만** 가능, 읽기(래스터화)는 **Windows 에서만**(공식 문서). macOS·Linux·Pyodide 불가.
- 순수 파이썬 래스터라이저: 성숙한 오픈소스 **미확인**(검색 결과는 상용 Aspose 뿐). rhwp `src/wmf/`, `src/emf/` 가 Rust 로 WMF/EMF → SVG 변환(MIT) — 알고리즘 참고 가능하나 포팅 규모 큼(레코드 수십 종).
- 현실적 선택지: (a) 선택 의존: 시스템에 LibreOffice(`soffice --headless --convert-to png`) 또는 Inkscape 가 있으면 변환, 없으면 원본 저장 (b) 최소 WMF/EMF → SVG 변환기를 직접 작성(선·다각형·텍스트·비트맵 블릿 정도만) — 상 난이도 (c) EMF 안에 `EMR_STRETCHDIBITS` 비트맵 하나만 든 경우(스캔 이미지 흔함)는 DIB 를 BMP 로 꺼내는 부분 처리 — 중 난이도, rhwp `ole_container.rs` DIB→BMP 포장 로직(386행 근처) 참고.
- 출력: 변환 성공 시 `img_NNN.png` 와 원본 둘 다 두지 말고 PNG 하나. 실패 시 현재처럼 원본 확장자.

### 2.15 HWPML 2.x (.hml)

- 판별: 파일이 XML 텍스트, 루트 `<HWPML Version="2.1">`(샘플 S019·S020 둘 다 2.1). 확장자가 `.hwp` 여도 OLE 시그니처 없이 `<?xml` 로 시작 → 현재는 `NotHwpFileError`. UTF-8 외 UTF-16LE/BE(BOM) 가능(rhwp `parser/hml/encoding.rs`).
- **DTD 내부 엔티티**: 샘플 두 개 모두 `<!DOCTYPE HWPML [<!ENTITY nbsp "&#160;">]>` 선언 후 본문에 `&nbsp;` 사용(각각 21회·73회). 현재 프로젝트 XML 파서 설정(`resolve_entities=False`)으로는 엔티티가 풀리지 않는다 → 이 엔티티만 허용하는 처리 필요(rhwp `reader.rs` 1448~1660행: 값에 `&` 없는 리터럴 `<!ENTITY 이름 "값">` 만 받아들이고 파라미터 엔티티 거부). 공공 법령 정보 배포본이 이 형태로 내보낸다는 rhwp 주석과 일치.
- 구조(스펙HWPML II장 + 샘플 확인):
  - `HWPML/HEAD[@SecCnt]/MAPPINGTABLE/{BINDATALIST, FACENAMELIST, BORDERFILLLIST, CHARSHAPELIST, TABDEFLIST, NUMBERINGLIST, PARASHAPELIST, STYLELIST}`, `HEAD/DOCSUMMARY`(TITLE·AUTHOR 등 — 메타데이터로 쓸 수 있으나 개인정보 주의), `HEAD/DOCSETTING`.
  - 본문: `HWPML/BODY/SECTION[@Id]/P[@ParaShape,@Style]/TEXT[@CharShape]/CHAR`(텍스트). `CHAR` 자식 인라인: `TAB`, `LINEBREAK`, `HYPEN`(철자 그대로), `NBSPACE`, `FWSPACE`, `TITLEMARK`, `MARKPENBEGIN/END`.
  - `TEXT` 의 자식(표68 이후): `SECDEF`, `COLDEF`, `TABLE`, `PICTURE`, `CONTAINER`, `OLE`, `EQUATION`, `TEXTART`, `LINE`, `RECTANGLE`, `ELLIPSE`, `ARC`, `POLYGON`, `CURVE`, `CONNECTLINE`, `FIELDBEGIN`, `FIELDEND`, `BOOKMARK`, `HEADER`, `FOOTER`, `FOOTNOTE`, `ENDNOTE`, `AUTONUM`, `NEWNUM`, `PAGENUMCTRL`, `PAGEHIDING`, `PAGENUM`, `INDEXMARK`, `COMPOSE`, `DUTMAL`, `HIDDENCOMMENT`, 양식 컨트롤. → HWPX `hp:run` 자식과 거의 1:1 (대문자·속성 CamelCase).
  - 문단 순서: `TEXT` 들과 그 안 `CHAR`·컨트롤 순서가 문서 순서.
- 제목(개요) 판정: `P@ParaShape` → `PARASHAPE[@Id]` 의 `@HeadingType`("None"|"Outline"|"Number"|"Bullet") 과 `@Level`(0~6). `Outline` 이면 Markdown 수준 = Level+1. (샘플에서 HeadingType 값 "None"/"Outline", Level 0~6 확인. 두 샘플 모두 본문 단락이 Outline 모양을 실제로 쓰지는 않음.) 번호/글머리표는 `@Heading`(ID) → `NUMBERINGLIST/NUMBERING/PARAHEAD[@Level,@NumFormat]`.
- 표: `TABLE[@RowCount,@ColCount]/ROW/CELL[@ColAddr,@RowAddr,@ColSpan,@RowSpan]/PARALIST/P…`. 기존 `_place_cells` 그대로 재사용 가능. 캡션은 `TABLE/CAPTION/PARALIST`(스펙 기준, 샘플 없음).
- 그림: `PICTURE/IMAGE@BinItem` → `HEAD/MAPPINGTABLE/BINDATALIST/BINITEM[@Type="Embedding"|"Link", @BinData, @Format]` → `TAIL/BINDATASTORAGE/BINDATA[@Id=BinData, @Encoding="Base64", @Size, @Compress]` 텍스트(Base64, 줄바꿈 포함). `Type="Link"` 는 외부 파일(`@APath`/`@RPath`) — 제외.
  - 압축: 스펙 표181 은 `Compress` 기본값 **true**(raw deflate 로 추정). 그러나 두 샘플은 `Compress` 속성이 없고 Base64 해제 결과가 바로 JPEG/PNG/BMP/GIF 매직(압축 아님). → 해제 후 매직 바이트 판별, 아니면 raw deflate 시도, 실패 시 원본 사용(현재 HWP5 BinData 정책과 같음).
  - `@Size` 는 실제 디코딩 길이와 다르게 기록된 경우가 있음(샘플에서 여러 BINDATA 가 같은 큰 값) → 신뢰하지 말 것.
  - 샘플에서 그림 위치: 본문 `SECTION/P/TEXT/PICTURE` 와 **표 셀 안**, `HEADER/FOOTER` 안 표.
- 필드: `FIELDBEGIN[@Type,@Name,@InstId,@Command,…]`, `FIELDEND`. 하이퍼링크는 `Type="Hyperlink"`, URL 은 `@Command`(HWP5 command 와 같은 형식으로 추정, 샘플은 `Bookmark` 형만 있어 미확인).
- 머리말·꼬리말: `TEXT/HEADER[@ApplyPageType]/PARALIST`, `FOOTER` 동일. 각주 `FOOTNOTE/PARALIST`. 수식 `EQUATION/SCRIPT`.
- 보안: 크기 상한·XXE 차단은 HWPX 와 같은 파서 설정 + nbsp 예외. Base64 해제 총량 상한 필요(BINDATA 는 수백 KB~수 MB).
- 오픈소스: rhwp `src/parser/hml/`(MIT, Rust, 2,410줄 — 요소 지원 목록·엔티티 처리·경고 체계). hwplib 에는 HWPML 리더 없음(검색 결과 없음). pyhwp 는 HWP→자체 XML 출력이지 HWPML 리더 아님.
- 합성 문서: 문자열로 바로 생성 가능(가장 쉬움). HEAD(PARASHAPE 2개: None/Outline Level 0, BINITEM 1개), BODY(제목 단락, 본문 단락, 1×2 표, 그림 1개), TAIL(BINDATA Base64 PNG 1개), DOCTYPE nbsp 엔티티 포함 케이스 1개.

### 2.16 문서보안 DRM 파일

- 시그니처(샘플 S001.hwpx·S002.hwp 헤더만 확인): 오프셋 0 `9B 20`, 이어서 ASCII `DRMONE  This Document is encrypted and protected by 상용 DRM \r\n` (상용 문서보안 제품명이 헤더 문자열에 명시). 그 뒤 버전·길이로 보이는 바이너리 헤더(오프셋 0x40~0x100, 0x00/0xFF 채움 구간)가 있고 이후 본체는 엔트로피 약 7.97 bit/byte(암호문 수준). 파일 안 어디에도 `PK\x03\x04`·`D0 CF 11 E0` 시그니처 없음 → 원본 컨테이너 전체가 암호화되어 래핑됨.
- 공개 스펙: 웹 검색으로 형식 문서 **찾지 못함(미확인)**. 오픈소스 복호화 구현도 찾지 못함. 이런 기업 DRM 은 키를 라이선스 서버·클라이언트 에이전트가 관리하므로 오픈소스로 원문 복원은 **불가**로 판정.
- HWP 5.0 FileHeader 의 "DRM 보안 문서"(bit4)·"공인 인증서 DRM"(bit10)는 **한컴 자체 DRM** 으로, OLE 컨테이너는 유지되고 `DocOptions/DrmLicense`·`DrmRootSect` 스트림이 있다(스펙5 §3.2.8). 이 경우도 키 없이는 불가 — 현재 미검사이므로 `UnsupportedHwpError("drm document")` 거절 추가 권장(unhwp `hwp5/header.rs` 가 bit4·bit10 을 DRM 으로 판정).
- 판별 규칙 제안: 입력 앞 64바이트 안에 `b"DRMONE"` 가 있거나(오프셋 2), 앞 2바이트가 `9B 20` 이고 OLE/zip/XML 시그니처가 아니면 `drm_protected` 오류. 사용자 문구: "문서보안(DRM)이 적용된 파일입니다. 보안 프로그램에서 해제 후 다시 시도하세요." 복호화·우회 시도는 하지 않는다.
- 합성 문서: 테스트용 가짜 헤더(`9B 20 'DRMONE  …'` + 난수 바이트)로 판별만 검증. 실샘플 내용은 테스트에 쓰지 않는다.

---

## 3. 라이선스 결론

전제: 프로젝트에 LICENSE 파일이 없고 `pyproject.toml` 에도 license 필드가 없다(확인함). 무엇을 가져오든 **프로젝트 라이선스를 먼저 정해야** 한다(MIT 또는 Apache-2.0 권장 — 아래 Apache 코드 벤더링과 호환).

**직접 가져올 수 있는 것 (벤더링 + 라이선스 고지)**

- python-hwpx `src/hwpx/equation/eqedit.py`, `tokens.py` (Apache-2.0, 표준 라이브러리만): 수식 → LaTeX. 파일 상단 SPDX 유지, 프로젝트 `NOTICE` 에 출처·변경 사실 기재.
- hml-equation-parser 변환 함수와 `convertMap.json` (Apache-2.0): 같은 조건. 둘 중 하나만 택할 것(python-hwpx 쪽이 최신·상한 처리 있음).
- rhwp·unhwp(MIT) 코드는 Rust 라 직접 사용은 아니지만, 포팅 시 MIT 고지를 남기면 허용.

**스펙만 참고해 새로 구현해야 하는 것**

- HWP 5.0 레코드 확장 전부(필드·각주·머리말·글상자·묶음·OLE·EQEDIT·NUMBERING/BULLET·CHAR_SHAPE·캡션·메모) — 스펙5 + Apache 구현(hwplib·hwp-rs) 의 바이트 레이아웃 확인만.
- 배포용 문서 복호화 — 스펙배포(한컴 공개)대로 새로 작성. **pyhwp(AGPL-3.0)는 코드·구조를 옮기지 않는다** (읽은 것은 알고리즘 확인 목적).
- HWPML 2.x 리더 — 스펙HWPML 로 새로 작성.
- OOXML 차트 캐시 → 표, OLE CFB 스트림 분리, OlePres 헤더 스킵 — 공개 표준(ECMA-376, MS-OLEDS) 기준 새로 작성.
- **한컴 공개 문서 조건**: 스펙을 참고한 결과물은 "본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다." 를 UI·매뉴얼·도움말·소스에 기재해야 한다(스펙5·스펙배포 저작권 절). 현재 누락 → README·웹 UI 푸터·`src/hwp2md/__init__.py` docstring 에 추가 필요.

**선택적 의존성으로 둘 수 있는 것**

- `cryptography`(Apache-2.0/BSD) 또는 `pycryptodome`(BSD/Public Domain): 배포용 문서 AES-128-ECB. 둘 다 Pyodide 내장. 순수 파이썬 AES 직접 구현으로 의존성 0 유지도 가능.
- `python-hwpx` 전체(Apache-2.0, 의존성 lxml): 수식만 쓰기엔 큼(파이썬 파일 183개, 약 9만 줄) → 벤더링이 낫다.
- LibreOffice/Inkscape(외부 실행 파일): WMF/EMF 변환. 파이썬 패키지 의존성이 아니라 런타임 탐지로.
- `latex2mathml`(MIT): 웹 미리보기 수식 렌더가 필요할 때만.

---

## 4. 끝까지 불가능하거나 비현실적인 것

| 항목 | 판정 | 이유 |
|---|---|---|
| 비밀번호 문서 (HWP 5.0·HWPX) 를 비밀번호 없이 | 불가 | 키가 비밀번호에서 유도된다(rhwp 구현·ODF manifest). 알고리즘도 한컴 미공개. 무차별 대입은 범위·윤리상 제외 |
| 기업 DRM 래핑 파일 (`DRMONE` 헤더), 한컴 DRM(bit4·bit10) | 불가 | 원본 전체가 암호화, 키는 DRM 서버·에이전트 보유, 공개 형식·오픈소스 없음. 판별 후 거절만 |
| 구형 차트 `Contents`(VtChart 바이너리 객체 트리) 데이터 | 비현실적(1차) | 스펙차트 객체 수십 종, rhwp 도 별도 모듈로 대규모 구현. 미리보기 이미지로 대체 |
| WMF/EMF 순수 파이썬 래스터화 (Windows·외부 도구 없이, 브라우저 모드 포함) | 비현실적 | 성숙한 순수 파이썬 구현 미확인, Pillow 는 Windows 전용. 비트맵 1장짜리 EMF 만 부분 처리 가능 |
| 필드 값 재계산(날짜·쪽번호·상호참조 최신값) | 불가·불필요 | 저장된 마지막 표시 텍스트만 있다. 쪽 번호는 레이아웃 엔진 없이는 계산 불가 |
| 수식의 완전한 LaTeX 동등 변환 | 부분 | 한컴 수식 문법 전 범위를 커버하는 변환기 없음(오픈소스 모두 토큰 치환 기반). 실패 시 원문 스크립트 보존으로 손실 방지 |
| 묶음·글상자 텍스트의 시각적 읽기 순서 | 부분 | 저장 순서(자식 배열)만 신뢰 가능. 좌표 기반 재정렬은 레이아웃 계산 필요 |
| 번호 목록의 정확한 번호(새 번호 시작·구역 이어짐·개요 번호 혼합) | 부분 | 한글 레이아웃 엔진 규칙 전부는 미공개, 근사 카운터로만 |

## 남은 확인 사항 (실샘플·합성 문서로)

1. gso 글상자 `LIST_HEADER`·단락의 level 관계, 캡션 있는 표에서 현재 `_parse_table` 오동작 여부.
2. `SHAPE_COMPONENT_OLE` BinData ID 오프셋(12 vs 10).
3. `PARA_SHAPE` 오프셋 30 번호/글머리표 ID 가 0-기준인지 1-기준인지, NUMBERING 문단 머리 정보의 번호 모양 비트 위치.
4. HWPX `hp:chart` 의 chartIDRef 가리키는 파일의 실제 루트 요소(OOXML `c:chartSpace` 직접인지 한컴 래퍼인지).
5. HWPML `FIELDBEGIN Type="Hyperlink"` 의 `Command` 형식, `BINDATA Compress="true"` 실제 압축 방식.
6. 비밀번호 HWP 의 `PrvText` 평문 여부.
