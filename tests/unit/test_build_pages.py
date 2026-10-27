"""Unit tests for scripts/build_pages.py (static GitHub Pages build)."""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest

from hwp2md.web.app import STATIC_DIR, build_runtime_zip

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_pages.py"
ABSOLUTE_RE = re.compile(r"""(src|href)="/[^/]|url\(["']?/[^/]""")


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_pages", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_pages"] = module
    spec.loader.exec_module(module)
    return module


bp = _load()


def test_build_structure_zip_and_meta(tmp_path: Path) -> None:
    out = tmp_path / "site"
    assert bp.main(["--out", str(out)]) == 0

    assert sorted(p.name for p in out.iterdir()) == [
        ".nojekyll",
        "convert.html",
        "index.html",
        "pkg",
        "static",
    ]
    assert (out / ".nojekyll").read_bytes() == b""
    assert (out / "pkg" / "hwp2md.zip").read_bytes() == build_runtime_zip()
    assert not list((out / "static").rglob("*.html"))
    for rel in ("css/app.css", "js/app.js", "pyodide-runner.js", "vendor/marked.min.js"):
        assert (out / "static" / rel).is_file(), rel

    convert = (out / "convert.html").read_text(encoding="utf-8")
    assert convert.count('<meta name="hwp2md-site" content="static">') == 1
    assert convert.count('<meta name="hwp2md-pkg-url" content="pkg/hwp2md.zip">') == 1
    after_title = convert.split("</title>", 1)[1].lstrip().splitlines()
    assert after_title[0].strip() == '<meta name="hwp2md-site" content="static">'
    assert after_title[1].strip() == '<meta name="hwp2md-pkg-url" content="pkg/hwp2md.zip">'

    index = (out / "index.html").read_text(encoding="utf-8")
    assert index.count('<meta name="hwp2md-site" content="static">') == 1
    assert "hwp2md-pkg-url" not in index
    assert 'href="convert.html"' in index
    assert 'href="index.html#limits"' in convert


def test_no_absolute_paths(tmp_path: Path) -> None:
    out = tmp_path / "site"
    bp.build_site(out)
    hits = []
    for path in out.rglob("*"):
        if path.suffix in {".html", ".css"}:
            for line in path.read_text(encoding="utf-8").splitlines():
                if ABSOLUTE_RE.search(line) or '"/api/' in line:
                    hits.append(f"{path}: {line}")
    assert hits == []
    fonts = (out / "static" / "vendor" / "fonts" / "fonts.css").read_text(encoding="utf-8")
    assert 'url("PretendardVariable.woff2")' in fonts


def test_bad_source_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    static = tmp_path / "static"
    shutil.copytree(STATIC_DIR, static)
    index = static / "index.html"
    bad = '<script src="/x.js"></script></body>'
    index.write_text(
        index.read_text(encoding="utf-8").replace("</body>", bad),
        encoding="utf-8",
    )
    code = bp.main(["--out", str(tmp_path / "site"), "--static-dir", str(static)])
    assert code == 1
    err = capsys.readouterr().err
    assert re.search(r"^convert\.html:\d+: absolute-path$", err, re.MULTILINE), err


def test_refuses_foreign_dir(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "mine"
    out.mkdir()
    keep = out / "keep.txt"
    keep.write_text("precious", encoding="utf-8")
    assert bp.main(["--out", str(out)]) == 2
    assert keep.read_text(encoding="utf-8") == "precious"
    assert sorted(p.name for p in out.iterdir()) == ["keep.txt"]
    assert "refuse:" in capsys.readouterr().err


def test_rebuild_over_previous_build(tmp_path: Path) -> None:
    out = tmp_path / "site"
    bp.build_site(out)
    (out / "stale.txt").write_text("old", encoding="utf-8")
    bp.build_site(out)
    assert not (out / "stale.txt").exists()
    assert (out / ".nojekyll").is_file()
