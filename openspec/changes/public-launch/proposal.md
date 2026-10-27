# Proposal — public-launch

## Why

hwp2md 는 PyPI(`hwp2markdown` 0.1.0)에 게시됐지만 저장소가 비공개이고, 설치하지 않고 써 볼 방법이 없으며, PyPI 페이지에는 저장소·문서 링크와 분류 정보가 없다. 사람들이 찾고 바로 써 보게 하려면 (1) 설치 없는 브라우저 체험, (2) 공개 저장소, (3) 검색되는 메타데이터와 README, (4) 그것을 반영한 새 릴리스가 필요하다. 저장소를 공개하기 전에 과거 커밋에 남은 실제 샘플 변환 결과물과 내부 메모를 이력에서 지워야 한다.

## What Changes

- 변환 화면에 "정적 사이트" 설정(meta 태그)을 더한다. 설정이 있으면 브라우저 모드로 고정하고 모드 스위치를 숨긴다. 설정이 없으면(`hwp2md serve`) 지금과 같다.
- `scripts/build_pages.py` 가 `dist-pages/` 에 GitHub Pages 용 정적 사이트(소개 `index.html`, 변환 `convert.html`, `static/`, `pkg/hwp2md.zip`)를 만든다. 모든 내부 경로는 상대 경로라 `/hwp2md/` 같은 하위 경로에서 동작한다.
- `.github/workflows/pages.yml` 이 main push 때 정적 사이트를 Pages 에 배포한다(비공개 저장소면 건너뜀).
- `pyproject.toml` 에 `[project.urls]`·keywords·classifiers 를 더하고, README 맨 위에 배지·체험 링크·30초 데모·영문 요약을 두며 그림·링크를 절대 URL 로 바꾼다. `CHANGELOG.md`, 이슈 템플릿을 더한다.
- 사용자 승인 게이트 뒤에서 `git filter-repo` 로 이력을 정리하고(백업 bundle 선행), force-push 후 저장소를 공개로 바꾼다.
- 버전 0.1.1 을 PyPI 에 게시한다.
- `docs/launch/` 에 한국어 홍보 초안 2개를 둔다(게시는 하지 않음).

## Non-Goals

- Docker 이미지, 텔레메트리·사용 추적, 외부 커뮤니티 실제 게시, 저장소 이름 변경, 서버 모드를 공개 호스팅하는 것, `hwp2md serve` 동작 변경, 커스텀 도메인.

## Impact

- 코드: `src/hwp2md/web/static/js/app.js`, `src/hwp2md/web/static/pyodide-runner.js`, `src/hwp2md/__init__.py`(버전), 새 `scripts/build_pages.py`
- 테스트: 새 `tests/unit/test_build_pages.py`, `tests/e2e/test_pages_site.py`
- 설정·문서: `pyproject.toml`, `.gitignore`, `CLAUDE.md`, `.github/**`, `README.md`, `CHANGELOG.md`, `docs/releasing.md`, `docs/decisions.md`, `docs/launch/*`
- 저장소: 이력 재작성(모든 커밋 SHA 변경, 태그 v0.1.0 재지정), 공개 전환, Pages 활성화
