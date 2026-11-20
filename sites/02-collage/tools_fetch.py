# Download Commons files by exact title (throttled; other agents share the rate limit).
import json, sys, time, urllib.parse, urllib.request, subprocess
UA = {"User-Agent": "ui-remix/0.1 (open-source demo gallery)"}
def info(title):
    q = urllib.parse.urlencode({"action": "query", "titles": "File:" + title, "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "iiurlwidth": 3000, "format": "json"})
    for _ in range(5):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers=UA), timeout=30))
            ii = list(d["query"]["pages"].values())[0]["imageinfo"][0]
            return ii.get("thumburl", ii["url"]), ii["extmetadata"].get("LicenseShortName", {}).get("value")
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(60)
for pair in sys.argv[1:]:
    out, title = pair.split("=", 1)
    url, lic = info(title); time.sleep(5)
    subprocess.run(["curl", "-sL", "-A", UA["User-Agent"], "-o", "src-img/" + out, url], check=True)
    print(out, "|", title, "|", lic, flush=True); time.sleep(5)
