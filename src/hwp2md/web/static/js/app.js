/* hwp2md V3 — 변환 화면. 변환은 MODES 에 위임한다 (서버 모드: /api, 브라우저 모드: Pyodide).
   상태: body[data-state] = idle | converting | done | error,  #mode-status[data-state] = server | loading | browser | error
   기존 UI 계약(id, data-state, 오류 코드 → 문구)을 그대로 지킨다. docs/feature-reference.md §9·§10 참고. */
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
  // 정적 사이트(<meta name="hwp2md-site" content="static">)는 브라우저 모드 고정, 링크는 상대 경로.
  const STATIC_SITE = (document.querySelector('meta[name="hwp2md-site"]') || {}).content === "static";
  const ABOUT_URL = STATIC_SITE ? "index.html" : "/about";
  const LIMITS_DOC = ABOUT_URL + "#limits";
  const MODE_STATUS_TEXT = {
    server: "서버 모드",
    loading: "브라우저 모드 준비 중…",
    browser: "브라우저 모드: 파일이 서버로 전송되지 않습니다",
    error: "브라우저 모드를 불러오지 못했습니다: ",
  };

  const $ = (s) => document.querySelector(s);
  const els = {
    body: document.body,
    dropZone: $("#drop-zone"),
    fileInput: $("#file-input"),
    modeToggle: $("#mode-toggle"),
    modeStatus: $("#mode-status"),
    fileChip: $("#file-chip"),
    fileName: $("#file-name"),
    fileBadge: $("#file-badge"),
    fileSize: $("#file-size"),
    resultMeta: $("#result-meta"),
    preview: $("#preview"),
    raw: $("#raw"),
    rawMeta: $("#raw-meta"),
    download: $("#download"),
    copy: $("#copy"),
    error: $("#error"),
    errorText: $("#error-text"),
    errorClose: $("#error-close"),
    skipped: $("#skipped"),
    toast: $("#toast"),
  };
  const PREVIEW_EMPTY = els.preview.innerHTML;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const hasGsap = Boolean(window.gsap);

  /* ---------- 안전한 미리보기 렌더러 (현재 UI 와 같은 규칙) ---------- */
  function escapeHtml(text) {
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  const LINK_SCHEMES = ["http", "https", "mailto"];
  const DATA_IMAGE_RE = /^data:image\/(png|jpeg|gif|bmp|webp);base64,/;
  function normalizeUrl(url) {
    let s = String(url == null ? "" : url);
    s = new DOMParser().parseFromString(s, "text/html").documentElement.textContent || "";
    try { s = decodeURIComponent(s); } catch (_) { /* 잘못된 % 시퀀스는 그대로 */ }
    return s.replace(/[\u0000-\u0020\u007f-\u009f\u00a0\u2000-\u200f\u2028\u2029\ufeff]/g, "").toLowerCase();
  }
  function isSafeUrl(url, allowDataImage) {
    const s = normalizeUrl(url);
    const m = /^([^/?#]*?):/.exec(s);
    if (!m) return true;
    if (LINK_SCHEMES.includes(m[1])) return true;
    return Boolean(allowDataImage) && DATA_IMAGE_RE.test(s);
  }
  const titleAttr = (t) => (t ? ' title="' + escapeHtml(t) + '"' : "");
  window.marked.use({
    renderer: {
      html(token) {
        const text = typeof token === "string" ? token : (token.text ?? "");
        return /^<br\s*\/?>$/i.test(text.trim()) ? "<br>" : escapeHtml(text);
      },
      link(href, title, text) {
        if (href == null || !isSafeUrl(href, false)) return text;
        return '<a href="' + escapeHtml(href) + '"' + titleAttr(title) + ">" + text + "</a>";
      },
      image(href, title, text) {
        if (href == null || !isSafeUrl(href, true)) return escapeHtml(text);
        return '<img src="' + escapeHtml(href) + '" alt="' + escapeHtml(text) + '"' + titleAttr(title) + ">";
      },
    },
  });

  /* ---------- 원문: 줄마다 span, Markdown 기호만 강조. textContent == markdown ---------- */
  function highlightLine(line) {
    const esc = escapeHtml(line);
    if (/^#{1,6}( |$)/.test(line)) return esc.replace(/^(#{1,6})/, '<span class="k">$1</span>');
    if (line.startsWith("|")) return esc.replace(/\|(-+\|)*/g, (m) => '<span class="k">' + m + "</span>");
    return esc.replace(/!\[|\]\(|(?<=\]\([^)]*)\)/g, (m) => '<span class="k">' + m + "</span>");
  }
  function renderRaw(markdown) {
    const lines = markdown.split("\n");
    if (lines.length && lines[lines.length - 1] === "") lines.pop();
    const endsWithNewline = markdown.endsWith("\n");
    els.raw.innerHTML = lines
      .map((l, i) => '<span class="l">' + highlightLine(l) + (i < lines.length - 1 || endsWithNewline ? "\n" : "") + "</span>")
      .join("");
    els.rawMeta.textContent = lines.length + "줄 · " + markdown.length.toLocaleString("ko-KR") + "자";
  }

  /* ---------- 상태 ---------- */
  const state = { mode: "server", file: null, result: null, seq: 0 };
  const currentMode = () => MODES[state.mode];
  const setState = (v) => { els.body.dataset.state = v; };

  function setModeStatus(name, detail) {
    els.modeStatus.dataset.state = name;
    els.modeStatus.textContent = MODE_STATUS_TEXT[name] + (detail || "");
  }

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

  function showError(text) { els.errorText.textContent = text; els.error.hidden = false; }
  function clearError() { els.errorText.textContent = ""; els.error.hidden = true; }

  // 건너뛴 요소 경고. 라벨은 응답의 skipped[].label 그대로, 글자는 textContent 로만 넣는다.
  function renderSkipped(list) {
    const items = Array.isArray(list) ? list.filter((s) => s && Number(s.count) > 0) : [];
    els.skipped.textContent = "";
    if (!items.length) { els.skipped.hidden = true; return; }
    const text = document.createElement("span");
    text.textContent = "변환하지 못한 요소: " + items.map((s) => String(s.label) + " " + Number(s.count) + "개").join(" · ");
    const link = document.createElement("a");
    link.href = LIMITS_DOC;
    link.textContent = "왜 빠졌나요?";
    els.skipped.append(text, " ", link);
    els.skipped.hidden = false;
  }

  function clearResult() {
    state.result = null;
    renderSkipped([]);
    els.download.disabled = true;
    els.copy.disabled = true;
    els.resultMeta.textContent = "";
    els.preview.innerHTML = PREVIEW_EMPTY;
    els.raw.textContent = "";
    els.rawMeta.textContent = "";
  }

  function formatSize(n) {
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    return (n / 1024 / 1024).toFixed(1) + " MB";
  }

  // 배지는 확장자 표시일 뿐이다. 실제 포맷 판별은 엔진이 파일 내용으로 한다.
  function showFile(file) {
    const ext = (file.name.split(".").pop() || "").toLowerCase();
    els.fileName.textContent = file.name;
    els.fileName.title = file.name;
    els.fileBadge.textContent = ext === "hwpx" ? "HWPX" : ext === "hwp" ? "HWP" : ext === "hml" ? "HWPML" : "";
    els.fileBadge.className = "badge " + (ext === "hwpx" ? "badge--hwpx" : "badge--hwp");
    els.fileSize.textContent = formatSize(file.size);
    const wasHidden = els.fileChip.hidden;
    els.fileChip.hidden = false;
    if (hasGsap && !reduced.matches) {
      gsap.fromTo(els.fileChip, { opacity: 0, x: wasHidden ? -8 : 0, y: wasHidden ? 0 : 4 }, { opacity: 1, x: 0, y: 0, duration: 0.32, ease: "expo.out" });
    }
  }

  const COUNT_LABELS = [["paragraphs", "단락"], ["tables", "표"], ["headings", "제목"], ["images", "이미지"]];
  // 숫자는 처음부터 최종값을 넣는다 (증가 모션 없음. E2E 가 글자를 바로 읽는다).
  function renderCounts(c) {
    els.resultMeta.innerHTML = COUNT_LABELS.map(([k, label]) => label + ' <b data-k="' + k + '">' + Number(c[k] || 0) + "</b>개").join(" · ");
  }

  function animateIn() {
    if (!hasGsap || reduced.matches) return;
    const blocks = Array.from(els.preview.children);
    const per = Math.min(0.04, 0.36 / Math.max(blocks.length, 1));
    gsap.from(blocks, { opacity: 0, y: 8, duration: 0.42, ease: "expo.out", stagger: per, clearProps: "transform,opacity" });
    const lines = Array.from(els.raw.children);
    const perLine = Math.min(0.02, 0.32 / Math.max(lines.length, 1));
    gsap.from(lines, { opacity: 0, x: -4, duration: 0.3, ease: "power2.out", stagger: perLine, clearProps: "transform,opacity" });
  }

  function renderResult(body) {
    renderCounts(body.counts || {});
    els.preview.innerHTML = window.marked.parse(body.preview_markdown || "");
    renderRaw(body.markdown || "");
    renderSkipped(body.skipped);
    els.download.disabled = false;
    els.copy.disabled = false;
    els.preview.parentElement.scrollTop = 0;
    els.raw.parentElement.scrollTop = 0;
    animateIn();
  }

  async function handleFile(file) {
    if (!file) return;
    const seq = ++state.seq;
    state.file = file;
    showFile(file);
    clearError();
    clearResult();
    setState("converting");
    let res;
    try {
      res = await currentMode().convert(file);
    } catch (err) {
      res = { status: 0, body: { error: { code: "convert_failed", message: String((err && err.message) || err) } } };
    }
    if (seq !== state.seq) return; // 더 나중에 넣은 파일의 결과가 우선
    const body = (res && res.body) || {};
    if (body.error) {
      showError(errorMessage(body.error.code, body.error.message));
      setState("error");
      return;
    }
    state.result = body;
    setState("done");
    renderResult(body);
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
      toast(name + ".zip 을 내려받았습니다");
    } catch (err) {
      showError(errorMessage(err && err.code, err && err.message));
    } finally {
      els.download.disabled = !state.result;
    }
  }

  /* ---------- 복사 + 토스트 ---------- */
  let toastTimer = 0;
  function toast(text) {
    els.toast.textContent = text;
    els.toast.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => els.toast.classList.remove("is-on"), 1500);
  }
  async function handleCopy() {
    if (!state.result) return;
    const text = state.result.markdown || "";
    try {
      await navigator.clipboard.writeText(text);
    } catch (_) {
      const range = document.createRange();
      range.selectNodeContents(els.raw);
      const sel = getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      document.execCommand("copy");
      sel.removeAllRanges();
    }
    els.copy.classList.add("is-done");
    els.copy.querySelector("span").textContent = "복사됨";
    setTimeout(() => { els.copy.classList.remove("is-done"); els.copy.querySelector("span").textContent = "복사"; }, 1500);
    toast("Markdown 원문을 복사했습니다");
  }

  /* ---------- 파일 입력: 클릭·키보드·드롭 (페이지 어디에 놓아도 받는다) ---------- */
  els.dropZone.addEventListener("click", (e) => {
    if (e.target === els.fileInput) return;
    els.fileInput.click();
  });
  els.dropZone.addEventListener("keydown", (ev) => {
    if (ev.target !== els.dropZone) return;
    if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); els.fileInput.click(); }
  });
  els.fileInput.addEventListener("change", () => {
    const file = els.fileInput.files && els.fileInput.files[0];
    handleFile(file);
    els.fileInput.value = "";
  });

  let dragDepth = 0;
  const hasFiles = (ev) => ev.dataTransfer && Array.from(ev.dataTransfer.types || []).includes("Files");
  window.addEventListener("dragenter", (ev) => {
    if (!hasFiles(ev)) return;
    ev.preventDefault();
    dragDepth += 1;
    els.dropZone.classList.add("dragover");
  });
  window.addEventListener("dragover", (ev) => {
    if (!hasFiles(ev)) return;
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "copy";
  });
  window.addEventListener("dragleave", (ev) => {
    if (!hasFiles(ev)) return;
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) els.dropZone.classList.remove("dragover");
  });
  window.addEventListener("drop", (ev) => {
    if (!hasFiles(ev)) return;
    ev.preventDefault();
    dragDepth = 0;
    els.dropZone.classList.remove("dragover");
    handleFile(ev.dataTransfer.files[0]);
  });

  els.download.addEventListener("click", handleDownload);
  els.copy.addEventListener("click", handleCopy);
  els.errorClose.addEventListener("click", clearError);

  /* ---------- 모드 전환 ---------- */
  async function handleModeToggle() {
    if (!els.modeToggle.checked) {
      state.mode = "server";
      setModeStatus("server");
      return;
    }
    if (!window.Hwp2mdBrowser) {
      els.modeToggle.checked = false;
      state.mode = "server";
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
  els.modeToggle.addEventListener("change", handleModeToggle);

  // 정적 사이트: 서버가 없으므로 스위치를 숨기고 브라우저 모드로 시작한다. 실패해도 서버로 돌아가지 않는다.
  async function startStaticSite() {
    const sw = els.modeToggle.closest("label.switch");
    if (sw) {
      sw.hidden = true;
      sw.style.display = "none"; // .switch { display: inline-flex } 가 hidden 속성을 덮으므로
    }
    els.modeToggle.checked = true;
    els.modeToggle.disabled = true;
    state.mode = "browser";
    setModeStatus("loading");
    try {
      if (!window.Hwp2mdBrowser) throw new Error("pyodide-runner.js 없음");
      await window.Hwp2mdBrowser.load();
      setModeStatus("browser");
    } catch (err) {
      setModeStatus("error", String((err && err.message) || err));
    }
  }
  if (STATIC_SITE) startStaticSite();

  /* ---------- 좁은 화면: 미리보기 / Markdown 탭 ---------- */
  const tabs = [$("#tab-preview"), $("#tab-raw")];
  const panes = [$("#pane-preview"), $("#pane-raw")];
  const narrow = window.matchMedia("(max-width: 899px)");
  let activeTab = 0;
  function applyTabs() {
    tabs.forEach((t, i) => {
      const on = i === activeTab;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      panes[i].hidden = narrow.matches && !on;
    });
  }
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => { activeTab = i; applyTabs(); });
    t.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      activeTab = 1 - i;
      applyTabs();
      tabs[activeTab].focus();
    });
  });
  narrow.addEventListener("change", applyTabs);
  applyTabs();

  window.Hwp2mdApp = {
    MODES: MODES,
    els: els,
    setMode(name) { if (MODES[name]) state.mode = name; },
    get mode() { return state.mode; },
    handleFile: handleFile,
    get staticSite() { return STATIC_SITE; },
  };
})();
