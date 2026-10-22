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
```
