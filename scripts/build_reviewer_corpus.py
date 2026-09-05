#!/usr/bin/env python3
"""Build analysis/reviewer_corpus.jsonl: FACTUAL manifest only.
Forbidden: every prior-judgment field (scores, strengths, weaknesses, verdict,
confidence, tiers, ranks, rationales). Consumed by slice_batches2.py ONLY."""
import csv, json, os

BASE = "/mnt/work/webmcp-analysis"

parsed = {}
for line in open(os.path.join(BASE, "raw", "parsed.jsonl")):
    d = json.loads(line)
    parsed[d["slug"]] = d

signals = {}
for line in open(os.path.join(BASE, "analysis", "signals.jsonl")):
    d = json.loads(line)
    signals[d["slug"]] = d

vidmeta = {}
for line in open(os.path.join(BASE, "raw", "video_meta.jsonl")):
    d = json.loads(line)
    for s in d.get("slugs", []):
        vidmeta[s] = d

rows = list(csv.DictReader(open(os.path.join(BASE, "raw", "all_projects.csv"))))
out = open(os.path.join(BASE, "analysis", "reviewer_corpus.jsonl"), "w")
n = 0
for r in rows:
    slug = r["slug"]
    p = parsed.get(slug, {})
    about = ""
    ap = os.path.join(BASE, "raw", "about", slug + ".txt")
    if os.path.exists(ap):
        about = open(ap, encoding="utf-8", errors="ignore").read()
    sig = signals.get(slug, {})
    vm = vidmeta.get(slug, {})
    fdir = os.path.join(BASE, "raw", "frames", vm.get("video_id", ""))
    sheets = sorted(f for f in os.listdir(fdir) if f.startswith("sheet") and f.endswith(".jpg")) \
        if os.path.isdir(fdir) else []
    gh = sig.get("gh") or {}
    rec = {
        # factual manifest
        "slug": slug,
        "title": (r.get("title") or "").strip(),
        "devpost_url": r.get("url"),
        "pitch": p.get("pitch", ""),
        "about_excerpt": about[:9000],
        "has_public_repo": bool(p.get("github")),
        "has_demo_link": bool(p.get("demo_links")),
        "demo_alive": sig.get("demo_alive", "unknown"),
        "gallery_image_count": len(p.get("gallery", [])),
        "has_video": bool(vm.get("duration")),
        "video_duration_secs": vm.get("duration", ""),
        "video_title": (vm.get("title") or "")[:150],
        "video_transcript_excerpt": (vm.get("transcript") or "")[:6000],
        "video_frame_sheets": [os.path.join("raw", "frames", vm.get("video_id", ""), s) for s in sheets],
        "devpost_page_screenshot": os.path.join("screenshots", slug + ".png"),
        # repo facts WITHOUT popularity: existence/visibility only
        "repo_archived": gh.get("archived", "") if p.get("github") else "",
    }
    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n += 1
out.close()
print(f"reviewer_corpus records: {n}")
