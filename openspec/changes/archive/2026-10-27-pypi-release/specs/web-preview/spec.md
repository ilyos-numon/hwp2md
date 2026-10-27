## MODIFIED Requirements

### Requirement: serve 하위 명령이 로컬 서버를 띄운다
CLI 는 `hwp2md serve [--host HOST] [--port PORT] [--no-browser]` 를 제공해야 한다(SHALL). 기본값은 host `localhost`, port `8770` 이고, `--no-browser` 가 없으면 기본 브라우저로 화면을 연다. 준비되면 `GET /api/health` 가 `{"ok": true, "version": "<버전>"}` 를 200 으로 준다. 포트가 사용 중이면 표준 오류에 `hwp2md: error: port <PORT> already in use` 를 쓰고 종료 코드 1 로 끝난다. web extra 가 설치되지 않았으면 표준 오류에 배포 이름 기준 설치 안내 `pip install 'hwp2markdown[web]'` 를 쓰고 종료 코드 1 로 끝난다. 첫 인자가 `serve` 가 아니면 기존 변환 CLI 로 동작한다.

#### Scenario: 서버 기동
- **WHEN** `hwp2md serve --no-browser --port <빈 포트>` 를 실행한다
- **THEN** 30초 안에 `GET /api/health` 가 200 이고 `GET /` 가 `text/html` 화면을 준다

#### Scenario: web extra 없음
- **WHEN** starlette·uvicorn import 를 막은 프로세스에서 `main(["serve", "--no-browser"])` 를 호출한다
- **THEN** 반환값 1, 표준 오류에 `hwp2markdown[web]` 이 포함되고 `'hwp2md[web]'` 은 포함되지 않는다
