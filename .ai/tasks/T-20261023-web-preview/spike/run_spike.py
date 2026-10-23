"""S2 spike: prove hwp2md converts the 5 fixtures inside CDN Pyodide + lxml.

Run: uv run python .ai/tasks/T-20261023-web-preview/spike/run_spike.py
Last stdout line: ``SPIKE OK 5/5`` or ``SPIKE FAIL <reason>``.
"""

from __future__ import annotations

import difflib
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

import olefile
from playwright.sync_api import sync_playwright

import hwp2md

SPIKE_DIR = Path(__file__).resolve().parent
PROJECT = SPIKE_DIR.parents[3]
SRC = PROJECT / "src" / "hwp2md"
FIXTURES = PROJECT / "tests" / "fixtures"
WORK = Path("/private/tmp/claude-501/hwp2md-spike")
WWW = WORK / "www"
PORT = 8799
BASE_URL = f"http://localhost:{PORT}/spike.html"
FIRST_VERSIONS = ["0.27.7", "0.26.4"]
FALLBACK_028 = "0.28.3"
PAGE_TIMEOUT_MS = 240_000
LOAD_LIMIT_SECONDS = 120.0
NETWORK_MARKERS = ("network", "Failed to fetch", "NetworkError", "ERR_", "net::")


def log(msg: str) -> None:
    print(msg, flush=True)


def samples() -> list[Path]:
    hwp = sorted(FIXTURES.glob("*.hwp"))
    hwpx = sorted((FIXTURES / "hwpx").glob("*.hwpx"))
    return hwp + hwpx


def latest_028() -> str:
    url = "https://data.jsdelivr.com/v1/packages/npm/pyodide"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.load(resp)
        versions = [v["version"] for v in data.get("versions", [])]
        stable = [v for v in versions if v.startswith("0.28.") and v.count(".") == 2]
        stable = [v for v in stable if v.split(".")[2].isdigit()]
        if stable:
            return max(stable, key=lambda v: int(v.split(".")[2]))
    except Exception as exc:  # noqa: BLE001 - spike: fall back to a known version
        log(f"WARN jsdelivr version list failed: {exc!r}")
    return FALLBACK_028


