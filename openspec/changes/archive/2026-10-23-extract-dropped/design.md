# Design

## Context

- 파이프라인: `detect_format` → 포맷별 `read_blocks` → `render_blocks` → `.md`·이미지 쓰기(`convert`) 또는 메모리 결과(`memory.convert_bytes` → `to_payload`). 렌더러는 포맷을 모른다.
- 블록 모델은 `Paragraph(text, level)`, `Table(rows)`, `Image(file_name, data)` 세 가지라 링크 주소·각주 위치·수식·목록·칸 안 그림을 담을 곳이 없다.
- HWP 5.0 `decode_para_text` 는 확장 제어문자(1,2,3,11,12,14~18,21~23)를 지워 위치를 버린다. 확장 제어문자 하나는 같은 단락의 `CTRL_HEADER` 하나와 등장 순서로 1:1 대응한다(스펙5 표6). 이 대응으로 링크·각주·수식의 단락 안 위치를 복원한다.
- HWP 5.0 `_parse_paragraph` 는 표·`gso` 가 아닌 컨트롤의 안쪽 단락을 본문으로 흘려보내 머리말·각주가 본문에 섞인다. `_parse_table` 은 `TABLE` 앞 캡션 `LIST_HEADER` 를 칸으로 오인할 수 있다. `_parse_gso` 는 글상자 글을 버리고 머리말 안 그림까지 모은다.
- HWPX `parse_paragraph` 는 `hp:t`·`hp:tbl`·`hp:pic`·`hp:container` 외 run 자식을 무시하고, 칸 안 단락은 이미지 해석기 없이 파싱한다.
- 실제 샘플(`tests/fixtures/**`)은 gitignore 대상이라 저장소·CI·git worktree 에 없다. 샘플 이름에는 기관명이 들어 있어 테스트 코드에 쓰지 않는다 → 실제 샘플 E2E 는 구조 탐색(probe)으로 고르고, 없으면 skip.
- 오늘 추가된 샘플 때문에 기존 테스트 6개(단위)가 이미 실패한다: 샘플 수 고정 단언(`== 5`, `== 3`)과 확장자 `.hwpx` 인 DRM 래핑 파일을 HWPX 로 기대하는 매개변수 케이스.
- 의존성은 olefile·lxml 만. Pyodide 런타임 zip(`build_runtime_zip`)은 `hwp2md/**/*.py`(web 제외)를 자동으로 싣는다.
- 라이선스: pyhwp(AGPL-3.0) 코드는 쓰지 않는다. python-hwpx 수식 변환기(Apache-2.0)는 벤더링하고 NOTICE 에 출처를 적는다. 한컴 공개 스펙 조건 문구를 README·UI·소스에 넣는다.

## Goals / Non-Goals

**Goals:**
- 조사로 구조가 확정된 요소(칸 그림·글상자·캡션·링크·각주/미주·수식·목록·OOXML 차트·OLE 원본 이미지·배포용 문서·HWPML)를 세 포맷에서 같은 Markdown 으로 꺼낸다.
- 못 꺼내는 것은 종류별로 세어 CLI·API·화면에 보고하고, 이유·대안을 `docs/extraction-limits.md` 에 적는다.
- 기존 블록 생성자·동등성·출력은 새 요소가 없는 문서에서 그대로다.

**Non-Goals:**
- 비밀번호 문서 복호화(비밀번호 입력 포함), DRM 해제, 구형 VtChart 차트 데이터, WMF/EMF 래스터화·OLE 미리보기(OlePres) 추출, 필드 값 재계산, 굵게·기울임 등 서식(README "하지 않는 것"), 좌표 기반 읽기 순서, 단락 중간 그림 위치 통일, 웹 미리보기 수식 렌더러, CLI 새 옵션, `design/v3` 의 백엔드 연결.

## Decisions

