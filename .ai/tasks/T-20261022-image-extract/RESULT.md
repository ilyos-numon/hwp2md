# RESULT — T-20261022-image-extract hwp2md 이미지 추출 (HWP 5.0·HWPX)

> 작성: scribe · 2026-10-23 00:15 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- HWP 5.0·HWPX 본문 이미지를 `out/<stem>_images/img_NNN.<ext>`로 추출하고, Markdown 제자리에 `![그림 N](<stem>_images/img_NNN.<ext>)` 상대 링크를 남긴다. CLI 2행에 `이미지 K개`, 3행에 저장 폴더를 출력한다.
- 실제 HWP 5.0 이미지 샘플이 없어 HWP 5.0 경로는 합성 fixture와 스펙 교차 확인으로만 검증했다. 표 셀·머리말 안 이미지는 제외.
- 바로 사용 가능 (브랜치 `ai/T-20261022-image-extract`, main 병합 대기). 실행: `uv run hwp2md <file.hwp|.hwpx> -o <outdir>`

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| S1 | 합성 이미지 fixture 두 포맷 동일 Markdown·파일 (`test_cli_image.py` 13건) | PASS | `uv run pytest tests/e2e/test_cli_image.py -q`, reviewer PASS (PROGRESS S8·S9) |
| S2 | E2E 전체 | PASS 46/46 | `uv run pytest tests/e2e -q` → 46 passed, `.ai/tasks/T-20261022-image-extract/logs/e2e.log` (PROGRESS S8) |
| S3 | 단위 회귀 없음 | PASS 240 passed | `uv run pytest tests/unit -q` (플랜 기대 216 이상) |
| S4 | 린트·포맷·타입 | PASS | ruff check·format --check OK, mypy 18 source files OK |
| S5 | 브라더 HWPX 이미지 추출 | PASS | 2행 `이미지 1개`, sha256 `f9be5b73bc6b32a79f15e52fd850b24c95203459756867104a6c297dbfc58632` 일치, 링크 1줄 |
| S6 | 이미지 없는 실제 샘플 4개 출력 불변 | PASS | 4개 샘플 2·3행 기대값 일치, `_images` 폴더 0개 |
| S7 | 이미지 없는 합성 입력 바이트 불변 | PASS | `test_synth_hwp5.py`·`test_synth_hwpx.py` sha256 테스트 통과 |
| S8 | 기존 E2E 수정 범위 | PASS | 정규식 1줄씩 (`test_cli_convert`·`test_cli_heading`·`test_cli_hwpx`) |
| S9·S10 | 플랜 §2 나머지 행 | PASS (보고 기준) | 플랜 원문 행 상세 확인 필요. reviewer VERDICT PASS "§2 S1~S10 PASS" (PROGRESS S9) |
| - | sanitize-check | OK | orchestrator 보고 (로그 경로 확인 필요) |

## 변경 요약
- 커밋 범위: `18d054d..51416b6` (11 commits, `git log main..HEAD` 기준)
- 추가/수정 파일: 59개 (+4249 / -85) — 핵심: `src/hwp2md/images.py`, `src/hwp2md/hwp5/body.py`, `src/hwp2md/hwpx/bindata.py`, `src/hwp2md/hwpx/body.py`, `src/hwp2md/convert.py`, `src/hwp2md/cli.py`
- 새 의존성: 없음 (플랜상 Pillow 등 금지, pyproject.toml 변경 금지. diff 개별 확인 필요)
- 새 환경변수: 없음

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → pass, 240 passed
- E2E: `uv run pytest tests/e2e -q` → pass, 46 passed, 0 failed
  - test_cli_image — 합성 HWP5·HWPX 두 포맷 같은 Markdown·같은 파일
  - test_cli_image — 같은 이미지 재참조 시 파일 1개 재사용
  - test_cli_image — 표 셀 안 이미지 제외
  - test_cli_image — 누락 BinData 참조 시 링크·폴더 처리
  - test_cli_image — 실제 HWPX 샘플 브라더 sha256 일치

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md
uv run hwp2md "tests/fixtures/hwpx/브라더 공공기관 보고서 양식.hwpx" -o out/
# 2행: 이미지 1개 / 3행: out/브라더 공공기관 보고서 양식_images/ (1 files)
```

## 못 한 것 / 알려진 문제
- 실제 HWP 5.0 이미지 샘플 없음 — 합성 fixture + 스펙 교차 확인만 — 이미지 있는 실제 HWP 5.0 샘플 확보 필요
- 표 셀 안 이미지 제외 — 셀 내 인라인 렌더 없음 — 후속 태스크
- 머리말·꼬리말·글상자·각주 안 이미지 제외 — 플랜 OUT 범위
- 포맷 변환 없음 (WMF/EMF 등 원본 바이트 그대로 저장)
- 증거 md의 이미지 폴더는 `screenshots/`에 미복사 (별도 png로 복사됨)
- PARTIAL 1건 (S1 implementer 1차: mypy 2건 범위 밖) — RETRY 1회로 해소. BLOCKED 0건

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- §7 기본값 10개 적용 (ec3b8a9 approved) — 사용자 자동 승인 지시에 따름
- S1 Block Union 확장으로 `hwp5/body.py`·`hwpx/body.py`의 `else`→`elif isinstance(b, Table)` 각 1줄 쓰기 범위 추가 — Image가 Table로 오인되는 것 방지
- planner fable 한도로 이후 implementer를 opus로 사용 (planner는 S0에서 완료, 재호출 없음)
- 플랜 테스트 개수 오기: 일부 parametrize 미산입 (synth 플랜 33 → 실제 38 passed)

## OpenSpec
- `openspec validate` 통과
- 아카이브: `openspec/changes/archive/2026-10-23-image-extract/`
- main spec: `openspec/specs/image-extraction/`

## 후속 제안 (별도 태스크로)
- 이미지 있는 실제 HWP 5.0 샘플 추가 (BIN_DATA·gso 실제 바이트 검증)
- 샘플 20개 품질 비교표
- pip 배포·CI
- 각주 안 이미지 (머리말·각주 태스크)

## 비용
- 서브에이전트 호출: 15회 (fable 1 / opus 7 / sonnet 7 / haiku 0, scribe 본 호출 제외)
- 재시도: 1회 (S1 RETRY) · 차단: 0회
