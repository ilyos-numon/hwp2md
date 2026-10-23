# PLAN — T-20261023-extract-dropped 버려지던 HWP 요소 추출과 추출 한계 명시

> 작성: planner opus · 2026-10-23 17:30 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> BASE: `main` HEAD `e18cd70` 기준 작업 트리 · 단위 `366 collected / 360 passed / 6 failed`(오늘 추가된 실제 샘플 때문, §1-D) · Python 3.12 · olefile·lxml
> 근거 자료: `.ai/tasks/T-20261023-extract-dropped/research.md`(조사), `inventory.md`(실제 샘플 구조 개수), `inventory.py`(구조 탐색 코드). 실제 샘플 파일 이름은 이 플랜·OpenSpec·테스트 코드에 쓰지 않는다. 샘플은 inventory.md 의 행 이름(예: "§4 표 칸 안 그림 행")으로만 가리키고, 테스트는 구조 탐색으로 고른다.

## 0. 한 줄 목표
사용자는 HWP 5.0·HWPX·HWPML·배포용 문서를 변환해 지금은 사라지던 표 칸 안 그림·글상자·캡션·하이퍼링크·각주·수식·번호 목록·차트 데이터를 Markdown 으로 받을 수 있고, 끝내 꺼내지 못한 요소는 CLI·API·웹 화면·`design/v3` 화면에서 종류별 개수와 이유 문서(`docs/extraction-limits.md`) 링크로 확인할 수 있다. DRM·비밀번호 문서는 "HWP 아님"이 아니라 정확한 이유로 거절된다.

### 0.1 OpenSpec 연동
- change: `openspec/changes/extract-dropped/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate extract-dropped` (planner 확인: `Change 'extract-dropped' is valid`, `--strict` 도 통과)
- capability: `element-extraction`(신규), `hwpml-input`(신규), `document-protection`(신규), `image-extraction`(REMOVED 1·ADDED 1·MODIFIED 1), `memory-conversion`(MODIFIED 2), `web-preview`(ADDED 3)
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행 (27행).

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | 단위·E2E·실제 샘플별 CLI 기준선 기록 | S1 |
| 1.2 | `tests/samples.py` + 기존 테스트 샘플 집합을 기존 5개로 고정 | S2 |
| 2.1 | 블록 모델·건너뜀·번호 계산·렌더 계약 + 공용 합성 항목 | S3 |
| 2.2 | `convert`·`memory`·리더 시그니처에 `skipped` 연결, 한컴 문구 docstring | S4 |
| 3.1 | DRM·비밀번호 문서 전용 예외·판별·오류 코드 | S5 |
| 4.1 | 수식 변환기 벤더링 `equation/` + NOTICE | S6 |
| 4.2 | `ole.py` OLE·OOXML 차트 모듈 | S7 |
| 4.3 | `hwp5/aes.py`·`hwp5/distdoc.py` 배포용 복호 모듈 | S8 |
| 5.1 | HWP 5.0 단락 안 요소(링크·각주·수식·필드·머리말 제외) | S9 |
| 6.1 | HWPX 단락 안 요소 | S10 |
| 7.1 | HWPML 판별·인코딩·엔티티·본문·표·그림 | S11 |
| 5.2 | HWP 5.0 개체(칸 그림·캡션·글상자·묶음·OLE) | S12 |
| 6.2 | HWPX 개체 | S13 |
| 7.2 | HWPML 요소(링크·각주·수식·머리말·캡션·글상자·목록·차트) | S14 |
| 5.3 | HWP 5.0 목록 | S15 |
| 6.3 | HWPX 목록 | S16 |
| 5.4 | HWP 5.0 배포용 문서 읽기 | S17 |
| 8.1 | 칸 그림 기대값 갱신 + 세 포맷 동일성 | S18 |
| 9.1 | `cli.py` 오류 문구·건너뜀 요약 줄 | S19 |
| 10.1 | 웹 UI(`web/static`) 오류 문구·`#skipped`·한컴 문구·런타임 zip 확인 | S20 |
| 10.2 | `design/v3` 한계 절·변환 화면 경고·데모 페이로드 재생성 | S21 |
| 11.1 | `docs/extraction-limits.md` 신규 + `feature-reference.md` 갱신 | S22 |
| 11.2 | README·decisions·system-overview·LICENSE·NOTICE | S23 |
| 12.1 | E2E 작성: 실제 샘플 요소별·합성 CLI | S24 |
| 12.2 | E2E 작성: 화면(서버·브라우저·design/v3) | S25 |
| 12.3 | E2E 전체 실행·스크린샷 | S26 |
| 13.1 | 리뷰·RESULT·STATE | S27 |

## 1. 범위

### A. 요소별 결정 (근거: research.md §1·§4, inventory.md §1·§3·§4)

| 요소 | 결정 | 근거 | 단계 |
|---|---|---|---|
| 표 칸 안 그림 | 채택: 칸 안 `![그림 N](…)`, 번호 소비 | 샘플 14개(8파일). 레코드 구조가 본문 그림과 같다 | S12·S13·S14 |
| 머리말·꼬리말 안 그림 | 채택(제외로 일관화) | HWP 5.0 이 본문에 내보내던 것은 기존 스펙 위반(feature-reference §12.2②) | S9·S10·S14 |
| 글상자·도형·묶음 안 글/그림 | 채택 | 샘플 3개(2파일) + HWPX 도형 샘플. hwplib·hwp-rs 구조 일치 | S12·S13·S14 |
| 표·그림 캡션 | 채택(개체 뒤 단락) + 캡션 `LIST_HEADER` 오인 버그 수정 | research §2 공통 메모 | S12·S13·S14 |
| 차트(OOXML 캐시값) | 채택(제목 단락 + 표) | 샘플 1파일(OLE). 형식(OOXML/구형)은 구현 중 확인 | S7·S12·S13·S14 |
| 구형 차트(VtChart `Contents`) | 불가(이번): `chart_legacy` 보고 | 객체 직렬화 수십 종, 구현 비용 큼 | S7 |
| 그 밖의 OLE | 부분: `Ole10Native` 원본 이미지만, 나머지 `ole` 보고 | MS-OLEDS 공개 | S7 |
| 수식 | 채택: LaTeX `$…$`, 실패 시 원문 코드 스팬 | 샘플 1파일 3개. python-hwpx(Apache-2.0) 변환기 | S6·S9·S10·S14 |
| 하이퍼링크 | 채택: `[글자](주소)`, http/https/mailto 만 | 샘플 2파일 | S9·S10·S14 |
| 각주·미주 | 채택: `[^n]`/`[^en]` + 문서 끝 정의 | 각주 샘플 3개, 미주는 합성만 | S9·S10·S14 |
| 머리말·꼬리말 글 | 채택(본문 제외 + `header_footer` 보고) | 19개. HWPX 기존 동작과 통일 | S9·S10·S14 |
| 번호·글머리표 목록 | 채택(번호는 근사) | 26개 | S15·S16·S14 |
| 누름틀 등 필드 표시 글자 | 채택(보존 확인) | 표시 글자가 이미 본문에 있음 | S9·S10 |
| 쪽 번호·자동 번호 | 불가·불필요 | 레이아웃 계산 필요 | S22 문서화 |
| 책갈피 | 보류(출력 안 함, 보고 안 함) | 본문 내용 없음, GFM 앵커 표준 없음 | — |
| 메모·숨은 설명 | 보류: 기본 제외 + `memo`·`hidden_comment` 보고 | 작성자 정보 포함 가능(개인정보 원칙) | S9·S10·S14 |
| 글맵시·양식 개체 | 보류: `textart`·`form_control` 보고 | 샘플 없음 | S12·S13·S14 |
| BMP 이미지 | 유지(원본 그대로) | 브라우저가 표시함 | — |
| WMF/EMF 변환 | 불가: 원본 그대로 저장 | Pillow 는 Windows 에서만 읽음, 순수 파이썬 구현 없음 | S22 문서화 |
| 배포용 문서 | 채택(공개 알고리즘 복호화) | 샘플 2파일, 한컴 공개 스펙 | S8·S17 |
| HWPML 2.x | 채택(세 번째 입력) | 샘플 2파일(지금 "HWP 아님"으로 거부) | S11·S14 |
| DRM 래핑·한컴 DRM | 거부 정확화(`drm`) | 샘플 2파일, 공개 형식 없음 | S5 |
| 비밀번호 문서 | 거부 정확화(`encrypted`) | 알고리즘 비공개, 비밀번호 필요 | S5 |
| 굵게·기울임 등 서식 | 불가(범위 밖) | README "하지 않는 것" | — |
| 단락 중간 그림 위치 통일 | 보류(§7 Q3) | 기존 출력·단락 수가 넓게 바뀜 | S22 문서화 |
| `PrvText` 부분 추출 | 보류 | 작성자가 잠근 문서 | — |
| HWP 3.x | 불가(유지) | 형식 다름 | — |

### B. 포함 (IN)
- 블록 모델·렌더·건너뜀·번호 계산: `src/hwp2md/blocks.py`, 신규 `skips.py`·`numbering.py`, `render.py` (§4-A~D)
- 결과·페이로드: `convert.py`, `memory.py`, `__init__.py` (§4-E)
- 보호 문서: `errors.py`, `detect.py`, `hwp5/reader.py`, `hwpx/reader.py`, `memory.py` (§4-F)
- 공용 모듈: 신규 `src/hwp2md/equation/`(벤더링), `src/hwp2md/ole.py`, `src/hwp2md/hwp5/aes.py`, `src/hwp2md/hwp5/distdoc.py` (§4-G~I)
- 리더: `src/hwp2md/hwp5/{records,body,docinfo,reader}.py`, `src/hwp2md/hwpx/{body,header,reader,bindata}.py`, 신규 `src/hwp2md/hwpml/{__init__,reader,body}.py` (§4-J)
- CLI: `src/hwp2md/cli.py` (S19 단독, §4-K)
- 화면: `src/hwp2md/web/static/{app.js,index.html,style.css}`, `design/v3/{index.html,app.html,README.md,js/app.js,js/demo-engine.js,js/demo-payload.js,css/app.css}` (§4-L)
- 문서: 신규 `docs/extraction-limits.md`·`LICENSE`, `docs/feature-reference.md`, `docs/decisions.md`, `docs/system-overview.md`, `README.md`, 신규 `NOTICE`
- 테스트: 신규 `tests/samples.py`·`tests/synth_items.py`·`tests/synth_ole.py`·`tests/synth_distdoc.py`·`tests/synth_hwpml.py`, `tests/synth_hwp5.py`·`tests/synth_hwpx.py` 확장, 단위·E2E 신규 파일(각 단계에 명시)

### C. 제외 (OUT) — 절대 건드리지 않는다
- 비밀번호 문서 복호화와 비밀번호 입력 기능, DRM 해제·우회 시도
- 구형 VtChart 차트 데이터 파싱, OLE 미리보기(`OlePres000`) 추출, WMF/EMF → PNG 변환(외부 도구 연동 포함)
- 필드 값 재계산(쪽 번호·날짜), 책갈피 앵커 출력, 메모·숨은 설명 내용 출력
- 굵게·기울임·밑줄 등 서식(`--emphasis`), `--table html`, `--split`·`--meta`, 폴더 일괄 변환
- CLI 새 옵션(머리말 출력 옵션 등). 오류 메시지 `not an HWP 5.0 file:` 문구 변경
- 단락 중간 그림의 HWP 5.0/HWPX 배치 통일(§7 Q3 기본값)
- 웹 미리보기 수식 렌더러(KaTeX 등), marked 버전 변경
- `design/v3` 를 실제 백엔드에 연결하는 작업(`design/v3/README.md` "백엔드에 연결할 때" 1~5)
- 의존성 추가(`cryptography`, `python-hwpx` 패키지 설치 등)
- pyhwp(AGPL-3.0) 코드·구조 복사

