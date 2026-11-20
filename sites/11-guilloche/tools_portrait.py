# Dürer's Melanchthon (NGA, CC0) -> ink-only PNG: paper becomes transparent, line work keeps its weight.
from PIL import Image, ImageOps
import numpy as np
im = ImageOps.grayscale(Image.open("src-img/melanchthon.jpg"))
W, H = im.size
im = im.crop((int(W * .04), int(H * .03), int(W * .86), int(H * .735)))  # bust, without the inscription tablet
im = im.resize((1000, int(1000 * im.height / im.width)), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
lo, hi = np.percentile(a, [3, 88])
ink = np.clip((hi - a) / (hi - lo), 0, 1) ** 0.9  # 1 = full ink, 0 = bare paper
rgba = np.zeros((*ink.shape, 4), np.uint8)
rgba[..., :3] = (27, 34, 51)  # intaglio ink, tinted later in canvas
rgba[..., 3] = (ink * 255).astype(np.uint8)
Image.fromarray(rgba).save("img/portrait.png", optimize=True)
print(im.size)
