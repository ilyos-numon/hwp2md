"""Library API: convert an HWP 5.0 file to a Markdown file."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .blocks import Block, Paragraph, Table
from .detect import detect_format
from .hwp5.reader import read_blocks as read_hwp5_blocks
from .hwpx.reader import read_blocks as read_hwpx_blocks
from .render import render_blocks


@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int
    table_count: int
    heading_count: int
    markdown: str


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
    markdown = render_blocks(blocks)
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
    return ConvertResult(
        source=source,
        output=output,
        paragraph_count=paragraph_count,
        table_count=table_count,
        heading_count=heading_count,
        markdown=markdown,
    )
