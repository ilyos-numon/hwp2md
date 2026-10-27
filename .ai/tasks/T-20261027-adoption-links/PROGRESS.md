# PROGRESS — T-20261027-adoption-links

> append-only.

---

## [2026-10-27 20:23] S1 | orchestrator | START
- 한 일: 배지·uvx 안내·프로젝트 링크
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 3bd34e6 [record] STATE 브랜치 main

## [2026-10-27 20:25] S1 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): README.en.md README.md src/hwp2md/web/static/about.html src/hwp2md/web/static/index.html src/hwp2md/web/static/js/i18n-about.js src/hwp2md/web/static/js/i18n.js tests/e2e/test_project_links.py 
- 커밋: e5547db [T-20261027-adoption-links][plan] 사용 현황 배지·uvx 안내·프로젝트 링크, 0.1.3

## [2026-10-27 20:29] S1 | implementer(opus) | DONE
- 한 일: README·README.en 배지 2·uvx 안내, about·convert 바닥글 GitHub·PyPI 링크(ko/en aria), test_project_links 8, e2e 150 exit=0, unit 820, sanitize OK
- 변경 파일(미커밋, .ai 제외): CHANGELOG.md README.en.md README.md src/hwp2md/__init__.py src/hwp2md/web/static/about.html src/hwp2md/web/static/index.html src/hwp2md/web/static/js/i18n-about.js src/hwp2md/web/static/js/i18n.js tests/e2e/test_project_links.py 
- 커밋: e5547db [T-20261027-adoption-links][plan] 사용 현황 배지·uvx 안내·프로젝트 링크, 0.1.3
- 다음: S2

## [2026-10-27 20:29] S2 | orchestrator | DONE
- 한 일: __version__ 0.1.3, CHANGELOG [0.1.3], check_dist --tag v0.1.3 OK, twine PASSED
- 변경 파일(미커밋, .ai 제외): CHANGELOG.md README.en.md README.md src/hwp2md/__init__.py src/hwp2md/web/static/about.html src/hwp2md/web/static/index.html src/hwp2md/web/static/js/i18n-about.js src/hwp2md/web/static/js/i18n.js tests/e2e/test_project_links.py 
- 커밋: e5547db [T-20261027-adoption-links][plan] 사용 현황 배지·uvx 안내·프로젝트 링크, 0.1.3
- 다음: main push → CI·Pages → v0.1.3 태그

## [2026-10-27 20:33] S3 | orchestrator | DONE
- 한 일: CI 40496517738·Pages 40496485419 success, v0.1.3 Release 40496761182 build·publish success, pip 설치·uvx 모두 hwp2md 0.1.3, 실제 사이트 PyPI 링크 1
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 834f244 [T-20261027-adoption-links][s1] 배지·uvx 안내·프로젝트 링크, 버전 0.1.3
- 다음: 완료
