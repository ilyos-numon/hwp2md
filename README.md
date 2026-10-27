# hwp2md
[![PyPI](https://badgen.net/pypi/v/hwp2markdown)](https://pypi.org/project/hwp2markdown/)
[![Python](https://badgen.net/pypi/python/hwp2markdown)](https://pypi.org/project/hwp2markdown/)
[![CI](https://github.com/ilyos-numon/hwp2md/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ilyos-numon/hwp2md/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/hwp2markdown/month)](https://pepy.tech/projects/hwp2markdown)
[![Total downloads](https://static.pepy.tech/badge/hwp2markdown)](https://pepy.tech/projects/hwp2markdown)
[![GitHub stars](https://badgen.net/github/stars/ilyos-numon/hwp2md)](https://github.com/ilyos-numon/hwp2md/stargazers)
[![License: MIT](https://badgen.net/badge/license/MIT/blue)](https://github.com/ilyos-numon/hwp2md/blob/main/LICENSE)

**한국어** · [English](https://github.com/ilyos-numon/hwp2md/blob/main/README.en.md)

**한글(HWP·HWPX·HWPML) 문서를 한컴오피스 없이, 제목·표·그림이 살아 있는 Markdown 으로.**
LLM·RAG 입력, 검색, 버전 관리에 바로 쓸 수 있는 텍스트를 CLI·파이썬 라이브러리·로컬 웹 화면에서 같은 엔진으로 만든다.

![hwp2md 변환 화면 — 왼쪽은 렌더링된 미리보기, 오른쪽은 Markdown 원문](https://raw.githubusercontent.com/ilyos-numon/hwp2md/main/docs/images/hero-convert.png)

> 화면의 문서는 시연용으로 코드에서 만든 가상의 공고문이다. 실제 기관·문서와 관계없다.

## 바로 써 보기

| 방법 | 누구에게 | 명령·링크 |
|---|---|---|
| 브라우저 | 설치 없이 지금 바로 | https://ilyos-numon.github.io/hwp2md/ → "변환 도구 열기" (파일은 브라우저 밖으로 나가지 않음, 첫 준비 약 1분) |
| uvx | [uv](https://docs.astral.sh/uv/) 가 있는 사람, 설치 없이 한 번 | `uvx --from hwp2markdown hwp2md 문서.hwp -o out/` |
| Homebrew | macOS·Linux | `brew install ilyos-numon/tap/hwp2md` |
| 실행 파일 | Python 이 없는 Windows·macOS·Linux | [최신 릴리스](https://github.com/ilyos-numon/hwp2md/releases/latest) 에서 파일 하나 내려받기 |
| pip·uv·pipx | 파이썬 라이브러리·웹 미리보기까지 | `pip install 'hwp2markdown[web]'` (또는 `uv tool install`·`pipx install`) |

설치하면 명령은 `hwp2md` 다. PyPI 배포 이름은 `hwp2markdown` 이다 (PyPI 의 `hwp2md` 는 다른 프로젝트). 실행 파일 종류·경고 해제·체크섬 확인은 [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md#12-실행-파일-python-필요-없음) 에 있다.

<details>
<summary>브라우저 체험판·소개 페이지 화면</summary>

![hwp2md 소개 페이지 — "한글 문서를 Markdown으로 꺼냅니다"](https://raw.githubusercontent.com/ilyos-numon/hwp2md/main/docs/images/landing.png)

</details>

## 30초 예시

제목·표·그림이 든 짧은 공문(`demo.hwpx`)을 변환한다.

```console
$ hwp2md demo.hwpx -o out/
✓ demo.hwpx → out/demo.md
  단락 5개 · 표 1개 · 제목 5개 · 이미지 1개
  이미지: out/demo_images/ (1 files)
```

`out/demo.md` 앞부분:

```markdown
# 2026년도 가상 문서 디지털 전환 지원사업 공고

이 문서는 hwp2md 시연을 위해 만든 가상의 공고문입니다. 실제 기관·사업과 관계없습니다.

## 1. 사업 개요

종이와 한글 문서로 관리하던 업무 자료를 검색 가능한 형태로 바꾸는 기관을 지원합니다.

| 구분 | 내용 |
|---|---|
| 지원 규모 | 총 10억 원 (기관당 최대 5천만 원) |
| 지원 기간 | 2026. 3. ~ 2026. 12. |
| 신청 방법 | 온라인 접수 (붙임 서식 작성 후 제출) |

## 2. 추진 절차

신청서 접수 후 서면 심사를 거쳐 지원 대상을 선정합니다.

![그림 1](demo_images/img_001.png)
```

그림은 `out/demo_images/img_001.png` 로 따로 저장되고 Markdown 에서 상대 경로로 이어진다.

## 왜 hwp2md 인가

- **한컴오피스가 필요 없다.** 순수 파이썬이고 의존성은 `olefile`·`lxml` 두 개다.
- **구조를 지킨다.** 개요 수준은 `#` 제목으로, 표는 Markdown 표로, 그림은 파일로 꺼내 제자리에 링크한다. 각주·미주, 수식(LaTeX), 번호·글머리표 목록, 하이퍼링크도 옮긴다. 제목 단위로 나누기 좋아 RAG 청킹에 유리하다.
- **파일이 밖으로 나가지 않는다.** CLI·라이브러리·`hwp2md serve` 는 내 컴퓨터에서 변환하고, 브라우저 체험판은 브라우저 안에서 변환한다.
- **어디서 돌려도 같은 결과.** CLI·라이브러리·웹 화면이 같은 엔진을 쓰고, 세 곳의 출력은 바이트 단위로 같다 (E2E 로 비교).
- **무료, MIT 라이선스.**

## 무엇을 변환하나

| 입력 형식 | |
|---|---|
| HWP 5.0 (`.hwp`) | 지원. 배포용(복사·인쇄 제한) 문서 포함 |
| HWPX (`.hwpx`) | 지원 |
| HWPML 2.x (`.hml`) | 지원 |
| HWP 3.0 이하 | 미지원 (HWP 파일이 아닌 것으로 판정) |
| DRM 적용·비밀번호 문서 | 거부 (이유를 구분해 알려 줌) |

포맷은 확장자가 아니라 파일 내용으로 판별한다.

| 요소 | 결과 |
|---|---|
| 본문 단락·제목 계층 | 단락, 개요 1~6수준 → `#`~`######` |
| 표 | GFM 표. 셀 안 여러 단락은 `<br>`, 병합 셀은 원 셀에 텍스트(덮인 칸은 빈 칸) |
| 그림 | 원본 바이트 그대로 `<이름>_images/img_001.png` … 로 저장. 표 칸·글상자 안 그림 포함 |
| 각주·미주 | `[^1]` 참조 + 문서 끝 정의 |
| 수식 | 한글 수식 → LaTeX `$…$` (근사, 실패하면 원문을 코드로) |
| 목록·링크·캡션·글상자 | Markdown 목록, `[글자](https://…)`, 캡션 단락, 글상자 안 글 |
| OOXML 차트 | 저장된 값으로 데이터 표 |
| 머리말·꼬리말·메모·숨은 설명 | 일부러 빼고 개수만 보고 |

못 하는 것: 글자 서식(굵게·글꼴·색), 구형 차트 데이터, WMF/EMF 그림 변환, 쪽 번호 같은 필드 값 재계산. 목록 번호와 수식은 근사다. 꺼내지 못한 요소는 조용히 사라지지 않고 "건너뜀: 머리말·꼬리말 2개" 처럼 종류별 개수로 알려 준다. 요소별 상태·이유·우회 방법은 [docs/extraction-limits.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/extraction-limits.md) 에 있다.

## 사용법

CLI:

```bash
hwp2md 문서.hwp -o out/        # out/문서.md (+ out/문서_images/)
hwp2md --version
```

종료 코드는 0 성공 · 1 변환 오류 · 2 파일 없음 · 3 HWP 가 아니거나 지원하지 않는 문서다.

로컬 웹 미리보기 (extra `web` 필요):

```bash
hwp2md serve                  # http://localhost:8770 , 인터넷 없이 동작
hwp2md serve --port 8771 --no-browser
```

파일을 끌어다 놓으면 미리보기와 Markdown 이 나란히 나오고, ZIP 으로 `.md` 와 그림을 한 번에 받는다. 화면은 한국어·영어를 지원한다.

라이브러리:

```python
from hwp2md import convert

result = convert("문서.hwp", "out/")
print(result.markdown)
```

디스크에 쓰지 않는 `convert_bytes`, 예외 종류, 건너뜀 보고, 서버 모드와 브라우저 모드 차이는 [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md) 에 있다.

## 개인정보·보안

- 웹 서버는 업로드를 메모리에서 바로 변환하고 디스크에 쓰지 않는다. 브라우저 모드는 파일 바이트를 서버로 보내지 않는다. 두 가지 모두 E2E 테스트로 확인한다.
- 메모·숨은 설명은 작성자 정보가 있을 수 있어 내용을 출력하지 않는다. 미리보기는 문서 내용을 외부 입력으로 보고 HTML 을 이스케이프한다.
- `hwp2md serve` 는 `localhost` 용 도구다. 인증이 없으므로 외부에 공개하지 않는다. 자세한 설계는 [docs/system-overview.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/system-overview.md) 에 있다.

## 자주 묻는 질문

**한컴오피스(한/글)가 없어도 되나요?**
네. 공개된 파일 형식 문서를 바탕으로 파이썬이 직접 파일을 읽는다.

**DRM·비밀번호가 걸린 문서는요?**
풀지 않고 거부한다. CLI 는 종료 코드 3 과 함께 `DRM protected`·`password protected` 를 구분해 알려 준다. 한/글에서 암호를 해제하거나 반출 승인된 파일로 다시 변환한다. 배포용(복사·인쇄 제한) 문서는 공개된 절차로 변환하니, 작성자의 의도와 사용 권한을 확인하자.

**HWP 3.0 이하 문서는요?**
지원하지 않는다. 한/글에서 열어 HWP 5.0(`.hwp`) 또는 HWPX 로 다른 이름으로 저장한 뒤 변환한다.

**실행 파일을 열면 경고가 떠요.**
실행 파일은 코드 서명이 없다. macOS 는 `xattr -d com.apple.quarantine hwp2md-macos-arm64`, Windows SmartScreen 은 "추가 정보 → 실행" 을 누른다. 같은 릴리스의 `SHA256SUMS` 로 파일을 확인할 수 있다.

**PyPI 의 `hwp2md` 와 같은 건가요?**
아니다. PyPI 의 `hwp2md` 는 다른 프로젝트다. 이 프로젝트는 `hwp2markdown` 으로 설치하고, 명령과 import 이름이 `hwp2md` 다.

**인터넷 없이 쓸 수 있나요?**
네. CLI·라이브러리·`hwp2md serve` 는 인터넷 없이 동작한다. 브라우저 체험판(GitHub Pages)과 `serve` 의 "브라우저 안에서만 처리" 모드는 처음에 Pyodide 를 CDN 에서 받으므로 인터넷이 필요하다.

## 기여·버그 신고

- 변환 결과가 이상하면 [버그 신고 양식](https://github.com/ilyos-numon/hwp2md/issues/new?template=bug_report.yml)으로 알려 주세요. 실제 문서에는 개인정보·내부 정보가 있을 수 있으니, 가능하면 문제를 재현하는 짧은 문서를 새로 만들어 첨부해 주세요.
- 기능 제안·질문은 [Issues](https://github.com/ilyos-numon/hwp2md/issues) 에 남겨 주세요. 개발 환경과 테스트 명령은 [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md#8-개발) 에 있다.

## 문서

- [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md) — 상세 사용법 (설치, CLI, 웹 미리보기, 라이브러리, 지원 범위 표)
- [docs/extraction-limits.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/extraction-limits.md) — 추출 한계 (요소별 상태·이유·대안)
- [docs/feature-reference.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/feature-reference.md) — 기능 명세 (웹 API·오류 체계 포함)
- [docs/system-overview.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/system-overview.md) — 내부 구조 (모듈·데이터 흐름·보안·테스트)
- [docs/decisions.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/decisions.md) — 결정 기록 (날짜와 이유)
- [docs/releasing.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/releasing.md) — 릴리스 절차
- [CHANGELOG.md](https://github.com/ilyos-numon/hwp2md/blob/main/CHANGELOG.md) — 변경 기록

## 로드맵

- [ ] RAG 옵션: `--split section` (제목 단위 분할), `--meta` (목차·표 수·이미지 경로·원본 해시 JSON)
- [ ] 폴더 일괄 변환
- [ ] 병합 셀 개선 (`--table html` 로 rowspan/colspan 보존)
- [ ] 공공기관 샘플 20개 품질 비교표
- [x] 각주·미주, 배포용 문서, HWPML, PyPI·Homebrew·OS별 실행 파일 배포

## 하지 않는 것

- 역변환 (md → hwp)
- 서식 완벽 재현 (글꼴·색상)

## 라이선스

- hwp2md 는 [MIT 라이선스](https://github.com/ilyos-numon/hwp2md/blob/main/LICENSE)로 배포한다.
- `src/hwp2md/equation/eqedit.py`·`tokens.py` 는 python-hwpx 에서 가져온 코드로 Apache License 2.0 을 따른다. 출처·커밋·변경 사실은 [NOTICE](https://github.com/ilyos-numon/hwp2md/blob/main/NOTICE) 에 있다.
- 본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.
