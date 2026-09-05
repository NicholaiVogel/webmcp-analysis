#!/usr/bin/env python3
"""Rebuild reviewer packets for a list of slugs with corrected video metadata + sheets,
plus an audio-neutrality directive for music-audio re-reviews.

Writes: analysis/rerun/packets/<slug>.json   (one packet per file, resumable)
        analysis/rerun/manifest.json         (build info)
"""
import csv, glob, json, os, sys

BASE = "/mnt/work/webmcp-analysis"
CRIT_SHEETS = "raw/frames"

def sha16(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

# ---------- inputs ----------
rows = list(csv.DictReader(open(f"{BASE}/raw/all_projects.csv")))
by_slug = {r["slug"]: r for r in rows}

parsed = {}
for line in open(f"{BASE}/raw/parsed.jsonl"):
    d = json.loads(line)
    parsed[d["slug"]] = d

# About text lives in raw/about/<slug>.txt (same source as reviewer_corpus build)
def about_for(slug):
    p = f"{BASE}/raw/about/{slug}.txt"
    if os.path.exists(p):
        return open(p, encoding="utf-8", errors="replace").read()
    return ""

vids_fixed = json.load(open(f"{BASE}/raw/videos_fixed.json")) if os.path.exists(f"{BASE}/raw/videos_fixed.json") else {}
video_ids = json.load(open(f"{BASE}/raw/video_ids.json"))

music_slugs = set(json.load(open(f"{BASE}/analysis/recheck_music_audio.json"))) if os.path.exists(f"{BASE}/analysis/recheck_music_audio.json") else set()

os.makedirs(f"{BASE}/analysis/rerun/packets", exist_ok=True)

def sheets_for(vid):
    mpath = f"{BASE}/{CRIT_SHEETS}/{vid}/meta.json"
    if not os.path.exists(mpath):
        return [], 0
    m = json.load(open(mpath))
    sheets = [f"raw/frames/{vid}/{s}" for s in m.get("sheets", [])]
    return sheets, m.get("frame_count", 0)

def dur_for(vid):
    for line in open(f"{BASE}/raw/video_meta.jsonl"):
        d = json.loads(line)
        if d.get("video_id") == vid:
            return d.get("duration") or 0
    return 0

built = {}
skipped = []
for slug in sys.argv[1:]:
    if slug not in by_slug:
        skipped.append((slug, "not in manifest"))
        continue
    row = by_slug[slug]
    pg = parsed.get(slug, {})
    vid = vids_fixed.get(slug) or video_ids.get(slug) or ""
    sheets, nframes = sheets_for(vid) if vid else ([], 0)
    dur = dur_for(vid) if vid else 0
    packet = {
        "slug": slug,
        "title": row.get("title") or slug,
        "devpost_url": row.get("url") or row.get("devpost_url") or "",
        "pitch": (pg.get("pitch") or row.get("pitch") or "")[:1200],
        "about_excerpt": about_for(slug)[:8000],
        "has_public_repo": bool(pg.get("github_links")),
        "github_links": pg.get("github_links") or [],
        "has_demo_link": bool(pg.get("demo_links")),
        "demo_links": pg.get("demo_links") or [],
        "demo_alive": pg.get("demo_alive"),
        "gallery_image_count": len(pg.get("gallery", []) or []),
        "has_video": bool(vid) and bool(sheets),
        "video_id": vid,
        # Duration is only known for the 261 videos that survived the YouTube metadata
        # wall. Rather than imply absence, packets treat duration as optional evidence.
        "video_duration_secs": dur if dur else None,
        "video_title": pg.get("video_title") or "",
        "video_frame_sheets": sheets,
        "video_frame_count": nframes,
        "devpost_page_screenshot": f"screenshots/{slug}.png",
        "video_transcript_excerpt": (pg.get("transcript") or "")[:4000],
        "audio_neutrality_directive": slug in music_slugs,
    }
    out = f"{BASE}/analysis/rerun/packets/{slug}.json"
    json.dump(packet, open(out, "w"), ensure_ascii=False)
    built[slug] = {"path": os.path.relpath(out, BASE), "sha16": sha16(out),
                   "has_video": packet["has_video"], "n_sheets": len(sheets),
                   "audio_neutral": packet["audio_neutrality_directive"]}

manifest = {
    "built_by": "scripts/build_rerun_packets.py",
    "n_built": len(built), "n_skipped": len(skipped),
    "skipped": skipped,
    "packets": built,
}
json.dump(manifest, open(f"{BASE}/analysis/rerun/manifest.json", "w"), indent=1)
print(f"built {len(built)} packets, skipped {len(skipped)}")
if skipped:
    print("  skipped:", skipped[:10])
nv = sum(1 for v in built.values() if v["has_video"])
ns = sum(1 for v in built.values() if v["n_sheets"] > 0)
na = sum(1 for v in built.values() if v["audio_neutral"])
print(f"  with video: {nv} | with sheets: {ns} | audio-neutrality directive: {na}")
