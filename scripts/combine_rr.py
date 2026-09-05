#!/usr/bin/env python3
"""Combine re-scoring results (rr) into the final ranking.

Pre-registered rules (DEVIATIONS.md 2026-09-05 RE-SCORING PASS entry):
- Re-scored aggregate replaces the S1 provisional aggregate for the 1353 scope slugs.
- S2 scores are untouched.
- Combination within re-scored pair: N/A (single round) — each rr record is one
  reviewer; we take the record as-is (score = mean of 4 criteria by builder downstream).
- Fail-closed: every scope slug must have exactly one rr record; no extra slugs.

Steps:
1. Load rr records -> per-slug re-scored criteria + confidence.
2. Rewrite analysis/provisional.jsonl entries for scope slugs (S1 stage records).
3. Re-run scripts/build_final_ranking.py (monotonic gate + provenance) — it reads
   provisional + s2 rescore files. S2 block reads analysis/results/s2/, unchanged.
4. Regenerate BUILD_MANIFEST (done by builder) and verify.
"""
import glob, json, os, sys

BASE = "/mnt/work/webmcp-analysis"
scope = json.load(open(f"{BASE}/analysis/rerun_scope.json"))

# ---------- load rr results ----------
rr = {}
dupes = []
for f in sorted(glob.glob(f"{BASE}/analysis/results/rr/rr-*.jsonl")):
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d["slug"] in rr:
            dupes.append(d["slug"])
        rr[d["slug"]] = d

problems = []
if dupes:
    problems.append(f"duplicate rr records: {sorted(set(dupes))[:10]}")
missing = [s for s in scope if s not in rr]
extra = sorted(set(rr) - set(scope))
if missing:
    problems.append(f"scope slugs without rr record: {missing[:10]} (n={len(missing)})")
if extra:
    problems.append(f"rr records outside scope: {extra[:10]}")
if problems:
    print("COMBINE FAILED:", file=sys.stderr)
    for p in problems:
        print(" ", p, file=sys.stderr)
    sys.exit(1)

# ---------- rewrite provisional for scope slugs ----------
CRIT = ["leverage", "execution", "impact", "creativity"]
prov_lines = {}
for line in open(f"{BASE}/analysis/provisional.jsonl"):
    d = json.loads(line)
    prov_lines[d["slug"]] = d

updated = 0
for slug in scope:
    r = rr[slug]
    p = prov_lines[slug]
    scores = {c: r[c] for c in CRIT}
    aggregate = round(sum(scores[c] for c in CRIT), 2)
    old = p.get("provisional", {})
    p["provisional"] = {
        "scores": scores,
        "disagreement": False,
        "aggregate": aggregate,
        "advance_conflict": (r.get("advance") == "yes") != (p.get("advance_1") in (True, "yes")),
        "confidence_mean": round(float(r.get("overall_confidence", 0)), 3),
    }
    p["rescored"] = {
        "round": "rr-2026-09-05",
        "prior_aggregate": old.get("aggregate"),
        "new_aggregate": aggregate,
        "reviewer_file": r.get("_src") or "",
        "audio_neutral": bool(p.get("is_anchor") is False and slug in set(
            json.load(open(f"{BASE}/analysis/recheck_music_audio.json")))),
    }
    prov_lines[slug] = p
    updated += 1

with open(f"{BASE}/analysis/provisional.jsonl", "w") as f:
    for slug in sorted(prov_lines):
        f.write(json.dumps(prov_lines[slug], ensure_ascii=False) + "\n")

print(f"provisional updated for {updated} scope slugs")
print(f"  aggregate moves: ", end="")
moves = []
for slug in scope[:0]:
    pass
deltas = []
for slug in scope:
    r = rr[slug]
    p = prov_lines[slug]["rescored"]
    if p["prior_aggregate"] is not None:
        deltas.append((abs(p["new_aggregate"] - p["prior_aggregate"]), slug, p["prior_aggregate"], p["new_aggregate"]))
deltas.sort(reverse=True)
print(f"mean |delta| {sum(d[0] for d in deltas)/len(deltas):.2f}, max {deltas[0][0]:.0f} ({deltas[0][1]} {deltas[0][2]}->{deltas[0][3]})")
print("NOW RUN: python3 scripts/build_final_ranking.py")
