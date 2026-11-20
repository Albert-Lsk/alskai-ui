# Throttled Commons search/download for site 20. Usage:
#   python3 tools_fetch.py search "query" ...      -> list video files with licence + derivatives
#   python3 tools_fetch.py get <url> <outfile>
import json, sys, time, urllib.parse, urllib.request, re
UA = {"User-Agent": "alskai-ui/0.1 (open-source demo gallery; github Albert-Lsk)"}
def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})
    for _ in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))
        except urllib.error.HTTPError as e:
            if e.code == 429: print("429, waiting 60s", file=sys.stderr); time.sleep(60); continue
            raise
if sys.argv[1] == "search":
    for q in sys.argv[2:]:
        print("==", q)
        d = api({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrsearch": q + " filetype:video", "gsrlimit": 8,
                 "prop": "videoinfo", "viprop": "url|size|extmetadata|derivatives"})
        for p in (d.get("query", {}).get("pages", {}) or {}).values():
            vi = p["videoinfo"][0]; m = vi.get("extmetadata", {})
            lic = m.get("LicenseShortName", {}).get("value", "?")
            dur = m.get("Duration", {}).get("value") if "Duration" in m else None
            ders = [x for x in vi.get("derivatives", []) if x.get("height", 0) and x["height"] <= 480]
            der = sorted(ders, key=lambda x: x["height"])[-1:] if ders else []
            print(f'{p["title"][5:90]} | {lic} | {vi["width"]}x{vi["height"]} | {vi["size"]//1048576}MB | {der[0]["src"] if der else vi["url"]}')
        time.sleep(6)
else:
    _, _, url, out = sys.argv
    urllib.request.urlretrieve(url, out) if False else open(out, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read())
    print("saved", out)
