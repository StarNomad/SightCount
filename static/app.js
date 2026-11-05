// SightCount v1 — browser side.
// Counting = connected-component count of dark blobs in the frame.
// Honest by design: this is a blob estimate, NOT a verified person detector.
// Sample mode draws synthetic figures on the canvas, so its count is a
// count of drawn figures, and the UI labels it as such.

const canvas = document.getElementById('view');
const ctx = canvas.getContext('2d');
const video = document.getElementById('video');
const modeEl = document.getElementById('mode');
const sizeEl = document.getElementById('sampleSize');
const fileInput = document.getElementById('fileInput');
const startCam = document.getElementById('startCam');
let lastScene = null;
let stream = null;

function log(msg) {
  const li = document.createElement('li');
  li.textContent = new Date().toLocaleTimeString() + ' — ' + msg;
  document.getElementById('log').prepend(li);
}

// Deterministic pseudo-random so a sample scene is reproducible.
function mulberry(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function drawSample(n) {
  ctx.fillStyle = '#eef2f5'; ctx.fillRect(0, 0, 640, 360);
  ctx.fillStyle = '#223';
  const rnd = mulberry(42 + n * 7);
  // Grid placement with jitter: figures never overlap, so the blob
  // counter below counts drawn figures exactly.
  const cols = 8, cellW = 80, cellH = 90;
  for (let i = 0; i < n; i++) {
    const col = i % cols, row = Math.floor(i / cols);
    const x = col * cellW + 20 + rnd() * 20;
    const y = row * cellH + 30 + rnd() * 15;
    ctx.beginPath(); ctx.ellipse(x, y, 12, 20, 0, 0, Math.PI * 2); ctx.fill(); // body
    ctx.beginPath(); ctx.arc(x, y - 28, 8, 0, Math.PI * 2); ctx.fill();       // head
  }
  video.hidden = true; canvas.hidden = false;
}

function countBlobs() {
  const img = ctx.getImageData(0, 0, 640, 360).data;
  const W = 640, H = 360;
  const dark = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const r = img[i * 4], g = img[i * 4 + 1], b = img[i * 4 + 2];
    dark[i] = (r + g + b) / 3 < 110 ? 1 : 0;
  }
  const seen = new Uint8Array(W * H);
  let count = 0; const centroids = [];
  const stack = [];
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const idx = y * W + x;
    if (!dark[idx] || seen[idx]) continue;
    let size = 0, sx = 0, sy = 0; stack.length = 0; stack.push(idx); seen[idx] = 1;
    while (stack.length) {
      const p = stack.pop(); const px = p % W, py = (p / W) | 0;
      size++; sx += px; sy += py;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = px + dx, ny = py + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const np = ny * W + nx;
        if (dark[np] && !seen[np]) { seen[np] = 1; stack.push(np); }
      }
    }
    if (size >= 40) { count++; centroids.push([sx / size, sy / size]); }
  }
  // Grouping: clusters of centroids within 120px of each other.
  const grouped = new Set(); let groups = 0;
  for (let i = 0; i < centroids.length; i++) {
    if (grouped.has(i)) continue; groups++;
    for (let j = 0; j < centroids.length; j++) {
      const d = Math.hypot(centroids[i][0] - centroids[j][0], centroids[i][1] - centroids[j][1]);
      if (d < 120) grouped.add(j);
    }
  }
  const xs = centroids.map(c => c[0]);
  const spread = xs.length ? (Math.max(...xs) - Math.min(...xs) > 320 ? 'wide' : 'compact') : 'none';
  return { count, groups, spread };
}

async function refreshBadge() {
  try {
    const r = await fetch('/api/health'); const j = await r.json();
    document.getElementById('apiBadge').textContent =
      j.meta_api_key_set ? 'META MODEL API: key set' : 'LOCAL FALLBACK: no key set';
  } catch { document.getElementById('apiBadge').textContent = 'API: server unreachable'; }
}

modeEl.addEventListener('change', async () => {
  const m = modeEl.value;
  fileInput.hidden = m !== 'upload';
  startCam.hidden = m !== 'webcam';
  if (m === 'sample') { drawSample(parseInt(sizeEl.value, 10) || 0); log('Sample scene drawn (synthetic demo).'); }
  if (m === 'upload') fileInput.click();
});

sizeEl.addEventListener('change', () => {
  if (modeEl.value === 'sample') drawSample(parseInt(sizeEl.value, 10) || 0);
});

fileInput.addEventListener('change', () => {
  const f = fileInput.files[0]; if (!f) return;
  const img = new Image();
  img.onload = () => {
    ctx.fillStyle = '#eef2f5'; ctx.fillRect(0, 0, 640, 360);
    ctx.drawImage(img, 0, 0, 640, 360);
    video.hidden = true; canvas.hidden = false;
    log('Image uploaded; blob estimate only, not a verified headcount.');
  };
  img.src = URL.createObjectURL(f);
});

startCam.addEventListener('click', async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream; video.hidden = false; canvas.hidden = true;
    log('Camera started (preview only until a frame is captured).');
  } catch { log('Camera permission denied or unavailable.'); }
});

document.getElementById('countBtn').addEventListener('click', () => {
  const mode = modeEl.value;
  if (mode === 'webcam' && stream) {
    ctx.drawImage(video, 0, 0, 640, 360);
    video.hidden = true; canvas.hidden = false;
  }
  if (mode === 'sample') drawSample(parseInt(sizeEl.value, 10) || 0);
  const s = countBlobs();
  lastScene = { ...s, mode, note: mode === 'sample' ? 'synthetic demo scene' : 'blob estimate, not a verified headcount' };
  document.getElementById('countOut').textContent = s.count + (mode === 'sample' ? ' drawn figures' : ' blobs (estimate)');
  document.getElementById('countNote').textContent =
    mode === 'sample'
      ? 'Sample mode: synthetic scene, count = drawn figures.'
      : 'Estimate only: simple blob counter, not a person detector.';
  log(`Counted ${s.count} in ${s.groups} cluster(s), spread ${s.spread} (${mode}).`);
});

document.getElementById('interpretBtn').addEventListener('click', async () => {
  if (!lastScene) { log('Count a frame first.'); return; }
  document.getElementById('interpOut').textContent = 'Interpreting…';
  try {
    const r = await fetch('/api/interpret', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lastScene),
    });
    const j = await r.json();
    document.getElementById('interpSource').textContent = 'Source: ' + j.source;
    document.getElementById('interpOut').textContent =
      `Mood: ${j.mood}\nAttention: ${j.attention}\nGrouping: ${j.grouping}\n${j.happening}`;
    log('Scene interpreted via ' + j.source + '.');
  } catch { document.getElementById('interpOut').textContent = 'Interpretation failed (server unreachable).'; }
});

drawSample(parseInt(sizeEl.value, 10) || 12);
refreshBadge();
log('SightCount ready. Sample scene loaded (synthetic demo).');
