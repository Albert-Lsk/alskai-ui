# Subset Fusion Pixel 12px (zh_hans, OFL) to the characters this page uses. Re-run after editing copy.
import string, subprocess
text = open("index.html", encoding="utf-8").read() + string.printable + "0123456789·×“”：，。"
open("/tmp/onebit-chars.txt", "w", encoding="utf-8").write("".join(sorted(set(text))))
subprocess.run(["pyftsubset", "src-img/fusion/fusion-pixel-12px-proportional-zh_hans.otf.woff2",
                "--text-file=/tmp/onebit-chars.txt", "--flavor=woff2", "--output-file=fonts/fusion-pixel-12-sub.woff2",
                "--layout-features=*", "--no-hinting"], check=True)
