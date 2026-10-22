# RESULT — T-20261022-hwpx-reader HWPX(zip/XML) 입력 지원: 본문 단락·표 → 같은 Markdown

> 작성: scribe · 2026-10-22 18:18 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
1. `uv run hwp2md input.hwpx -o out/`로 HWPX도 HWP 5.0과 같은 규칙의 Markdown(단락·표·병합 셀 빈 칸·셀 내 `<br>`)이 나온다. 포맷은 확장자가 아니라 내용으로 판별하므로 `.hwp` 확장자의 HWPX도 변환된다.
2. 안 된 것: 이미지·각주·제목 계층은 미지원이고 머리말·도형 텍스트는 의도적으로 무시한다. 1행 표(헤더만 있는 표)와 목차 셀 렌더링에 품질 문제가 있다.
3. 지금 바로 쓸 수 있다. 실제 공공 양식 HWPX 샘플 3개(표 1·31·8개)에서 변환과 E2E가 통과했다. 샘플이 3개뿐이라 넓은 품질 검증은 후속 태스크다.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| S1 | 합성 HWPX(단락만) 변환 | ✅ | `uv run pytest tests/e2e/test_cli_hwpx.py -q -k synthetic_success` · `logs/e2e.log` (21 passed) · 최종 리뷰 PASS |
| S2 | 합성 HWPX 표·병합 셀 | ✅ | `-k "table_success or merged_table"` 2 passed · `screenshots/table_hwpx.md`, `screenshots/merged_hwpx.md` |
| S3 | `.hwp` 확장자의 HWPX 내용 변환 | ✅ | `-k hwp_extension` 1 passed |
| S4 | HWP 5.0·HWPX 같은 Markdown | ✅ | `-k same_markdown` 1 passed + `tests/unit/test_cross_format.py` 5 passed · `logs/s4-test.log` |
| S5 | zip이지만 HWPX 아님 exit 3 · 깨진 XML exit 1 | ✅ | `-k "not_hwpx or malformed"` 2 passed |
| S6 | 실제 HWPX 샘플 3개 | ✅ | `-k real_hwpx` 3 passed · `logs/s4-real.log` (단락·표 = (1,1) (80,31) (32,8)) · 구분선 1/31/8 · `screenshots/` 실제 샘플 .md 3개 |
| S7 | E2E 전체 | ✅ | `uv run pytest tests/e2e -q` → 21 passed, failed 0, error 0 · `logs/e2e.log` (exit=0) |
| S8 | 단위 전체 | ✅ | `uv run pytest tests/unit -q` → 113 passed (기존 64 + 신규 49) · `logs/s4-test.log` |
| S9 | 린트·포맷·타입 | ✅ | ruff All checks passed · format 30 files formatted · mypy Success: 14 source files |
| S10 | 보안 파서(엔티티) | ✅ | `-k entity` 2 passed · `logs/s3-entity.log` |
| S11 | 익명화 검사 | ✅ | `sanitize-check.sh` OK (22 patterns) |
| S12 | 결정 기록·문서 | ✅ | `docs/decisions.md` 날짜 항목 8건 · README HWPX 4회 · `tests/fixtures/README.md` `hwpx/` 1회 |

