#!/usr/bin/env python3
"""Collect YouTube metadata + transcripts for all unique video IDs. Resume-safe."""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/mnt/work/webmcp-analysis"
OUT = os.path.join(BASE, "raw", "video_meta.jsonl")
vids = json.load(open(os.path.join(BASE, "raw", "video_ids.json")))
byid = {}
for slug, vid in vids.items():
    byid.setdefault(vid, []).append(slug)

done = set()
if os.path.exists(OUT):
    for line in open(OUT):
        try:
            done.add(json.loads(line)["video_id"])
        except Exception:
            pass

todo = [v for v in byid if v not in done]
print(f"total={len(byid)} done={len(done)} todo={len(todo)}", flush=True)

def ytdlp_meta(vid):
    try:
        r = subprocess.run(
            ["yt-dlp", "--skip-download", "--print", "%(title)s\t%(duration)s\t%(view_count)s\t%(channel)s",
             f"https://www.youtube.com/watch?v={vid}"],
            capture_output=True, text=True, timeout=45)
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split("\t")
            return {"title": parts[0] if parts else "", "duration": parts[1] if len(parts) > 1 else "",
                    "views": parts[2] if len(parts) > 2 else "", "channel": parts[3] if len(parts) > 3 else ""}
    except Exception:
        pass
    return {}

def transcript(vid):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        t = YouTubeTranscriptApi().fetch(vid)
        txt = " ".join(s.text for s in t.snippets)
        return {"transcript": txt[:12000], "transcript_secs": len(t.snippets) > 0}
    except Exception as e:
        return {"transcript": "", "transcript_error": type(e).__name__}

def work(vid):
    rec = {"video_id": vid, "slugs": byid[vid]}
    rec.update(ytdlp_meta(vid))
    rec.update(transcript(vid))
    return vid, rec

out = open(OUT, "a")
ok = bad = 0
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(work, v): v for v in todo}
    for i, fu in enumerate(as_completed(futs), 1):
        vid, rec = fu.result()
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if rec.get("title"):
            ok += 1
        else:
            bad += 1
        if i % 100 == 0:
            out.flush()
            print(f"{i}/{len(todo)} ok={ok} bad={bad}", flush=True)
out.close()
print(f"DONE ok={ok} bad={bad}", flush=True)
