/* hwp2md 미리보기 화면. 변환·zip 은 모드 객체(MODES)에 위임한다. */
(function () {
  "use strict";

  const ERROR_TEXT = {
    empty: "빈 파일입니다",
    too_large: "파일이 너무 큽니다 (최대 50MB)",
    not_hwp: "HWP 5.0 또는 HWPX 파일이 아닙니다",
    unsupported: "지원하지 않는 HWP 문서라 변환할 수 없습니다",
    drm: "문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다. 보안 프로그램에서 해제한 뒤 다시 시도하세요",
    encrypted: "암호가 설정된 문서라 변환할 수 없습니다. 한글에서 암호를 해제한 뒤 다시 시도하세요",
  };

  const $ = (sel) => document.querySelector(sel);
  const els = {
    body: document.body,
    dropZone: $("#drop-zone"),
    fileInput: $("#file-input"),
    modeToggle: $("#mode-toggle"),
    modeStatus: $("#mode-status"),
    fileName: $("#file-name"),
    resultMeta: $("#result-meta"),
    preview: $("#preview"),
    raw: $("#raw"),
    download: $("#download"),
    error: $("#error"),
    skipped: $("#skipped"),
  };

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  const LINK_SCHEMES = ["http", "https", "mailto"];
  const DATA_IMAGE_RE = /^data:image\/(png|jpeg|gif|bmp|webp);base64,/;

  // 판정용 정규화: HTML 엔티티·퍼센트 인코딩을 풀고 제어문자·공백을 지운 뒤 소문자화.
  function normalizeUrl(url) {
    let s = String(url == null ? "" : url);
    s = new DOMParser().parseFromString(s, "text/html").documentElement.textContent || "";
    try {
      s = decodeURIComponent(s);
    } catch (_) {
      /* 잘못된 % 시퀀스는 그대로 둔다 */
    }
    return s.replace(/[\u0000-\u0020\u007f-\u009f\u00a0\u2000-\u200f\u2028\u2029\ufeff]/g, "").toLowerCase();
  }

  // 스킴이 없으면(상대 경로) 허용, 있으면 허용 목록만. image 는 data:image/*;base64 도 허용.
  function isSafeUrl(url, allowDataImage) {
    const s = normalizeUrl(url);
    const m = /^([^/?#]*?):/.exec(s);
    if (!m) return true;
    if (LINK_SCHEMES.includes(m[1])) return true;
    return Boolean(allowDataImage) && DATA_IMAGE_RE.test(s);
  }

  function titleAttr(title) {
    return title ? ' title="' + escapeHtml(title) + '"' : "";
  }

  // <br> 만 통과시키고 그 밖의 원시 HTML 은 이스케이프한다. link·image 는 URL 허용 목록으로 거른다.
  window.marked.use({
    renderer: {
      html(token) {
        const text = typeof token === "string" ? token : (token.text ?? "");
        return /^<br\s*\/?>$/i.test(text.trim()) ? "<br>" : escapeHtml(text);
      },
      // marked 12: text 는 이미 렌더된 인라인 HTML
      link(href, title, text) {
        if (href == null || !isSafeUrl(href, false)) return text;
        return '<a href="' + escapeHtml(href) + '"' + titleAttr(title) + ">" + text + "</a>";
      },
      // marked 12: text 는 alt 원문
      image(href, title, text) {
        if (href == null || !isSafeUrl(href, true)) return escapeHtml(text);
        return '<img src="' + escapeHtml(href) + '" alt="' + escapeHtml(text) + '"' +
          titleAttr(title) + ">";
      },
    },
  });

  function errorMessage(code, message) {
    if (Object.prototype.hasOwnProperty.call(ERROR_TEXT, code)) return ERROR_TEXT[code];
    return "변환 중 오류가 발생했습니다: " + (message || "");
  }

  class ConvertError extends Error {
    constructor(code, message) {
      super(message || code);
      this.code = code;
    }
  }

  async function readErrorBody(resp) {
    try {
      const body = await resp.json();
      if (body && body.error) return new ConvertError(body.error.code, body.error.message);
    } catch (_) {
      /* JSON 이 아니면 아래 기본 오류 */
    }
    return new ConvertError("convert_failed", "HTTP " + resp.status);
  }

  // 모드별 변환기. convert(file) -> {status, body}, zip(file) -> Blob
  const MODES = {
    server: {
      async convert(file) {
        const resp = await fetch("/api/convert?name=" + encodeURIComponent(file.name), {
          method: "POST",
          headers: { "Content-Type": "application/octet-stream" },
          body: file,
        });
        let body;
        try {
          body = await resp.json();
        } catch (_) {
          body = { error: { code: "convert_failed", message: "HTTP " + resp.status } };
        }
        return { status: resp.status, body: body };
      },
      async zip(file) {
        const resp = await fetch("/api/zip?name=" + encodeURIComponent(file.name), {
          method: "POST",
          headers: { "Content-Type": "application/octet-stream" },
          body: file,
        });
        if (!resp.ok) throw await readErrorBody(resp);
        return await resp.blob();
      },
    },
    // 브라우저 모드: Pyodide 안에서 처리하고 파일 바이트를 보내지 않는다. 로딩 중이면 끝날 때까지 기다린다.
    browser: {
      async convert(file) {
        return await window.Hwp2mdBrowser.convert(file);
      },
      async zip(file) {
        return await window.Hwp2mdBrowser.zip(file);
      },
    },
  };

  const MODE_STATUS_TEXT = {
    server: "서버 모드",
    loading: "브라우저 모드 준비 중…",
    browser: "브라우저 모드: 파일이 서버로 전송되지 않습니다",
    error: "브라우저 모드를 불러오지 못했습니다: ",
  };

  function setModeStatus(name, detail) {
    els.modeStatus.dataset.state = name;
    els.modeStatus.textContent = MODE_STATUS_TEXT[name] + (detail || "");
  }

  const state = {
    mode: "server",
    file: null,
    result: null,
    seq: 0,
  };

  function currentMode() {
    return MODES[state.mode];
  }

  function setState(value) {
    els.body.dataset.state = value;
  }

  function showError(text) {
    els.error.textContent = text;
    els.error.hidden = false;
  }

  function clearError() {
    els.error.textContent = "";
    els.error.hidden = true;
  }

  function clearResult() {
    state.result = null;
    els.download.disabled = true;
    els.resultMeta.textContent = "";
    els.preview.innerHTML = "";
    els.raw.textContent = "";
    clearSkipped();
  }

  const SKIPPED_PREFIX = "변환하지 못한 요소: ";
  const SKIPPED_SUFFIX = " (자세한 이유: docs/extraction-limits.md)";

  function clearSkipped() {
    els.skipped.textContent = "";
    els.skipped.hidden = true;
  }

  // 페이로드 skipped[] (서버·브라우저 모드 공통) 의 label 을 그대로 textContent 로 쓴다.
  function renderSkipped(skipped) {
    const items = Array.isArray(skipped) ? skipped.filter((s) => s && s.count > 0) : [];
    if (!items.length) {
      clearSkipped();
      return;
    }
    const parts = items.map((s) => String(s.label) + " " + s.count + "개");
    els.skipped.textContent = SKIPPED_PREFIX + parts.join(" · ") + SKIPPED_SUFFIX;
    els.skipped.hidden = false;
  }

  function renderResult(body) {
    const c = body.counts || {};
    els.resultMeta.textContent =
      "단락 " + c.paragraphs + "개 · 표 " + c.tables + "개 · 제목 " + c.headings +
      "개 · 이미지 " + c.images + "개";
    els.preview.innerHTML = window.marked.parse(body.preview_markdown || "");
    els.raw.textContent = body.markdown || "";
    renderSkipped(body.skipped);
    els.download.disabled = false;
  }

  async function handleFile(file) {
    if (!file) return;
    const seq = ++state.seq;
    state.file = file;
    els.fileName.textContent = file.name;
    clearError();
    clearResult();
    setState("converting");
    let res;
    try {
      res = await currentMode().convert(file);
    } catch (err) {
      res = { status: 0, body: { error: { code: "convert_failed", message: String(err && err.message || err) } } };
    }
    if (seq !== state.seq) return;
    const body = res.body || {};
    if (body.error) {
      showError(errorMessage(body.error.code, body.error.message));
      setState("error");
      return;
    }
    state.result = body;
    renderResult(body);
    setState("done");
  }

  async function handleDownload() {
    if (!state.file || !state.result) return;
    const name = state.result.name || "document";
    els.download.disabled = true;
    try {
      const blob = await currentMode().zip(state.file);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name + ".zip";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      showError(errorMessage(err && err.code, err && err.message));
    } finally {
      els.download.disabled = !state.result;
    }
  }

  // 드롭 영역
  els.dropZone.addEventListener("click", () => els.fileInput.click());
  els.dropZone.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      els.fileInput.click();
    }
  });
  els.dropZone.addEventListener("dragover", (ev) => {
    ev.preventDefault();
    els.dropZone.classList.add("dragover");
  });
  els.dropZone.addEventListener("dragleave", () => els.dropZone.classList.remove("dragover"));
  els.dropZone.addEventListener("drop", (ev) => {
    ev.preventDefault();
    els.dropZone.classList.remove("dragover");
    const file = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
    handleFile(file);
  });
  els.fileInput.addEventListener("change", () => {
    const file = els.fileInput.files && els.fileInput.files[0];
    handleFile(file);
    els.fileInput.value = "";
  });
  els.download.addEventListener("click", handleDownload);

  // 모드 토글: 켜면 Pyodide 를 불러와 브라우저 모드, 끄면 서버 모드 (Pyodide 는 메모리에 유지).
  async function handleModeToggle() {
    if (!els.modeToggle.checked) {
      state.mode = "server";
      setModeStatus("server");
      return;
    }
    if (!window.Hwp2mdBrowser) {
      els.modeToggle.checked = false;
      setModeStatus("error", "pyodide-runner.js 없음");
      return;
    }
    state.mode = "browser";
    setModeStatus("loading");
    try {
      await window.Hwp2mdBrowser.load();
      if (els.modeToggle.checked) setModeStatus("browser");
    } catch (err) {
      if (!els.modeToggle.checked) return;
      els.modeToggle.checked = false;
      state.mode = "server";
      setModeStatus("error", String((err && err.message) || err));
    }
  }
  els.modeToggle.disabled = false;
  els.modeToggle.addEventListener("change", handleModeToggle);

  // 다음 단계(브라우저 모드)가 모드를 추가·전환할 수 있게 노출한다.
  window.Hwp2mdApp = {
    MODES: MODES,
    els: els,
    setMode(name) {
      if (MODES[name]) state.mode = name;
    },
    get mode() {
      return state.mode;
    },
    handleFile: handleFile,
  };
})();
