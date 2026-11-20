// Record a ~65 s showcase of all 20 sites: each clip runs a scripted interaction,
// frames come from CDP screencast and are resampled to 30 fps for ffmpeg.
import { chromium } from "playwright-core";
import fs from "node:fs";
const BASE = "http://localhost:8765", OUT = new URL("./frames/", import.meta.url).pathname, FPS = 30;
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
const exe = process.env.HOME + "/Library/Caches/ms-playwright/chromium-1252/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
const browser = await chromium.launch({ headless: true, executablePath: exe, args: ["--window-size=1280,720", "--force-device-scale-factor=1.5", "--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
const cdp = await page.context().newCDPSession(page);
let frames = [], n = 0;
cdp.on("Page.screencastFrame", f => { frames.push({ t: f.metadata.timestamp, data: f.data }); cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {}); });
const W = 1280, H = 720, wait = ms => page.waitForTimeout(ms);
const box = async sel => page.locator(sel).first().boundingBox();
async function glide(x0, y0, x1, y1, ms, down = false) {
  const steps = Math.max(2, Math.round(ms / 16));
  await page.mouse.move(x0, y0); if (down) await page.mouse.down();
  for (let i = 1; i <= steps; i++) { const k = i / steps, e = k < .5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2; await page.mouse.move(x0 + (x1 - x0) * e, y0 + (y1 - y0) * e); await wait(16); }
  if (down) await page.mouse.up();
}
async function scrollTo(y, ms) { await page.evaluate(([y, ms]) => new Promise(r => { const y0 = scrollY, t0 = performance.now(); (function f(t) { const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2; scrollTo(0, y0 + (y - y0) * e); k < 1 ? requestAnimationFrame(f) : r(); })(t0); }), [y, ms]); }
async function label(no, name, tech) {
  await page.evaluate(([no, name, tech]) => {
    const d = document.createElement("div"); d.id = "__label";
    d.innerHTML = `<b>${no}</b><span>${name}</span><i>${tech}</i>`;
    d.style.cssText = "position:fixed;left:24px;bottom:24px;z-index:2147483647;display:flex;gap:12px;align-items:baseline;padding:10px 16px;background:rgba(18,17,14,.86);color:#f1ebdd;font:500 17px/1.2 'PingFang SC',sans-serif;border-radius:3px;pointer-events:none;backdrop-filter:blur(6px)";
    d.querySelector("b").style.cssText = "color:#e0703c;font:600 15px ui-monospace,monospace";
    d.querySelector("i").style.cssText = "font-style:normal;color:#a39d8c;font-size:14px";
    document.body.append(d);
  }, [no, name, tech]);
}
async function clip(fn, ms) {
  frames = [];
  await cdp.send("Page.startScreencast", { format: "jpeg", quality: 88, maxWidth: 1920, maxHeight: 1080 });
  const t0 = Date.now(); await fn(); const rest = ms - (Date.now() - t0); if (rest > 0) await wait(rest);
  await cdp.send("Page.stopScreencast"); await wait(150);
  if (!frames.length) return console.log("no frames!");
  const start = frames[0].t, end = start + ms / 1000;
  for (let t = start, j = 0; t < end; t += 1 / FPS) {
    while (j + 1 < frames.length && frames[j + 1].t <= t) j++;
    fs.writeFileSync(`${OUT}${String(n++).padStart(5, "0")}.jpg`, Buffer.from(frames[j].data, "base64"));
  }
}
async function open(site, settle = 2200) { await page.goto(`${BASE}/sites/${site}/?lang=zh`, { waitUntil: "load" }); await page.mouse.move(W - 4, 4); await wait(settle); }

// title card
await page.goto(`${BASE}/tools/video/card.html?k=title`); await wait(1500);
await clip(async () => {}, 2600);

const S = [
  ["01-halftone", "Acta 公报", "双色网点 · 印刷放大镜", async () => { await open("01-halftone", 1500); const y = await page.evaluate(() => { const c = [...document.querySelectorAll("canvas")].sort((a, b) => b.width * b.height - a.width * a.height)[0]; return c.getBoundingClientRect().top + scrollY - 60; }); await page.evaluate(y => scrollTo(0, y), y); await wait(1200); }, async () => { await glide(300, 330, 980, 420, 1500); await glide(980, 420, 640, 300, 1300); }],
  ["02-collage", "Cloudrift 云隙", "滚动撕开云层", async () => open("02-collage", 2600), async () => scrollTo(1500, 3000)],
  ["03-meadow", "Tend", "WebGL2 · 14.6 万根草", async () => open("03-meadow", 2500), async () => { await glide(80, 640, 1200, 590, 1500); await glide(1200, 590, 200, 660, 1400); }],
  ["04-object", "Ballast", "实时光线步进 · 按住签名", async () => open("04-object", 2000), async () => { const b = await box("#key"); const cx = b.x + b.width / 2, cy = b.y + b.height / 2; await glide(cx - 220, cy - 120, cx, cy, 900); await page.mouse.down(); await wait(2000); await page.mouse.up(); }],
  ["05-ink", "Inkstone 砚", "墨晕显影 · 盖印", async () => {}, async (lab) => { await page.goto(`${BASE}/sites/05-ink/?lang=zh`); await lab(); await wait(3200); }],
  ["06-ukiyoe", "Nami 波", "五块色版现场套印", async () => {}, async (lab) => { await page.goto(`${BASE}/sites/06-ukiyoe/?lang=zh`); await lab(); await wait(3300); const b = await box("canvas, .print, figure"); await glide(900, 300, 1000, 420, 700); }],
  ["07-riso", "Specimen 标本", "双滚筒套色 · 拖动错位", async () => open("07-riso", 2200), async () => { const b = await box("#hero-print"); const cx = b.x + b.width / 2, cy = b.y + b.height / 2; await glide(cx, cy, cx + 70, cy + 40, 1100, true); await wait(300); await glide(cx, cy, cx - 50, cy - 30, 1000, true); }],
  ["08-cyanotype", "Pressed", "鼠标就是太阳", async () => open("08-cyanotype", 1500), async () => { for (let i = 0; i < 6; i++) await glide(860 + (i % 3) * 110, 200 + i * 60, 900 + ((i + 1) % 3) * 110, 230 + i * 60, 480); }],
  ["09-onebit", "Speck", "镜头窗口重新抖动", async () => open("09-onebit", 1800), async () => { const b = await box("#lensBar"); const p = await box("#photo"); await glide(b.x + 40, b.y + 8, p.x + p.width * .25, p.y + 20, 1400, true); await glide(p.x + p.width * .25 + 0, p.y + 20, p.x + p.width * .55, p.y + p.height * .45, 1400, true); }],
  ["10-celestial", "Firmament 穹", "1010 颗真星 · 1690 年星座图", async () => open("10-celestial", 2500), async () => { await glide(1100, 300, 880, 420, 1400); await glide(880, 420, 900, 470, 1400); }],
  ["11-guilloche", "Tessera 契纹", "实时扭索纹 · 紫外灯", async () => open("11-guilloche", 2000), async () => { const b = await box("#noteCanvas"); await glide(b.x + 80, b.y + 80, b.x + b.width * .6, b.y + b.height * .5, 1300); await page.getByText(/紫外灯/).first().click(); await glide(b.x + b.width * .55, b.y + b.height * .3, b.x + b.width * .85, b.y + b.height * .5, 1400); }],
  ["12-manuscript", "Rubric 朱批", "WebGL 金箔反光", async () => open("12-manuscript", 2600), async () => { const b = await box("canvas.leaf"); const cx = b.x + b.width / 2, cy = b.y + b.height / 2; await glide(cx - 160, cy - 140, cx + 160, cy + 140, 1500); await glide(cx + 160, cy + 140, cx - 120, cy + 120, 1400); }],
  ["13-codex", "Mensura 度", "拖身高 · 比例重算", async () => open("13-codex", 2600), async () => { for (const v of [...Array(25)].map((_, i) => 175 - i).concat([...Array(45)].map((_, i) => 151 + i))) { await page.evaluate(v => { const r = document.getElementById("hgt"); r.value = v; r.dispatchEvent(new Event("input", { bubbles: true })); }, v); await wait(36); } }],
  ["14-ascii", "Glyph", "实时字符画 · 滚动解码", async () => open("14-ascii", 2500), async () => { await glide(760, 220, 880, 300, 1100); await scrollTo(720, 1900); }],
  ["15-glass", "Vitrail 花窗", "彩色的光跟着鼠标走", async () => open("15-glass", 2400), async () => { await glide(150, 380, 700, 300, 1400); await glide(700, 300, 300, 520, 1400); }],
  ["16-contour", "Saddle 鞍部", "鼠标塑形 · 等高线实时重算", async () => open("16-contour", 2000), async () => { await page.mouse.move(760, 420); await page.mouse.down(); for (let i = 0; i < 80; i++) { await page.mouse.move(760 + Math.cos(i / 6) * 60, 420 + Math.sin(i / 6) * 40); await wait(30); } await page.mouse.up(); }],
  ["17-marble", "Ebb & Comb 流沙笺", "滴墨 · 拉梳", async () => open("17-marble", 3500), async () => { await glide(700, 160, 1150, 600, 1600, true); await glide(1150, 200, 650, 560, 1400, true); }],
  ["18-swiss", "Raster 栅格", "改栏数 · 全版重排", async () => open("18-swiss", 2000), async () => { for (const c of ["3", "8", "12", "4"]) { await page.evaluate(c => { const b = [...document.querySelectorAll("button")].find(b => b.textContent.trim() === c && b.offsetParent); b && b.click(); }, c); await wait(780); } }],
  ["19-bauhaus", "Vorkurs 预科", "手写物理引擎", async () => {}, async (lab) => { await page.goto(`${BASE}/sites/19-bauhaus/?lang=zh`); await lab(); await wait(1800); for (const x of [900, 1020, 1140]) { await page.mouse.click(x, 140); await wait(250); } }],
  ["20-vhs", "Rewind 回带", "鼠标就是跟踪旋钮", async () => open("20-vhs", 2600), async () => { const b = await box("#heroScreen"); await glide(b.x + 30, b.y + b.height / 2, b.x + b.width - 30, b.y + b.height / 2, 1400); await glide(b.x + b.width - 30, b.y + b.height / 2, b.x + b.width * .4, b.y + b.height / 2, 1400); }],
];
const only = process.argv[2];
for (const [site, name, tech, pre, act] of S) {
  if (only && !site.startsWith(only)) continue;
  await pre();
  const lab = async () => { await label(site.slice(0, 2), name, tech); };
  if (page.url().includes(site)) await lab();
  await clip(async () => { await act(lab); }, 3000);
  console.log(site, n);
}
if (!only) { await page.goto(`${BASE}/tools/video/card.html?k=end`); await wait(1500); await clip(async () => {}, 3200); }
await browser.close();
console.log("frames:", n);
