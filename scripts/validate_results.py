#!/usr/bin/env python3
"""Validate reviewer output files against the frozen schema.
Fails (exit 1) listing problems. Usage: validate_results.py FILE [...]."""
import json, sys

REQ_KEYS = ["slug", "category", "category_secondary", "one_line", "what_it_does",
            "access_model", "substitution",
            "leverage", "leverage_rationale", "leverage_evidence", "leverage_confidence",
            "execution", "execution_rationale", "execution_evidence", "execution_confidence",
            "impact", "impact_rationale", "impact_evidence", "impact_confidence",
            "creativity", "creativity_rationale", "creativity_evidence", "creativity_confidence",
            "usability", "usability_note", "project_origin", "eligibility",
            "video_evidence", "red_flags", "standouts", "overall_confidence",
            "advance", "advance_reason"]
ENUMS = {
    "access_model": {"none", "login", "api-key", "unclear"},
    "substitution": {"TRANSFORMATIVE", "MAJOR_DELTA", "MEANINGFUL_DELTA", "MINOR_DELTA", "COSMETIC"},
    "project_origin": {"new", "pre_existing", "unclear"},
    "eligibility": {"LIKELY_ELIGIBLE", "UNCLEAR", "LIKELY_INELIGIBLE"},
    "advance": {"yes", "no"},
}
CATS = {"game", "music-audio", "creative-art", "dev-tool", "agent-infra", "productivity",
        "business-crm", "commerce", "data-viz", "education", "research", "writing",
        "social", "health", "finance", "travel-maps", "other"}

def validate(path):
    problems = []
    n = 0
    for i, line in enumerate(open(path), 1):
        line = line.strip()
        if not line:
            continue
        n += 1
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"{path}:{i} bad JSON: {e}")
            continue
        for k in REQ_KEYS:
            if k not in d:
                problems.append(f"{path}:{i} missing key: {k}")
        for k, allowed in ENUMS.items():
            if k in d and d[k] not in allowed:
                problems.append(f"{path}:{i} {k}={d[k]!r} not in {allowed}")
        for k in ("leverage", "execution", "impact", "creativity", "usability"):
            v = d.get(k)
            if k in d and (not isinstance(v, int) or not (1 <= v <= 10)):
                problems.append(f"{path}:{i} {k}={v!r} not int 1-10")
        cat = d.get("category")
        if cat is not None and cat not in CATS:
            problems.append(f"{path}:{i} category={cat!r} not in taxonomy")
        ve = d.get("video_evidence")
        if isinstance(ve, dict):
            for kk, vv in ve.items():
                if vv not in {"yes", "no", "partial", "unclear"}:
                    problems.append(f"{path}:{i} video_evidence.{kk}={vv!r}")
        if d.get("advance") == "yes" and not d.get("advance_reason", "").strip():
            problems.append(f"{path}:{i} advance=yes without advance_reason")
        for k in ("leverage_confidence", "execution_confidence", "impact_confidence",
                  "creativity_confidence", "overall_confidence"):
            v = d.get(k)
            if k in d and (not isinstance(v, (int, float)) or not (0 <= v <= 1)):
                problems.append(f"{path}:{i} {k}={v!r} not 0-1")
    return n, problems

if __name__ == "__main__":
    total = 0
    allp = []
    for p in sys.argv[1:]:
        n, probs = validate(p)
        total += n
        print(f"{p}: {n} records, {len(probs)} problems")
        allp += probs
    for pr in allp[:40]:
        print(" ", pr)
    sys.exit(1 if allp else 0)
