# Build data + images for the celestial site:
#  - bright stars (V<=4.6) + stick-figure lines, injected into index.html between /*DATA*/ markers
#  - three Hevelius figures as gold-on-transparent WebP, with sky<->plate reference points for live alignment
#  - Cellarius plate, web-sized
import json, math, re
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import tools_fit as t

def inv_tangent(x, y, ra0, dec0):
    ra0r, dec0r = math.radians(ra0), math.radians(dec0); rho = math.hypot(x, y); c = math.atan(rho)
    if rho == 0: return ra0, dec0
    dec = math.asin(math.cos(c) * math.sin(dec0r) + y * math.sin(c) * math.cos(dec0r) / rho)
    ra = ra0r + math.atan2(x * math.sin(c), rho * math.cos(dec0r) * math.cos(c) - y * math.sin(dec0r) * math.sin(c))
    return math.degrees(ra) % 360, math.degrees(dec)

def solve(anchors, preview_w, src):
    w = Image.open(f"src-img/{src}").width; k = w / preview_w
    ss = [t.find(*a[0]) for a in anchors]
    ra0 = float(np.mean([s["ra"] for s in ss])); dec0 = float(np.mean([s["dec"] for s in ss]))
    A = np.array([[*t.tangent(s, ra0, dec0), 1] for s in ss]); P = np.array([[a[1] * k, a[2] * k] for a in anchors])
    return dict(ra0=ra0, dec0=dec0, M=np.linalg.lstsq(A, P, rcond=None)[0])

