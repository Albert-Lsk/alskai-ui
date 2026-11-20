# Cut the marble Augustus out of its dark niche by luminance, composite onto Cole's painting.
from PIL import Image, ImageFilter, ImageOps, ImageChops
import numpy as np
a = Image.open("src-img/augustus.jpg").convert("L")
W, H = a.size
a = a.crop((int(W*.17), int(H*.08), int(W*.80), int(H*.70)))
a = a.crop((30*4, 35*4, 400*4, a.height))  # inside the niche only
arr = np.asarray(a).astype(np.float32)
m = (arr > 95).astype(np.uint8) * 255
mask = Image.fromarray(m).filter(ImageFilter.MedianFilter(7))
# keep only the largest connected blob touching the statue centre via flood fill
mask = mask.point(lambda v: 255 if v > 127 else 0)
seed = (int(mask.width * .60), int(mask.height * .40))  # breastplate
filled = mask.copy(); ImageOps  # noqa
from PIL import ImageDraw
ImageDraw.floodfill(filled, seed, 128)
mask = filled.point(lambda v: 255 if v == 128 else 0)
# fill dark crevices: everything not reachable from the corner is statue
inv = mask.copy(); ImageDraw.floodfill(inv, (0, 0), 64)
mask = inv.point(lambda v: 0 if v == 64 else 255).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))
mask.save("/tmp/uisabor/mask.png")
bg = Image.open("src-img/cole.jpg").convert("L")
bg = bg.resize((2400, int(bg.height * 2400 / bg.width)))
bg = bg.crop((0, bg.height - 1350, 2400, bg.height))  # lower 1350px: crowds, water, columns
bg = ImageOps.autocontrast(bg, cutoff=1)
s = 1350 * 1.05 / a.height
st = a.resize((int(a.width*s), int(a.height*s))); sm = mask.resize(st.size)
st = ImageOps.autocontrast(st, cutoff=1)
# fade the statue's lower edge
fade = Image.linear_gradient("L").resize(st.size).point(lambda v: 255 if v < 170 else int(255 * (255 - v) / 85))
sm = ImageChops.multiply(sm, fade)
# dim background, extra dark on the top-left headline area and as a halo behind the statue
bga = np.asarray(bg).astype(np.float32) * 0.72
yy, xx = np.mgrid[0:bg.height, 0:bg.width] / np.array([bg.height, bg.width])[:, None, None]
bga *= 1 - 0.45 * np.clip(1 - np.hypot(xx / .55, yy / .75), 0, 1)
pos = (2400 - st.width - 60, 1350 - st.height + 120)
halo = Image.new("L", bg.size, 0); halo.paste(sm, pos); halo = halo.filter(ImageFilter.GaussianBlur(60))
bga *= 1 - 0.55 * np.asarray(halo) / 255
bg = Image.fromarray(bga.clip(0, 255).astype(np.uint8))
bg.paste(st, pos, sm)
bg.save("hero-src.jpg", quality=88)
print(bg.size)
