## ADDED Requirements

### Requirement: OS별 단일 실행 파일
`scripts/build_binary.py` 는 현재 OS·CPU 에 맞는 단일 실행 파일 하나를 `hwp2md-<platform>[.exe]` 이름으로 만들어야 한다(SHALL). `<platform>` 은 `windows-x64`, `macos-arm64`, `macos-x64`, `linux-x64` 중 하나이고, 확장자 `.exe` 는 Windows 에만 붙는다. 실행 파일은 Python 설치 없이 `hwp2md` 콘솔 명령과 같은 인자·출력·종료 코드를 갖는다.

#### Scenario: 버전 출력
- **WHEN** 빌드한 실행 파일을 `--version` 으로 실행한다
- **THEN** 종료 코드 0, 표준 출력이 `hwp2md <__version__>` 한 줄이다

#### Scenario: 합성 HWPX 변환
- **WHEN** 합성 HWPX 파일을 `<실행 파일> 문서.hwpx -o <출력 디렉터리>` 로 변환한다
- **THEN** 종료 코드 0, `<출력 디렉터리>/문서.md` 가 생기고 합성 본문 문단 텍스트를 담는다

#### Scenario: 지원하지 않는 플랫폼
- **WHEN** 4개 대상이 아닌 OS·CPU 에서 `scripts/build_binary.py` 를 실행한다
- **THEN** 종료 코드 2 와 `build_binary: unsupported platform` 으로 시작하는 줄이 표준 오류에 나온다

### Requirement: 실행 파일의 오류 경로
실행 파일은 HWP 가 아니거나 손상된 입력에 대해 traceback 없이 비0 종료 코드와 `hwp2md: error:` 로 시작하는 표준 오류 줄을 내야 한다(SHALL).

#### Scenario: HWP 가 아닌 입력
- **WHEN** 일반 텍스트 파일 `note.txt` 를 변환한다
- **THEN** 종료 코드 3, 표준 오류에 `hwp2md: error: not an HWP 5.0 file` 이 있고 `Traceback` 이 없다

#### Scenario: 손상된 HWPX
- **WHEN** 앞 100바이트만 남긴 HWPX 파일을 변환한다
- **THEN** 종료 코드가 0 이 아니고, 표준 오류에 `hwp2md: error:` 가 있고 `Traceback` 이 없다

### Requirement: 실행 파일 안의 웹 미리보기
실행 파일의 `serve` 하위 명령은 web extra 를 포함해야 한다(SHALL). 정적 화면 자원(vendor 글꼴 포함)과 `/pkg/hwp2md.zip` 런타임 zip 이 실행 파일 안의 파일로 제공된다.

#### Scenario: 헬스체크와 정적 자원
- **WHEN** `<실행 파일> serve --no-browser --port <빈 포트>` 를 띄운다
- **THEN** 60초 안에 `GET /api/health` 가 200 과 `{"ok": true, "version": "<__version__>"}` 를 주고, `GET /static/vendor/fonts/PretendardVariable.woff2` 가 200 이며 본문이 저장소 파일과 바이트 단위로 같다

#### Scenario: 런타임 zip
- **WHEN** 같은 서버에 `GET /pkg/hwp2md.zip` 을 요청한다
- **THEN** 200 이고 zip 에 `hwp2md/__init__.py`, `hwp2md/convert.py`, `olefile/olefile.py` 가 있으며 `hwp2md/web/` 로 시작하는 항목은 없다

### Requirement: Release 자산과 체크섬
`vX.Y.Z` 태그 push 의 `Release` 워크플로우는 OS 4종 러너에서 실행 파일을 빌드하고 같은 러너에서 실행 파일 스모크를 통과한 뒤, GitHub Release `vX.Y.Z` 에 실행 파일 4개와 `SHA256SUMS` 를 올려야 한다(SHALL). `contents: write` 권한은 Release 를 만드는 job 에만 있다. PyPI 게시 job 과 Trusted Publishing 설정은 바뀌지 않는다.

#### Scenario: 자산 목록
- **WHEN** 태그 `v0.1.4` 의 `Release` 실행이 성공한다
- **THEN** Release `v0.1.4` 의 자산 이름이 정확히 `SHA256SUMS`, `hwp2md-linux-x64`, `hwp2md-macos-arm64`, `hwp2md-macos-x64`, `hwp2md-windows-x64.exe` 다섯 개다

#### Scenario: 체크섬 검증
- **WHEN** 자산을 같은 디렉터리에 내려받아 `shasum -a 256 -c SHA256SUMS` 를 실행한다
- **THEN** 실행 파일 네 줄 모두 `OK` 이고 종료 코드 0 이다

### Requirement: Homebrew 바이너리 formula
`scripts/update_formula.py` 는 버전과 `SHA256SUMS` 로 Homebrew formula `hwp2md.rb` 를 결정적으로 생성해야 한다(SHALL). formula 는 macOS arm64·macOS x64·Linux x64 실행 파일의 Release URL 과 sha256 을 쓰고, Python 리소스를 쓰지 않으며, `test do` 블록에서 `--version` 과 not-HWP 입력의 종료 코드 3 을 확인한다.

#### Scenario: 정상 생성
- **WHEN** 세 macOS·Linux 자산 줄이 모두 있는 `SHA256SUMS` 로 `--version 0.1.4` 를 생성한다
- **THEN** 종료 코드 0, 출력에 `version "0.1.4"` 와 세 URL·sha256 이 있고, 같은 입력으로 두 번 생성한 결과가 바이트 단위로 같다

#### Scenario: 자산 누락
- **WHEN** `hwp2md-macos-x64` 줄이 없는 `SHA256SUMS` 로 생성한다
- **THEN** 종료 코드 1 과 `update_formula: FAIL missing hwp2md-macos-x64` 가 표준 오류에 나온다

#### Scenario: brew 설치
- **WHEN** macOS 에서 `brew install ilyos-numon/tap/hwp2md` 후 `brew test hwp2md` 를 실행한다
- **THEN** 두 명령 모두 종료 코드 0 이고 `hwp2md --version` 이 `hwp2md 0.1.4` 다
