# Crop the Leonardo sheets, normalise paper to white, tint the ink one shared sepia,
# so every sheet can be multiplied onto the page's toned paper.
from PIL import Image, ImageOps
import numpy as np

INK = np.array([74, 42, 20], np.float32)  # sepia / iron-gall brown

def sepia(im, lo, hi, gamma=1.0):
    a = np.asarray(ImageOps.grayscale(im)).astype(np.float32)
    p0, p1 = np.percentile(a, [lo, hi])
    t = np.clip((a - p0) / (p1 - p0), 0, 1) ** gamma          # 0 = ink, 1 = paper
    rgb = INK[None, None] * (1 - t[..., None]) + 255 * t[..., None]
    return Image.fromarray(rgb.astype(np.uint8))

jobs = {  # name: (source, crop fractions l,t,r,b, percentiles, gamma, output width)
    "vitruvian": ("vitruvian.jpg", (.03, .0, .97, .80), (1, 72), 1.6, 1400),
    "hands":     ("hands.jpg",     (.075, .05, .955, .945), (1, 93), 1.35, 1200),
    "cranium":   ("cranium.jpg",   (.09, .07, .905, .93), (1, 90), 1.3, 1200),
}
for name, (src, (l, t, r, b), (lo, hi), g, w) in jobs.items():
    im = Image.open("src-img/" + src)
    W, H = im.size
    im = sepia(im.crop((int(W * l), int(H * t), int(W * r), int(H * b))), lo, hi, g)
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(f"img/{name}.jpg", quality=84)
    print(name, im.size)

# Seamless toned-paper tile: periodic FFT noise (no seams) for fibres + soft foxing.
rng = np.random.default_rng(13)
def periodic(n, sx, sy, k):
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky, kx = np.meshgrid(np.fft.fftfreq(n) / sy, np.fft.fftfreq(n) / sx, indexing="ij")
    o = np.real(np.fft.ifft2(f * np.exp(-(kx ** 2 + ky ** 2) * k)))
    return (o - o.mean()) / o.std()
t = .5 + .045 * periodic(512, 1, 1, 4000) + .03 * periodic(512, 1, 6, 900) + .03 * rng.standard_normal((512, 512))
Image.fromarray((np.clip(t, 0, 1) * 255).astype(np.uint8)).save("img/paper.png")
