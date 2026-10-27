# Tasks

## 1. 공개 전 설정

- [x] 1.1 `.gitignore` 에 `dist-pages/` 추가, `CLAUDE.md` 내부 메모 절 삭제, GitHub 저장소 description·homepage·topics 설정

## 2. 정적 사이트

- [x] 2.1 `app.js`·`pyodide-runner.js` 에 정적 사이트 meta 설정(브라우저 모드 고정, zip 주소, 소개 주소)을 더한다
- [x] 2.2 `scripts/build_pages.py` 와 단위 테스트를 쓴다
- [x] 2.3 정적 사이트 E2E(하위 경로 변환 성공, CDN 차단 실패, serve 회귀)를 쓰고 돌린다

## 3. 발견성

- [x] 3.1 `pyproject.toml` 에 urls·keywords·classifiers·description 을 더한다
- [ ] 3.2 README 배지·체험 링크·30초 데모·영문 요약·절대 URL, `CHANGELOG.md`, 버전 0.1.1, releasing·decisions 문서
- [ ] 3.3 `.github/workflows/pages.yml` 과 이슈 템플릿
- [ ] 3.4 `docs/launch/` 홍보 초안 2개

## 4. 공개

- [ ] 4.1 게이트 전 전체 검증과 브랜치 CI
- [ ] 4.2 [사용자 승인] bundle 백업 → main 병합 → filter-repo → 이력 검사 → force-push → 공개 전환
- [ ] 4.3 Pages 활성화와 배포 확인

## 5. 릴리스와 마감

- [ ] 5.1 v0.1.1 태그 push 와 PyPI 게시 확인
- [ ] 5.2 최종 E2E(로컬 전체 + 실제 Pages)
- [ ] 5.3 리뷰와 RESULT 기록
