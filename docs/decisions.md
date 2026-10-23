# 결정 기록

## 2026-10-22 스택: Python 3.11+, olefile, hatchling+uv, ruff+mypy, pytest
- 결정: HWP 5.0 바이너리는 `olefile`(OLE 컨테이너) + `zlib` + 자체 레코드 파서. HWPX는 `lxml`로 파싱하되 HWPX 태스크 시작 때 의존성을 선언한다. 패키징 hatchling(src 레이아웃), 환경 uv, 린트·포맷 ruff, 타입 mypy strict, 테스트 pytest(단위 `tests/unit`, E2E `tests/e2e`는 실제 콘솔 스크립트 실행).
- 이유: 한컴 없이 순수 파이썬으로 동작(README 방향). olefile는 의존성이 없고 HWP OLE 구조에 충분하다. uv는 lock·venv·스크립트 실행을 한 도구로 처리해 에이전트 명령 블록이 짧아진다.

## 2026-10-22 범위: 첫 스모크는 본문 단락 텍스트만
- 결정: 표·이미지·각주·제목 계층·HWPX는 후속 태스크. 이번 태스크는 PARA_TEXT → Markdown 단락만.
- 이유: 파이프라인(OLE → 압축 해제 → 레코드 → 렌더 → CLI)이 끝까지 한 번 돌아가는 것을 먼저 확인하고, 블록 추상화(표·이미지)는 그 위에 얹는다.

## 2026-10-22 테스트 fixture: 공개 샘플 대신 합성 HWP 5.0 생성기
- 결정: `tests/synth_hwp5.py`가 명세 기준 최소 HWP 5.0 파일(OLE + FileHeader + DocInfo + BodyText/Section0)을 코드로 만든다. 실제 샘플은 `tests/fixtures/*.hwp`에 넣으면 E2E가 자동으로 추가 실행한다(라이선스 확인 전까지 커밋하지 않음).
- 이유: 네트워크·라이선스 확인 없이 결정적(deterministic) 테스트가 가능하고, 압축/비압축·암호화 플래그 같은 변형을 바이트 단위로 통제할 수 있다.

## 2026-10-22 블록 모델 도입: 단락·표를 Block 리스트로 추상화
- 결정: reader는 `list[str]` 대신 `list[Block]`(`Paragraph(text)` | `Table(rows)`)을 돌려주고, renderer(`render_blocks`)가 블록 종류별로 Markdown을 만든다. 표는 HWP 5.0 레코드 level과 `CTRL_HEADER(tbl)` → `TABLE` → `LIST_HEADER`(셀) → 셀 단락 순서로 조립한다. 기존 `read_paragraphs`·`render_markdown`은 호환 래퍼로 남긴다.
- 이유: README "기술 방향"(블록 단위 추상화 후 렌더러 분리). 이미지·각주 블록을 같은 리스트에 얹을 수 있고, 표가 본문 단락 흐름 안의 제자리에 놓인다.

## 2026-10-22 표 렌더: 첫 행을 헤더로, 병합 셀은 빈 칸, 셀 내 단락은 <br>
- 결정: Markdown(GFM) 표는 헤더 행이 필수이므로 표의 첫 행을 헤더로 쓴다. 병합 셀(col_span/row_span > 1)은 원 셀 자리에 텍스트를 두고 덮인 칸은 빈 칸으로 둔다. 셀 안의 여러 단락·줄바꿈은 `<br>`로 잇고 `|`는 `\|`로 이스케이프한다. 중첩 표는 부모 셀 텍스트로 평탄화(셀 텍스트를 공백으로 이어 붙임)한다. 표 셀 안 단락은 본문 단락 수에 세지 않는다.
- 이유: GFM은 rowspan/colspan을 표현할 수 없어 행·열 수를 보존하는 쪽을 택했다. 빈 칸으로 두면 열 정렬이 유지되어 RAG 청킹과 사람이 읽는 데 모두 유리하다. 중첩 표는 공공 양식에서 드물고 레이아웃 재현은 범위 밖이다.

