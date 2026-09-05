#!/usr/bin/env python3
"""Music-audio S2 sensitivity table: did live observation bypass the modality bias?"""
import json

BASE = "/mnt/work/webmcp-analysis"
music = set()
for line in open(f"{BASE}/analysis/provisional.jsonl"):
    d = json.loads(line)
    if any(c == "music-audio" for c in d.get("categories", []) if c):
        music.add(d["slug"])
s2q = {r["slug"] for r in json.load(open(f"{BASE}/analysis/s2_queue.json"))}
in_s2 = sorted(music & s2q)
rank = json.load(open(f"{BASE}/analysis/final_ranking.json"))["ranking"]
by_slug = {r["slug"]: r for r in rank}
prov = {}
for line in open(f"{BASE}/analysis/provisional.jsonl"):
    d = json.loads(line)
    prov[d["slug"]] = d

rows = []
for s in in_s2:
    r = by_slug[s]
    s2a = r["aggregate"]
    p = prov[s]
    if "rescored" in p and p["rescored"].get("prior_aggregate") is not None:
        s1a = p["rescored"]["prior_aggregate"]
    else:
        s1a = p["provisional"]["aggregate"]
    s1e = p["provisional"]["scores"]["execution"]
    dE = (r["scores"]["execution"] - s1e) if s1e is not None else float("nan")
    rows.append((s, s1a, s2a, dE, r["final_rank"], r.get("verification", "?")))

rows.sort(key=lambda x: x[4])
out = ["# Music-audio S2 sensitivity table",
       "",
       "The 7 S2 music-audio projects (live-observed + 2 blind rescorers).",
       "Question: did live observation recover what audio-blind S1 review missed?",
       "",
       f"{'slug':<40} {'S1 agg':>7} {'S2 agg':>7} {'dExec':>6} {'rank':>5}  verification",
       "-" * 80]
for s, s1a, s2a, dE, rk, v in rows:
    s1s = f"{s1a:>7.1f}" if s1a is not None else "   None"
    dEs = f"{dE:>+6.1f}" if dE == dE else "   nan"  # NaN check
    out.append(f"{s:<40} {s1s} {s2a:>7.1f} {dEs} {rk:>5}  {v}")
def cmp3(a, b):
    if a is None or b is None:
        return 0  # unknown pairs don't count as movement
    return (a > b) - (a < b)
up = sum(1 for r in rows if cmp3(r[2], r[1]) > 0)
same = sum(1 for r in rows if cmp3(r[2], r[1]) == 0)
down = sum(1 for r in rows if cmp3(r[2], r[1]) < 0)
out += ["", f"moved up: {up} | unchanged: {same} | moved down: {down} (of {len(rows)})"]
text = "\n".join(out) + "\n"
open(f"{BASE}/analysis/music_audio_s2_sensitivity.md", "w").write(text)
print(text)
