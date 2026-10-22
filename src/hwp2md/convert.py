"""Library API: convert an HWP 5.0 file to a Markdown file."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .blocks import Block, Image, Paragraph, Table
from .detect import detect_format
from .hwp5.reader import read_blocks as read_hwp5_blocks
from .hwpx.reader import read_blocks as read_hwpx_blocks
from .images import image_dir_name
from .render import render_blocks


@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int
    table_count: int
    heading_count: int
    markdown: str
    image_count: int = 0  # Image 블록 수 (링크 수. 같은 파일 재참조도 센다)
    image_dir: Path | None = (
        None  # image_files 가 비어 있지 않을 때만 out_dir / image_dir_name(stem)
    )
    image_files: tuple[Path, ...] = ()  # 실제로 쓴 파일(고유 file_name 첫 등장 순)


def _write_images(blocks: Sequence[Block], target: Path) -> tuple[Path, ...]:
    """처음 보는 file_name 마다 target / file_name 에 data 를 쓴다.
    Image 가 0개면 target 을 만들지 않는다."""
    images = [b for b in blocks if isinstance(b, Image)]
    if not images:
        return ()
    target.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for img in images:
        if img.file_name in written:
            continue
        dest = target / img.file_name
        dest.write_bytes(img.data)
        written[img.file_name] = dest
    return tuple(written.values())


def read_blocks(path: Path) -> list[Block]:
    """포맷을 감지해 리더를 고른다.
    "hwp5" → read_hwp5_blocks, "hwpx" → read_hwpx_blocks. 예외는 그대로 전파."""
    if detect_format(path) == "hwpx":
        return read_hwpx_blocks(path)
    return read_hwp5_blocks(path)


def convert(path: str | Path, out_dir: str | Path = ".") -> ConvertResult:
    """path 가 파일이 아니면 FileNotFoundError(str(path)). <stem>.md 를 out_dir 에 UTF-8 로 저장."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(str(path))
    blocks = read_blocks(source)
    image_dir_rel = image_dir_name(source.stem)
    markdown = render_blocks(blocks, image_dir=image_dir_rel)
    paragraph_count = sum(
        isinstance(b, Paragraph) and bool(b.text) and b.level == 0 for b in blocks
    )
    heading_count = sum(isinstance(b, Paragraph) and bool(b.text) and b.level >= 1 for b in blocks)
    table_count = sum(isinstance(b, Table) for b in blocks)
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output = target_dir / f"{source.stem}.md"
    with output.open("w", encoding="utf-8", newline="\n") as f:
        f.write(markdown)
    files = _write_images(blocks, target_dir / image_dir_rel)
    image_count = sum(isinstance(b, Image) for b in blocks)
    return ConvertResult(
        source=source,
        output=output,
        paragraph_count=paragraph_count,
        table_count=table_count,
        heading_count=heading_count,
        markdown=markdown,
        image_count=image_count,
        image_dir=target_dir / image_dir_rel if files else None,
        image_files=files,
    )
