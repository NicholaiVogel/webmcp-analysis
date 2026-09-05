#!/usr/bin/env python3
"""Build S2 rescoring packets: original evidence + probe + live observation.
S1 scores/rationales EXCLUDED (blinding). Two packets per project (s2a/s2b)."""
import json, glob, os

BASE="/mnt/work/webmcp-analysis"
os.makedirs(f"{BASE}/analysis/s2/packets", exist_ok=True)

obs=defaultdict(list) if False else {}
from collections import defaultdict
obs=defaultdict(list)
for f in glob.glob(f"{BASE}/analysis/results/obs-*.jsonl"):
    for line in open(f):
        line=line.strip()
        if not line: continue
        try:
            d=json.loads(line); obs[d["slug"]].append(d)
        except: pass

probes={}
for line in open(f"{BASE}/analysis/probe_results.jsonl"):
    try: d=json.loads(line); probes[d["slug"]]=d
    except: pass

corpus={}
for line in open(f"{BASE}/analysis/reviewer_corpus.jsonl"):
    d=json.loads(line); corpus[d["slug"]]=d

queue=json.load(open(f"{BASE}/analysis/s2_queue.json"))
n=0
for item in queue:
    s=item["slug"]; c=corpus[s]; o=obs.get(s,[{}])[0]; pr=probes.get(s,{})
    packet={
        "slug": s,
        "title": c["title"],
        "pitch": c["pitch"],
        "about_excerpt": c["about_excerpt"][:7000],
        "has_public_repo": c["has_public_repo"],
        "demo_alive": c["demo_alive"],
        "has_video": c["has_video"],
        "video_frame_sheets": c["video_frame_sheets"],
        "devpost_page_screenshot": c["devpost_page_screenshot"],
        "video_transcript_excerpt": c["video_transcript_excerpt"][:4000],
        "probe_triage": {"verdict": pr.get("verdict","unknown"), "title": pr.get("title","")},
        "live_observation": o if o else {"reachable": False, "note": "no observation recorded"},
    }
    text=json.dumps(packet, ensure_ascii=False)
    open(f"{BASE}/analysis/s2/packets/{s}-a.json","w").write(text)
    open(f"{BASE}/analysis/s2/packets/{s}-b.json","w").write(text)
    n+=1
print(f"s2 packets written: {n} pairs")
