# document-protection Specification

## Purpose
TBD - created by archiving change extract-dropped. Update Purpose after archive.

## Requirements

### Requirement: 배포용 문서는 공개 알고리즘으로 복호화해 변환한다
HWP 5.0 FileHeader 속성 비트 2(배포용)가 켜진 문서에서 리더는 `BodyText` 대신 `ViewText/Section<N>` 을 읽고, 각 스트림 첫 레코드 `HWPTAG_DISTRIBUTE_DOC_DATA`(0x1C, 256바이트)에서 MSVC `rand()` 선형 합동 수열(seed = 앞 4바이트 LE, `seed = seed*214013 + 2531011 mod 2^32`, 값 `(seed>>16) & 0x7FFF`)로 만든 256바이트 배열을 XOR 해 오프셋 `4 + (seed & 0xF)` 의 해시 앞 16바이트를 키로 얻고, 레코드 뒤 나머지를 AES-128-ECB 로 복호화한 뒤 FileHeader 압축 비트가 켜져 있으면 raw deflate 를 풀어 일반 섹션처럼 변환해야 한다(SHALL). AES 는 의존성 없는 순수 파이썬 구현을 쓴다. `ViewText/Section0` 이 없거나 첫 레코드가 0x1C·256바이트가 아니면 `UnsupportedHwpError("distribution document: …")` 다.

#### Scenario: 합성 배포용 문서
- **WHEN** 단락 3개 문서를 압축·AES 암호화해 `ViewText/Section0` 에 넣고 FileHeader 속성 `0x5` 로 만든 합성 배포용 문서를 변환한다
- **THEN** Markdown 이 같은 단락의 일반 문서 변환 결과와 바이트 단위로 같다

#### Scenario: ViewText 없는 배포용 플래그
- **WHEN** FileHeader 속성 `0x5` 이고 `BodyText/Section0` 만 있는 문서를 변환한다
- **THEN** `UnsupportedHwpError` 가 나고 CLI 종료 코드는 3 이다

#### Scenario: AES 표준 벡터
- **WHEN** FIPS-197 부록 C.1 의 키 `000102030405060708090a0b0c0d0e0f` 와 암호문 `69c4e0d86a7b0430d8cdb78070b4c55a` 를 `aes128_ecb_decrypt` 에 넣는다
- **THEN** 평문 `00112233445566778899aabbccddeeff` 가 나온다

### Requirement: 문서보안(DRM) 파일은 전용 오류로 거부한다
변환기는 입력 앞 2바이트가 `9B 20` 이거나 앞 64바이트 안에 ASCII `DRMONE` 이 있는 파일, 그리고 HWP 5.0 FileHeader 속성 비트 4 또는 비트 10 이 켜진 문서를 `DrmProtectedError`(`UnsupportedHwpError` 하위)로 거부해야 하고(SHALL), 복호화·우회를 시도하지 않는다. 메모리 API 오류 코드는 `drm`(HTTP 415), CLI 는 종료 코드 3 과 표준 오류 `hwp2md: error: unsupported HWP file (DRM protected): <입력>` 이다.

#### Scenario: DRM 래핑 서명
- **WHEN** `9B 20` + `DRMONE  ` + 난수 4000바이트인 입력을 `convert_to_response` 로 넘긴다
- **THEN** `(415, {"error": {"code": "drm", …}})` 이다

#### Scenario: 한컴 DRM 비트
- **WHEN** FileHeader 속성 `0x11` 인 합성 HWP 5.0 문서를 CLI 로 변환한다
- **THEN** 종료 코드 3, 표준 오류에 `DRM protected` 가 있고 `.md` 가 생기지 않는다

### Requirement: 비밀번호 문서는 전용 오류로 거부한다
변환기는 HWP 5.0 FileHeader 속성 비트 1(암호)이 켜진 문서와, HWPX `META-INF/manifest.xml` 에 `encryption-data` 요소(이름공간 무관)가 있는 문서를 `EncryptedDocumentError`(`UnsupportedHwpError` 하위)로 거부해야 한다(SHALL). 메모리 API 오류 코드는 `encrypted`(HTTP 415), CLI 는 종료 코드 3 과 표준 오류 `hwp2md: error: unsupported HWP file (password protected): <입력>` 이다. 비밀번호 입력 기능은 제공하지 않는다.

#### Scenario: HWP 5.0 암호 비트
- **WHEN** FileHeader 속성 `0x3` 인 합성 문서를 `convert_to_response` 로 넘긴다
- **THEN** status 415, `error.code == "encrypted"` 다

#### Scenario: HWPX 암호화 매니페스트
- **WHEN** `META-INF/manifest.xml` 에 `<odf:encryption-data>` 를 가진 합성 HWPX 를 변환한다
- **THEN** `EncryptedDocumentError` 가 난다
