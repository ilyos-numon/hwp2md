/* 브라우저 전용 모드: Pyodide 로 브라우저 안에서 hwp2md 를 실행한다.
   파일 바이트는 페이지 밖으로 나가지 않는다 (네트워크는 Pyodide·lxml·/pkg/hwp2md.zip GET 뿐). */
(function () {
  "use strict";

  const PYODIDE_VERSION = "0.27.7";
  const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
  const PKG_DIR = "/hwp2md_pkg";
  // 정적 사이트는 <meta name="hwp2md-pkg-url"> 로 상대 경로를 준다. 없으면 serve 경로.
  const PKG_URL = (document.querySelector('meta[name="hwp2md-pkg-url"]') || {}).content || "/pkg/hwp2md.zip";

  const PY_SETUP = `
import sys
sys.path.insert(0, ${JSON.stringify(PKG_DIR)})
import json
import hwp2md.memory
from hwp2md.memory import build_zip, convert_bytes, convert_to_response, error_code


def _h2m_convert(data, name):
    status, body = convert_to_response(data.to_bytes(), name)
    return json.dumps({"status": status, "body": body}, ensure_ascii=False)


def _h2m_zip(data, name):
    try:
        return build_zip(convert_bytes(data.to_bytes(), name))
    except Exception as exc:  # 오류는 서버 모드와 같은 code 로 돌려준다
        return json.dumps({"code": error_code(exc), "message": str(exc)}, ensure_ascii=False)
`;

  let pyodide = null;
  let loading = null;

  function injectScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error("failed to load " + src));
      document.head.appendChild(s);
    });
  }

  async function doLoad() {
    if (typeof window.loadPyodide !== "function") {
      await injectScript(PYODIDE_BASE + "pyodide.js");
    }
    const py = await window.loadPyodide({ indexURL: PYODIDE_BASE });
    let pkgErr = null;
    await py.loadPackage("lxml", {
      errorCallback: (m) => { pkgErr = (pkgErr ? pkgErr + "; " : "") + m; },
    });
    if (pkgErr) throw new Error("lxml: " + pkgErr);
    const resp = await fetch(PKG_URL, { method: "GET", cache: "no-store" });
    if (!resp.ok) throw new Error(PKG_URL + " HTTP " + resp.status);
    py.unpackArchive(await resp.arrayBuffer(), "zip", { extractDir: PKG_DIR });
    py.runPython(PY_SETUP);
    pyodide = py;
  }

  // 한 번만 불러온다. 실패하면 다음 호출에서 다시 시도할 수 있게 비운다.
  function load() {
    if (pyodide) return Promise.resolve();
    if (!loading) {
      loading = doLoad().catch((err) => {
        loading = null;
        throw err;
      });
    }
    return loading;
  }

  async function callPy(fnName, file) {
    await load();
    const data = new Uint8Array(await file.arrayBuffer());
    const fn = pyodide.globals.get(fnName);
    try {
      return fn(data, file.name);
    } finally {
      fn.destroy();
    }
  }

  async function convert(file) {
    const text = await callPy("_h2m_convert", file);
    return JSON.parse(text);
  }

  async function zip(file) {
    const out = await callPy("_h2m_zip", file);
    if (typeof out === "string") {
      const info = JSON.parse(out);
      const err = new Error(info.message || info.code);
      err.code = info.code;
      throw err;
    }
    try {
      const buf = out.getBuffer("u8");
      try {
        return new Blob([new Uint8Array(buf.data)], { type: "application/zip" });
      } finally {
        buf.release();
      }
    } finally {
      out.destroy();
    }
  }

  window.Hwp2mdBrowser = {
    load: load,
    convert: convert,
    zip: zip,
  };
})();
