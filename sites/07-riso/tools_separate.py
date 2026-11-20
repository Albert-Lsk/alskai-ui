# Separate each plate into two riso drums (fluorescent pink, blue).
# Like a printer's hand separation: blue drum takes the cyan component (blue ink absorbs red),
# pink takes magenta minus what blue already covers in light tones; darks get both drums.
from PIL import Image, ImageOps, ImageFilter
import numpy as np

PINK = np.array([255, 72, 176]) / 255    # Riso Fluorescent Pink
BLUE = np.array([0, 120, 191]) / 255     # Riso Blue

def separate(img, invert=False, crop=None, width=1000, white_pct=97, bias=(1, 1), gamma=.9):
    im = img.convert("RGB")
    if crop: W, H = im.size; im = im.crop((int(W*crop[0]), int(H*crop[1]), int(W*crop[2]), int(H*crop[3])))
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(.6))
    if invert: im = ImageOps.invert(im)
    a = np.asarray(im).astype(np.float32) / 255
    paper = np.percentile(a.reshape(-1, 3), white_pct, axis=0)           # normalise scan paper to white
    a = np.clip(a / paper, 0, 1)
    C, M = 1 - a[..., 0], 1 - a[..., 1]
    pink = np.clip((M - .6 * C * (1 - M)) * bias[0], 0, 1)
    blue = np.clip((C - .1) / .9 * bias[1], 0, 1)  # light warm tones stay pink-only
    return [Image.fromarray((l ** gamma * 255).astype(np.uint8)) for l in (pink, blue)]

def save(name, layers):
    for k, l in zip(("pink", "blue"), layers):
        l.save(f"img/{name}-{k}.jpg", quality=86)
    print(name, layers[0].size)

save("medusa", separate(Image.open("src-img/medusa8.jpg"), crop=(.04, .03, .96, .93), width=1000))
save("anemone", separate(Image.open("src-img/actiniae.jpg"), crop=(.04, .04, .96, .9), width=820, white_pct=99.7, gamma=1.5))
save("disc", separate(Image.open("src-img/medusa88.jpg"), invert=True, crop=(.04, .03, .96, .95), width=820, bias=(.5, 1.1)))
save("diatom", separate(Image.open("src-img/diatomea.jpg"), invert=True, crop=(.04, .03, .96, .95), width=820, bias=(1.1, .25)))

# preview: recombine with flat multiply so I can judge the separation
def preview(name):
    p = np.asarray(Image.open(f"img/{name}-pink.jpg")).astype(np.float32)[..., None] / 255
    b = np.asarray(Image.open(f"img/{name}-blue.jpg")).astype(np.float32)[..., None] / 255
    paper = np.array([243, 239, 228]) / 255
    out = paper * (1 - p * (1 - PINK)) * (1 - b * (1 - BLUE))
    return Image.fromarray((out * 255).astype(np.uint8))
ps = [preview(n) for n in ("medusa", "anemone", "disc", "diatom")]
H = 600; ps = [p.resize((int(p.width * H / p.height), H)) for p in ps]
sheet = Image.new("RGB", (sum(p.width for p in ps), H), "white"); x = 0
for p in ps: sheet.paste(p, (x, 0)); x += p.width
sheet.save("/tmp/uisabor/riso-sep.jpg")

# Seamless tiles: ink grain mask (speckled coverage) and paper tooth. Periodic blur via FFT so tiles wrap.
rng = np.random.default_rng(3)
def pblur(a, sigma):
    n = a.shape[0]; k = np.fft.fftfreq(n)
    g = np.exp(-(k[:, None] ** 2 + k[None, :] ** 2) * (2 * np.pi * sigma) ** 2 / 2)
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))
n = 256
clumps = pblur(rng.standard_normal((n, n)), 6); clumps /= clumps.std()
speck = rng.random((n, n))
alpha = np.where(speck < .07 + .05 * (clumps < -.8), 60, 255) * np.clip(.86 + .1 * clumps, .6, 1)
Image.fromarray(np.full((n, n), 0, np.uint8)).convert("LA")
la = np.stack([np.zeros((n, n)), alpha], -1).astype(np.uint8)
Image.fromarray(la, "LA").save("img/grain.png")
tooth = .5 + .07 * pblur(rng.standard_normal((n, n)), .8) / pblur(rng.standard_normal((n, n)), .8).std() + .04 * clumps / 3
Image.fromarray((np.clip(tooth, 0, 1) * 255).astype(np.uint8)).save("img/paper.png")
