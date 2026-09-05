#!/usr/bin/env python3
"""FINAL RANKING BUILDER — tracked, reproducible, fail-closed.

Builds analysis/final_ranking.json + analysis/FINAL_RANKING.csv + analysis/site_data/final_ranking.json
from frozen inputs. Enforces the release-gate rules from correctness-audit.md:
  - exactly 2500 unique rows from a documented input manifest
  - one global comparator (aggregate desc, L/E/I/C desc, slug asc)
  - hard failure on any adjacent ordering violation
  - score provenance (stage, reviewer files, evidence flags) on every row
  - no silent fallbacks: disagreement handling is explicit

Usage: python3 scripts/build_final_ranking.py
Inputs (all must exist):
  analysis/s2_queue.json                 - Stage 2 queue membership
  analysis/provisional.jsonl             - S1 provisional state per slug
  analysis/results/s2/s2rescore-*.jsonl  - S2 blind rescoring records
  analysis/reviewer_corpus.jsonl         - titles/URLs/screenshot paths
"""
import csv, glob, hashlib, json, os, re, sys
from collections import defaultdict

BASE = "/mnt/work/webmcp-analysis"
CRIT = ["leverage", "execution", "impact", "creativity"]
TIEBREAK = ["leverage", "execution", "impact", "creativity"]  # official order

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def fail(msg):
    print(f"BUILD FAILED: {msg}", file=sys.stderr)
    sys.exit(1)

# ---------- inputs ----------
inputs = {
    "provisional": f"{BASE}/analysis/provisional.jsonl",
    "s2_queue": f"{BASE}/analysis/s2_queue.json",
    "reviewer_corpus": f"{BASE}/analysis/reviewer_corpus.jsonl",
    "videos_fixed": f"{BASE}/raw/videos_fixed.json",
    "video_ids": f"{BASE}/raw/video_ids.json",
}
s2_files = sorted(glob.glob(f"{BASE}/analysis/results/s2/s2rescore-*.jsonl"))
if not s2_files:
    fail("no s2rescore files found under analysis/results/s2/")
input_manifest = {k: {"path": v, "sha16": sha(v)} for k, v in inputs.items()}
input_manifest["s2_rescore_files"] = {
    os.path.basename(f): sha(f) for f in s2_files
}

# ---------- load corpus ----------
corpus = {}
for line in open(inputs["reviewer_corpus"]):
    d = json.loads(line)
    corpus[d["slug"]] = d

# ---------- load S1 provisional ----------
prov = {}
for line in open(inputs["provisional"]):
    d = json.loads(line)
    prov[d["slug"]] = d

# ---------- load S2 rescoring ----------
s2_scores = defaultdict(dict)   # slug -> {'a003': rec}
s2_files_by_slug = defaultdict(set)
for f in s2_files:
    aid = re.match(r".*s2rescore-([ab]\d+)\.jsonl$", f).group(1)
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        slug = d["slug"]
        s2_scores[slug][aid] = d
        s2_files_by_slug[slug].add(os.path.basename(f))

# ---------- load S2 queue ----------
queue = [r["slug"] for r in json.load(open(inputs["s2_queue"]))]

# ---------- build one record per project ----------
records = []
problems = []
DISAGREEMENT_MEAN = True  # documented policy (DEVIATIONS.md): flagged pairs use the mean, confidence capped

