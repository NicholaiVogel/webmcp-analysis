#!/usr/bin/env python3
"""Combine Stage 1 results per FUNNEL.md: provisional scores, disagreement flags,
calibration drift stats. Deterministic; no discretionary choices."""
import glob, hashlib, json, os, sys
from collections import defaultdict

BASE = "/mnt/work/webmcp-analysis"
COMMON_CORE = set(json.load(open(os.path.join(BASE, "analysis", "calibration_set.json")))["common_core"])
CRIT = ["leverage", "execution", "impact", "creativity"]

def load(files):
    per = defaultdict(dict)  # slug -> reviewer_file -> record
    for f in files:
        for line in open(f):
            d = json.loads(line)
            per[d["slug"]][os.path.basename(f)] = d
    return per

def provisional(a, b):
    out = {"scores": {}, "disagreement": False}
    for c in CRIT:
        x, y = a[c], b[c]
        if abs(x - y) <= 2:
            out["scores"][c] = (x + y) / 2
        else:
            out["scores"][c] = None
            out["disagreement"] = True
    out["aggregate"] = (sum(out["scores"].values())
                        if not out["disagreement"] else None)
    out["advance_conflict"] = (a["advance"] != b["advance"])
    out["confidence_mean"] = (a["overall_confidence"] + b["overall_confidence"]) / 2
    return out

def drift(per, files):
    stats = {}
    for f in files:
        devs = []
        for s in COMMON_CORE:
            if s in per and f in per[s]:
                devs.append(per[s][f])
        stats[f] = {"n_common": len(devs),
                    "mean_leverage": (sum(d["leverage"] for d in devs) / len(devs)) if devs else None,
                    "mean_execution": (sum(d["execution"] for d in devs) / len(devs)) if devs else None,
                    "mean_impact": (sum(d["impact"] for d in devs) / len(devs)) if devs else None,
                    "mean_creativity": (sum(d["creativity"] for d in devs) / len(devs)) if devs else None}
    return stats

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(BASE, "analysis", "results", "*.jsonl")))
    if len(files) < 2:
        print("need >=2 result files (two rounds); found", len(files))
        sys.exit(1)
    per = load(files)
    out = open(os.path.join(BASE, "analysis", "provisional.jsonl"), "w")
    flagged = 0
    for slug, revs in sorted(per.items()):
        if len(revs) < 2:
            rec = {"slug": slug, "status": "MISSING_REVIEWS", "n": len(revs)}
            out.write(json.dumps(rec) + "\n")
            continue
        names = sorted(revs)
        a, b = revs[names[0]], revs[names[1]]
        p = provisional(a, b)
        rec = {"slug": slug, "status": "OK", "provisional": p,
               "substitution_1": a["substitution"], "substitution_2": b["substitution"],
               "advance_1": a["advance"], "advance_2": b["advance"],
               "red_flags": sorted(set(a.get("red_flags", []) + b.get("red_flags", [])))[:6],
               "standouts": sorted(set(a.get("standouts", []) + b.get("standouts", [])))[:6],
               "categories": [a.get("category"), b.get("category")]}
        if p["disagreement"]:
            flagged += 1
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    out.close()
    st = drift(per, [os.path.basename(f) for f in files])
    print(json.dumps(st, indent=1))
    print(f"projects: {len(per)} disagreement-flagged: {flagged}")
