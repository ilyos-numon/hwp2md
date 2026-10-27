# Design — binaries-brew

## Context
- 엔진은 순수 Python + `lxml`(C 확장) + `olefile`. web extra 는 Starlette·uvicorn.
- `hwp2md.web.app` 은 `Path(__file__).parent / "static"` 로 정적 자원을 찾고, `build_runtime_zip()` 은 `Path(hwp2md.__file__).parent.rglob("*")` 에서 `.py` 원본과 `olefile` 의 `.py` 를 읽어 zip 을 만든다. 동결(frozen) 실행 파일은 모듈을 `.pyc` 아카이브(PYZ)로만 싣기 때문에, 원본 `.py` 를 데이터로 따로 싣지 않으면 `/pkg/hwp2md.zip` 이 비거나 `olefile` 항목이 빠진다.
- `cli.py` 는 성공 시 `✓`·한글을 출력한다. 표준 출력 인코딩이 UTF-8 이 아닌 환경(Windows 파이프 cp1252, `LANG=C`)에서 `UnicodeEncodeError` 가 날 수 있다.

## Goals / Non-Goals
- Goals: Python 없이 4개 OS 에서 CLI·serve 동작, Release 자산 + 체크섬, Homebrew 탭 설치.
- Non-Goals: 코드 서명·공증(Apple notarization, Authenticode), Linux arm64·Windows arm64, Docker 이미지, winget·scoop·apt 저장소, Homebrew core 등록, 자동 탭 갱신(PAT).

## Decisions
1. 빌더: PyInstaller 6.22.3 `--onefile`. 이유: 세 후보 중 lxml·uvicorn hook 이 기본 제공(pyinstaller-hooks-contrib)되고 C 컴파일러가 필요 없으며 빌드가 수 분 안에 끝난다. 라이선스는 GPL-2.0-or-later + 부트로더 예외라 만든 실행 파일은 MIT 로 배포할 수 있다. Nuitka 는 C 컴파일 시간이 길고 GitHub 가 보고하는 라이선스가 AGPL-3.0 이며, PyApp 은 첫 실행 때 Python 배포본·의존성을 내려받거나 Rust 툴체인이 필요해 "오프라인 단일 파일" 목표와 맞지 않는다.
2. PyInstaller 는 `pyproject.toml`·`uv.lock` 에 넣지 않고 `uv run --with pyinstaller==6.22.3` 으로만 쓴다(배포 의존성·lock 변화 없음).
3. 데이터 동봉: `src/hwp2md` 트리를 `__pycache__` 를 뺀 임시 스테이징 디렉터리로 복사해 `--add-data <stage>/hwp2md:hwp2md` 로, `olefile` 패키지의 `*.py` 를 `--add-data <...>:olefile` 로 싣는다. 동결 앱에서 `hwp2md.__file__` 의 부모가 `_MEIPASS/hwp2md` 이므로 `app.py` 를 고치지 않고 `STATIC_DIR` 과 `build_runtime_zip()` 이 그대로 동작한다.
4. 진입 스크립트 `packaging/pyinstaller/hwp2md_entry.py` 가 표준 출력·오류 인코딩이 UTF-8 이 아니면 `reconfigure(encoding="utf-8", errors="replace")` 후 `hwp2md.cli.main()` 을 부른다. `cli.py` 는 바꾸지 않는다.
5. 자산 이름에 버전을 넣지 않는다(`releases/latest/download/<이름>` 고정 링크). 압축하지 않은 실행 파일 그대로 올린다.
6. Linux 는 glibc 호환 범위를 넓히려고 `ubuntu-22.04` 러너, macOS x64 는 `macos-15-intel`, macOS arm64 는 `macos-15`, Windows 는 `windows-2022` 러너에서 빌드한다. CI 러너에서는 `actions/setup-python` 의 3.12 인터프리터를 쓴다(python-build-standalone 과 PyInstaller 의 공유 라이브러리 문제 회피).
7. Homebrew: Python 리소스 방식 대신 바이너리 formula. `lxml` 소스 빌드(libxml2·libxslt)와 리소스 목록 유지 비용을 피한다. 갱신은 `scripts/update_formula.py` 로 생성 → orchestrator 가 탭 저장소에 커밋·push(토큰 secret 없음).
8. 실행 파일 스모크는 pytest E2E 하나(`tests/e2e/test_binary_smoke.py`)로 로컬·CI 공통. `HWP2MD_BINARY` 가 있으면 그 파일을 쓰고, 없으면 세션당 한 번 `scripts/build_binary.py` 로 빌드한다.

## Risks / Trade-offs
- onefile 은 실행마다 임시 디렉터리에 풀어 첫 실행이 1~3초 느리다 → 수용(단일 파일 요구 우선).
- 서명하지 않은 실행 파일은 Gatekeeper·SmartScreen 경고가 뜬다 → README 에 해제 방법.
- Windows Defender 오탐 가능 → README 에 체크섬 검증 방법, 반복되면 §7 후속 작업.
- `macos-15-intel` 러너는 GitHub 가 마지막 x86 이미지로 예고했다 → 러너가 사라지면 macOS x64 자산을 빼고 formula 의 `on_intel` 을 제거하는 후속 변경.
