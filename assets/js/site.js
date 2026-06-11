/* ============================================================
   site.js — mobile nav + generative network-graph hero.
   The hero canvas reads its colors from CSS variables (--hero-*),
   so it recolors with the active theme. It's also the seed for the
   Direction 3 interactive embedding: swap drawNetwork() for a real
   waveform/manifold scatter when ready, or set data-hero-image on
   .hero to use a static banner instead.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Mobile nav ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") links.classList.remove("open");
    });
  }

  /* ---------- Scroll reveal ---------- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll(".reveal, .sketch-bg").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal, .sketch-bg").forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Hero network graph ---------- */
  var canvas = document.getElementById("hero-canvas");
  if (!canvas) return;

  // Optional static-image override: <section class="hero" data-hero-image="assets/img/banner.png">
  var hero = canvas.closest(".hero");
  if (hero && hero.dataset.heroImage) {
    hero.style.backgroundImage = "url('" + hero.dataset.heroImage + "')";
    hero.style.backgroundSize = "cover";
    hero.style.backgroundPosition = "center";
    canvas.remove();
    return;
  }

  var ctx = canvas.getContext("2d");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var W = 0, H = 0, dpr = 1;

  // Theme-driven colors, read from CSS variables so the graph matches the palette.
  var PALETTE, heroBg, edgeIntra, edgeInter, fiberRGB, glow;
  function readTheme() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) { var x = cs.getPropertyValue(name).trim(); return x || fallback; }
    heroBg    = v("--hero-bg", "#070a10");
    edgeIntra = v("--hero-edge-intra", "rgba(120,170,225,0.22)");
    edgeInter = v("--hero-edge-inter", "rgba(95,150,215,0.30)");
    fiberRGB  = v("--hero-fiber-rgb", "90,140,200");
    glow      = parseFloat(v("--hero-glow", "8")) || 0;
    var pal = v("--hero-nodes", "");
    PALETTE = pal ? pal.split(",").map(function (s) { return s.trim(); })
                  : ["#b491d6", "#6f8fe0", "#82c6ea", "#eef3f7", "#54c7a3", "#f2c14e", "#ef8a4b", "#f29bbf"];
  }

  var COMM = [
    { x: 0.05, y: 0.24, c: 0 }, { x: 0.12, y: 0.58, c: 1 }, { x: 0.19, y: 0.36, c: 2 },
    { x: 0.27, y: 0.72, c: 5 }, { x: 0.34, y: 0.20, c: 3 }, { x: 0.41, y: 0.52, c: 4 },
    { x: 0.48, y: 0.80, c: 6 }, { x: 0.55, y: 0.30, c: 7 }, { x: 0.62, y: 0.64, c: 0 },
    { x: 0.69, y: 0.40, c: 2 }, { x: 0.76, y: 0.74, c: 5 }, { x: 0.83, y: 0.26, c: 6 },
    { x: 0.90, y: 0.58, c: 1 }, { x: 0.96, y: 0.38, c: 4 }
  ];

  var nodes = [], edges = [], fibers = [];

  function rand(a, b) { return a + Math.random() * (b - a); }
  function gauss() { return (Math.random() + Math.random() + Math.random() - 1.5) / 1.5; }

  function build() {
    nodes = []; edges = [];
    COMM.forEach(function (cm, ci) {
      var n = Math.round(rand(15, 24));
      var spread = rand(0.045, 0.07);
      var start = nodes.length;
      for (var i = 0; i < n; i++) {
        nodes.push({
          comm: ci, color: PALETTE[cm.c % PALETTE.length],
          bx: cm.x + gauss() * spread,
          by: cm.y + gauss() * spread * 1.5,
          r: rand(1.2, 2.6),
          ph: rand(0, Math.PI * 2), amp: rand(0.004, 0.012), sp: rand(0.3, 0.8)
        });
      }
      // intra-community edges: connect each node to ~2 nearest in-community
      for (var a = start; a < nodes.length; a++) {
        var d = [];
        for (var b = start; b < nodes.length; b++) if (a !== b) {
          d.push({ b: b, dist: Math.hypot(nodes[a].bx - nodes[b].bx, nodes[a].by - nodes[b].by) });
        }
        d.sort(function (p, q) { return p.dist - q.dist; });
        for (var k = 0; k < Math.min(2, d.length); k++) edges.push({ a: a, b: d[k].b, intra: true });
      }
    });
    // inter-community fibers: link nearest pair between neighboring communities
    for (var c1 = 0; c1 < COMM.length; c1++) {
      for (var c2 = c1 + 1; c2 < COMM.length; c2++) {
        if (Math.abs(COMM[c1].x - COMM[c2].x) > 0.32) continue;
        var best = null;
        nodes.forEach(function (na, ia) {
          if (na.comm !== c1) return;
          nodes.forEach(function (nb, ib) {
            if (nb.comm !== c2) return;
            var dd = Math.hypot(na.bx - nb.bx, na.by - nb.by);
            if (!best || dd < best.dist) best = { a: ia, b: ib, dist: dd };
          });
        });
        if (best) { edges.push({ a: best.a, b: best.b, intra: false }); if (Math.random() < 0.5) edges.push({ a: best.a, b: best.b, intra: false }); }
      }
    }
    // faint streaky backdrop fibers
    fibers = [];
    for (var f = 0; f < 72; f++) {
      var y0 = rand(0.05, 0.95);
      fibers.push({
        x0: rand(-0.05, 0.4), y0: y0,
        x1: rand(0.6, 1.05), y1: y0 + gauss() * 0.12,
        cx: rand(0.3, 0.7), cy: y0 + gauss() * 0.25,
        a: rand(0.015, 0.05), ph: rand(0, 6.28), amp: rand(0.003, 0.01)
      });
    }
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = hero.clientWidth; H = hero.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = heroBg; ctx.fillRect(0, 0, W, H);
    var tt = t * 0.0004;

    // backdrop fibers
    ctx.lineWidth = 1;
    fibers.forEach(function (fb) {
      var off = Math.sin(tt + fb.ph) * fb.amp;
      ctx.strokeStyle = "rgba(" + fiberRGB + "," + fb.a + ")";
      ctx.beginPath();
      ctx.moveTo(fb.x0 * W, (fb.y0 + off) * H);
      ctx.quadraticCurveTo(fb.cx * W, (fb.cy + off) * H, fb.x1 * W, (fb.y1 + off) * H);
      ctx.stroke();
    });

    // current node positions
    nodes.forEach(function (nd) {
      var o = reduce ? 0 : Math.sin(tt * nd.sp + nd.ph) * nd.amp;
      nd.x = (nd.bx + o) * W;
      nd.y = (nd.by + o * 0.6) * H;
    });

    // edges
    edges.forEach(function (e) {
      var a = nodes[e.a], b = nodes[e.b];
      if (e.intra) { ctx.strokeStyle = edgeIntra; ctx.lineWidth = 0.8; }
      else { ctx.strokeStyle = edgeInter; ctx.lineWidth = 1.1; }
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    });

    // nodes with optional glow
    nodes.forEach(function (nd) {
      ctx.beginPath();
      ctx.arc(nd.x, nd.y, nd.r, 0, Math.PI * 2);
      ctx.fillStyle = nd.color;
      ctx.shadowColor = nd.color; ctx.shadowBlur = glow;
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }

  var raf = null;
  function loop(t) { draw(t); raf = requestAnimationFrame(loop); }

  function start() {
    readTheme(); resize(); build();
    if (raf) cancelAnimationFrame(raf);
    if (reduce) { draw(0); }
    else { raf = requestAnimationFrame(loop); }
  }
  // allow re-init (e.g. theme preview / live theme switch)
  window.__initHero = start;

  var rt;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { resize(); build(); if (reduce) draw(0); }, 180);
  });
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { if (raf) cancelAnimationFrame(raf); raf = null; }
    else if (!reduce && !raf) { raf = requestAnimationFrame(loop); }
  });

  start();
})();
