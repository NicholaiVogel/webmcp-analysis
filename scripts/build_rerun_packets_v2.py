#!/usr/bin/env python3
"""Rebuild reviewer packets for the re-scoring pass — v2, source-parity build.

Sources match scripts/build_reviewer_corpus.py field-for-field:
  - raw/all_projects.csv        title/url
  - raw/parsed.jsonl            pitch, github, demo_links, gallery
  - raw/about/<slug>.txt        about text
  - analysis/signals.jsonl      demo_alive, gh.archived (repo state)
  - raw/video_meta.jsonl        video title/transcript (for the 261 that have it)
  - raw/videos_fixed.json + raw/video_ids.json   video ids (incl. sweep-fixed)
  - raw/frames/<vid>/           contact sheets (AUTHORITATIVE video evidence)

Only three intentional deviations from the original corpus packets (DEVIATIONS.md):
  1. has_video / video_frame_sheets / frame_count  — corrected to sheet truth
  2. audio_neutrality_directive flag on music-audio packets (new field)
  3. duration None when unknown (261/2398 metadata survived); never implies absence

Writes: analysis/rerun/packets/<slug>.json + analysis/rerun/manifest.json
"""
import csv, hashlib, json, os, sys

BASE = "/mnt/work/webmcp-analysis"

def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

# ---------- sources (same as original corpus builder) ----------
rows = {r["slug"]: r for r in csv.DictReader(open(f"{BASE}/raw/all_projects.csv"))}
parsed = {}
for line in open(f"{BASE}/raw/parsed.jsonl"):
    d = json.loads(line)
    parsed[d["slug"]] = d
signals = {}
for line in open(f"{BASE}/analysis/signals.jsonl"):
    d = json.loads(line)
    signals[d["slug"]] = d
vidmeta = {}
for line in open(f"{BASE}/raw/video_meta.jsonl"):
    d = json.loads(line)
    vidmeta[d.get("slug") or ""] = d          # keyed by slug where present
vidmeta_by_vid = {}
for line in open(f"{BASE}/raw/video_meta.jsonl"):
    d = json.loads(line)
    vidmeta_by_vid[d.get("video_id") or ""] = d
vids_fixed = json.load(open(f"{BASE}/raw/videos_fixed.json"))
video_ids = json.load(open(f"{BASE}/raw/video_ids.json"))
music_slugs = set(json.load(open(f"{BASE}/analysis/recheck_music_audio.json")))

def about_for(slug):
    p = f"{BASE}/raw/about/{slug}.txt"
    if os.path.exists(p):
        return open(p, encoding="utf-8", errors="ignore").read()
    return ""

def sheets_for(vid):
    fdir = f"{BASE}/raw/frames/{vid}"
    if not os.path.isdir(fdir):
        return [], 0
    sheets = sorted(f for f in os.listdir(fdir) if f.startswith("sheet") and f.endswith(".jpg"))
    n = 0
    mpath = os.path.join(fdir, "meta.json")
    if os.path.exists(mpath):
        n = json.load(open(mpath)).get("frame_count", 0)
    return [f"raw/frames/{vid}/{s}" for s in sheets], n

os.makedirs(f"{BASE}/analysis/rerun/packets", exist_ok=True)

built, skipped = {}, []
for slug in sys.argv[1:]:
    if slug not in rows:
        skipped.append((slug, "not in manifest"))
        continue
    r = rows[slug]
    p = parsed.get(slug, {})
    sig = signals.get(slug, {})
    vid = vids_fixed.get(slug) or video_ids.get(slug) or ""
    vm = vidmeta_by_vid.get(vid, {})
    sheets, nframes = sheets_for(vid) if vid else ([], 0)
    gh = sig.get("gh") or {}
    packet = {
        "slug": slug,
        "title": (r.get("title") or "").strip(),
        "devpost_url": r.get("url"),
        "pitch": p.get("pitch", ""),
        "about_excerpt": about_for(slug)[:9000],
        "has_public_repo": bool(p.get("github")),
        "has_demo_link": bool(p.get("demo_links")),
        "demo_alive": sig.get("demo_alive", "unknown"),
        "gallery_image_count": len(p.get("gallery", [])),
        # ---- corrected fields (intentional deviations) ----
        "has_video": bool(sheets),
        "video_id": vid,
        "video_duration_secs": vm.get("duration") or None,
        "video_title": (vm.get("title") or "")[:150],
        "video_transcript_excerpt": (vm.get("transcript") or "")[:6000],
        "video_frame_sheets": sheets,
        "video_frame_count": nframes,
        # ---- new field ----
        "audio_neutrality_directive": slug in music_slugs,
        # ---- packaging ----
        "devpost_page_screenshot": f"screenshots/{slug}.png",
        "repo_archived": gh.get("archived") if gh else "",  # '' when no gh signal (corpus parity)
    }
    out = f"{BASE}/analysis/rerun/packets/{slug}.json"
    json.dump(packet, open(out, "w"), ensure_ascii=False)
    built[slug] = {"path": os.path.relpath(out, BASE), "sha16": sha16(out),
                   "has_video": packet["has_video"], "n_sheets": len(sheets),
                   "audio_neutral": packet["audio_neutrality_directive"]}

manifest = {
    "built_by": "scripts/build_rerun_packets_v2.py",
    "sources": "same as build_reviewer_corpus.py; corrections: has_video/sheets/duration from frames truth; audio directive added",
    "n_built": len(built), "n_skipped": len(skipped), "skipped": skipped,
    "packets": built,
}
json.dump(manifest, open(f"{BASE}/analysis/rerun/manifest.json", "w"), indent=1)
print(f"built {len(built)} packets, skipped {len(skipped)}")
if skipped:
    print("  skipped:", skipped[:10])
nv = sum(1 for v in built.values() if v["has_video"])
na = sum(1 for v in built.values() if v["audio_neutral"])
print(f"  with sheets(video): {nv} | audio-directive: {na}")