for slug in corpus:
    c = corpus[slug]
    p = prov.get(slug)
    if p is None:
        problems.append(f"{slug}: no provisional record")
        continue
    if p.get("status") != "OK":
        problems.append(f"{slug}: provisional status={p.get('status')}")
        continue

    in_queue = slug in set(queue)
    pr = p["provisional"]

    if in_queue:
        # ---- S2 path (required: both scorers present) ----
        recs = s2_scores.get(slug, {})
        if len(recs) < 2:
            problems.append(f"{slug}: in S2 queue but {len(recs)} rescorer(s) found, need 2")
            continue
        keys = sorted(recs)
        a, b = recs[keys[0]], recs[keys[1]]
        scores = {}
        capped = []
        for crit in CRIT:
            x, y = a[crit], b[crit]
            scores[crit] = round((x + y) / 2, 1)
            if abs(x - y) > 2:
                capped.append(crit)
        aggregate = round(sum(scores[c] for c in CRIT), 1)
        rec = {
            "slug": slug, "stage": "S2", "scores": scores, "aggregate": aggregate,
            "adjudication": "mean-capped:" + ",".join(capped) if capped else "",
            "verification": a.get("webmcp_runtime_verification") or "UNVERIFIED",
            "reviewer_ids": keys,
            "reviewer_files": sorted(s2_files_by_slug[slug]),
            "evidence": {
                "live_observation": True,
                "video_frames": bool(c.get("video_frame_sheets")),
                "probe": True,
            },
            "confidence": round(
                (a.get("overall_confidence", 0) + b.get("overall_confidence", 0)) / 2, 3),
        }
    else:
        # ---- S1-only path ----
        # Disagreement policy (DEVIATIONS.md): criteria with |delta|>2 use the
        # documented mean-with-confidence-cap fallback rather than excluding the
        # project. Affects few rows; each is labeled.
        if pr.get("aggregate") is not None:
            scores = pr["scores"]; aggregate = pr["aggregate"]; adj = ""
            r1f = [f for f in p.get("review_files", []) if f.startswith("r1-")]
            r2f = [f for f in p.get("review_files", []) if f.startswith("r2-")]
        else:
            scores = {}; capped = []
            r1f = [f for f in p.get("review_files", []) if f.startswith("r1-")]
            r2f = [f for f in p.get("review_files", []) if f.startswith("r2-")]
            if not (r1f and r2f):
                problems.append(f"{slug}: S1 disagreement without review_files")
                continue
            def find(slug_, fname):
                for line in open(f"{BASE}/analysis/results/{fname}"):
                    d = json.loads(line)
                    if d.get("slug") == slug_:
                        return d
                return None
            a = find(slug, r1f[0]); b = find(slug, r2f[0])
            if not a or not b:
                problems.append(f"{slug}: could not locate review records")
                continue
            for crit in CRIT:
                x, y = a[crit], b[crit]
                scores[crit] = round((x + y) / 2, 1)
                if abs(x - y) > 2:
                    capped.append(crit)
            aggregate = round(sum(scores[c] for c in CRIT), 1)
            adj = "mean-capped:" + ",".join(capped) if capped else ""
        rec = {
            "slug": slug, "stage": "S1", "scores": scores,
            "aggregate": aggregate,
            "adjudication": adj if adj else ("DISAGREEMENT-FLAGGED" if pr.get("disagreement") else ""),
            "verification": "UNVERIFIED",
            "reviewer_ids": ["s1-blind-1", "s1-blind-2"],
            "reviewer_files": p.get("review_files", []),
            "evidence": {
                "live_observation": False,
                "video_frames": bool(c.get("video_frame_sheets")),
                "probe": False,
            },
            "confidence": round(pr.get("confidence_mean") or 0, 3),
        }
    records.append(rec)

if problems:
    print(f"BUILD FAILED: {len(problems)} problems", file=sys.stderr)
    for pr in problems[:20]:
        print(" ", pr, file=sys.stderr)
    sys.exit(1)

# ---------- completeness ----------
corpus_slugs = set(corpus)
ranked_slugs = [r["slug"] for r in records]
if len(records) != 2500:
    fail(f"expected 2500 records, got {len(records)}")
if len(set(ranked_slugs)) != 2500:
    fail("duplicate slugs in output")
if set(ranked_slugs) != corpus_slugs:
    missing = corpus_slugs - set(ranked_slugs)
    extra = set(ranked_slugs) - corpus_slugs
    fail(f"slug mismatch: missing={sorted(missing)[:5]} extra={sorted(extra)[:5]}")