## 2026-10-22 포맷 감지: 확장자가 아니라 파일 내용(OLE 시그니처 / zip + mimetype)으로 판정
- 결정: `convert()`는 `detect_format()`으로 입력을 판정한다. OLE 복합 파일이면 HWP 5.0 리더, zip이고 `mimetype` 엔트리가 `application/hwp+zip`이거나 `Contents/section0.xml`이 있으면 HWPX 리더, 그 외는 `NotHwpFileError`. 확장자(.hwp/.hwpx)는 보지 않는다.
- 이유: 공공기관 배포 파일은 HWPX 내용에 .hwp 확장자가 붙은 경우가 있다. 두 포맷은 첫 바이트(OLE 매직 / zip 매직)로 확실히 구분되므로 내용 판정이 더 정확하고, 사용자는 포맷 차이를 몰라도 된다(vision 시나리오 4).

## 2026-10-22 HWPX 파서: lxml + 보안 파서 옵션(외부 엔티티·네트워크 차단)
- 결정: HWPX 섹션 XML은 `lxml.etree`로 파싱하고 파서는 항상 `XMLParser(resolve_entities=False, no_network=True, huge_tree=False)`로 만든다. 섹션 XML 엔트리가 50MB를 넘으면 거부한다. 타입 검사는 `lxml-stubs`(dev 의존성)로 한다.
- 이유: 외부에서 받은 문서를 그대로 열므로 XXE(외부 엔티티로 로컬 파일 읽기)·엔티티 폭발(billion laughs)·zip 폭탄을 기본으로 막아야 한다. lxml은 수 MB 섹션도 빠르고 네임스페이스 처리가 표준 라이브러리보다 안정적이다.

## 2026-10-22 HWPX 본문 범위: 단락 텍스트와 표만, 머리말·꼬리말·각주·그림·도형은 무시
- 결정: `hp:p`의 `hp:run` 안에서 `hp:t`(텍스트)와 `hp:tbl`(표)만 블록으로 바꾼다. `hp:secPr`, `hp:ctrl`(머리말·꼬리말·쪽번호·단 설정), `hp:footNote`/`hp:endNote`, `hp:pic`, 도형 요소는 건너뛴다. 인라인 요소는 `hp:tab`→공백, `hp:lineBreak`→줄바꿈, 그 외는 빈 문자열(뒤따르는 텍스트는 유지).
- 이유: 머리말·쪽번호는 본문 흐름에 섞이면 RAG 청킹에 잡음이 된다. 각주·그림은 별도 태스크(각주 → 하단 참조, 이미지 → 추출)에서 자기 자리를 갖는다. HWP 5.0 리더의 "표 아닌 컨트롤 단락 흘려보냄"과 다르지만 실제 샘플에서 두 방식의 결과 차이는 없었고, 통일은 각주 태스크에서 한다.

## 2026-10-22 제목 판정: 문단 모양(PARA_SHAPE/paraPr)의 개요 비트만 본다
- 결정: HWP 5.0은 `DocInfo`의 `HWPTAG_PARA_SHAPE` 속성1 비트 23~24(머리 모양)가 개요(1)일 때 비트 25~27(수준 0~6)을, HWPX는 `header.xml`의 `hh:paraPr/hh:heading[@type="OUTLINE"]/@level`을 제목 수준으로 쓴다. 단락은 `PARA_HEADER.para_shape_id` / `hp:p/@paraPrIDRef`로 문단 모양을 찾는다. 스타일(`STYLE` 레코드, `hh:style`)의 이름·참조는 판정에 쓰지 않는다. 머리 모양이 번호·글머리표인 단락은 본문으로 둔다(리스트 렌더는 후속).
- 이유: 한컴은 스타일을 적용하면 단락의 문단 모양 ID를 바꿔 저장하므로 문단 모양이 실제로 렌더되는 속성이다. 실제 샘플 5개 모두 본문 단락의 스타일 ID가 0(바탕글)이고 개요 정보는 문단 모양에만 정의되어 있었다(단, 현재 실제 샘플의 본문 단락은 개요 문단 모양을 쓰지 않아 양성 검증은 합성 fixture로 한다). 스타일 이름("개요 N"/"Outline N")은 언어·사용자 설정에 따라 바뀔 수 있다.

