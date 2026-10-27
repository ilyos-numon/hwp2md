# Tasks

## 1. 기준선

- [x] 1.1 추적 파일만 있는 클린 체크아웃에서 LINT·TYPECHECK·TEST·E2E 를 돌려 실제 샘플 때문에 깨지는 테스트 목록과 PyPI 이름 가용성을 기록한다

## 2. 패키지 메타데이터

- [x] 2.1 `pyproject.toml` 배포 이름 `hwp2markdown`·동적 버전·license-files·sdist 허용 목록, `uv.lock` 갱신
- [x] 2.2 `src/hwp2md/cli.py` web extra 안내를 `pip install 'hwp2markdown[web]'` 로 바꾼다

## 3. 배포물 검사

- [x] 3.1 `scripts/check_dist.py` (허용·금지 경로, 크기, `--tag`, `--patterns`) 를 쓴다

## 4. CI 용 테스트 표시

- [x] 4.1 `real_samples` 마커 등록·표시, 모듈 수준 `next()` 수집 오류 제거, web extra 안내 단언 갱신

## 5. 워크플로우

- [x] 5.1 `.github/workflows/ci.yml` (lint·typecheck·unit·e2e·dist)
- [x] 5.2 `.github/workflows/release.yml` (build·publish, environment `pypi`, Trusted Publishing)

## 6. 문서

- [x] 6.1 README 설치·한계·로드맵, `docs/feature-reference.md`·`docs/decisions.md`·`src/hwp2md/web/__init__.py` 안내 문자열 갱신
- [x] 6.2 `docs/releasing.md` 에 사용자 수동 절차와 릴리스 절차를 쓴다

## 7. 검증

- [x] 7.1 `tests/e2e/test_dist_package.py` (깨끗한 venv 설치 스모크 성공, 금지 파일·태그 불일치·패턴 적중 실패) 작성·실행
- [x] 7.2 브랜치 push 후 CI 실행 다섯 job success 확인
- [x] 7.3 diff 리뷰와 RESULT 기록

## 8. 릴리스

- [x] 8.1 사용자 승인 뒤 main 병합·태그 `v0.1.0` push·Release 워크플로우 확인·PyPI 에서 설치 확인
