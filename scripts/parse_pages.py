#!/usr/bin/env python3
"""Parse fetched Devpost HTML pages into one structured JSONL + per-project text files."""
import csv, json, os, re, sys, html as H
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(BASE, "raw", "pages")
OUT_TXT = os.path.join(BASE, "raw", "about")
os.makedirs(OUT_TXT, exist_ok=True)

TAG = re.compile(r"<[^>]+>")
SCRIPT = re.compile(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", re.S)

def clean(s):
    return H.unescape(re.sub(r"\s+", " ", s)).strip()

def parse_page(slug):
    path = os.path.join(PAGES, slug + ".html")
    if not os.path.exists(path):
        return None
    try:
        h = open(path, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        return {"slug": slug, "error": str(e)}
    # browser-fetched pages carry escaped quotes from the eval round-trip
    if '\\"' in h[:5000]:
        h = h.replace('\\"', '"')
    d = {"slug": slug}
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    d["page_title"] = clean(m.group(1)) if m else ""
    m = re.search(r'property="og:description" content="([^"]*)"', h)
    d["pitch"] = clean(m.group(1)) if m else ""
    # external links
    hrefs = re.findall(r'href="(https?://[^"]+)"', h)
    ext = []
    for u in hrefs:
        if ("devpost.com" in u or "cloudfront.net/assets" in u or "browsehappy" in u
                or "devpost.team" in u or "newrelic" in u or "google-analytics" in u
                or "doubleclick" in u or "facebook.com" in u or "twitter.com" in u):
            continue
        ext.append(u)
    seen = set(); d["links"] = [u for u in ext if not (u in seen or seen.add(u))]
    d["github"] = [u for u in d["links"] if "github.com" in u]
    d["demo_links"] = [u for u in d["links"] if "github.com" not in u
                       and "d112y698adiu2z.cloudfront.net" not in u
                       and "gravatar" not in u]
    # gallery images
    d["gallery"] = list(dict.fromkeys(re.findall(
        r'https://d112y698adiu2z\.cloudfront\.net/photos/production/software_photos/[^"]+', h)))
    # video
    vids = re.findall(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|vimeo\.com)/[^"\s<]+)', h)
    d["video"] = vids[0] if vids else ""
    # about text: strip scripts, take main region between og:title occurrence and footer
    body = SCRIPT.sub("", h)
    # the software page main content: cut at last 'Comments'/'Leaderboard' footer markers
    for marker in ["Devpost Requirements", "Hackathons", "About Devpost"]:
        idx = body.rfind(marker)
        if idx > 20000:
            body = body[:idx]
            break
    txt = clean(TAG.sub(" ", body))
    # isolate from the pitch onward if present
    j = txt.find(d["pitch"][:60]) if d["pitch"] else -1
    if j > 0:
        txt = txt[j:]
    # cut footer junk after comments section
    for foot in ["Leave feedback in the comments!", "Log in or sign up for Devpost"]:
        k = txt.rfind(foot)
        if k > 500:
            txt = txt[:k]
            break
    d["text_len"] = len(txt)
    out = os.path.join(OUT_TXT, slug + ".txt")
    with open(out, "w") as f:
        f.write(txt)
    return d

if __name__ == "__main__":
    with open(os.path.join(BASE, "raw", "all_projects.csv")) as f:
        slugs = [r["slug"] for r in csv.DictReader(f)]
    results = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for d in ex.map(parse_page, slugs):
            if d:
                results.append(d)
    with open(os.path.join(BASE, "raw", "parsed.jsonl"), "w") as f:
        for d in results:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    ok = sum(1 for d in results if d.get("pitch"))
    print(f"parsed={len(results)} with_pitch={ok}")
