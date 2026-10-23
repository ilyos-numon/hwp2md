# RESULT — T-20261023-extract-dropped 버려지던 HWP 요소 추출과 추출 한계 명시

> 작성: scribe · 2026-10-23 19:21 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다.

## 결론 (3줄)
- 표 칸 그림, 글상자, 캡션, 링크, 각주, 수식, 목록, 차트(OOXML), 배포용 문서, HWPML 이 Markdown 으로 나온다. 실제 샘플 69개 중 65개 변환, 4개는 정확한 이유로 거부, 오류 0.
- 끝내 못 꺼내는 것(DRM·비밀번호 해제, 구형 차트, 필드 값 재계산 등)은 건너뜀 개수로 CLI·API·화면에 보이고, 이유는 `docs/extraction-limits.md` 에 있다.
- 지금 바로 쓸 수 있다. 단 브랜치 `ai/T-20261023-extract-dropped` 는 아직 main 에 병합하지 않았다(사용자 검토 후).

## 요소별 결과
| 요소 | 이전 | 지금 | 실제 샘플 검증 |
|---|---|---|---|
| 표 칸 안 그림 | 사라짐 | 칸 안 `![그림 N](…)`, 번호 소비 | 14/14 |
| 머리말·꼬리말 | HWP 5.0 은 본문에 섞임(스펙 위반) | 제외 + 건너뜀 보고 | 23개 보고(HWP 5.0·HWPX 19, HWPML 4), 본문 미혼입 |
| 글상자·도형·묶음 안 글/그림 | 사라짐 | 추출 | 글상자 3개, 단락 12/12 |
| 표·그림 캡션 | 사라짐(LIST_HEADER 오인) | 개체 뒤 단락 | 합성 테스트 통과 (실제 샘플 캡션 개수는 별도 집계하지 않음) |
| 하이퍼링크 | 사라짐 | `[글자](주소)` | 3/3 |
| 각주·미주 | 사라짐 | `[^n]` + 문서 끝 정의 | 각주 3/3, 미주 실제 샘플 없음(합성만) |
| 수식 | 사라짐 | LaTeX `$…$`/`$$…$$`, 실패 시 코드 스팬 | 3/3, 전체 샘플 수식 4개 중 변환 실패 0 |
| 번호·글머리표 목록 | 평문 | Markdown 목록, 칸 안은 머리 글자 | 본문 4/4, 칸 안 19/22 (나머지 3개 빈 단락) |
| 차트 (OOXML) | 사라짐 | `차트: 제목` + 데이터 표 | 실제 OOXML 샘플 없음(합성만). 실제 차트 1개는 구형 |
| OLE | 사라짐 | 원본 그림만, 나머지 건너뜀 | 실제 OLE 1개는 빈 CFB → `ole` 1 보고 (부분) |
| 배포용 문서 | 거부(종료 3) | 순수 파이썬 AES 복호 후 변환 | 2/2 종료 0 (0.12s · 0.08s) |
| HWPML 2.x | 거부(종료 3) | 입력 포맷 추가 | 2/2 종료 0 |
| DRM·비밀번호 | 일반 거부 | 정확한 거부 (`drm`·`encrypted`, 415) | DRM 2/2 종료 3. 비밀번호 실제 샘플 없음(합성만) |
| 0바이트 그림 | 빈 파일을 이미지로 셈 | 본체 없는 그림으로 보고 | 실제 BMP 1개 (E2E 에서 발견·수정) |

## 성공 기준 C1~C19
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| C1 | 단위 회귀 없음 | ✅ 813 passed, failed 0 | `logs/s26-unit.log` |
| C2 | 린트·타입 | ✅ 종료 0 | runner 보고 (S26) |
| C3 | OpenSpec valid | ✅ | `logs/openspec-validate.log` |
| C4 | E2E 전체 | ✅ 120 passed, failed 0, skipped 0 | `logs/e2e.log` |
| C5 | 실제 샘플 요소별 E2E | ✅ 18 passed, skipped 0 | runner 보고 (S26) |
| C6 | 표 칸 그림 | ✅ 14/14 | `docs/extraction-limits.md` §3 |
| C7 | 수식·각주·링크 | ✅ 수식 3/3, 각주 3/3, 링크 3/3 | 같은 문서 §3 |
| C8 | 머리말·꼬리말 | ✅ 건너뜀 보고, 본문 미혼입 | C5 테스트 안 (수치는 같은 문서 §3) |
| C9 | 배포용 2개 | ✅ 종료 0 | PROGRESS S17 |
| C10 | HWPML 2개 | ✅ 종료 0, 머리말·꼬리말 2개씩 (정정: 표 0) | PROGRESS S14·S22 |
| C11 | DRM·텍스트·HWP3 거부 | ✅ DRM 2 종료 3, 텍스트 1·HWP3 1 종료 3 | 같은 문서 §3 |
| C12 | 실제 샘플 무오류 | ✅ 69개: 65 변환, 거부 4, 종료 1 은 0개 | 같은 문서 §3 |
| C13 | API·화면 건너뜀 | ✅ pass (웹 E2E 포함) | `screenshots/s26-web-skipped.png`, `screenshots/s26-web-drm.png` |
| C14 | design/v3 반영 | ✅ pass | `screenshots/s26-design-app-skipped.png`, `screenshots/s26-design-limits.png` |
| C15 | 한컴 문구 | ✅ 5 | runner 보고 (S26) |
| C16 | 한계 문서 라벨 | ✅ 9 | runner 보고 (S26) |
| C17 | 런타임 zip 에 새 모듈 | ✅ 6 passed | runner 보고 (S26) |
| C18 | 익명화 | ✅ OK | runner 보고 (S26) |
| C19 | 실제 샘플 이름 미유출 | ✅ 0 | runner 보고 (S26) |

