/* 라이트·다크 전환. 저장된 선택 → 시스템 설정 순. 전환은 버튼에서 퍼지는 원형 View Transition. */
(function () {
  "use strict";

  const KEY = "hwp2md-theme";
  const root = document.documentElement;
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  function stored() {
    try { return localStorage.getItem(KEY); } catch (_) { return null; }
  }

  function current() {
    return root.dataset.theme || (media.matches ? "dark" : "light");
  }

  function apply(theme) {
    root.dataset.theme = theme;
    try { localStorage.setItem(KEY, theme); } catch (_) { /* 저장 불가여도 화면은 바뀐다 */ }
    document.querySelectorAll(".theme-toggle").forEach((b) => {
      b.setAttribute("aria-label", theme === "dark" ? "라이트 모드로 전환" : "다크 모드로 전환");
    });
    document.dispatchEvent(new CustomEvent("themechange", { detail: theme }));
  }

  const saved = stored();
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;

  function toggle(ev) {
    const next = current() === "dark" ? "light" : "dark";
    if (!document.startViewTransition || reduced.matches) {
      apply(next);
      return;
    }
    const rect = ev.currentTarget.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const r = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    const vt = document.startViewTransition(() => apply(next));
    vt.ready.then(() => {
      root.animate(
        { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${r}px at ${x}px ${y}px)`] },
        { duration: 520, easing: "cubic-bezier(0.16, 1, 0.3, 1)", pseudoElement: "::view-transition-new(root)" }
      );
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".theme-toggle").forEach((b) => {
      b.addEventListener("click", toggle);
      b.setAttribute("aria-label", current() === "dark" ? "라이트 모드로 전환" : "다크 모드로 전환");
    });
  });
})();
