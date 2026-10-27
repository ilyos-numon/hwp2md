# PLAN — T-20261027-adoption-links 사용 현황 배지·uvx 안내·프로젝트 링크, 0.1.3

> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)  · 사용자 지시 "Discussion 여는거 하지마. 나머지 다해"
> 작은 문서·링크 변경이라 OpenSpec 없이 진행 (동작 변경 없음: 외부 요청 0, 기존 문구·id 불변)

## 범위
- IN: README.md·README.en.md 배지 2개(누적 다운로드 static.pepy.tech/badge/hwp2markdown, GitHub stars badgen.net/github/stars/ilyos-numon/hwp2md) + `uvx --from hwp2markdown hwp2md 문서.hwp -o out/` 한 줄 실행 안내, 소개·변환 화면 바닥글에 GitHub·PyPI 텍스트 링크(ko/en), E2E, CHANGELOG [0.1.3], __version__ 0.1.3, v0.1.3 릴리스
- OUT: GitHub Discussions, 화면 안 외부 이미지·숫자, CLI 변경
## 성공 기준
- C1 tests/unit failed 0 · C2 tests/e2e exit=0 (logs/e2e.log) · C3 lint(--no-cache)·mypy 0 · C4 README relative 링크 0 · C5 sanitize OK · C6 build_pages OK·check_dist --tag v0.1.3 OK · C7 CI 6 job success · C8 PyPI 0.1.3 설치 `hwp2md 0.1.3` · C9 Pages 재배포 후 실제 사이트 바닥글 링크 보임
## 실패 기준
- 같은 오류 2회 수정 실패 → BLOCKED · 기존 E2E 단언 변경 필요 → BLOCKED
## 단계
- S1 implementer(opus): README·README.en·about.html·index.html·i18n.js·i18n-about.js·tests/e2e/test_project_links.py (새, 성공: 링크 href·텍스트 ko/en, 실패 경로: 외부 요청 0 가드)
- S2 orchestrator: CHANGELOG·버전 0.1.3, 검증 C1~C6, main push, CI·Pages 확인
- S3 orchestrator: v0.1.3 태그(사용자 "다 해" 지시), Release·PyPI 확인, RESULT
