"""Check the hwp2markdown sdist and wheel before release.

Usage: python scripts/check_dist.py DIST_DIR [--tag vX.Y.Z] [--patterns FILE]

Prints one ``check_dist: FAIL <archive>: <member or ->: <reason>`` line per
violation and exits 1, or ``check_dist: OK sdist=<n> wheel=<m> version=<V>``
and exits 0. Usage errors and a missing DIST_DIR exit 2.
"""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from collections.abc import Iterable
from email.parser import HeaderParser
from pathlib import Path, PurePosixPath

DIST_NAME = "hwp2markdown"
PACKAGE = "hwp2md"
MAX_SIZE = 5 * 1024 * 1024
TAG_RE = re.compile(r"^v\d+\.\d+\.\d+$")
WHEEL_RE = re.compile(rf"^{DIST_NAME}-(?P<version>[^-]+)-py3-none-any\.whl$")

FORBIDDEN_PARTS = frozenset(
    {
        ".ai",
        "design",
        "openspec",
        "tests",
        "docs",
        ".impeccable",
        ".github",
        "logs",
        "out",
        "screenshots",
        "__pycache__",
    }
)
FORBIDDEN_NAMES = frozenset({"CLAUDE.md", "uv.lock", ".DS_Store"})
FORBIDDEN_SUFFIXES = frozenset({".hwp", ".hwpx", ".hwpml", ".pyc"})
SDIST_ALLOWED_FILES = frozenset(
    {"PKG-INFO", "pyproject.toml", "README.md", "LICENSE", "NOTICE", ".gitignore"}
)


class UsageError(Exception):
    """Input problem that maps to exit code 2."""


# (relative path, size, content)
Member = tuple[str, int, bytes]


def is_forbidden(path: str) -> bool:
    p = PurePosixPath(path)
    if any(part in FORBIDDEN_PARTS for part in p.parts):
        return True
    if p.name in FORBIDDEN_NAMES or p.name.startswith(".env"):
        return True
    return p.suffix.lower() in FORBIDDEN_SUFFIXES


def read_sdist(path: Path) -> list[Member]:
    members: list[Member] = []
    try:
        with tarfile.open(path, "r:gz") as tar:
            for info in tar.getmembers():
                if info.isdir():
                    continue
                parts = PurePosixPath(info.name).parts
                rel = "/".join(parts[1:]) if len(parts) > 1 else info.name
                data = b""
                if info.isfile():
                    fh = tar.extractfile(info)
                    if fh is not None:
                        data = fh.read()
                members.append((rel, info.size, data))
    except (tarfile.TarError, OSError) as exc:
        raise UsageError(f"cannot read {path.name}: {exc}") from exc
    return members


def read_wheel(path: Path) -> list[Member]:
    members: list[Member] = []
    try:
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                members.append((info.filename, info.file_size, zf.read(info)))
    except (zipfile.BadZipFile, OSError) as exc:
        raise UsageError(f"cannot read {path.name}: {exc}") from exc
    return members


def pattern_hits(members: Iterable[Member], patterns: list[re.Pattern[str]]) -> list[str]:
    hits: list[str] = []
    if not patterns:
        return hits
    for name, _size, data in members:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(p.search(line) for p in patterns):
                hits.append(f"{name}:{lineno}")
    return hits


def check_common(members: list[Member]) -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    for name, size, _data in members:
        if size > MAX_SIZE:
            problems.append((name, "too-large"))
    return problems


def check_sdist(members: list[Member]) -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    for name, _size, _data in members:
        if is_forbidden(name):
            problems.append((name, "forbidden-path"))
        elif name not in SDIST_ALLOWED_FILES and not name.startswith(f"src/{PACKAGE}/"):
            problems.append((name, "not-allowed"))
    return problems + check_common(members)


