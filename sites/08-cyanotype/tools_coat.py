# Hand-brushed emulsion mask (coat.png) and a seamless watercolour-paper tile (paper.png).
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

rng = np.random.default_rng(1843)  # the year Atkins published part one

def coat(w=1000, h=1250):
    m = w * .075
    def smooth1d(n, k):  # periodic smooth noise in [-1, 1]
        f = np.fft.fft(rng.standard_normal(n)); kk = np.fft.fftfreq(n)
        o = np.real(np.fft.ifft(f * np.exp(-(kk ** 2) * k))); return o / np.abs(o).max()
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    L = m + m * .35 * smooth1d(h, 9000)[:, None]
    R = w - m + m * .35 * smooth1d(h, 9000)[:, None]
    T = m * .8 + m * .25 * smooth1d(w, 9000)[None, :]
    B = h - m * .8 + m * .25 * smooth1d(w, 9000)[None, :]
    # brush streaks: noise stretched along the stroke direction (horizontal)
    S = periodic(1280, 1, 60, 20000)[:h, :w]
    S = (S - S.min()) / (S.max() - S.min())
    f = m * .3
    edge = lambda d: np.clip(d / f + (S - .5) * 1.6, 0, 1)
    a = edge(xx - L) * edge(R - xx) * np.clip((yy - T) / (f * .5) + (S - .5) * .6, 0, 1) * np.clip((B - yy) / (f * .5) + (S - .5) * .6, 0, 1)
    # dry brush near the edges, solid in the middle
    near = 1 - np.clip(np.minimum.reduce([xx - L, R - xx, yy - T, B - yy]) / (m * 1.2), 0, 1)
    a *= 1 - near * .55 * (S > .62)
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))).astype(np.float32) / 255
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return out, a

def periodic(n, fx, fy, k):
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky, kx = np.meshgrid(np.fft.fftfreq(n) / fy, np.fft.fftfreq(n) / fx, indexing="ij")
    o = np.real(np.fft.ifft2(f * np.exp(-(kx ** 2 + ky ** 2) * k)))
    return (o - o.mean()) / o.std()

if __name__ == "__main__":
    c, a = coat()
    c.save("img/coat.png", optimize=True)
    assert .6 < a.mean() < .92, a.mean()  # mostly coated, with a ragged border
    tile = np.clip(.5 + .05 * periodic(384, 1, 1, 400) + .04 * periodic(384, 1, 1, 30000) + .03 * rng.standard_normal((384, 384)), 0, 1)
    Image.fromarray((tile * 255).astype(np.uint8)).save("img/paper.png", optimize=True)
    print("coat", c.size, round(float(a.mean()), 2))
