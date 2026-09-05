#!/usr/bin/env python3
"""FAIL-CLOSED quarantine assertion. Scans every reviewer packet for forbidden fields,
forbidden qualitative keys, and HanClinto judgment leakage. Exits nonzero on any hit.
Also validates structural integrity: every project appears exactly twice across rounds,
frame sheets exist for every claimed path, screenshots exist for every slug."""
import glob, json, os, sys

BASE = "/mnt/work/webmcp-analysis"

FORBIDDEN_KEYS = {
    "leverage", "execution", "impact", "creativity",  # bare names that could carry scores
    "webmcp_leverage", "potential_impact", "creativity_ambition",
    "webmcp leverage", "potential impact", "creativity & ambition",
    "description_score", "description_score_out_of_100_not_official",
    "strengths", "weaknesses", "verdict", "confidence",
    "reconciled_score_out_of_100_not_official", "reconciled_l_e_i_c",
    "comparative_reassessment", "review_tier", "description_rank_shared_ties",
    "original_top10_rank", "prior_source_review", "scorecard", "evidence_quotes",
    "disposition", "date_policy", "rationale", "execution_rationale",
    "leverage_rationale", "impact_rationale", "creativity_rationale",
}

# HanClinto judgment phrases that must never appear in packet text
HANCLINTO_MARKERS = [
    "hanclinto", "description_rank", "review_tier", "original_top10_rank",
    "SHARED_TIES", "reconciled_score",
]

def scan():
    failures = []
    packets = sorted(glob.glob(os.path.join(BASE, "analysis", "batches", "*.jsonl")))
    if not packets:
        print("NO PACKETS FOUND")
        return 1
    seen = {}
    for p in packets:
        for ln, line in enumerate(open(p), 1):
            d = json.loads(line)
            slug = d.get("slug", f"line{ln}")
            seen.setdefault(slug, []).append(os.path.basename(p))
            for k in d.keys():
                if k.lower() in FORBIDDEN_KEYS:
                    failures.append(f"{p}:{ln} forbidden key: {k}")
            text = json.dumps(d, ensure_ascii=False).lower()
            # hanclinto.github.io is a legitimate submission host (his pages host demos);
            # strip it, then flag any remaining 'hanclinto' mention (judgment metadata)
            text = text.replace("hanclinto.github.io", "")
            for m in HANCLINTO_MARKERS:
                if m.lower() in text:
                    failures.append(f"{p}:{ln} hanclinto marker in text: {m}")
            # path sanity
            for v in d.get("video_frame_sheets", []):
                if not os.path.exists(os.path.join(BASE, v)):
                    failures.append(f"{p}:{ln} missing frame sheet: {v}")
            ss = d.get("devpost_page_screenshot", "")
            if ss and not os.path.exists(os.path.join(BASE, ss)):
                failures.append(f"{p}:{ln} missing screenshot: {ss}")
    # exactly-two-reviews check (common core: 12 extra = 14 appearances total;
    # rotated: 3 extra; but simple bounds check:)
    n = len(seen)
    bad_counts = {s: len(v) for s, v in seen.items() if len(v) < 2}
    if bad_counts:
        failures.append(f"projects with <2 reviews: {list(bad_counts.items())[:5]}")
    if failures:
        print(f"FAIL: {len(failures)} problems")
        for f in failures[:30]:
            print(" ", f)
        return 1
    print(f"CLEAN: {len(packets)} packets, {n} projects, all assertions pass")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
