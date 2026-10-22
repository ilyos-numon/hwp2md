# RESULT — T-20261022-stack-cli-smoke hwp2md 스택 확정 + CLI 스캐폴드 + HWP 5.0 스모크 변환

> 작성: scribe · 2026-10-22 13:06 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 됨: `uv sync` 후 `uv run hwp2md input.hwp -o out/`로 HWP 5.0 본문 단락이 `out/input.md`로 나온다. 없는 파일(exit 2), HWP 아님(exit 3), 암호화 플래그(exit 3)는 한 줄 에러로 거절된다.
- 안 됨: 표·이미지·각주·제목 계층·HWPX. 실제 공공기관 HWP 샘플로는 검증하지 않았다.
- 바로 쓸 수 있는가: 합성 fixture 기준으로 동작 확인됨. 실제 한컴 파일은 미검증. 샘플을 `tests/fixtures/*.hwp`에 넣으면 E2E가 자동 실행된다.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| S1 | `uv sync && hwp2md --version` | ✅ | stdout `hwp2md 0.1.0`, exit 0 — `logs/s6-runner.log` |
| S2 | 합성 HWP → Markdown | ✅ | stdout 2줄 `✓ sample.hwp → <D>/out/sample.md` / `  단락 3개`, exit 0, 내용 `테스트 문서 제목\n\n본문 단락 1\n\n본문 단락 2\n` 일치 — `logs/s6-runner.log`, `screenshots/sample.md` |
| S3 | 없는 파일 | ✅ | stderr `hwp2md: error: file not found: /nonexistent/x.hwp`, exit 2 — `logs/s6-runner.log` |
| S4 | HWP 아닌 파일 | ✅ | stderr `hwp2md: error: not an HWP 5.0 file: <D>/fake.hwp`, exit 3, `.md` 미생성 — `logs/s6-runner.log` |
| S5 | E2E | ✅ 5 passed / 1 skipped | `5 passed, 1 skipped`, failed 0, error 0, `exit=0` — `logs/e2e.log` |
| S6 | unit·ruff·format·mypy | ✅ | unit 35 passed; ruff check 통과; ruff format 통과(S6 시점 12 files, 리뷰어 최종 14 files); mypy `Success: no issues found in 8 source files` — `logs/s6-runner.log`, `logs/s5-*.log` |
| S7 | 익명화 검사 | ✅ | `sanitize-check: OK (22 patterns)` — reviewer 13:05 직접 실행 |
| S8 | CLAUDE.md 명령 블록 | ✅ | "채워 넣을 것" 0건, TEST_CMD/E2E_CMD/E2E_ONE이 PLAN §4.7과 일치 — reviewer 13:05 확인 |
| S9 | 결정 기록 | ✅ | `## 2026-10-22` 3건 — `docs/decisions.md` |
| S10 | README 실행 방법 | ✅ | `uv run hwp2md` 1건 — `README.md` |

- 게이트: `gate.sh` GATE PASS 6/6 (orchestrator 13:05 실행).
- 범위: OUT 키워드(lxml/hwpx/footnote) 매치 없음. 표 로직 없음. `HWPTAG_TABLE` 상수 정의만 있음.

## 변경 요약
- 커밋 범위: `308f1fb..c601668` (11 commits). [s9]·[done] 커밋은 이후 추가 예정.
- 추가/수정 파일: 22개 (+1454 / -10). 핵심: `src/hwp2md/cli.py`, `src/hwp2md/hwp5/records.py`, `src/hwp2md/hwp5/reader.py`, `src/hwp2md/convert.py`, `tests/synth_hwp5.py`, `tests/e2e/test_cli_convert.py`. (`src/.gitkeep` → `src/hwp2md/py.typed` 이름 변경 1건 포함)
- 새 의존성: 런타임 `olefile>=0.46`. dev `pytest>=8`, `ruff>=0.6`, `mypy>=1.10`. 잠금 파일 `uv.lock` (15 packages).
- 새 환경변수: `ILLY_SHOT_DIR` (E2E 증거 저장 위치, 선택. 기본 `tests/e2e/screenshots`).

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → pass (35 passed, fail 0)
- E2E: `uv run pytest tests/e2e -q` → pass (5 passed, 1 skipped, fail 0, exit 0). 케이스:
  - `test_convert_synthetic_success` — 종료 0, stdout 2줄, 파일 내용 == 기대 Markdown
  - `test_convert_uncompressed_variant` — 비압축 fixture도 같은 결과
  - `test_missing_input_exit_2` — 없는 파일, exit 2, stderr `file not found:`
  - `test_not_hwp_exit_3` — HWP 아님, exit 3, `.md` 미생성
  - `test_encrypted_flag_exit_3` — 암호화 플래그, exit 3, `unsupported HWP file`
  - `test_real_fixture_converts` — skipped (실제 샘플 없음, 빈 parametrize)

## 실행 방법
```bash
uv sync
uv run hwp2md input.hwp -o out/
uv run pytest tests/unit tests/e2e -q
```

## 못 한 것 / 알려진 문제
- 실제 공공기관 HWP 샘플 검증 없음 — 합성 fixture만 사용 — 라이선스 확인 전까지 샘플 커밋 금지. 샘플을 `tests/fixtures/*.hwp`에 넣으면 `test_real_fixture_converts`가 자동 실행 (PLAN §7-3).
- 표 셀·머리말 단락이 본문에 섞여 나올 수 있음 — level/CTRL_HEADER 미처리, 이번 범위에서 허용 — 표 태스크에서 처리 (PLAN §8).
- 깨진 OLE 파일의 OSError는 변환되지 않아 일반 예외(exit 1)로 나옴 — reader 범위 밖 — 후속 태스크에서 NotHwpFileError로 매핑 제안.
- 표·이미지·각주·제목 계층·HWPX 미구현 — OUT 범위 — 후속 태스크.

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- Stage 7 담당을 scribe(haiku)에서 implementer(opus)로 변경. 이유: scribe 정의가 `.ai/` 밖 파일 쓰기를 금지. 범위·내용·검증은 불변 (PLAN 변경 이력 기록).
- 설정·문서 단계(S1·S2·S7)는 runner/reviewer를 생략하고 orchestrator가 검증 명령을 직접 실행.
- macOS에 `timeout` 명령이 없어 S8 runner 실행 블록에서 `timeout 600` 제거, Bash 도구 timeout 사용.
- S6 implementer 1차 호출이 session rate limit으로 시작 직후 종료. 같은 프롬프트로 재호출.

## 후속 제안 (별도 태스크로)
- 표(HWPTAG_TABLE) → Markdown 표 (다음 태스크 후보)
- 이미지 추출(BinData)
- HWPX 파싱(lxml, 그 태스크에서 의존성 선언)
- 제목 계층(DocInfo 스타일)
- 실제 샘플 20개 품질 비교표 (README MVP)
- GitHub Actions, LICENSE (라이선스 결정 후)

## 비용
- 서브에이전트 호출: 20회 (fable 1 / opus 6 / sonnet 7 / haiku 6). PROGRESS 기준, 이 scribe 호출 제외.
- 재시도: 3회 (S6 implementer rate limit 1, S7 담당 재배정 1 — 실패 아님, S8 runner exit 127 1) · 차단: 0회
