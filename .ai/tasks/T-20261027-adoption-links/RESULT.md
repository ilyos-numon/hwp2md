# RESULT — T-20261027-adoption-links

결론: README 에 누적 다운로드·GitHub star 배지와 `uvx` 한 줄 실행 안내를 넣고, 소개·변환 화면 바닥글에 GitHub·PyPI 텍스트 링크(ko/en)를 넣어 v0.1.3 으로 PyPI·Pages 에 배포했다. Discussions 는 사용자 지시로 하지 않았다.

| 기준 | 결과 | 근거 |
|---|---|---|
| C1 unit | PASS | 820 passed |
| C2 e2e | PASS | 150 passed, logs/e2e.log exit=0 (새 test_project_links.py 8) |
| C3 lint·mypy | PASS | ruff --no-cache 0, mypy no issues |
| C4 README 상대 링크 | PASS | README.md·README.en.md 모두 [] |
| C5 sanitize | PASS | OK (22 patterns) |
| C6 build_pages·check_dist | PASS | build OK, check_dist --tag v0.1.3 OK, twine PASSED 2 |
| C7 CI | PASS | run 40496517738 6 job success, Pages 40496485419 success |
| C8 PyPI 0.1.3 | PASS | Release 40496761182 build·publish success, 새 venv 설치·uvx 모두 `hwp2md 0.1.3` |
| C9 실제 사이트 링크 | PASS | https://ilyos-numon.github.io/hwp2md/ 에 PyPI 링크 1 |

- 스크린샷: screenshots/s1-footer-en.png, screenshots/s1-convert-footer-en.png
- 남은 점: pepy 배지는 집계가 시작되기 전까지(보통 하루) 깨진 그림으로 보일 수 있다. 화면에는 외부 이미지를 넣지 않았다(오프라인·전송 없음 약속 유지).
