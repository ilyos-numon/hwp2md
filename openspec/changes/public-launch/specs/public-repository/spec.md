## ADDED Requirements

### Requirement: 공개 이력에는 실제 샘플 산출물과 내부 메모가 없다
공개되는 저장소의 모든 커밋은 `.ai/tasks/*/screenshots/*.md`, `.ai/tasks/T-20261023-extract-dropped/inventory.md`, `CLAUDE.md` 의 내부 메모 절, 익명화 금지 패턴 적중 문자열을 담지 않아야 한다(SHALL). 이력 재작성 전에 전체 저장소 bundle 백업을 저장소 밖에 만든다.

#### Scenario: 재작성 후 전체 이력 검사
- **WHEN** `git rev-list --all` 의 모든 커밋에서 금지 경로와 금지 패턴을 찾는다
- **THEN** 적중이 0건이다

### Requirement: 태그 v0.1.0 은 게시된 배포물과 같은 내용을 가리킨다
재작성 후 `v0.1.0` 이 가리키는 커밋의 `src`·`README.md`·`LICENSE`·`NOTICE`·`pyproject.toml` 객체 해시는 재작성 전과 같아야 한다(SHALL).

#### Scenario: 해시 대조
- **WHEN** 백업의 이전 `v0.1.0^{commit}` 과 새 `v0.1.0^{commit}` 에서 다섯 경로의 `git rev-parse <커밋>:<경로>` 를 비교한다
- **THEN** 다섯 쌍이 모두 같다

### Requirement: 공개 전환은 사용자 승인 뒤에만 한다
force-push 와 `gh repo edit --visibility public` 은 사용자가 승인한 뒤에만 실행해야 한다(SHALL).

#### Scenario: 승인 전
- **WHEN** 게이트 단계에서 사용자 승인이 없다
- **THEN** 원격 main SHA 와 저장소 visibility 가 바뀌지 않는다
