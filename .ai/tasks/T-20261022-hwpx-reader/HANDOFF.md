# HANDOFF — T-20261022-hwpx-reader

> 세션을 의도적으로 끊을 때(limit 임박, 네트워크 불안, 모델 교체) 작성.
> 비정상 종료 시에는 이 파일이 없을 수 있다 → STATE.md + PROGRESS.md 끝 항목으로 복구한다.

- 작성: 2026-10-22 14:45 · 작성자: orchestrator(fable) — scribe 호출은 한도 임박으로 생략, orchestrator가 직접 작성
- 끊는 이유: limit (사용자 요청으로 중단)

## 지금까지 (프로젝트 전체 맥락)
- **DONE·main 병합**: `T-20261022-stack-cli-smoke` — 스택(Python 3.11+, uv, olefile, ruff, mypy strict, pytest)·CLI `hwp2md INPUT -o OUT_DIR`·HWP 5.0 본문 단락 → Markdown. RESULT: `.ai/tasks/T-20261022-stack-cli-smoke/RESULT.md`
- **DONE·main 병합**: `T-20261022-table-markdown` — 블록 모델(`blocks.py` Paragraph/Table), 표 파서(`hwp5/body.py`), `read_blocks`/`render_blocks`, `ConvertResult.table_count`, CLI 2행 `단락 N개 · 표 M개`. 단위 64 + E2E 11 통과. 실제 샘플(표 8개) 검증. RESULT: `.ai/tasks/T-20261022-table-markdown/RESULT.md`
- **main HEAD**: e13ae70 (전체 테스트 75 passed)
- **현재 태스크 `T-20261022-hwpx-reader`**: HWPX(zip/XML, lxml) 리더 추가. 상태 = **S0 플랜 작성 중, 플랜 미완성**.

## 현재 태스크 진행 상태
- 완료 단계: 없음 (S0 플랜 단계 진행 중)
- 진행 중 단계: S0 — planner(fable)는 14:52에 PLAN.md(633행)를 완성했으나 한도 오류로 보고만 유실. 17:50 재개 후 orchestrator가 셀프체크 10/10 확인 → 사용자 승인 대기.
- 작업 트리 상태: 브랜치 `ai/T-20261022-hwpx-reader` (main에서 분기), 미커밋은 `.ai/` 기록만. 코드 변경 없음.
- planner에게 준 프롬프트 전문: `.ai/tasks/T-20261022-hwpx-reader/planner-prompt.md` (재호출 시 그대로 사용)

## 이어받는 사람이 처음 5분에 할 일
1. `cd /Users/illi/illy-projects/hwp2md && git status && git log --oneline -5` — 브랜치가 `ai/T-20261022-hwpx-reader`인지 확인
2. `.ai/STATE.md` 읽기 (상태 PLANNING)
3. `.ai/tasks/T-20261022-hwpx-reader/PROGRESS.md` 마지막 2개 항목 읽기
4. **분기**:
   - `PLAN.md`가 있으면 → `/plan` 절차 2번부터: plan-standard 10개 셀프체크 → `checkpoint.sh S0 "planner(fable)" DONE ...` → STATE AWAITING_APPROVAL → `git add .ai && git commit -m "[T-20261022-hwpx-reader][plan] ..."` → 사용자에게 단계 목록·§7 질문 제시
   - `PLAN.md`가 없으면 → `planner-prompt.md` 내용을 그대로 planner(fable, 실패 시 opus)에게 보내 재호출 → 위와 동일
5. 사용자 승인("기본값" 등) 뒤 `/implement`

## 주의
- **환경 제약(메모리 `workflow-gotchas-macos.md`에도 기록)**: macOS에 `timeout` 명령 없음(runner 블록은 Bash 도구 timeout 사용) · zsh에서 `${PIPESTATUS}` 비어 나옴(`cmd > log 2>&1; echo "exit=$?"`) · scribe는 `.ai/` 밖 못 씀(docs/README는 implementer) · scribe에 STATE 경로를 `.ai/STATE.md`로 명시(전 태스크에서 태스크 폴더에 잘못 썼음) · `ls -la <file>`·`out/` 읽기가 권한 거부되는 경우 있음(`[ -e ]`, mktemp 사용)
- 검증 항목에 "삭제 줄 0" 같은 과도한 제약을 넣지 않는다 (전 태스크 S2에서 implementer가 함수 중복 정의로 우회 → RETRY 유발)
- `tests/fixtures/**`는 전부 gitignore (README.md·.gitkeep만 추적). HWPX 샘플 3개는 `tests/fixtures/unsupported/hwpx/`, HWP 5.0 샘플 2개는 `tests/fixtures/*.hwp`, HWP 3.0 1개는 `unsupported/hwp3/`. 지원되면 hwpx 폴더를 `tests/fixtures/hwpx/`로 옮기는 단계가 플랜에 들어갈 예정
- lxml은 아직 미설치. 의존성 추가(`uv add lxml`, dev `lxml-stubs`)는 pyproject·uv.lock이 orchestrator 전용이라 orchestrator가 직접 하는 단계로 플랜에 적도록 지시했다
- 설계 방향(planner 프롬프트에 있음): `convert.py`에서 내용 기반 포맷 감지(OLE → hwp5, zip+mimetype/section0.xml → hwpx) → 공통 블록 → 공통 렌더. 확장자로 판단하지 않음
- 다음 후보 태스크(HWPX 뒤): 이미지 추출(BinData), 제목 계층, 각주, --split/--meta
