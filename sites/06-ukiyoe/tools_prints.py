# Posterize the public-domain prints to flat woodblock palettes.
# The Great Wave is also split into one alpha mask per ink ("block"), so the page can
# print it block by block and let blocks drift out of register.
from PIL import Image, ImageFilter
import numpy as np, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

CREAM, SUMI = (239, 228, 204), (24, 30, 48)
PALETTES = {
    "wave":    [CREAM, (205, 192, 164), (150, 143, 128), (128, 160, 186), (34, 64, 118), SUMI],
    "plum":    [CREAM, (196, 72, 56), (230, 160, 140), (96, 128, 88), (164, 180, 128), SUMI, (248, 244, 236)],
    "shower":  [CREAM, (60, 60, 64), (128, 128, 128), (200, 178, 122), (92, 124, 152), (72, 100, 80), SUMI],
    "redfuji": [CREAM, (192, 64, 48), (34, 64, 118), (128, 160, 186), (72, 110, 72), (150, 143, 128), SUMI],
}

def posterize(im, size, colors):
    im = im.convert("RGB"); im.thumbnail(size, Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(1.1))  # paper fibres would otherwise speckle between inks
    pal = Image.new("P", (1, 1)); pal.putpalette(sum(colors, ()) + (0, 0, 0) * (256 - len(colors)))
    q = im.quantize(palette=pal, dither=Image.Dither.NONE).filter(ImageFilter.ModeFilter(5))
    return q

srcs = {"wave": ("wave.jpg", (2400, 2400)), "plum": ("plum.jpg", (1100, 1600)),
        "shower": ("shower.jpg", (1100, 1600)), "redfuji": ("redfuji.jpg", (1800, 1800))}
for name, (src, size) in srcs.items():
    q = posterize(Image.open("src-img/" + src), size, PALETTES[name])
    q.convert("RGB").save(f"img/{name}.jpg", quality=86)
    if name == "wave":
        idx = np.asarray(q)
        for k in range(1, len(PALETTES[name])):  # block 0 is the paper itself
            alpha = Image.fromarray(((idx == k) * 255).astype(np.uint8))
            Image.merge("LA", (Image.new("L", alpha.size, 0), alpha)).save(f"img/block-{k}.png", optimize=True)
    print(name, q.size)
