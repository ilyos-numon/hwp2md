"""hwp2md — HWP 5.0·HWPX 문서를 Markdown 으로 변환한다.

본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.
"""

from .blocks import Block, Image, Link, ListInfo, Math, Note, NoteRef, Paragraph, Table
from .convert import ConvertResult, convert
from .detect import DocFormat, detect_format
from .errors import (
    DrmProtectedError,
    EncryptedDocumentError,
    Hwp2mdError,
    NotHwpFileError,
    UnsupportedHwpError,
)
from .memory import MemoryResult, convert_bytes
from .skips import SkipCounter

__version__ = "0.1.0"

__all__ = [
    "Block",
    "ConvertResult",
    "DocFormat",
    "DrmProtectedError",
    "EncryptedDocumentError",
    "Hwp2mdError",
    "Image",
    "Link",
    "ListInfo",
    "Math",
    "MemoryResult",
    "NotHwpFileError",
    "Note",
    "NoteRef",
    "Paragraph",
    "SkipCounter",
    "Table",
    "UnsupportedHwpError",
    "__version__",
    "convert",
    "convert_bytes",
    "detect_format",
]
