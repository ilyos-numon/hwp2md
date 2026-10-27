/* 화면 언어(ko/en). 결정: ?lang= → 저장값 → 브라우저 언어(ko* 면 한국어, 그 밖은 영어).
   HTML 원문 한국어가 곧 ko 값이다. data-i18n / data-i18n-html / data-i18n-attr 로 표시한 요소만 바꾼다.
   KO 는 JS 가 쓰는 문구, EN 은 JS 문구 + 변환 화면 HTML 문구의 영어값. 소개 화면 영어값은 HWP2MD_I18N_EXTRA. */
(function () {
  "use strict";

  const STORE_KEY = "hwp2md-lang";
  const LANGS = ["ko", "en"];

  const KO = {
    "mode.server": "서버 모드",
    "mode.loading": "브라우저 모드 준비 중…",
    "mode.browser": "브라우저 모드: 파일이 서버로 전송되지 않습니다",
    "mode.error": "브라우저 모드를 불러오지 못했습니다: ",
    "mode.no_runner": "pyodide-runner.js 없음",
    "error.empty": "빈 파일입니다",
    "error.too_large": "파일이 너무 큽니다 (최대 50MB)",
    "error.not_hwp": "HWP 5.0 또는 HWPX 파일이 아닙니다",
    "error.unsupported": "지원하지 않는 HWP 문서라 변환할 수 없습니다",
    "error.drm": "문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다. 보안 프로그램에서 해제한 뒤 다시 시도하세요",
    "error.encrypted": "암호가 설정된 문서라 변환할 수 없습니다. 한글에서 암호를 해제한 뒤 다시 시도하세요",
    "error.generic": "변환 중 오류가 발생했습니다: ",
    "skipped.prefix": "변환하지 못한 요소: ",
    "skipped.item": "{label} {n}개",
    "skipped.why": "왜 빠졌나요?",
    "count.paragraphs": "단락 {n}개",
    "count.tables": "표 {n}개",
    "count.headings": "제목 {n}개",
    "count.images": "이미지 {n}개",
    "raw.meta": "{lines}줄 · {chars}자",
    "toast.zip": "{name}.zip 을 내려받았습니다",
    "toast.copied": "Markdown 원문을 복사했습니다",
    "copy.idle": "복사",
    "copy.done": "복사됨",
    "theme.to_dark": "다크 모드로 전환",
    "theme.to_light": "라이트 모드로 전환",
  };

  const EN = {
    "mode.server": "Server mode",
    "mode.loading": "Preparing browser mode…",
    "mode.browser": "Browser mode: files are not sent to a server",
    "mode.error": "Could not load browser mode: ",
    "mode.no_runner": "pyodide-runner.js not found",
    "error.empty": "The file is empty",
    "error.too_large": "The file is too large (max 50MB)",
    "error.not_hwp": "Not an HWP 5.0 or HWPX file",
    "error.unsupported": "This HWP document is not supported and cannot be converted",
    "error.drm": "This file is protected by document security (DRM) and cannot be converted. Remove the protection in your security software and try again",
    "error.encrypted": "This document is password-protected and cannot be converted. Remove the password in Hangul and try again",
    "error.generic": "An error occurred during conversion: ",
    "skipped.prefix": "Not converted: ",
    "skipped.item": "{label} ({n})",
    "skipped.why": "Why?",
    "count.paragraphs": "{n} paragraphs",
    "count.paragraphs_one": "{n} paragraph",
    "count.tables": "{n} tables",
    "count.tables_one": "{n} table",
    "count.headings": "{n} headings",
    "count.headings_one": "{n} heading",
    "count.images": "{n} images",
    "count.images_one": "{n} image",
    "raw.meta": "{lines} lines · {chars} chars",
    "toast.zip": "Downloaded {name}.zip",
    "toast.copied": "Copied the Markdown source",
    "copy.idle": "Copy",
    "copy.done": "Copied",
    "theme.to_dark": "Switch to dark mode",
    "theme.to_light": "Switch to light mode",
    "lang.toggle_text": "KO",
    "lang.toggle_label": "한국어로 보기",
    "about.open_converter": "Open converter",
    // 변환 화면 (index.html)
    "convert.title": "hwp2md converter",
    "convert.heading": "HWP documents to Markdown",
    "convert.lead": "Choose an HWP, HWPX or HWPML file and check the conversion result.",
    "common.brand_label": "Go to the hwp2md overview",
    "common.nav_label": "Site",
    "common.nav_about": "About",
    "convert.switch_label": "Process in the browser only",
    "convert.error_close": "Close error",
    "convert.drop_label": "Choose an HWP, HWPX or HWPML file",
    "convert.drop_idle": "Drop a file here or choose one",
    "convert.drop_drag": "Drop it here to convert right away",
    "convert.drop_hint": "HWP · HWPX · HWPML · max 50MB",
    "convert.status_label": "Conversion status",
    "convert.no_file": "No file selected",
    "convert.status_idle": "Waiting for a file",
    "convert.busy": "Converting…",
    "convert.download": "Download ZIP",
    "convert.tabs_label": "Result view",
    "convert.preview": "Preview",
    "convert.preview_empty": "A preview of the converted document appears here",
    "convert.raw_empty": "The converted Markdown source appears here",
    "convert.foot_notice": "This product was developed with reference to the HWP (.hwp) document file format specification published by Hancom Inc. (본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.)",
    "convert.foot_limits_pre": "Elements that cannot be converted, and why, are listed in the ",
    "convert.foot_limits_link": "extraction limits document",
    "convert.foot_limits_post": ".",
  };

  const extra = window.HWP2MD_I18N_EXTRA;
  if (extra && extra.en && typeof extra.en === "object") Object.assign(EN, extra.en);

  const has = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);

  function storedLang() {
    try {
      const v = localStorage.getItem(STORE_KEY);
      return LANGS.includes(v) ? v : null;
    } catch (_) { return null; }
  }
  function store(lang) {
    try { localStorage.setItem(STORE_KEY, lang); } catch (_) { /* 저장 불가여도 화면은 바뀐다 */ }
  }

  function decide() {
    let q = null;
    try { q = new URLSearchParams(location.search).get("lang"); } catch (_) { q = null; }
    if (LANGS.includes(q)) {
      store(q);
      return { lang: q, source: "query" };
    }
    const s = storedLang();
    if (s) return { lang: s, source: "storage" };
    const nav = String((navigator.languages && navigator.languages[0]) || navigator.language || "").toLowerCase();
    return { lang: nav.startsWith("ko") ? "ko" : "en", source: "navigator" };
  }

  const decided = decide();
  let lang = decided.lang;
  let source = decided.source;
  document.documentElement.lang = lang;

  function format(template, vars) {
    if (!vars) return template;
    return template.replace(/\{(\w+)\}/g, (m, name) => (has(vars, name) ? String(vars[name]) : m));
  }

  function t(key, vars) {
    let v;
    if (lang === "en") v = has(EN, key) ? EN[key] : has(KO, key) ? KO[key] : key;
    else v = has(KO, key) ? KO[key] : key;
    return format(v, vars);
  }

  /* ---------- DOM 적용 ---------- */
  const originals = new WeakMap(); // element -> { text, html, attrs: {name: value} }
  function orig(el) {
    let o = originals.get(el);
    if (!o) { o = { attrs: {} }; originals.set(el, o); }
    return o;
  }
  function parseAttrSpec(spec) {
    return String(spec || "").split(";").map((p) => p.trim()).filter(Boolean).map((p) => {
      const i = p.indexOf(":");
      return i < 0 ? null : [p.slice(0, i).trim(), p.slice(i + 1).trim()];
    }).filter((x) => x && x[0] && x[1]);
  }
  const markMissing = (el, key) => {
    el.setAttribute("data-i18n-missing", key);
    console.warn("[i18n] missing en key:", key);
  };

  function applyEl(el) {
    let missingKey = null;
    const textKey = el.getAttribute("data-i18n");
    if (textKey) {
      const o = orig(el);
      if (o.text === undefined) o.text = el.textContent;
      const next = lang === "en" && has(EN, textKey) ? EN[textKey] : o.text;
      if (lang === "en" && !has(EN, textKey)) missingKey = textKey;
      if (el.textContent !== next) el.textContent = next;
    }
    const htmlKey = el.getAttribute("data-i18n-html");
    if (htmlKey) {
      const o = orig(el);
      if (o.html === undefined) o.html = el.innerHTML;
      const next = lang === "en" && has(EN, htmlKey) ? EN[htmlKey] : o.html;
      if (lang === "en" && !has(EN, htmlKey)) missingKey = htmlKey;
      if (el.innerHTML !== next) el.innerHTML = next;
    }
    const spec = el.getAttribute("data-i18n-attr");
    if (spec) {
      const o = orig(el);
      parseAttrSpec(spec).forEach(([attr, key]) => {
        if (!has(o.attrs, attr)) o.attrs[attr] = el.getAttribute(attr);
        let next = o.attrs[attr];
        if (lang === "en") {
          if (has(EN, key)) next = EN[key];
          else missingKey = key;
        }
        if (next === null) el.removeAttribute(attr);
        else if (el.getAttribute(attr) !== next) el.setAttribute(attr, next);
      });
    }
    if (missingKey) markMissing(el, missingKey);
    else el.removeAttribute("data-i18n-missing");
  }

  const SELECTOR = "[data-i18n],[data-i18n-html],[data-i18n-attr]";
  function apply(root) {
    const r = root || document;
    if (r.nodeType === 1 && r.matches(SELECTOR)) applyEl(r);
    if (r.querySelectorAll) r.querySelectorAll(SELECTOR).forEach(applyEl);
  }

  function domKeys() {
    const keys = [];
    document.querySelectorAll(SELECTOR).forEach((el) => {
      const a = el.getAttribute("data-i18n");
      const b = el.getAttribute("data-i18n-html");
      if (a) keys.push(a);
      if (b) keys.push(b);
      parseAttrSpec(el.getAttribute("data-i18n-attr")).forEach(([, k]) => keys.push(k));
    });
    return keys;
  }

  function missing() {
    const out = new Set();
    Object.keys(KO).forEach((k) => { if (!has(EN, k)) out.add(k); });
    domKeys().forEach((k) => { if (!has(EN, k)) out.add(k); });
    return Array.from(out).sort();
  }

  function set(next) {
    if (!LANGS.includes(next)) return;
    store(next);
    try {
      const url = new URL(location.href);
      if (url.searchParams.has("lang")) {
        url.searchParams.delete("lang");
        history.replaceState(history.state, "", url.pathname + url.search + url.hash);
      }
    } catch (_) { /* URL 정리 실패는 무시 */ }
    if (document.body && document.body.hasAttribute("data-i18n-reload")) {
      location.reload();
      return;
    }
    lang = next;
    source = "storage";
    document.documentElement.lang = lang;
    apply(document);
    document.dispatchEvent(new CustomEvent("hwp2md:langchange", { detail: lang }));
  }

  // 헤더 KO/EN 버튼: 누르면 반대 언어로.
  document.addEventListener("click", (ev) => {
    const btn = ev.target && ev.target.closest ? ev.target.closest(".lang-toggle") : null;
    if (!btn) return;
    ev.preventDefault();
    set(lang === "en" ? "ko" : "en");
  });

  window.Hwp2mdI18n = {
    get lang() { return lang; },
    get source() { return source; },
    t: t,
    set: set,
    apply: apply,
    missing: missing,
  };

  apply(document);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => apply(document));
})();