### D. 의도적으로 바뀌는 기존 테스트 (이 목록 밖의 기존 테스트는 수정 금지)
| 파일::대상 | 바뀌는 이유 | 단계 |
|---|---|---|
| `tests/unit/test_memory.py` 의 `SAMPLES` 정의, `tests/unit/test_source_bytes.py` 의 `HWP5_SAMPLES`·`HWPX_SAMPLES` 정의, `tests/unit/test_web_app.py`·`tests/e2e/conftest.py`·`tests/e2e/test_cli_hwpx.py`·`tests/e2e/test_cli_image.py`·`tests/e2e/test_cli_heading.py` 의 실제 샘플 glob 정의 | 오늘 `tests/fixtures/hwpx/` 에 샘플 50여 개(DRM 파일 포함)가 추가되어 `== 5`·`== 3` 단언과 DRM 파일 매개변수 케이스가 이미 실패(기준선 6 failed). 샘플 집합 정의만 `tests/samples.py` 의 기존 5개 고정 목록으로 바꾼다. 단언은 그대로 | S2 |
| `tests/unit/test_memory.py::test_to_payload_shape` | 페이로드 키 `skipped` 추가 | S4 |
| `tests/unit/test_memory.py::test_constants`, `::test_convert_to_response_errors` 의 `unsupported` 케이스 | 오류 코드 `drm`·`encrypted` 추가, 속성 `0x3` 문서가 `encrypted` 로 바뀜 (`unsupported` 케이스는 `UnsupportedHwpError` 를 내도록 monkeypatch 한 입력으로 유지) | S5 |
| `tests/unit/test_hwpx_body.py::test_ctrl_header_and_footnote_ignored` | 각주를 이제 추출 → 이름 `test_ctrl_header_skipped_footnote_extracted`, 기대값 각주 참조·정의 | S10 |
| `tests/synth_hwp5.py` 의 `EXPECTED_BLOCKS/MARKDOWN/COUNTS/IMAGE_FILES_IMAGE_IN_CELL` (→ `test_hwp5_bindata[in_cell]`, `test_hwpx_bindata[in_cell]`, `test_cross_format::test_image_fixtures_same_result_both_formats[in_cell]`, `test_synth_*` 중 이 상수를 쓰는 것) | 셀 그림 추출·번호 소비 | S18 |
| `tests/e2e/test_cli_image.py::test_image_in_table_cell_not_extracted_both_formats` | 셀 그림 추출 → 이름 `test_image_in_table_cell_extracted_both_formats`, 파일 2개 | S24 |
| `tests/e2e/test_cli_image.py::test_real_fixture_images` 의 `len(lines) == 3` | 건너뜀 줄이 있으면 4 | S24 |
| `tests/e2e/test_cli_heading.py::REAL_EXPECTED`, `test_cli_hwpx.py::REAL_HWPX_EXPECTED`, `test_cli_image.py::REAL_IMAGE_EXPECTED`, `test_web_ui.py` 의 `#preview table` 개수 | 기존 5개 샘플의 수가 캡션·글상자·차트로 바뀐 경우에만. 바뀐 값마다 S1 기준선 값과 구조 탐색 개수를 주석으로 남긴다 | S24·S25 |

### 건드리면 안 되는 파일/디렉토리
- orchestrator 전용: `pyproject.toml`, `uv.lock`, `.gitignore`, `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.claude/**`. `src/hwp2md/cli.py` 는 S19 만 쓴다
- `tests/fixtures/**`(실제 샘플, 읽기만. `tests/fixtures/README.md` 는 S2 만), `src/hwp2md/web/static/vendor/**`, `design/stitch/**`, `design/v3/css/base.css`·`landing.css`, `design/v3/js/{effects,landing,theme}.js`, `openspec/specs/**`(archive 가 반영), `openspec/changes/archive/**`, `.impeccable/**`
- 워크스페이스 루트 `doc/my_info/**` (읽기 전용 원본)

## 2. 성공 기준 (전부 만족해야 DONE)
모든 명령은 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다.

| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| C1 | 단위 테스트 회귀 없음 | `uv run pytest tests/unit -q 2>&1 \| tail -1` | `failed`·`error` 0, passed ≥ 400 |
| C2 | 린트·타입 | `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | 종료 코드 0 |
| C3 | OpenSpec | `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate extract-dropped` | `Change 'extract-dropped' is valid` |
| C4 | E2E 전체 | `uv run pytest tests/e2e -q 2>&1 \| tail -1` | failed 0 (CDN 이 막히면 브라우저 모드 케이스만 skip 허용, 로그에 사유) |
| C5 | 실제 샘플 요소별 E2E (inventory.md §4 행마다 1개 이상) | `uv run pytest tests/e2e/test_extract_real.py -q -rs 2>&1 \| tail -3` | 18개 테스트 함수 전부 PASSED, SKIPPED 0 (이 머신 기준) |
| C6 | 표 칸 안 그림 (inventory §4 "표 칸 안 그림" 행) | C5 의 `test_cell_image` | 구조 탐색 개수가 가장 큰 샘플: 칸 안 그림 링크 수 ≥ 탐색 개수(6), 이미지 파일 ≥ 6 |
| C7 | 수식·각주·링크 (inventory §4 해당 행) | C5 의 `test_equation`, `test_footnote`, `test_hyperlink` | 수식 렌더(`$…$`/`$$…$$`/코드 스팬) 수 = 탐색 `eqed` 수(3), `[^n]:` 정의 수 = 탐색 `fn  ` 수(3), http/https/mailto 링크 수 ≥ 탐색 웹 링크 수 |
| C8 | 머리말·꼬리말 (inventory §4 해당 행) | C5 의 `test_header_footer` | CLI 마지막 줄 `  건너뜀: 머리말·꼬리말 N개` 의 N = 탐색 `head`+`foot` 수, 머리말 단락 글자가 본문 Markdown 에 없음 |
| C9 | 배포용 문서 (inventory §4 "배포용 문서" 행 2개) | C5 의 `test_distribution` | 2개 모두 종료 코드 0, 단락 ≥ 1, 파일당 변환 30초 이하 |
| C10 | HWPML (inventory §3 HWPML 2개) | C5 의 `test_hwpml` | 2개 모두 종료 코드 0, 표 ≥ 2, 이미지 수 ≥ inventory §3 그림 수(3, 7), 건너뜀 `머리말·꼬리말 2개` |
| C11 | DRM·텍스트·HWP3 거부 (inventory §3) | C5 의 `test_drm`, `test_not_hwp` | DRM 2개: 종료 코드 3, 표준 오류에 `DRM protected`, API `drm`/415. 텍스트 1개·HWP3 1개: 종료 코드 3, `not an HWP 5.0 file:` |
| C12 | 전체 실제 샘플 무오류 | C5 의 `test_all_samples_convert` | `tests/fixtures/**` 모든 파일이 종료 코드 0, 또는 분류 `drm`/`text`/HWP3 이면 3. 종료 코드 1 은 0개 |
| C13 | API·화면 건너뜀 표시 | `uv run pytest tests/e2e/test_web_extract.py -q` + 스크린샷 `.ai/tasks/T-20261023-extract-dropped/screenshots/s26-web-skipped.png`, `s26-web-drm.png` | pass. 스크린샷에 `#skipped` "변환하지 못한 요소: 머리말·꼬리말 1개", DRM 오류 문구가 보인다 (reviewer 가 직접 본다) |
| C14 | design/v3 반영 | `uv run pytest tests/e2e/test_design_v3.py -q` + 스크린샷 `s26-design-app-skipped.png`, `s26-design-limits.png` | pass. 변환 화면에 건너뜀 경고와 `docs/extraction-limits.md` 링크, `#limits` 에 불가·부분 항목과 문서 링크가 보인다 |
| C15 | 한컴 공개 문서 문구 | `grep -lF '본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.' README.md src/hwp2md/__init__.py src/hwp2md/web/static/index.html design/v3/index.html design/v3/app.html \| wc -l` | `5` |
| C16 | 추출 한계 문서 | `uv run python -c "from hwp2md.skips import SKIP_LABELS; t=open('docs/extraction-limits.md',encoding='utf-8').read(); print(sum(l in t for l in SKIP_LABELS.values()))"` | `9` |
| C17 | 런타임 zip 에 새 모듈 | `uv run pytest tests/unit/test_web_runtime_zip.py -q` | pass (`hwp2md/hwpml/reader.py`, `hwp2md/equation/__init__.py`, `hwp2md/hwp5/aes.py`, `hwp2md/ole.py`, `hwp2md/skips.py` 포함) |
| C18 | 익명화 | `/Users/illi/illy-projects/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` | OK |
| C19 | 실제 샘플 이름이 추적 파일에 새로 들어가지 않음 | `git diff --name-only d6f98cc -- tests src docs design \| xargs grep -lE '규정\|지침\|정관\|세칙' 2>/dev/null \| wc -l` | `0` |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 단계 재시도 3회 초과 → BLOCKED
- 같은 오류로 수정 2회 실패 → BLOCKED
- 단계 하나 도구 호출 40회 목표, 60회 초과 → PARTIAL 기록 후 orchestrator 에 반환
- 단계 하나 30분 초과(S26 은 60분) → PARTIAL
- §4 계약을 바꿔야만 진행 가능 → BLOCKED (planner 재호출)
- §1-D 목록 밖 기존 테스트를 고쳐야만 통과 → BLOCKED
- `pyproject.toml` 의존성 추가 또는 pyhwp 코드가 필요 → BLOCKED
- sanitize-check 실패 → 커밋하지 않고 1회 수정, 다시 실패하면 BLOCKED
- **PARTIAL 로 끝내도 다음 단계로 가는 경우(대체 동작이 정의됨)**:
  - S6: python-hwpx 저장소를 받을 수 없음 → `to_latex` 가 항상 `None`(코드 스팬 출력), NOTICE 에는 벤더링 없음 기록, S22 문서에 한계로 기록
  - S12: 실제 OLE 샘플이 구형 차트 → `chart_legacy` 보고가 정답
  - S17: 합성 배포용 문서는 통과하지만 실제 샘플 2개 복호화가 수정 2회 뒤에도 깨짐 → 실제 배포용 문서는 `UnsupportedHwpError` 로 남기고 C9 를 PARTIAL 로 RESULT 에 기록

## 4. 인터페이스 계약 (병렬 작업 전 확정)

### A. 블록 모델 — `src/hwp2md/blocks.py` (S3). 기존 필드 순서·기본값 유지, 새 필드는 뒤에 기본값과 함께
```python
NoteKind = Literal["footnote", "endnote"]

@dataclass(frozen=True)
class Link:
    text: str
    url: str            # 원문 주소 그대로(언이스케이프만 리더가 함). 허용 판정은 render.safe_link_url

@dataclass(frozen=True)
class NoteRef:
    kind: NoteKind
    number: int         # 종류별 문서 읽기 순서 1부터 (섹션을 넘어 이어짐)

@dataclass(frozen=True)
class Math:
    script: str         # 한글 수식 스크립트 원문 (strip)
    latex: str | None   # equation.to_latex(script) 결과

Inline = str | Link | NoteRef | Math | Image   # Image 는 기존 클래스

@dataclass(frozen=True)
class ListInfo:
    kind: Literal["bullet", "number"]
    depth: int          # 0부터 (원문 수준 1 → 0), 0~6
    label: str          # number: numbering.apply_template 결과("1.", "가.", "(1)"), bullet: ""

@dataclass(frozen=True)
class Paragraph:
    text: str
    level: int = 0
    inlines: tuple[Inline, ...] = ()      # () 면 text 로 렌더 (기존 동작)
    list_info: ListInfo | None = None

@dataclass(frozen=True)
class Table:
    rows: list[list[str]]                  # 칸의 plain_text, 칸 안 단락은 "\n"
    cells: tuple[tuple[tuple[Inline, ...], ...], ...] = ()   # rows 와 같은 모양. () 면 rows 로 렌더

@dataclass(frozen=True)
class Note:
    kind: NoteKind
    number: int
    paragraphs: tuple[Paragraph, ...]

Block = Paragraph | Table | Image | Note

def plain_text(inlines: Sequence[Inline]) -> str
    # str 그대로 + Link.text + Math.script, NoteRef·Image 는 "" 
def make_paragraph(inlines: Sequence[Inline], level: int = 0,
                   list_info: ListInfo | None = None) -> Paragraph | None
    # 인접 str 병합, 맨 앞/뒤 str 의 공백 strip. str 이 아닌 인라인이 없으면 inlines=().
    # text = plain_text(정규화 inlines).strip(). text=="" 이고 str 이 아닌 인라인도 없으면 None.
def make_table(grid: Sequence[Sequence[Sequence[Inline]]]) -> Table
    # 각 칸: 인라인 사이 단락 경계는 "\n" str 로 리더가 넣는다. rows[r][c] = plain_text(칸).strip().
    # 모든 칸이 str 만이면 cells=() — 기존 Table(rows) 와 같은 값.
def iter_images(blocks: Sequence[Block]) -> Iterator[Image]
    # 렌더 순서와 같다: 블록 순서 → Paragraph.inlines 순서 → Table.cells 행 우선·칸 안 순서 → Note.paragraphs 순서
```
- 리더는 새 블록을 `make_paragraph`·`make_table` 로만 만든다. 그래서 새 요소가 없는 문서는 블록 값이 지금과 같다.
- `Note` 블록은 리더가 문서 끝(모든 섹션 뒤)에 각주 번호순, 이어서 미주 번호순으로 둔다. 각주 안 각주는 만들지 않는다(안쪽 각주 컨트롤은 건너뛰고 보고하지 않는다).
- 이미지 블록(`Image`)은 본문에서는 지금처럼 단락 블록 뒤(HWP 5.0)·분할 위치(HWPX)에 둔다. `Image` 인라인은 표 칸·각주 단락 안에서만 쓴다.

### B. 건너뜀 — `src/hwp2md/skips.py` (S3)
```python
SkipKind = Literal["header_footer", "memo", "hidden_comment", "chart_legacy", "ole",
                   "textart", "form_control", "image_link", "image_missing"]
SKIP_LABELS: dict[SkipKind, str] = {   # 이 순서가 보고 순서
    "header_footer": "머리말·꼬리말", "memo": "메모", "hidden_comment": "숨은 설명",
    "chart_legacy": "데이터를 꺼낼 수 없는 차트", "ole": "OLE 개체", "textart": "글맵시",
    "form_control": "양식 개체", "image_link": "외부 연결 그림", "image_missing": "본체 없는 그림",
}
class SkipCounter:
    def add(self, kind: SkipKind, n: int = 1) -> None
    def items(self) -> tuple[tuple[SkipKind, int], ...]   # count > 0 만, SKIP_LABELS 순서
```
세는 단위: 머리말·꼬리말·메모·숨은 설명·차트·OLE·글맵시·양식 개체는 컨트롤(요소) 1개당 1, 그림은 참조 1개당 1. 머리말 안의 그림·표는 따로 세지 않는다.

### C. 번호 계산 — `src/hwp2md/numbering.py` (S3)
```python
NumFormat = Literal["DIGIT", "CIRCLED_DIGIT", "ROMAN_CAPITAL", "ROMAN_SMALL", "LATIN_CAPITAL",
                    "LATIN_SMALL", "HANGUL_SYLLABLE", "CIRCLED_HANGUL_SYLLABLE", "HANGUL_JAMO",
                    "HANJA_DIGIT"]
def format_number(n: int, fmt: NumFormat) -> str      # 1→"1","①","I","i","A","a","가","㉮","ㄱ","一". 범위 밖은 DIGIT
def apply_template(template: str, numbers: Sequence[int], formats: Sequence[NumFormat]) -> str
    # "^k"(k=1..7)를 수준 k 번호로, "^n"/"^N" 을 현재(마지막) 수준 번호로 바꾼다. 예: ("^1.", [3], ["DIGIT"]) → "3."
class NumberingCounter:
    def next(self, numbering_id: int, depth: int, start: int = 1) -> list[int]
    # 같은 id 의 depth 번호 +1, 더 깊은 수준은 리셋, 처음이면 start. 반환: 수준 0..depth 번호 목록
```
리더는 포맷별 번호 모양 값을 `NumFormat` 으로 바꿔 넘긴다. 모르는 값은 `"DIGIT"`.

### D. 렌더 규칙 — `src/hwp2md/render.py` (S3)
```python
def safe_link_url(url: str) -> str | None
    # strip 후 스킴(소문자)이 http·https·mailto 면 퍼센트 인코딩(공백 %20, ( %28, ) %29, < %3C, > %3E)한 값, 아니면 None
def render_blocks(blocks: Sequence[Block], *, image_dir: str = "") -> str   # 시그니처 불변
```
- `inlines == ()`·`list_info is None` 인 Paragraph, `cells == ()` 인 Table 은 지금과 같은 문자열.
- 인라인: `str` 그대로(이스케이프 없음, 기존 원칙) · `Link` → `safe_link_url` 이 값이면 `[글자](값)`(글자의 `[`·`]` → `\[`·`\]`), 아니면 글자만 · `NoteRef` → `[^n]`(각주)·`[^en]`(미주) · `Math` → latex 가 있으면 `$latex$`, 단락 인라인이 (공백뿐인 str 을 빼면) Math 하나뿐이면 `$$latex$$`; latex 가 None 이면 스크립트 안 가장 긴 백틱 연속보다 1개 많은 백틱으로 감싼 코드 스팬(내용이 백틱으로 시작·끝나면 양쪽 공백 1칸) · `Image` → `![그림 N](경로)` (N 은 문서 전체 이미지 카운터, 블록 이미지와 공유).
- 인라인 렌더 결과는 앞뒤 strip. 제목은 `\n` → 공백 후 `#` × min(level, 6) + 공백.
- 목록: 글머리표 `- 글자`, 숫자 머리(`^\d{1,9}[.)]$`) `머리 글자`, 그 밖 머리 `머리 글자`(목록 문법 아님, 들여쓰기 없음). 들여쓰기 = 공백 4 × 유효 수준, 유효 수준 = 직전 렌더 블록이 목록 문법 항목(글머리표·숫자)이 아니면 0, 맞으면 min(depth, 직전 유효 수준 + 1). 목록 문법 항목끼리는 `"\n"` 하나로 잇고, 그 밖은 지금처럼 `"\n\n"`.
- 표 칸: `cells` 가 있으면 칸 인라인을 렌더해 `\n` → `<br>`, `str`·링크 글자의 `|` → `\|`, strip.
- Note: `[^n]: ` + 첫 단락 렌더, 둘째 단락부터 `"\n\n    "` + 단락(단락 안 줄바꿈 뒤에도 공백 4칸). 미주는 `[^en]: `.
- 개수(`_count_blocks`): 단락 = 텍스트가 있는 level 0 Paragraph(목록 포함, Note 안 단락 제외) · 제목 = level ≥ 1 · 표 = 최상위 Table · 이미지 = `len(list(iter_images(blocks)))`.

### E. 결과·페이로드 (S4)
```python
# convert.py
def read_blocks(path: Source, skips: SkipCounter | None = None) -> list[Block]   # 포맷 감지 후 리더에 skips 전달
@dataclass(frozen=True)
class ConvertResult:  # 기존 필드 뒤에 추가
    skipped: tuple[tuple[SkipKind, int], ...] = ()
# 각 리더: hwp5.reader / hwpx.reader / hwpml.reader
def read_blocks(path: Source, skips: SkipCounter | None = None) -> list[Block]
# memory.py
@dataclass(frozen=True)
class MemoryResult:   # 기존 필드 뒤에 추가
    skipped: tuple[tuple[SkipKind, int], ...] = ()
# to_payload 에 키 추가 (항상 존재):
#   "skipped": [{"kind": k, "label": SKIP_LABELS[k], "count": n} for k, n in result.skipped]
```
- `convert_bytes` 는 모듈 전역 이름 `read_blocks` 를 `read_blocks(data, skips=counter)` 로 부른다(기존 monkeypatch 테스트 유지).
- `_write_images`·`convert_bytes` 의 고유 이미지 목록은 `iter_images` 순서.
- `src/hwp2md/__init__.py`: 모듈 docstring 에 한컴 공개 문서 문구(§4-L 원문 그대로), `__all__` 에 `DrmProtectedError`, `EncryptedDocumentError`(S5 에서), `Note`, `Link`, `NoteRef`, `Math`, `ListInfo`, `SkipCounter` 추가.

### F. 보호 문서 (S5)
```python
# errors.py
class DrmProtectedError(UnsupportedHwpError): """DRM 래핑 파일 또는 HWP 5.0 DRM 비트 (종료 코드 3)"""
class EncryptedDocumentError(UnsupportedHwpError): """비밀번호 문서 (종료 코드 3)"""
# detect.py — 판정 순서: ① DRM 서명 ② OLE ③ zip ④ HWPML(S11) ⑤ NotHwpFileError
DocFormat = Literal["hwp5", "hwpx", "hwpml"]
# DRM 서명: head = 앞 64바이트; head[:2] == b"\x9b\x20" 또는 b"DRMONE" in head
#   → DrmProtectedError(f"DRM-protected document: {label}")
# hwp5/reader.py: properties bit1 → EncryptedDocumentError(f"encrypted document: {label}"),
#   bit4(0x10)·bit10(0x400) → DrmProtectedError(f"DRM-protected document: {label}")  (bit1 검사가 먼저)
# hwpx/reader.py: zip 에 "META-INF/manifest.xml" 이 있고(50MB 이하) 어떤 요소의 local-name 이
#   "encryption-data" 면 EncryptedDocumentError(f"encrypted document: {label}")
# memory.py
ErrorCode = Literal["empty", "too_large", "not_hwp", "unsupported", "drm", "encrypted", "convert_failed"]
STATUS_BY_CODE["drm"] = 415; STATUS_BY_CODE["encrypted"] = 415
# error_code: DrmProtectedError → "drm", EncryptedDocumentError → "encrypted" (UnsupportedHwpError 보다 먼저)
```

### G. 수식 — `src/hwp2md/equation/` (S6)
```python
# src/hwp2md/equation/__init__.py
def to_latex(script: str) -> str | None   # 예외를 내지 않는다. 빈 스크립트·변환 실패 → None. 결과는 strip
# src/hwp2md/equation/eqedit.py, tokens.py — python-hwpx(commit 7ca4582) src/hwpx/equation/ 벤더링.
#   상단 SPDX·저작권 유지, import 경로만 수정, 필요하면 `# mypy: ignore-errors`. 루트 NOTICE 에 출처·커밋·변경 사실.
```

### H. OLE·차트 — `src/hwp2md/ole.py` (S7)
```python
ImageFactory = Callable[[str, bytes], Image]      # (고유 키, 원본 바이트) → 이름 붙은 Image (리더의 ImageNamer 사용)
MAX_OLE_BYTES = 50 * 1024 * 1024
def unwrap_hwpx_ole(data: bytes) -> bytes          # 앞 UINT32 LE == len(data) - 4 이면 data[4:], 아니면 data
def chart_xml_to_blocks(xml: bytes) -> list[Block] # c:chartSpace 캐시값 → [Paragraph("차트: 제목" | "차트"), Table]. 계열 0·파싱 실패 → []
    # Table 첫 행 ["항목", 계열명...], 행마다 [범주, 값...]. 값은 c:v 문자열 그대로. 계열명 없으면 "계열 k"
@dataclass(frozen=True)
class OleOutcome:
    blocks: tuple[Block, ...]          # 차트 블록 또는 (Image,) 또는 ()
    skipped: SkipKind | None           # "chart_legacy" | "ole" | None
def ole_to_outcome(cfb: bytes, key: str, make_image: ImageFactory) -> OleOutcome
    # CFB 가 아니거나 열 수 없으면 OleOutcome((), "ole").
    # "OOXMLChartContents" 스트림 → chart_xml_to_blocks (빈 결과면 "chart_legacy")
    # 아니면 "\x01Ole10Native" = [UINT32 LE 길이][원본] 이 PNG/JPEG/GIF/BMP 면 (make_image(key, 원본),)
    # 아니면 "Contents" 스트림이 있으면 "chart_legacy", 그 밖 "ole"
```
XML 파싱은 `resolve_entities=False, no_network=True, huge_tree=False` 파서를 호출마다 새로 만든다.

### I. 배포용 문서 — `src/hwp2md/hwp5/aes.py`, `src/hwp2md/hwp5/distdoc.py` (S8)
```python
def aes128_ecb_decrypt(key: bytes, data: bytes) -> bytes   # len(key)!=16 또는 len(data)%16!=0 → ValueError. FIPS-197 역암호
HWPTAG_DISTRIBUTE_DOC_DATA = 0x1C
def distribution_key(record_payload: bytes) -> bytes        # 256B → 16B 키 (research §2.11 3~6단계)
def decrypt_view_text(stream: bytes) -> bytes
    # 첫 레코드 헤더(평문) 검사: tag 0x1C, size 256. 아니면 UnsupportedHwpError("distribution document: bad header")
    # 레코드 뒤 나머지 길이를 16의 배수로 내림해 AES 복호 → 반환(압축 해제는 호출자)
```
- 순수 파이썬, 표준 라이브러리만. pyhwp 코드를 보지 않고 research §2.11 과 한컴 공개 문서 절차로 작성.

### J. 리더 공통 규칙 (S9~S17)
- 확장 제어문자(HWP 5.0 코드 1,2,3,11,12,14,15,16,17,18,21,22,23)와 같은 단락의 `CTRL_HEADER`(level = 단락+1)를 등장 순서로 1:1 대응한다. 개수가 다르면 그 단락은 대응을 포기하고 지금처럼 텍스트 + 뒤 블록으로 처리한다(실패하지 않는다).
- `records.py` 신규(S9): `decode_para_runs(payload: bytes) -> list[str | CtrlMark]`, `@dataclass(frozen=True) class CtrlMark: code: int` (확장·필드끝(4) 위치 표시). `decode_para_text` 결과는 바뀌지 않는다.
- 컨트롤 ID 상수(역순 바이트, S9 가 `records.py` 에 추가): `head`, `foot`, `fn  `, `en  `, `%hlk`, `eqed`, `tcmt`, `%%me`. 태그: `HWPTAG_SHAPE_COMPONENT_OLE=0x54`, `HWPTAG_EQEDIT=0x58`, `HWPTAG_SHAPE_COMPONENT_TEXTART=0x5A`, `HWPTAG_MEMO_LIST=0x5D`, `HWPTAG_NUMBERING=0x17`, `HWPTAG_BULLET=0x18`, `HWPTAG_CTRL_DATA=0x57`.
- 하이퍼링크 command 해석: 꼬리 `;\d+;\d+;\d+;?$` 제거 → `|` 앞부분 → `\(.)` 언이스케이프. 종류가 문서 안 이동이거나 결과가 비면 `str` 로(링크 아님).
- 문서 단위 상태(각주 번호·건너뜀·번호 카운터)는 리더별 내부 컨텍스트 객체가 섹션을 넘어 유지한다(이름·형태는 리더 내부, 계약 아님).
- 표 칸 안 단락은 이미지 해석기를 받는다. 칸 안 표는 지금처럼 글자를 공백으로 이어 붙이고, 그 안의 그림은 부모 칸 인라인 끝에 붙인다.
- 머리말·꼬리말 컨트롤은 하위 트리를 통째로 건너뛰고 `header_footer` 1.
- HWPML 은 HWPX 요소와 1:1 로 대응시키고(대문자 이름·CamelCase 속성), `_place_cells` 동등 로직과 `ImageNamer` 를 재사용한다.

### K. CLI 문자열 (S19, `src/hwp2md/cli.py`)
- `DrmProtectedError` → stderr `hwp2md: error: unsupported HWP file (DRM protected): <INPUT>`, 종료 코드 3
- `EncryptedDocumentError` → `hwp2md: error: unsupported HWP file (password protected): <INPUT>`, 3
- 그 밖 `UnsupportedHwpError` → 기존 문구 그대로, 3. `NotHwpFileError` 문구 그대로
- 성공 시 기존 1~3행 뒤, `result.skipped` 가 있으면 `  건너뜀: ` + `" · ".join(f"{SKIP_LABELS[k]} {n}개")` 한 줄
- `INPUT` 도움말: `변환할 HWP·HWPX·HWPML 파일 경로`

### L. 화면·문서 문자열 (S20·S21·S22·S23)
- 한컴 공개 문서 문구(그대로): `본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.`
- 오류 문구: `drm` → `문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다. 보안 프로그램에서 해제한 뒤 다시 시도하세요` · `encrypted` → `암호가 설정된 문서라 변환할 수 없습니다. 한글에서 암호를 해제한 뒤 다시 시도하세요` · `unsupported` → `지원하지 않는 HWP 문서라 변환할 수 없습니다` · `not_hwp` → `HWP·HWPX·HWPML 파일이 아닙니다` 는 쓰지 않는다(기존 `HWP 5.0 또는 HWPX 파일이 아닙니다` 유지 — E2E 문구 단언 보존)
- 건너뜀 경고 DOM: `<div id="skipped" role="status" hidden>` 안에 `변환하지 못한 요소: ` + `skipped[].label` `n개` 를 ` · ` 로 이은 글자(`textContent`). `design/v3` 는 끝에 `<a href="../../docs/extraction-limits.md">왜 빠졌나요?</a>`, 서버 UI 는 링크 없이 ` (자세한 이유: docs/extraction-limits.md)` 글자
- 문서 경로: `docs/extraction-limits.md` — 표 열 `요소 | 상태(추출·부분·불가·제외) | 이유 | 대안·우회 | 건너뜀 종류`

### M. 테스트 공용 — `tests/samples.py` (S2, S24 확장), `tests/synth_items.py` (S3)
```python
# tests/samples.py (S2)
FIXTURES: Path                      # tests/fixtures
LEGACY_NAMES: tuple[str, ...]       # tests/e2e/test_cli_heading.py 의 REAL_EXPECTED 키 5개, 같은 순서
LEGACY_HWP5: list[Path]; LEGACY_HWPX: list[Path]; LEGACY_SAMPLES: list[Path]   # 있는 파일만, 기존 glob 순서와 같게 정렬
SampleClass = Literal["hwp5", "hwpx", "hwpml", "drm", "text", "unknown"]
def classify(path: Path) -> SampleClass   # 앞 1024바이트만 본다 (DRM 서명 → OLE → zip → <HWPML → 인쇄 가능 텍스트)
def all_samples() -> list[Path]           # tests/fixtures 아래 모든 파일, README.md·.gitkeep 제외, 정렬
# S24 추가
def probe(path: Path) -> dict[str, int]   # inventory.py 와 같은 방식의 요소별 개수 (키 목록은 S24 에 명시)
def samples_with(feature: str) -> list[tuple[Path, int]]   # probe 값 > 0, 개수 내림차순
def probe_texts(path: Path, feature: str) -> list[str]     # 글상자·누름틀·머리말 안 단락 글자 (레코드/XML 저수준 디코딩)

# tests/synth_items.py (S3) — 세 합성기가 공유하는 항목. synth_hwp5 를 import 하지 않는다
@dataclass(frozen=True) class SynthLink: text: str; url: str
@dataclass(frozen=True) class SynthNote: paragraphs: tuple[str, ...]; kind: Literal["footnote", "endnote"] = "footnote"
@dataclass(frozen=True) class SynthEquation: script: str
@dataclass(frozen=True) class SynthField: text: str            # 누름틀
Run = str | SynthLink | SynthNote | SynthEquation | SynthField
@dataclass(frozen=True) class SynthRich: runs: tuple[Run, ...] # 단락 하나
@dataclass(frozen=True) class SynthHeaderFooter: paragraphs: tuple[str, ...]; kind: Literal["header", "footer"] = "header"; with_image: bool = False
@dataclass(frozen=True) class SynthHidden: paragraphs: tuple[str, ...]          # 숨은 설명
@dataclass(frozen=True) class SynthTextBox: anchor_text: str; paragraphs: tuple[str, ...]; with_image: bool = False
@dataclass(frozen=True) class SynthCaptionedTable: cells: tuple[tuple[str, ...], ...]; caption: str
@dataclass(frozen=True) class SynthListPara: text: str; kind: Literal["bullet", "number"]; depth: int = 0; template: str = "^1."
@dataclass(frozen=True) class SynthChart: title: str; categories: tuple[str, ...]; series: tuple[tuple[str, tuple[str, ...]], ...]; legacy: bool = False
ExtItem = SynthRich | SynthHeaderFooter | SynthHidden | SynthTextBox | SynthCaptionedTable | SynthListPara | SynthChart
EXT_FIXTURES: dict[str, tuple[list[object], str, tuple[tuple[str, int], ...]]]
    # id → (items, 기대 Markdown(stem "doc"), 기대 skipped). ids:
    # link, link_unsafe, footnote, note_mixed, equation_display, equation_inline, field, header, header_image,
    # hidden_comment, textbox, caption, bullets, numbers, chart, chart_legacy
EXT_IDS_BY_STAGE = {"inline": [...S9·S10 대상 10개], "objects": [...S12·S13 대상 4개], "lists": ["bullets", "numbers"]}
```
기대 Markdown 은 OpenSpec `element-extraction`·`image-extraction` 시나리오 값과 같다(예: `footnote` → `가[^1]나\n\n[^1]: 주석\n`). 그림이 필요한 항목은 합성기가 `synth_hwp5.PNG_1X1` 을 쓴다.

## 5. 단계 (Stage)

**공통 규칙 (모든 단계)**
- 모든 Bash 는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. Read/Glob 은 절대경로.
- 표준 검증 `STD_VERIFY` = `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src && uv run pytest tests/unit -q`
- 칸 그림 허용 제외 `CELL_DESELECT` = `--deselect "tests/unit/test_hwp5_bindata.py::test_read_blocks_image_fixtures[in_cell]" --deselect "tests/unit/test_hwpx_bindata.py::test_read_blocks_image_fixtures[in_cell]" --deselect "tests/unit/test_cross_format.py::test_image_fixtures_same_result_both_formats[in_cell]"` — S12·S13·S14·S15·S16·S17 의 검증에서만 `STD_VERIFY` 의 마지막 `uv run pytest tests/unit -q` 뒤에 붙인다(표기 `STD_VERIFY CELL_DESELECT`). S18 부터는 붙이지 않는다.
- 단계마다 새 단위 테스트를 쓴다(파일 이름은 각 단계에 명시). 실제 샘플을 쓰는 단위 테스트는 만들지 않는다(E2E 에서만).
- 실제 샘플 확인이 필요한 단계(S9·S12·S15·S17)는 임시 스크립트를 `/private/tmp/claude-501/-Users-illi-illy-projects/4b7ad5a2-bb97-4539-bbfd-1f4c9f6f768a/scratchpad/` 아래에 두고, 결과는 `.ai/tasks/T-20261023-extract-dropped/logs/s<n>-*.log` 에 개수만 남긴다(문서 글자를 로그·보고에 옮기지 않는다).
- 단계 완료 = 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261023-extract-dropped][s<n>] …` (커밋은 orchestrator).

**S0 (orchestrator, 서브에이전트 아님)**: 브랜치 `ai/T-20261023-extract-dropped` 생성. 추적되지 않은 `design/`, `docs/feature-reference.md`, `.ai/tasks/T-20261023-extract-dropped/{research.md,inventory.py,PLAN.md}` 를 sanitize-check 후 커밋(worktree 가 HEAD 에서 만들어지므로 필수). `inventory.md` 는 샘플 파일 이름을 담고 있어 sanitize-check 가 실패하면 커밋하지 않고 절대경로로만 프롬프트에 준다. `.impeccable/config.json` 은 건드리지 않는다.

### Stage 1 — 기준선 기록
- 목적: 바뀌기 전 단위·E2E 결과와 실제 샘플별 CLI 출력을 남겨 이후 비교 기준으로 쓴다.
- 담당: runner(haiku) · 병렬 가능: 아니오 · 선행: S0
- 입력: §2 명령, `tests/fixtures/**`
- 쓰기 범위: `.ai/tasks/T-20261023-extract-dropped/logs/s1-unit.log`, `logs/s1-e2e.log`, `logs/baseline/**` (gitignored)
- 산출물: `logs/baseline/index.tsv`(번호·종료 코드·경로), `logs/baseline/<번호>/{stdout.txt,stderr.txt,*.md}`
- 명령:
  - `uv run pytest tests/unit -q > .ai/tasks/T-20261023-extract-dropped/logs/s1-unit.log 2>&1; tail -1 .ai/tasks/T-20261023-extract-dropped/logs/s1-unit.log`
  - `uv run pytest tests/e2e -q > .ai/tasks/T-20261023-extract-dropped/logs/s1-e2e.log 2>&1; tail -1 .ai/tasks/T-20261023-extract-dropped/logs/s1-e2e.log` (실패해도 계속, 결과만 기록)
  - `B=.ai/tasks/T-20261023-extract-dropped/logs/baseline; mkdir -p $B; : > $B/index.tsv; i=0; find tests/fixtures -type f ! -name README.md ! -name .gitkeep | sort | while IFS= read -r f; do i=$((i+1)); mkdir -p "$B/$i"; uv run hwp2md "$f" -o "$B/$i" > "$B/$i/stdout.txt" 2> "$B/$i/stderr.txt"; printf '%s\t%s\t%s\n' "$i" "$?" "$f" >> $B/index.tsv; done; wc -l $B/index.tsv`
- 검증: `tail -1 …/s1-unit.log` → `6 failed, 360 passed` 형태 · `wc -l …/baseline/index.tsv` → 파일 수(약 68)와 같음
- 완료 조건: 두 로그와 index.tsv 존재, 보고에 단위/E2E 요약 줄과 종료 코드별 파일 수만 적는다(파일 이름 금지)
- 실패 시: 명령 오류는 1회 재실행, 그래도 실패하면 BLOCKED

### Stage 2 — 실제 샘플 선정 규칙 고정
- 목적: 오늘 추가된 샘플 때문에 깨진 기존 테스트를 샘플 집합 정의만 바꿔 되살리고, 내용 기준 분류 도우미를 만든다.
- 담당: test-writer(sonnet) · 병렬 가능: 아니오 · 선행: S1
- 입력: §1-D 첫 행, §4-M `tests/samples.py` 계약, `logs/s1-unit.log`
- 쓰기 범위: `tests/samples.py`(신규), `tests/unit/test_memory.py`, `tests/unit/test_source_bytes.py`, `tests/unit/test_web_app.py`, `tests/e2e/conftest.py`, `tests/e2e/test_cli_hwpx.py`, `tests/e2e/test_cli_image.py`, `tests/e2e/test_cli_heading.py`, `tests/fixtures/README.md` (9개: 각 파일은 샘플 집합 정의 1~3줄만 바뀌므로 한 단계로 묶는다)
- 산출물: `classify`, `all_samples`, `LEGACY_*` (§4-M). 각 테스트의 실제 샘플 glob 을 `LEGACY_*` 로 교체. 단언·기대값은 그대로. README 에 "새 샘플은 구조 탐색 E2E(`tests/e2e/test_extract_real.py`)가 다룬다" 설명 추가
- 검증: `uv run pytest tests/unit -q 2>&1 | tail -1` → failed 0 · `grep -rn 'glob("\*.hwpx")' tests/unit tests/e2e | wc -l` → `0` · `uv run pytest tests/e2e --collect-only -q 2>&1 | tail -1` → 오류 없음 · `uv run ruff check tests && uv run ruff format --check tests`
- 완료 조건: 위 통과 + `tests/samples.py` 에 실제 샘플 이름이 `LEGACY_NAMES` 5개 외에 없음
- 실패 시: 단언을 바꿔야만 통과하면 BLOCKED

### Stage 3 — 블록 모델·렌더 계약
- 목적: §4-A~D 를 코드로 고정해 이후 모든 리더 단계가 같은 표현을 쓰게 한다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S2
- 입력: §4-A·B·C·D·M(`synth_items.py`), `src/hwp2md/blocks.py`, `render.py`, feature-reference §5
- 쓰기 범위: `src/hwp2md/blocks.py`, `src/hwp2md/skips.py`(신규), `src/hwp2md/numbering.py`(신규), `src/hwp2md/render.py`, `tests/synth_items.py`(신규), `tests/unit/test_render_extract.py`(신규)
- 산출물: §4 계약 전부 + `EXT_FIXTURES` 16개의 items·기대 Markdown·기대 skipped. `test_render_extract.py`: 블록을 직접 만들어 `render_blocks` 결과가 EXT_FIXTURES 기대 Markdown 과 같음(16개), 링크 허용목록·퍼센트 인코딩, 코드 스팬 백틱 규칙, 목록 들여쓰기·연결, 칸 인라인, Note 여러 단락, `iter_images` 순서, `make_paragraph`/`make_table` 정규화(문자열뿐이면 기존 값과 `==`), `format_number`·`apply_template`·`NumberingCounter`
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_render_extract.py -q` → pass
- 완료 조건: 기존 단위 테스트 무수정 통과 + 신규 테스트 pass
- 실패 시: 기존 렌더 출력이 바뀌면 원인 수정, 2회 실패 시 BLOCKED

### Stage 4 — 결과·페이로드 건너뜀 연결
- 목적: 리더 → convert/memory → API 페이로드까지 `skipped` 경로를 연다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S3
- 입력: §4-E, `convert.py`, `memory.py`, `__init__.py`, 두 리더의 `read_blocks`
- 쓰기 범위: `src/hwp2md/convert.py`, `src/hwp2md/memory.py`, `src/hwp2md/__init__.py`, `src/hwp2md/hwp5/reader.py`, `src/hwp2md/hwpx/reader.py`, `tests/unit/test_memory.py`(`test_to_payload_shape` 만), `tests/unit/test_convert_skipped.py`(신규)
- 산출물: 리더 `read_blocks(path, skips=None)`(이 단계는 받기만), `ConvertResult.skipped`, `MemoryResult.skipped`, 페이로드 `skipped`, `iter_images` 기반 이미지 수집·개수, `__init__` docstring 한컴 문구. 신규 테스트: SkipCounter 를 monkeypatch 로 채운 리더 → `ConvertResult.skipped`·페이로드 배열 형식, 건너뜀 없는 문서 `skipped == ()`/`[]`
- 검증: `STD_VERIFY` → failed 0 · `grep -cF '본 제품은 한글과컴퓨터의' src/hwp2md/__init__.py` → `1`
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 5 — 보호 문서 판별 (P1, worktree)
- 목적: DRM·비밀번호 문서를 전용 예외·오류 코드로 거절한다.
- 담당: implementer(opus) · 병렬 가능: 예(S6·S7·S8 과, worktree) · 선행: S4
- 입력: §4-F, research §2.12·§2.16, OpenSpec `document-protection`
- 쓰기 범위: `src/hwp2md/errors.py`, `src/hwp2md/detect.py`, `src/hwp2md/hwp5/reader.py`, `src/hwp2md/hwpx/reader.py`, `src/hwp2md/memory.py`, `tests/unit/test_protection.py`(신규), `tests/unit/test_memory.py`(§1-D 의 두 테스트만)
- 산출물: 예외 2개, DRM 서명 판별, HWP 5.0 비트 1·4·10, HWPX 매니페스트 암호화, 오류 코드. 신규 테스트: 합성 DRM 바이트(`9B 20` + `DRMONE  ` + 난수 4000B) 경로·bytes 입력, 속성 0x3/0x11/0x401, HWPX 매니페스트(합성 zip), `convert_to_response` 코드·상태, `UnsupportedHwpError` 하위 관계
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_protection.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 6 — 수식 변환기 벤더링 (P1, worktree)
- 목적: 한글 수식 스크립트 → LaTeX 변환 함수를 의존성 없이 갖춘다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S4
- 입력: §4-G, research §2.4·§3. 원본: `git clone --depth 1 https://github.com/airmang/python-hwpx <스크래치패드>/python-hwpx` 후 `src/hwpx/equation/eqedit.py`, `tokens.py`, 저장소 LICENSE·NOTICE
- 쓰기 범위: `src/hwp2md/equation/__init__.py`, `src/hwp2md/equation/eqedit.py`, `src/hwp2md/equation/tokens.py`, `NOTICE`(신규), `tests/unit/test_equation.py`(신규)
- 산출물: `to_latex`. 신규 테스트: `a over b` → `\frac` 포함, `sqrt x`, `sum _{i=1} ^{n}`, 그리스 문자, 빈 문자열 → None, 깊은 중첩·긴 입력 → 예외 없이 None 또는 문자열, 변환기 내부 예외를 삼키는지(monkeypatch)
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_equation.py -q` → pass · `grep -c 'Apache' NOTICE` → ≥ 1
- 완료 조건: 위 통과
- 실패 시: 저장소 접근 불가 → `to_latex` 가 항상 None 인 구현 + NOTICE 에 "벤더링 없음" 기록, PARTIAL(§3)

### Stage 7 — OLE·차트 모듈 (P1, worktree)
- 목적: 세 리더가 공유할 OLE·OOXML 차트 해석기를 만든다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S4
- 입력: §4-H, research §2.3, `tests/synth_hwp5.py` 의 `build_cfb`(import 만)
- 쓰기 범위: `src/hwp2md/ole.py`(신규), `tests/synth_ole.py`(신규), `tests/unit/test_ole_chart.py`(신규)
- 산출물: §4-H 함수. `synth_ole.py`: `chart_xml(title, categories, series) -> bytes`(c:chartSpace + c:barChart, strCache·numCache), `build_ole_cfb(streams: Mapping[str, bytes]) -> bytes`(`synth_hwp5.build_cfb` 사용), `hwpx_ole_entry(cfb) -> bytes`(4바이트 길이 접두). 신규 테스트: 막대 차트 → 기대 블록(OpenSpec "막대 차트 캐시값"), 제목 없음, 계열 2개, `Contents` 만 → chart_legacy, Ole10Native PNG → Image, CFB 아님 → ole, 길이 접두 벗기기 2경우, XXE 시도 XML → 엔티티 미해석
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_ole_chart.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 8 — 배포용 문서 복호 모듈 (P1, worktree)
- 목적: 배포용 문서 `ViewText` 스트림을 복호화하는 순수 파이썬 모듈을 만든다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S4
- 입력: §4-I, research §2.11(알고리즘), FIPS-197. pyhwp 소스는 열지 않는다
- 쓰기 범위: `src/hwp2md/hwp5/aes.py`(신규), `src/hwp2md/hwp5/distdoc.py`(신규), `tests/synth_distdoc.py`(신규), `tests/unit/test_distdoc.py`(신규)
- 산출물: §4-I. `synth_distdoc.py`: `aes128_ecb_encrypt(key, data)`, `build_distribute_doc_data(seed: int, key: bytes) -> bytes`(256B, 역 XOR), `encrypt_view_text(section: bytes, *, seed: int = 0x2A7F3C11, key: bytes = bytes(range(16))) -> bytes`(레코드 헤더 + 256B + AES, 패딩 0). 신규 테스트: FIPS-197 C.1 벡터, 키 유도 왕복(seed 3종, seed & 0xF 경계), `decrypt_view_text(encrypt_view_text(x))` 앞부분 == x, 잘못된 태그·크기 → UnsupportedHwpError, 1MB 복호 소요 시간 기록(단언은 10초 이하)
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_distdoc.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 9 — HWP 5.0 단락 안 요소 (R1, worktree)
- 목적: HWP 5.0 단락 안 링크·각주/미주·수식·필드 글자를 위치대로 꺼내고 머리말·꼬리말·숨은 설명·메모를 건너뜀으로 보고한다.
- 담당: implementer(opus) · 병렬 가능: 예(S10·S11 과, worktree) · 선행: S5~S8 합침
- 입력: §4-A·B·J, research §2 공통 메모·§2.4~2.7·§2.9, `EXT_IDS_BY_STAGE["inline"]`
- 쓰기 범위: `src/hwp2md/hwp5/records.py`, `src/hwp2md/hwp5/body.py`, `src/hwp2md/hwp5/reader.py`, `tests/synth_hwp5.py`, `tests/unit/test_hwp5_inline.py`(신규)
- 산출물: `decode_para_runs`, 컨트롤 대응, `%hlk` command 해석, `fn  `/`en  ` → NoteRef + 문서 끝 Note, `eqed` + `EQEDIT`(WORD 길이 + UTF-16 스크립트) → Math, `head`/`foot` 건너뜀, `tcmt` → hidden_comment, 마지막 섹션 `MEMO_LIST` 마다 memo. `synth_hwp5.py`: `SynthRich`·`SynthHeaderFooter`·`SynthHidden` 을 레코드로 쓰는 빌더(확장 제어문자 + CTRL_HEADER 순서 일치). 신규 테스트: inline 대상 EXT_FIXTURES 10개가 기대 Markdown·skipped 와 같음, 제어문자·CTRL_HEADER 개수 불일치 시 실패하지 않음, 기존 `test_hwp5_body.py` 무수정 통과
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_hwp5_inline.py -q` → pass · 실제 샘플 확인: inventory §4 "수식"·"각주"·"하이퍼링크"·"머리말·꼬리말"·"누름틀" 행 파일을 변환해 Math·NoteRef·Link 개수, 건너뜀 개수를 `logs/s9-real.log` 에 기록(inventory 개수와 비교)
- 완료 조건: 위 통과 + 실제 샘플 개수가 inventory 개수와 같거나 차이 사유가 로그에 있음
- 실패 시: 2회 실패 시 BLOCKED

### Stage 10 — HWPX 단락 안 요소 (R1, worktree)
- 목적: HWPX 의 같은 요소를 같은 블록으로 꺼낸다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S5~S8 합침
- 입력: §4-A·B·J, research §2.4~2.7·§2.9(HWPX 부분), `EXT_IDS_BY_STAGE["inline"]`
- 쓰기 범위: `src/hwp2md/hwpx/body.py`, `src/hwp2md/hwpx/reader.py`, `tests/synth_hwpx.py`, `tests/unit/test_hwpx_inline.py`(신규), `tests/unit/test_hwpx_body.py`(§1-D 한 테스트만)
- 산출물: `hp:fieldBegin[@type="HYPERLINK"]`(`hp:stringParam[@name="Path"]` 우선, 없으면 `Command`)…`hp:fieldEnd` → Link, `hp:footNote`/`hp:endNote`(run 직계 또는 `hp:ctrl` 안) → NoteRef + Note(`hp:autoNum` 무시), `hp:equation/hp:script` → Math, `hp:ctrl/hp:header|hp:footer` → header_footer, `hp:hiddenComment` → hidden_comment, `hp:memogroup/hp:memo` → memo. 합성기 빌더와 신규 테스트(inline EXT_FIXTURES 10개)
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_hwpx_inline.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 11 — HWPML 판별·본문·표·그림 (R1, worktree)
- 목적: 지금 "HWP 아님"으로 거부되는 HWPML 2.x 를 세 번째 입력으로 읽는다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S5~S8 합침
- 입력: OpenSpec `hwpml-input`, research §2.15, §4-E·F·J, `hwpx/body.py` 의 `_place_cells`, `images.ImageNamer`
- 쓰기 범위: `src/hwp2md/hwpml/__init__.py`, `src/hwp2md/hwpml/reader.py`, `src/hwp2md/hwpml/body.py`(모두 신규), `src/hwp2md/detect.py`, `src/hwp2md/convert.py`, `tests/synth_hwpml.py`(신규), `tests/unit/test_hwpml.py`(신규) — 7개: 새 패키지 3파일이 한 덩어리
- 산출물: `looks_like_hwpml`, `prepare_xml`(BOM·UTF-16 → UTF-8, 리터럴 엔티티 치환, DOCTYPE 제거, 그 밖 선언 → `Hwp2mdError("unsupported DTD in HWPML")`), `read_blocks(path, skips=None)`(단락·제목·표·그림, Base64 → 시그니처 판별 → raw deflate 시도, BINDATA 50MB 상한, `Type="Link"` → image_link), detect ④, convert 분기. `synth_hwpml.py`: `build_hwpml(items, *, encoding="utf-8", doctype_nbsp=False) -> bytes`, `write_hwpml(path, items, **kw) -> Path` (기존 `Item`: str·SynthHeading·SynthTable·SynthImage 지원). 신규 테스트: OpenSpec `hwpml-input` 시나리오 전부, 기존 `FIXTURE_ITEMS_*`(단락·표·병합·제목·이미지)로 만든 HWPML 이 HWPX 와 같은 Markdown
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/unit/test_hwpml.py -q` → pass · 실제 샘플 확인: inventory §3 HWPML 2개를 CLI 로 변환해 종료 코드·요약 줄을 `logs/s11-real.log` 에 기록
- 완료 조건: 위 통과 + 실제 HWPML 2개 종료 코드 0
- 실패 시: 2회 실패 시 BLOCKED

### Stage 12 — HWP 5.0 개체 (R2, worktree)
- 목적: HWP 5.0 표 칸 그림·캡션·글상자·묶음·OLE 를 꺼내고 캡션 오인 버그를 고친다.
- 담당: implementer(opus) · 병렬 가능: 예(S13·S14 와, worktree) · 선행: R1 합침
- 입력: §4-A·B·H·J, research §2.1~2.3·§2.10·공통 메모(캡션), `EXT_IDS_BY_STAGE["objects"]`
- 쓰기 범위: `src/hwp2md/hwp5/body.py`, `src/hwp2md/hwp5/reader.py`, `tests/synth_hwp5.py`(빌더 추가만, `EXPECTED_*_IMAGE_IN_CELL` 은 건드리지 않음), `tests/unit/test_hwp5_objects.py`(신규)
- 산출물: 칸 단락에 이미지 해석기 전달 → `make_table`, `TABLE` 앞 `LIST_HEADER` = 캡션, gso 하위 순회(SHAPE_COMPONENT 종류: 그림·글상자 LIST_HEADER 단락·묶음 재귀·OLE(BinData ID 오프셋 12 우선, 실제 샘플로 확인)·글맵시 → textart), 캡션 단락, 머리말 안 그림 제외, `BinDataStore` 가 LINK → image_link, 본체 없음 → image_missing 보고, OLE 원시 바이트 제공. 합성기: `SynthTextBox`·`SynthCaptionedTable`·`SynthChart`(synth_ole 사용)·SynthHeaderFooter(with_image) 빌더. 신규 테스트: objects EXT_FIXTURES 4개 + header_image, 칸 그림 번호, 캡션 있는 표의 칸 수
- 검증: `STD_VERIFY CELL_DESELECT` → failed 0 · `uv run pytest tests/unit/test_hwp5_objects.py -q` → pass · 실제 샘플: inventory §4 "표 칸 안 그림"·"글상자"·"그래프·차트(OLE)" 행 파일 → 칸 그림 수·글상자 단락 수·차트 결과(표/legacy)를 `logs/s12-real.log`
- 완료 조건: 위 통과 + 칸 그림 수가 inventory 개수와 같음
- 실패 시: 2회 실패 시 BLOCKED (OLE 가 구형 차트인 것은 실패 아님)

### Stage 13 — HWPX 개체 (R2, worktree)
- 목적: HWPX 의 같은 개체를 같은 블록으로 꺼낸다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: R1 합침
- 입력: §4-A·B·H·J, research §2.1~2.3·§2.10(HWPX)
- 쓰기 범위: `src/hwp2md/hwpx/body.py`, `src/hwp2md/hwpx/reader.py`, `src/hwp2md/hwpx/bindata.py`, `tests/synth_hwpx.py`, `tests/unit/test_hwpx_objects.py`(신규)
- 산출물: `_cell_text` → 칸 인라인(이미지 포함) `make_table`, `hp:tbl/hp:caption`·`hp:pic/hp:caption` 단락, `hp:rect|ellipse|arc|polygon|curve|connectLine` 의 `hp:drawText/hp:subList/hp:p` 재귀, `hp:container` 자식 순서 재귀(글·그림), `hp:chart/@chartIDRef` zip 엔트리(50MB 상한) → `chart_xml_to_blocks`, `hp:ole/@binaryItemIDRef` → `unwrap_hwpx_ole` → `ole_to_outcome`, `hp:textart` → textart, 양식 개체(`hp:btn|checkBtn|radioBtn|comboBox|listBox|edit|scrollBar`) → form_control, 해석 불가 그림 → image_missing. 신규 테스트: objects EXT_FIXTURES 4개 + header_image
- 검증: `STD_VERIFY CELL_DESELECT` → failed 0 · `uv run pytest tests/unit/test_hwpx_objects.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 14 — HWPML 요소 (R2, worktree)
- 목적: HWPML 에서도 링크·각주·수식·머리말·캡션·글상자·목록·차트를 같은 블록으로 꺼낸다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: R1 합침
- 입력: §4 전부, research §2.15, OpenSpec `element-extraction`
- 쓰기 범위: `src/hwp2md/hwpml/body.py`, `src/hwp2md/hwpml/reader.py`, `tests/synth_hwpml.py`, `tests/unit/test_hwpml_elements.py`(신규)
- 산출물: `FIELDBEGIN[@Type="Hyperlink"]@Command`, `FOOTNOTE`/`ENDNOTE`, `EQUATION/SCRIPT`, `HEADER`/`FOOTER` 건너뜀, `HIDDENCOMMENT`, 캡션, 도형 `DRAWTEXT`, `CONTAINER`, `OLE`(BINDATA → CFB), 칸 그림, `PARASHAPE@HeadingType="Number|Bullet"` + `NUMBERINGLIST`/`BULLETLIST` 목록. 신규 테스트: EXT_FIXTURES 16개 전부(HWPML 판)
- 검증: `STD_VERIFY CELL_DESELECT` → failed 0 · `uv run pytest tests/unit/test_hwpml_elements.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 15 — HWP 5.0 목록 (R3, worktree)
- 목적: HWP 5.0 번호·글머리표 단락에 목록 정보를 붙인다.
- 담당: implementer(opus) · 병렬 가능: 예(S16·S17 과, worktree) · 선행: R2 합침
- 입력: §4-A·C, research §2.8, hwplib 의 문단 머리 정보 비트 정의(읽기만, Apache-2.0)
- 쓰기 범위: `src/hwp2md/hwp5/docinfo.py`, `src/hwp2md/hwp5/body.py`, `tests/synth_hwp5.py`, `tests/unit/test_hwp5_lists.py`(신규)
- 산출물: `ParaShape` 에 머리 종류·수준·번호/글머리표 ID(오프셋 30 UINT16, 1-기준 우선), `NUMBERING`(수준별 형식 문자열·번호 모양·시작 번호), `BULLET`(문자), 단락 `ListInfo`(번호는 `NumberingCounter`·`apply_template`). 기존 `heading_level` 동작 불변. 신규 테스트: bullets·numbers EXT_FIXTURES, 수준 리셋, 번호 모양 3종
- 검증: `STD_VERIFY CELL_DESELECT` → failed 0 · `uv run pytest tests/unit/test_hwp5_lists.py -q` → pass · 실제 샘플: inventory §4 "번호 목록"·"글머리표 목록" 행 파일의 ListInfo 개수를 `logs/s15-real.log`(inventory 개수와 비교, ID 기준 0/1 결론 기록)
- 완료 조건: 위 통과 + ListInfo 개수 = inventory 개수
- 실패 시: 2회 실패 시 BLOCKED

### Stage 16 — HWPX 목록 (R3, worktree)
- 목적: HWPX 번호·글머리표 단락에 목록 정보를 붙인다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: R2 합침
- 입력: §4-A·C, research §2.8(HWPX)
- 쓰기 범위: `src/hwp2md/hwpx/header.py`, `src/hwp2md/hwpx/body.py`, `tests/synth_hwpx.py`, `tests/unit/test_hwpx_lists.py`(신규)
- 산출물: `HeaderInfo` 에 paraPr → (종류, idRef, level), `hh:numbering[@id,@start]/hh:paraHead[@level,@start,@numFormat]` 글자, `hh:bullet[@id,@char]`. 기존 `heading_level` 불변. 신규 테스트: bullets·numbers EXT_FIXTURES, `hp:switch/hp:case` 안 heading
- 검증: `STD_VERIFY CELL_DESELECT` → failed 0 · `uv run pytest tests/unit/test_hwpx_lists.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 17 — HWP 5.0 배포용 문서 읽기 (R3, worktree)
- 목적: 배포용 문서를 거절하지 않고 변환한다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: R2 합침
- 입력: §4-I, OpenSpec `document-protection` 첫 요구, `hwp5/distdoc.py`
- 쓰기 범위: `src/hwp2md/hwp5/reader.py`, `tests/synth_distdoc.py`, `tests/unit/test_hwp5_distribution.py`(신규)
- 산출물: 속성 bit2 → `ViewText/Section<N>` 복호 → (압축이면) inflate. `ViewText/Section0` 없음 → `UnsupportedHwpError("distribution document: ViewText missing: …")`. `synth_distdoc.py` 에 `build_hwp5_distribution(items, *, compressed=True) -> bytes` 추가. 신규 테스트: 합성 배포용 == 일반 문서 Markdown(압축·비압축), ViewText 없음 → UnsupportedHwpError, 기존 `test_convert.py::test_encrypted_or_distribution_rejected[0x5]` 무수정 통과
- 검증: `STD_VERIFY CELL_DESELECT` → failed 0 · `uv run pytest tests/unit/test_hwp5_distribution.py -q` → pass · 실제 샘플: inventory §4 "배포용 문서" 행 2개를 CLI 로 변환, 종료 코드·단락 수·소요 초를 `logs/s17-real.log`
- 완료 조건: 위 통과 + 실제 2개 종료 코드 0, 각 30초 이하
- 실패 시: 실제 샘플만 실패 → §3 PARTIAL 규칙

### Stage 18 — 교차 포맷 정합
- 목적: 칸 그림 기대값을 새 규칙으로 바꾸고, 모든 새 요소가 세 포맷에서 같은 결과임을 확인한다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: R3 합침
- 입력: §1-D, OpenSpec `element-extraction` "세 입력 포맷은…", `tests/synth_items.py`
- 쓰기 범위: `tests/synth_hwp5.py`(`EXPECTED_*_IMAGE_IN_CELL` 4개 상수와 주석만), `tests/unit/test_cross_format_extract.py`(신규), `src/hwp2md/hwp5/body.py`, `src/hwp2md/hwpx/body.py`, `src/hwp2md/hwpml/body.py` (차이를 고칠 때만)
- 산출물: 칸 그림 기대값(OpenSpec "셀 그림과 본문 그림" 시나리오 값), EXT_FIXTURES 16개 × 3포맷 Markdown·skipped 동일 테스트 + 기존 `FIXTURE_ITEMS_*` 의 HWPML 판 동일 테스트
- 검증: `STD_VERIFY`(CELL_DESELECT 없이) → failed 0 · `uv run pytest tests/unit/test_cross_format_extract.py -q` → pass
- 완료 조건: 위 통과
- 실패 시: 포맷 차이를 계약 변경 없이 못 고치면 BLOCKED

### Stage 19 — CLI 오류 문구·건너뜀 요약 (cli.py 전용 단계)
- 목적: CLI 가 보호 문서 사유와 건너뛴 요소를 알린다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S18
- 입력: §4-K, `src/hwp2md/cli.py`
- 쓰기 범위: `src/hwp2md/cli.py` (이 파일만)
- 산출물: §4-K 문자열
- 검증: `STD_VERIFY` → failed 0 · `uv run pytest tests/e2e/test_cli_convert.py tests/e2e/test_cli_hwpx.py tests/e2e/test_cli_image.py -q --deselect "tests/e2e/test_cli_image.py::test_image_in_table_cell_not_extracted_both_formats" --deselect "tests/e2e/test_cli_image.py::test_real_fixture_images"` → failed 0 · `printf '\x9b\x20DRMONE  x' > /private/tmp/claude-501/-Users-illi-illy-projects/4b7ad5a2-bb97-4539-bbfd-1f4c9f6f768a/scratchpad/d.hwp; uv run hwp2md /private/tmp/claude-501/-Users-illi-illy-projects/4b7ad5a2-bb97-4539-bbfd-1f4c9f6f768a/scratchpad/d.hwp; echo rc=$?` → stderr `unsupported HWP file (DRM protected)`, `rc=3`
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 20 — 웹 UI 갱신 (P3, worktree)
- 목적: 현재 웹 화면이 새 오류 코드·건너뜀 경고·한컴 문구를 보여 준다.
- 담당: implementer(opus) · 병렬 가능: 예(S21·S22·S23 과, worktree) · 선행: S19
- 입력: §4-L, feature-reference §9·§10.2 불변식, `src/hwp2md/web/static/*`
- 쓰기 범위: `src/hwp2md/web/static/app.js`, `src/hwp2md/web/static/index.html`, `src/hwp2md/web/static/style.css`, `tests/unit/test_web_runtime_zip.py`(신규)
- 산출물: `ERROR_TEXT` drm·encrypted·unsupported, `#skipped`(role=status, hidden 기본, textContent), 바닥글 한컴 문구. 신규 테스트: `build_runtime_zip()` 이름 목록에 C17 의 5개 경로, `GET /` 본문에 한컴 문구와 `id="skipped"`
- 검증: `STD_VERIFY` → failed 0 · `source ~/.nvm/nvm.sh >/dev/null 2>&1 && node --check src/hwp2md/web/static/app.js` → 종료 0
- 완료 조건: 위 통과 (화면 확인은 S26 스크린샷)
- 실패 시: 2회 실패 시 BLOCKED

### Stage 21 — design/v3 갱신 (P3, worktree)
- 목적: 개발 중인 프론트엔드 시안에 추출 한계와 건너뜀 경고를 명시하고 데모 응답을 실제 엔진 출력으로 바꾼다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S19
- 입력: §4-L, `design/v3/README.md`, `index.html` `#limits`, `app.html`, `js/app.js`, `js/demo-engine.js`, OpenSpec `web-preview` ADDED 요구, `docs/extraction-limits.md` 의 행 목록(§4-L 열, 내용은 §1-A 의 불가·부분·보류 행)
- 쓰기 범위: `design/v3/index.html`, `design/v3/app.html`, `design/v3/js/app.js`, `design/v3/js/demo-engine.js`, `design/v3/js/demo-payload.js`, `design/v3/css/app.css`, `design/v3/README.md`, `.ai/tasks/T-20261023-extract-dropped/demo/make_payload.py`(신규) — 8개: 시안 한 화면 세트
- 산출물: `#limits` 목록을 §1-A 의 불가·부분·보류 항목(이유 한 줄)으로 다시 쓰고 `docs/extraction-limits.md` 링크, 이미 된 항목(각주·배포용·표 칸 그림·글상자·목록)은 지원 항목으로 이동. 변환 화면 `#skipped` + 링크, `ERROR_TEXT` drm·encrypted·unsupported, 데모 엔진 STATUS·MESSAGE 에 drm·encrypted 와 데모 도크 "DRM 오류" 버튼, 바닥글·변환 화면 한컴 문구. `make_payload.py`: `tests/synth_hwpx.py`·`synth_items.py` 로 데모 HWPX(제목·링크·각주·글머리표·칸 그림 표·수식·머리말)를 만들고 `hwp2md.memory.convert_to_response(data, "2026_가상_공고문.hwpx")` 결과로 `demo-payload.js` 를 쓴다(기존 파일 머리 주석 형식 유지)
- 검증: `uv run python .ai/tasks/T-20261023-extract-dropped/demo/make_payload.py && grep -c '"skipped"' design/v3/js/demo-payload.js` → ≥ 1 · `source ~/.nvm/nvm.sh >/dev/null 2>&1 && for f in design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js; do node --check $f || exit 1; done` → 종료 0 · `grep -c 'extraction-limits.md' design/v3/index.html design/v3/app.html` → 각 ≥ 1
- 완료 조건: 위 통과 (화면 확인은 S26)
- 실패 시: 2회 실패 시 BLOCKED

### Stage 22 — 추출 한계 문서·기능 명세 (P3, worktree)
- 목적: 끝내 추출하지 못하는 것을 이유·대안과 함께 정리하고 기능 명세를 현재 동작에 맞춘다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S19
- 입력: §1-A, §4 전부, research §4, OpenSpec 세 신규 capability, `logs/s9·s12·s15·s17-real.log`(개수만)
- 쓰기 범위: `docs/extraction-limits.md`(신규), `docs/feature-reference.md`
- 산출물: extraction-limits — 요약, 표(§4-L 열; 건너뜀 9종 각 1행 + 비밀번호·DRM·구형 차트·WMF/EMF·필드 값·목록 번호·수식 근사·글상자 순서·단락 중간 그림·서식·책갈피 행), 실제 샘플 기준 개수(파일 이름 없이 "샘플 N개 중 M개"), 사용자 우회 방법. feature-reference — §0 목차, §1 지도, §2 파이프라인(HWPML), §3 판별 순서, §4 블록 모델·HWP5·HWPX·HWPML·각 요소, §5 렌더 규칙·개수, §7 API 필드, §8.3 `skipped`, §8.4·§9.7·§11 오류 코드, §12 해결된 차이와 남은 차이, §14 한계(→ extraction-limits 링크), §15 색인
- 검증: C16 명령 → `9` · `grep -c '^| ' docs/extraction-limits.md` → ≥ 20 · `grep -c 'skipped' docs/feature-reference.md` → ≥ 3 · `/Users/illi/illy-projects/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md` → OK
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 23 — README·결정 기록·라이선스 고지 (P3, worktree)
- 목적: 사용자 문서와 결정 기록, 라이선스 고지를 갱신한다.
- 담당: implementer(opus) · 병렬 가능: 예 · 선행: S19
- 입력: §1-A, §7 기본값(또는 사용자 답), S6 의 `NOTICE`
- 쓰기 범위: `README.md`, `docs/decisions.md`, `docs/system-overview.md`, `LICENSE`(신규), `NOTICE`
- 산출물: README 지원 범위 표(새 요소·HWPML·배포용·DRM/암호 거부), 로드맵 체크(각주·배포용), 한계 → extraction-limits 링크, 한컴 문구, 배포용 문서 고지("편집·복사 제한 문서를 텍스트로 꺼내므로 작성자 의도를 확인하세요"), 라이선스 절. decisions: 2026-10-23 날짜로 §design.md Decisions 1~13 요약(각 1~3줄). system-overview: 모듈 목록(`skips`, `numbering`, `ole`, `equation`, `hwpml`, `hwp5/aes`, `hwp5/distdoc`). LICENSE: §7 Q7 기본값 MIT 전문(저작권자 "hwp2md contributors", 2026). NOTICE: 벤더링 출처 + 한컴 문구
- 검증: C15 중 README 1건 · `grep -c '2026-10-23' docs/decisions.md` → 이전보다 ≥ 10 증가 · `test -f LICENSE` · sanitize-check OK
- 완료 조건: 위 통과
- 실패 시: 2회 실패 시 BLOCKED

### Stage 24 — E2E 작성: 실제 샘플·CLI
- 목적: inventory 우선 검증 요소마다 실제 샘플 E2E 와 합성 문서 CLI E2E 를 만든다.
- 담당: test-writer(sonnet, 2회 실패 시 opus) · 병렬 가능: 아니오 · 선행: P3 합침
- 입력: §2 C5~C12, inventory.md §4 행 이름, `inventory.py`(탐색 방식), §4-M, `logs/baseline/**`, §1-D
- 쓰기 범위: `tests/samples.py`, `tests/e2e/test_extract_real.py`(신규), `tests/e2e/test_extract_cli.py`(신규), `tests/e2e/test_cli_image.py`, `tests/e2e/test_cli_heading.py`, `tests/e2e/test_cli_hwpx.py` (뒤 셋은 §1-D 해당 항목만)
- 산출물: `probe` 키: `cell_image`, `body_image`, `header_footer`, `header_footer_image`, `textbox`, `ole`, `equation`, `hyperlink_web`, `footnote`, `endnote`, `numbered`, `bullet`, `field_clk`, `distribution`, `hwpml_table`, `hwpml_picture`, `hwpml_header_footer`, `bmp`. `test_extract_real.py` 함수 18개: `test_cell_image`, `test_header_footer_image`, `test_textbox`, `test_chart_ole`, `test_equation`, `test_hyperlink`, `test_footnote`, `test_header_footer`, `test_numbered_list`, `test_bullet_list`, `test_field_text`, `test_shapes_hwpx`, `test_bmp`, `test_distribution`, `test_hwpml`, `test_drm`, `test_not_hwp`, `test_all_samples_convert` — 각자 `samples_with(feature)` 로 대상 선택, 없으면 `pytest.skip`. 기대값은 §2 C6~C12. Markdown 사본은 `tests/e2e/screenshots/`(gitignored)에만. `test_extract_cli.py`: EXT_FIXTURES 대표 6개(link, footnote, header, textbox, numbers, chart)를 세 포맷 CLI 로 변환해 같은 `.md`·요약 줄, DRM 합성·암호 합성(0x3)·HWPX 매니페스트 → 종료 코드 3·문구, 배포용 합성 → 0. 기존 기대값 갱신은 S1 기준선과 구조 탐색 개수 주석 필수
- 검증: `uv run pytest tests/e2e/test_extract_real.py tests/e2e/test_extract_cli.py tests/e2e/test_cli_image.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py -q -rs 2>&1 | tail -3` → failed 0, skipped 0 · C19 → `0`
- 완료 조건: 위 통과
- 실패 시: 제품 버그로 실패 → 실패 그대로 보고(테스트 약화 금지), orchestrator 가 해당 리더 단계 RETRY

### Stage 25 — E2E 작성: 화면
- 목적: 서버·브라우저 모드와 design/v3 화면이 건너뜀·보호 문서·한계를 보여 주는지 검증하고 스크린샷을 남긴다.
- 담당: test-writer(sonnet, 2회 실패 시 opus) · 병렬 가능: 아니오 · 선행: S24
- 입력: C13·C14, §4-L, `tests/e2e/test_web_ui.py`(기존 패턴), OpenSpec `web-preview` ADDED 요구
- 쓰기 범위: `tests/e2e/test_web_extract.py`(신규), `tests/e2e/test_design_v3.py`(신규), `tests/e2e/test_web_ui.py`(§1-D 해당 항목만)
- 산출물: `test_web_extract.py`: 서버 모드 머리말 합성 HWPX → `#skipped` 보임·글자, 단락만 → 숨김, DRM 합성 → 오류 문구, 브라우저 모드 같은 세 경우(CDN 필요, 실패 시 skip 사유), API `/api/convert` 의 `skipped`·`drm`/415·`encrypted`/415, HWPML 합성 업로드 → 200. 스크린샷 `tests/e2e/screenshots/s26-web-skipped.png`, `s26-web-drm.png`. `test_design_v3.py`: `file://…/design/v3/app.html` 데모 도크 "예시 변환" → `#skipped` 보임·링크 href 가 `extraction-limits.md` 로 끝남, "DRM 오류" → 문구, `index.html#limits` 항목 수 ≥ 8·링크 존재(CDN 필요). 스크린샷 `s26-design-app-skipped.png`, `s26-design-limits.png`
- 검증: `uv run pytest tests/e2e/test_web_extract.py tests/e2e/test_design_v3.py -q -rs 2>&1 | tail -3` → failed 0
- 완료 조건: 위 통과 + 스크린샷 4개 존재
- 실패 시: S24 와 같음

### Stage 26 — E2E 실행·스크린샷
- 목적: 전체 검증을 한 번에 돌려 기록한다.
- 담당: runner(haiku, 2회 실패 시 sonnet) · 병렬 가능: 아니오 · 선행: S25
- 입력: §2 C1~C19 명령
- 쓰기 범위: `logs/e2e.log`(프로젝트 루트 `logs/`), `.ai/tasks/T-20261023-extract-dropped/logs/s26-*.log`, `.ai/tasks/T-20261023-extract-dropped/screenshots/*.png`
- 산출물: C1~C19 결과 표(명령·결과 한 줄씩), 스크린샷 4개를 `tests/e2e/screenshots/` 에서 TASK 스크린샷 폴더로 복사
- 검증: `uv run pytest tests/e2e -q > logs/e2e.log 2>&1; tail -1 logs/e2e.log` → failed 0 · C1~C19 각 기대 결과
- 완료 조건: 모든 C 통과, 실패 항목은 숫자와 함께 보고
- 실패 시: 실패 테스트 목록만 보고(수정 금지), orchestrator 가 해당 단계 RETRY

### Stage 27 — 리뷰·결과 기록
- 담당: reviewer(sonnet) → scribe(haiku) · 선행: S26
- 입력: `git diff e18cd70..HEAD`, 스크린샷 4개(reviewer 가 직접 연다), §1-D 목록, C1~C19 결과, OpenSpec change
- 쓰기 범위: `.ai/tasks/T-20261023-extract-dropped/RESULT.md`, `.ai/STATE.md`(scribe 전체 재작성)
- 산출물: reviewer PASS/FAIL(§1-D 밖 기존 테스트 수정 0, pyhwp 흔적 0, 실제 샘플 이름 신규 추적 0, 스크린샷 기대 요소), RESULT.md(결론 3줄, 요소별 결과 표, PARTIAL 항목, 남은 한계 → extraction-limits)
- 검증: `test -f .ai/tasks/T-20261023-extract-dropped/RESULT.md` · reviewer 결과 PASS
- 완료 조건: PASS + RESULT·STATE 기록 + orchestrator 가 `openspec validate` 후 archive

## 6. 병렬 실행 맵
```
S0 → S1 → S2 → S3 → S4 ─┬─ S5 (보호 문서) ─┐
                        ├─ S6 (수식)      ─┤  P1: worktree 격리
                        ├─ S7 (OLE·차트)   ─┤
                        └─ S8 (배포용 복호) ─┘
                              │ 합침 + STD_VERIFY
        ┌─ S9  (HWP5 단락) ──┐
  R1 ───┼─ S10 (HWPX 단락) ──┼─ 합침 + STD_VERIFY      worktree 격리
        └─ S11 (HWPML 기본) ─┘
        ┌─ S12 (HWP5 개체) ──┐
  R2 ───┼─ S13 (HWPX 개체) ──┼─ 합침 + STD_VERIFY CELL_DESELECT
        └─ S14 (HWPML 요소) ─┘
        ┌─ S15 (HWP5 목록) ──┐
  R3 ───┼─ S16 (HWPX 목록) ──┼─ 합침 + STD_VERIFY CELL_DESELECT
        └─ S17 (HWP5 배포용) ┘
  → S18 (교차 포맷) → S19 (cli.py 단독)
        ┌─ S20 (웹 UI) ─────┐
  P3 ───┼─ S21 (design/v3) ─┼─ 합침 + STD_VERIFY      worktree 격리
        ├─ S22 (한계·명세) ──┤
        └─ S23 (README 등) ─┘
  → S24 → S25 (E2E 작성) → S26 (E2E 실행) → S27 (리뷰·기록)
```
쓰기 범위 대조 (경로 단위, planner 확인):
- P1: S5 {errors.py, detect.py, hwp5/reader.py, hwpx/reader.py, memory.py, test_protection.py, test_memory.py} · S6 {equation/*, NOTICE, test_equation.py} · S7 {ole.py, synth_ole.py, test_ole_chart.py} · S8 {hwp5/aes.py, hwp5/distdoc.py, synth_distdoc.py, test_distdoc.py} → 교집합 없음
- R1: S9 {hwp5/records.py, hwp5/body.py, hwp5/reader.py, synth_hwp5.py, test_hwp5_inline.py} · S10 {hwpx/body.py, hwpx/reader.py, synth_hwpx.py, test_hwpx_inline.py, test_hwpx_body.py} · S11 {hwpml/*, detect.py, convert.py, synth_hwpml.py, test_hwpml.py} → 교집합 없음
- R2: S12 {hwp5/body.py, hwp5/reader.py, synth_hwp5.py, test_hwp5_objects.py} · S13 {hwpx/body.py, hwpx/reader.py, hwpx/bindata.py, synth_hwpx.py, test_hwpx_objects.py} · S14 {hwpml/body.py, hwpml/reader.py, synth_hwpml.py, test_hwpml_elements.py} → 교집합 없음
- R3: S15 {hwp5/docinfo.py, hwp5/body.py, synth_hwp5.py, test_hwp5_lists.py} · S16 {hwpx/header.py, hwpx/body.py, synth_hwpx.py, test_hwpx_lists.py} · S17 {hwp5/reader.py, synth_distdoc.py, test_hwp5_distribution.py} → 교집합 없음
- P3: S20 {web/static/app.js, index.html, style.css, test_web_runtime_zip.py} · S21 {design/v3/* 7개, .ai/…/demo/make_payload.py} · S22 {docs/extraction-limits.md, docs/feature-reference.md} · S23 {README.md, docs/decisions.md, docs/system-overview.md, LICENSE, NOTICE} → 교집합 없음 (NOTICE 는 S6 이후 S23 만)

worktree 운영 (쓰는 단계 2개 이상 병렬 → **worktree 격리** 필수):
- 각 worktree 는 HEAD 에서 만들어지므로 S0 커밋이 먼저다. 생성 직후 `cd <WT> && uv sync` 그리고 실제 샘플 링크: `for p in /Users/illi/illy-projects/hwp2md/tests/fixtures/*; do n=$(basename "$p"); [ -e "<WT>/tests/fixtures/$n" ] || ln -s "$p" "<WT>/tests/fixtures/$n"; done` (`tests/fixtures/**` 는 gitignored 라 링크가 커밋되지 않는다. 커밋 전 `git -C <WT> status --porcelain tests/fixtures` 가 비어 있는지 확인)
- 서브에이전트 프롬프트의 PROJECT_ROOT 는 worktree 경로, research.md·inventory.md 는 메인 트리 절대경로로 준다.
- 묶음이 끝나면 orchestrator 가 단계 번호 순서로 각 worktree diff 를 적용하고 메인 트리에서 그 묶음의 검증 명령을 돌린 뒤 단계별로 커밋한다.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)

> 2026-10-23 승인: Q1~Q6, Q9, Q10 기본값. Q7 MIT, Q8 기본 변환 + 고지 (사용자가 직접 선택).

- [x] Q1. 오늘 추가된 실제 샘플 때문에 기존 테스트 6개가 이미 실패합니다. 기존 테스트의 샘플 집합 정의만 기존 5개 파일로 고정해도 될까요(단언은 그대로, 새 샘플은 새 E2E 가 다룸)? — 기본값: 예 (S2)
- [x] Q2. 머리말·꼬리말은 본문에서 빼고 "건너뜀"으로 보고합니다(HWPX 기존 동작과 통일). 문서 앞/뒤에 한 번 출력하는 쪽을 원하시나요? — 기본값: 제외 + 보고
- [x] Q3. 단락 중간 그림의 HWP 5.0/HWPX 배치 차이(feature-reference §12.2①)를 이번에 맞출까요? — 기본값: 이번엔 맞추지 않고 한계 문서에 기록
- [x] Q4. 표 칸 안 그림도 `img_NNN`·`그림 N` 번호를 소비해 기존 문서의 이미지 번호가 밀릴 수 있습니다. — 기본값: 번호 소비(문서 순서)
- [x] Q5. 수식 → LaTeX 에 python-hwpx 의 변환기(Apache-2.0, 약 670줄)를 저장소에 복사(벤더링)하고 NOTICE 에 출처를 적습니다. — 기본값: 벤더링. 실패 시 원문 스크립트 코드 스팬
- [x] Q6. 배포용 문서 복호화의 AES 를 순수 파이썬으로 직접 구현합니다(의존성 0, 느릴 수 있음). `cryptography` 선택 의존성을 원하시나요? — 기본값: 순수 파이썬
- [x] Q7. 프로젝트에 LICENSE 가 없습니다. 벤더링 코드와 호환되는 라이선스를 정해야 합니다. — 기본값: MIT (`LICENSE` 파일은 S23, `pyproject.toml` 의 `license = "MIT"` 한 줄은 orchestrator 가 S23 커밋에 포함)
- [x] Q8. 배포용 문서(복사·인쇄 제한 문서)를 기본으로 변환합니다. README 에 작성자 의도 확인 고지를 넣습니다. — 기본값: 기본 변환 + 고지
- [x] Q9. 메모·숨은 설명은 작성자 정보가 들어 있을 수 있어 기본 제외하고 개수만 보고합니다. — 기본값: 제외 + 보고
- [x] Q10. 표·그림 캡션을 개체 뒤 일반 단락으로 출력합니다(기존 샘플의 단락 수가 늘 수 있음). — 기본값: 출력

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| worktree 에 실제 샘플(gitignored)·미추적 `design/`·`feature-reference.md` 가 없음 | 높음 | S0 커밋, worktree 마다 샘플 심볼릭 링크(§6) |
| HWP 5.0 글상자 LIST_HEADER 레벨·OLE BinData 오프셋·목록 ID 기준이 추정값 | 중 | S12·S15 가 실제 샘플 개수로 확인, 다르면 단계 안에서 고치고 로그에 결론 |
| 실제 OLE 샘플이 구형 차트 | 중 | `chart_legacy` 보고가 정답(§3 PARTIAL 아님) |
| 순수 파이썬 AES 가 실제 배포용 샘플에서 30초 초과(브라우저 모드는 더 느림) | 중 | S17 측정. 넘으면 RESULT 에 기록하고 Q6 대안을 결정 기록에 남김 |
| 벤더링 저장소 접근 불가(프록시) | 낮음 | S6 PARTIAL 대체 동작 |
| 렌더 변경이 기존 실제 샘플 출력을 의도치 않게 바꿈 | 중 | S1 기준선 비교, 바뀐 값은 구조 탐색 개수로만 설명 허용(§1-D) |
| 실제 샘플 문서 내용이 로그·커밋·보고로 새어 나감 | 중 | 로그는 gitignored `logs/` 에 개수만, E2E 사본은 `tests/e2e/screenshots/`(gitignored), C19 검사 |
| 병렬 묶음 합칠 때 같은 합성기 파일 충돌 | 낮음 | 묶음 안에서 합성기 파일이 겹치지 않게 배치(§6 대조) |
| HWPML DTD 처리에서 XXE 회귀 | 낮음 | 리터럴 엔티티만 허용 + 기존 파서 옵션 + 거부 테스트(S11) |
| 브라우저 모드 E2E 가 CDN 접근 실패 | 중 | 기존 정책대로 해당 케이스 skip 사유 기록, C4 허용 범위 |

## 9. 예상 비용
- 예상 단계 수: 27 (S0 은 orchestrator) · 서브에이전트 호출: 약 32회(재시도 5회 여유) · 주 모델: implementer opus 20단계, test-writer sonnet 3단계, runner haiku 2단계, reviewer sonnet·scribe haiku 1단계
- 병렬 묶음 5개(P1 4·R1 3·R2 3·R3 3·P3 4)로 순차 대비 약 14단계 분량 단축
