# Web-sized crops for the collage: sky, a keyed foreground cloud layer, painting fragments.
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

def save(im, name, w, q=82):
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    if im.mode == "RGBA": im.save(f"img/{name}.webp", quality=q)
    else: im.convert("RGB").save(f"img/{name}.jpg", quality=q, optimize=True)

# sky: landscape crop of the vivid portrait sky
c2 = Image.open("src-img/clouds2.jpg").convert("RGB"); W, H = c2.size
sky = c2.crop((0, 0, W, int(W * .62)))
save(ImageEnhance.Color(sky).enhance(1.12), "sky", 2400)

# foreground clouds: key white puffs out of the blue (alpha from whiteness, blue sky -> transparent)
fg = c2.crop((0, int(H * .62), W, H))
a = np.asarray(fg).astype(np.float32)
white = a.min(axis=2); blue = a[..., 2] - a[..., 0]
alpha = np.clip((white - 150) / 70, 0, 1) * np.clip(1 - (blue - 30) / 60, 0, 1)
rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
save(Image.fromarray(rgba, "RGBA"), "clouds-fg", 2000, 70)

# Vermeer: the hero painting (face + earring) and two citation details
v = Image.open("src-img/vermeer.jpg").convert("RGB"); W, H = v.size
save(v.crop((0, int(H * .10), W, int(H * .10) + int(W * .66))), "vermeer", 2200)
save(v.crop((int(W * .55), int(H * .47), int(W * .72), int(H * .61))), "pearl", 700)
save(v.crop((int(W * .32), int(H * .10), int(W * .90), int(H * .42))), "turban", 800)

# Michelangelo: the two hands
ad = Image.open("src-img/adam.jpg").convert("RGB"); W, H = ad.size
save(ad.crop((int(W * .17), int(H * .22), int(W * .56), int(H * .70))), "hands", 1600)

# Canova terracotta model: heads and wings
ps = Image.open("src-img/psyche1.jpg").convert("RGB"); W, H = ps.size
save(ps.crop((int(W * .30), int(H * .02), int(W * .80), int(H * .55))), "psyche", 1200)
