#!/usr/bin/env python3
"""Keyframes v2: per video, resolve storyboard via yt-dlp (Zen cookies, web_safari),
download signed sprite fragments, stitch each 3x3 sprite into a contact sheet.
Output: raw/frames/<vid>/sheet.jpg + meta.json. Resume-safe via sheet.jpg presence."""
import json, os, subprocess, sys, io
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

BASE = "/mnt/work/webmcp-analysis"
FRAMES = os.path.join(BASE, "raw", "frames")
TMP = "/mnt/work/hermes-scratch/kf2"
os.makedirs(FRAMES, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
COOKIES = "firefox:/home/nicholai/.zen/p0l8lluq.Default (release)"
EA = "youtube:player_client=web_safari"
WORKERS = 6

vids = json.load(open(os.path.join(BASE, "raw", "video_ids.json")))
byid = {}
for slug, vid in vids.items():
    byid.setdefault(vid, []).append(slug)

def resolve(vid):
    """Return (duration, [sprite_urls]) or raise."""
    out = os.path.join(TMP, vid + ".json")
    r = subprocess.run(["yt-dlp", "--cookies-from-browser", COOKIES,
                        "--extractor-args", EA, "-J", "-f", "sb0", "--skip-download",
                        "--no-warnings", f"https://www.youtube.com/watch?v={vid}"],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[-1][:160] if r.stderr else "rc!=0")
    d = json.loads(r.stdout)
    dur = d.get("duration") or 0
    urls = []
    for f in d.get("formats", []):
        if str(f.get("format_id", "")) == "sb0":
            urls = [fr["url"] for fr in f.get("fragments", [])]
            break
    if not urls:
        raise RuntimeError("no storyboard")
    return dur, urls

def fetch(url, tries=2):
    import urllib.request
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=25).read()
        except Exception:
            if a == tries - 1:
                raise
    return b""

def work(vid):
    d = os.path.join(FRAMES, vid)
    if os.path.exists(os.path.join(d, "sheet.jpg")):
        return vid, "cached"
    if os.path.exists(os.path.join(d, "unavailable")):
        return vid, "cached_unavailable"
    os.makedirs(d, exist_ok=True)
    try:
        dur, urls = resolve(vid)
        frames = []
        cols, rows, w, h = 3, 3, 320, 180
        for u in urls:
            data = fetch(u)
            im = Image.open(io.BytesIO(data))
            for i in range(cols * rows):
                x, y = (i % cols) * w, (i // cols) * h
                if x + w <= im.size[0] and y + h <= im.size[1]:
                    frames.append(im.crop((x, y, x + w, y + h)))
        if len(frames) < 4:
            raise RuntimeError(f"only {len(frames)} frames")
        # stitch all frames into grid sheets, max 3 sheets x 45 frames = 135 thumbnails
        sheets = []
        per = cols * rows * 5  # 5x3 grid of 320x180 per sheet = 960x2700, too tall; use 3x5 -> 960x900
        per = 15
        for si in range(0, min(len(frames), 45), per):
            chunk = frames[si:si + per]
            cw, ch = 3 * w, 5 * h
            sheet = Image.new("RGB", (cw, ch))
            for i, fr in enumerate(chunk):
                sheet.paste(fr, ((i % 3) * w, (i // 3) * h))
            p = os.path.join(d, f"sheet{len(sheets)}.jpg")
            sheet.save(p, quality=78)
            sheets.append(p)
        # single combined sheet if <=15 frames total
        if len(sheets) > 1:
            pass  # keep multiple sheets; reviewers get all
        meta = {"video_id": vid, "duration": dur, "sprite_count": len(urls),
                "frame_count": len(frames), "sheets": [os.path.basename(p) for p in sheets],
                "slugs": byid[vid]}
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"))
        return vid, f"ok{len(frames)}"
    except Exception as e:
        open(os.path.join(d, "unavailable"), "w").write(str(e)[:200])
        return vid, f"FAIL {str(e)[:60]}"

todo = [v for v in byid if not (os.path.exists(os.path.join(FRAMES, v, "sheet.jpg"))
                                or os.path.exists(os.path.join(FRAMES, v, "unavailable")))]
print(f"todo={len(todo)}", flush=True)
stats = {}
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(work, v): v for v in todo}
    for i, fu in enumerate(as_completed(futs), 1):
        vid, st = fu.result()
        key = st.split()[0] if st.startswith("ok") else st
        stats[key] = stats.get(key, 0) + 1
        if i % 50 == 0:
            print(f"{i}/{len(todo)} {stats}", flush=True)
print("DONE", stats, flush=True)
