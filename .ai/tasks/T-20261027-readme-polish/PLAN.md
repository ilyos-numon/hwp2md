# PLAN — T-20261027-readme-polish README 재구성 (GitHub 첫인상)

> 상태: (현재: DONE) · 사용자 지시 "Github 에 잘 정리해서 올려. 다른 사람들이 잘 이해하고 좋아할 만한 readme 로". 문서·이미지만 변경(동작 변경 없음) → OpenSpec 없이.

## 범위
- IN: README.md·README.en.md 전면 재구성, docs/images/ 새 V3 스크린샷(합성 문서로 촬영), 쓰지 않게 된 옛 이미지 삭제, docs/ 상세 문서로 옮길 내용은 기존 docs 파일에 링크(새 문서가 필요하면 docs/usage.md 1개까지)
- OUT: 코드·테스트·워크플로우 변경, PyPI 재배포(이번엔 GitHub 만), GitHub 설정 변경
## 성공 기준
- C1 두 README 상대 링크 0 (코드 블록 제외) · 그림은 raw.githubusercontent 절대 URL
- C2 README 첫 화면(상단 40줄 안)에 한 줄 소개·배지·스크린샷·"바로 써 보기" 5가지 방법
- C3 두 README `## ` 절 구성 동일
- C4 tests/unit·tests/e2e/test_dist_package.py·test_project_links.py 통과, sanitize OK
- C5 GitHub main 에서 README 이미지 200
## 단계
- S1 implementer(opus): 스크린샷 촬영 + README 2개 재작성 + 필요 시 docs/usage.md
- S2 orchestrator: 검증·main push·이미지 URL 200 확인
