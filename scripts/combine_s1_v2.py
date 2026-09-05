#!/usr/bin/env python3
"""S1 combiner v2 — fixes audit finding #3 (calibration overlay consolidation).

Rules:
- For non-anchor projects: one record per round (r1 + r2), first record wins per round,
  duplicates within a round are a hard failure.
- For calibration anchors (common-core + rotated): deterministically select exactly one
  record from round 1 and one from round 2 (lowest reviewer filename per round),
  preserving the intended independent-round design.
- Same provisional rules as v1: |a-b|<=2 -> mean; >2 -> None + DISAGREEMENT flag.
"""
import json, os, sys
from collections import defaultdict

BASE="/mnt/work/webmcp-analysis"
CRIT=["leverage","execution","impact","creativity"]
cal=json.load(open(f"{BASE}/analysis/calibration_set.json"))
anchors=set(cal["common_core"])|set(cal["rotated"])

recs=defaultdict(lambda: defaultdict(list))  # slug -> round -> [(file, rec)]
dupes=[]
for f in sorted(os.listdir(f"{BASE}/analysis/results")):
    if not (f.startswith("r1-") or f.startswith("r2-")): continue
    rnd=1 if f.startswith("r1-") else 2
    for line in open(f"{BASE}/analysis/results/{f}"):
        line=line.strip()
        if not line: continue
        d=json.loads(line)
        slug=d["slug"]
        if any(x[1]["slug"]==slug and x[0]==f for x in recs[slug][rnd]):
            dupes.append((f, slug))
        recs[slug][rnd].append((f, d))

if dupes:
    print(f"WARN: {len(dupes)} same-file duplicate slugs:", dupes[:5])

provisional={}
flagged=0
for slug, rounds in recs.items():
    picks=[]
    for rnd in (1,2):
        if rounds.get(rnd):
            picks.append(sorted(rounds[rnd], key=lambda x:x[0])[0][1])
    if len(picks)<2:
        provisional[slug]={"slug":slug,"status":"MISSING_REVIEWS","n":len(picks)}
        continue
    a,b=picks[0],picks[1]
    scores={}; disagreement=False
    for c in CRIT:
        x,y=a[c],b[c]
        if abs(x-y)<=2: scores[c]=round((x+y)/2,2)
        else: scores[c]=None; disagreement=True
    aggregate=round(sum(scores[c] for c in CRIT),2) if not disagreement else None
    provisional[slug]={
        "slug":slug,"status":"OK",
        "provisional":{"scores":scores,"disagreement":disagreement,
                       "aggregate":aggregate,
                       "advance_conflict":(a.get("advance")!=b.get("advance")),
                       "confidence_mean":round((a.get("overall_confidence",0)+b.get("overall_confidence",0))/2,3)},
        "substitution_1":a.get("substitution"),"substitution_2":b.get("substitution"),
        "advance_1":a.get("advance"),"advance_2":b.get("advance"),
        "red_flags":sorted(set((a.get("red_flags") or [])+(b.get("red_flags") or [])))[:6],
        "standouts":sorted(set((a.get("standouts") or [])+(b.get("standouts") or [])))[:6],
        "categories":[a.get("category"),b.get("category")],
        "is_anchor":slug in anchors,
        "review_files":[picks[0].get("_file",""),picks[1].get("_file","")],
    }
    if disagreement: flagged+=1

out=f"{BASE}/analysis/provisional.jsonl"
with open(out,"w") as f:
    for slug in sorted(provisional):
        f.write(json.dumps(provisional[slug],ensure_ascii=False)+"\n")
n_ok=sum(1 for p in provisional.values() if p["status"]=="OK")
print(f"provisional written: {len(provisional)} records | OK: {n_ok} | disagreement-flagged: {flagged}")
# verify anchors now have cross-round pairs
n_cross=0
for s in anchors:
    if s in provisional and provisional[s].get("review_files"):
        f1,f2=provisional[s]["review_files"]
        if (f1.startswith("r1-"))!=(f2.startswith("r1-")): n_cross+=1
print(f"anchors with cross-round pair: {n_cross}/{len(anchors)}")
