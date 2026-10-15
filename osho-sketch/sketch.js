// Animated p5.brush sketch of Osho, built up stroke by stroke from a reference photo.
//
// Each portrait is drawn in layers, the way a sketch artist works:
//   block  – soft charcoal that blocks in the darkest masses
//   tone   – light pencil strokes following the form; they pile up where the photo is dark
//   cross  – cross-hatching in the shadows
//   lift   – paper-coloured "eraser" strokes that pull highlights back out of the shadows
//   detail – short fine strokes concentrated on edges (eyes, beard, hands)
//   accent – a few confident ink lines along the strongest contours
// When a portrait is finished it rests for a moment, then the next one begins.

// crop:  [x0, y0, x1, y1] as fractions of the photo, framing the face for a portrait canvas.
// focus: [x, y] centre of the vignette as fractions of the canvas; strokes fade out away from it.
// fade:  [start, end] radius of the vignette, as a fraction of the half-diagonal.
// gamma: < 1 darkens midtones (brings out facial shading), > 1 lightens them.
const PHOTOS = [
  { src: "images/osho-2.jpg", crop: [0.12, 0, 0.82, 1], focus: [0.52, 0.4], gamma: 0.8, fade: [0.25, 0.8] },
  { src: "images/osho-1.jpg", crop: [0.24, 0.05, 0.84, 1], focus: [0.5, 0.45], gamma: 1.3, fade: [0.5, 1.1] },
];
const PAPER = "#f3ece0";
const INK = ["#2b2621", "#33291f", "#45362a"];
const W = 720;
const H = 860;
const STROKES_PER_FRAME = 70;
const HOLD_FRAMES = 300;

// pick(d, e, l) returns the probability of keeping a spot with darkness d, edge strength e and local lightness l.
const PASSES = [
  { brushName: "charcoal", count: 500,  weight: [0.5, 0.9],  len: [30, 60], alpha: 50,  turn: 0,       pick: (d) => ramp(0.55, 0.9, d) },
  { brushName: "2B",       count: 6500, weight: [0.35, 0.6], len: [10, 26], alpha: 120, turn: 0,       pick: (d) => d * d },
  { brushName: "2B",       count: 3000, weight: [0.3, 0.5],  len: [8, 20],  alpha: 110, turn: Math.PI / 2.5, pick: (d) => ramp(0.5, 0.85, d) },
  { brushName: "HB",       count: 1500, weight: [0.3, 0.5],  len: [5, 12],  alpha: 140, turn: 0,       pick: (d, e, l) => ramp(0.04, 0.2, l), color: PAPER },
  { brushName: "HB",       count: 3500, weight: [0.25, 0.4], len: [5, 12],  alpha: 170, turn: 0,       pick: (d, e) => ramp(0.12, 0.45, e) * (0.4 + d) },
  { brushName: "pen",      count: 450,  weight: [0.18, 0.3], len: [12, 28], alpha: 200, turn: 0,       pick: (d, e) => ramp(0.35, 0.7, e) },
];

let maps = [];
let current = 0;
let passIndex = 0;
let drawnInPass = 0;
let holdCounter = 0;

async function setup() {
  const photos = await Promise.all(PHOTOS.map((p) => loadImage(p.src)));
  createCanvas(W, H, WEBGL);
  pixelDensity(1);
  maps = photos.map((img, k) => analyse(img, PHOTOS[k]));
  startPortrait();
}

