# Tasks

## 1. 기준선

- [x] 1.1 단위·E2E 기준선과 실제 샘플별 CLI 결과(종료 코드·요약 줄·Markdown)를 `.ai/tasks/T-20261023-extract-dropped/logs/` 에 기록한다
- [x] 1.2 `tests/samples.py` 에 샘플 분류(내용 기준)와 기존 샘플 5개 고정 목록을 두고, 기존 테스트의 샘플 집합 정의만 그 목록으로 바꿔 단위 실패 0 으로 되돌린다

## 2. 공통 계약

- [x] 2.1 `blocks.py`(Link·NoteRef·Math·ListInfo·Note, Paragraph·Table 필드 추가, make_paragraph·make_table·plain_text·iter_images)와 `skips.py`(SkipKind·SKIP_LABELS·SkipCounter)를 추가하고 `render.py` 를 계약대로 확장한다
- [x] 2.2 `convert.py`·`memory.py` 가 `skips` 를 받아 `ConvertResult.skipped`·`MemoryResult.skipped`·페이로드 `skipped` 를 채우게 하고, `__init__.py` docstring 에 한컴 공개 문서 문구와 새 export 를 넣는다

## 3. 보호 문서

- [x] 3.1 `DrmProtectedError`·`EncryptedDocumentError`, DRM 서명 판별, HWP 5.0 DRM 비트, HWPX 암호화 매니페스트, 오류 코드 `drm`·`encrypted` 를 구현한다

## 4. 독립 모듈

- [x] 4.1 python-hwpx 수식 변환기를 `src/hwp2md/equation/` 에 벤더링하고 `to_latex()` 와 NOTICE 를 추가한다
- [x] 4.2 `src/hwp2md/ole.py` 에 HWPX 길이 접두 벗기기·CFB 스트림 판별·OOXML 차트 캐시값 → 블록·Ole10Native 이미지 판별을 구현한다
- [x] 4.3 `src/hwp2md/hwp5/aes.py`(AES-128-ECB 복호)와 `hwp5/distdoc.py`(ViewText 레코드 복호)를 구현하고 합성 암호화 도우미로 왕복 검증한다

## 5. HWP 5.0 리더

- [x] 5.1 PARA_TEXT 위치 디코딩과 확장 컨트롤 1:1 대응으로 링크·각주/미주·수식·필드 글자를 단락 안에 두고 머리말·꼬리말·숨은 설명·메모를 건너뜀으로 보고한다
- [ ] 5.2 표 칸 그림·캡션(오인 버그 수정)·글상자·도형·묶음·OLE 차트/이미지·외부 연결/본체 없는 그림 보고를 구현한다
- [ ] 5.3 DocInfo `NUMBERING`·`BULLET` 과 문단 모양 머리 종류로 목록 정보를 붙인다
- [ ] 5.4 배포용 문서를 `ViewText` 복호화로 읽고, 실제 배포용 샘플 2개 변환을 확인한다

## 6. HWPX 리더

- [ ] 6.1 필드 하이퍼링크·각주/미주·수식·머리말/꼬리말·숨은 설명·메모 처리를 구현한다
- [ ] 6.2 칸 그림·캡션·도형 글상자(`hp:drawText`)·묶음 재귀·`hp:chart`·`hp:ole`·글맵시·양식 개체 처리를 구현한다
- [ ] 6.3 `header.xml` 의 `hh:numbering`·`hh:bullet` 과 `hh:heading` 으로 목록 정보를 붙인다

## 7. HWPML 리더

- [ ] 7.1 HWPML 판별·인코딩·안전한 엔티티 처리·본문·제목·표·그림을 구현하고 `convert.read_blocks` 에 연결한다
- [ ] 7.2 HWPML 링크·각주/미주·수식·머리말/꼬리말·캡션·글상자·목록·차트·OLE 를 구현한다

## 8. 교차 포맷

- [ ] 8.1 칸 그림 기대값을 새 규칙으로 바꾸고 요소별 세 포맷 동일성 테스트를 추가해 차이를 없앤다

## 9. CLI

- [ ] 9.1 `cli.py` 에 DRM·암호 문서 오류 문구, 건너뜀 요약 줄, 입력 도움말 문구를 넣는다

## 10. 화면

- [ ] 10.1 `src/hwp2md/web/static` 화면에 오류 코드 `drm`·`encrypted` 문구, `#skipped` 경고, 한컴 공개 문서 문구를 넣고 런타임 zip 에 새 모듈이 실리는지 확인한다
- [ ] 10.2 `design/v3` 의 `#limits`·변환 화면 `#skipped`·데모 엔진 오류 코드·한컴 문구를 갱신하고 데모 페이로드를 실제 엔진 출력으로 다시 만든다

## 11. 문서

- [ ] 11.1 `docs/extraction-limits.md` 를 새로 쓰고 `docs/feature-reference.md` 의 엔진·렌더·API·UI·오류·포맷 차이·한계 절을 갱신한다
- [ ] 11.2 README 지원 범위·로드맵·한컴 문구·배포용 문서 고지, `docs/decisions.md` 결정 기록, `LICENSE`, `NOTICE` 를 갱신한다

## 12. E2E

- [ ] 12.1 구조 탐색으로 고른 실제 샘플 요소별 E2E 와 합성 문서 CLI E2E 를 작성하고 의도적으로 바뀐 기존 E2E 기대값을 고친다
- [ ] 12.2 화면 E2E(서버·브라우저 모드 건너뜀 경고, DRM 오류 문구, design/v3 변환 화면·한계 절)와 스크린샷을 작성한다
- [ ] 12.3 E2E 전체를 실행하고 스크린샷과 로그를 저장한다

## 13. 마감

- [ ] 13.1 리뷰(diff·스크린샷), RESULT.md, STATE.md 갱신
