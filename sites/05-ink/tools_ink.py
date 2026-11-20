# Normalise paper to white so the art can be multiplied onto the page's xuan-paper colour.
from PIL import Image, ImageOps
import numpy as np

def paperwhite(im, lo=1, hi=92, gamma=1.0):
    a = np.asarray(ImageOps.grayscale(im)).astype(np.float32)
    p0, p1 = np.percentile(a, [lo, hi])
    a = np.clip((a - p0) / (p1 - p0), 0, 1) ** gamma
    return Image.fromarray((a * 255).astype(np.uint8))

# handscroll: three consecutive landscape segments, mounting and colour chart cropped off
segs = []
for n in ["08", "09", "10"]:
    im = Image.open(f"src-img/songnian-{n}.jpg")
    W, H = im.size
    im = im.crop((0, int(H * .062), W, int(H * .868)))
    segs.append(paperwhite(im, 0.5, 80, 1.15).resize((int(W * 1100 / im.height), 1100)))
OV = 40  # crossfade the photographic seams between segments
scroll = Image.new("L", (sum(s.width for s in segs) - OV * (len(segs) - 1), 1100), 255)
ramp = Image.linear_gradient("L").rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT).resize((OV, 1100))
x = 0
for k, s in enumerate(segs):
    if k:
        m = Image.new("L", s.size, 255); m.paste(ramp, (0, 0)); scroll.paste(s, (x, 0), m)
    else:
        scroll.paste(s, (x, 0))
    x += s.width - OV
scroll.save("img/scroll.jpg", quality=82)

# calligraphy leaf
im = Image.open("src-img/songnian-06.jpg"); W, H = im.size
paperwhite(im.crop((int(W * .02), int(H * .062), int(W * .98), int(H * .868))), 0.5, 75, 1.2).resize((1600, 1600 * 0 + int(1600 * (H * .806) / (W * .96)))).save("img/calligraphy.jpg", quality=82)

# Fan Kuan: dark silk lifted towards paper; keep the monumental peak and the travellers below
im = Image.open("src-img/fankuan.jpg"); W, H = im.size
fk = paperwhite(im.crop((int(W * .04), int(H * .03), int(W * .96), int(H * .86))), 2, 80, .62)
fk.resize((1300, int(1300 * fk.height / fk.width))).save("img/fankuan.jpg", quality=84)
print(scroll.size)

# Seamless xuan-paper texture: FFT noise is periodic, so the tile has no seams.
rng = np.random.default_rng(7)
def periodic_noise(n, fx, fy):
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky, kx = np.meshgrid(np.fft.fftfreq(n) / fy, np.fft.fftfreq(n) / fx, indexing="ij")
    out = np.real(np.fft.ifft2(f * np.exp(-(kx ** 2 + ky ** 2) * 900)))
    return (out - out.mean()) / out.std()
fibres = periodic_noise(512, 1.0, 9.0)       # long horizontal fibres
grain = rng.standard_normal((512, 512))
a = np.clip(.5 + .06 * fibres + .035 * grain, 0, 1)
Image.fromarray((a * 255).astype(np.uint8)).save("img/paper.png")
