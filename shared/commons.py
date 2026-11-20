# Search Wikimedia Commons files, print title | license | artist | size | url
import json, sys, urllib.parse, urllib.request
UA = {"User-Agent": "ui-remix/0.1 (local demo)"}
def get(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
for q in sys.argv[1:]:
    print("==", q)
    d = get({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrsearch": q, "gsrlimit": 6,
             "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 2400})
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "?")
        art = m.get("Artist", {}).get("value", "?")
        import re; art = re.sub("<[^>]+>", "", art)[:40]
        print(f'{p["title"][5:80]} | {lic} | {art} | {ii["width"]}x{ii["height"]} | {ii.get("thumburl", ii["url"])}')
