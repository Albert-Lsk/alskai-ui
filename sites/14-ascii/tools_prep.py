# Build two same-size 16:9 colour compositions for the ASCII renderer (Saturn V launch, Earthrise).
from PIL import Image, ImageOps
W, H = 2400, 1350
l = Image.open("src-img/launch.jpg").convert("RGB")
# zoom 1.45x so the rocket (x≈46% of the photo) lands at 70% of the frame
s = H * 1.45 / l.height
l = l.resize((int(l.width * s), int(l.height * s)))
bg = Image.new("RGB", (W, H), (0, 0, 0))
x0 = int(.70 * W - .46 * l.width)
fade = Image.linear_gradient("L").rotate(90, expand=True).resize((240, l.height))  # 0→255 left→right
mask = Image.new("L", l.size, 255); mask.paste(fade, (0, 0))
bg.paste(l, (x0, -190), mask)
bg.save("img/launch.jpg", quality=86)
e = Image.open("src-img/earthrise.jpg").convert("RGB")
e = e.resize((W, W))
# earth centre ~(1368,1235) r~190 in the 2400 square: zoom 2.1x, earth at 64% x / 50% y
z = 2.1; cw, ch = W / z, H / z
e = e.crop((int(1368 - .64 * cw), int(1235 - .5 * ch), int(1368 + .36 * cw), int(1235 + .5 * ch))).resize((W, H), Image.LANCZOS)
e.save("img/earthrise.jpg", quality=86)
for n in ("launch", "earthrise"):
    Image.open(f"img/{n}.jpg").resize((960, 540)).save(f"/tmp/uisabor/ascii-{n}.jpg")
