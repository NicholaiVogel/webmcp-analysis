#!/usr/bin/env python3
"""Slice corpus into 20 randomized reviewer batches with hidden calibration anchors.
QUARANTINE: no sheet judgment columns, no desc_score, no HanClinto data in packets."""
import csv, json, os, random

BASE = "/mnt/work/webmcp-analysis"
random.seed(20260905)

signals = {}
for line in open(os.path.join(BASE, "analysis", "signals.jsonl")):
    d = json.loads(line)
    signals[d["slug"]] = d

vidmeta = {}
for line in open(os.path.join(BASE, "raw", "video_meta.jsonl")):
    d = json.loads(line)
    for s in d.get("slugs", []):
        vidmeta[s] = d

corpus = [json.loads(l) for l in open(os.path.join(BASE, "analysis", "corpus.jsonl"))]

def evidence_count(c):
    s = signals.get(c["slug"], {})
    v = vidmeta.get(c["slug"], {})
    n = 0
    if c["page"].get("demo_links"): n += 1
    if s.get("demo_alive") == "alive": n += 1
    if c["page"].get("github"): n += 1
    if c["page"].get("gallery_count", 0): n += 1
    try:
        if float(v.get("duration") or 0) > 30: n += 1
    except (ValueError, TypeError):
        pass
    if min(c["about_text"].find("Gallery"), 999999) >= 0 or len(c["about_text"]) > 6000: n += 1
    return n

by_slug = {c["slug"]: c for c in corpus}
counts = sorted(((evidence_count(c), c["slug"]) for c in corpus))
slugs_sorted = [s for _, s in counts]
n = len(slugs_sorted)
anchors = set(
    slugs_sorted[:12] +
    slugs_sorted[n // 2 - 6:n // 2 + 6] +
    slugs_sorted[-12:]
)
print("anchors:", len(anchors))

order = [c["slug"] for c in corpus]
random.shuffle(order)
N_REVIEWERS = 20
batches = [[] for _ in range(N_REVIEWERS)]
for i, s in enumerate(order):
    batches[i % N_REVIEWERS].append(s)

# distribute each anchor to 2 additional distinct reviewers (3 total views)
anchor_reviewers = {}
for j, a in enumerate(sorted(anchors)):
    home = None
    for bi, b in enumerate(batches):
        if a in b:
            home = bi
            break
    others = [x for x in range(N_REVIEWERS) if x != home]
    random.shuffle(others)
    for k in others[:2]:
        batches[k].append(a)
    anchor_reviewers[a] = [home] + others[:2]

os.makedirs(os.path.join(BASE, "analysis", "batches"), exist_ok=True)
os.makedirs(os.path.join(BASE, "analysis", "results"), exist_ok=True)
manifest = []
for bi, sl in enumerate(batches):
    random.shuffle(sl)
    with open(os.path.join(BASE, "analysis", "batches", f"batch-{bi:02d}.jsonl"), "w") as f:
        for s in sl:
            c = by_slug[s]
            sig = signals.get(s, {})
            vid = vidmeta.get(s, {})
            try:
                dur = int(float(vid.get("duration") or 0))
            except (ValueError, TypeError):
                dur = 0
            packet = {
                "slug": s,
                "title": c["title"],
                "devpost_url": c["url"],
                "pitch": c["page"]["pitch"],
                "about_excerpt": c["about_text"][:9000],
                "has_repo": bool(c["page"]["github"]),
                "repo": (sig.get("gh") or {}).get("repo", ""),
                "repo_stars": (sig.get("gh") or {}).get("stars", ""),
                "repo_pushed": (sig.get("gh") or {}).get("pushed", ""),
                "repo_archived": (sig.get("gh") or {}).get("archived", ""),
                "has_demo_link": bool(c["page"]["demo_links"]),
                "demo_alive": sig.get("demo_alive", "unknown"),
                "gallery_image_count": c["page"]["gallery_count"],
                "has_video": dur > 0,
                "video_duration_secs": dur,
                "video_title": vid.get("title", "")[:120],
                "video_transcript_excerpt": (vid.get("transcript") or "")[:6000],
            }
            f.write(json.dumps(packet, ensure_ascii=False) + "\n")
    manifest.append({"batch": bi, "n": len(sl)})
with open(os.path.join(BASE, "analysis", "batch_manifest.json"), "w") as f:
    json.dump({"batches": manifest, "anchors": sorted(anchors),
               "anchor_reviewers": anchor_reviewers}, f, indent=1)
print("batches:", [(m['batch'], m['n']) for m in manifest])
