"""Frozen-executable entry point for the PyInstaller build of ``hwp2md``.

Forces UTF-8 on stdout/stderr when the console encoding is something else
(Windows pipes, ``LANG=C``) so ``✓`` and Korean text never raise
``UnicodeEncodeError``, then runs ``hwp2md.cli.main()``.
"""

from __future__ import annotations

import sys

from hwp2md.cli import main


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        encoding = (getattr(stream, "encoding", None) or "").lower().replace("-", "")
        if encoding != "utf8":
            reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    _force_utf8()
    raise SystemExit(main())
