# Grayscale, web-sized sources; the page dithers them live in canvas.
from PIL import Image, ImageOps
crops = {  # name: (source, left, top, right, bottom fractions, max side)
    "tetons": ("tetons.jpg", 0, 0, 1, 1, 1400),
    "aldrin": ("aldrin.jpg", .12, .02, .88, .90, 1100),
    "canyon": ("canyon.jpg", 0, 0, 1, 1, 1100),
    "eiffel": ("eiffel.jpg", .08, .04, .92, .80, 1000),
}
for name, (src, l, t, r, b, mx) in crops.items():
    im = ImageOps.grayscale(Image.open("src-img/" + src))
    W, H = im.size
    im = im.crop((int(W * l), int(H * t), int(W * r), int(H * b)))
    im.thumbnail((mx, mx))
    ImageOps.autocontrast(im, cutoff=.5).save(f"img/{name}.jpg", quality=86)
    print(name, im.size)
