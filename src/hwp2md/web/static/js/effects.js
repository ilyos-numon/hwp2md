/* hwp2md V3 — 재사용 모션 효과 (gsap.registerEffect).
   모두 extendTimeline: true 라서 gsap.effects.이름(대상, 설정) 과 tl.이름(대상, 설정, 위치) 둘 다 된다.
   효과의 소재는 이 제품의 것만 쓴다: Markdown 기호, 블록 꼬리표, 코드 줄. */
(function () {
  "use strict";
  if (!window.gsap) return;

  const MD_CHARS = "#|-![]()*_`<>";
  const EXPO = "expo.out";

  function escapeHtml(t) {
    return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Markdown·셸·파이썬 기호만 강조 (내용 글자는 그대로)
  function highlight(text, kind) {
    const esc = escapeHtml(text);
    if (kind === "cmd") return '<em class="p">$</em> ' + esc;
    if (kind === "py") return '<em class="p">&gt;&gt;&gt;</em> ' + esc;
    if (kind === "note") return '<em class="c">' + esc + "</em>";
    if (/^#{1,6}( |$)/.test(text)) return esc.replace(/^(#{1,6})/, '<em class="k">$1</em>');
    if (text.startsWith("|")) return esc.replace(/\|(-+\|)*/g, (m) => '<em class="k">' + m + "</em>");
    if (text.startsWith("![")) {
      return esc.replace(/^!\[/, '<em class="k">![</em>').replace(/\]\(/, '<em class="k">](</em>').replace(/\)$/, '<em class="k">)</em>');
    }
    if (text.startsWith("✓")) return '<em class="ok">✓</em>' + esc.slice(1);
    return esc;
  }

  /* 글자 단위로 아래에서 올라온다. SplitText 결과는 요소에 보관해 다시 나누지 않는다. */
  gsap.registerEffect({
    name: "riseChars",
    extendTimeline: true,
    defaults: { duration: 1.1, stagger: 0.022, y: 115 },
    effect(targets, config) {
      const chars = [];
      gsap.utils.toArray(targets).forEach((el) => {
        if (!el._h2mSplit) el._h2mSplit = SplitText.create(el, { type: "lines,chars", mask: "lines" });
        chars.push(...el._h2mSplit.chars);
      });
      return gsap.from(chars, { yPercent: config.y, duration: config.duration, stagger: config.stagger, ease: EXPO });
    },
  });

  /* Markdown 기호로 뒤섞였다가 원래 글자로 해독된다 (파싱의 은유) */
  gsap.registerEffect({
    name: "scrambleIn",
    extendTimeline: true,
    defaults: { duration: 1.1, text: "{original}", chars: MD_CHARS, speed: 0.6, revealDelay: 0.25 },
    effect(targets, config) {
      return gsap.to(targets, {
        duration: config.duration,
        ease: "none",
        scrambleText: { text: config.text, chars: config.chars, speed: config.speed, revealDelay: config.revealDelay },
      });
    },
  });

  /* 선이 한쪽에서 그어진다 */
  gsap.registerEffect({
    name: "drawIn",
    extendTimeline: true,
    defaults: { duration: 0.8, axis: "x", ease: "power3.inOut" },
    effect(targets, config) {
      const prop = config.axis === "y" ? "scaleY" : "scaleX";
      return gsap.fromTo(targets, { [prop]: 0 }, { [prop]: 1, duration: config.duration, ease: config.ease });
    },
  });

  /* 블록 꼬리표가 튀어나온다 */
  gsap.registerEffect({
    name: "tagPop",
    extendTimeline: true,
    defaults: { duration: 0.5, stagger: 0.06 },
    effect(targets, config) {
      return gsap.from(targets, {
        autoAlpha: 0, scale: 0.6, y: 8, transformOrigin: "50% 100%",
        duration: config.duration, stagger: config.stagger, ease: EXPO,
      });
    },
  });

  /* 코드 줄을 한 글자씩 친다. 대상은 data-t(텍스트)와 tl--cmd/py/note 클래스를 가진 줄 요소들 */
  gsap.registerEffect({
    name: "typeLines",
    extendTimeline: true,
    defaults: { cps: 55, linePause: 0.08, outputPause: 0.02, typeAll: false },
    effect(targets, config) {
      const tl = gsap.timeline();
      gsap.utils.toArray(targets).forEach((line) => {
        const text = line.dataset.t != null ? line.dataset.t : line.dataset.type || "";
        const kind = line.classList.contains("tl--cmd") ? "cmd"
          : line.classList.contains("tl--py") ? "py"
          : line.classList.contains("tl--note") ? "note" : "";
        const typed = config.typeAll || kind === "cmd" || kind === "py";
        line.innerHTML = "";
        if (!typed) {
          // 출력 줄은 사람이 치지 않으니 한 번에 나타난다
          tl.call(() => { line.innerHTML = highlight(text, kind); }, null, "+=" + config.outputPause);
          return;
        }
        const st = { n: 0 };
        tl.to(st, {
          n: text.length, duration: Math.max(0.15, text.length / config.cps), ease: "none", snap: { n: 1 },
          onStart() { line.innerHTML = highlight("", kind); },
          onUpdate() { line.innerHTML = highlight(text.slice(0, st.n), kind); },
          onComplete() { line.innerHTML = highlight(text, kind); },
        }, "+=" + config.linePause);
      });
      return tl;
    },
  });

  /* 숫자가 목표값까지 오른다 */
  gsap.registerEffect({
    name: "countTo",
    extendTimeline: true,
    defaults: { duration: 0.6, to: 0 },
    effect(targets, config) {
      const tl = gsap.timeline();
      gsap.utils.toArray(targets).forEach((el) => {
        const o = { v: 0 };
        tl.to(o, { v: config.to, duration: config.duration, ease: "power2.out", onUpdate: () => { el.textContent = Math.round(o.v); } }, 0);
      });
      return tl;
    },
  });

  window.H2M_FX = { highlight: highlight, MD_CHARS: MD_CHARS };
})();
