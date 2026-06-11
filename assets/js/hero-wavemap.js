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

  // cluster colormap encodes spike width: narrow (blue) -> broad (red).
  // Sampled to however many clusters the data has (ECG decides the count).
  var RAMP = ["#2563eb", "#06b6d4", "#10b981", "#eab308", "#f97316", "#ef4444"];
  function hx(h) { h = h.replace("#", ""); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
  function xh(c) { return "#" + c.map(function (v) { return ("0" + Math.max(0, Math.min(255, Math.round(v))).toString(16)).slice(-2); }).join(""); }
  function palette(K) {
    var r = RAMP.map(hx);
    if (K <= 1) return [RAMP[0]];
    var out = [];
    for (var i = 0; i < K; i++) {
      var t = i / (K - 1) * (r.length - 1), lo = Math.floor(t), hi = Math.min(lo + 1, r.length - 1), f = t - lo;
      out.push(xh([0, 1, 2].map(function (j) { return r[lo][j] + (r[hi][j] - r[lo][j]) * f; })));
    }
    return out;
  }
  var PAL = RAMP.slice();
  function colorFor(c) { return PAL[c % PAL.length]; }

  function theme() {
    var cs = getComputedStyle(document.documentElement);
    function v(n, f) { var x = cs.getPropertyValue(n).trim(); return x || f; }
    return {
      edge: v("--hero-edge-inter", "rgba(37,99,235,0.18)"),
      ink:  v("--ink", "#14171c")
    };
  }
  var TH = theme();

  var data;
  try { data = await fetch("assets/data/wavemap.json").then(function (r) { return r.json(); }); }
  catch (e) { return; }
  PAL = palette(data.clusters || 6);

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
    var x0 = wide ? W * 0.42 : W * 0.05, x1 = W * 0.98;
    var y0 = H * 0.13, y1 = H * 0.90;
    P = data.points.map(function (p) {
      return { sx: x0 + (-p.x * 0.5 + 0.5) * (x1 - x0), sy: y0 + (p.y * 0.5 + 0.5) * (y1 - y0), c: p.c, w: p.w };
    });
  }

  var active = -1, hoverLock = false, nextTour = 0, raf = null;

  function drawInset() {
    if (active < 0) { insetWrap.style.opacity = 0; return; }
    insetWrap.style.opacity = 1;
    var p = P[active], col = colorFor(p.c), w = p.w, n = w.length;
    var iw = inset.clientWidth, ih = inset.clientHeight;
    inset.width = iw * dpr; inset.height = ih * dpr; ictx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ictx.clearRect(0, 0, iw, ih);
    var pad = 10, mn = Math.min.apply(null, w), mx = Math.max.apply(null, w), rng = (mx - mn) || 1;
    // zero baseline
    ictx.strokeStyle = "rgba(20,23,28,.12)"; ictx.lineWidth = 1;
    var zy = pad + (1 - (0 - mn) / rng) * (ih - 2 * pad);
    ictx.beginPath(); ictx.moveTo(pad, zy); ictx.lineTo(iw - pad, zy); ictx.stroke();
    // waveform
    ictx.strokeStyle = col; ictx.lineWidth = 2.4; ictx.lineJoin = "round"; ictx.beginPath();
    for (var i = 0; i < n; i++) {
      var xx = pad + i / (n - 1) * (iw - 2 * pad);
      var yy = pad + (1 - (w[i] - mn) / rng) * (ih - 2 * pad);
      if (i) ictx.lineTo(xx, yy); else ictx.moveTo(xx, yy);
    }
    ictx.stroke();
    var K = data.clusters || 6;
    var kind = p.c < K * 0.3 ? "narrow-spiking" : (p.c >= K * 0.66 ? "broad-spiking" : "intermediate");
    labelEl.innerHTML = "<b>Cluster " + (p.c + 1) + "</b> · " + kind + " · " + t2p(w) + "-sample trough-to-peak";
    labelEl.style.color = col;
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = TH.edge; ctx.lineWidth = 0.7; ctx.beginPath();
    for (var e = 0; e < data.edges.length; e++) {
      var pa = P[data.edges[e][0]], pb = P[data.edges[e][1]];
      ctx.moveTo(pa.sx, pa.sy); ctx.lineTo(pb.sx, pb.sy);
    }
    ctx.stroke();
    for (var i = 0; i < P.length; i++) {
      var p = P[i];
      ctx.beginPath(); ctx.arc(p.sx, p.sy, i === active ? 5 : 2.6, 0, 6.2832);
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

  function frame(t) {
    if (!hoverLock && !reduce && t > nextTour) { active = Math.floor(Math.random() * P.length); drawInset(); nextTour = t + 2200; }
    draw();
    raf = requestAnimationFrame(frame);
  }

  hero.addEventListener("mousemove", function (e) {
    var hr = hero.getBoundingClientRect(), mx = e.clientX - hr.left, my = e.clientY - hr.top;
    var best = -1, bd = 26 * 26;
    for (var i = 0; i < P.length; i++) {
      var dx = P[i].sx - mx, dy = P[i].sy - my, d = dx * dx + dy * dy;
      if (d < bd) { bd = d; best = i; }
    }
    if (best >= 0) { hoverLock = true; active = best; drawInset(); } else { hoverLock = false; }
  });
  hero.addEventListener("mouseleave", function () { hoverLock = false; });

  function start() {
    TH = theme(); layout();
    if (active < 0) active = Math.floor(Math.random() * P.length);
    drawInset();
    if (raf) cancelAnimationFrame(raf);
    if (reduce) draw(); else { nextTour = 0; raf = requestAnimationFrame(frame); }
  }
  var rt;
  window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(start, 150); });
  start();
})();
