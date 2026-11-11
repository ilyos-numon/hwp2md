# hwp2md 사용법 (상세)

README 에서 덜어낸 상세 사용법이다. 설치 방법 고르기·요약은 [README](https://github.com/ilyos-numon/hwp2md/blob/main/README.md), 동작의 전체 명세는 [feature-reference.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/feature-reference.md), 꺼내지 못하는 요소는 [extraction-limits.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/extraction-limits.md) 에 있다.

## 1. 설치

### 1.1 Homebrew (macOS·Linux)

```bash
brew install ilyos-numon/tap/hwp2md
hwp2md --version
```

### 1.2 실행 파일 (Python 필요 없음)

OS 에 맞는 실행 파일 하나를 내려받는다. 압축하지 않은 단일 파일이고, 링크는 항상 최신 릴리스를 가리킨다.

| OS | 실행 파일 |
|----|-----------|
| Windows x64 | [hwp2md-windows-x64.exe](https://github.com/ilyos-numon/hwp2md/releases/latest/download/hwp2md-windows-x64.exe) |
| macOS Apple Silicon (arm64) | [hwp2md-macos-arm64](https://github.com/ilyos-numon/hwp2md/releases/latest/download/hwp2md-macos-arm64) |
| macOS Intel (x64) | [hwp2md-macos-x64](https://github.com/ilyos-numon/hwp2md/releases/latest/download/hwp2md-macos-x64) |
| Linux x64 | [hwp2md-linux-x64](https://github.com/ilyos-numon/hwp2md/releases/latest/download/hwp2md-linux-x64) |

macOS·Linux 는 실행 권한을 준다. 브라우저로 받은 macOS 파일은 서명·공증이 없어 Gatekeeper 가 막으므로 격리 속성을 지운다.

```bash
chmod +x hwp2md-macos-arm64
xattr -d com.apple.quarantine hwp2md-macos-arm64   # macOS 만
./hwp2md-macos-arm64 문서.hwp -o out/
./hwp2md-macos-arm64 serve                         # 웹 미리보기
```

Windows 는 SmartScreen 경고가 뜨면 "추가 정보 → 실행" 을 누른다. `hwp2md-windows-x64.exe 문서.hwp -o out/` 처럼 명령 프롬프트·PowerShell 에서 실행한다.

내려받은 파일은 같은 릴리스의 [SHA256SUMS](https://github.com/ilyos-numon/hwp2md/releases/latest/download/SHA256SUMS) 로 확인할 수 있다.

```bash
shasum -a 256 -c SHA256SUMS --ignore-missing      # macOS·Linux (Linux 는 sha256sum -c 도 된다)
```

```powershell
Get-FileHash .\hwp2md-windows-x64.exe -Algorithm SHA256   # 출력 Hash 를 SHA256SUMS 의 값과 비교
```

실행 파일은 처음 실행할 때 임시 폴더에 압축을 풀어 몇 초 걸린다.

### 1.3 Python 패키지

PyPI 배포 이름은 `hwp2markdown` 이다. 설치 후 명령과 import 이름은 `hwp2md` 다. Python 3.11 이상이 필요하다. PyPI 의 `hwp2md` 는 이 저장소와 무관한 다른 프로젝트다.

```bash
uvx --from hwp2markdown hwp2md 문서.hwp -o out/   # 설치 없이 한 번 실행 (uv 필요)
pip install 'hwp2markdown[web]'                    # 또는 uv tool install / pipx install
hwp2md --version
```

웹 미리보기 의존성(Starlette·uvicorn)은 extra `web` 에만 있다. 기본 설치(`pip install hwp2markdown`, CLI·라이브러리)는 `olefile`·`lxml` 만 쓴다. extra 없이 `hwp2md serve` 를 실행하면 `pip install 'hwp2markdown[web]'` 안내와 함께 종료 코드 1로 끝난다.

### 1.4 소스에서 (개발용)

```bash
git clone https://github.com/ilyos-numon/hwp2md.git && cd hwp2md

# 방법 1: uv (웹 미리보기·테스트 도구까지 함께 설치)
uv sync
uv run hwp2md --version

# 방법 2: pip (웹 미리보기가 필요 없으면 '[web]' 을 빼도 된다)
pip install '.[web]'
hwp2md --version
```

## 2. CLI

```text
usage: hwp2md [-h] [-o OUT_DIR] [--version] INPUT
usage: hwp2md serve [-h] [--host HOST] [--port PORT] [--no-browser]
```

```console
$ hwp2md demo.hwpx -o out/
✓ demo.hwpx → out/demo.md
  단락 5개 · 표 1개 · 제목 5개 · 이미지 1개
  이미지: out/demo_images/ (1 files)
```

```text
out/
├── demo.md
└── demo_images/
    └── img_001.png
```

- `-o` 를 생략하면 현재 폴더에 쓴다. 출력 폴더가 없으면 만든다.
- HWP 5.0·HWPX·HWPML 은 같은 명령이다. 포맷은 확장자가 아니라 파일 내용으로 판별한다.
- 이미지가 없는 문서는 `_images` 폴더를 만들지 않고, 요약 줄에서 0개인 제목·이미지 항목을 생략한다.
- 종료 코드: 0 성공 · 1 변환 오류 · 2 파일 없음 · 3 HWP 가 아니거나 지원하지 않는 문서(DRM·비밀번호 문서 등). 오류 줄은 `unsupported HWP file (DRM protected): …`, `unsupported HWP file (password protected): …` 처럼 거부 이유를 구분한다.
- 변환하지 못한 요소가 있으면 마지막에 `  건너뜀: 머리말·꼬리말 2개 · 메모 1개` 같은 줄이 붙는다 (§5).
- 변환할 파일 이름이 `serve` 이면 `hwp2md ./serve` 처럼 경로로 적는다.

## 3. 웹 미리보기 (`hwp2md serve`)

```bash
hwp2md serve                       # http://localhost:8770 , 브라우저가 자동으로 열린다
hwp2md serve --port 8771           # 8770 이 이미 쓰이고 있을 때
hwp2md serve --no-browser          # 브라우저 자동 열기 끔
```

`/` 은 변환 화면, `/about` 은 서비스 소개(기능, 사용 장면, 추출 한계 `/about#limits`)다. 두 화면에 쓰는 글꼴·GSAP·marked 는 패키지 안에 동봉돼 있어 서버 모드는 인터넷 없이 동작한다. 화면은 한국어·영어를 지원한다(브라우저 언어로 자동 선택, 헤더의 KO/EN 버튼, `?lang=ko|en`).

1. HWP·HWPX·HWPML 파일을 끌어다 놓거나 클릭해서 고른다 (최대 50MB).
2. 왼쪽에 렌더링된 미리보기, 오른쪽에 Markdown 원문이 나온다.
3. "ZIP 다운로드" 로 `.md` 와 이미지 폴더를 한 번에 받는다.

오른쪽 위 "브라우저 안에서만 처리" 스위치로 변환 위치를 고른다.

| | 서버 모드 (기본) | 브라우저 안에서만 처리 |
|---|---|---|
| 변환 위치 | 로컬 `hwp2md serve` 프로세스 (메모리에서 변환) | 브라우저 안의 Pyodide (WebAssembly 파이썬) |
| 파일 바이트 전송 | 로컬 서버로 `POST /api/convert` | 보내지 않음 |
| 첫 변환까지 | 즉시 | 첫 로딩 약 1분 (Pyodide·lxml 다운로드, 측정 약 65초) |
| 인터넷 | 필요 없음 (화면 자원 동봉) | 필요 (Pyodide 를 jsDelivr CDN 에서 받음) |
| 결과 | 같은 Markdown | 같은 Markdown (E2E 로 바이트 비교) |

기본 바인드는 `localhost` 이고 인증이 없다. `--host` 로 외부에 열 수는 있지만 외부 공개용으로 설계하지 않았다. 기본 포트가 다른 프로그램과 겹치면 `--port` 로 바꾼다 (자동으로 다음 포트를 찾지 않는다).

## 4. 라이브러리

파일로 쓰기 (`convert`):

```python
from hwp2md import convert

result = convert("input.hwp", "out/")       # out/input.md (+ out/input_images/)
print(result.output)                         # Path("out/input.md")
print(result.heading_count, result.table_count, result.image_count)
print(result.markdown)                       # 파일에 쓴 것과 같은 내용
```

메모리에서만 변환하기 (`convert_bytes`, 디스크에 아무것도 쓰지 않는다):

```python
from pathlib import Path
from hwp2md import convert_bytes

data = Path("input.hwp").read_bytes()
result = convert_bytes(data, filename="input.hwp")  # filename 은 이미지 폴더 이름에만 쓰인다
print(result.markdown)                     # convert() 가 쓰는 .md 와 바이트 동일
for img in result.images:                  # 추출된 이미지 (고유 파일만)
    print(img.file_name, img.mime, len(img.data))
```

- 시그니처: `convert(path: str | Path, out_dir: str | Path = ".") -> ConvertResult`, `convert_bytes(data: bytes, filename: str = "document.hwp") -> MemoryResult`.
- 예외: `NotHwpFileError`(HWP 아님), `UnsupportedHwpError`(지원하지 않는 문서)와 그 하위 `DrmProtectedError`(DRM 적용 문서)·`EncryptedDocumentError`(비밀번호 문서), 모두 `Hwp2mdError` 하위.
- 건너뛴 요소: `result.skipped` 는 `(("header_footer", 2), …)` 처럼 종류와 개수의 튜플이다(0개는 빠진다). `convert`·`convert_bytes` 결과 모두에 있다. `convert` 는 파일이 없으면 `FileNotFoundError`, `convert_bytes` 는 빈 입력·50MB 초과도 `Hwp2mdError` 하위 예외로 거부한다.

## 5. 건너뜀 보고

변환하지 못한 요소는 조용히 버리지 않고 종류별 개수를 알려 준다. 종류는 머리말·꼬리말, 메모, 숨은 설명, 데이터를 꺼낼 수 없는 차트, OLE 개체, 글맵시, 양식 개체, 외부 연결 그림, 본체 없는 그림 아홉 가지다.

| 어디서 | 모양 |
|---|---|
| CLI | 요약 끝 줄 `  건너뜀: 머리말·꼬리말 2개 · OLE 개체 1개` |
| 라이브러리 | `ConvertResult.skipped`·`MemoryResult.skipped` (종류, 개수) 튜플 |
| 웹 API | 응답 JSON 의 `skipped`: `[{"kind": "header_footer", "label": "머리말·꼬리말", "count": 2}]` (항상 있음, 없으면 빈 배열) |
| 웹 화면 | 미리보기 위 "변환하지 못한 요소: …" 경고 |

## 6. 지원 범위 상세

| 구분 | 항목 | 설명 |
|---|---|---|
| 지원 | 포맷 | HWP 5.0 바이너리(OLE), HWPX(zip/XML), HWPML 2.x(단일 XML). 확장자가 아니라 내용으로 판별 |
| 지원 | 본문 단락 | 탭은 공백, 줄바꿈 유지 |
| 지원 | 제목 계층 | 문단 모양의 개요 1~6수준 → `#`~`######`, 7수준은 `######` |
| 지원 | 표 | GFM 표 (첫 행이 헤더), 셀 안 여러 단락은 `<br>`, `\|` 이스케이프, 중첩 표는 셀 텍스트로 평탄화 |
| 지원 | 이미지 | 본문 그림을 `<이름>_images/img_001.png` … 로 추출(원본 바이트 그대로)하고 제자리에 그림 링크(`![그림 N]` 꼴). 같은 그림을 다시 참조하면 파일 1개 |
| 지원 | 표 칸 안 그림 | 칸 안에 그림 링크(`![그림 N]` 꼴). 문서 순서대로 그림 번호를 쓴다 |
| 지원 | 캡션 | 표·그림 캡션을 개체 뒤 단락으로 출력 |
| 지원 | 글상자·도형·묶음 | 안쪽 글과 그림을 개체 자리에 출력 |
| 지원 | 하이퍼링크 | `[글자](https://…)` 꼴. http·https·mailto 만 링크로 쓰고 그 밖의 주소는 글자만 남긴다 |
| 지원 | 각주·미주 | 본문에 `[^1]`·`[^e1]` 참조, 문서 끝에 정의 |
| 지원 | 수식 | 한글 수식 스크립트 → LaTeX `$…$` (단락에 수식만 있으면 `$$…$$`). 변환에 실패하면 원문 스크립트를 코드 스팬으로 |
| 지원 | 번호·글머리표 목록 | 글머리표는 `-`, `1.`·`1)` 꼴 번호는 Markdown 목록 문법, 그 밖의 번호(`가.`·`①` 등)는 단락 앞 글자로. 번호는 문단 번호 정의로 근사 계산 |
| 지원 | OOXML 차트 | 차트에 저장된 값으로 `차트: 제목` 단락 + 표 |
| 지원 | 배포용 문서 | 공개된 절차로 복호화해 변환 (§7) |
| 부분 | OLE 개체 | 원본이 그림(PNG·JPEG·GIF·BMP)이면 그림으로 추출, 그 밖은 건너뜀 보고 |
| 제한 | 병합 셀 | 원 셀에 텍스트, 덮인 칸은 빈 칸 (GFM 이 병합을 표현하지 못함) |
| 제외 | 머리말·꼬리말 | 본문 흐름에 넣지 않고(청킹 잡음 방지) 건너뜀으로 보고. 세 포맷 동일 |
| 제외 | 메모·숨은 설명 | 작성자 정보가 있을 수 있어 내용은 출력하지 않고 개수만 보고 |
| 제한 | 서식 | 글꼴·색상·정렬은 버린다 |
| 거부 | DRM 적용 문서 | `DrmProtectedError`, CLI 종료 코드 3, API 오류 코드 `drm` |
| 거부 | 비밀번호 문서 | `EncryptedDocumentError`, CLI 종료 코드 3, API 오류 코드 `encrypted`. 비밀번호 입력 기능은 없다 |
| 미지원 | HWP 3.0 이하 | HWP 파일이 아닌 것으로 판정 (종료 코드 3) |

## 7. 배포용 문서 고지

배포용 문서(편집·복사·인쇄를 제한해 배포한 HWP 5.0 문서)는 기본으로 변환한다. 편집·복사 제한 문서를 텍스트로 꺼내므로 작성자의 의도와 사용 권한을 확인하세요. hwp2md 는 공개된 복호화 절차만 쓰며, DRM 적용 문서와 비밀번호 문서는 풀지 않고 거부한다.

## 8. 개발

```bash
uv sync && uv run playwright install chromium   # 개발 환경 (E2E 용 브라우저 포함)
uv run pytest tests/unit -q                     # 단위
uv run pytest tests/e2e -q                      # E2E (브라우저 모드 케이스는 인터넷 필요)
uv run ruff check src tests && uv run ruff format --check src tests
uv run mypy src                                 # strict
```

테스트 문서는 `tests/synth_hwp5.py`·`tests/synth_hwpx.py` 가 명세 기준으로 코드에서 만든다. 실제 문서 샘플은 저장소에 넣지 않는다. `tests/fixtures/` 에 넣으면 E2E 가 자동으로 함께 돌린다.

## 9. 알려진 이슈

- 브라우저 모드 첫 로딩이 약 1분 걸리고 인터넷(jsDelivr)이 필요하다. 오프라인 번들은 없다.
- CI 는 Python 3.11·3.13 에서 검증한다. 3.14 에서는 손상된 zip 의 오류 문구가 다르게 나오는 알려진 차이가 있다.
- 이미지가 있는 실제 HWP 5.0 샘플이 없어, HWP 5.0 이미지 경로는 합성 문서와 공개 스펙 교차 확인으로만 검증했다.
- 이미지 포맷은 변환하지 않는다. WMF/EMF 같은 원본은 그대로 저장되어 브라우저에서 안 보일 수 있다.
- 단락 중간에 놓인 그림의 위치가 HWP 5.0 과 HWPX 에서 다를 수 있다.
