#!/usr/bin/env python3
"""Extract 5 keyframes per submitted video at 10/30/50/70/90% positions.
Downloads lowest-res <=360p, extracts frames, deletes video. Resume-safe.
Frames: raw/frames/<video_id>/f1.jpg..f5.jpg ; failures logged in-frame status."""
import json, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ThreadPoolExecutor

BASE = "/mnt/work/webmcp-analysis"
FRAMES = os.path.join(BASE, "raw", "frames")
os.makedirs(FRAMES, exist_ok=True)
TMP = "/mnt/work/hermes-scratch/kf"
os.makedirs(TMP, exist_ok=True)

vids = json.load(open(os.path.join(BASE, "raw", "video_ids.json")))
byid = {}
for slug, vid in vids.items():
    byid.setdefault(vid, []).append(slug)

def already(v):
    d = os.path.join(FRAMES, v)
    return os.path.exists(os.path.join(d, "done")) or os.path.exists(os.path.join(d, "unavailable"))

def work(v):
    d = os.path.join(FRAMES, v)
    if already(v):
        return v, "cached"
    os.makedirs(d, exist_ok=True)
    url = f"https://www.youtube.com/watch?v={v}"
    mp4 = os.path.join(TMP, v + ".mp4")
    # metadata check first: skip live/premium/unavailable cheaply
    r = subprocess.run(["yt-dlp", "--skip-download", "--print", "%(duration)s", "--no-warnings",
                        url], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        open(os.path.join(d, "unavailable"), "w").write(r.stderr[-200:])
        return v, "meta_fail"
    try:
        dur = float(r.stdout.strip() or 0)
    except ValueError:
        dur = 0
    if dur < 5:
        open(os.path.join(d, "unavailable"), "w").write(f"duration={dur}")
        return v, "short_or_live"
    dl = subprocess.run(["yt-dlp", "-f", "worst[height>=240][height<=360]/worst[height<=480]/worst",
                         "-o", mp4, "--no-warnings", "--quiet", url],
                        capture_output=True, text=True, timeout=240)
    if dl.returncode != 0 or not os.path.exists(mp4):
        open(os.path.join(d, "unavailable"), "w").write(dl.stderr[-200:])
        return v, "dl_fail"
    fracs = [0.1, 0.3, 0.5, 0.7, 0.9]
    ok = 0
    for i, fr in enumerate(fracs, 1):
        at = max(1.0, dur * fr)
        out = os.path.join(d, f"f{i}.jpg")
        ff = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(at), "-i", mp4,
                             "-frames:v", "1", "-q:v", "5", out], capture_output=True, text=True, timeout=60)
        if os.path.exists(out) and os.path.getsize(out) > 3000:
            ok += 1
        elif os.path.exists(out):
            os.remove(out)
    if os.path.exists(mp4):
        os.remove(mp4)
    if ok >= 3:
        open(os.path.join(d, "done"), "w").write(str(ok))
        return v, f"ok{ok}"
    open(os.path.join(d, "unavailable"), "w").write(f"only {ok} frames")
    return v, "frames_fail"

todo = [v for v in byid if not already(v)]
print(f"todo={len(todo)}", flush=True)
stats = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(work, v): v for v in todo}
    for i, fu in enumerate(as_completed(futs), 1):
        v, st = fu.result()
        stats[st.split()[0] if st.startswith('ok') else st] = stats.get(st if not st.startswith('ok') else 'ok', 0) + 1
        if i % 100 == 0:
            print(f"{i}/{len(todo)} {stats}", flush=True)
print("DONE", stats, flush=True)