게이트: `logs/gate.log` → GATE PASS (PLAN APPROVED, e2e exit 0, skip/only 추가 없음, sanitize 통과).

## 변경 요약
- 커밋 범위: PROGRESS 기록 기준 `ae6ed95`(S0) … `73345bd`(S27). `e18cd70..HEAD` 커밋 31개, 121개 파일 변경 (+25220 / −337, orchestrator 집계).
- 핵심 파일: `src/hwp2md/{blocks,render,numbering,skips,convert,memory,ole,detect,errors,cli}.py`, `src/hwp2md/hwp5/{reader,body,aes,distdoc}.py`, `src/hwp2md/hwpx/`, 신규 `src/hwp2md/hwpml/`, `src/hwp2md/equation/` (벤더링), `docs/extraction-limits.md`
- 새 의존성: 없음 (순수 파이썬 AES, 수식 변환기는 벤더링). 라이선스 MIT 추가 (`LICENSE`, `NOTICE`).
- 새 환경변수: 없음

## 테스트
- 단위: `uv run pytest tests/unit -q` → 813 passed
- E2E: `uv run pytest tests/e2e -q` → 120 passed
  - 이번 태스크 신규 파일: `test_extract_real` 18 (실제 샘플 요소별), `test_extract_cli` 14, `test_web_extract` 14 (서버·브라우저·API), `test_design_v3` 4. E2E 전체 120 passed
  - 브라우저 모드 케이스도 통과 (CDN 접근 가능)

## 실행 방법
```bash
uv run hwp2md 문서.hwp -o out/      # CLI 변환 (건너뜀 요약 줄 표시)
uv run hwp2md serve                 # 웹 미리보기
```

## 못 한 것 / 알려진 문제
- 비밀번호 문서 복호화, DRM 해제 — 범위 밖(OUT). 정확한 거부만 한다.
- 구형 차트(VtChart) 데이터, OLE 미리보기, WMF/EMF 변환 — 불가 또는 부분. 이유와 대안은 `docs/extraction-limits.md` §2.
- 필드 값(쪽 번호·날짜) 재계산, 글자 서식 — 불가.
- 실제 샘플 부재: OOXML 차트, 미주, 글맵시, 양식 개체, 비밀번호 문서, HWPML 의 캡션·글상자·각주·수식·목록 — 합성 테스트로만 검증.
- 단락 중간 그림 위치: HWP 5.0 과 HWPX·HWPML 이 다르다(Q3 보류).
- 수식 LaTeX 는 토큰 치환 변환기라 전 범위를 덮지 않는다(실패 시 원문 코드 스팬).
- `tests/e2e/test_cli_convert.py:16` 에 `*.hwp` glob 이 남아 있다(현재 통과, 범위 밖).

## 결정 사항 (플랜에 없었거나 실행 중 정한 것)
- §1-D 추가 4건: ① 칸 그림 JPG 파일 기대값(S13) ② HWPML 묶음·도형 자식 순서 `[앞뒤, 상자, 타원]`(S18) ③ `_IMAGE_BYTES` 키 2개(S18) ④ `test_cli_image` 2개 케이스 갱신(S24). 모두 기존 단언 약화가 아니라 새 규칙에 맞춘 기대값 갱신.
- 표 칸 안 목록 머리 글자 계약 추가 (PLAN §4-D): 칸 안은 목록 문법을 쓰지 않고 머리 글자만 붙인다(S15 발견).
- C10 정정: HWPML 표 2개는 머리말 안이라 제외 대상 → 표 0.
- C19 기준 커밋을 `e18cd70` 으로 정정 (S22).
- 0바이트 그림 결함: 실제 샘플 E2E 에서 발견 → `image_missing` 으로 보고하도록 수정 (커밋 `ca3fd9e` 메시지 기준).
- 게이트 skip 대응: 샘플 없음 skip 을 매개변수화로 바꿈 (`73345bd`). skip 추가 없음.
- worktree 문제: S5 worktree 가 `main`(e18cd70)에서 생성돼 S3·S4 가 없었다 → 메인 트리에서 재실행. 이후 병렬 묶음은 `.claude/worktrees/` 를 쓰고 새 파일만 복사로 합쳤다. worktree venv 가 Python 3.14 로 생성돼 `uv sync --python 3.12` 로 맞췄다. reviewer 가 만든 `git add -N` 인덱스 항목은 `git reset` 으로 제거했다.
- S18 BLOCKED 는 §1-D 승인 뒤 같은 에이전트 재호출로 해제.

## 후속 제안 (별도 태스크로)
- 사용자 RESULT 검토 → `ai/T-20261023-extract-dropped` 를 main 에 병합 (OpenSpec 아카이브 `openspec/changes/archive/2026-10-23-extract-dropped/` 포함).
- `design/v3` 를 실제 백엔드에 연결 (`/plan`, `design/v3/README.md` "백엔드에 연결할 때" 1~5). 이번 태스크 범위 밖.
- 단락 중간 그림 배치 HWP 5.0·HWPX 통일 (Q3 보류).
- 구형 VtChart 차트 파싱, 실제 OOXML 차트 샘플 확보.
- `test_cli_convert.py` 의 `*.hwp` glob 정리.

## 비용
- 서브에이전트 호출: 약 45회 (조사 1·planner 1·implementer 26·test-writer 7·reviewer 8·runner 2·scribe 1, 재시도 포함 orchestrator 집계)
- 재시도: 3회 (S5 · S7 중단 · S18) · 차단: 1회 (S18, §1-D 승인 후 해제)
