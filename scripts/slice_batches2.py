#!/usr/bin/env python3
"""Slice reviewer_corpus into TWO independent randomized assignment rounds (S1).
Each round: every project exactly once, 20 reviewer-slots. Adds the calibration
overlays (12 common core to every slot; 28 rotated anchors to 3 slots each).
Also emits calibration/ selection support: nothing here uses evidence_count."""
import csv, hashlib, json, os, random

BASE = "/mnt/work/webmcp-analysis"
random.seed(20260905)
N_SLOTS = 20
COMMON_CORE = 12
ROTATED = 28

corpus = [json.loads(l) for l in open(os.path.join(BASE, "analysis", "reviewer_corpus.jsonl"))]
by_slug = {c["slug"]: c for c in corpus}
slugs = sorted(by_slug)

# --- calibration cohort selection: deterministic diversity, no evidence_count ---
def axes(s):
    c = by_slug[s]
    h = hashlib.sha256(s.encode()).hexdigest()
    return {
        "len_bucket": 0 if len(c["about_excerpt"]) < 1500 else (1 if len(c["about_excerpt"]) < 6000 else 2),
        "hash": h,
        "has_video": c["has_video"],
        "has_repo": c["has_public_repo"],
        "demo_alive": c["demo_alive"] == "alive",
    }

# spread selection across text-length buckets, video/repo presence, and category-ish
# diversity proxy (title keyword bands); then seeded random within buckets.
buckets = {}
for s in slugs:
    a = axes(s)
    key = (a["len_bucket"], a["has_video"], a["has_repo"])
    buckets.setdefault(key, []).append(s)
for k in buckets:
    buckets[k].sort(key=lambda s: hashlib.sha256((s + "calib").encode()).hexdigest())
selected = []
keys = sorted(buckets)
ki = 0
while len(selected) < COMMON_CORE + ROTATED and keys:
    k = keys[ki % len(keys)]
    if buckets[k]:
        selected.append(buckets[k].pop(0))
    if not buckets[k]:
        keys.remove(k)
    ki += 1
common_core = selected[:COMMON_CORE]
rotated = selected[COMMON_CORE:]
json.dump({"common_core": common_core, "rotated": rotated},
          open(os.path.join(BASE, "analysis", "calibration_set.json"), "w"), indent=1)

os.makedirs(os.path.join(BASE, "analysis", "batches"), exist_ok=True)
os.makedirs(os.path.join(BASE, "analysis", "results"), exist_ok=True)
manifest = []
for rnd in (1, 2):
    order = slugs[:]
    random.shuffle(order)  # independent shuffle per round
    for i, s in enumerate(order):
        pass
    slots = [[] for _ in range(N_SLOTS)]
    for i, s in enumerate(order):
        slots[i % N_SLOTS].append(s)
    # overlays
    for si in range(N_SLOTS):
        slots[si].extend(common_core)  # every slot sees all 12
    for j, a in enumerate(rotated):
        slots[j % N_SLOTS].append(a)
        slots[(j + 7) % N_SLOTS].append(a)
        slots[(j + 13) % N_SLOTS].append(a)
    for si, sl in enumerate(slots):
        random.shuffle(sl)
        path = os.path.join(BASE, "analysis", "batches", f"r{rnd}-slot{si:02d}.jsonl")
        with open(path, "w") as f:
            for s in sl:
                f.write(json.dumps(by_slug[s], ensure_ascii=False) + "\n")
        manifest.append({"round": rnd, "slot": si, "n": len(sl), "path": os.path.basename(path)})
json.dump(manifest, open(os.path.join(BASE, "analysis", "batch_manifest.json"), "w"), indent=1)
tot = sum(m["n"] for m in manifest)
print(f"slots: {len(manifest)} total assignments: {tot} "
      f"(expect {2*(len(slugs)+N_SLOTS*COMMON_CORE+3*ROTATED)})")
