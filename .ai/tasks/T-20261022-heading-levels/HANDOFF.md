# HANDOFF — T-20261022-heading-levels

- 작성: 2026-10-22 18:55 · 작성자: orchestrator(opus)
- 끊는 이유: 사용자 요청 (토큰 한도 초기화 대기). 사용자가 "계속해"라고 하면 이 플랜대로 진행.

## 지금까지
- 완료 단계: S0 플랜 작성·셀프체크 10/10·**승인 완료**(§7 7개 전부 기본값). PLAN 상태 APPROVED.
- 진행 중 단계: 없음. S1 미착수 (코드 변경 없음)
- 작업 트리: 브랜치 `ai/T-20261022-heading-levels`, 커밋 후 clean. main HEAD ce0a3f5에서 분기.
- 앞선 태스크 3개(stack-cli-smoke, table-markdown, hwpx-reader) DONE·main 병합. 단위 113 + E2E 21 통과.

## 이어받는 사람이 처음 5분에 할 일
1. `cd /Users/illi/illy-projects/hwp2md && git status && git log --oneline -3` — 브랜치·clean 확인
2. `.ai/STATE.md`, `.ai/tasks/T-20261022-heading-levels/PROGRESS.md` 끝 2항목 읽기
3. `/implement` 절차로 Stage 1 시작:
   - `git rev-parse HEAD > .ai/tasks/T-20261022-heading-levels/.base-s1`
   - `scripts/checkpoint.sh S1 "orchestrator" START "블록 모델 level 필드·제목 렌더·heading_count"`
   - implementer(opus)에 PLAN §1, §4 해당 절, §5 Stage 1 행 범위를 주고 위임 → runner(haiku) → reviewer(sonnet) → 커밋 `[s1]`
4. 이후 §6 순서대로 S2~S9. S7(cli.py 3줄)은 orchestrator 직접.

## 승인된 결정 (§7 기본값)
- 7-1 `Paragraph.level: int = 0` 필드 (별도 블록 아님)
- 7-2 판정은 문단 모양만 (HWP5 PARA_SHAPE 개요 비트 / HWPX paraPr heading OUTLINE). 스타일 이름 미사용
- 7-3 개요 7수준 이상 → `######` clamp
- 7-4 CLI 2행: 제목 ≥1일 때만 ` · 제목 K개` 추가, 제목은 단락 수에서 분리. 기존 E2E 정규식 2줄 수정 허용(§4.13-A)
- 7-5 제목 길이 제한 없음, 표 셀 안 개요 단락은 셀 텍스트로만
- 7-6 HWPX `hp:switch`는 `hp:case` 쪽 heading 사용
- 7-7 HWPX 양성은 합성 fixture로 검증. 실제 HWPX 양성 샘플은 사용자가 나중에 추가

## 주의
- 실제 샘플 기대값: form200005063113.hwp → (단락 100, 표 8, 제목 18). 나머지 4개 샘플은 제목 0, 기존 (단락, 표) 불변
- 합성 생성기 변경은 기존 입력에서 바이트 불변(sha256 테스트 있음). 제목 입력이 있을 때만 DocInfo/header.xml 확장
- lxml 자식 없는 요소는 falsy → `find() or` 패턴 금지 (계약 명시)
- S6에서 tests/fixtures/README.md 10행의 잘못 복사된 ``` 1줄 삭제 지시 포함
- 환경 제약(메모리 workflow-gotchas-macos): `timeout` 명령 없음, PIPESTATUS 비어 있음, scribe는 .ai/ 밖 금지·STATE 절대경로 명시, 문서 복사는 울타리 제외 행 범위
