#!/usr/bin/env python3
"""Regenerate web/public/data/rankings.json from the CURRENT analysis artifacts.

Emits the exact short-key shape index.astro's client script expects:
  s,r,t,p,c,st,v,l,e,i,cr,a,cf,d,o,ac,rp,vd,rs

Sources (in priority order):
  - analysis/final_ranking.json  rich ranked rows (provenance, evidence)
  - analysis/reviewer_corpus.jsonl  pitch text, category, repo/video flags
  - raw/parsed.jsonl  fallback for origin

Run from repo root:  python3 scripts/export_rankings_json.py
"""
import csv, json, os

BASE = "/mnt/work/webmcp-analysis"
OUT = f"{BASE}/web/public/data/rankings.json"

wrap = json.load(open(f"{BASE}/analysis/final_ranking.json"))
ranked = wrap["ranking"]

corpus = {}
for line in open(f"{BASE}/analysis/reviewer_corpus.jsonl"):
    d = json.loads(line)
    corpus[d["slug"]] = d

provisional = {}
for line in open(f"{BASE}/analysis/provisional.jsonl"):
    d = json.loads(line)
    provisional[d["slug"]] = d

# category: prefer the consolidated S1/rescore category from provisional
def category_for(slug):
    p = provisional.get(slug) or {}
    cats = [c for c in (p.get("categories") or []) if c]
    if cats:
        return cats[0]
    return ""

# origin: 'new' | 'pre_existing' | '' from provisional project_origin if present,
# else leave empty (filters treat empty as unknown)
def origin_for(slug):
    p = provisional.get(slug) or {}
    o = p.get("origin") or p.get("project_origin") or ""
    return o if o in ("new", "pre_existing") else ""

# access: from provisional access_model if present
def access_for(slug):
    p = provisional.get(slug) or {}
    return p.get("access_model") or ""

rows = []
for r in ranked:
    slug = r["slug"]
    c = corpus.get(slug, {})
    ev = r.get("evidence") or {}
    rs = ev.get("rescored")
    pitch = (c.get("pitch") or "").strip()
    rows.append({
        "s": slug,
        "r": r["final_rank"],
        "t": r.get("title") or slug,
        "p": pitch[:140],
        "c": category_for(slug),
        "st": r["stage"],
        "v": r.get("verification") or "UNVERIFIED",
        "l": r["scores"]["leverage"],
        "e": r["scores"]["execution"],
        "i": r["scores"]["impact"],
        "cr": r["scores"]["creativity"],
        "a": r["aggregate"],
        "cf": r.get("confidence"),
        "d": 1 if (r.get("adjudication") or "").startswith("DISAGREEMENT") else 0,
        "o": origin_for(slug),
        "ac": access_for(slug),
        "rp": 1 if c.get("has_public_repo") else 0,
        "vd": 1 if c.get("has_video") else 0,
        "rs": 1 if rs else 0,
    })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(rows, f, separators=(",", ":"), ensure_ascii=False)

print(f"wrote {len(rows)} rows -> {OUT}")
r1 = rows[0]
print(f"rank 1: {r1['s']} agg {r1['a']} [{r1['st']}]")
rs = sum(1 for x in rows if x["rs"])
print(f"rescored rows (rs=1): {rs}")
