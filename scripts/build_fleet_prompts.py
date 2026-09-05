#!/usr/bin/env python3
"""Build per-reviewer prompts for the FULL S1 fleet from the frozen batch manifest.
Reviewer granularity: 10 projects per reviewer (context-safe with images).
Reviewer assignment files: analysis/fleet/prompts/r{rnd}-{k:04d}.txt
Index: analysis/fleet/index.json"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_prompt import PREAMBLE, RUBRIC, CATS, packet_block  # noqa: E402

BASE = "/mnt/work/webmcp-analysis"
OUT = os.path.join(BASE, "analysis", "fleet", "prompts")
os.makedirs(OUT, exist_ok=True)

corpus = {}
for line in open(os.path.join(BASE, "analysis", "reviewer_corpus.jsonl")):
    d = json.loads(line)
    corpus[d["slug"]] = d

index = []
k = 0
for rnd in (1, 2):
    for path in sorted(glob.glob(os.path.join(BASE, "analysis", "batches", f"r{rnd}-slot*.jsonl"))):
        slugs = [json.loads(l)["slug"] for l in open(path)]
        for i in range(0, len(slugs), 10):
            chunk = slugs[i:i + 10]
            parts = [PREAMBLE, "=== RUBRIC (frozen) ===", RUBRIC,
                     "=== CATEGORY TAXONOMY (frozen) ===", CATS, "=== PROJECT PACKETS ==="]
            for s in chunk:
                parts.append(packet_block(corpus[s]))
            fname = f"r{rnd}-{k:04d}.txt"
            open(os.path.join(OUT, fname), "w").write("\n".join(parts))
            index.append({"reviewer": fname, "round": rnd, "slugs": chunk,
                          "results_file": f"analysis/results/{fname.replace('.txt', '')}.jsonl"})
            k += 1
json.dump(index, open(os.path.join(BASE, "analysis", "fleet", "index.json"), "w"), indent=1)
print(f"reviewer prompts: {k}")
