"""Build the static GitHub Pages site for the in-browser converter.

Usage: python scripts/build_pages.py --out DIR [--static-dir DIR]

Writes ``.nojekyll``, ``index.html`` (about page), ``convert.html`` (converter),
``static/`` (assets without HTML) and ``pkg/hwp2md.zip`` into DIR. Every site
internal path is relative so the site works under any base path.

Exit codes: 0 success, 1 absolute path left after rewriting (one
``<rel>:<line>: absolute-path`` line per hit on stderr), 2 DIR is a non-empty
directory that is not a previous build (nothing is deleted).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from hwp2md.web.app import STATIC_DIR, build_runtime_zip

HTML_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ('"/static/', '"static/'),
    ('href="/about#', 'href="index.html#'),
    ('href="/about"', 'href="index.html"'),
    ('href="/"', 'href="convert.html"'),
)
FONTS_CSS = Path("static/vendor/fonts/fonts.css")
FONTS_REPLACEMENT = ('url("/static/vendor/fonts/', 'url("')
ABSOLUTE_RE = re.compile(r"""(src|href)="/[^/]|url\(["']?/[^/]""")
SITE_META = '<meta name="hwp2md-site" content="static">'
PKG_META = '<meta name="hwp2md-pkg-url" content="pkg/hwp2md.zip">'
MARKER = ".nojekyll"


class BuildError(Exception):
    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


class RefuseError(Exception):
    pass


def _rewrite_html(text: str, metas: list[str], rel: str) -> str:
    for old, new in HTML_REPLACEMENTS:
        text = text.replace(old, new)
    if "</title>" not in text:
        raise BuildError([f"{rel}:0: missing-title"])
    injected = "".join(f"\n  {m}" for m in metas)
    return text.replace("</title>", "</title>" + injected, 1)


def _check_absolute(out_dir: Path) -> list[str]:
    problems: list[str] = []
    files = sorted(p for p in out_dir.rglob("*") if p.is_file() and p.suffix in {".html", ".css"})
    for path in files:
        rel = path.relative_to(out_dir).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if ABSOLUTE_RE.search(line):
                problems.append(f"{rel}:{lineno}: absolute-path")
    return problems


def _prepare_out(out_dir: Path) -> None:
    if out_dir.exists():
        if not out_dir.is_dir():
            raise RefuseError(f"refuse: {out_dir} is not a previous build")
        if any(out_dir.iterdir()):
            if not (out_dir / MARKER).is_file():
                raise RefuseError(f"refuse: {out_dir} is not a previous build")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    (out_dir / MARKER).write_bytes(b"")


def build_site(out_dir: Path, static_dir: Path = STATIC_DIR) -> None:
    out_dir = Path(out_dir)
    static_dir = Path(static_dir)
    _prepare_out(out_dir)

    pages = (
        ("about.html", "index.html", [SITE_META]),
        ("index.html", "convert.html", [SITE_META, PKG_META]),
    )
    for src_name, dst_name, metas in pages:
        text = (static_dir / src_name).read_text(encoding="utf-8")
        (out_dir / dst_name).write_text(_rewrite_html(text, metas, dst_name), encoding="utf-8")

    shutil.copytree(static_dir, out_dir / "static", ignore=shutil.ignore_patterns("*.html"))

    fonts = out_dir / FONTS_CSS
    if fonts.is_file():
        old, new = FONTS_REPLACEMENT
        fonts.write_text(fonts.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    pkg = out_dir / "pkg"
    pkg.mkdir()
    (pkg / "hwp2md.zip").write_bytes(build_runtime_zip())

    problems = _check_absolute(out_dir)
    if problems:
        raise BuildError(problems)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the static GitHub Pages site.")
    parser.add_argument("--out", required=True, type=Path, help="output directory")
    parser.add_argument("--static-dir", type=Path, default=STATIC_DIR, help="source static dir")
    args = parser.parse_args(argv)
    try:
        build_site(args.out, args.static_dir)
    except RefuseError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except BuildError as exc:
        for problem in exc.problems:
            print(problem, file=sys.stderr)
        return 1
    print(f"build_pages: OK {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
