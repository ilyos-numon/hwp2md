# 버려지던 HWP 요소 추출과 추출 한계 명시

## Why

지금 변환기는 본문 단락·제목·표·본문 그림만 꺼낸다. 실제 공공 문서 샘플 60여 개를 구조만 세어 본 결과(`.ai/tasks/T-20261023-extract-dropped/inventory.md`), 표 칸 안 그림 14개, 글상자 3개, 각주 3개, 수식 6개, 하이퍼링크 2개, 머리말·꼬리말 19개, 번호·글머리표 목록 26개, 차트 1개가 출력에서 사라지거나 본문에 엉뚱하게 섞인다. 배포용 문서 2개와 HWPML(XML) 문서 2개는 통째로 거부되고, 문서보안(DRM) 파일 2개는 "HWP 아님"이라는 틀린 안내를 받는다. 오픈소스·한컴 공개 스펙 조사(`research.md`)로 이 중 대부분은 구조가 확정되어 추출할 수 있고, 끝까지 못 꺼내는 것은 이유를 밝혀 사용자에게 알려야 한다.

## What Changes

- **블록 모델 확장 (하위 호환)**: 단락에 인라인 목록(`Link`, `NoteRef`, `Math`, `Image`)과 목록 정보(`ListInfo`)를, 표에 칸별 인라인(`cells`)을, 새 블록 `Note`(각주·미주 정의)를 더한다. 기존 필드·기본값·동등성은 그대로다.
- **새로 추출하는 요소 (HWP 5.0·HWPX·HWPML 공통)**: 표 칸 안 그림(GFM 칸 안 이미지 링크), 글상자·도형·묶음 개체 안 글과 그림, 표·그림 캡션, 하이퍼링크(`[글자](주소)`, http/https/mailto 만 링크), 각주·미주(`[^n]`/`[^en]` + 문서 끝 정의), 수식(한글 수식 스크립트 → LaTeX `$…$`, 실패 시 원문 코드 스팬), 번호·글머리표 목록(`- `, `1. `, 그 밖 번호는 머리 문자열), OOXML 차트 캐시값(→ 제목 단락 + Markdown 표), OLE 안 원본 이미지.
- **동작 정리**: 머리말·꼬리말은 두 포맷 모두 본문에서 빼고 "건너뜀"으로 보고한다(HWP 5.0 에서 본문에 섞이던 동작 수정). 머리말 안 그림도 같이 뺀다. 캡션 `LIST_HEADER` 를 표 칸으로 오인하던 HWP 5.0 표 파서를 고친다.
- **새 입력**: HWP 5.0 배포용 문서(한컴 공개 알고리즘으로 `ViewText` 복호화, 순수 파이썬 AES-128), HWPML 2.x(`.hml`, XML) 문서. HWPML 의 내부 DTD 리터럴 엔티티(`&nbsp;`)만 풀고 외부·파라미터 엔티티는 거부한다.
- **거부를 정확히**: DRM 래핑 파일·한컴 DRM 비트 → `DrmProtectedError`/코드 `drm`, 비밀번호 문서(HWP 5.0 비트, HWPX `manifest.xml` 암호화 항목) → `EncryptedDocumentError`/코드 `encrypted`. 둘 다 `UnsupportedHwpError` 하위라 CLI 종료 코드 3 유지.
- **"버려진 것" 보고**: `ConvertResult.skipped`, `MemoryResult.skipped`, API 페이로드 `skipped` 배열(`kind`·`label`·`count`), CLI 요약 끝 `  건너뜀: …` 한 줄, 웹 화면 경고.
- **문서화와 화면 표기**: `docs/extraction-limits.md` 에 추출하지 못하는 요소·이유·대안을 정리하고, `docs/feature-reference.md`·README 지원 범위를 갱신한다. 현재 웹 UI 와 `design/v3`(index `#limits`, app 변환 화면 경고·문서 링크·데모 페이로드)에 반영한다. 한컴 공개 문서 조건 문구를 README·UI·소스에 넣는다.
- **BREAKING (출력 변화)**: 셀 안 그림이 번호를 소비해 기존 `img_NNN` 번호가 밀릴 수 있다. HWP 5.0 머리말·각주 텍스트가 본문에서 사라진다. API 페이로드 키 `skipped` 추가, 오류 코드 `drm`·`encrypted` 추가, 비밀번호 문서의 코드가 `unsupported` → `encrypted` 로 바뀐다.

## Capabilities

### New Capabilities
- `element-extraction`: 표 칸 그림·글상자·캡션·링크·각주·수식·목록·차트·머리말 처리와 건너뛴 요소 보고, 포맷 간 동일 출력
- `hwpml-input`: HWPML 2.x 입력 판별·본문·표·그림·안전한 엔티티 처리
- `document-protection`: 배포용 문서 복호화, DRM·비밀번호 문서의 전용 거부와 안내

### Modified Capabilities
- `image-extraction`: 표 칸·글상자 안 그림을 추출하도록, 머리말·꼬리말 안 그림 제외를 두 포맷 공통으로, 건너뛴 참조를 보고하도록 바꾼다
- `memory-conversion`: 응답 페이로드에 `skipped`, 오류 코드에 `drm`·`encrypted` 를 더하고, 경로 API·CLI 호환 범위를 "추가만 허용"으로 다시 정의한다
- `web-preview`: 화면이 건너뛴 요소 경고·보호 문서 오류 문구·한컴 공개 문서 문구를 보여 준다

## Impact

- 코드: `src/hwp2md/{blocks,render,convert,memory,errors,detect,__init__}.py`, 새 `skips.py`·`ole.py`·`equation/`(Apache-2.0 벤더링)·`hwpml/`·`hwp5/{aes,distdoc}.py`, `hwp5/*`, `hwpx/*`, `cli.py`(orchestrator 전용 단계), `web/static/*`
- 프론트엔드 시안: `design/v3/{index.html,app.html,js/app.js,js/demo-engine.js,js/demo-payload.js,css/app.css}`
- 문서: `docs/extraction-limits.md`(신규), `docs/feature-reference.md`, `docs/decisions.md`, `README.md`, `NOTICE`, `LICENSE`
- 의존성: 추가 없음 (olefile·lxml 유지, AES 는 순수 파이썬)
- 브라우저 모드: `/pkg/hwp2md.zip` 에 새 순수 파이썬 모듈이 자동 포함된다
- 테스트: 합성 문서 생성기 확장(`tests/synth_hwp5.py`, `tests/synth_hwpx.py`), 신규 `tests/synth_hwpml.py`·`tests/synth_ole.py`·`tests/synth_distdoc.py`·`tests/samples.py`, 실제 샘플 E2E 는 내용 탐색으로 고르고 없으면 skip
