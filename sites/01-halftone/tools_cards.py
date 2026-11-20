# Crop card backgrounds (4:5, grayscale) from the public-domain sources.
from PIL import Image, ImageOps
crops = {  # name: (source, left, top, right, bottom) as fractions
    "c-legion":   ("legion.jpg",   .30, .10, .80, .72),
    "c-colosseo": ("colosseo.jpg", .22, .05, .68, .78),
    "c-arco":     ("arco.jpg",     .12, .00, .52, .98),
    "c-gerome":   ("gerome.jpg",   .55, .00, .95, .80),
    "c-cole":     ("cole.jpg",     .00, .05, .34, .70),
    "c-gladiators": ("gerome.jpg", .22, .30, .62, 1.0),
}
for name, (src, l, t, r, b) in crops.items():
    im = Image.open("src-img/" + src).convert("L")
    W, H = im.size
    im = im.crop((int(W*l), int(H*t), int(W*r), int(H*b)))
    im = ImageOps.fit(im, (800, 1000), centering=(.5, .5))
    ImageOps.autocontrast(im, cutoff=1).save(f"img/{name}.jpg", quality=85)
    print(name)
