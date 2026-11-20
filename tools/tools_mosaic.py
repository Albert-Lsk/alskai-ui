# Build the 20-site mosaic (5 x 4) from docs/shots/<site>-<lang>.png.
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
lang = sys.argv[1] if len(sys.argv) > 1 else "zh"
shots = sorted(glob.glob(f"docs/shots/*-{lang}.png"))
assert len(shots) == 20, len(shots)
W, H, G, M = 576, 360, 16, 40          # tile size (16:10), gutter, margin
cols, rows = 5, 4
out = Image.new("RGB", (M * 2 + cols * W + (cols - 1) * G, M * 2 + rows * H + (rows - 1) * G), "#15140f")
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
for i, p in enumerate(shots):
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    x, y = M + (i % cols) * (W + G), M + (i // cols) * (H + G)
    out.paste(im, (x, y))
    d = ImageDraw.Draw(out)
    tag = os.path.basename(p).split("-")[0]
    d.rectangle((x, y, x + 46, y + 30), fill="#15140f")
    d.text((x + 9, y + 3), tag, fill="#f1ebdd", font=font)
out.save(f"docs/mosaic-{lang}.jpg", quality=88)
print(out.size)