FIG = {
  "Ori": dict(src="orion.jpg", crop=(370, 55, 760, 630), erase=[(540, 98, 636, 126), (690, 100, 720, 140)], fit=dict(ra0=82.90347222222222, dec0=1.8516666666666668,
         M=np.array([[3175.008, 181.600], [256.829, -3420.865], [2090.079, 1530.493]]))),
  "Leo": dict(src="leo.jpg", crop=(170, 60, 880, 560), erase=[(500, 178, 562, 202), (355, 72, 470, 100), (830, 345, 880, 375), (175, 330, 160, 360), (580, 410, 650, 432), (190, 410, 240, 432), (730, 480, 800, 505)], fit=solve([(("Leo", "α"), 429, 401), (("Leo", "β"), 779, 203), (("Leo", "δ"), 577, 190), (("Leo", "θ"), 650, 245)], 1000, "leo.jpg")),
  "UMa": dict(src="uma.jpg", crop=(150, 140, 830, 690), erase=[(428, 198, 548, 228), (290, 155, 355, 180), (150, 510, 210, 535), (560, 615, 655, 640), (750, 460, 810, 485), (820, 255, 830, 280)], fit=solve([(("UMa", b), x, y) for b, x, y in
         [("α", 467, 285), ("β", 499, 351), ("γ", 593, 321), ("δ", 590, 257), ("ε", 645, 219), ("ζ", 690, 192)]], 1000, "uma.jpg")),
}
GOLD = np.array([236, 205, 140], float)
figs = {}
for key, f in FIG.items():
    im = Image.open(f"src-img/{f['src']}").convert("RGB"); k = im.width / 1000
    x0, y0, x1, y1 = [int(v * k) for v in f["crop"]]
    c = im.crop((x0, y0, x1, y1)); scale = min(1.0, 1100 / max(c.size)); c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
    g = ImageOps.grayscale(c)
    L = np.asarray(g).astype(float) / 255
    local = np.asarray(g.filter(ImageFilter.GaussianBlur(5))).astype(float) / 255
    lines = np.clip((local - L) * 7, 0, 1)                    # engraved strokes only, hand-colouring ignored
    paper = np.percentile(L, 92); tone = np.clip((paper - L) / paper, 0, 1)
    a = np.clip(lines * .95 + tone * .18, 0, 1) ** .9
    yy, xx = np.mgrid[0:c.height, 0:c.width]; e = np.hypot((xx / c.width - .5) / .5, (yy / c.height - .5) / .5)
    a *= np.clip((1.08 - e) / .32, 0, 1)                      # soft oval vignette hides plate borders
    for ex0, ey0, ex1, ey1 in f.get("erase", []):             # plate lettering would read mirrored on the sky
        X0, X1 = sorted(((ex0 * k - x0) * scale, (ex1 * k - x0) * scale)); Y0, Y1 = sorted(((ey0 * k - y0) * scale, (ey1 * k - y0) * scale))
        a[max(0, int(Y0)):int(Y1), max(0, int(X0)):int(X1)] = 0
    rgba = np.dstack([np.broadcast_to(GOLD, L.shape + (3,)), a * 255]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(f"img/fig-{key}.webp", quality=82, method=6)
    fit = f["fit"]; M = np.asarray(fit["M"]); h = .08
    ref = []
    for (x, y) in [(0, 0), (h, 0), (0, h)]:
        px, py = np.array([x, y, 1]) @ M
        ra, dec = inv_tangent(x, y, fit["ra0"], fit["dec0"])
        ref.append([round(ra, 4), round(dec, 4), round((px - x0) * scale, 1), round((py - y0) * scale, 1)])
    figs[key] = dict(ref=ref, w=c.width, h=c.height)
    print(key, c.size, ref)

# stars: [ra, dec, mag, bv-ish colour from K]  (K = effective temperature in the catalogue)
stars, index = [], {}
for s in json.load(open("/tmp/bsc5.json")):
    if not s.get("V") or float(s["V"]) > 4.6: continue
    ra, dec = t.deg(s["RA"], True), t.deg(s["Dec"])
    if s.get("C") and s.get("B"):
        key = (s["C"], s["B"].rstrip("¹²³⁴⁵⁶⁷⁸⁹"))
        if key not in index or float(s["V"]) < stars[index[key]][2]: index[key] = len(stars)
    stars.append([round(ra, 3), round(dec, 3), round(float(s["V"]), 2), int(s.get("K") or 6000)])

LINES = {  # Bayer letters, as seen from Earth
  "Ori": "λα λγ αζ γδ δε εζ ζκ δβ", "UMa": "αβ βγ γδ δα δε εζ ζη", "Leo": "αη ηγ γζ ζμ με γδ δβ βθ θα δθ",
  "Cas": "βα αγ γδ δε", "Cyg": "αγ γη ηβ δγ γε εζ", "Lyr": "αζ ζβ βγ γδ δζ", "Sco": "βδ δπ δσ σα ατ τε εμ μζ ζη ηθ θι ικ κλ",
  "Tau": "γδ δε εβ γα αζ", "Gem": "αβ ατ τε εμ βδ δζ ζγ", "CMa": "βα αδ δε δη", "Aql": "δα αγ αθ αζ", "Cru": "αγ βδ",
  "Peg": "αβ αγ αε", "Boo": "αε εδ δβ βγ γρ ρα αη",
}
NAMES = {"Ori": ["Orion", "猎户座"], "UMa": ["Ursa Major", "大熊座"], "Leo": ["Leo", "狮子座"], "Cas": ["Cassiopeia", "仙后座"],
  "Cyg": ["Cygnus", "天鹅座"], "Lyr": ["Lyra", "天琴座"], "Sco": ["Scorpius", "天蝎座"], "Tau": ["Taurus", "金牛座"], "Gem": ["Gemini", "双子座"],
  "CMa": ["Canis Major", "大犬座"], "Aql": ["Aquila", "天鹰座"], "Cru": ["Crux", "南十字座"], "Peg": ["Pegasus", "飞马座"], "Boo": ["Boötes", "牧夫座"]}
cons = {}
for c, spec in LINES.items():
    pairs = []
    for p in spec.split():
        a, b = (c, p[0]), (c, p[1])
        if a in index and b in index: pairs += [index[a], index[b]]
        else: print("missing", c, p)
    cons[c] = dict(n=NAMES[c], l=pairs)
data = "const STARS=%s;\nconst CONS=%s;\nconst FIGS=%s;" % (json.dumps(stars, separators=(",", ":")), json.dumps(cons, ensure_ascii=False, separators=(",", ":")), json.dumps(figs, separators=(",", ":")))
html = open("index.html").read()
html = re.sub(r"/\*DATA\*/.*?/\*END\*/", lambda m: "/*DATA*/" + data + "/*END*/", html, flags=re.S)
open("index.html", "w").write(html)

for n in ["copernicanum", "arateum"]:
    im = Image.open(f"src-img/{n}.jpg").convert("RGB"); im.thumbnail((1700, 1700), Image.LANCZOS); im.save(f"img/{n}.jpg", quality=80)
print("stars", len(stars))
