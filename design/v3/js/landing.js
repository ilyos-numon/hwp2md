/* hwp2md V3 — 서비스 소개 페이지 모션 (GSAP 3.13: ScrollTrigger, SplitText, ScrambleText + js/effects.js 의 등록 효과).
   원칙: 내용은 기본 상태에서 보인다. 모션은 matchMedia 안에서만 초기 상태를 바꾼다.
   움직임 줄이기 설정이면 최종 상태를 바로 보여 준다. 반복 애니메이션은 화면에 보일 때만 돈다. */
(function () {
  "use strict";

  const root = document.documentElement;
  window.__h2mReady = true;

  if (!window.gsap || !window.ScrollTrigger || !window.SplitText || !window.ScrambleTextPlugin || !gsap.effects.typeLines) {
    root.classList.remove("js");
    initTabs(null);
    initEntryTabs(null);
    return;
  }

  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin);
  const fx = gsap.effects;
  const EXPO = "expo.out";
  const MOTION = "(prefers-reduced-motion: no-preference)";
  const REDUCE = "(prefers-reduced-motion: reduce)";
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const mm = gsap.matchMedia();

  // SplitText 는 글꼴이 들어온 뒤에 나눠야 줄바꿈이 맞다 (최대 1.5초 대기)
  const fontsReady = Promise.race([
    document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve(),
    new Promise((r) => setTimeout(r, 1500)),
  ]);

  /* ================= 머리글 스크롤 진행 막대 ================= */
  mm.add(MOTION, () => {
    gsap.fromTo(".scroll-progress", { scaleX: 0 }, {
      scaleX: 1, ease: "none",
      scrollTrigger: { start: 0, end: "max", scrub: 0.3 },
    });
  });

  /* ================= HERO ================= */
  const heroTitle = $(".hero__title");
  const heroMd = $(".hero__md");
  const heroLines = $$(".hv-line");
  const tokens = $$(".tokens span");

  function heroFinal() {
    gsap.set([heroTitle, ".hero__lead", ".hero__cta", ".hero__facts"], { visibility: "visible" });
    heroMd.textContent = "Markdown";
    heroLines.forEach((l) => { l.innerHTML = window.H2M_FX.highlight(l.dataset.type, ""); });
  }

  fontsReady.then(() => {
    mm.add(MOTION, () => {
      const split = SplitText.create(heroTitle, { type: "lines", mask: "lines" });
      gsap.set([heroTitle, ".hero__lead", ".hero__cta", ".hero__facts"], { visibility: "visible" });
      heroMd.textContent = heroMd.dataset.from; // 처음엔 HWP·HWPX 로 보이다가 Markdown 으로 해독된다

      const tl = gsap.timeline({ defaults: { ease: EXPO } });
      tl.from(split.lines, { yPercent: 110, duration: 1.1, stagger: 0.12 })
        .scrambleIn(heroMd, { text: "Markdown", duration: 1.2, revealDelay: 0.35 }, 0.55)
        .from(".hero__lead", { y: 18, autoAlpha: 0, duration: 0.8 }, 0.7)
        .from(".hero__cta .btn", { y: 16, autoAlpha: 0, duration: 0.7, stagger: 0.08 }, 0.85)
        .from(".hero__facts li", { y: 10, autoAlpha: 0, duration: 0.6, stagger: 0.07 }, 1.0)
        .from(tokens, {
          autoAlpha: 0, scale: 0.4, rotation: () => gsap.utils.random(-50, 50),
          y: () => gsap.utils.random(-60, 60), duration: 1.4, stagger: { each: 0.05, from: "random" },
        }, 0.2)
        .from(".hv-card--in", { x: -40, rotation: -4, autoAlpha: 0, duration: 0.9 }, 0.5)
        .drawIn(".hv-link__line", { axis: innerWidth <= 720 ? "y" : "x", duration: 0.6 }, 1.0)
        .fromTo(".hv-link__dot", {
          left: () => (innerWidth <= 720 ? "50%" : "0%"), top: () => (innerWidth <= 720 ? "0%" : "50%"),
        }, {
          left: () => (innerWidth <= 720 ? "50%" : "100%"), top: () => (innerWidth <= 720 ? "100%" : "50%"),
          duration: 0.6, ease: "power2.inOut",
        }, 1.0)
        .from(".hv-card--out", { x: 40, rotation: 4, autoAlpha: 0, duration: 0.9 }, 1.3)
        .typeLines(heroLines, { typeAll: true, cps: 48, linePause: 0.05 }, 1.7);

      // 기호 입자: 보일 때만 천천히 떠다닌다
      const drift = tokens.map((t) => gsap.to(t, {
        rotation: gsap.utils.random(-10, 10), yPercent: gsap.utils.random(-40, 40),
        duration: gsap.utils.random(3, 6), ease: "sine.inOut", repeat: -1, yoyo: true, paused: true,
      }));
      ScrollTrigger.create({
        trigger: ".hero", start: "top bottom", end: "bottom top",
        onToggle: (s) => drift.forEach((d) => (s.isActive ? d.play() : d.pause())),
      });

      // 스크롤로 빠져나갈 때: 깊이에 따라 기호가 다른 속도로 올라가고, 결과 카드가 기울며 물러난다
      const out = gsap.timeline({ scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: 0.6 } });
      tokens.forEach((t) => out.to(t, { y: -240 * Number(t.dataset.d || 0.5), ease: "none" }, 0));
      out.to(".hero__visual", { y: 80, rotationX: 14, scale: 0.94, transformPerspective: 1200, ease: "none" }, 0)
        .to(".hero__copy", { y: -40, autoAlpha: 0.2, ease: "none" }, 0);

      return () => { split.revert(); heroFinal(); };
    });

    mm.add(REDUCE, heroFinal);

    /* 마우스 시차: 깊이가 큰 기호일수록 더 움직인다 (정밀 포인터만) */
    mm.add("(hover: hover) and (pointer: fine) and " + MOTION, () => {
      const movers = tokens.map((t) => ({
        d: Number(t.dataset.d || 0.5),
        x: gsap.quickTo(t, "x", { duration: 0.9, ease: "power3.out" }),
        r: gsap.quickTo(t, "rotationY", { duration: 0.9, ease: "power3.out" }),
      }));
      const hero = $(".hero");
      const move = (e) => {
        const nx = e.clientX / innerWidth - 0.5;
        movers.forEach((m) => { m.x(nx * 70 * m.d); m.r(nx * 30 * m.d); });
      };
      hero.addEventListener("pointermove", move);
      return () => hero.removeEventListener("pointermove", move);
    });

    /* ================= PROBLEM: 문장을 읽어 내려가고, 쓰일 곳에 밑줄이 그어진다 ================= */
    mm.add(MOTION, () => {
      const split = SplitText.create(".problem__text", { type: "words", wordsClass: "word" });
      gsap.fromTo(split.words, { opacity: 0.16 }, {
        opacity: 1, ease: "none", stagger: 0.1,
        scrollTrigger: { trigger: ".problem__text", start: "top 80%", end: "bottom 45%", scrub: true },
      });
      gsap.fromTo(".problem mark", { backgroundSize: "0% 100%" }, {
        backgroundSize: "100% 100%", ease: "none", stagger: 0.3,
        scrollTrigger: { trigger: ".problem__text", start: "top 60%", end: "center 40%", scrub: true },
      });
      gsap.from(".problem__title", {
        y: 40, autoAlpha: 0, duration: 1, ease: EXPO,
        scrollTrigger: { trigger: ".problem", start: "top 80%", once: true },
      });
      return () => split.revert();
    });

    /* ================= 섹션 제목: 글자가 올라온다 ================= */
    mm.add(MOTION, () => {
      $$(".fx-title").forEach((el) => {
        ScrollTrigger.create({ trigger: el, start: "top 86%", once: true, onEnter: () => fx.riseChars(el, { stagger: 0.018, duration: 1 }) });
      });
      return () => $$(".fx-title").forEach((el) => { if (el._h2mSplit) { el._h2mSplit.revert(); el._h2mSplit = null; } });
    });

    ScrollTrigger.refresh();
  });

  /* ================= PIPELINE (focal) ================= */
  const stage = $(".pipeline__stage");
  const sheet = $(".paper__sheet");
  const blocks = $$(".blk");
  const phases = $$(".phase");
  const flyersBox = $(".flyers");
  const countEls = { h: $('[data-count="h"]'), p: $('[data-count="p"]'), t: $('[data-count="t"]'), i: $('[data-count="i"]') };
  const KIND = { h1: "h", h2: "h", h3: "h", p1: "p", tbl: "t", img: "i" };
  const FINAL = { h: 3, p: 1, t: 1, i: 1 };

  const renderCounts = (c) => Object.keys(countEls).forEach((k) => { countEls[k].textContent = Math.round(c[k]); });
  const setActivePhase = (idx) => phases.forEach((p, i) => p.classList.toggle("is-active", i === idx));

  function rel(el) {
    const s = stage.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    return { x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height };
  }

  function pipelineFinal() {
    blocks.forEach((b) => b.style.setProperty("--tag", 1));
    phases.forEach((p) => p.style.setProperty("--p", 1));
    gsap.set(".ln", { clipPath: "inset(0 0% 0 0)" });
    gsap.set(".detect__q", { autoAlpha: 0 });
    gsap.set(".detect__a", { autoAlpha: 1 });
    gsap.set(blocks, { clearProps: "transform" });
    renderCounts(FINAL);
    setActivePhase(2);
  }

  function buildPipeline(tl, { flyers }) {
    const counts = { h: 0, p: 0, t: 0, i: 0 };
    renderCounts(counts);
    gsap.set(".ln", { clipPath: "inset(0 100% 0 0)" });
    blocks.forEach((b) => b.style.setProperty("--tag", 0));
    phases.forEach((p) => p.style.setProperty("--p", 0));
    const titles = phases.map((p) => p.querySelector("b"));

    // 1) 읽기: 스캔선이 원고를 훑고 포맷을 판별한다
    tl.addLabel("read")
      .call(setActivePhase, [0])
      .scrambleIn(titles[0], { duration: 0.5 }, "read")
      .to(phases[0], { "--p": 1, duration: 1, ease: "none" }, "read")
      .fromTo(".scan", { autoAlpha: 1, y: 0 }, { y: () => sheet.offsetHeight - 56, duration: 1, ease: "power1.inOut" }, "read")
      .to(".scan", { autoAlpha: 0, duration: 0.15 }, "read+=0.95")
      .to(".detect__q", { autoAlpha: 0, y: -6, duration: 0.2 }, "read+=0.7")
      .fromTo(".detect__a", { autoAlpha: 0, y: 6 }, { autoAlpha: 1, y: 0, duration: 0.25 }, "read+=0.8");

    // 2) 블록으로 나누기: 꼬리표가 붙고, 원고가 분해도처럼 벌어졌다가 다시 모인다
    tl.addLabel("blocks")
      .call(setActivePhase, [1], "blocks")
      .scrambleIn(titles[1], { duration: 0.5 }, "blocks")
      .to(phases[1], { "--p": 1, duration: 1.4, ease: "none" }, "blocks")
      .to(blocks, { "--tag": 1, duration: 0.3, stagger: 0.16, ease: "power2.out" }, "blocks")
      .to(blocks, {
        x: (i) => (i % 2 ? 22 : -22), y: (i) => (i - 2.5) * 6, rotation: (i) => (i % 2 ? 1.2 : -1.2),
        duration: 0.6, stagger: 0.04, ease: "power2.inOut",
      }, "blocks+=0.5")
      .to(blocks, { x: 0, y: 0, rotation: 0, duration: 0.45, stagger: 0.03, ease: "power2.inOut" }, "blocks+=1.25");

    // 3) Markdown 으로 쓰기
    tl.addLabel("write")
      .call(setActivePhase, [2], "write")
      .scrambleIn(titles[2], { duration: 0.5 }, "write")
      .to(phases[2], { "--p": 1, duration: blocks.length * 0.5, ease: "none" }, "write");

    flyersBox.innerHTML = "";
    blocks.forEach((b, i) => {
      const key = b.dataset.blk;
      const lines = $$('.ln[data-for="' + key + '"]');
      const at = "write+=" + (i * 0.5).toFixed(2);
      if (flyers) {
        const f = document.createElement("span");
        f.className = "flyer";
        f.textContent = b.dataset.tag;
        flyersBox.appendChild(f);
        tl.fromTo(f, {
          x: () => rel(b).x + rel(b).w - f.offsetWidth + 4,
          y: () => rel(b).y - 9,
          autoAlpha: 1, scale: 1, rotation: 0,
        }, {
          x: () => rel(lines[0]).x - f.offsetWidth - 10,
          y: () => rel(lines[0]).y + 4,
          scale: 0.92, rotation: i % 2 ? 6 : -6, duration: 0.42, ease: "power2.inOut", immediateRender: false,
        }, at)
          .to(f, { autoAlpha: 0, scale: 0.6, duration: 0.12 }, ">-0.02");
      }
      tl.to(b, { "--tag": 0.35, duration: 0.2 }, at)
        .to(lines, { clipPath: "inset(0 0% 0 0)", duration: 0.3, stagger: 0.06, ease: "power1.inOut" }, flyers ? at + "+0.34" : at)
        .to(counts, {
          [KIND[key]]: counts[KIND[key]] + 1, duration: 0.2, snap: { h: 1, p: 1, t: 1, i: 1 },
          onUpdate: () => renderCounts(counts),
        }, flyers ? at + "+0.4" : at);
      counts[KIND[key]] += 1; // 다음 블록의 목표값 계산용 (트윈 시작값은 처음 렌더할 때 읽힌다)
    });
    Object.keys(counts).forEach((k) => { counts[k] = 0; });
    renderCounts(counts);
  }

  mm.add({
    desk: "(min-width: 900px) and " + MOTION,
    mob: "(max-width: 899px) and " + MOTION,
  }, (ctx) => {
    if (ctx.conditions.desk) {
      const tl = gsap.timeline({
        defaults: { ease: "power2.out" },
        scrollTrigger: { trigger: ".pipeline", start: "top top", end: "+=3200", pin: ".pipeline__pin", scrub: 0.6, invalidateOnRefresh: true, anticipatePin: 1 },
      });
      buildPipeline(tl, { flyers: true });
      tl.to({}, { duration: 0.6 });
    } else {
      const tl = gsap.timeline({
        paused: true, defaults: { ease: "power2.out" },
        scrollTrigger: { trigger: ".pipeline__stage", start: "top 70%", toggleActions: "play none none none" },
      });
      buildPipeline(tl, { flyers: false });
      tl.timeScale(1.6);
    }
    return () => { flyersBox.innerHTML = ""; pipelineFinal(); };
  });
  mm.add(REDUCE, pipelineFinal);

  /* ================= ENTRY: 터미널에 실제 명령과 출력이 찍힌다 ================= */
  let entryTl = null;
  let entrySeen = false;
  const reduceMq = window.matchMedia(REDUCE);

  function lineKind(l) {
    if (l.classList.contains("tl--cmd")) return "cmd";
    if (l.classList.contains("tl--py")) return "py";
    if (l.classList.contains("tl--note")) return "note";
    return "";
  }

  function playEntry(panel) {
    if (entryTl) entryTl.kill();
    const lines = $$(".tl", panel);
    if (reduceMq.matches) {
      lines.forEach((l) => { l.innerHTML = window.H2M_FX.highlight(l.dataset.t, lineKind(l)); });
      return;
    }
    entryTl = fx.typeLines(lines, { cps: 42, linePause: 0.18 });
  }

  initEntryTabs((panel) => { if (entrySeen || reduceMq.matches) playEntry(panel); });

  mm.add(MOTION, () => {
    ScrollTrigger.create({
      trigger: ".term", start: "top 75%", once: true,
      onEnter: () => { entrySeen = true; playEntry($(".term__panel:not([hidden])")); },
    });
    gsap.fromTo(".term", { rotationX: 18, y: 60, scale: 0.94, transformPerspective: 1400 }, {
      rotationX: 0, y: 0, scale: 1, ease: "none",
      scrollTrigger: { trigger: ".entry__body", start: "top bottom", end: "top 35%", scrub: 0.6 },
    });
    gsap.from(".entry__tabs button", {
      x: -24, autoAlpha: 0, duration: 0.7, stagger: 0.08, ease: EXPO,
      scrollTrigger: { trigger: ".entry__tabs", start: "top 85%", once: true },
    });
  });
  mm.add(REDUCE, () => { $$(".term__panel").forEach(playEntry); });

  /* ================= FEATURES: 목록이 나타나고 예시 코드가 해독된다 ================= */
  mm.add(MOTION, () => {
    const items = $$(".feat");
    gsap.set(items, { autoAlpha: 0, y: 24 });
    ScrollTrigger.batch(items, {
      start: "top 88%", once: true,
      onEnter: (batch) => {
        gsap.to(batch, { autoAlpha: 1, y: 0, duration: 0.7, ease: EXPO, stagger: 0.08, overwrite: true });
        gsap.from(batch.map((it) => it.querySelector(".feat__icon")), { rotation: -90, scale: 0.4, duration: 0.8, stagger: 0.08, ease: EXPO });
        batch.forEach((it, i) => gsap.delayedCall(0.15 + i * 0.08, () => fx.scrambleIn(it.querySelector("[data-scramble]"), { duration: 0.9 })));
      },
    });
    return () => gsap.set(items, { clearProps: "all" });
  });

  /* ================= CASES: 가로로 흘러가는 사용 장면 ================= */
  mm.add({
    desk: "(min-width: 900px) and " + MOTION,
    mob: "(max-width: 899px) and " + MOTION,
  }, (ctx) => {
    const track = $(".cases__track");
    const cases = $$(".case");
    if (ctx.conditions.desk) {
      const dist = () => track.scrollWidth - track.clientWidth;
      const scroll = gsap.to(track, {
        x: () => -dist(), ease: "none",
        scrollTrigger: { trigger: ".cases", start: "top top", end: () => "+=" + dist() * 1.2, pin: ".cases__pin", scrub: 0.7, invalidateOnRefresh: true },
      });
      cases.forEach((c) => {
        ScrollTrigger.create({
          trigger: c, containerAnimation: scroll, start: "left 80%", once: true,
          onEnter: () => fx.scrambleIn(c.querySelector("h3"), { duration: 1 }),
        });
        // 카드가 화면 가운데를 지날 때 바로 서고, 양옆에서는 살짝 기운다
        gsap.to(c, {
          keyframes: { rotation: [3, 0, -3], scale: [0.94, 1, 0.94], easeEach: "none" }, ease: "none",
          scrollTrigger: { trigger: c, containerAnimation: scroll, start: "left right", end: "right left", scrub: true },
        });
      });
    } else {
      cases.forEach((c) => gsap.from(c, { y: 40, autoAlpha: 0, duration: 0.8, ease: EXPO, scrollTrigger: { trigger: c, start: "top 88%", once: true } }));
    }
    return () => gsap.set([track, ...cases], { clearProps: "all" });
  });

  /* ================= PRIVACY: 두 모드의 파일 흐름 ================= */
  const flow = $(".flow");
  const pk = { file: $(".packet--file"), md: $(".packet--md"), code: $(".packet--code") };
  let loop = null;
  let flowVisible = false;
  let flowEnabled = false;

  function center(el, packet) {
    const f = flow.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    return { x: r.left - f.left + r.width / 2 - packet.offsetWidth / 2, y: r.top - f.top + r.height / 2 - packet.offsetHeight / 2 };
  }

  function buildLoop(mode) {
    if (loop) loop.kill();
    gsap.set(Object.values(pk), { autoAlpha: 0, scale: 1, filter: "none" });
    const browser = $(".flow__node--browser > svg");
    const server = $(".flow__mem");
    const B = (p) => center(browser, p);
    const S = (p) => center(server, p);
    const tl = gsap.timeline({ repeat: -1, repeatDelay: 0.6, paused: true, defaults: { ease: "power2.inOut" } });
    if (mode === "server") {
      tl.set(pk.file, { ...B(pk.file), autoAlpha: 0, scale: 0.8 })
        .to(pk.file, { autoAlpha: 1, scale: 1, duration: 0.3 })
        .to(pk.file, { ...S(pk.file), duration: 0.9 })
        .to(pk.file, { scale: 0.6, autoAlpha: 0, filter: "blur(4px)", duration: 0.45, ease: "power2.in" }, "+=0.25")
        .set(pk.md, { ...S(pk.md), autoAlpha: 0, scale: 0.8 }, "<0.2")
        .to(pk.md, { autoAlpha: 1, scale: 1, duration: 0.3 })
        .to(pk.md, { ...B(pk.md), duration: 0.9 })
        .to(pk.md, { autoAlpha: 0, duration: 0.3 }, "+=0.5")
        .set(pk.file, { filter: "none" });
    } else {
      tl.set(pk.code, { ...S(pk.code), autoAlpha: 0, scale: 0.8 })
        .to(pk.code, { autoAlpha: 1, scale: 1, duration: 0.3 })
        .to(pk.code, { ...B(pk.code), duration: 1 })
        .to(pk.code, { autoAlpha: 0, scale: 0.8, duration: 0.3 })
        .set(pk.file, { ...B(pk.file), y: B(pk.file).y + 34, autoAlpha: 0 })
        .to(pk.file, { autoAlpha: 1, duration: 0.3 })
        .to(pk.file, { scale: 0.6, autoAlpha: 0, filter: "blur(4px)", duration: 0.45, ease: "power2.in" }, "+=0.5")
        .set(pk.md, { ...B(pk.md), y: B(pk.md).y + 34, autoAlpha: 0, scale: 0.8 }, "<0.2")
        .to(pk.md, { autoAlpha: 1, scale: 1, duration: 0.3 })
        .to(pk.md, { autoAlpha: 0, duration: 0.3 }, "+=0.9")
        .set(pk.file, { filter: "none" });
    }
    loop = tl;
    if (flowVisible) tl.play();
  }

  mm.add(MOTION, () => {
    flowEnabled = true;
    buildLoop(flow.dataset.mode);
    const st = ScrollTrigger.create({
      trigger: flow, start: "top 85%", end: "bottom 15%",
      onToggle(self) { flowVisible = self.isActive; if (loop) (flowVisible ? loop.play() : loop.pause()); },
    });
    const onRefresh = () => buildLoop(flow.dataset.mode);
    ScrollTrigger.addEventListener("refresh", onRefresh);
    return () => {
      flowEnabled = false;
      st.kill();
      ScrollTrigger.removeEventListener("refresh", onRefresh);
      if (loop) loop.kill();
      loop = null;
      gsap.set(Object.values(pk), { autoAlpha: 0 });
    };
  });
  initTabs((mode) => { if (flowEnabled) buildLoop(mode); });

  /* ================= LIMITS: 한계가 나열되고, 예정 표시가 뒤따라 붙는다 ================= */
  mm.add(MOTION, () => {
    const tl = gsap.timeline({ scrollTrigger: { trigger: ".limits ul", start: "top 80%", once: true } });
    tl.from(".limits li", { y: 14, autoAlpha: 0, duration: 0.5, stagger: 0.05, ease: EXPO })
      .tagPop(".limits li .chip", { stagger: 0.07 }, 0.35);
  });

  /* ================= CTA: 두 줄 기호 띠, 스크롤 속도만큼 기운다 ================= */
  mm.add(MOTION, () => {
    const rows = $$(".marquee__row");
    const loops = rows.map((row) => {
      const track = row.querySelector(".marquee__track");
      const original = track.innerHTML;
      track.innerHTML = original + original; // 끊김 없는 반복용 복제
      const dir = Number(row.dataset.dir);
      const tw = gsap.fromTo(track, { xPercent: dir > 0 ? -50 : 0 }, { xPercent: dir > 0 ? 0 : -50, ease: "none", duration: 36, repeat: -1, paused: true });
      tw._restore = () => { track.innerHTML = original; };
      return tw;
    });
    const skew = gsap.quickTo(rows, "skewX", { duration: 0.4, ease: "power3.out" });
    ScrollTrigger.create({
      trigger: ".cta", start: "top bottom", end: "bottom top",
      onToggle: (s) => loops.forEach((l) => (s.isActive ? l.play() : l.pause())),
      onUpdate: (s) => {
        const v = gsap.utils.clamp(-14, 14, s.getVelocity() / -260);
        skew(v);
        loops.forEach((l) => l.timeScale(1 + Math.abs(v) / 3));
      },
    });
    gsap.from(".cta .btn", { scale: 0.8, autoAlpha: 0, duration: 0.8, ease: EXPO, scrollTrigger: { trigger: ".cta", start: "top 70%", once: true } });
    return () => loops.forEach((l) => l._restore());
  });

  /* ================= 자석 버튼 (정밀 포인터만) ================= */
  mm.add("(hover: hover) and (pointer: fine) and " + MOTION, () => {
    const offs = [];
    $$(".magnetic").forEach((btn) => {
      const qx = gsap.quickTo(btn, "x", { duration: 0.5, ease: "power3.out" });
      const qy = gsap.quickTo(btn, "y", { duration: 0.5, ease: "power3.out" });
      const move = (e) => {
        const r = btn.getBoundingClientRect();
        qx((e.clientX - (r.left + r.width / 2)) * 0.25);
        qy((e.clientY - (r.top + r.height / 2)) * 0.35);
      };
      const leave = () => { qx(0); qy(0); };
      btn.addEventListener("pointermove", move);
      btn.addEventListener("pointerleave", leave);
      offs.push(() => { btn.removeEventListener("pointermove", move); btn.removeEventListener("pointerleave", leave); gsap.set(btn, { x: 0, y: 0 }); });
    });
    return () => offs.forEach((f) => f());
  });

  /* ================= 탭 (모션과 무관하게 동작) ================= */
  function wireTabs(tabs, onSelect) {
    function select(tab, focus) {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
      onSelect(tab);
    }
    tabs.forEach((t, i) => {
      t.addEventListener("click", () => select(t, false));
      t.addEventListener("keydown", (e) => {
        if (!["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp"].includes(e.key)) return;
        e.preventDefault();
        const step = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : tabs.length - 1;
        select(tabs[(i + step) % tabs.length], true);
      });
    });
  }

  function initTabs(onChange) {
    const tabsBox = document.querySelector(".mode-tabs");
    const flowEl = document.querySelector(".flow");
    wireTabs(Array.from(document.querySelectorAll(".mode-tab")), (tab) => {
      tabsBox.dataset.mode = tab.dataset.mode;
      flowEl.dataset.mode = tab.dataset.mode;
      if (onChange) onChange(tab.dataset.mode);
    });
  }

  function initEntryTabs(onChange) {
    const box = document.querySelector(".entry__tabs");
    wireTabs(Array.from(document.querySelectorAll(".entry__tabs [role=tab]")), (tab) => {
      box.dataset.entry = tab.dataset.entry;
      document.querySelector(".term__title").textContent = tab.dataset.entry === "lib" ? "python" : "~/docs";
      if (onChange) onChange(document.getElementById(tab.getAttribute("aria-controls")));
    });
    // 스크립트(GSAP)가 없을 때도 터미널 글자는 보이게
    if (!onChange) document.querySelectorAll(".tl").forEach((l) => { if (!l.textContent) l.textContent = l.dataset.t; });
  }
})();
