## ADDED Requirements

### Requirement: 정적 사이트 설정은 브라우저 모드를 고정한다
변환 화면은 `<meta name="hwp2md-site" content="static">` 이 있으면 시작할 때 브라우저 모드로 들어가 Pyodide 를 불러오고, 모드 스위치(`label.switch`)를 숨기며, 불러오기에 실패해도 서버 모드로 돌아가지 않아야 한다(SHALL). `<meta name="hwp2md-pkg-url">` 이 있으면 런타임 zip 을 그 주소에서 받고, 없으면 `/pkg/hwp2md.zip` 에서 받는다. 두 meta 가 없으면 화면 동작은 이 변경 전과 같다.

#### Scenario: serve 화면은 그대로
- **WHEN** `hwp2md serve` 의 `/` 를 연다
- **THEN** `#mode-status[data-state="server"]` 이고 `label.switch` 가 보인다

#### Scenario: 정적 설정이 있는 화면
- **WHEN** 두 meta 가 있는 `convert.html` 을 연다
- **THEN** `label.switch` 가 보이지 않고 `#mode-status` 가 `loading` 을 거쳐 `browser` 가 된다

### Requirement: 웹 화면은 한국어와 영어로 보인다
변환 화면과 소개 페이지는 사용자 노출 문구를 한국어(`ko`)와 영어(`en`)로 보여야 한다(SHALL). 언어는 `?lang=ko|en` 쿼리, 저장된 선택(`localStorage` `hwp2md-lang`), 브라우저 언어(`ko` 로 시작하면 한국어, 아니면 영어) 순으로 정하고 `<html lang>` 에 반영한다. 알 수 없는 `lang` 값은 무시한다. 헤더의 KO/EN 버튼은 언어를 바꾸고 선택을 저장한다. 한국어 문구는 이 변경 전과 같고, CLI 출력과 HTTP API 응답(건너뜀 라벨 포함)은 바뀌지 않는다. `hwp2md serve` 화면과 정적 사이트 모두에 적용된다.

#### Scenario: 영어 브라우저의 첫 방문
- **WHEN** 브라우저 언어가 `en-US` 이고 저장된 선택이 없는 상태로 변환 화면을 연다
- **THEN** `<html lang="en">` 이고 모드 상태가 `Server mode` 이며, 비 HWP 파일을 넣으면 오류가 `Not an HWP 5.0 or HWPX file` 이다

#### Scenario: 전환과 유지
- **WHEN** 영어 화면에서 KO/EN 버튼을 누르고 새로고침한다
- **THEN** 화면이 한국어(`서버 모드`)로 바뀌고 새로고침 뒤에도 한국어다

#### Scenario: 알 수 없는 언어 값
- **WHEN** 브라우저 언어가 `ko-KR` 인 상태로 `?lang=fr` 을 연다
- **THEN** 쿼리를 무시하고 한국어로 보이며 선택을 저장하지 않는다

#### Scenario: 정적 사이트 영어 변환
- **WHEN** 브라우저 언어가 `en-US` 인 상태로 정적 사이트 `convert.html` 에서 합성 HWPX 를 넣는다
- **THEN** 상태가 `Browser mode: files are not sent to a server` 이고 변환이 끝난다