def build_www(sample_paths: list[Path]) -> None:
    if WWW.exists():
        shutil.rmtree(WWW)
    (WWW / "samples").mkdir(parents=True)
    with zipfile.ZipFile(WWW / "pkg.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(SRC.rglob("*.py")):
            rel = f.relative_to(SRC)
            if rel.parts[0] in ("web", "__pycache__") or "__pycache__" in rel.parts:
                continue
            zf.write(f, f"hwp2md/{rel.as_posix()}")
        ole_dir = Path(olefile.__file__).parent
        for f in sorted(ole_dir.glob("*.py")):
            zf.write(f, f"olefile/{f.name}")
    for s in sample_paths:
        shutil.copy2(s, WWW / "samples" / s.name)
    (WWW / "samples.json").write_text(
        json.dumps([s.name for s in sample_paths], ensure_ascii=False), encoding="utf-8"
    )
    shutil.copy2(SPIKE_DIR / "spike.html", WWW / "spike.html")


def native_markdown(sample_paths: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    with tempfile.TemporaryDirectory(dir=WORK) as tmp:
        for s in sample_paths:
            out[s.name] = hwp2md.convert(s, Path(tmp) / s.stem).markdown
    return out


def wait_http(url: str) -> None:
    for _ in range(50):
        try:
            with urllib.request.urlopen(url, timeout=2):
                return
        except Exception:  # noqa: BLE001
            time.sleep(0.2)
    raise RuntimeError(f"http.server not reachable: {url}")


def open_page(browser, version: str, convert: bool) -> dict:  # type: ignore[no-untyped-def]
    ctx = browser.new_context()
    try:
        page = ctx.new_page()
        page.on("console", lambda m: log(f"  [console] {m.text}") if m.type == "error" else None)
        page.goto(f"{BASE_URL}?v={version}&convert={1 if convert else 0}", wait_until="commit")
        page.wait_for_function("window.__spike !== null", timeout=PAGE_TIMEOUT_MS)
        return page.evaluate("window.__spike")
    finally:
        ctx.close()


def is_network_error(res: dict) -> bool:
    err = res.get("error", "")
    return res.get("stage") in ("script", "loadPyodide", "loadPackage") and any(
        m in err for m in NETWORK_MARKERS
    )


def try_version(browser, version: str, native: dict[str, str]) -> tuple[str, dict | None]:  # type: ignore[no-untyped-def]
    """Returns (status, first_result). status: ok | network | lxml | import | diff | error."""
    res: dict = {}
    for attempt in range(1, 4):
        try:
            res = open_page(browser, version, convert=True)
        except Exception as exc:  # noqa: BLE001
            res = {"ok": False, "stage": "timeout", "error": repr(exc)}
        if res.get("ok") or not is_network_error(res):
            break
        log(f"  attempt {attempt} network error: {res.get('error')}")
    else:
        return "network", res
    if not res.get("ok"):
        log(f"  FAIL stage={res.get('stage')} error={res.get('error')}")
        stage = res.get("stage")
        if stage == "loadPackage":
            return "lxml", res
        if stage in ("import", "unpack"):
            return "import", res
        return "error", res
    return "ok", res


def compare(res: dict, native: dict[str, str]) -> int:
    ok = 0
    for name, md in native.items():
        got = res.get("results", {}).get(name, {})
        if "error" in got:
            log(f"FIXTURE {name} DIFF (pyodide error: {got['error'][-500:]})")
            continue
        if got.get("markdown") == md:
            log(f"FIXTURE {name} OK")
            ok += 1
        else:
            log(f"FIXTURE {name} DIFF")
            diff = difflib.unified_diff(
                md.splitlines(), (got.get("markdown") or "").splitlines(),
                "native", "pyodide", lineterm="",
            )
            for line in list(diff)[:20]:
                log(f"  {line}")
    return ok


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    sample_paths = samples()
    log(f"SAMPLES={len(sample_paths)} " + ", ".join(s.name for s in sample_paths))
    if len(sample_paths) != 5:
        log(f"SPIKE FAIL expected 5 samples, found {len(sample_paths)}")
        return 1
    build_www(sample_paths)
    native = native_markdown(sample_paths)

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "localhost"],
        cwd=WWW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    final = "SPIKE FAIL no version produced 5/5"
    try:
        wait_http(BASE_URL)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                versions = [*FIRST_VERSIONS, None]
                failures: list[str] = []
                for v in versions:
                    version = v or latest_028()
                    log(f"TRY PYODIDE_VERSION={version}")
                    status, res = try_version(browser, version, native)
                    if status == "network":
                        final = f"SPIKE FAIL network errors 3x on {version} (BLOCKED cond 1)"
                        break
                    if status != "ok" or res is None:
                        failures.append(status)
                        if status == "import":
                            err = res and res.get("error")
                            final = f"SPIKE FAIL import hwp2md failed on {version}: {err}"
                        continue
                    ok = compare(res, native)
                    if ok != len(native):
                        final = (
                            f"SPIKE FAIL {ok}/{len(native)} markdown match on {version}"
                            " (BLOCKED cond 4)"
                        )
                        break
                    times = [float(res["load_seconds"])]
                    for _ in range(2):
                        r = open_page(browser, version, convert=False)
                        if not r.get("ok"):
                            raise RuntimeError(f"reload failed: {r}")
                        times.append(float(r["load_seconds"]))
                    log(f"PYODIDE_VERSION={version}")
                    log(f"LXML_VERSION={res.get('lxml_version')}")
                    log("LOAD_SECONDS=" + ",".join(f"{t:.2f}" for t in times))
                    median = statistics.median(times)
                    if median > LOAD_LIMIT_SECONDS:
                        final = f"SPIKE FAIL load median {median:.1f}s > 120s (BLOCKED cond 5)"
                    else:
                        final = f"SPIKE OK {ok}/{len(native)}"
                    break
                else:
                    if failures and all(f == "lxml" for f in failures):
                        final = (
                            "SPIKE FAIL lxml loadPackage failed on all versions (BLOCKED cond 2)"
                        )
            finally:
                browser.close()
    finally:
        server.terminate()
        server.wait(10)
    log(final)
    return 0 if final.startswith("SPIKE OK") else 1


if __name__ == "__main__":
    raise SystemExit(main())
