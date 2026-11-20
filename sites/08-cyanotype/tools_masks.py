# Turn Atkins' cyanotype plates into plant masks: the plant blocked the sun, so it is the
# light (high red) area on the blue ground. Output white RGBA PNGs with alpha = plant.
from PIL import Image, ImageFilter
import numpy as np

PLATES = {  # name: (source, crop fractions l, t, r, b, max side)
    "granulata": ("granulata.jpg", .03, .02, .97, .86, 1400),
    "ferns":     ("ferns.jpg",     .04, .03, .96, .97, 1100),
    "dictyota":  ("dictyota.jpg",  .07, .05, .84, .78, 1000),
    "single":    ("met021.jpg",    .30, .25, .88, .66, 1100),
}

def mask_of(src, l, t, r, b, side):
    im = Image.open("src-img/" + src).convert("RGB")
    W, H = im.size
    im = im.crop((int(W * l), int(H * t), int(W * r), int(H * b)))
    s = side / max(im.size)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    red = a[..., 0]
    # flatten uneven exposure of the old print: subtract a heavily blurred ground estimate
    ground = np.asarray(Image.fromarray(red.astype(np.uint8)).filter(ImageFilter.GaussianBlur(60))).astype(np.float32)
    ground = np.minimum(ground, np.percentile(red, 60))
    m = (red - ground - 18) / (np.percentile(red, 99.7) - ground.mean() - 18)
    m = np.clip(m, 0, 1) ** .8
    # fade the outer 7% so crop lines and plate edges never show as hard straight cuts
    h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([xx / w, (w - 1 - xx) / w, yy / h, (h - 1 - yy) / h])
    m *= np.clip(d / .07, 0, 1)
    alpha = Image.fromarray((m * 255).astype(np.uint8))
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out, alpha

if __name__ == "__main__":
    for name, (src, l, t, r, b, side) in PLATES.items():
        out, alpha = mask_of(src, l, t, r, b, side)
        out.save(f"img/{name}.png", optimize=True)
        cov = (np.asarray(alpha) > 128).mean()
        assert .02 < cov < .6, (name, cov)  # a plant, not the whole sheet or nothing
        print(name, out.size, f"coverage {cov:.2f}")
