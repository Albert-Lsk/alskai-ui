# Fit plate-pixel <- sky affine from 3 anchor stars, overlay catalogue stars on the plate to check.
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw

CAT = json.load(open("/tmp/bsc5.json"))
def deg(s, ra=False):
    s = s.replace("h", " ").replace("m", " ").replace("s", "").replace("°", " ").replace("′", " ").replace("″", "")
    p = s.split(); sign = -1 if p[0].startswith("-") else 1
    v = abs(float(p[0])) + float(p[1]) / 60 + float(p[2]) / 3600
    return v * 15 if ra else sign * v
STARS = [dict(ra=deg(x["RA"], True), dec=deg(x["Dec"]), v=float(x["V"]), c=x.get("C"), b=x.get("B"), n=x.get("N"))
         for x in CAT if x.get("V") and float(x["V"]) <= 5.0]

def find(c, b):
    m = [s for s in STARS if s["c"] == c and s["b"] and s["b"].rstrip("¹²³⁴⁵⁶⁷⁸⁹") == b]
    return min(m, key=lambda s: s["v"])

def tangent(s, ra0, dec0):  # gnomonic, east = +x (left on the sky as seen), north = +y
    ra, dec, ra0r, dec0r = map(math.radians, (s["ra"], s["dec"], ra0, dec0))
    c = math.sin(dec0r) * math.sin(dec) + math.cos(dec0r) * math.cos(dec) * math.cos(ra - ra0r)
    x = math.cos(dec) * math.sin(ra - ra0r) / c
    y = (math.cos(dec0r) * math.sin(dec) - math.sin(dec0r) * math.cos(dec) * math.cos(ra - ra0r)) / c
    return x, y

def fit(name, src, preview_w, anchors):
    im = Image.open(f"src-img/{src}").convert("RGB"); k = im.width / preview_w
    ss = [find(*a[0]) for a in anchors]
    ra0 = np.mean([s["ra"] for s in ss]); dec0 = np.mean([s["dec"] for s in ss])
    A = np.array([[*tangent(s, ra0, dec0), 1] for s in ss]); P = np.array([[a[1] * k, a[2] * k] for a in anchors])
    M = np.linalg.solve(A, P)  # 3x2: [x y 1] @ M = pixel
    d = ImageDraw.Draw(im)
    for s in STARS:
        x, y = tangent(s, ra0, dec0)
        if abs(x) > .8 or abs(y) > .8: continue
        px, py = np.array([x, y, 1]) @ M
        if 0 <= px < im.width and 0 <= py < im.height:
            r = max(4, (6 - s["v"]) * 5); d.ellipse([px - r, py - r, px + r, py + r], outline=(0, 200, 255), width=4)
    im.resize((1000, int(1000 * im.height / im.width))).save(f"/tmp/uisabor/fit-{name}.jpg", quality=85)
    return dict(ra0=ra0, dec0=dec0, M=M.round(2).tolist())

if __name__ == "__main__":
    print(fit("orion", "orion.jpg", 1000, [(("Ori", "α"), 637, 316), (("Ori", "β"), 468, 563), (("Ori", "γ"), 520, 328)]))

from scipy import ndimage
def marks(im):  # centroids of the hand-coloured yellow/orange star symbols
    a = np.asarray(im).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = (R > 160) & (G > 115) & (R - B > 115) & (G - B > 75)
    lab, n = ndimage.label(ndimage.binary_opening(m, iterations=1))
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    c = ndimage.center_of_mass(m, lab, range(1, n + 1))
    return np.array([(x, y) for (y, x), s in zip(c, sizes) if 25 < s < 900])

def icp(name, src, preview_w, anchors, iters=8, radius=0.025, show=True):
    im = Image.open(f"src-img/{src}").convert("RGB"); k = im.width / preview_w
    mk = marks(im)
    ss = [find(*a[0]) for a in anchors]
    ra0 = np.mean([s["ra"] for s in ss]); dec0 = np.mean([s["dec"] for s in ss])
    A = np.array([[*tangent(s, ra0, dec0), 1] for s in ss]); P = np.array([[a[1] * k, a[2] * k] for a in anchors])
    M = np.linalg.lstsq(A, P, rcond=None)[0]
    pool = [s for s in STARS if s["v"] <= 4.6]
    T = np.array([[*tangent(s, ra0, dec0), 1] for s in pool])
    keep = (np.abs(T[:, 0]) < .7) & (np.abs(T[:, 1]) < .7); T = T[keep]
    for it in range(iters):
        pred = T @ M
        d = np.hypot(*(pred[:, None, :] - mk[None, :, :]).transpose(2, 0, 1))
        j = d.argmin(1); ok = d[np.arange(len(T)), j] < radius * im.width
        inside = (pred[:, 0] > 0) & (pred[:, 0] < im.width) & (pred[:, 1] > 0) & (pred[:, 1] < im.height)
        ok &= inside
        M = np.linalg.lstsq(T[ok], mk[j[ok]], rcond=None)[0]
        res = np.median(d[np.arange(len(T)), j][ok])
    print(name, "matched", ok.sum(), "of", inside.sum(), "median px err", round(float(res), 1), "marks", len(mk))
    if show:
        d = ImageDraw.Draw(im)
        for px, py in mk: d.ellipse([px - 8, py - 8, px + 8, py + 8], outline=(255, 0, 255), width=3)
        for px, py in T @ M:
            d.ellipse([px - 14, py - 14, px + 14, py + 14], outline=(0, 200, 255), width=4)
        im.resize((1000, int(1000 * im.height / im.width))).save(f"/tmp/uisabor/fit-{name}.jpg", quality=85)
    return dict(ra0=float(ra0), dec0=float(dec0), M=M.tolist(), size=im.size)
