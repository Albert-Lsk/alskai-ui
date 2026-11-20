# Web-size the manuscript crops and build a seamless vellum tile (FFT noise is periodic).
from PIL import Image, ImageOps
import numpy as np

def out(src, name, box=None, w=None, h=None):
    im = Image.open(f"src-img/{src}").convert("RGB")
    if box:
        W, H = im.size
        im = im.crop((int(W * box[0]), int(H * box[1]), int(W * box[2]), int(H * box[3])))
    if w: im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    if h: im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    im.save(f"img/{name}", quality=84)
    print(name, im.size)

out("janvier.jpg", "janvier.jpg", h=1300)
out("kl.jpg", "kl.jpg", w=900)
out("w246.jpg", "w246.jpg", w=900)
out("w90.jpg", "w90.jpg", w=850)

rng = np.random.default_rng(3)
def noise(n, scale):
    f = np.fft.fft2(rng.standard_normal((n, n)))
    k = np.hypot(*np.meshgrid(np.fft.fftfreq(n), np.fft.fftfreq(n)))
    o = np.real(np.fft.ifft2(f * np.exp(-(k * scale) ** 2)))
    return (o - o.mean()) / o.std()
n = 512
v = .5 + .035 * noise(n, 18) + .02 * noise(n, 60) + .025 * rng.standard_normal((n, n))
Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)).save("img/vellum.png")
