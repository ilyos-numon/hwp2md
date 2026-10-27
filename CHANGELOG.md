# Changelog

이 프로젝트의 주요 변경을 기록한다. 형식은 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 를 따르고, 버전은 [Semantic Versioning](https://semver.org/) 을 따른다.

## [0.1.3] - 2026-10-27

### Added
- README 에 설치 없이 한 줄로 실행하는 방법(`uvx --from hwp2markdown hwp2md 문서.hwp -o out/`)과 누적 다운로드·GitHub star 배지.
- 소개·변환 화면 바닥글에 GitHub·PyPI 링크 (외부 이미지 없이 텍스트 링크만).

## [0.1.2] - 2026-10-27

### Added
- 웹 화면(변환·소개) 영어 지원: 브라우저 언어로 자동 선택, 헤더 KO/EN 전환, `?lang=ko|en`. README 영어판(README.en.md).

### Fixed
- 소개 페이지를 글꼴이 캐시된 상태로 다시 열면 제목이 두 번 보이던 문제.

## [0.1.1] - 2026-10-27

### Added
- 브라우저 체험 사이트 (https://ilyos-numon.github.io/hwp2md/): 설치 없이 브라우저 안의 Pyodide 로 변환하며 파일을 서버로 보내지 않는다. `scripts/build_pages.py` 가 같은 화면을 정적 사이트로 빌드하고 GitHub Pages 로 배포한다.
- 패키지 메타데이터: 프로젝트 URL 4개(Homepage·Repository·Issues·Changelog), 분류자, 키워드.
- README 배지(PyPI·Python·CI·Downloads·License), 체험 링크, 30초 데모, 영문 요약(English).

### Changed
- README 의 그림과 저장소 파일 링크를 절대 URL 로 바꿔 PyPI 페이지에서도 열리게 했다.
- 패키지 description 을 영문으로 바꿨다.

## [0.1.0] - 2026-10-27

### Added
- 첫 PyPI 릴리스 (배포 이름 `hwp2markdown`, 명령·import 이름 `hwp2md`).
- HWP 5.0·HWPX·HWPML 을 제목 계층·표·이미지·각주·수식(LaTeX)이 살아 있는 Markdown 으로 바꾸는 CLI 와 라이브러리(`convert`, `convert_bytes`).
- 로컬 웹 미리보기 `hwp2md serve` (extra `web`): 서버 모드와 브라우저 안에서만 처리하는 Pyodide 모드.
- 배포용 문서 변환, DRM·비밀번호 문서 거부, 변환하지 못한 요소의 건너뜀 보고.

[0.1.3]: https://github.com/ilyos-numon/hwp2md/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/ilyos-numon/hwp2md/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/ilyos-numon/hwp2md/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ilyos-numon/hwp2md/releases/tag/v0.1.0
