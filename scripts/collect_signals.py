#!/usr/bin/env python3
"""Check liveness of each project's first demo link + GitHub repo stats.
Writes analysis/signals.jsonl keyed by slug."""
import json, os, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/mnt/work/webmcp-analysis"

parsed = {}
for line in open(os.path.join(BASE, "raw", "parsed.jsonl")):
    d = json.loads(line)
    parsed[d["slug"]] = d

def head(url):
    """Return 'alive', 'dead', or 'unknown' via curl HEAD/GET probe."""
    try:
        r = subprocess.run(
            ["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code}",
             "--max-time", "12", "-A", "Mozilla/5.0 (X11; Linux x86_64) Firefox/132.0", url],
            capture_output=True, text=True, timeout=15)
        code = r.stdout.strip()[:3]
        if code in ("200",):
            return "alive"
        if code and code[0] in "45":
            return "dead"
        return "unknown"
    except Exception:
        return "unknown"

def gh_stats(url):
    try:
        parts = url.rstrip("/").split("github.com/")[1].split("/")
        if len(parts) < 2:
            return {}
        repo = f"{parts[0]}/{parts[1]}"
        r = subprocess.run(["gh", "api", "repos/" + repo, "--jq",
                            "{stars: .stargazers_count, pushed: .pushed_at, archived: .archived, desc: .description}"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            d = json.loads(r.stdout)
            d["repo"] = repo
            return d
    except Exception:
        pass
    return {}

def work(item):
    slug, p = item
    demo = p.get("demo_links") or []
    gh = p.get("github") or []
    return slug, {
        "demo_alive": head(demo[0]) if demo else "no_demo",
        "demo_url": demo[0] if demo else "",
        "gh": gh_stats(gh[0]) if gh else {},
    }

out = open(os.path.join(BASE, "analysis", "signals.jsonl"), "a")
done = set()
if os.path.exists(os.path.join(BASE, "analysis", "signals.jsonl")):
    for line in open(os.path.join(BASE, "analysis", "signals.jsonl")):
        try:
            done.add(json.loads(line)["slug"])
        except Exception:
            pass
todo = [(s, p) for s, p in parsed.items() if s not in done]
print(f"signals todo={len(todo)} done={len(done)}", flush=True)
done_count = 0
with ThreadPoolExecutor(max_workers=40) as ex:
    futs = {ex.submit(work, it): it[0] for it in todo}
    for fu in as_completed(futs):
        slug, sig = fu.result()
        sig["slug"] = slug
        out.write(json.dumps(sig, ensure_ascii=False) + "\n")
        done_count += 1
        if done_count % 250 == 0:
            print(f"{done_count}/{len(todo)}", flush=True)
out.close()
print("signals done", done_count)
