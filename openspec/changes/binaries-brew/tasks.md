# Tasks

## 1. 빌더와 빌드 스크립트

- [x] 1.1 `docs/decisions.md` 에 빌더 비교(PyInstaller·Nuitka·PyApp)와 결정, 출처 URL 을 남긴다
- [x] 1.2 `scripts/build_binary.py` 와 `packaging/pyinstaller/hwp2md_entry.py` 를 쓰고 로컬 macOS arm64 실행 파일을 빌드한다

## 2. Homebrew formula 생성기

- [x] 2.1 `scripts/update_formula.py` 와 단위 테스트 `tests/unit/test_update_formula.py`, 탭 README 원본 `packaging/homebrew/README.md` 를 쓴다

## 3. 문서와 버전

- [x] 3.1 README·README.en 설치 절(brew·실행 파일·Gatekeeper/SmartScreen), `docs/releasing.md`, `CHANGELOG.md` 0.1.4, `__version__` 0.1.4

## 4. 릴리스 워크플로우

- [x] 4.1 `.github/workflows/release.yml` 에 `binaries` matrix job 과 `github-release` job 을 더한다

## 5. 실행 파일 E2E

- [x] 5.1 `tests/e2e/test_binary_smoke.py` 를 쓰고 로컬에서 E2E·단위·lint·타입 검사를 통과시킨다

## 6. 릴리스

- [ ] 6.1 main 반영, CI 성공 확인, 태그 `v0.1.4` push, Release 자산 5개와 PyPI 0.1.4 확인
- [ ] 6.2 `ilyos-numon/homebrew-tap` 공개 저장소를 만들고 `Formula/hwp2md.rb`·`README.md` 를 push 한다

## 7. 배포물 검증과 기록

- [ ] 7.1 Release 자산 체크섬·실행 파일 스모크, `brew install`·`brew test`, 다른 OS 러너 스모크 로그를 확인한다
- [ ] 7.2 리뷰와 RESULT 기록
