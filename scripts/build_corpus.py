#!/usr/bin/env python3
"""Merge sheet rows + parsed page data into one corpus JSONL for analyst subagents."""
import csv, json, os

BASE = "/mnt/work/webmcp-analysis"

parsed = {}
with open(os.path.join(BASE, "raw", "parsed.jsonl")) as f:
    for line in f:
        d = json.loads(line)
        parsed[d["slug"]] = d

rows = list(csv.DictReader(open(os.path.join(BASE, "raw", "all_projects.csv"))))
out = open(os.path.join(BASE, "analysis", "corpus.jsonl"), "w")
n = 0
for r in rows:
    slug = r["slug"]
    p = parsed.get(slug, {})
    about = ""
    ap = os.path.join(BASE, "raw", "about", slug + ".txt")
    if os.path.exists(ap):
        about = open(ap, encoding="utf-8", errors="ignore").read()
    rec = {
        "slug": slug,
        "title": r.get("title") or p.get("page_title", "").replace(" | Devpost", ""),
        "url": r.get("url"),
        "sheet": {
            "leverage": r.get("WebMCP Leverage"),
            "execution": r.get("Execution"),
            "impact": r.get("Potential Impact"),
            "creativity": r.get("Creativity & Ambition"),
            "desc_score": r.get("description_score_out_of_100_NOT_OFFICIAL"),
            "strengths": r.get("strengths"),
            "weaknesses": r.get("weaknesses"),
            "verdict": r.get("verdict"),
            "confidence": r.get("confidence"),
            "repo": r.get("repository_links"),
            "video": r.get("video_links"),
        },
        "page": {
            "pitch": p.get("pitch", ""),
            "github": p.get("github", []),
            "demo_links": p.get("demo_links", []),
            "gallery_count": len(p.get("gallery", [])),
            "video": p.get("video", ""),
            "page_found": bool(p),
        },
        "about_text": about[:24000],
    }
    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n += 1
out.close()
print(f"corpus records: {n}")
