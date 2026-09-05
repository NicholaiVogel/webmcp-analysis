#!/usr/bin/env python3
"""Bulk-fetch Devpost software pages as static HTML. Resume-safe."""
import csv, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(BASE, "raw", "pages")
os.makedirs(PAGES, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
      "Accept": "text/html,application/xhtml+xml"}

def slugs():
    with open(os.path.join(BASE, "raw", "all_projects.csv")) as f:
        return [r["slug"] for r in csv.DictReader(f)]

def done_ok(p):
    return os.path.exists(p) and os.path.getsize(p) > 10000

def fetch(slug):
    out = os.path.join(PAGES, slug + ".html")
    if done_ok(out):
        return slug, "cached", os.path.getsize(out)
    url = f"https://devpost.com/software/{slug}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 10000:
                return slug, f"short({len(data)})", len(data)
            with open(out, "wb") as f:
                f.write(data)
            return slug, "ok", len(data)
        except Exception as e:
            if attempt == 2:
                return slug, f"ERR {type(e).__name__}: {e}", 0
            time.sleep(1.5 * (attempt + 1))

if __name__ == "__main__":
    sl = slugs()
    todo = [s for s in sl if not done_ok(os.path.join(PAGES, s + ".html"))]
    print(f"total={len(sl)} todo={len(todo)}", flush=True)
    ok = bad = 0
    errors = []
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = {ex.submit(fetch, s): s for s in todo}
        for i, fu in enumerate(as_completed(futs), 1):
            slug, status, size = fu.result()
            if status.startswith("ERR") or status.startswith("short"):
                bad += 1
                errors.append((slug, status))
            else:
                ok += 1
            if i % 100 == 0:
                print(f"{i}/{len(todo)} ok={ok} bad={bad}", flush=True)
    print(f"DONE ok={ok} bad={bad}", flush=True)
    with open(os.path.join(BASE, "raw", "fetch_errors.txt"), "w") as f:
        for slug, status in errors:
            f.write(f"{slug}\t{status}\n")