1. **블록 모델은 필드 추가로 확장한다** — `Paragraph.inlines`, `Paragraph.list_info`, `Table.cells`, 새 블록 `Note`, 인라인 타입 `Link`·`NoteRef`·`Math`(+ 기존 `Image`). 기본값이 빈 값이라 `Paragraph("x") == Paragraph("x", 0)` 같은 기존 비교가 유지된다. 대안 A(텍스트에 Markdown 을 미리 박아 넣기)는 이미지 번호를 렌더 순서로 매기는 현재 규칙과 충돌하고, 링크 허용목록 판정을 리더마다 반복하게 된다. 대안 B(블록 타입 전면 교체)는 기존 테스트 수백 개를 바꾼다.
2. **정규화 함수로 동등성을 지킨다** — 리더는 `make_paragraph(inlines, …)` 와 `make_table(grid)` 로만 새 블록을 만든다. 인라인이 문자열뿐이면 `inlines=()`, 칸이 모두 문자열뿐이면 `cells=()` 로 줄여 기존 값과 같아진다.
3. **각주 정의는 리더가 문서 끝에 `Note` 블록으로 둔다** — 번호는 종류별 문서 순서. 렌더러는 위치 그대로 출력하므로 끝에 모인다. 각주 단락은 단락 수에 세지 않는다.
4. **링크 허용 판정은 렌더러 한 곳(`render.safe_link_url`)** — 리더는 원문 주소를 그대로 넣는다. 허용 스킴은 미리보기 렌더러(feature-reference §9.6)와 같은 http·https·mailto.
5. **건너뜀 보고는 `SkipCounter` 를 리더에 선택 인자로 넘긴다** — `read_blocks(path, skips=None)`. 반환 타입(`list[Block]`)을 바꾸지 않아 기존 호출·테스트(`memory.read_blocks` monkeypatch 포함)가 유지된다. 페이로드는 라벨까지 담은 배열이라 화면이 라벨 표를 따로 갖지 않는다(변환 로직은 하나).
6. **머리말·꼬리말은 기본 제외 + 보고** — HWPX 의 기존 동작에 HWP 5.0 을 맞춘다(RAG 청킹 잡음 방지 결정 유지). 출력 옵션은 이번에 만들지 않는다.
7. **셀 안 그림은 칸 안 이미지 링크, 번호 소비** — GFM 칸 안 `![…](…)` 는 일반 렌더러가 표시한다. 번호를 소비하지 않으면 같은 이미지 이름 체계를 둘로 나눠야 한다.
8. **수식은 python-hwpx `eqedit.py`·`tokens.py` 벤더링(`src/hwp2md/equation/`)** — 표준 라이브러리만 쓰고 깊이·길이 상한이 있다. 벤더링 파일 상단 SPDX·저작권 유지, 루트 `NOTICE` 에 출처·커밋·변경 사실. 가져올 수 없으면 `to_latex` 가 항상 `None` → 코드 스팬 출력(손실 없음).
9. **AES 는 순수 파이썬 복호 전용 구현(`hwp5/aes.py`)** — 배포용 문서만 쓰고, 기본 설치·Pyodide 에 의존성을 늘리지 않는다. 속도 상한: 실제 배포용 샘플 각 30초 안.
10. **OLE·차트는 공용 모듈(`ole.py`)** — CFB 열기(olefile), HWPX 길이 접두 벗기기, OOXML `c:chartSpace` 캐시값 → 블록. 두 포맷과 HWPML 이 같은 함수를 쓴다. 구형 `Contents` 는 파싱하지 않는다.
11. **HWPML 은 세 번째 리더(`hwpml/`)** — 요소가 HWPX 와 거의 1:1 이지만 이름·속성 표기가 달라 HWPX 코드를 공유하지 않고, 칸 배치(`_place_cells`)·이미지 이름(`ImageNamer`) 같은 포맷 무관 부분만 재사용한다. DTD 는 리터럴 내부 엔티티만 문자열 치환으로 풀고 파서 보안 옵션은 그대로 둔다.
12. **보호 문서는 `UnsupportedHwpError` 하위 예외 2개** — CLI 종료 코드 3 과 기존 `except UnsupportedHwpError` 경로가 그대로 동작한다. 오류 코드만 세분한다.
13. **실제 샘플 테스트는 구조 탐색으로 고른다** — `tests/samples.py` 가 파일 앞 바이트·OLE 레코드·zip XML 을 세어 요소별 샘플을 찾는다. 파일 이름을 테스트에 쓰지 않는다(익명화). 기존 테스트의 샘플 집합은 기존 테스트 파일에 이미 있는 이름 5개로 고정한다.

## Risks / Trade-offs

- [HWP 5.0 글상자 `LIST_HEADER` 레벨 관계·OLE BinData ID 오프셋(12 vs 10)·목록 ID 기준(0/1)이 추정값] → 합성 문서로 구현 후 구조 탐색으로 찾은 실제 샘플에서 확인. 다르면 단계 안에서 고치고 결정 기록.
- [제어문자 수와 `CTRL_HEADER` 수가 어긋난 손상 문서] → 대응이 깨지면 그 단락은 위치 없이 기존 방식(텍스트 + 뒤에 블록)으로 처리하고 실패하지 않는다.
- [실제 OLE 샘플이 구형 차트] → `chart_legacy` 로 보고. 문서에 한계로 적는다.
- [순수 파이썬 AES 가 느림(브라우저 모드는 더 느림)] → 30초 상한을 E2E 로 측정. 넘으면 `cryptography` 선택 의존성 대안을 결정 기록에 남긴다.
- [기존 실제 샘플의 단락·표 수가 캡션·글상자·차트로 늘어남] → 기준선(S1)과 비교해 늘어난 수를 구조 탐색 개수로 설명할 수 있을 때만 기대값을 바꾼다.
- [벤더링 대상 저장소 접근 불가] → 코드 스팬 출력으로 내려가고 해당 tasks 항목을 PARTIAL 로 기록.
- [배포용 문서 복호화가 작성자 의도(복사 제한)와 다를 수 있음] → README 에 명시. 법률 판단은 하지 않는다.
