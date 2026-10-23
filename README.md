# hwp2md

## 철학
한국의 공공·기업 문서는 HWP 안에 갇혀 있다. LLM 시대에 가장 먼저 필요한 건 그 문을 여는 열쇠다.

## 문제
- HWP/HWPX는 RAG 파이프라인, LLM 입력, 버전 관리 어디에도 바로 쓸 수 없다
- 기존 변환 도구는 표·각주·이미지 위치를 잃거나, 한컴 설치를 요구한다
- 개발자들이 매번 같은 파싱 코드를 다시 짠다

## 방향
- 한컴 없이 동작하는 순수 파이썬 CLI + 라이브러리
- 표는 마크다운 표로, 이미지는 추출 후 상대 경로로, 각주는 하단 참조로
- 문서 구조(제목 계층, 목차)를 최대한 보존해 청킹에 유리하게
- RAG용 옵션: 섹션 단위 분할, 메타데이터(JSON) 동시 출력

## 하지 않는 것
- 역변환(md → hwp)
- 서식 완벽 재현(글꼴·색상)

## 기술 방향
- HWP 5.0 바이너리는 OLE 파싱, HWPX는 XML 파싱으로 분리 구현
- 표·이미지 등 블록 단위 추상화 후 마크다운 렌더러 분리
- pip 배포, GitHub Actions 테스트

## MVP
- 본문·제목·표·이미지 4종 지원
- `hwp2md input.hwp -o out/` 한 줄
- 공공기관 샘플 문서 20개로 변환 품질 비교표 작성

## 설치와 실행 (개발 중)
```bash
uv sync                               # .venv 생성 + 개발 의존성 설치
uv run hwp2md input.hwp -o out/       # out/input.md (+ 이미지가 있으면 out/input_images/)
uv run hwp2md input.hwpx -o out/      # HWPX 도 같은 명령 (포맷은 내용으로 판별)
uv run pytest tests/unit tests/e2e -q # 테스트
uv run hwp2md serve                   # 웹 미리보기 (개발 체크아웃)
```

배포 패키지로 설치할 때는 웹 미리보기용 의존성(Starlette·uvicorn)을 extra 로 함께 받는다. 개발 중에는 `uv sync` 가 이미 설치한다.
```bash
pip install 'hwp2md[web]'
hwp2md serve [--port 8765] [--no-browser]   # 기본 주소 http://localhost:8765 , 브라우저가 자동으로 열림
```
- 포트가 이미 쓰이고 있으면 `hwp2md serve --port 8780` 처럼 `--port` 로 바꾼다.
- 화면 사용법: (1) HWP·HWPX 파일을 끌어다 놓거나 클릭해서 고른다(최대 50MB). (2) 왼쪽에 렌더링된 미리보기, 오른쪽에 Markdown 원문이 나온다. (3) "zip 다운로드" 로 `.md` 와 이미지 폴더를 한 번에 받는다.
- "브라우저 안에서만 처리" 스위치를 켜면 변환이 브라우저 안(Pyodide)에서 돌고 파일은 서버로 가지 않는다. 처음 켤 때 jsDelivr CDN 에서 Pyodide(수십 MB)를 받으므로 첫 로딩은 1분 안팎 걸리고 인터넷 연결이 필요하다.
- 서버 모드에서도 업로드한 파일은 메모리에서만 변환하고 디스크에 저장하지 않는다.
- 변환할 파일 이름이 `serve` 이면 `hwp2md ./serve` 처럼 경로로 적는다.

라이브러리로 쓸 때는 파일을 쓰지 않고 메모리에서 바로 변환할 수 있다.
```python
from hwp2md import convert_bytes

result = convert_bytes(open("input.hwp", "rb").read(), filename="input.hwp")
print(result.markdown)                     # .md 내용 (이미지 링크는 input_images/... 상대 경로)
for img in result.images:                  # 추출된 이미지 바이트
    print(img.file_name, img.mime, len(img.data))
```
현재 지원: HWP 5.0 바이너리와 HWPX(zip/XML) 두 포맷의 본문 단락 텍스트, 제목 계층(개요 1~7수준 → Markdown # ~ ######, 7수준은 ######), 표(Markdown 표, 병합 셀은 빈 칸, 셀 내 단락은 <br>), 이미지(본문 그림을 out/<입력 파일명>_images/img_001.png … 로 추출하고 Markdown 제자리에 상대 경로 링크. 표 셀·머리말 안 그림은 제외). 포맷은 확장자가 아니라 파일 내용으로 판별한다. 같은 변환을 웹 미리보기(`hwp2md serve`, 서버 모드·브라우저 전용 모드)와 메모리 변환 API(`convert_bytes`)로도 쓸 수 있다. 각주는 진행 중.
