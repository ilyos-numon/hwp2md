# RESULT — T-20261022-table-markdown HWP 5.0 표 → Markdown 표 변환

> 작성: scribe · 2026-10-22 14:23 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 됨: HWP 5.0 문서의 표가 본문 흐름 속 제자리에 Markdown 표로 나온다 (첫 행 헤더, 병합 셀은 빈 칸, 셀 안 여러 단락은 `<br>`, `|` 이스케이프). CLI 2행이 `  단락 N개 · 표 M개`로 표 개수를 보여준다. 실제 공공 양식 샘플(표 8개, 병합 포함)에서 확인.
- 안 됨 (범위 밖, 미구현): 이미지, 각주·미주, 제목 계층, HWPX.
- 지금 바로 쓸 수 있는가: 예. HWP 5.0 문서의 본문과 표 변환에 한해 `uv run hwp2md input.hwp -o out/`로 사용 가능.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| S1 | 합성 표 fixture → Markdown 표, 위치 보존 | PASS | 2행 `  단락 2개 · 표 1개`, exit 0, 파일 == EXPECTED_MARKDOWN_WITH_TABLE (최종 리뷰 직접 실행) · `logs/s4-cli.log` |
| S2 | 병합 셀·이스케이프·`<br>` | PASS | 2행 `  단락 1개 · 표 1개`, exit 0, 파일 == EXPECTED_MARKDOWN_MERGED (최종 리뷰) |
| S3 | 표 없는 기존 fixture 불변 | PASS | 2행 `  단락 3개 · 표 0개`, exit 0, 내용 불변 · `logs/s3-test.log` |
| S4 | 실제 샘플(표 8개) | PASS | 2행 `  단락 118개 · 표 8개`, exit 0, 구분선 8, 제목용 1×1 표 존재, 병합 빈 칸 21, `<br>` 19 · `screenshots/form200005063113.md`, `logs/s3-real8.log` |
| S5 | 표 없는 실제 샘플 회귀 없음 | PASS | 2행 `  단락 47개 · 표 0개`, exit 0, `\|` 0건 · `screenshots/form210001070268.md`, `logs/s3-real0.log` |
| S6 | E2E 테스트 통과 | PASS | 11 passed, failed 0, error 0, `logs/e2e.log` exit=0 |
| S7 | unit·ruff·format·mypy 통과 | PASS | unit 64 passed (기준 55 이상), ruff OK, format 19 files, mypy Success (10 files) · `logs/s3-test.log` |
| S8 | 익명화 검사 | PASS | `sanitize-check: OK` (22 patterns) |
| S9 | 결정 기록 | PASS | `docs/decisions.md` 의 `## 2026-10-22` 5개 (기존 3 + 신규 2) |
| S10 | README 현재 지원 갱신 | PASS | "Markdown 표" 1건 (`README.md`) |

Note: 스크린샷 없음. CLI라 UI가 없고, 증거는 `screenshots/*.md` 텍스트 산출물이다.

## 변경 요약
- 커밋 범위: `6e24c12..e8f5754` (8 commits, 전부 `[T-20261022-table-markdown]` 접두). 완료 커밋 `[s7]`·`[done]`은 orchestrator가 추가 예정.
- 추가/수정 파일: 16개 (+881 / -40, `.ai` 제외) — 핵심: `src/hwp2md/blocks.py`, `src/hwp2md/hwp5/body.py`, `src/hwp2md/hwp5/reader.py`, `src/hwp2md/render.py`, `src/hwp2md/convert.py`, `tests/synth_hwp5.py`, `tests/e2e/test_cli_table.py`
- 새 의존성: 없음 (`pyproject.toml` 변경 없음)
- 새 환경변수: 없음

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → pass (64 passed, 기존 35에서 증가)
- E2E: `uv run pytest tests/e2e -q` → pass (11 passed, 기존 7에서 증가 = 합성 5 + 표 4 + 실제 샘플 2), 케이스 목록:
  - test_convert_table_success — 합성 표가 Markdown 표로 나오고 2행 문자열 일치
  - test_convert_merged_table — 병합 셀 빈 칸, 셀 내 `<br>`, `|` 이스케이프
  - test_convert_table_uncompressed_variant — 비압축 섹션에서도 표 변환
  - test_truncated_section_exit_1 — 잘린 섹션은 exit 1
  - test_real_fixture_converts[form200005063113.hwp] — 실제 샘플 표 8개
  - test_real_fixture_converts[form210001070268.hwp] — 실제 샘플 표 0개 (회귀 없음)
  - 기존 합성 5개 — 2행 기대 문자열만 `표 M개` 형식으로 갱신

## 실행 방법
```bash
uv sync
uv run hwp2md input.hwp -o out/
uv run pytest tests/unit tests/e2e -q
```

## 못 한 것 / 알려진 문제
- 다중 섹션 문서 전용 테스트 없음 — `read_blocks`는 섹션 순서대로 이어붙이지만 해당 fixture가 없음 — 다중 섹션 fixture 추가가 필요 (후속 제안 참조)
- 1열 표는 헤더 행만 있는 표가 됨 — §7-2 기본값(첫 행 = 헤더)의 결과. 실제 샘플의 제목용 1×1 표가 이 경우 — 1행 표 처리 방식 재검토 필요
- 표 자리표시자 단락에 본문 텍스트가 함께 있으면 표가 그 단락 뒤로 놓임 (§8) — 제자리 배치 정확도의 한계
- 중첩 표는 부모 셀 텍스트로 평탄화 (§7-4 기본값) — 중첩 구조 유실
- 깨진 OLE의 `OSError` 미매핑 — 전 태스크부터 이월된 알려진 문제

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- §7 질문 5개 전부 기본값으로 진행 (사용자 승인). 셀 내 단락은 `<br>`, 첫 행 헤더, CLI 2행은 항상 `표 M개` 표기, 중첩 표 평탄화, 표 밖 컨트롤 단락은 본문으로 흘림
- S2에서 implementer가 `build_paragraph`/`build_section0`을 중복 정의 → 플랜 §4.6대로 같은 함수의 제자리 확장으로 수정 (RETRY 1). 원인은 orchestrator 검증 항목 "삭제 줄 0"의 오류
- S4(CLI 1줄)·S5(문서) 단계는 runner/reviewer를 생략하고 orchestrator가 직접 검증 (1줄 변경, 문서 변경이라 판단)

## 후속 제안 (별도 태스크로)
- 이미지 추출 (BinData → 상대 경로)
- 제목 계층 (DocInfo 스타일·문단 모양)
- HWPX 지원 (lxml, `tests/fixtures/unsupported/hwpx` 샘플 3개 있음)
- 각주·미주
- `--split` / `--meta`
- 다중 섹션 fixture 추가
- 공개 샘플 20개 품질 비교표 (README MVP 항목)

## 비용
- 서브에이전트 호출: 17회 (fable 1 / opus 6 / sonnet 6 / haiku 4). PROGRESS 보고 단위 집계이며, 플랜 §9 예상 9회보다 많음. opus 6에는 S2 재요청 1건 포함.
- 재시도: 1회 (S2 implementer) · 차단: 0회
