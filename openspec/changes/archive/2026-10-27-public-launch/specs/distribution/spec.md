## ADDED Requirements

### Requirement: 패키지 메타데이터는 찾을 수 있는 정보를 담는다
`pyproject.toml` 은 `[project.urls]` 에 Homepage·Repository·Issues·Changelog 를, `keywords` 와 `classifiers` 에 HWP·Markdown·한국어 관련 항목을 담아야 한다(SHALL). License 분류자는 쓰지 않는다(`license` 표현식과 충돌).

#### Scenario: wheel 메타데이터
- **WHEN** wheel 을 빌드하고 METADATA 를 읽는다
- **THEN** `Project-URL` 4줄, `Classifier: Natural Language :: Korean`, `Classifier: Topic :: Text Processing :: Markup :: Markdown` 이 있다

### Requirement: README 는 PyPI 에서도 그림과 링크가 열린다
`README.md` 의 코드 블록 밖 그림·링크는 `https://` 절대 주소 또는 `#` 앵커여야 한다(SHALL). 맨 위에 PyPI 버전·CI·다운로드·라이선스 배지, 브라우저 체험 링크, 영문 요약 절이 있다.

#### Scenario: 상대 링크 검사
- **WHEN** 코드 블록을 뺀 README 에서 `](` 뒤 주소를 모은다
- **THEN** `https://` 나 `#` 으로 시작하지 않는 주소가 0개다

### Requirement: 변경 기록을 남긴다
저장소 루트 `CHANGELOG.md` 는 릴리스된 각 버전의 절(`## [X.Y.Z] - YYYY-MM-DD`)을 가져야 한다(SHALL).

#### Scenario: 0.1.1 릴리스
- **WHEN** `__version__` 이 `0.1.1` 이다
- **THEN** `CHANGELOG.md` 에 `## [0.1.1]` 과 `## [0.1.0]` 절이 있다