## 변경 요약
- 커밋 범위: `e13ae70..860ad2d` (9 commits). 이 기록의 `[s7]`·`[done]` 커밋은 orchestrator가 추가 예정.
- 추가/수정 파일: 18개 (`.ai/` 제외, +1248 / -9) — 핵심: `src/hwp2md/detect.py`, `src/hwp2md/hwpx/body.py`, `src/hwp2md/hwpx/reader.py`, `src/hwp2md/convert.py`, `tests/synth_hwpx.py`, `tests/e2e/test_cli_hwpx.py`
- 새 의존성: `lxml>=5` (런타임), `lxml-stubs` (dev)
- 새 환경변수: 없음
- 샘플 폴더 이동: `tests/fixtures/unsupported/hwpx/` → `tests/fixtures/hwpx/` (gitignore 대상, git 변경 없음)

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → 113 passed, failed 0 (기존 64 + 신규 49)
- E2E: `uv run pytest tests/e2e -q` → 21 passed, failed 0, exit 0 (기존 11 + 신규 10)
- 정적 검사: `uv run ruff check src tests`, `uv run ruff format --check src tests`, `uv run mypy src` 통과. `gate.sh` GATE PASS 6/6.
- E2E HWPX 케이스 (`tests/e2e/test_cli_hwpx.py`, 10개):
  - test_convert_hwpx_synthetic_success — 합성 단락 문서의 Markdown 일치
  - test_convert_hwpx_table_success — 표와 구분선 출력
  - test_convert_hwpx_merged_table — 병합 셀 빈 칸 처리
  - test_hwpx_content_with_hwp_extension_converts — `.hwp` 확장자 HWPX 변환
  - test_hwp5_and_hwpx_same_markdown — 같은 내용의 HWP 5.0·HWPX 출력 바이트 동일
  - test_zip_not_hwpx_exit_3 — zip이지만 HWPX 아님, exit 3
  - test_hwpx_malformed_section_exit_1 — 깨진 섹션 XML, exit 1
  - test_real_hwpx_fixture_converts[×3] — 실제 샘플 3개 exit 0, 2행 수치 일치

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md
uv sync
uv run hwp2md input.hwpx -o out/        # HWP 5.0(.hwp)도 같은 명령
uv run pytest tests/unit tests/e2e -q
```

## 못 한 것 / 알려진 문제
- 1행 표는 헤더만 있는 표가 된다. 서식 박스·목차가 1×N 표로 나온다(샘플 2에서 16개, 샘플 3에서 다수) — 제안: 1행 표를 단락으로 펴거나 빈 헤더 옵션 추가 (렌더 개선 태스크)
- 목차 셀의 `<br>` 장문이 한 셀에 몰린다 — 제안: 셀 내 단락 분리 또는 길이 처리 규칙
- 머리말·각주·이미지·도형 텍스트는 의도적으로 무시한다. HWP 5.0은 컨트롤 단락을 흘려보내고 HWPX는 무시하므로 두 포맷 결과가 다르다 — 제안: 각주 태스크에서 통일
- 이미지·각주·제목 계층·`--split`/`--meta`는 미지원 (이번 범위 밖)
- CLI 에러 문구는 `not an HWP 5.0 file:`로 유지했다. HWPX를 거절할 때도 같은 문구가 나온다 — 제안: 문구 변경 여부를 별도 결정
- 다중 섹션 HWPX의 실제 샘플이 없다(합성 테스트만 있음)
- 실제 샘플이 3개뿐이라 공공 샘플 품질 비교표는 아직 없다

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- 포맷 판별을 내용 기준으로 한다 (OLE → hwp5, zip + mimetype/section0.xml → hwpx). 이유: 확장자와 실제 내용이 어긋날 수 있다 (PLAN §4.2).
- 명시적 `rowCnt=0`은 표 생략, 속성이 없을 때만 행·셀 수로 대체한다. 플랜 의사코드 오류를 S2 리뷰에서 판정해 변경 이력에 기록. hwp5와 동일 동작.
- lxml 6.x `XMLParser`에 `resolve_entities` 속성이 없어 보안 검사를 동작 기반으로 바꿨다 (변경 이력 2026-10-22 18:04). 외부 엔티티 미해석·내부 엔티티 미확장 계약은 유지.
- §7 확인 5개는 전부 기본값으로 승인됨 (lxml-stubs, CLI 문구 유지, 컨트롤 단락 무시, lineBreak=`\n`, 샘플 폴더 이동). Stage 4b는 건너뜀.
- 실행 중 사건: planner(fable)가 PLAN 작성 직후 rate limit으로 보고가 유실됨. orchestrator가 셀프체크 10/10을 직접 수행하고 HANDOFF를 작성한 뒤 17:50에 재개했다.
- decisions.md에 남아 있던 잔여 코드 펜스 2줄을 orchestrator가 제거했다 (전 태스크 잔재 1 + 복사 범위 오류 1).

## 후속 제안 (별도 태스크로)
- 이미지 추출 (hwp5 BinData / hwpx BinData → 상대 경로)
- 제목 계층 (DocInfo·header.xml 스타일)
- 각주 (하단 참조) + 컨트롤 단락 처리 통일
- 1행 표 렌더 개선 (헤더만인 표 → 단락 또는 빈 헤더 옵션)
- `--split` / `--meta`
- 공공 샘플 20개 품질 비교표 (README MVP 항목)
- GitHub Actions, LICENSE

## 비용
- 서브에이전트 호출: 15회 (fable 1 / opus 4 / sonnet 6 / haiku 4). 이 scribe 호출(haiku 1)은 제외.
- 재시도: 0회 · 차단: 0회 (PROGRESS 집계). 주: planner rate limit 1건은 PROGRESS 메모에만 있고 재호출 없이 orchestrator가 대체했다.