def check_wheel(members: list[Member], version: str) -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    dist_info = f"{DIST_NAME}-{version}.dist-info/"
    for name, _size, _data in members:
        if is_forbidden(name):
            problems.append((name, "forbidden-path"))
        elif not (name.startswith(f"{PACKAGE}/") or name.startswith(dist_info)):
            problems.append((name, "not-allowed"))
    names = {m[0] for m in members}
    for lic in ("LICENSE", "NOTICE"):
        if f"{dist_info}licenses/{lic}" not in names:
            problems.append((f"{dist_info}licenses/{lic}", "missing-license"))
    return problems + check_common(members)


def wheel_metadata_version(members: list[Member], version: str) -> str | None:
    target = f"{DIST_NAME}-{version}.dist-info/METADATA"
    for name, _size, data in members:
        if name == target:
            headers = HeaderParser().parsestr(data.decode("utf-8", errors="replace"))
            value = headers.get("Version")
            return value.strip() if value else None
    return None


def load_patterns(path: Path) -> list[re.Pattern[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise UsageError(f"cannot read patterns file: {exc}") from exc
    patterns: list[re.Pattern[str]] = []
    for lineno, line in enumerate(lines, start=1):
        p = line.strip()
        if not p or p.startswith("#"):
            continue
        try:
            patterns.append(re.compile(p, re.IGNORECASE))
        except re.error as exc:
            raise UsageError(f"invalid pattern at line {lineno}: {exc}") from exc
    return patterns


def run(dist_dir: Path, tag: str | None, patterns_file: Path | None) -> int:
    if not dist_dir.is_dir():
        raise UsageError(f"DIST_DIR not found: {dist_dir}")
    patterns = load_patterns(patterns_file) if patterns_file is not None else []

    failures: list[str] = []

    def fail(archive: str, member: str, reason: str) -> None:
        failures.append(f"check_dist: FAIL {archive}: {member}: {reason}")

    sdists = sorted(dist_dir.glob(f"{DIST_NAME}-*.tar.gz"))
    wheels = sorted(dist_dir.glob(f"{DIST_NAME}-*-py3-none-any.whl"))
    if len(sdists) != 1:
        fail(f"{DIST_NAME}-*.tar.gz", "-", "missing-artifact")
    if len(wheels) != 1:
        fail(f"{DIST_NAME}-*-py3-none-any.whl", "-", "missing-artifact")
    if failures:
        print("\n".join(failures))
        return 1

    sdist_path, wheel_path = sdists[0], wheels[0]
    match = WHEEL_RE.match(wheel_path.name)
    if match is None:
        raise UsageError(f"unexpected wheel file name: {wheel_path.name}")
    version = match.group("version")

    sdist_members = read_sdist(sdist_path)
    wheel_members = read_wheel(wheel_path)

    for member, reason in check_sdist(sdist_members):
        fail(sdist_path.name, member, reason)
    for hit in pattern_hits(sdist_members, patterns):
        fail(sdist_path.name, hit, "pattern-hit")

    for member, reason in check_wheel(wheel_members, version):
        fail(wheel_path.name, member, reason)
    for hit in pattern_hits(wheel_members, patterns):
        fail(wheel_path.name, hit, "pattern-hit")

    if tag is not None:
        meta_version = wheel_metadata_version(wheel_members, version)
        if not TAG_RE.match(tag) or meta_version is None or tag[1:] != meta_version:
            fail(wheel_path.name, "-", "version-mismatch")

    if failures:
        print("\n".join(failures))
        return 1
    print(f"check_dist: OK sdist={len(sdist_members)} wheel={len(wheel_members)} version={version}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_dist", description="Check hwp2markdown sdist and wheel contents."
    )
    parser.add_argument("dist_dir", metavar="DIST_DIR", type=Path)
    parser.add_argument("--tag", help="release tag vX.Y.Z; must match the wheel version")
    parser.add_argument("--patterns", type=Path, help="file of forbidden regex patterns")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        return run(args.dist_dir, args.tag, args.patterns)
    except UsageError as exc:
        print(f"check_dist: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
