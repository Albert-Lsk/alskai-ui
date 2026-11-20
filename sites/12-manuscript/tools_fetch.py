# Throttled Commons download: search -> first file hit -> 2000px thumb, prints title + licence.
import json, sys, time, urllib.parse, urllib.request, subprocess
UA = {"User-Agent": "ui-remix/0.1 (open-source demo gallery)"}
want = {
    "shaw1.jpg": "Illuminated ornaments selected from manuscripts Shaw Madden plate",
    "w189.jpg": "Book of Hours, Annunciation, Walters Manuscript W.189, fol. 19v",
    "w246.jpg": "Book of Hours, Walters Manuscript W.246, fol. 22r",
    "w90.jpg": "Book of Hours, Initial D with the Annunciation, Walters Manuscript W.90",
    "kl.jpg": "Initiales KL de Janvier Très Riches Heures f2r",
    "janvier.jpg": "Les Très Riches Heures du duc de Berry Janvier-2",
}
def api(p):
    for _ in range(5):
        try:
            u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**p, "format": "json"})
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))
        except Exception as e:
            print("retry", e, flush=True); time.sleep(60)
for name, q in want.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]: continue
    d = api({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrsearch": q, "gsrlimit": 1,
             "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 2000})
    pg = list(d["query"]["pages"].values())[0]; ii = pg["imageinfo"][0]
    lic = ii["extmetadata"].get("LicenseShortName", {}).get("value")
    time.sleep(5)
    subprocess.run(["curl", "-sL", "-A", UA["User-Agent"], "-o", f"src-img/{name}", ii.get("thumburl", ii["url"])])
    print(name, "|", pg["title"][5:120], "|", lic, flush=True)
    time.sleep(6)
