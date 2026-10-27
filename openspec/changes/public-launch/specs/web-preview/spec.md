## ADDED Requirements

### Requirement: 정적 사이트 설정은 브라우저 모드를 고정한다
변환 화면은 `<meta name="hwp2md-site" content="static">` 이 있으면 시작할 때 브라우저 모드로 들어가 Pyodide 를 불러오고, 모드 스위치(`label.switch`)를 숨기며, 불러오기에 실패해도 서버 모드로 돌아가지 않아야 한다(SHALL). `<meta name="hwp2md-pkg-url">` 이 있으면 런타임 zip 을 그 주소에서 받고, 없으면 `/pkg/hwp2md.zip` 에서 받는다. 두 meta 가 없으면 화면 동작은 이 변경 전과 같다.

#### Scenario: serve 화면은 그대로
- **WHEN** `hwp2md serve` 의 `/` 를 연다
- **THEN** `#mode-status[data-state="server"]` 이고 `label.switch` 가 보인다

#### Scenario: 정적 설정이 있는 화면
- **WHEN** 두 meta 가 있는 `convert.html` 을 연다
- **THEN** `label.switch` 가 보이지 않고 `#mode-status` 가 `loading` 을 거쳐 `browser` 가 된다
