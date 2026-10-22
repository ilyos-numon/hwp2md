from .blocks import Block, Paragraph, Table
from .convert import ConvertResult, convert
from .detect import DocFormat, detect_format
from .errors import Hwp2mdError, NotHwpFileError, UnsupportedHwpError

__version__ = "0.1.0"

__all__ = [
    "Block",
    "ConvertResult",
    "DocFormat",
    "Hwp2mdError",
    "NotHwpFileError",
    "Paragraph",
    "Table",
    "UnsupportedHwpError",
    "__version__",
    "convert",
    "detect_format",
]