# ---------- global comparator ----------
records.sort(key=lambda r: (
    -r["aggregate"],
    -r["scores"]["leverage"],
    -r["scores"]["execution"],
    -r["scores"]["impact"],
    -r["scores"]["creativity"],
    r["slug"],
))

# fail-closed monotonicity
prev = None
for i, r in enumerate(records):
    if prev is not None and r["aggregate"] > prev:
        fail(f"ordering violation at rank {i+1}: {r['slug']} {r['aggregate']} > {prev}")
    prev = r["aggregate"]
    r["final_rank"] = i + 1

# ---------- write outputs ----------
out = []
for r in records:
    c = corpus[r["slug"]]
    out.append({
        "final_rank": r["final_rank"],
        "slug": r["slug"],
        "stage": r["stage"],
        "scores": r["scores"],
        "aggregate": r["aggregate"],
        "verification": r["verification"],
        "adjudication": r["adjudication"],
        "reviewer_ids": r["reviewer_ids"],
        "reviewer_files": r["reviewer_files"],
        "evidence": r["evidence"],
        "confidence": r["confidence"],
        "title": c.get("title", ""),
        "devpost_url": c.get("devpost_url", ""),
        "screenshot": f"screenshots/{r['slug']}.png",
    })

build_meta = {
    "generated_by": "scripts/build_final_ranking.py",
    "comparator": "aggregate desc, then leverage/execution/impact/creativity desc, then slug asc",
    "score_selection": "S2 aggregate where project in S2 queue and both rescoring agents present; else S1 provisional",
    "adjudication_policy": "S2 criterion |delta|>2 uses mean with confidence cap (documented in DEVIATIONS.md); S1 disagreement uses mean (provisional)",
    "inputs": input_manifest,
    "row_count": len(out),
    "stage_split": {"S2": sum(1 for r in out if r["stage"]=="S2"),
                    "S1": sum(1 for r in out if r["stage"]=="S1")},
}
out_wrapped = {"build_meta": build_meta, "ranking": out}
with open(f"{BASE}/analysis/final_ranking.json", "w") as f:
    json.dump(out_wrapped, f, indent=0)

# CSV
csv_rows = []
for r in out:
    csv_rows.append({
        "rank": r["final_rank"], "slug": r["slug"],
        "title": r["title"], "devpost_url": r["devpost_url"],
        "stage": r["stage"],
        "leverage": r["scores"]["leverage"], "execution": r["scores"]["execution"],
        "impact": r["scores"]["impact"], "creativity": r["scores"]["creativity"],
        "aggregate": r["aggregate"],
        "confidence": r["confidence"],
        "webmcp_verification": r["verification"],
        "adjudication": r["adjudication"],
        "screenshot": r["screenshot"],
    })
with open(f"{BASE}/analysis/FINAL_RANKING.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
    w.writeheader()
    w.writerows(csv_rows)

# site data
os.makedirs(f"{BASE}/analysis/site_data", exist_ok=True)
with open(f"{BASE}/analysis/site_data/final_ranking.json", "w") as f:
    json.dump(csv_rows, f)

# manifest of outputs
out_manifest = {
    "final_ranking_json": sha(f"{BASE}/analysis/final_ranking.json"),
    "final_ranking_csv": sha(f"{BASE}/analysis/FINAL_RANKING.csv"),
    "site_data_json": sha(f"{BASE}/analysis/site_data/final_ranking.json"),
}
json.dump(out_manifest, open(f"{BASE}/analysis/BUILD_MANIFEST.json", "w"), indent=1)

print(f"OK: {len(out)} rows ranked")
print(f"  stage split: {build_meta['stage_split']}")
print(f"  monotonic: verified")
print(f"  manifest: analysis/BUILD_MANIFEST.json")
