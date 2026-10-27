# Design — public-launch

## Context

- 웹 화면(`src/hwp2md/web/static`)은 모든 자원을 `/static/...` 절대 경로로 부르고, `pyodide-runner.js` 는 `fetch("/pkg/hwp2md.zip")`, `app.js` 는 `/api/convert`·`/api/zip`·`/about#limits` 를 쓴다. `fonts.css` 도 `url("/static/vendor/fonts/...")` 다. GitHub 프로젝트 Pages 는 `https://ilyos-numon.github.io/hwp2md/` 하위 경로라 절대 경로가 깨진다.
- 런타임 zip 은 `hwp2md.web.app.build_runtime_zip()` 이 만든다(web 제외 hwp2md + olefile 순수 파이썬, 고정 날짜). 정적 빌드는 이 함수를 그대로 쓴다.
- GitHub Pages 는 무료 플랜에서 공개 저장소만 된다. 그래서 Pages 활성화·배포는 공개 게이트 뒤다.
- 과거 커밋에 실제 샘플 변환 결과(`.ai/tasks/*/screenshots/*.md`, 이후 추적 해제됨)와 실제 샘플 구조 조사표(`inventory.md`, 아직 추적 중)가 있고, 모든 `CLAUDE.md` 판에 내부 메모 절이 있다. 금지 패턴 적중은 과거 PROGRESS·테스트 판의 루프백 IP 리터럴과 버전 문자열 1개다.
- PyPI Trusted Publisher 는 `ilyos-numon/hwp2md` · `release.yml` · environment `pypi` 에 묶여 있다. 저장소 이름은 바꾸지 않는다.

## Goals / Non-Goals

Goals: 설치 없는 브라우저 체험 URL, 공개 저장소, 검색되는 PyPI·GitHub 메타데이터, 0.1.1 릴리스, 홍보 초안.
Non-Goals: 서버 모드 공개 호스팅, 텔레메트리, Docker, 실제 커뮤니티 게시, 커스텀 도메인, 저장소 재생성.

## Decisions

1. **원본 HTML 은 그대로 두고 빌드에서 경로를 바꾼다**: `serve` 화면을 건드리지 않으려고 HTML·CSS 경로 치환은 `build_pages.py` 가 한다. JS 의 동작 차이(브라우저 모드 고정, zip 주소, 소개 페이지 주소)만 meta 태그로 켠다. meta 가 없으면 기존 코드 경로 그대로라 `serve` 회귀가 없다. 대안(별도 정적 전용 HTML 복제)은 화면 두 벌 유지 비용 때문에 기각.
2. **모든 사이트 내부 경로는 상대 경로**: base path 를 빌드 인자로 받지 않는다. 상대 경로라 `/hwp2md/` 에서도, 로컬 테스트의 임의 하위 경로에서도 같은 결과물이 동작한다.
3. **첫 화면은 소개 페이지**: `index.html` = 소개(about), `convert.html` = 변환. 링크 `href="/"` → `convert.html`, `href="/about"` → `index.html`.
4. **빌드 검증 내장**: 치환 후 HTML·CSS 에 루트 절대 경로가 남으면 빌드 실패. 원본이 바뀌어 치환 규칙이 빠지는 회귀를 막는다.
5. **Pages 배포는 Actions 공식 액션**: `actions/configure-pages`·`actions/upload-pages-artifact`·`actions/deploy-pages`. `if: ${{ !github.event.repository.private }}` 로 비공개일 때 건너뛴다. 빌드는 `uv sync --locked` 후 `uv run python scripts/build_pages.py --out dist-pages`.
6. **이력 재작성 = git filter-repo, 제자리 실행 + bundle 백업**: 25커밋 규모. `--invert-paths` 로 경로를 지우고 `--replace-text` 로 내부 메모 절·금지 패턴 문자열을 바꾼다. annotated 태그는 filter-repo 가 새 커밋으로 다시 쓴다. 배포물에 들어가는 경로(src, README, LICENSE, NOTICE, pyproject)는 규칙 대상이 아니므로 v0.1.0 의 해당 객체 해시는 그대로다.
7. **원격 정리**: main 과 태그만 force-push 하고 원격의 다른 브랜치는 지운다. PR 이 있으면 GitHub 의 `refs/pull/*` 가 옛 커밋을 붙잡으므로 PR 0건일 때만 진행한다.
8. **0.1.1 은 게이트 뒤 태그 push**: README 의 절대 그림 주소가 공개 뒤에야 열리고, 재작성 전 태그를 만들면 SHA 가 바뀐다.

## Risks / Trade-offs

- GitHub 은 force-push 뒤에도 옛 커밋을 SHA 로 한동안 보여 줄 수 있다 → 비공개 기간에 SHA 가 외부에 알려진 적이 없으므로 수용. Actions 실행 기록의 커밋 링크는 남는다(로그에 샘플 내용 없음).
- jsDelivr 장애 시 체험 화면이 동작하지 않는다 → 상태 표시에 오류를 보이고 CLI 설치 안내 링크(README)를 소개 페이지에서 제공.
- Pyodide 첫 로드 약 1분 → 소개 페이지·README 에 안내.
- 소개 페이지 문구 일부가 `hwp2md serve` 기준(서버 모드 설명)이다 → 사실과 어긋나지 않으므로 이번에는 그대로 둔다.