## 2026-10-22 제목 수준: 개요 1~6 → `#`~`######`, 7 이상은 `######`로 clamp. 블록은 `Paragraph.level`
- 결정: Markdown 제목 수준 = min(개요 수준 + 1, 6). 별도 `Heading` 블록 대신 `Paragraph`에 `level: int = 0` 필드를 둔다(0 본문). 렌더는 `#`×level + 공백 + 텍스트(내부 줄바꿈은 공백), 빈 텍스트 제목은 생략, 표 셀 안의 개요 단락은 셀 텍스트로만 쓴다. 제목 길이 제한은 두지 않는다.
- 이유: Markdown은 6수준까지만 있고, 개요 7수준도 문단 모양으로 정의될 수 있으므로(샘플 1 DocInfo에 정의 있음) 버리는 것보다 가장 낮은 제목으로 두는 쪽이 구조를 보존한다. 제목은 HWP에서도 "개요 속성이 붙은 단락"이라 필드 추가가 모델에 맞고, 기존 `Paragraph("text")` 호출·동등 비교·테스트가 그대로 유효하다.

## 2026-10-22 CLI 2행: 제목이 있을 때만 ` · 제목 K개`를 덧붙이고, 제목은 단락 수에서 분리한다
- 결정: `paragraph_count`는 본문 단락(level 0)만, `heading_count`는 제목만 센다. CLI 2행은 `단락 N개 · 표 M개`를 유지하고 제목이 1개 이상일 때만 ` · 제목 K개`를 덧붙인다.
- 이유: vision 시나리오 1의 `제목 12개 · 표 4개` 표기와 맞추면서, 제목이 없는 문서(양식류 대부분)의 출력과 기존 테스트 문자열을 바꾸지 않기 위해서다.

## 2026-10-22 이미지 블록: Image(file_name, data), out/<stem>_images/img_NNN.<ext>, 링크 ![그림 N](<stem>_images/…)
- 결정: Image 를 블록 모델의 세 번째 블록으로 둔다. 리더가 원본별 파일명을 첫 등장 순 3자리(`img_001.png`)로 부여하고, 렌더러는 등장 순 `그림 N` alt 와 `.md` 기준 상대 경로(공백 → `%20`)로 링크를 쓰며, convert 는 고유 파일만 `out/<stem>_images/` 에 쓴다. 같은 원본을 다시 참조하면 파일 1개·링크 N개다. 포맷 변환은 하지 않는다(바이트 그대로).
- 이유: vision 시나리오 1의 출력 레이아웃과 맞추고, 블록 모델 일관성을 지키며, 두 포맷이 같은 출력을 내고, 의존성을 늘리지 않기 위해서다.

## 2026-10-22 이미지 제외 범위: 표 셀·머리말·꼬리말·글상자 안 그림, LINK 그림, 본체 없는 참조는 건너뜀
- 결정: 표 셀 단락은 바이너리 해석 없이 파싱해 그림 번호를 선점하지 않는다. HWPX `hp:ctrl` 무시 정책을 유지하고, HWP 5.0 BIN_DATA 의 LINK/STORAGE 종류는 무시하며, 본체가 없는 참조는 경고 없이 생략한다.
- 이유: GFM 표 셀 안 이미지는 후속 과제이고, 머리말 로고는 RAG 에 잡음이며(실제 샘플에서 같은 로고가 머리말에 중복), 외부 경로 그림은 재현할 수 없다.

## 2026-10-22 HWP 5.0 BinData 해석: BIN_DATA(0x12) 1-based ID → BinData/BIN%04X.<ext>, 그림 레코드(0x55) offset 71, 압축은 레코드 비트 → 헤더 비트 → zlib 실패 시 raw
- 결정: DocInfo BIN_DATA(0x12) 레코드를 등장 순 1-based ID 로 세어 EMBEDDING 항목만 `BinData/BIN%04X.<ext>` 스트림에 대응시킨다. 본문 gso 컨트롤 아래 그림 레코드(0x55)의 offset 71 에서 BinData ID(UINT16)를 읽는다. 압축 여부는 레코드 속성 비트가 지정하면 그것을, 기본값이면 FileHeader 압축 비트를 따르고, zlib(raw deflate) 해제에 실패하면 원본 바이트를 그대로 쓴다.
- 이유: 레이아웃은 공개 스펙과 pyhwp 소스로 교차 확인했다. 저장소의 실제 HWP 5.0 샘플 2개에는 그림이 없어(BinData 스토리지·BIN_DATA 레코드 0) 실제 바이트 검증은 불가했고, 양성 샘플이 추가되면 E2E 가 자동으로 검증한다. 해제 실패 시 raw 로 두어 변환 전체가 실패하지 않게 한다.