function ramp(a, b, x) {
  const t = constrain((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}

// Draw the cropped photo to cover the canvas, return its grayscale pixels after a blur.
function sample(img, crop, blurAmount) {
  const g = createGraphics(W, H);
  g.pixelDensity(1);
  const sx = crop[0] * img.width, sy = crop[1] * img.height;
  const sw = (crop[2] - crop[0]) * img.width, sh = (crop[3] - crop[1]) * img.height;
  const s = Math.max(W / sw, H / sh);
  g.image(img, (W - sw * s) / 2, (H - sh * s) / 2, sw * s, sh * s, sx, sy, sw, sh);
  g.filter(BLUR, blurAmount);
  g.loadPixels();
  const out = new Float32Array(W * H);
  const px = g.pixels;
  for (let i = 0; i < W * H; i++) out[i] = 1 - (0.299 * px[i * 4] + 0.587 * px[i * 4 + 1] + 0.114 * px[i * 4 + 2]) / 255;
  g.remove();
  return out;
}

function sobel(src, x, y) {
  const i = y * W + x;
  return [
    src[i - W + 1] + 2 * src[i + 1] + src[i + W + 1] - src[i - W - 1] - 2 * src[i - 1] - src[i + W - 1],
    src[i + W - 1] + 2 * src[i + W] + src[i + W + 1] - src[i - W - 1] - 2 * src[i - W] - src[i - W + 1],
  ];
}

// Precompute normalised darkness, edge strength and a smooth stroke direction field.
function analyse(img, { crop, focus, gamma, fade }) {
  const fine = sample(img, crop, 1);
  const soft = sample(img, crop, 7);

  // Stretch contrast between the 5th and 98th percentile so mid-grey backgrounds stay light.
  const sorted = Float32Array.from(fine).sort();
  const lo = sorted[Math.floor(sorted.length * 0.05)];
  const hi = sorted[Math.floor(sorted.length * 0.98)];
  const dark = new Float32Array(W * H);
  const fx = focus[0] * W, fy = focus[1] * H, R = Math.hypot(W, H) / 2;
  for (let i = 0; i < dark.length; i++) {
    const r = Math.hypot((i % W) - fx, Math.floor(i / W) - fy) / R;
    const vignette = 1 - ramp(fade[0], fade[1], r);
    dark[i] = Math.pow(constrain((fine[i] - lo) / (hi - lo), 0, 1), gamma) * vignette;
  }

  // Local lightness: how much brighter a pixel is than its neighbourhood (eyes, nose, beard highlights).
  const light = new Float32Array(W * H);
  for (let i = 0; i < light.length; i++) light[i] = Math.max(0, soft[i] - fine[i]) / (hi - lo);

  const edge = new Float32Array(W * H);
  const angle = new Float32Array(W * H);
  let maxEdge = 1e-6;
  for (let y = 1; y < H - 1; y++) {
    for (let x = 1; x < W - 1; x++) {
      const i = y * W + x;
      const [ex, ey] = sobel(dark, x, y);
      edge[i] = Math.hypot(ex, ey);
      maxEdge = Math.max(maxEdge, edge[i]);
      // Strokes run along contours: perpendicular to the (smoothed) gradient.
      const [sx, sy] = sobel(soft, x, y);
      angle[i] = Math.hypot(sx, sy) > 0.02 ? Math.atan2(sy, sx) + HALF_PI : -Math.PI / 4;
    }
  }
  for (let i = 0; i < edge.length; i++) edge[i] = Math.min(1, edge[i] / (maxEdge * 0.5));
  return { dark, edge, angle, light };
}

function startPortrait() {
  background(PAPER);
  passIndex = 0;
  drawnInPass = 0;
  holdCounter = 0;
}

function draw() {
  if (passIndex >= PASSES.length) {
    if (++holdCounter > HOLD_FRAMES) nextPortrait();
    return;
  }
  const pass = PASSES[passIndex];
  for (let n = 0; n < STROKES_PER_FRAME && drawnInPass < pass.count; n++) {
    if (drawStroke(pass, maps[current])) drawnInPass++;
  }
  if (drawnInPass >= pass.count) {
    passIndex++;
    drawnInPass = 0;
  }
}

function mousePressed() {
  nextPortrait();
}

function nextPortrait() {
  current = (current + 1) % maps.length;
  startPortrait();
}

// Pick a spot by rejection sampling against the pass's pick() rule, then lay one stroke there.
function drawStroke(pass, map) {
  for (let tries = 0; tries < 60; tries++) {
    const x = Math.floor(random(2, W - 2));
    const y = Math.floor(random(2, H - 2));
    const i = y * W + x;
    const d = map.dark[i];
    if (random() > pass.pick(d, map.edge[i], map.light[i])) continue;

    const a = map.angle[i] + pass.turn + random(-0.18, 0.18);
    const len = random(pass.len[0], pass.len[1]);
    const col = color(pass.color || random(INK));
    col.setAlpha(pass.color ? pass.alpha : pass.alpha * (0.5 + 0.5 * d));
    brush.set(pass.brushName, col, random(pass.weight[0], pass.weight[1]));

    const cx = x - W / 2, cy = y - H / 2;
    const dx = (Math.cos(a) * len) / 2, dy = (Math.sin(a) * len) / 2;
    brush.line(cx - dx, cy - dy, cx + dx, cy + dy);
    return true;
  }
  return false;
}
