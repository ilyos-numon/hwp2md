"""hwp2md exception types."""


class Hwp2mdError(Exception):
    """hwp2md 최상위 예외 (CLI 종료 코드 1)"""


class NotHwpFileError(Hwp2mdError):
    """OLE 아님 / FileHeader 시그니처 불일치 / BodyText/Section0 없음 (종료 코드 3)"""


class UnsupportedHwpError(Hwp2mdError):
    """암호화 또는 배포용 문서 (종료 코드 3)"""


class DrmProtectedError(UnsupportedHwpError):
    """DRM 래핑 파일 또는 HWP 5.0 DRM 비트 (종료 코드 3)"""


class EncryptedDocumentError(UnsupportedHwpError):
    """비밀번호 문서 (종료 코드 3)"""


class EmptyInputError(Hwp2mdError):
    """메모리 변환 입력이 0바이트"""


class InputTooLargeError(Hwp2mdError):
    """메모리 변환 입력이 MAX_INPUT_BYTES 초과"""