## 2026-10-23 웹 프레임워크: Starlette+uvicorn (extra web)
- 결정: `hwp2md serve` 는 Starlette 앱을 uvicorn 으로 띄운다. 두 의존성은 optional extra `hwp2md[web]` 에만 두고, 기본 설치(CLI·라이브러리)는 그대로 olefile·lxml 만 쓴다. 기본 바인드는 localhost:8765, 외부 바인드는 `--host` 로만 하고 인증은 없다.
- 이유: 순수 파이썬 소형 의존성이고 정적 파일 제공과 TestClient 가 내장돼 테스트가 쉽다. FastAPI 는 pydantic 이 추가로 들어오고, 표준 라이브러리 `http.server` 는 라우팅·멀티파트·테스트를 직접 짜야 한다.

## 2026-10-23 메모리 변환: Source = Path | bytes, olefile 에는 BytesIO
- 결정: 리더 입력 타입을 `Path | bytes` 로 넓히고, bytes 일 때 HWP 5.0 은 `olefile.OleFileIO(io.BytesIO(data))`, HWPX 는 `zipfile.ZipFile(io.BytesIO(data))` 로 연다. 공개 API `convert_bytes(data, filename)` 는 디스크에 쓰지 않고 `MemoryResult`(markdown·images·개수)를 돌려주며, markdown 은 `convert()` 가 쓰는 `.md` 와 바이트 동일하다. 입력은 50MB 상한.
- 이유: 웹 업로드를 임시 파일 없이 처리해야 "업로드는 저장하지 않음" 을 지킬 수 있고, 브라우저(Pyodide) 안에서도 같은 함수를 그대로 부를 수 있다. 같은 렌더 경로를 쓰므로 CLI 와 웹 결과가 갈라지지 않는다.

## 2026-10-23 브라우저 모드: Pyodide 0.27.7 CDN + 서버가 소스 zip 제공
- 결정: "브라우저 안에서만 처리" 모드는 jsDelivr 에서 버전 고정한 Pyodide 0.27.7 을 불러오고, hwp2md(web 제외)와 olefile 의 순수 파이썬 소스는 서버가 `GET /pkg/hwp2md.zip` 으로 즉석에서 묶어 준다. lxml 은 Pyodide 가 제공하는 패키지를 쓴다. 변환할 파일 바이트는 서버로 보내지 않는다.
- 이유: wheel 에 Pyodide 를 동봉하면 패키지가 수십 MB 커지고, wheel 빌드 + micropip 방식은 빌드 단계와 PyPI 접근이 필요하다. 실행 중인 소스를 그대로 실으면 서버 모드와 같은 코드가 돈다. 대가로 첫 사용 시 인터넷이 필요하고 콜드 로드가 약 1분(측정 약 65초) 걸린다.

## 2026-10-23 미리보기 렌더러: 동봉 marked 12.0.2, <br> 외 HTML 이스케이프
- 결정: 미리보기는 `static/vendor/` 에 동봉한 marked 12.0.2 로 렌더하고, 원시 HTML 은 표 셀 줄바꿈용 `<br>` 만 살리고 나머지는 이스케이프한다. 링크·이미지 주소는 허용목록만 통과시킨다: 링크는 http/https/mailto 와 상대 경로, 이미지는 상대 경로와 `data:image/*;base64`.
- 이유: 문서 내용은 외부에서 온 입력이라 미리보기가 XSS 통로가 되면 안 된다. hwp2md 출력이 실제로 쓰는 HTML 은 `<br>` 뿐이고, 렌더러를 동봉하면 서버 모드는 CDN 없이 동작한다. 자체 렌더러보다 GFM 표 처리가 검증돼 있다.
