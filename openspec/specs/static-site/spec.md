# static-site Specification

## Purpose
TBD - created by archiving change public-launch. Update Purpose after archive.

## Requirements

### Requirement: 정적 빌드는 하위 경로에서 동작하는 사이트를 만든다
`scripts/build_pages.py --out <DIR>` 는 `<DIR>` 에 `index.html`(소개 페이지), `convert.html`(변환 화면), `static/`(웹 정적 자원 사본, HTML 제외), `pkg/hwp2md.zip`(`build_runtime_zip()` 과 같은 바이트), `.nojekyll` 을 만들어야 한다(SHALL). 생성된 HTML·CSS 에는 `/` 로 시작하는 내부 경로(`"/static/`, `"/api/`, `href="/"`, `href="/about`, `url("/`)가 하나도 없어야 하며, 남아 있으면 스크립트는 종료 코드 1 로 실패한다.

#### Scenario: 정상 빌드
- **WHEN** 빈 임시 폴더를 `--out` 으로 주고 스크립트를 실행한다
- **THEN** 종료 코드 0, 위 5개 경로가 존재하고 `pkg/hwp2md.zip` 바이트가 `hwp2md.web.app.build_runtime_zip()` 결과와 같다

#### Scenario: 절대 경로가 남은 원본
- **WHEN** 원본 HTML 에 치환 규칙에 없는 `src="/x.js"` 가 들어 있는 상태로 빌드한다
- **THEN** 종료 코드 1 이고 표준 오류에 파일 이름과 `absolute-path` 가 나온다

### Requirement: 정적 사이트 변환은 브라우저 안에서만 일어난다
`convert.html` 은 Pyodide(jsDelivr CDN)만 외부에서 받고, 문서 바이트를 어떤 호스트에도 보내지 않아야 한다(SHALL). 사이트 자체 자원 요청은 모두 사이트 기준 경로(예: `/hwp2md/`) 아래로만 간다.

#### Scenario: 하위 경로에서 합성 HWPX 변환
- **WHEN** 빌드 결과를 로컬 정적 서버의 `/hwp2md/` 아래에 두고 `convert.html` 에서 합성 HWPX 를 넣는다
- **THEN** `body[data-state="done"]` 이 되고, POST 요청은 0건, 사이트 호스트 요청은 모두 `/hwp2md/` 로 시작하며, 그 밖의 외부 요청은 `cdn.jsdelivr.net` 뿐이다

#### Scenario: CDN 차단
- **WHEN** `cdn.jsdelivr.net` 요청을 차단한 상태로 `convert.html` 을 연다
- **THEN** `#mode-status[data-state="error"]` 가 되고, 파일을 넣으면 `body[data-state="error"]` 와 오류 문구가 보인다

### Requirement: main push 가 Pages 에 배포한다
`.github/workflows/pages.yml` 은 main push 와 수동 실행에서 정적 빌드를 만들어 GitHub Pages 에 배포해야 한다(SHALL). 저장소가 비공개이면 job 은 건너뛴다(실패하지 않음).

#### Scenario: 공개 저장소 main push
- **WHEN** 공개 저장소 main 에 push 한다
- **THEN** `Pages` 워크플로우가 성공하고 `https://ilyos-numon.github.io/hwp2md/` 와 `.../pkg/hwp2md.zip` 이 HTTP 200 이다
