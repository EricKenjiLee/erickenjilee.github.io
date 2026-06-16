/* ============================================================
   hero-wavemap.js — Direction 3 interactive hero.
   Renders the real WaveMAP embedding (625 premotor-cortex neurons,
   Lee et al. eLife 2021) as a point cloud; hover or idle-tour a
   neuron to read out its actual extracellular waveform.
   Data: assets/data/wavemap.json  (needs to be served over http).
   ============================================================ */
(async function () {
  "use strict";
  var host = document.getElementById("wm-embed");
  if (!host) return;
  var hero = host.closest(".hero");
  var ctx = host.getContext("2d");
  var inset = document.getElementById("wm-wave");
  var ictx = inset.getContext("2d");
  var labelEl = document.getElementById("wm-label");
  var insetWrap = document.getElementById("wm-inset");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Turbo colormap (Google / Anton Mikhailov polynomial approximation) — the same
  // colormap the WaveMAP paper uses. Cluster c maps to turbo(c/(K-1)), narrow->broad.
  function turbo(x) {
    x = Math.max(0, Math.min(1, x));
    var v4 = [1, x, x * x, x * x * x], v2 = [x * x * x * x, x * x * x * x * x];
    function d4(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]; }
    function d2(a, b) { return a[0] * b[0] + a[1] * b[1]; }
    var R = d4(v4, [0.13572138, 4.61539260, -42.66032258, 132.13108234]) + d2(v2, [-152.94239396, 59.28637943]);
    var G = d4(v4, [0.09140261, 2.19418839, 4.84296658, -14.18503333]) + d2(v2, [4.27729857, 2.82956604]);
    var B = d4(v4, [0.10667330, 12.64194608, -60.58204836, 110.36276771]) + d2(v2, [-89.90310912, 27.34824973]);
    function ch(v) { v = Math.max(0, Math.min(1, v)) * 0.87; return ("0" + Math.round(v * 255).toString(16)).slice(-2); }
    return "#" + ch(R) + ch(G) + ch(B);
  }
  // sample Turbo over a trimmed range so we skip the near-black indigo/maroon ends
  function buildPalette(K) { var LO = 0.18, HI = 0.92, o = []; for (var i = 0; i < K; i++) o.push(turbo(K > 1 ? LO + i / (K - 1) * (HI - LO) : (LO + HI) / 2)); return o; }
  var PAL = [];
  function colorFor(c) { return PAL[c % PAL.length] || "#2563eb"; }
  var OMIT = [7];   // clusters hidden purely for composition

  function theme() {
    var cs = getComputedStyle(document.documentElement);
    function v(n, f) { var x = cs.getPropertyValue(n).trim(); return x || f; }
    return {
      edge: "rgba(26,40,78,0.42)",   // darker connecting lines for the data hero
      ink:  v("--ink", "#14171c")
    };
  }
  var TH = theme();

  var data;
  try { data = await fetch("assets/data/wavemap.json").then(function (r) { return r.json(); }); }
  catch (e) { return; }
  PAL = buildPalette(data.clusters || 6);

  // Each WaveMAP cluster carries a stable cell-type character from the median
  // trough-to-peak (in samples) of its own member waveforms — real data, computed
  // once. Individual neurons then read out their own precise value around it.
  // Thresholds ~0.35 ms (10.5 samp) and ~0.45 ms (13.5 samp) at 30 kHz.
  var clusterKind = (function () {
    var bins = {}, i, c;
    for (i = 0; i < data.points.length; i++) { c = data.points[i].c; (bins[c] = bins[c] || []).push(t2p(data.points[i].w)); }
    var out = {};
    for (c in bins) { var a = bins[c].sort(function (x, y) { return x - y; }), m = a[a.length >> 1]; out[c] = m < 10.5 ? "narrow-spiking" : (m >= 13.5 ? "broad-spiking" : "intermediate"); }
    return out;
  })();

  // data bounds — for an aspect-preserving (uniform-scale) layout
  var BX0 = Infinity, BX1 = -Infinity, BY0 = Infinity, BY1 = -Infinity;
  data.points.forEach(function (p) {
    if (p.x < BX0) BX0 = p.x; if (p.x > BX1) BX1 = p.x;
    if (p.y < BY0) BY0 = p.y; if (p.y > BY1) BY1 = p.y;
  });
  var BW = (BX1 - BX0) || 1, BH = (BY1 - BY0) || 1;

  function t2p(w) {
    var tr = 0, i;
    for (i = 1; i < w.length; i++) if (w[i] < w[tr]) tr = i;
    var pk = tr;
    for (i = tr; i < w.length; i++) if (w[i] > w[pk]) pk = i;
    return pk - tr;
  }

  var W = 0, H = 0, dpr = 1, P = [];
  function layout() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = hero.clientWidth; H = hero.clientHeight;
    host.width = W * dpr; host.height = H * dpr;
    host.style.width = W + "px"; host.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var wide = W > 820;
    var x0 = wide ? W * 0.38 : W * 0.04, x1 = W * 0.94;
    var y0 = H * 0.13, y1 = H * 0.90;
    // Map the embedding with a single uniform scale so the UMAP keeps its aspect
    // ratio (no horizontal stretch on wide screens); center it in the available box.
    var GROW = 1.25;   // 1.0 = fit-to-box; >1 enlarges the embedding (overflow clipped by the hero)
    var s = Math.min((x1 - x0) / BW, (y1 - y0) / BH) * GROW;
    var ox = x0 + ((x1 - x0) - BW * s) / 2;
    var oy = y0 + ((y1 - y0) - BH * s) / 2 - H * 0.06;   // centered, nudged up a bit
    P = data.points.map(function (p) {
      return { sx: ox + (BX1 - p.x) * s, sy: oy + (p.y - BY0) * s, c: p.c, w: p.w, om: OMIT.indexOf(p.c) >= 0 };
    });
  }

  var active = -1, hoverLock = false, nextTour = 0, raf = null, mobile = false;

  var FS = 30000;  // sampling rate (Hz)
  function drawInset() {
    if (active < 0) { insetWrap.style.opacity = 0; return; }
    insetWrap.style.opacity = 1;
    var p = P[active], col = colorFor(p.c), w = p.w, n = w.length;
    var iw = inset.clientWidth, ih = inset.clientHeight;
    inset.width = iw * dpr; inset.height = ih * dpr; ictx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ictx.clearRect(0, 0, iw, ih);
    var mn = Math.min.apply(null, w), mx = Math.max.apply(null, w), rng = (mx - mn) || 1;
    var padX = iw * 0.17, plotW = iw - 2 * padX;     // narrower waveform
    var padT = 8, botBand = 32, plotH = ih - padT - botBand;
    function X(i) { return padX + i / (n - 1) * plotW; }
    function Y(v) { return padT + (1 - (v - mn) / rng) * plotH; }
    // waveform
    ictx.strokeStyle = col; ictx.lineWidth = 1.6; ictx.lineJoin = "round"; ictx.beginPath();
    for (var i = 0; i < n; i++) { if (i) ictx.lineTo(X(i), Y(w[i])); else ictx.moveTo(X(i), Y(w[i])); }
    ictx.stroke();
    // trough (min) and post-hyperpolarization peak (max after the trough)
    var tr = 0, j; for (j = 1; j < n; j++) if (w[j] < w[tr]) tr = j;
    var pk = tr; for (j = tr; j < n; j++) if (w[j] > w[pk]) pk = j;
    // markers
    ictx.fillStyle = "#1c1c22";
    ictx.beginPath(); ictx.arc(X(tr), Y(w[tr]), 2.4, 0, 6.2832); ictx.fill();
    ictx.beginPath(); ictx.arc(X(pk), Y(w[pk]), 2.4, 0, 6.2832); ictx.fill();
    // droplines from each marker down to a shared dimension line + bracket with end ticks
    var yL = ih - 11;
    ictx.strokeStyle = "rgba(28,28,34,.40)"; ictx.lineWidth = 1;
    ictx.setLineDash([2, 2]);
    ictx.beginPath();
    ictx.moveTo(X(tr), Y(w[tr]) + 4); ictx.lineTo(X(tr), yL);
    ictx.moveTo(X(pk), Y(w[pk]) + 4); ictx.lineTo(X(pk), yL);
    ictx.stroke(); ictx.setLineDash([]);
    ictx.beginPath();
    ictx.moveTo(X(tr), yL); ictx.lineTo(X(pk), yL);
    ictx.moveTo(X(tr), yL - 3); ictx.lineTo(X(tr), yL + 3);
    ictx.moveTo(X(pk), yL - 3); ictx.lineTo(X(pk), yL + 3);
    ictx.stroke();
    // trough-to-peak duration label, on a white pill so it stays legible over the droplines
    var ms = (pk - tr) / FS * 1000, txt = ms.toFixed(2) + " ms";
    ictx.font = "italic 10px Georgia, serif"; ictx.textAlign = "center"; ictx.textBaseline = "alphabetic";
    var lx = (X(tr) + X(pk)) / 2, ly = yL - 5, tw = ictx.measureText(txt).width, lp = 3;
    ictx.fillStyle = "rgba(255,255,255,.92)";
    if (ictx.roundRect) { ictx.beginPath(); ictx.roundRect(lx - tw / 2 - lp, ly - 9, tw + 2 * lp, 12, 3); ictx.fill(); }
    else { ictx.fillRect(lx - tw / 2 - lp, ly - 9, tw + 2 * lp, 12); }
    ictx.fillStyle = "#33312e"; ictx.fillText(txt, lx, ly);
    // caption — descriptor is the cluster's fixed character (stable per cluster),
    // shown next to this neuron's own measured trough-to-peak above.
    labelEl.innerHTML = "<b>Cluster " + (p.c + 1) + "</b> · " + (clusterKind[p.c] || "intermediate");
    labelEl.style.color = col;
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = TH.edge; ctx.lineWidth = 0.7; ctx.beginPath();
    for (var e = 0; e < data.edges.length; e++) {
      var pa = P[data.edges[e][0]], pb = P[data.edges[e][1]];
      if (pa.om || pb.om) continue;
      ctx.moveTo(pa.sx, pa.sy); ctx.lineTo(pb.sx, pb.sy);
    }
    ctx.stroke();
    for (var i = 0; i < P.length; i++) {
      var p = P[i];
      if (p.om) continue;
      ctx.beginPath(); ctx.arc(p.sx, p.sy, i === active ? 6 : 3.3, 0, 6.2832);
      ctx.fillStyle = colorFor(p.c); ctx.globalAlpha = i === active ? 1 : 0.82; ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (active >= 0) {
      var a = P[active];
      ctx.beginPath(); ctx.arc(a.sx, a.sy, 9, 0, 6.2832); ctx.strokeStyle = colorFor(a.c); ctx.lineWidth = 1.5; ctx.stroke();
      var r = insetWrap.getBoundingClientRect(), hr = hero.getBoundingClientRect();
      var tx = r.left - hr.left + r.width * 0.5, ty = r.top - hr.top;
      ctx.strokeStyle = TH.edge; ctx.setLineDash([3, 3]); ctx.beginPath();
      ctx.moveTo(a.sx, a.sy); ctx.lineTo(tx, ty); ctx.stroke(); ctx.setLineDash([]);
    }
  }

  function randLive() { var i, g = 0; do { i = Math.floor(Math.random() * P.length); g++; } while (P[i] && P[i].om && g < 60); return i; }
  function frame(t) {
    if (!hoverLock && !reduce && t > nextTour) { active = randLive(); drawInset(); nextTour = t + 3800; }
    draw();
    raf = requestAnimationFrame(frame);
  }

  hero.addEventListener("mousemove", function (e) {
    if (mobile) return;                 // non-interactive on mobile
    var hr = hero.getBoundingClientRect(), mx = e.clientX - hr.left, my = e.clientY - hr.top;
    var best = -1, bd = 26 * 26;
    for (var i = 0; i < P.length; i++) {
      if (P[i].om) continue;
      var dx = P[i].sx - mx, dy = P[i].sy - my, d = dx * dx + dy * dy;
      if (d < bd) { bd = d; best = i; }
    }
    if (best >= 0) { hoverLock = true; active = best; drawInset(); } else { hoverLock = false; }
  });
  hero.addEventListener("mouseleave", function () { hoverLock = false; });

  function start() {
    TH = theme(); layout();
    mobile = window.matchMedia("(max-width: 760px)").matches;
    if (raf) cancelAnimationFrame(raf);
    if (mobile) {            // mobile: a faint, static, non-interactive backdrop (CSS fades it out)
      active = -1; drawInset(); draw(); return;
    }
    if (active < 0) active = randLive();
    drawInset();
    if (reduce) draw(); else { nextTour = 0; raf = requestAnimationFrame(frame); }
  }
  var rt;
  window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(start, 150); });
  start();
})();
