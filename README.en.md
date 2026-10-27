# hwp2md
[![PyPI](https://badgen.net/pypi/v/hwp2markdown)](https://pypi.org/project/hwp2markdown/)
[![Python](https://badgen.net/pypi/python/hwp2markdown)](https://pypi.org/project/hwp2markdown/)
[![CI](https://github.com/ilyos-numon/hwp2md/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ilyos-numon/hwp2md/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/hwp2markdown/month)](https://pepy.tech/projects/hwp2markdown)
[![Total downloads](https://static.pepy.tech/badge/hwp2markdown)](https://pepy.tech/projects/hwp2markdown)
[![GitHub stars](https://badgen.net/github/stars/ilyos-numon/hwp2md)](https://github.com/ilyos-numon/hwp2md/stargazers)
[![License: MIT](https://badgen.net/badge/license/MIT/blue)](https://github.com/ilyos-numon/hwp2md/blob/main/LICENSE)

[한국어](https://github.com/ilyos-numon/hwp2md/blob/main/README.md) · **English**

**Convert Korean HWP, HWPX and HWPML documents to Markdown — without Hancom Office, keeping headings, tables and images.**
Get text ready for LLM/RAG input, search and version control, from one engine shared by a CLI, a Python library and a local web UI.

![hwp2md converter — rendered preview on the left, Markdown source on the right](https://raw.githubusercontent.com/ilyos-numon/hwp2md/main/docs/images/convert-en.png)

> The document on screen is a fictional notice generated in code for the demo. It has nothing to do with any real organization or document.

## Try it now

| Way | For whom | Command or link |
|---|---|---|
| Browser | Right now, nothing to install | https://ilyos-numon.github.io/hwp2md/ → "Open converter" (your file never leaves the browser; first load takes about a minute) |
| uvx | Anyone with [uv](https://docs.astral.sh/uv/), one-off run | `uvx --from hwp2markdown hwp2md document.hwp -o out/` |
| Homebrew | macOS and Linux | `brew install ilyos-numon/tap/hwp2md` |
| Executable | Windows, macOS or Linux without Python | Download one file from the [latest release](https://github.com/ilyos-numon/hwp2md/releases/latest) |
| pip, uv, pipx | Python library and web preview too | `pip install 'hwp2markdown[web]'` (or `uv tool install`, `pipx install`) |

Once installed, the command is `hwp2md`. The PyPI distribution name is `hwp2markdown` (the `hwp2md` package on PyPI is a different project). Executable names, how to get past OS warnings and checksum verification are in [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md#12-실행-파일-python-필요-없음) (Korean).

<details>
<summary>Browser demo and landing page</summary>

![hwp2md landing page — "Turn HWP files into Markdown, structure intact"](https://raw.githubusercontent.com/ilyos-numon/hwp2md/main/docs/images/landing-en.png)

</details>

## 30-second example

Convert a short notice (`notice-demo.hwpx`) with headings, a table and an image.

```console
$ hwp2md notice-demo.hwpx -o out/
✓ notice-demo.hwpx → out/notice-demo.md
  단락 5개 · 표 1개 · 제목 5개 · 이미지 1개
  이미지: out/notice-demo_images/ (1 files)
```

The beginning of `out/notice-demo.md`:

```markdown
# 2026 Document Digitization Grant (Fictional Notice)

This is a fictional notice made for the hwp2md demo. It is not related to any real organization.

## 1. Overview

The program supports teams that turn paper and HWP archives into searchable text.

| Item | Details |
|---|---|
| Budget | 1.0 billion KRW in total (up to 50 million per team) |
| Period | Mar 2026 - Dec 2026 |
| How to apply | Online, with the attached form |

## 2. Process

Applications are reviewed on paper, then grantees are selected.

![그림 1](notice-demo_images/img_001.png)
```

The image is saved as `out/notice-demo_images/img_001.png` and linked from the Markdown by relative path. CLI messages and the image alt text are in Korean.

## Why hwp2md

- **No Hancom Office needed.** Pure Python with two dependencies: `olefile` and `lxml`.
- **Keeps the structure.** Outline levels become `#` headings, tables become Markdown tables, and images are extracted to files and linked in place. Footnotes and endnotes, equations (LaTeX), numbered and bulleted lists and hyperlinks come along too. Heading-based structure makes RAG chunking easier.
- **Your files stay with you.** The CLI, the library and `hwp2md serve` convert on your machine; the browser demo converts inside your browser.
- **Same result everywhere.** The CLI, the library and the web UI share one engine, and their output is byte-for-byte identical (compared in E2E tests).
- **Free, MIT licensed.**

## What it converts

| Input format | |
|---|---|
| HWP 5.0 (`.hwp`) | Supported, including distribution documents (copy/print restricted) |
| HWPX (`.hwpx`) | Supported |
| HWPML 2.x (`.hml`) | Supported |
| HWP 3.0 and older | Not supported (detected as not an HWP file) |
| DRM-protected or password-protected | Rejected, with the reason reported |

The format is detected from the file content, not the extension.

| Element | Result |
|---|---|
| Paragraphs and headings | Paragraphs; outline levels 1-6 → `#`-`######` |
| Tables | GFM tables. Multiple paragraphs in a cell become `<br>`; merged cells keep text in the origin cell (covered cells are empty) |
| Images | Saved byte-for-byte as `<name>_images/img_001.png` …, including images in table cells and text boxes |
| Footnotes and endnotes | `[^1]` references + definitions at the end |
| Equations | HWP equation script → LaTeX `$…$` (approximate; falls back to the original script as code) |
| Lists, links, captions, text boxes | Markdown lists, `[text](https://…)`, caption paragraphs, text inside text boxes |
| OOXML charts | A data table from the stored values |
| Headers/footers, memos, hidden comments | Left out on purpose; only counted |

What it does not do: character formatting (bold, fonts, colors), legacy chart data, WMF/EMF image conversion, recalculating fields such as page numbers. List numbers and equations are approximations. Elements it cannot extract do not vanish silently: they are reported by kind and count, like "건너뜀: 머리말·꼬리말 2개" (skipped: 2 headers/footers). The per-element status, reason and workaround are in [docs/extraction-limits.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/extraction-limits.md) (Korean).

## Usage

CLI:

```bash
hwp2md document.hwp -o out/    # out/document.md (+ out/document_images/)
hwp2md --version
```

Exit codes: 0 success · 1 conversion error · 2 file not found · 3 not an HWP file or an unsupported document.

Local web preview (needs the `web` extra):

```bash
hwp2md serve                  # http://localhost:8770 , works without internet
hwp2md serve --port 8771 --no-browser
```

Drop a file to see the preview and the Markdown side by side, and download the `.md` and images as one ZIP. The UI is available in Korean and English.

Library:

```python
from hwp2md import convert

result = convert("document.hwp", "out/")
print(result.markdown)
```

The in-memory `convert_bytes`, exception types, skip reports and the difference between server mode and browser mode are in [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md) (Korean).

## Privacy and security

- The web server converts uploads in memory and writes nothing to disk. Browser mode never sends file bytes to a server. Both are checked by E2E tests.
- Memos and hidden comments may contain author information, so their content is not output. The preview treats document content as untrusted input and escapes HTML.
- `hwp2md serve` is a `localhost` tool with no authentication; do not expose it publicly. Design details are in [docs/system-overview.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/system-overview.md) (Korean).

## FAQ

**Do I need Hancom Office?**
No. Python reads the files directly, based on the published file format documents.

**What about DRM- or password-protected documents?**
They are rejected, not unlocked. The CLI exits with code 3 and tells `DRM protected` and `password protected` apart. Remove the password in Hancom Office, or use a copy cleared by your security software. Distribution documents (copy/print restricted) are converted using the published procedure, so please respect the author's intent and your usage rights.

**HWP 3.0 or older?**
Not supported. Open the file in Hancom Office and save it as HWP 5.0 (`.hwp`) or HWPX, then convert.

**The executable shows a warning.**
The executables are not code-signed. On macOS run `xattr -d com.apple.quarantine hwp2md-macos-arm64`; on Windows SmartScreen click "More info → Run anyway". You can verify the files with `SHA256SUMS` from the same release.

**Is this the `hwp2md` package on PyPI?**
No. The `hwp2md` package on PyPI is a different project. Install this one as `hwp2markdown`; the command and import name are `hwp2md`.

**Does it work offline?**
Yes. The CLI, the library and `hwp2md serve` work without internet. The browser demo (GitHub Pages) and the "process in the browser only" mode of `serve` download Pyodide from a CDN on first load, so they need internet.

## Contributing and bug reports

- If a conversion looks wrong, please use the [bug report form](https://github.com/ilyos-numon/hwp2md/issues/new?template=bug_report.yml) (in Korean). Real documents can contain personal or internal information, so if possible attach a short new document that reproduces the problem.
- Feature ideas and questions go to [Issues](https://github.com/ilyos-numon/hwp2md/issues). The development setup and test commands are in [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md#8-개발) (Korean).

## Documentation

The documents below are written in Korean.

- [docs/usage.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/usage.md) — detailed usage (install, CLI, web preview, library, support table)
- [docs/extraction-limits.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/extraction-limits.md) — extraction limits (status, reason and workaround per element)
- [docs/feature-reference.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/feature-reference.md) — feature reference (including the web API and error model)
- [docs/system-overview.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/system-overview.md) — internals (modules, data flow, security, tests)
- [docs/decisions.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/decisions.md) — decision log (dates and reasons)
- [docs/releasing.md](https://github.com/ilyos-numon/hwp2md/blob/main/docs/releasing.md) — release procedure
- [CHANGELOG.md](https://github.com/ilyos-numon/hwp2md/blob/main/CHANGELOG.md) — changelog

## Roadmap

- [ ] RAG options: `--split section` (split by heading), `--meta` (JSON with table of contents, table count, image paths, source hash)
- [ ] Batch conversion of folders
- [ ] Better merged cells (`--table html` to keep rowspan/colspan)
- [ ] Quality comparison on 20 public-sector samples
- [x] Footnotes and endnotes, distribution documents, HWPML, PyPI, Homebrew and per-OS executables

## Out of scope

- Reverse conversion (md → hwp)
- Faithful reproduction of formatting (fonts, colors)

## License

- hwp2md is distributed under the [MIT License](https://github.com/ilyos-numon/hwp2md/blob/main/LICENSE).
- `src/hwp2md/equation/eqedit.py` and `tokens.py` are code taken from python-hwpx and follow the Apache License 2.0. The source, commit and modifications are recorded in [NOTICE](https://github.com/ilyos-numon/hwp2md/blob/main/NOTICE).
- This product was developed with reference to the HWP (.hwp) document file format specification published by Hancom Inc. (본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.)
