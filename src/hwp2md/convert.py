"""Library API: convert an HWP 5.0 file to a Markdown file."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .hwp5.reader import read_paragraphs
from .render import render_markdown


@dataclass(frozen=True)
class ConvertResult:
    source: Path
    output: Path
    paragraph_count: int
    markdown: str


def convert(path: str | Path, out_dir: str | Path = ".") -> ConvertResult:
    """path 가 파일이 아니면 FileNotFoundError(str(path)). <stem>.md 를 out_dir 에 UTF-8 로 저장."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(str(path))
    paragraphs = [p for p in read_paragraphs(source) if p]
    markdown = render_markdown(paragraphs)
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output = target_dir / f"{source.stem}.md"
    with output.open("w", encoding="utf-8", newline="\n") as f:
        f.write(markdown)
    return ConvertResult(
        source=source, output=output, paragraph_count=len(paragraphs), markdown=markdown
    )
